# Installation

First, clone craftium's repo using the `--recurse-submodules` flag (**important**: the flag fetches submodules needed by the library) and `cd` into the project's main directory:

```bash
git clone --recurse-submodules https://github.com/mikelma/craftium.git # if you prefer ssh: git@github.com:mikelma/craftium.git

cd craftium
```

`craftium` depends on [Minetest](https://github.com/minetest/minetest), which in turn, depends on a series of libraries that we need to install. Minetest's repo contains [instructions](https://github.com/minetest/minetest/blob/master/doc/compiling/linux.md) on how to setup the build environment for many Linux distros (and  [MacOS](https://github.com/minetest/minetest/blob/master/doc/compiling/macos.md)). In Ubuntu/Debian the following command installs all the required libraries:

```bash
sudo apt install g++ make libc6-dev cmake libpng-dev libjpeg-dev libgl1-mesa-dev libsqlite3-dev libogg-dev libvorbis-dev libopenal-dev libcurl4-gnutls-dev libfreetype6-dev zlib1g-dev libgmp-dev libjsoncpp-dev libzstd-dev libluajit-5.1-dev gettext libsdl2-dev
```

Once Minetest's dependencies are installed, check that `setuptools` is updated and run the installation command in the craftium repo's directory:

```bash
pip install -U setuptools
```

and,

```bash
pip install .
```

This last command should compile minetest, install python dependencies, and, finally, craftium. If the installation process fails, please consider submitting an issue [here](https://github.com/mikelma/craftium/issues).
