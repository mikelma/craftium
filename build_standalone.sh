#!/bin/bash
set -e

# --- CONFIGURATION ---
DEST="$1"
# DEST="./standalone_luanti"
# Path to your compiled binary
BINARY_PATH="./bin/luanti"
# Where you want the final python package structure to be
DEST_DIR="$DEST/bin" 
LIB_DIR="$DEST/lib"

mkdir -p "$DEST"

# Clear previous builds
rm -rf "$DEST_DIR" "$LIB_DIR"
mkdir -p "$DEST_DIR"
mkdir -p "$LIB_DIR"

# Copy the binary to the destination
cp "$BINARY_PATH" "$DEST_DIR/luanti"
echo "✅ Copied Luanti binary to $DEST_DIR"

# --- EXCLUSION LIST ---
# These are core system libraries we SHOULD NOT bundle.
# If we bundle libc/libpthread, we risk breaking things on different distros.
EXCLUDE_LIST="linux-vdso|ld-linux|libc\.so|libdl\.so|libm\.so|libpthread\.so|librt\.so|libutil\.so|libnsl\.so|libresolv\.so"

# --- DEPENDENCY COPYING ---
echo "🔍 Scanning and copying dependencies..."

# Get list of dependencies using ldd
DEPENDENCIES=$(ldd "$BINARY_PATH" | awk '{if ($3 != "") print $3}' | sort | uniq)

for dep in $DEPENDENCIES; do
    dep_name=$(basename "$dep")
    
    # Check if the library is in the exclusion list
    if [[ "$dep_name" =~ $EXCLUDE_LIST ]]; then
        echo "   Skipping system lib: $dep_name"
        continue
    fi

    # Copy the library to the lib folder
    cp -L "$dep" "$LIB_DIR/"
    echo "   📦 Bundled: $dep_name"
done

# --- PATCHING RPATH ---
# This tells the binary: "Don't look in /usr/lib. Look in ../lib relative to where I am."
echo "🔧 Patching RPATH..."
patchelf --set-rpath '$ORIGIN/../lib' "$DEST_DIR/luanti"

# OPTIONAL: Patch the bundled libraries too.
# Sometimes libSDL needs to find libX11, and they are both now in "$LIB_DIR".
for lib in "$LIB_DIR"/*.so*; do
    patchelf --set-rpath '$ORIGIN' "$lib"
done

# --- MOVING REQUIRED ASSETS ---
# cp -r builtin client fonts locale textures $DEST

echo "🎉 Done! Your portable Luanti is ready in $DEST"
