#!/bin/bash

CC=/local/dgursoy/Applications/Anaconda/bin/mpicc ./configure --prefix=$PREFIX --enable-linux-lfs --enable-parallel --enable-shared --with-zlib=$PREFIX --with-ssl
make
make install

rm -rf $PREFIX/share/hdf5_examples

# Add more build steps here, if they are necessary.

# See
# http://docs.continuum.io/conda/build.html
# for a list of environment variables that are set during the build process.
