mkdir /build && cd /build

/postgres-source/configure --prefix=/pg --disable-rpath --with-python --without-readline --with-uuid=e2fs CFLAGS='-O2' CXXFLAGS='-O2' CC=clang-12 CXX=clang++-12

make -j $(nproc) world-bin

make install-world-bin

cd /pg/bin &&  find ./ -type l -exec sh -c 'cp --remove-destination $(readlink "{}") "{}"' \;
cd /pg/lib &&  find ./ -type l -exec sh -c 'cp --remove-destination $(readlink "{}") "{}"' \;

