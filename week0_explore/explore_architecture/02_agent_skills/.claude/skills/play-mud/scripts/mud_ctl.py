#!/usr/bin/env python3
"""
mud_ctl.py - deterministic telnet control for a tbaMUD / CircleMUD server.

Why a daemon instead of "connect, run one command, disconnect" per call?
tbaMUD drops a disconnected character back at the entry room (e.g. "By the
Temple Altar") unless the player has rented at an Inn. An agent that is
exploring or grinding needs its position and combat state to survive between
tool calls, so this script keeps ONE long-lived telnet connection open in a
background daemon process and lets you send it commands many times:

    mud_ctl.py connect                 # once, starts the daemon + logs in
    mud_ctl.py send "look"             # as many times as you like
    mud_ctl.py send "north" "look"     # multiple commands in one round trip
    mud_ctl.py status
    mud_ctl.py disconnect              # graceful quit + shutdown

The login handshake (username -> password -> Welcome/Reconnecting menu) and
the telnet IAC negotiation stripping are the two things that are genuinely
fiddly to get right by trial and error against this server. Both are ported
from a hand-verified Ruby implementation
(week0_explore/mud_manager/lib/mud_manager/session.rb) that was built and
tested against this exact tbaMUD instance.
"""

import argparse
import json
import os
import re
import selectors
import socket
import sys
import time

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 4000
DEFAULT_NAME = os.environ.get("MUD_NAME", "dummy")
DEFAULT_PASSWORD = os.environ.get("MUD_PASSWORD", "helloworld")

RUNTIME_DIR = os.path.expanduser("~/.play-mud")

# Telnet protocol bytes. We don't negotiate any options -- we just consume
# and discard IAC sequences so they don't pollute the text buffer.
IAC, DONT, DO, WONT, WILL, SB, SE = 0xFF, 0xFE, 0xFD, 0xFC, 0xFB, 0xFA, 0xF0

PROMPT_SENTINEL = b"> "


def runtime_paths(host, port):
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    tag = f"{host}_{port}"
    return {
        "sock": os.path.join(RUNTIME_DIR, f"{tag}.sock"),
        "pid": os.path.join(RUNTIME_DIR, f"{tag}.pid"),
        "log": os.path.join(RUNTIME_DIR, f"{tag}.log"),
        "status": os.path.join(RUNTIME_DIR, f"{tag}.status"),
    }


def strip_iac(buf: bytes) -> bytes:
    """Remove telnet IAC negotiation sequences, keeping literal 0xFF bytes."""
    out = bytearray()
    i, n = 0, len(buf)
    while i < n:
        b = buf[i]
        if b == IAC:
            nxt = buf[i + 1] if i + 1 < n else None
            if nxt is None:
                break
            if nxt == IAC:
                out.append(0xFF)
                i += 2
            elif nxt in (WILL, WONT, DO, DONT):
                i += 3
            elif nxt == SB:
                j = i + 2
                while j < n - 1 and not (buf[j] == IAC and buf[j + 1] == SE):
                    j += 1
                i = j + 2
            else:
                i += 2
        else:
            out.append(b)
            i += 1
    return bytes(out)


class MudError(Exception):
    pass


class LoginError(MudError):
    pass


