#!/bin/bash

set -e

if [[ "$(uname -s)" == "Darwin" ]]; then
    # macOS: SDL2 (e.g. from Homebrew) is found through CMake's config
    # files, the /usr/lib64 workaround below is Linux-only. OpenGL must be
    # the system framework: if Homebrew's Mesa is installed, CMake would
    # pick its X11-targeted libGL, whose symbols don't match the Cocoa GL
    # context SDL creates (GL version/GLSL detection then fails).
    cmake . -DRUN_IN_PLACE=TRUE \
            -DCMAKE_BUILD_TYPE=RelWithDebInfo \
            -DCMAKE_FIND_FRAMEWORK=LAST \
            -DUSE_SDL2_SHARED=TRUE \
            -DOPENGL_gl_LIBRARY=/System/Library/Frameworks/OpenGL.framework \
            -DOPENGL_glu_LIBRARY=/System/Library/Frameworks/OpenGL.framework

    make -j"$(sysctl -n hw.ncpu)"
else
    sed -i '/$<$<BOOL:${USE_SDL2_SHARED}>:SDL2::SDL2>/,/$<$<BOOL:${USE_SDL2_STATIC}>:SDL2::SDL2-static>/c\ \ \ \ \ \ \ \ -L/usr/lib64 -lSDL2' irr/src/CMakeLists.txt

    cmake . -DRUN_IN_PLACE=TRUE \
            -DCMAKE_BUILD_TYPE=RelWithDebInfo \
            -DSDL2_LIBRARIES="/usr/lib64/libSDL2.so" \
            -DUSE_SDL2_SHARED=TRUE

    make -j"$(nproc)"
fi

mkdir -p craftium/luanti

cp -r bin builtin client fonts locale textures craftium/luanti

cp -r craftium-envs craftium/

echo "recursive-include craftium/luanti *" > MANIFEST.in
echo "recursive-include craftium/craftium-envs *" >> MANIFEST.in
