#!/bin/bash
 
set -e

CC="gcc -march=x86-64 -mtune=generic"
CPP="g++ -march=x86-64 -mtune=generic"

cmake . -DRUN_IN_PLACE=TRUE -DCMAKE_BUILD_TYPE=Release -DBUILD_UNITTESTS=OFF -DENABLE_GETTEXT=OFF -DCMAKE_C_COMPILER=$CC -DCMAKE_CXX_COMPILER=$CPP
make -j$(nproc)

# cmake3 -B . \
# 	-DCMAKE_BUILD_TYPE=Release \
# 	-DENABLE_LTO=FALSE \
# 	-DRUN_IN_PLACE=TRUE \
# 	-DENABLE_GETTEXT=TRUE \
# 	-DBUILD_SERVER=TRUE \
# 	${CMAKE_FLAGS}

# cmake3 --clean-first --build . --parallel $(($(nproc) + 1))

# bash build_standalone.sh standalone_luanti
# cp -r standalone_luanti craftium/luanti
mkdir -p craftium/luanti
cp -r bin craftium/luanti

cp -r craftium-envs craftium/

echo "recursive-include craftium/luanti *" > MANIFEST.in
echo "recursive-include craftium/craftium-envs *" >> MANIFEST.in
