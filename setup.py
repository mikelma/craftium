from setuptools import setup, Extension
import numpy
from setuptools.command.build_ext import build_ext


class BuildMinetest(build_ext):
    def run(self):
        super().run()


module = Extension("mt_server",
                   sources=["mt_server.c"],
                   include_dirs=[numpy.get_include()])

setup(
    ext_modules=[module],
    cmdclass={"build_ext": BuildMinetest},
)
