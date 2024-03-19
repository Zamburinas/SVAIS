git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build; cd build; cmake ..; cmake --build .
cd ..
python3 setup.py install
python3 -m pip install face_recognition
sudo apt install qtwayland5
