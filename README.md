# noteworthy

## Dependencies
1. Python 3.x & pip3
2. NPM
3. OpenCV
    ```sh
    pip3 install opencv-python
    ```
4. OpenVINO toolkit
    Goto this [link](https://software.intel.com/en-us/openvino-toolkit/choose-download?) for installation, based on your OS.

## Initialize the environment
source /opt/intel/openvino/bin/setupvars.sh

## Test the file
python app.py -m models/intel/text-detection-0004/FP32/text-detection-0004.xml

## Handly Links
- [Text Detection 004 Pre-trained Model](http://docs.openvinotoolkit.org/latest/_models_intel_text_detection_0004_description_text_detection_0004.html)
- [All Pre-trained Models in OpenVINO Zoo](https://software.intel.com/en-us/openvino-toolkit/documentation/pretrained-models)

