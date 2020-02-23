echo "This shell program installs all dependencies if you're using a Linux environment."
echo "Note: It is assumed OpenVINO toolkit is already installed. This program will NOT be installing the OpenVINO toolkit."

pip3=`which pip3`
if [ $pip3 = "" ] 
then
    echo "pip3 not found"
    echo "Please install pip3, then run the file again"
    echo "Or install the following packages manually: opencv, poppler, pdf2image, numpy"
fi
num=4

echo ""
echo "Install dependency 1 of $num: OpenCV"
$pip3 install opencv-python

echo ""
echo "Install dependency 2 of $num: Poppler"
sudo apt install poppler-utils

echo ""
echo "Install dependency 3 of $num: pdf2image"
$pip3 install pdf2image

echo ""
echo "Install dependencies 4 of $num: numpy"
$pip3 install numpy
