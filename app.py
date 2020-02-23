import argparse
import cv2
import numpy as np
import os

from openvino.inference_engine import IECore, IENetwork
import json

import pdffed
from time import time

# Get all the settings
options = None
with open("options.json", "r") as f:
    options = json.load(f)

# Get the mandatory options
DETECTOR_PATH = options["detector_model_xml"]
ENCODER_PATH = options["encoder_model_xml"]
DECODER_PATH = options["decoder_model_xml"]
THRESHOLD = float(options["probability_threshold"])
ALPHABET = options["alphabet"]
DEVICE = options["device_name"]

# Get the other options
CPU_EXT = options["CPU_extenstion_path"]

SOS_INDEX = 0
MAX_SEQ_LEN = 28
EOS_INDEX = 1
TOTAL_TASKS = 3
ALLOWED_DEVICES = ["CPU", "GPU", "FPGA", "HHDL", "MYRIAD"]

def files_exist(files):
    '''
    Checks if the files entered exist or not
    '''
    for file in files:
        if not os.path.isfile(file):
            return False
    return True

def check_extension(name, extension):
    '''
    Check if the file matches with the expected extension
    '''
    return name.lower().endswith(extension)

def check_options():
    '''
    Checks whether all options entered by the user in options.json are correct
    '''
    # Check if all the keys are correct
    assert list(options.keys()) == ['input', 'output', 'detector_model_xml', 'encoder_model_xml', 'decoder_model_xml', 'probability_threshold', 'alphabet', 'CPU_extenstion_path', 'device_name', 'jpegopt']
    
    # Retrieve the keys
    inputOpt = options["input"]
    output =  options["output"]
    detector_xml, encoder_xml, decoder_xml = options["detector_model_xml"], options["encoder_model_xml"], options["decoder_model_xml"]
    pt = float(options["probability_threshold"])
    alphabet = options["alphabet"]
    CPU = options["CPU_extenstion_path"]
    device_name = options["device_name"]
    jpegopt = options["jpegopt"]
    
    # Make sure the mandatory keys have values
    try:
        assert inputOpt and output and detector_xml and encoder_xml and decoder_xml and pt and alphabet and device_name
    except:
        print ("Error: One or more of the mandatory keys have no value. Refer to the README for the list of mandatory keys, and make sure they all have values")
        return -1
    
    # Check input and output
    if not (os.path.isfile(inputOpt) and check_extension(inputOpt, ".pdf")):
        print ("Error: Input file error. \nEither the file is missing, or the file isn't a PDF.")
        return -1
    if not (check_extension(output, ".txt") or check_extension(output, ".text")):
        print ("Error: Output file is not a text file. Text files can only end in 'txt' or 'text'")
        return -1
    
    # Check the models
    if not (
        check_extension(detector_xml, ".xml") and 
        check_extension(encoder_xml, ".xml") and 
        check_extension(decoder_xml, ".xml") and 
        files_exist([detector_xml, encoder_xml, decoder_xml])
    ):
        print("Error: The models are not supplied correctly. Please check all three models are provided.")
        return -1
    
    # Check the probability threshold
    if not (pt >=0 and pt <= 1):
        print ("Error: Probability threshold not in the correct range [0,1].")
        return -1
        
    # Check for the existence of CPU path
    if CPU_EXT and not os.path.isfile(CPU_EXT):
        print("CPU extension file does not exist")
        return -1
    
    # Check for correct device name
    if device_name not in ALLOWED_DEVICES:
        print ("Error: Device name invalid. Check README for the list of valid device names")
        return -1
        
    # Lastly, check for jpegopt
    quality, progressive, optimize = int(jpegopt["quality"]), jpegopt["progressive"], jpegopt["optimize"]
    if quality < 0 or quality > 100:
        print ("Error: Quality not in range [0, 100]")
        return -1
    if progressive not in ["True", "False"]:
        print ("Error: Progressive needs to a boolean")
        return -1
    if  optimize not in ["True", "False"]:
        print ("Error: Optimize needs to a boolean")
        return -1
    
    # If all goes well, flash the green signal
    return 0

def get_bin(xml):
    '''
    Given an XML path, return the corresponding BIN path
    '''
    return os.path.splitext(xml)[0] + ".bin"

def dump_text(texts):
    '''
    Dump the texts obtained onto the output file
    '''
    with open(options["output"], "a") as f:
        for text in texts:
            text = str(text) + " "
            f.write(text)
        f.write("\n\n")

