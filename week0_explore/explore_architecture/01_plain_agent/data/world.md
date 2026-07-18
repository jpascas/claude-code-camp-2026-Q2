# World Map (Midgaard)

## Known Rooms & Connections

- **Temple of Midgaard** (south end, start room): exits n e s w d
  - n -> By The Temple Altar (exits n s)
  - e -> The Midgaard Donation Room (exits w)
  - w -> The Reading Room (exits e) - has teleporter, bulletin board, saleswoman
  - s -> The Temple Square (exits n e s w)

- **The Temple Square**: exits n e s w
  - n -> Temple of Midgaard
  - e -> The Eastern End Of Poor Alley
  - w -> The Entrance To The Clerics' Guild
  - s -> Market Square

- **The Entrance To The Clerics' Guild**: exits n e
  - e -> Temple Square
  - n -> bar entrance (guarded by knight templar, blocks entry)

- **The Eastern End Of Poor Alley**: exits e s w
  - w -> Poor Alley (further west, city wall, beggar here)
  - s -> Grubby Inn (blocked/inaccessible so far)
  - e -> Common Square

- **The Common Square**: exits n e s w
  - n -> Market Square
  - e -> The Dark Alley
  - w -> Eastern End Of Poor Alley
  - s -> The Dump (nasty smell)

- **Market Square** (center of Midgaard): exits n e s w
  - n -> Temple Square
  - s -> Common Square
  - w -> Main Street (bakery/armory area)
  - e -> (unexplored, likely more Main Street)

- **Main Street**: exits n e s w
  - e -> Market Square
  - n -> **The Bakery**
  - s -> entrance to the Armory (unexplored)
  - Cityguard(s) stand here

- **The Bakery**: exits s
  - s -> Main Street
  - Baker NPC present
  - Sign on counter with instructions (buy/list)

- **The Dark Alley**: exits e s w
  - w -> Common Square
  - s -> Guild of Thieves (unexplored)
  - e -> The Dark Alley At The Levee (exits e s w, s -> the levee, unexplored)

- **The Dump**: exits n d
  - n -> Common Square
  - d -> sewer system (unexplored)

## Shops

### The Bakery (north of Main Street, west of Market Square)
Description: Small bakery, sweet scent of danish and fine bread. Shelves of fine quality bread/pastry.

**Menu (via `list` command):**
| # | Availability | Item | Cost |
|---|---|---|---|
| 1 | Unlimited | A danish pastry | 7 |
| 2 | Unlimited | A bread | 14 |
| 3 | Unlimited | A waybread | 73 |

Shop commands: `buy`, `list`

## Notes
- Character position persists across telnet/socket reconnects (server-side save).
- MUD login flow: name -> password -> [press return] -> main menu (1=enter game).
