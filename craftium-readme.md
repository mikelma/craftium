# Craftium

<img src="../craftium-docs/docs/imgs/Craftium_Logo.png" alt="Craftium logo" width="400" align="right">

✨ *Imagine the features of Minecraft: open world, procedural generation, fully destructible voxel environments... but open source, without Java, easily extensible in [Lua](https://www.lua.org), and with a modern [Gymnasium API](https://gymnasium.farama.org/index.html) designed for RL... This is* **Craftium!** ✨

Craftium is a fully open-source research platform for Reinforcement Learning (RL) research that provides a [Gymnasium](https://gymnasium.farama.org/index.html) wrapper for the [Minetest](https://www.minetest.net/) voxel game engine.

## Features ✨

- **Super extensible 🧩:** Minetest is built with modding in mind! The game engine is completely extensible using the [Lua](https://www.lua.org) programming language. Easily create mods to implement the environment that suits the needs of your research!

- **Modern RL API 🤖:** Craftium slightly modifies Mintest to communicate with Python, and implements the well-known [Gymnasium](https://gymnasium.farama.org/index.html)'s [Env](https://gymnasium.farama.org/api/env/) API. This opens the door to a huge number of existing tools and libraries compatible with this API, such as [stable-baselines3](https://stable-baselines3.readthedocs.io) or [CleanRL](https://github.com/vwxyzjn/cleanrl).

- **Fully open source 🤠:** Craftium is based on the Minetest and Gymnasium, both open-source projects.

- **No more Java ⚡:** The Minecraft game is written in Java, not a very friendly language for clusters and high-performance applications. Contrarily, Minetest is written in C++, much more friendly for clusters, and highly performant!

## Installation

First, clone craftium and `cd` into the project's main directory:

```bash
git clone https://github.com/mikelma/craftium.git # if you prefer ssh: git@github.com:mikelma/craftium.git
cd craftium
```

`craftium` depends on [Minetest](https://github.com/minetest/minetest), which in turn, depends on a series of libraries that we need to install. Minetest's repo contains [instructions](https://github.com/minetest/minetest/blob/master/doc/compiling/linux.md) on how to setup the build environment for many Linux distros (and  [MacOS](https://github.com/minetest/minetest/blob/master/doc/compiling/macos.md)). In Ubuntu/Debian the following command installs all the required libraries:

```bash
sudo apt install g++ make libc6-dev cmake libpng-dev libjpeg-dev libgl1-mesa-dev libsqlite3-dev libogg-dev libvorbis-dev libopenal-dev libcurl4-gnutls-dev libfreetype6-dev zlib1g-dev libgmp-dev libjsoncpp-dev libzstd-dev libluajit-5.1-dev gettext libsdl2-dev
```

Then, check that `setuptools` is updated and run the installation command in the craftium repo's directory:

```bash
pip install -U setuptools
```

and,

```bash
pip install .
```

This last command should compile minetest, install python dependencies, and, finally, craftium. If the installation process fails, please consider submitting an issue [here](https://github.com/mikelma/craftium/issues).

## Get started

Craftium implements [Gymnasium's](https://gymnasium.farama.org/) [`Env`](https://gymnasium.farama.org/api/env/) API, making it compatible with many popular reinforcement learning libraries and tools like [stable-baselines3](https://stable-baselines3.readthedocs.io/en/master/index.html) and [CleanRL](https://github.com/vwxyzjn/cleanrl).

Thanks to the mentioned API, using craftium environments is as simple as using any gymnasium environment. The example below shows the implementation of a random agent in one of the craftium's environments:

```python
import gymnasium as gym
import craftium

env = gym.make("Craftium/ChopTree-v0")

observation, info = env.reset()

for t in range(100):
    action = env.action_space.sample()  # get a random action
    observation, reward, terminated, truncated, _info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()

env.close()
```

Training a CNN-based agent usingh PPO is as simple as:

```python
from stable_baselines3 import PPO
from stable_baselines3.common import logger
import gymnasium as gym
import craftium

env = gym.make("Craftium/ChopTree-v0")

model = PPO("CnnPolicy", env, verbose=1)

new_logger = logger.configure("logs-ppo-agent", ["stdout", "csv"])
model.set_logger(new_logger)
model.learn(total_timesteps=100_000)

env.close()
```

This example trains a CNN-based agent for 10K timesteps in the `Craftium/ChopTree-v0` environment using PPO. Additionally, we set up a custom logger that records training statistics to a CSV file inside the `logs-ppo-agent/` directory.

## Contributing

TODO

## Citing Craftium

TODO
