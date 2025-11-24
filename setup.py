import os
import shutil
from setuptools import setup, Extension
import numpy
from setuptools.command.build_ext import build_ext


STANDALONE_BIN_DIR = "./standalone_luanti"

if not os.path.exists(STANDALONE_BIN_DIR):
    raise RuntimeError(
        f"{STANDALONE_BIN_DIR} directory is missing. "
        "Run ./build_engine.sh first."
    )


def setup_irr_shaders_dir():
    # remove the original link
    path = "client/shaders/Irrlicht"
    if os.path.islink(path):
        os.unlink(path)

        # copy the old linked files to `path`
        src = "irr/media/Shaders"
        print(f"\n[*] Copying {src} to {path} \n")
        shutil.copytree(src, path)


def create_data_dir():
    data_dir = "craftium-pkg/"

    os.makedirs(data_dir, exist_ok=True)

    include = ["builtin", "fonts", "locale", "irr",
               "textures", "client", "craftium-envs", "craftium"]

    with open("MANIFEST.in", "w") as manifest:
        for path in include:
            tgt = os.path.join(data_dir, path)
            manifest.write(f"recursive-include {tgt} *\n")
            if not os.path.exists(tgt):
                shutil.copytree(path, tgt)

        # copy patched Luanti bin and system libs
        for dir in ["bin", "lib"]:
            tgt = os.path.join(data_dir, dir)
            shutil.copytree(
                os.path.join(STANDALONE_BIN_DIR, dir),
                tgt,
                dirs_exist_ok=True
            )
            manifest.write(f"recursive-include {tgt} *\n")


class BuildMinetest(build_ext):
    def run(self):
        setup_irr_shaders_dir()
        create_data_dir()
        super().run()


module = Extension("mt_server",
                   sources=["mt_server.c"],
                   include_dirs=[numpy.get_include()])

setup(
    ext_modules=[module],
    cmdclass={"build_ext": BuildMinetest},
)
