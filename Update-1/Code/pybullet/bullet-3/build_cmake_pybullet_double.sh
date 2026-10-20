#!/bin/sh

# 1. Clean up old root-level build files to avoid conflicts
if [ -e CMakeCache.txt ]; then
  rm -rf CMakeCache.txt CMakeFiles/
fi

# 2. Setup build directory
mkdir -p build_cmake
cd build_cmake || exit 1

# 3. Run CMake with optimization flags and pointer error bypass
cmake \
  -DBUILD_PYBULLET=ON \
  -DBUILD_PYBULLET_NUMPY=ON \
  -DUSE_DOUBLE_PRECISION=ON \
  -DBT_USE_EGL=ON \
  -DBUILD_BULLET_EXAMPLES=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="-Wno-error=incompatible-pointer-types -w" \
  -DCMAKE_CXX_FLAGS="-Wno-error=incompatible-pointer-types -w" .. || exit 1

# 4. Compile using available CPU cores
make -j "$(nproc 2>/dev/null || echo 12)" || exit 1

# 5. Navigate to pybullet outputs
cd examples/pybullet || exit 1

# 6. Fix macOS naming to Linux standard if necessary
if [ -e pybullet.dylib ]; then
  ln -f -s pybullet.dylib pybullet.so
fi

# 7. Refresh Symlinks clean
for dir in pybullet_envs pybullet_data pybullet_utils; do
  if [ -L "$dir" ] || [ -e "$dir" ]; then
    rm -rf "$dir"
  fi
done

# 8. Create relative symbolic links to the Gym/Environment data
ln -s ../../../examples/pybullet/gym/pybullet_envs .
ln -s ../../../examples/pybullet/gym/pybullet_data .
ln -s ../../../examples/pybullet/gym/pybullet_utils .

echo "🎉 Completed build of Bullet and PyBullet."
