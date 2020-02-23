echo "This shell program installs all dependencies if you're using a Linux environment."
echo "Note: It is assumed OpenVINO toolkit is already installed. This program will NOT be installing the OpenVINO toolkit."

num=4
echo "Install dependency 1 of $num: OpenCV"
pip3 install opencv-python

echo "Install dependency 2 of $num: OpenCV"
sudo apt install poppler-utils

echo "Install dependency 3 of $num: OpenCV"
pip3 install pdf2image

echo "Install dependencies 4 of $num: numpy"
pip3 install numpy

