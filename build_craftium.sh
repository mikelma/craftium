#!/bin/bash
 
set -e

sed -i '/$<$<BOOL:${USE_SDL2_SHARED}>:SDL2::SDL2>/,/$<$<BOOL:${USE_SDL2_STATIC}>:SDL2::SDL2-static>/c\ \ \ \ \ \ \ \ -L/usr/lib64 -lSDL2' irr/src/CMakeLists.txt

# cmake . -DRUN_IN_PLACE=TRUE -DCMAKE_BUILD_TYPE=Release -DBUILD_UNITTESTS=OFF -DENABLE_GETTEXT=OFF -DSDL2_LIBRARIES="/usr/lib64/libSDL2.so" -DSDL2_INCLUDE_DIRS="/usr/include/SDL2"
cmake . -DRUN_IN_PLACE=TRUE -DCMAKE_BUILD_TYPE=Release -DSDL2_LIBRARIES="/usr/lib64/libSDL2.so" -DUSE_SDL2_SHARED=TRUE
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
