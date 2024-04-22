sudo apt-get install cmake -y
sudo apt-get install build-essential checkinstall -y
sudo apt-get install libpulse-dev -y
sudo apt-get install libasound2-dev -y

wget http://www.aishub.net/downloads/aisdecoder-1.0.0.tar.gz
tar zxvf aisdecoder-1.0.0.tar.gz
mv aisdecoder-1.0.0 aisdecoder
cd aisdecoder
mkdir build
cd build/
cmake ../ -DCMAKE_BUILD_TYPE=RELEASE
make