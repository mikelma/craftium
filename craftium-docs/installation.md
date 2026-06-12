# Installation

First, clone craftium using the `--recurse-submodules` flag (**important**: the flag fetches submodules needed by the library) and `cd` into the project's main directory:

```bash
git clone --recurse-submodules https://github.com/mikelma/craftium.git # if you prefer ssh: git@github.com:mikelma/craftium.git
cd craftium
```

`craftium` depends on [Luanti](https://github.com/luanti-org/luanti), which in turn, depends on a series of libraries that we need to install. Luanti's repo contains [instructions](https://github.com/luanti-org/luanti/blob/master/doc/compiling/linux.md) on how to setup the build environment for many Linux distros (and [MacOS](https://github.com/luanti-org/luanti/blob/master/doc/compiling/macos.md). In Ubuntu/Debian the following command installs all the required libraries:

```bash
sudo apt install g++ make libc6-dev cmake libpng-dev libjpeg-dev libgl1-mesa-dev libsqlite3-dev libogg-dev libvorbis-dev libopenal-dev libcurl4-gnutls-dev libfreetype6-dev zlib1g-dev libgmp-dev libjsoncpp-dev libzstd-dev libluajit-5.1-dev gettext libsdl2-dev
```

Additionally, `craftium` requires Python's header files to build a dedicated Python module implemented in C (`mt_server`):

```bash
sudo apt install libpython3-dev
```

Then, check that `setuptools` is updated and run the installation command in the craftium repo's directory:

```bash
pip install -U setuptools
```

and,

```bash
pip install .
```

This last command should compile Luanti, install python dependencies, and, finally, craftium. If the installation process fails, please consider submitting an issue [here](https://github.com/mikelma/craftium/issues). Note that this command only installs the minimum dependencies to run craftium, execute `pip install ".[examples]"` for installing optional dependencies (e.g., for running examples).

## macOS

Craftium also builds and runs natively on macOS (Apple Silicon and Intel),
with one difference: SDL's `offscreen` video driver has no OpenGL support on
macOS, so environments render to a hidden window of the default cocoa driver
instead (see [troubleshooting](troubleshooting.md)). There are no pre-built
wheels for macOS, so craftium is installed from source.

Install the build dependencies with [Homebrew](https://brew.sh):

```bash
brew install cmake freetype gettext gmp jpeg-turbo jsoncpp libpng libogg libvorbis luajit openal-soft sdl2 zstd
```

Clone the repo as described above and, inside it, build the Luanti engine and
install craftium into a virtual environment (Python >= 3.11):

```bash
bash build_craftium.sh

python3.11 -m venv .venv
source .venv/bin/activate
pip install -U setuptools
pip install .
```
