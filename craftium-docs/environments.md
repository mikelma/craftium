# Environments

This page lists and describes the environments included with craftium.

!!! note

    Although craftium is a reinforcement learning environment creation framework, it comes with some predefined environments ready to use and whose implementations can also serve as inspiration for creating new ones. Check `mods/craftium_env` inside the directory of every environment in the [repo](https://github.com/mikelma/craftium/tree/main/craftium-envs).

## "Classic" RL tasks
---

### Chop tree 🪓

The player spawns in a dense forest with many trees, equipped with a steel axe. Every time the player chops a tree a positive reward of `1.0` is given, otherwise the reward is `0.0`.

<center>
<img src="../imgs/env_chop_tree.gif" width="200" align="center">
</center>

- **Import:** `gymnasium.make("Craftium/ChopTree-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(8)` (`nop`, `forward`, `jump`, `dig` (used to chop), `mouse x+`, `mouse x-`, `mouse y+`, `mouse y-`)

- **Default episode length:** 2000

- **Reward range:** {0.0, 1.0}

### Room 🏃

The player is placed at one end of a closed room. In the other half of the room, a red block is spawned. The objective is to reach the red block as fast as possible. At every timestep the reward is set to `-1`, and when the player reaches the block the episode terminates. The positions of the player and the red block are randomized and change in every episode, thus the agent cannot memorize the target's position.

<center>
<img src="../imgs/env_room.gif" width="200" align="center">
</center>

- **Import:** `gymnasium.make("Craftium/Room-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(4)` (`nop`, `forward`, `mouse x+`, `mouse x-`)

- **Default episode length:** 2000

- **Reward range:** {-1}

### Small room 🏃

<center>
<img src="../imgs/env_small_room.gif" width="200" align="center">
</center>

The same as `Craftium/Room-v0` but in a smaller room, resulting in a considerably easier task (less sparse). However, note that the default episode length is shorter than in the previous environment.

- **Import:** `gymnasium.make("Craftium/SmallRoom-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(4)` (`nop`, `forward`, `mouse x+`, `mouse x-`)

- **Default episode length:** 1000

- **Reward range:** {-1}

### Speleo 🦇

In this environment, the player spawns in a closed cave illuminated with torches. The objective is to reach the bottom of the cave as fast as possible. For this purpose, the reward at each timestep is the negative Y-axis position of the player (the reward gets more positive as the player goes deeper into the cave).

<center>
<img src="../imgs/env_speleo.gif" width="200" align="center">
</center>

- **Import:** `gymnasium.make("Craftium/Speleo-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(7)` (`nop`, `forward`, `jump`, `mouse x+`, `mouse x-`, `mouse y+`, `mouse y-`)

- **Default episode length:** 3000

- **Reward range:** [-8.8, 24.5]

### Spiders attack 🕷️

The player is spawned in a closed cage with a spider inside it. The player is equipped with a steel sword, and the objective is to kill as many spiders as possible until the end of the episode. Every time the player kills a spider the reward of that timestep is set to `1.0`, and `0.0` otherwise. Moreover, when all spiders inside the cage are dead, spiders are respawned with one more spider than in the previous round. The episode terminates if the player is dead or if it survives the last round (with 5 spiders).

<center>
<img src="../imgs/env_spiders_attack.gif" width="200" align="center">
</center>

- **Import:** `gymnasium.make("Craftium/SpidersAttack-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(10)` (`nop`, `forward`, `left`, `right`, `jump`, `dig` (attack), `mouse x+`, `mouse x-`, `mouse y+`, `mouse y-`)

- **Default episode length:** 4000

- **Reward range:** {0.0, 1.0}

## Open world

---
<center>
<img src="../imgs/env_open_world.gif" width="300" align="center">
</center>


The player has to survive and gather resources in an open world ([VoxeLibre](https://content.minetest.net/packages/Wuzzy/mineclone2/)). The environment is designed to have three different tracks: tools, hunt, and defend.
Each track has milestones and rewards, ordered in a hierarchical tree of skills.

<center>
<img src="../imgs/open_world_skills_tree.png" align="center">
</center>

Every time the player unlocks a milestone in any of the tracks, it receives a reward corresponding to the unlocked skill. The milestones and their rewards are:

- **Tools track:**
    - **T1:** Collect two wood blocks. When completed, a reward of 128 is given and the player obtains a wood pickaxe and sword.
    - **T2:** Collect three stone blocks. When completed, a reward of 256 is given and the player obtains a stone pickaxe and sword.
    - **T3:** Collect three iron blocks. When completed, a reward of 1024 is given and the player obtains an iron pickaxe, axe, and sword.
    - **T4:** Collect a diamond block. When completed, a reward of 2048 is given and the player obtains a diamond pickaxe, axe, and sword.

- **Hunt track:** The player is rewarded every time it hunts an animal. The world is populated with chickens, sheep, pigs, and cows, and the reward for hunting them is 16, 32, 64, and 128 respectively.

- **Defend track:** The player is rewarded every time it kills a monster. The world is populated with zombies, skeletons, spiders, and cave spiders, and the reward for killing them is 32, 64, 128, and 256 respectively.
<br>
<br>

In minetest, the time of day of the game is linked to the real clock time, where the day/night cycle lasts for 20 minutes by default (see this wiki [page](https://wiki.minetest.net/Time_of_day)). In this environment, the time of day is set according to the global timestep to maintain consistency and avoid relaying in "real" clock time while training RL agents.

Additional information:

- **Import:** `gymnasium.make("Craftium/OpenWorld-v0")`

- **Observation space:** `Box(0, 255, (180, 320, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(18)` (`nop`, `forward`, `backward`, `left`, `right`, `jump`, `sneak`, `dig`, `place`, `slot_1`, `slot_2`, `slot_3`, `slot_4`, `slot_5`, `mouse x+`, `mouse x-`, `mouse y+`, `mouse y-`)

- **Default episode length:** 10k

- **Reward range:** {0.0, 2048}

## Procedural environment generation

<center>
    <img src="../imgs/env_procdungeons.gif" align="center" width="200px">
    <img src="../imgs/example_dungeon_2.png" align="center" width="220px">
</center>

This environment showcases the flexibility of Craftium by implementing procedurally generated environments and tasks. These environments can be used for less conventional RL research such as unsupervised environment design, continual RL, and meta-RL.

In this case, craftium builds a dungeon environment specified by an ASCII map representation. ASCII maps can be defined by hand or (more interestingly) generated using a procedural map generator. Craftium provides a map generator class `RandomMapGen` (check the reference [here](./reference)), but you could use your own. Although the parameters of the reward function can be changed (see the section below), generally, the objective is to survive in a labyrinthic dungeon full of monstrous creatures and reach the objective (a diamond by default).

This environment uses the following minetest mods: [`Superflat`](https://content.minetest.net/packages/srifqi/superflat/), [`mobs`](https://content.minetest.net/packages/TenPlus1/mobs/), and [`mobs_monster`](https://content.minetest.net/packages/TenPlus1/mobs_monster/). Refer to the mods' documentation for further information (e.g., available monsters).

General information:

- **Import:** `gymnasium.make("Craftium/ProcDungeons-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(10)` (`nop`, `forward`, `left`, `right`, `jump`, `dig` (attack), `mouse x+`, `mouse x-`, `mouse y+`, `mouse y-`)

- **Default episode length:** 5_000

- **Reward range:** Specified by the developer.

!!! note "Environment initialization"

    Instantiating the environment using the default parameters (i.e., `gymnasium.make("Craftium/ProcDungeons-v0")`) will always initialize the same default map. Use the `ascii_map` parameter to change the map (optionally, generate random maps with `ProcMapGen`).

### Custom parameters

This environment expects some parameters when initialized. These parameters are specified using the `mintest_conf` keyword parameter when calling `gymnasium.make`. Here's an example:


```python
import gymnasium as gym
import craftium
from craftium.extra.random_map_generator import RandomMapGen

# Generate a random map using the random dungeon generator provided by craftium
mapgen = RandomMapGen(
        n_rooms=5,
        dispersion=0.4,
        room_min_size=5,
        room_max_size=10,
        max_monsters_per_room=5,
        monsters={"a": 0.4, "b": 0.3, "c": 0.2, "d": 0.1},
    )

ascii_map = mapgen.rasterize(wall_height=5)  # Convert map into a string

env = gym.make(
    "Craftium/ProcDungeons-v0",
    minetest_conf=dict(
        give_initial_stuff=True,
        initial_stuff="default:sword_steel",  # Provide the player with a sword
        performance_tradeoffs=True,
        # ProcDungeons-v0 specific:
        monster_type_a="mobs_monster:sand_monster",
        monster_type_b="mobs_monster:spider",
        monster_type_c="mobs_monster:stone_monster",
        monster_type_d="mobs_monster:mese_monster",
        wall_material="default:steelblock",
        objective_item="default:diamond",  # item to serve as objective
        rwd_objective=1.0,  # Reward of collecting the objective item
        rwd_kill_monster=0.5,  # Reward for killing a monster
        ascii_map=ascii_map.replace("\n", "\\n"),
    ),
)
```

The required parameters are:

| Parameter          | Description                                           |
|--------------------|-------------------------------------------------------|
| `monster_type_a`   | Name of the type `a` monster                          |
| `monster_type_b`   | Name of the type `b` monster                          |
| `monster_type_c`   | Name of the type `c` monster                          |
| `monster_type_d`   | Name of the type `d` monster                          |
| `wall_material`    | Name of the material to use for construction          |
| `objective_item`   | `itemstring` of the item to use as objective          |
| `rwd_objective`    | Reward for reaching the objective                     |
| `rwd_kill_monster` | Reward for killing a monster                          |
| `ascii_map`        | Map specification in ASCII format (see section below) |


### Map format specification

Maps are specified as ASCII strings, where each character has a different meaning. Maps are organized into layers, where the first layer is the floor layer, the second includes walls, the player, and monsters, and the rest of the layers are used for walls.

| Character              | Meaning                               |
|------------------------|---------------------------------------|
| (whitespace)           | Air block                             |
| `#`                    | Wall or floor block (`wall_material`) |
| `@`                    | Player                                |
| `O`                    | Objective item (`objective_item`)     |
| `a`, `b`, `c`, and `d` | Monsters of types a, b, c, and d      |
| `-`                    | New layer                             |

An example map with three layers (walls have a height of 2 blocks). The map describes a dungeon of two rooms, with a single objective item and a monster of type `b`.

```text
##########
##########
##########
##########
##########
      #####
       #####
       ##########
       ##########
       ##########
       ##########
       ##########
-
##########
#        #
#    @   #
#        #
######   #
      #   #
       #   #
       #    #####
       #        #
       #    O   #
       #      b #
       ##########
-
##########
#        #
#        #
#        #
######   #
      #   #
       #   #
       #    #####
       #        #
       #        #
       #        #
       ##########
```

This ASCII map is transalted to the following craftium environment:

<center>
    <img src="../imgs/example_dungeon_1.png" align="center" width="40%">
</center>

In this case, the `objective_item` was set to `default:diamond`, and `monster_type_b` to `mobs_monster:spider`.
