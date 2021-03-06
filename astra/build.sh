cd build/linux
./autogen.sh
if [ -z "$CUDA_ROOT" ];
   then
       export CUDA_ROOT='/usr/local/cuda/'
fi
./configure --with-python --with-cuda=$CUDA_ROOT --prefix=$PREFIX
if [ $MAKEOPTS == '<UNDEFINED>' ]
  then
    MAKEOPTS=""
fi
make $MAKEOPTS python-root-install
