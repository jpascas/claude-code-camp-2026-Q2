# tbaMUD / CircleMUD command reference

A working command surface for the `dummy` character. Not exhaustive —
`help <topic>` in-game is authoritative and always available (e.g.
`help kick`, `help quests`, `help ac`) if a command below doesn't behave
as expected.

## Movement & posture

| Command | Effect |
|---|---|
| `north` / `n`, `east` / `e`, `south` / `s`, `west` / `w`, `up` / `u`, `down` / `d` | Move one room in that direction |
| `exits` | List obvious exits from the current room |
| `look` (`l`) | Redisplay the current room description |
| `look at <target>` / `examine <target>` | Inspect an object, feature, or creature more closely |
| `enter <keyword>` | Enter a portal/building keyword shown in the room text |
| `stand` / `sit` / `rest` / `sleep` / `wake` | Change posture. `rest`/`sleep` regenerate HP/mana/move faster than standing |
| `follow <name>` | Follow another player/mob when grouped |
| `flee` | Escape combat in a random direction — use when HP is critical |

## Perception & self-info

| Command | Effect |
|---|---|
| `score` | HP/mana/move, level, exp needed, alignment, AC, hunger/thirst, position |
| `inventory` (`i`) | What you're carrying |
| `equipment` (`eq`) | What you're wearing/wielding |
| `where` | Rough map of nearby players |
| `time` / `weather` | In-game clock / weather |
| `consider <target>` | Gauge a monster's difficulty **before** attacking — always do this first |
| `diagnose [target]` | Detailed HP read on self or a target |

## Combat

| Command | Effect |
|---|---|
| `consider <target>` | Check difficulty first (see above) |
| `kill <target>` / `hit <target>` / `murder <target>` | Attack (murder = attack another player, PK) |
| `backstab <target>` | Thief opener from stealth |
| `bash <target>` | Warrior stun attempt |
| `kick <target>` | Extra damage, needs practice |
| `flee` | Break off combat |
| `rescue <target>` | Redirect a mob's aggro from an ally to you |
| `wimpy <hp>` | Auto-flee once HP drops below this threshold — set it before grinding solo |

## Guild / skills / magic

| Command | Effect |
|---|---|
| `practice [skill]` | Improve a known skill/spell at your guild; no arg lists what's practicable |
| `cast '<spell>' [target]` | Cast a spell (quotes required around the spell name) |
| `use` / `quaff` / `recite <item>` | Use a wand/potion/scroll |

Guild locations from town center (Temple Square): Clerics west, Thieves
south of the Dark Alley, Warriors east of Main Street, Mages west Main
Street.

## Items & equipment

| Command | Effect |
|---|---|
| `get <item> [container]` | Pick up an item, optionally from a container |
| `get all corpse` | Loot a corpse after a kill |
| `drop` / `donate` / `junk <item>` | Get rid of an item various ways |
| `put <item> <container>` | Store an item |
| `give <item> <target>` | Hand an item to someone |
| `wear` / `wield` / `hold <item>` | Equip an item |
| `remove <item>` | Unequip |
| `eat` / `drink <item>` | Consume food/drink (watch hunger/thirst in `score`) |

## Shops & bank

| Command | Effect |
|---|---|
| `list` | Show a shop's wares (while standing in a shop room) |
| `buy <item>` / `sell <item>` | Trade with a shopkeeper |
| `value <item>` | Ask what a shop would pay for an item |
| `balance` / `deposit <amt>` / `withdraw <amt>` | Bank at the Temple of Midgaard |

## Doors

| Command | Effect |
|---|---|
| `open` / `close <door\|direction>` | Doors |
| `lock` / `unlock <door>` | Needs the right key |
| `pick <door>` | Thief skill |

## Communication

| Command | Effect |
|---|---|
| `say <text>` | Talk to the room |
| `tell <player> <text>` | Private message |
| `emote <action>` | Roleplay action text |
| `shout` / `gossip` / `auction <text>` | Global channels |

## Session / character

| Command | Effect |
|---|---|
| `save` | Force-save character state |
| `rent` | Pay to store yourself safely at an Inn — do this before `quit` if you want to resume at the same spot instead of the Temple Altar |
| `quit` | Leave the game. On tbaMUD this returns you to the character menu (0-5) on the same connection, not an immediate disconnect — `mud_ctl.py disconnect` already handles this correctly, no need to do it manually |

## Notes specific to this server

- Fresh disconnects (without `rent`) put the character back "By the Temple
  Altar" on next login. `mud_ctl.py`'s daemon avoids repeatedly triggering
  this by keeping one connection open for the whole play session — treat
  `disconnect` as an end-of-session action, not something to call between
  every command.
- World data reference (rooms/mobs/objects) if you need ground truth beyond
  what the game text tells you: https://github.com/Yuffster/CircleMUD/tree/master/lib/world