class MudSession:
    """A single blocking telnet connection plus a decoded text buffer."""

    def __init__(self, host, port, timeout=10.0, log_path=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.buf = b""
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.setblocking(False)
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.sock, selectors.EVENT_READ)
        self.log_fh = open(log_path, "a", buffering=1) if log_path else None

    def _log(self, direction, text):
        if self.log_fh and text:
            ts = time.strftime("%H:%M:%S")
            for line in text.splitlines():
                self.log_fh.write(f"[{ts}] {direction} {line}\n")

    def _pump(self, deadline):
        """Read whatever is available until deadline; return True if data came in."""
        remaining = max(0.0, deadline - time.monotonic())
        events = self.sel.select(timeout=remaining)
        if not events:
            return False
        try:
            chunk = self.sock.recv(4096)
        except BlockingIOError:
            return False
        if not chunk:
            raise MudError("connection closed by server")
        text = strip_iac(chunk)
        if text:
            self.buf += text
            self._log("<", text.decode("utf-8", errors="replace"))
        return True

    def send(self, line: str):
        self._log(">", line)
        self.sock.setblocking(True)
        self.sock.sendall(line.encode("utf-8") + b"\r\n")
        self.sock.setblocking(False)

    def read_until(self, pattern: bytes, timeout=None) -> str:
        """Block until `pattern` (bytes or compiled regex) appears in the buffer."""
        deadline = time.monotonic() + (timeout or self.timeout)
        is_re = hasattr(pattern, "search")
        while True:
            m = pattern.search(self.buf) if is_re else (self.buf.find(pattern) if pattern in self.buf else -1)
            if is_re:
                if m:
                    cut = m.end()
                    out, self.buf = self.buf[:cut], self.buf[cut:]
                    return out.decode("utf-8", errors="replace")
            elif m != -1:
                cut = m + len(pattern)
                out, self.buf = self.buf[:cut], self.buf[cut:]
                return out.decode("utf-8", errors="replace")
            if time.monotonic() >= deadline:
                raise MudError(f"timed out waiting for {pattern!r}")
            self._pump(deadline)

    def read_until_quiet(self, quiet_seconds=0.6, timeout=None) -> str:
        """Return accumulated text once `quiet_seconds` pass with no new bytes."""
        deadline = time.monotonic() + (timeout or self.timeout)
        last_data_at = None
        while True:
            got = self._pump(min(deadline, time.monotonic() + quiet_seconds))
            now = time.monotonic()
            if got:
                last_data_at = now
            if last_data_at is not None and (now - last_data_at) >= quiet_seconds and self.buf:
                break
            if now >= deadline:
                break
        out, self.buf = self.buf, b""
        return out.decode("utf-8", errors="replace")

    def read_until_prompt(self, timeout=None) -> str:
        """CircleMUD ends every response with a '> ' prompt -- wait for it,
        falling back to a quiet-drain if it never shows (e.g. mid-combat
        spam or a room description with no trailing prompt yet)."""
        try:
            return self.read_until(PROMPT_SENTINEL, timeout=timeout)
        except MudError:
            return self.read_until_quiet(timeout=0.1)

    def login(self, name: str, password: str):
        """Walk the tbaMUD login dance for an EXISTING character."""
        self.read_until(re.compile(rb"By what name do you wish to be known.*\?", re.I))
        self.send(name)
        self.read_until(re.compile(rb"Password", re.I))
        self.send(password)
        output = self.read_until(re.compile(rb"Welcome|Reconnecting|Wrong password|incorrect password", re.I))
        if re.search(r"wrong password|incorrect password", output, re.I):
            raise LoginError(f"login failed for {name!r}: bad password")
        if not re.search(r"reconnecting", output, re.I):
            # Fresh login -> main menu. "Return" dismisses the MOTD/menu
            # prompt, "1" is "enter the game" on a stock tbaMUD menu.
            self.send("")
            self.send("1")
        # Either path ends with an idle "HP Mana Move >" prompt sitting in
        # the buffer. Drain it now so the buffer is empty and the *next*
        # send()/read_until_prompt() pairs cleanly with its own response
        # instead of matching this leftover prompt immediately.
        self.read_until_quiet(quiet_seconds=0.3, timeout=5)

    def close(self):
        try:
            self.sel.unregister(self.sock)
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass
        if self.log_fh:
            self.log_fh.close()


# --------------------------------------------------------------------------
# Daemon: owns the long-lived MudSession, serves commands over a unix socket
# --------------------------------------------------------------------------

def run_daemon(host, port, name, password, timeout):
    paths = runtime_paths(host, port)
    for key in ("sock", "status"):
        try:
            os.remove(paths[key])
        except FileNotFoundError:
            pass

    def write_status(state, detail=""):
        with open(paths["status"], "w") as f:
            json.dump({"state": state, "detail": detail, "pid": os.getpid()}, f)

    try:
        session = MudSession(host, port, timeout=timeout, log_path=paths["log"])
        session.login(name, password)
    except Exception as e:
        write_status("error", str(e))
        sys.exit(1)

    write_status("ready")

    with open(paths["pid"], "w") as f:
        f.write(str(os.getpid()))

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(paths["sock"])
    server.listen(4)

    try:
        while True:
            conn, _ = server.accept()
            try:
                data = b""
                conn.settimeout(5)
                while not data.endswith(b"\n"):
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                req = json.loads(data.decode("utf-8"))
                action = req.get("action", "send")
                if action == "send":
                    results = []
                    for command in req.get("commands", []):
                        session.send(command)
                        output = session.read_until_prompt(timeout=req.get("timeout", 8))
                        results.append({"command": command, "output": output})
                    conn.sendall((json.dumps({"ok": True, "results": results}) + "\n").encode("utf-8"))
                elif action == "ping":
                    conn.sendall((json.dumps({"ok": True}) + "\n").encode("utf-8"))
                elif action == "quit":
                    session.send("quit")
                    output = session.read_until_quiet(timeout=5)
                    # tbaMUD's "quit" saves and leaves the game but drops you
                    # back on the character menu (0-5 options) on the SAME
                    # connection -- it does not close the socket. Choice "0"
                    # is what actually closes the telnet connection.
                    try:
                        session.send("0")
                        output += session.read_until_quiet(timeout=3)
                    except MudError:
                        pass  # server already closed the socket, nothing more to read
                    conn.sendall((json.dumps({"ok": True, "results": [{"command": "quit", "output": output}]}) + "\n").encode("utf-8"))
                    break
                else:
                    conn.sendall((json.dumps({"ok": False, "error": f"unknown action {action!r}"}) + "\n").encode("utf-8"))
            except Exception as e:
                try:
                    conn.sendall((json.dumps({"ok": False, "error": str(e)}) + "\n").encode("utf-8"))
                except Exception:
                    pass
            finally:
                conn.close()
    finally:
        session.close()
        for key in ("sock", "pid", "status"):
            try:
                os.remove(paths[key])
            except FileNotFoundError:
                pass


