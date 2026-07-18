---
name: play-mud
description: Play, explore, and level up a character on the tbaMUD/CircleMUD text-adventure server running at localhost:4000 via telnet, using the dummy/helloworld player. Use this skill whenever the user asks to connect to the MUD, log in as dummy, look around, move through rooms, fight or grind monsters, check score/inventory/exits, visit shops or the bank, practice skills, complete quests, or generally "play the game" or "level up the character" — even if they don't mention telnet or CircleMUD by name. Also use it whenever the user sets or references a longer-running goal for the character (e.g. "get to level 7", "go kill the graveyard ghoul", "keep working toward X", "what's the character's status/goal", "continue where we left off") — this skill maintains persistent memory of character state, world knowledge, and active goals across sessions in this skill's data/player.md and data/world.md files, so those requests should route here even without an explicit "play"/"connect" verb. Always use the bundled scripts/mud_ctl.py for the actual connection instead of writing ad-hoc telnet/socket code or shelling out to `telnet`/`nc` directly — it already solves the tricky parts (the multi-step login handshake, telnet protocol byte stripping, and keeping the character's connection alive between tool calls so it doesn't get bounced back to the entry room).
---

# Playing the tbaMUD server

This skill gives you a reliable way to drive a tbaMUD (CircleMUD-derived)
game character over telnet. The server for this project runs at
`localhost:4000` and the playable character is `dummy` / `helloworld` (an
admin character may also exist, but never play as that one — see
"Boundaries" below).

## Why not just write your own telnet code

If you try to hand-roll a socket/telnet client for this each time, you will
burn turns rediscovering the same two gotchas: the login sequence has a
branch (fresh login vs. an already-connected "Reconnecting" resume) that
looks different depending on prior state, and raw telnet bytes contain
protocol negotiation junk (IAC sequences) that will corrupt what you think
the server said if you don't strip it. `scripts/mud_ctl.py` already handles
both, ported from a hand-verified session manager
(`week0_explore/mud_manager` in this repo) built and tested against this
exact server. Use it instead of reinventing the connection.

## The tool: `scripts/mud_ctl.py`

It keeps ONE long-lived telnet connection open in a small background daemon
process, so your character's position, HP, and combat state persist across
however many tool calls you make. This matters because tbaMUD drops a
disconnected character back at the entry room ("By the Temple Altar")
unless they've rented at an Inn — reconnecting fresh for every single
command would make navigation and multi-step goals nearly impossible.

```bash
# Once, at the start of a play session:
python3 scripts/mud_ctl.py connect
# -> logs in as dummy/helloworld on localhost:4000 by default

# As many times as you like during play — one or several commands per call:
python3 scripts/mud_ctl.py send "look"
python3 scripts/mud_ctl.py send "north" "look"
python3 scripts/mud_ctl.py send "consider rat" "kill rat"

# Check the connection is still alive:
python3 scripts/mud_ctl.py status

# Only when you are fully done playing (or need a clean restart):
python3 scripts/mud_ctl.py disconnect
```

Defaults (`localhost:4000`, `dummy`/`helloworld`) come from `--host`/`--port`
flags on `connect` or the `MUD_NAME`/`MUD_PASSWORD` env vars — you shouldn't
need to pass anything for this project's server. `send` accepts multiple
quoted commands in one call, which is the efficient way to walk a known
path or execute a short combat sequence without a round trip per step.

Each `send` call prints the command echoed back plus the raw server
response beneath it. Full session history (everything sent and received,
timestamped) is logged to `~/.play-mud/<host>_<port>.log` — tail that
file if something looks stuck or you need to see exactly what the server
sent.

## Long-term memory: `data/player.md` and `data/world.md`

`mud_ctl.py`'s daemon keeps the connection alive within one session, but it
doesn't survive between separate conversations — and neither does your
context. A goal like "reach level 7" or "defeat the graveyard ghoul" is
usually bigger than one session, so it can't live only in the connection or
in this conversation's context. It has to live in a file. Two files, right
next to `scripts/` in this skill folder (`data/player.md` and
`data/world.md`), exist for exactly this:

- **`data/player.md`** — this character's state: active goals, a completed-
  goals log, the last-known level/HP/location/inventory snapshot, and a
  dated journal of what happened.
- **`data/world.md`** — knowledge about the game world that outlives any one
  goal: which mobs are safe or dangerous at what level, where shops/guilds
  are, rooms worth remembering, unexplored leads.

Both start out as empty templates with the section headers already in
place — fill them in as you go rather than restructuring them.

**How to use them:**

1. **Read both files near the start of any play session**, before or right
   after connecting. If `player.md` already lists active goals, that's
   what you're working toward when the user says something open-ended like
   "keep playing" or "continue" — don't ask what to do or re-explain the
   game, just pick up where the journal left off. If `world.md` already
   has notes on a mob or room you're about to encounter, trust it instead
   of re-discovering it from scratch (though it's fine to double check
   with `consider` if a lot of sessions have passed).
2. **When the user states a new goal** ("get to level 7", "go kill X"),
   add it to the Active Goals list in `player.md` right away, in the same
   turn — don't just track it mentally. If you only keep it in
   conversation context, it's gone as soon as this session ends.
3. **Update `player.md` at natural checkpoints**: after a level-up, a
   death, a goal completed, or the end of a play session — not after every
   single command, which would be a lot of noise for very little signal.
   Move finished goals to Completed Goals with the date rather than
   deleting them, so there's a durable record of progress.
4. **Update `world.md` when you learn something that will matter again**:
   a mob's difficulty from `consider`, a shop's wares, a guild's practice
   list, a room layout worth remembering. Skip anything that's only
   relevant to this one moment.
5. **Treat "current state" as a snapshot, not a live value.** HP in
   particular changes too fast to keep current in the file — use it for
   level/location/gold/equipment, and always re-check `score` in-game
   before making a real-time decision like whether to flee a fight.

## Playing effectively

- **Read before you act.** `look`, `exits`, and `score` are cheap and
  answer most "what should I do next" questions. Run `score` periodically
  during any grinding/combat loop to track HP — don't just fire off attack
  commands blind.
- **`consider <target>` before you `kill <target>`.** It tells you whether
  a monster is a fair fight, tough, or suicide, without any risk. Skipping
  this is the single most common way a low-level character dies.
- **Retreat is cheap, death is not.** If HP is low, `flee` or move away and
  `rest`/`sleep` to heal before continuing. A death typically costs
  experience and drops you back at a start point — much more expensive
  than a few turns spent healing.
- **Batch known sequences.** If you already know the path to a room (e.g.
  from earlier exploration), send the whole chain of directions in one
  `send` call rather than one call per step.
- **Keep `data/player.md` and `data/world.md` current as you go** (see
  above) — the MUD itself won't summarize progress for you, and the user
  likely wants a durable journal/map, not just raw game transcript that
  vanishes at the end of the conversation.
- See `references/commands.md` for the fuller tbaMUD command surface
  (combat, shops, banking, guilds/practice, communication, equipment) —
  skim it once at the start of a session rather than guessing command
  syntax by trial and error.

## Boundaries

- Only play as `dummy`. If an admin/implementor character exists on this
  server, it is the equivalent of a root account and is not for playing —
  never log into it or run wizard-only commands (`wizhelp`, `goto`, `load`,
  etc.) unless the user explicitly asks you to administer the server.
- Don't run destructive commands (`purge`, deleting the character, etc.)
  without the user explicitly asking for them.
