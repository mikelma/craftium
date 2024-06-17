import os
import shutil
from skbuild import setup
from setuptools import find_packages

# Default to using all available CPU cores except two
num_cores = os.getenv("BUILD_THREADS", max(os.cpu_count()-2, 2))
os.environ["SKBUILD_BUILD_OPTIONS"] = f"-j{num_cores}"  # will call `make` with `-j`

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

setup(
    name="craftium",
    version="0.1.0",
    description="A Gymnasium wrapper for the Minetest voxel game engine",
    author="Mikel Malagón",
    author_email="mikelma7@gmail.com",
    packages=find_packages(where="craftium"),
    package_dir={"": "craftium"},
    cmake_args=[
        "-DRUN_IN_PLACE=TRUE",
        "-DCMAKE_BUILD_TYPE=Release",
    ],
    python_requires=">=3.9",
    options={
        "bdist_egg": {"unpack_source": True}
    }
)
