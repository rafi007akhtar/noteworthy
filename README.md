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
5. Poppler
    ```sh
    sudo apt install poppler-utils
    ```
6. Pdf2Image
    ```sh
    pip3 install pdf2image
    ```

## Initialize the environment variables
```sh
source /opt/intel/openvino/bin/setupvars.sh
```

## Test the file
```sh
python app2.py -m models/intel/text-detection-0004/FP32/text-detection-0004.xml -i input.jpg
```

## Shortened Paths
```
    export md=/opt/intel/openvino/deployment_tools/tools/model_downloader/downloader.py
    
    export models=~/environment/noteworthy/models/intel/
```

# Demo paths
- All Python demos:
    ```sh
    cd /opt/intel/openvino/deployment_tools/open_model_zoo/demos/python_demo
    ```
- Python demo for text spotting
    ```sh
    cd /opt/intel/openvino/deployment_tools/open_model_zoo/demos/python_demos/text_spotting_demo
    ```

## Run the demo
```sh
# make sure to export the models path before running this
python3 text_spotting_demo.py \
-m_m $models/text-spotting-0001-detector/FP16/text-spotting-0001-detector.xml \
-m_te $models/text-spotting-0001-recognizer-encoder/FP16/text-spotting-0001-recognizer-encoder.xml \
-m_td $models/text-spotting-0001-recognizer-decoder/FP16/text-spotting-0001-recognizer-decoder.xml \
-i ~/environment/noteworthy/input.jpg
```

## Handly Links
- [Text Detection 004 Pre-trained Model](http://docs.openvinotoolkit.org/latest/_models_intel_text_detection_0004_description_text_detection_0004.html)
- [All Pre-trained Models in OpenVINO Zoo](https://software.intel.com/en-us/openvino-toolkit/documentation/pretrained-models)
- [Demo Working Link](http://docs.openvinotoolkit.org/latest/_demos_python_demos_text_spotting_demo_README.html)

## Text output (maybe)
- output[0] => classification
- output[1] => confidence

