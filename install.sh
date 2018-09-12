#!/bin/bash
echo "Installing dependancies"
cd library/
sudo python3 setup.py install
cd ../gui/
sudo python3 setup.py install
cd ..
brew install graphicsmagick