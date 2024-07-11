# Environments

This page lists and describes the environments included with craftium.

!!! note

    Although craftium is a reinforcement learning environment creation framework, it comes with some predefined environments ready to use and whose implementations can also serve as inspiration for creating new ones. Check `mods/craftium_env` inside the directory of every environment in the [repo](https://github.com/mikelma/craftium/tree/main/craftium-envs).

## Chop tree 🪓

The player spawns in a dense forest with many trees, equipped with a steel axe. Every time the player chops a tree a positive reward of `1.0` is given, otherwise the reward is `0.0`.

<center>
<img src="../imgs/env_chop_tree.gif" width="200" align="center">
</center>

- **Import:** `gymnasium.make("Craftium/ChopTree-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(8)` (`nop`, `forward`, `jump`, `dig` (used to chop), `mouse x+`, `mouse x-`, `mouse y+`, `mouse y-`)

- **Default episode length:** 500

- **Reward range:** {0.0, 1.0}

## Room 🏃

The player is placed at one end of a closed room. In the other half of the room, a red block is spawned. The objective is to reach the red block as fast as possible. At every timestep the reward is set to `-1`, and when the player reaches the block the episode terminates. The positions of the player and the red block are randomized and change in every episode, thus the agent cannot memorize the target's position.

<center>
<img src="../imgs/env_room.gif" width="200" align="center">
</center>

- **Import:** `gymnasium.make("Craftium/Room-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(4)` (`nop`, `forward`, `mouse x+`, `mouse x-`)

- **Default episode length:** 500

- **Reward range:** {-1}

## Small room 🏃

<center>
<img src="../imgs/env_small_room.gif" width="200" align="center">
</center>

The same as `Craftium/Room-v0` but in a smaller room, resulting in a considerably easier task (less sparse). However, note that the default episode length is shorter than in the previous environment.

- **Import:** `gymnasium.make("Craftium/SmallRoom-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(4)` (`nop`, `forward`, `mouse x+`, `mouse x-`)

- **Default episode length:** 200

- **Reward range:** {-1}

## Speleo 🦇

In this environment, the player spawns in a closed cave illuminated with torches. The objective is to reach the bottom of the cave as fast as possible. For this purpose, the reward at each timestep is the negative Y-axis position of the player (the reward gets more positive as the player goes deeper into the cave).

<center>
<img src="../imgs/env_speleo.gif" width="200" align="center">
</center>

- **Import:** `gymnasium.make("Craftium/Speleo-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(7)` (`nop`, `forward`, `jump`, `mouse x+`, `mouse x-`, `mouse y+`, `mouse y-`)

- **Default episode length:** 500

- **Reward range:** [-8.8, 24.5]

## Spiders attack 🕷️

The player is spawned in a closed cage with a spider inside it. The player is equipped with a steel sword, and the objective is to kill as many spiders as possible until the end of the episode. Every time the player kills a spider the reward of that timestep is set to `1.0`, and `0.0` otherwise. Moreover, when all spiders inside the cage are dead, spiders are respawned with one more spider than in the previous round. The episode terminates if the player is dead or if it survives the last round (with 5 spiders).

<center>
<img src="../imgs/env_spiders_attack.gif" width="200" align="center">
</center>

- **Import:** `gymnasium.make("Craftium/SpidersAttack-v0")`

- **Observation space:** `Box(0, 255, (64, 64, 3), uint8)` (64x64 RGB image)

- **Action space:** `Discrete(10)` (`nop`, `forward`, `left`, `right`, `jump`, `dig` (attack), `mouse x+`, `mouse x-`, `mouse y+`, `mouse y-`)

- **Default episode length:** 2000

- **Reward range:** {0.0, 1.0}
