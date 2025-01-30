
✨ *Imagine the richness of Minecraft: open worlds, procedural generation, fully destructible voxel environments... but open source, without Java, easily extensible in [Lua](https://www.lua.org), and with the modern [Gymnasium](https://gymnasium.farama.org/index.html) and [PettingZoo](https://pettingzoo.farama.org/) APIs for AI single-and multi-agent research... This is* **Craftium!** ✨

<center>
<img src="imgs/craftium_logo.png" alt="Craftium logo" width="350" align="right">
</center>

<p align="left">
  <img src="imgs/env_chop_tree.gif" width="60" align="center">
  <img src="imgs/env_room.gif" width="60" align="center">
  <img src="imgs/env_procdungeons.gif" width="63", align="center">
  <img src="imgs/env_speleo.gif" width="60" align="center">
  <img src="imgs/env_spiders_attack.gif" width="60", align="center">
</p>


[Craftium](https://craftium.readthedocs.io/en/latest/) is a fully open-source platform for creating fast, rich, and diverse **single and multi-agent** environments. Craftium is based on the amazing [Luanti](https://www.luanti.org/) voxel game engine and the popular [Gymnasium](https://gymnasium.farama.org/index.html) and [PettingZoo](https://pettingzoo.farama.org/) APIs.

Check the [installation](./installation.md) instructions and the [getting started](./getting-started.md) pages to start using craftium!

- GitHub repository: [https://github.com/mikelma/craftium](https://github.com/mikelma/craftium)
- Online documentation: [https://craftium.readthedocs.io/en/latest/](https://craftium.readthedocs.io/en/latest/)
- Paper (ArXiv): [https://arxiv.org/abs/2407.03969](https://arxiv.org/abs/2407.03969)

## Features ✨

- **Super extensible 🧩:** Luanti is built with modding in mind! The game engine is completely extensible using the [Lua](https://www.lua.org) programming language. Easily create mods to implement the environment that suits the needs of your research! See [environments](https://craftium.readthedocs.io/en/latest/environments/) for a showcase of what is possible with craftium.

- **Blazingly fast ⚡:** Craftium achieves +2K steps per second more than Minecraft-based alternatives! Environment richness, 3D, computational efficiency all meet in craftium!

- **Extensive documentation 📚:** Craftium extensively [documents](https://craftium.readthedocs.io) how to [use](https://craftium.readthedocs.io/en/latest/getting-started/) existing [environments](https://craftium.readthedocs.io/en/latest/environments) and [create](https://craftium.readthedocs.io/en/latest/creating-envs/) new ones. The documentation also includes a low-level [reference](https://craftium.readthedocs.io/en/latest/reference/) of the exported Python classes and gymnasium [Wrappers](https://craftium.readthedocs.io/en/latest/wrappers/), [extensions to the Lua API](https://craftium.readthedocs.io/en/latest/lua_functions/), and [code examples](https://craftium.readthedocs.io/en/latest/lua_env_cookbook/). Moreover, Craftium greatly benefits from existing Luanti documentation like the [wiki](https://wiki.luanti.org/), [reference](https://api.luanti.org/), and [modding book](https://rubenwardy.com/minetest_modding_book/en/basics/getting_started.html).

- **Modern API 🤖:** Craftium implements the well-known [Gymnasium](https://gymnasium.farama.org/index.html)'s [PettingZoo](https://pettingzoo.farama.org/) APIs, opening the door to a huge number of existing tools and libraries compatible with these APIs. For example, [stable-baselines3](https://stable-baselines3.readthedocs.io) or [CleanRL](https://github.com/vwxyzjn/cleanrl) (check [examples](#examples-) section!).

- **Fully open source 🤠:** Both, craftium and Luanti are fully open-source projects. This allowed us to modify Luanti's source code to tightly integrate it with our library, reducing the number of ugly hacks.

- **No more Java 👹:** The Minecraft game is written in Java, not a very friendly language for clusters and high-performance applications. Contrarily, Luanti is written in C++, much more friendly for clusters, and highly performant!

## Citing Craftium 📑

To cite Craftium in publications:

```bibtex
@article{malagon2024craftium,
  title={Craftium: An Extensible Framework for Creating Reinforcement Learning Environments},
  author={Mikel Malag{\'o}n and Josu Ceberio and Jose A. Lozano},
  journal={arXiv preprint arXiv:2407.03969},
  year={2024}
}
```

## Contributing 🏋️

We appreciate contributions to craftium! craftium is in early development, so many possible improvements and bugs are expected. If you have found a bug or have a suggestion, please consider opening an [issue](https://github.com/mikelma/craftium/issues) if it isn't already covered. In case you want to submit a fix or an improvement to the library, [pull requests](https://github.com/mikelma/craftium/pulls) are also very welcome!
