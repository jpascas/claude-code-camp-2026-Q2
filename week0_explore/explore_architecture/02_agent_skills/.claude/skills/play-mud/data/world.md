# World Memory — tbaMUD localhost:4000

_Last updated: (not yet saved)_

## Known Locations
<!-- Room name -> notable exits/contents/why it matters. Only log rooms
     worth remembering (hubs, guilds, shops, danger zones) — not every
     room passed through. -->
- **Route to Newbie Zone from start (Tournament Yard)**: north (Bar) ->
  west (Entrance Hall) -> north (Main Street) -> west (Main St 2) ->
  west (Market Square) -> north (Temple Square) -> north (Temple of
  Midgaard) -> north (By The Temple Altar) -> north (Behind Temple
  Altar) -> north (Great Field) -> east (structure) -> north (Entrance
  to Newbie Zone) -> north (Beginning of Passage).
- **Newbie Zone interior map**: Beginning of Passage (pet dragon) -e->
  Dirty Hallway -e-> A Nexus -s-> More Of The Hallway (had loot: gold +
  newbie vest) -w(locked, needs key)-> **A Small Room** (Newbie Guard
  mob, well w/ grate down, doors north+east both start locked) -n->
  loops back to Dirty Hallway's south door (same door, two sides).
  Also from More Of The Hallway: -w(other branch)-> Another Corner
  (newbie monsters) -w-> A Brighter Hallway -w-> End of Passage -w->
  Open Field by Great Field -n-> back to Great Field (loop).
- **A Small Room -> down (well/grate) -> The Dark Pit**: dead-end room,
  only exit is "up" back to Small Room. Contains "the big, ugly
  pit-beast" (tough, see Mob Notes) + a creepy crawler. The grate
  re-locks after passing through — must carry the key to get back out
  (unlock grate / open grate from below).
- **Doors need object keywords, not direction words**: `open north`
  fails ("there doesn't seem to be a north here"); must use `open door`
  or `open grate` / `unlock door` / `unlock grate`. Bare movement
  (`north`, `down`) still uses the direction and correctly reports
  "door/grate seems to be closed" if shut.
- Mobs/doors in this zone appear to **reset/respawn periodically**
  (Newbie Guard respawned and both doors re-locked after some time
  passed) — don't assume a cleared room stays cleared.
- **Path to the Red Room / Minotaur (likely found 2026-07-18):**
  Another Corner (in the newbie zone hallways) has a locked "door"
  keyword to the east (separate from Small Room's doors — same "wee
  little key" from the Newbie Guard unlocks it too). East from Another
  Corner -> **The Alchemist's Room** (mob: The Newbie Alchemist, not
  yet fought/considered). This room has exits n(locked)/w/d(down —
  dark stairway). A sign by the stairway reads: *"If you are below
  level 7 and alone, or below level 4 then bugger off!  Or else don't
  blame me if you die..."* — near-certain this stairway leads to the
  Red Room / Minotaur. Have NOT gone down yet (still level 1 as of
  this note). Full route from Nexus: south -> More Of The Hallway ->
  west(unlock/open door+key) -> A Small Room -> north -> Dirty Hallway
  -> ... OR simpler: from Nexus -> s -> More Of Hallway -> further w
  branch -> Another Corner -> unlock/open door (east) -> east ->
  Alchemist's Room -> down (once leveled enough).

## Mob Notes
<!-- Monster name -> `consider` result, danger level, decent XP for what
     character level, notable drops. This is what lets future sessions
     skip re-considering a monster they've already sized up. -->
- **Newbie Zone Corridor:**
  - Pet dragon (beginning passage) - unknown level, not yet fought
  - Creepy crawling thing (multiple locations) - EASY, safe for level 1,
    ~30-35 exp per kill, barely dents HP
  - Newbie monster (another corner/hallway) - EASY-MODERATE, safe for
    level 1, ~10 exp per hit, takes a while to kill (low damage output),
    respawns, drops a "bright green newbie vest"
  - Newbie Guard (A Small Room) - consider: "You would need a lot of
    luck!" (moderate difficulty, doable solo at level 1, cost only 3/24
    HP to kill). Drops: gold coins, "a wee little key" (unlocks the
    door + grate in A Small Room), "a bright newbie helm" (has a soft
    glowing aura - magical!). Respawns after some time.
  - The big, ugly pit-beast (The Dark Pit, down the well from A Small
    Room) - consider: "Do you feel lucky, punk?" — noticeably TOUGHER
    than the Newbie Guard, likely NOT safe at level 1. Retreated
    without fighting (2026-07-18). Revisit once leveled up.
  - Chess Pawn (chessboard - too high level area, explicit "zone above
    your recommended level" warning)

## Shops & Services
<!-- Shop/bank name/location -> wares or services, notable prices. -->

## Guild / Practice
<!-- Guild locations, what skills/spells are practicable at what level. -->

## Open Threads
<!-- Unexplored exits, rumors, quest hooks not yet followed up — things to
     come back to when there's no more pressing goal. -->
