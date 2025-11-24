#!/bin/bash
 
set -e

cmake . -DRUN_IN_PLACE=TRUE -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

bash build_standalone.sh standalone_luanti

cp -r standalone_luanti craftium/luanti

echo "recursive-include craftium/luanti *" > MANIFEST.in