def perform_inference():
    '''
    Performs inference on an input image, given a model.
    '''
    
    # Start the timer
    t1 = time()
    
    print("TASK 1 OF {}: Load the models".format(TOTAL_TASKS))
    # Get all the XML and BIN paths for all the models
    detector_xml = DETECTOR_PATH
    detector_bin = get_bin(detector_xml)
    
    encoder_xml = ENCODER_PATH
    encoder_bin = get_bin(encoder_xml)
    
    decoder_xml = DECODER_PATH
    decoder_bin = get_bin(decoder_xml)

    # Get network instances for all models
    ie = IECore()
    if CPU_EXT and "CPU" in DEVICE:
        ie.add_extension(CPU_EXT, "CPU")
    detector_net = IENetwork(model=detector_xml, weights=detector_bin)
    encoder_net = IENetwork(model=encoder_xml, weights=encoder_bin)
    decoder_net = IENetwork(model=decoder_xml, weights=decoder_bin)
    
    # Load these networks
    detector_exec = ie.load_network(network=detector_net, device_name=DEVICE, num_requests=2)
    encoder_exec = ie.load_network(network=encoder_net, device_name=DEVICE)
    decoder_exec = ie.load_network(network=decoder_net, device_name=DEVICE)
    print("TASK 1 DONE. All three models are loaded\n")
    
    # Obtain all the shapes needed
    hidden_shape = decoder_net.inputs["prev_hidden"].shape
    n, c, h, w = detector_net.inputs["im_data"].shape
    
    # The networks are no longer needed, so get rid of them
    del detector_net
    del encoder_net
    del decoder_net
    
    # Create a new output file for texts
    f = open(options["output"], "w")
    f.close()
    
    print("TASK 2 OF {}: Retrieve pages from the PDF document".format(TOTAL_TASKS))
    # Get all the images
    number_of_pages, image_objs = pdffed.pdf_to_images()
    pdffed.save_images(image_objs)
    
    images = []
    for i in range(number_of_pages):
        image = ".tmp/img-{}.jpeg".format(i)
        images.append(image)
    len_images = len(images)
    print("TASK 2 DONE. Total {} pages retrieved\n".format(len_images))
    
    print("TASK 3 OF {}: Extract text from all pages".format(TOTAL_TASKS))
    # Now loop through all the images, and perform inference on each one of them
    for index in range(len_images):
        print("Extracting text from page {} of {}".format(index+1, len_images))
        
        # Read the input image texts
        input_image = images[index]
        image = cv2.imread(input_image)
        scale_x = w / image.shape[1]
        scale_y = h / image.shape[0]
        image = cv2.resize(image, (w, h))
        
        # Apply preprocessing on the image
        image_size = image.shape[:2]
        image = np.pad(
            image, (
                (0, h - image_size[0]), 
                (0, w - image_size[1]),
                (0, 0)
            ),
            mode='constant', constant_values=0
        )
        image = image.transpose((2, 0, 1))
        image = image.reshape((n, c, h, w)).astype(np.float32)
        
        # Get the info for inference
        info = np.asarray([[image_size[0], image_size[1], 1]], dtype=np.float32)
    
        # Perform first inference - for text spotting - and parse the output
        output = detector_exec.infer({"im_data": image, "im_info": info})
    
        boxes = output["boxes"]
        scores = output["scores"]
        classes = output["classes"].astype(np.uint32)
        rms = output["raw_masks"]
        tfs = output["text_features"]
        
        # Filter out low-confidence entries
        filter_condition = scores > THRESHOLD
        boxes = boxes[filter_condition]
        scores = scores[filter_condition]
        classes = classes[filter_condition]
        rms = rms[filter_condition]
        tfs = tfs[filter_condition]
        
        boxes[:, 0::2] /= scale_x
        boxes[:, 1::2] /= scale_y
        
        texts = []
        for tf in tfs:
            # Perform the second inference - for text encoding
            tf = encoder_exec.infer({"input": tf})["output"]
            tf = np.reshape(tf, (tf.shape[0], tf.shape[1], -1))
            tf = np.transpose(tf, (0,2,1))
            
            hidden = np.zeros(hidden_shape) 
            prev_symbol_index = np.ones((1,)) * SOS_INDEX
    
            text = ""
            # Peform the third inference - for text decoding
            for i in range(MAX_SEQ_LEN):
                decoder_output = decoder_exec.infer({
                    "prev_symbol": prev_symbol_index,
                    "prev_hidden": hidden,
                    "encoder_outputs": tf
                })
    
                symbols_distr = decoder_output["output"]
                prev_symbol_index = int(np.argmax(symbols_distr, axis=1))
                if prev_symbol_index == EOS_INDEX or prev_symbol_index >= len(ALPHABET):
                    break
                text += ALPHABET[prev_symbol_index]
                hidden = decoder_output["hidden"]
            texts.append(text)
            
        pdffed.remove_image(index)
            
        # Now dump the texts onto a text file
        dump_text(texts)
        
        print("Text extracted from page {}".format(index+1))
    
    print("TASK 3 DONE. Please check the output file for the notes\n")
    
    # Clear the temp files
    pdffed.remove_temp()
    
    # Finally, stop the timer, and report time
    t2 = time()
    print("This entire operation was done in {:.2f} minutes".format((t2-t1)/60))


def main():
    if not check_options():
        perform_inference()
    else:
        print("Please make sure all options are entered correctly, and try again.")


if __name__ == "__main__":
    main()
