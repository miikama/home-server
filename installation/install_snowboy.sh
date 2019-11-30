#!/bin/bash

snowboy_repo_dir="snowboy"
snowboy_target_dir="../../homeserver/voice_control/snowboy"

clone=1

test -d snowboy &&{ echo "target folder $snowboy_repo_dir exists already. "; clone=0; }

# snowboy uses swig to produce python bindings
sudo apt install swig

# only download if not done already
if [ $clone -gt 0 ]; then
git clone https://github.com/Kitt-AI/snowboy.git
fi
cd snowboy/swig/Python3
make

cd ../..
CUR_DIR=$(pwd)
CUR_USER=$(whoami)
echo "In directory $CUR_DIR as user $CUR_USER"
cp -rv "swig/Python3/_snowboydetect.so" $snowboy_target_dir
cp -rv swig/Python3/snowboydetect.py $snowboy_target_dir
cp -rv swig/Python3/snowboy-detect-swig.i $snowboy_target_dir
cp -rv swig/Python3/snowboy-detect-swig.o $snowboy_target_dir
cp -rv swig/Python3/snowboy-detect-swig.cc $snowboy_target_dir

cp -rv resources/common.res $snowboy_target_dir/resources

cp -rv examples/Python3/snowboydecoder.py $snowboy_target_dir

echo "Succesfully installed snowboy in $snowboy_target_dir."