# --------------------------------------------------------------------------
# Client-side CLI
# --------------------------------------------------------------------------

def _control_request(host, port, payload, timeout=15):
    paths = runtime_paths(host, port)
    if not os.path.exists(paths["sock"]):
        raise MudError("no session running -- call `mud_ctl.py connect` first")
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    client.connect(paths["sock"])
    client.sendall((json.dumps(payload) + "\n").encode("utf-8"))
    data = b""
    while not data.endswith(b"\n"):
        chunk = client.recv(65536)
        if not chunk:
            break
        data += chunk
    client.close()
    return json.loads(data.decode("utf-8"))


def cmd_connect(args):
    paths = runtime_paths(args.host, args.port)
    if os.path.exists(paths["sock"]):
        try:
            resp = _control_request(args.host, args.port, {"action": "ping"}, timeout=3)
            if resp.get("ok"):
                print(f"already connected to {args.host}:{args.port} (session alive)")
                return
        except Exception:
            pass
        for key in ("sock", "pid", "status"):
            try:
                os.remove(paths[key])
            except FileNotFoundError:
                pass

    import subprocess

    script_path = os.path.abspath(__file__)
    proc = subprocess.Popen(
        [sys.executable, script_path,
         "--host", args.host, "--port", str(args.port),
         "_daemon",
         "--name", args.name, "--password", args.password,
         "--timeout", str(args.timeout)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL, start_new_session=True,
    )

    deadline = time.monotonic() + max(args.timeout, 10)
    while time.monotonic() < deadline:
        if os.path.exists(paths["status"]):
            try:
                with open(paths["status"]) as f:
                    status = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                time.sleep(0.2)
                continue
            if status["state"] == "ready":
                print(f"connected and logged in as {args.name!r} on {args.host}:{args.port} "
                      f"(daemon pid {proc.pid}, log: {paths['log']})")
                return
            if status["state"] == "error":
                print(f"login failed: {status['detail']}", file=sys.stderr)
                sys.exit(1)
        time.sleep(0.2)
    print("timed out waiting for daemon to become ready", file=sys.stderr)
    sys.exit(1)


def cmd_send(args):
    resp = _control_request(args.host, args.port,
                             {"action": "send", "commands": args.commands, "timeout": args.timeout},
                             timeout=args.timeout + 5)
    if not resp.get("ok"):
        print(f"error: {resp.get('error')}", file=sys.stderr)
        sys.exit(1)
    for r in resp["results"]:
        print(f"--- > {r['command']}")
        print(r["output"].rstrip())


def cmd_status(args):
    paths = runtime_paths(args.host, args.port)
    if not os.path.exists(paths["sock"]):
        print(f"no session for {args.host}:{args.port}")
        return
    try:
        resp = _control_request(args.host, args.port, {"action": "ping"}, timeout=3)
        print(f"session alive: {resp.get('ok')}")
    except Exception as e:
        print(f"session socket present but not responding: {e}")


def cmd_disconnect(args):
    paths = runtime_paths(args.host, args.port)
    if not os.path.exists(paths["sock"]):
        print("no session running")
        return
    try:
        resp = _control_request(args.host, args.port, {"action": "quit"}, timeout=10)
        if resp.get("results"):
            print(resp["results"][0]["output"].rstrip())
    except Exception as e:
        print(f"warning: {e}", file=sys.stderr)
    finally:
        for key in ("sock", "pid", "status"):
            try:
                os.remove(paths[key])
            except FileNotFoundError:
                pass
        print("disconnected")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    sub = p.add_subparsers(dest="action", required=True)

    sp = sub.add_parser("connect", help="start the background session and log in")
    sp.add_argument("--name", default=DEFAULT_NAME)
    sp.add_argument("--password", default=DEFAULT_PASSWORD)
    sp.add_argument("--timeout", type=float, default=10.0)
    sp.set_defaults(func=cmd_connect)

    sp = sub.add_parser("send", help="send one or more commands to the running session")
    sp.add_argument("commands", nargs="+")
    sp.add_argument("--timeout", type=float, default=8.0)
    sp.set_defaults(func=cmd_send)

    sp = sub.add_parser("status", help="check whether a session is alive")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("disconnect", help="gracefully quit and shut down the session")
    sp.set_defaults(func=cmd_disconnect)

    # internal: not for direct use
    sp = sub.add_parser("_daemon")
    sp.add_argument("--name", required=True)
    sp.add_argument("--password", required=True)
    sp.add_argument("--timeout", type=float, default=10.0)
    sp.set_defaults(func=lambda a: run_daemon(a.host, a.port, a.name, a.password, a.timeout))

    args = p.parse_args()
    try:
        args.func(args)
    except MudError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
