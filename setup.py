import os
import shutil
from setuptools import setup, Command
from setuptools.command.build_ext import build_ext as _build_ext
import subprocess


class BuildCMake(Command):
    description = "run cmake and make to build the minetest game engine (C++)"
    user_options = []

    # def initialize_options(self):
    #     pass
    #
    # def finalize_options(self):
    #     pass

    def run(self):
        # run cmake
        subprocess.check_call(["cmake", ".", "-DRUN_IN_PLACE=TRUE", "-DCMAKE_BUILD_TYPE=Release"])

        # default to using all available CPU cores except two
        num_cores = os.getenv("BUILD_THREADS", max(os.cpu_count()-2, 2))

        # run make
        subprocess.check_call(["make", f"-j{num_cores}"])


class CustomBuildExt(_build_ext):
    def run(self):
        self.run_command("build_cpp")
        _build_ext.run(self)


def create_data_dir():
    data_dir = "craftium/"

    include = ["bin", "builtin", "fonts", "locale",
               "textures", "client", "craftium-envs"]

    # with open("MANIFEST.in", "w") as manifest:
    for path in include:
        tgt = os.path.join(data_dir, path)
            # manifest.write(f"recursive-include {tgt} *\n")
        if not os.path.exists(tgt):
            shutil.copytree(path, tgt)

def setup_irr_shaders_dir():
    # remove the original link
    path = "client/shaders/Irrlicht"
    if os.path.islink(path):
        os.unlink(path)

        # copy the old linked files to `path`
        src = "irr/media/Shaders"
        print(f"\n[*] Copying {src} to {path} \n")
        shutil.copytree(src, path)

setup_irr_shaders_dir()

create_data_dir()

setup(
    cmdclass={
        "build_cpp": BuildCMake,
        "build_ext": CustomBuildExt,
    },
)
