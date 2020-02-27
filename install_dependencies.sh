echo "This shell program installs all dependencies if you're using a Linux environment."
echo "Note: It is assumed OpenVINO toolkit is already installed. This program will NOT be installing the OpenVINO toolkit."

pip3=`which pip3`
if [ $pip3 = "" ] 
then
    echo "pip3 not found"
    echo "Please install pip3, then run the file again"
    echo "Or install the following packages manually: opencv, poppler, pdf2image, numpy"
fi
num=5

echo ""
echo "Install dependency 1 of $num: OpenCV"
sudo apt-get install python3-opencv

echo ""
echo "Install dependency 2 of $num: Poppler"
sudo apt install poppler-utils

echo ""
echo "Install dependency 3 of $num: pdf2image"
$pip3 install pdf2image

echo ""
echo "Install dependency 4 of $num: numpy"
$pip3 install numpy

echo ""
echo "Install dependency 5 of $num: Pyhunspell"
sudo apt-get install libhunspell-dev
$pip install hunspell
