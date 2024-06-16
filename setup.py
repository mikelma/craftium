import os
from skbuild import setup
from setuptools import find_packages

# Default to using all available CPU cores except two
num_cores = os.getenv("BUILD_THREADS", max(os.cpu_count()-2, 2))

os.environ["SKBUILD_BUILD_OPTIONS"] = f"-j{num_cores}"

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
)
