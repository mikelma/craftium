#!/bin/bash
 
set -e

sed -i '/$<$<BOOL:${USE_SDL2_SHARED}>:SDL2::SDL2>/,/$<$<BOOL:${USE_SDL2_STATIC}>:SDL2::SDL2-static>/c\ \ \ \ \ \ \ \ -L/usr/lib64 -lSDL2' irr/src/CMakeLists.txt

cmake . -DRUN_IN_PLACE=TRUE \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DSDL2_LIBRARIES="/usr/lib64/libSDL2.so" \
        -DUSE_SDL2_SHARED=TRUE

make -j$(nproc)

mkdir -p craftium/luanti

cp -r bin builtin client fonts locale textures craftium/luanti

cp -r craftium-envs craftium/

echo "recursive-include craftium/luanti *" > MANIFEST.in
echo "recursive-include craftium/craftium-envs *" >> MANIFEST.in
