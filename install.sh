#!/bin/bash
echo "Installing dependancies"
cd library/
sudo python3 setup.py install
cd ../gui/
sudo python3 setup.py install
cd ..
echo "Installing graphicsmagick"
sudo apt-get install graphicsmagick
echo "Check if pics folder exists"
mkdir -p pics
echo "Create executable script"
cd ../Desktop
cp /home/pi/photoBooth/photoBooth.sh photoBooth.sh
chmod ugo+x photoBooth.sh
