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
