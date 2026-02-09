# Developer guide

## Manual build

1. Clone Craftium's repo and `cd` inside. Make sure that you have the build dependencies installed (see [Installation](installation.md)).

2. Build the Luanti engine:

    ```
    cmake . -DRUN_IN_PLACE=TRUE -DCMAKE_BUILD_TYPE=Release
    make -j$(nproc)
    ```

3. Build `mt_server.c` library:

    ```
    gcc -shared -o mt_server.so -fPIC $(python3 -m pybind11 --includes) mt_server.c -I/usr/include/python3.11 -I$(python3 -c "import numpy; print(numpy.get_include())")  -lpython3.11
    ```

    **Note:** Replace the python version with the one corresponding to your system.

Done! Note that these steps don't install Craftium, they just build all its components, but you can use Craftium inside the project's directory.


## Updating Craftium to new Luanti versions

Luanti, the game engine Craftium is based on, gets updated Instructions to update Craftium to a new Luanti version.

1. Add the Luanti repo as a new remote repo (`upstream`) if it isn't already included (you can check `git remote -v`):

    ```
    git remote add upstream git@github.com:luanti-org/luanti.git
    ```

2. Fetch all tags from the `upstream` remote:

    ```
    git fetch upstream --tags
    ```

    After this step, running `git tag -l` should list all the available Luanti tags.

3. Merge the Luanti tag into the current branch:

    ```
     git merge <version-tag>
    ```

    Where `<version-tag>` is the tag of the version you want to update Craftium to, for example: `5.10.0`.
    This last command will merge as many changes as possible, but some might conflict with the Craftium's modifications to Luanti. Check the command's output to get the list of conflicts. You can also check conflicts from the `Unmerged paths` section of `git status`.

4. After resolving the conflicts, check that all Craftium functionalities continue to work and commit the changes. Note that Craftium doesn't have unit tests yet, so any pull request updating Craftium to a new Luanti version will have to be manually checked.


## Building Craftium as a Python wheel

This method employs [`uv`](https://docs.astral.sh/uv/) and [`docker`](https://www.docker.com/), so please be sure to have a proper installation of both tools in your system before trying to build the wheel.

Once `uv` and `docker` are set up, just call `CIBW_SKIP="*-musllinux_*" uvx cibuildwheel --platform linux` inside the cloned craftium repo. After a while (+ 10mins), the Python wheels will be located inside a new `wheelhouse/` directory in the current path.

## Locally serving the docs

To serve craftium's docs locally, run:

```bash
uv run --group docs mkdocs serve
```

This command will serve craftium's documentation in `http://127.0.0.1:8000/` by default.
