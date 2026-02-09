#!/bin/bash

set -e
 
wget https://www.libsdl.org/release/SDL2-2.32.0.tar.gz

tar -xzf SDL2-2.32.0.tar.gz

cd SDL2-2.32.0

./configure --enable-video-dummy --enable-video-offscreen --prefix=/usr

make -j

make install

cd ..
