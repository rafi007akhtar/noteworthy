import argparse
import cv2
import numpy as np
import os
import logging as log

from openvino.inference_engine import IECore, IENetwork
import json

import pdffed
from time import time

DETECTOR_PATH = "models/intel/text-spotting-0001-detector/FP32/text-spotting-0001-detector.xml"
ENCODER_PATH = "models/intel/text-spotting-0001-recognizer-encoder/FP32/text-spotting-0001-recognizer-encoder.xml"
DECODER_PATH = "models/intel/text-spotting-0001-recognizer-decoder/FP32/text-spotting-0001-recognizer-decoder.xml"
INPUT_STREAM = "input.jpg"
SOS_INDEX = 0
MAX_SEQ_LEN = 28
EOS_INDEX = 1

def get_args():
    '''
    Gets the arguments from the command line.
    '''

    parser = argparse.ArgumentParser("Basic Edge App with Inference Engine")
    # -- Create the descriptions for the commands

    c_desc = "CPU extension file location, if applicable"
    d_desc = "Device, if not CPU (GPU, FPGA, MYRIAD)"
    i_desc = "The location of the input image"
    detp_desc = "The location of the Text Detector model XML file"
    encp_desc = "The location of the Text Encoder model XML file"
    decp_desc = "The location of the Text Decoder model XML file"
    pt_desc = "The probability threshold"
    letters_desc = "Set of letters used for decoding"

    # -- Add required and optional groups
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    # -- Create the arguments
    optional.add_argument("-i", help=i_desc, default=INPUT_STREAM)
    optional.add_argument("-detp", help=detp_desc, default=DETECTOR_PATH)
    optional.add_argument("-encp", help=encp_desc, default=ENCODER_PATH)
    optional.add_argument("-decp", help=decp_desc, default=DECODER_PATH)
    optional.add_argument("-c", help=c_desc, default=None)
    optional.add_argument("-d", help=d_desc, default="CPU")
    optional.add_argument("-pt", help=pt_desc, default=0.5)
    optional.add_argument(
        "-letters", 
        help=letters_desc, 
        default="  0123456789abcdefghijklmnopqrstuvwxyz"
    )
    
    args = parser.parse_args()

    return args


def get_bin(xml):
    return os.path.splitext(xml)[0] + ".bin"

def perform_inference(args):
    '''
    Performs inference on an input image, given a model.
    '''
    
    # Start the timer
    t1 = time()
    
    print("TASK 1 of 3: Load the models")
    # Get all the XML and BIN paths for all the models
    detector_xml = args.detp
    detector_bin = get_bin(detector_xml)
    
    encoder_xml = args.encp
    encoder_bin = get_bin(encoder_xml)
    
    decoder_xml = args.decp
    decoder_bin = get_bin(decoder_xml)

    # Get network instances for all models
    ie = IECore()
    detector_net = IENetwork(model=detector_xml, weights=detector_bin)
    encoder_net = IENetwork(model=encoder_xml, weights=encoder_bin)
    decoder_net = IENetwork(model=decoder_xml, weights=decoder_bin)
    
    # Load these networks
    detector_exec = ie.load_network(network=detector_net, device_name=args.d, num_requests=2)
    encoder_exec = ie.load_network(network=encoder_net, device_name=args.d)
    decoder_exec = ie.load_network(network=decoder_net, device_name=args.d)
    print("TASK 1 DONE. All three models are loaded\n")
    
    # Obtain all the shapes needed
    hidden_shape = decoder_net.inputs["prev_hidden"].shape
    n, c, h, w = detector_net.inputs["im_data"].shape
    
    # The networks are no longer needed, so get rid of them
    del detector_net
    del encoder_net
    del decoder_net
    
    # Get all the settings
    options = None
    with open("options.json", "r") as f:
        options = json.load(f)
    
    # Create a new output file for texts
    f = open(options["output"], "w")
    f.close()
    
    print("TASK 2 OF 3: Retrieve pages from the PDF document")
    # Get all the images
    number_of_pages, image_objs = pdffed.pdf_to_images()
    pdffed.save_images(image_objs)
    
    images = []
    for i in range(number_of_pages):
        image = "temp/img-{}.jpeg".format(i)
        images.append(image)
    if not images:
        images = [args.i]
    print("TASK 2 DONE. Total {} pages retrieved\n".format(len(images)))
    
    print("TASK 3 OF 3: Extract text from all pages")
    # Now loop through all the images, and perform inference on each one of them
    for i in range(len(images)):
        page_number = i
        print("Extracting text from page {} of {}".format(page_number+1, len(images)))
        
        # Read the input image texts
        input_image = images[i]
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
        filter_condition = scores > args.pt
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
                if prev_symbol_index == EOS_INDEX or prev_symbol_index >= len(args.letters):
                    break
                text += args.letters[prev_symbol_index]
                hidden = decoder_output["hidden"]
            texts.append(text)
            
    
        # print(texts)
        
        # Now dump the texts onto a text file
        with open(options["output"], "a") as f:
            for text in texts:
                text = str(text) + " "
                f.write(text)
            f.write("\n\n")
        print("Text extracted from page {}".format(page_number+1))
    
    print("TASK 3 DONE. Please check the output file for the notes.\n")

    # Save down the resulting image
    # cv2.imwrite("outputs/{}-output.png".format(args.t), output_image)
    # cv2.imwrite("outputs/mask.png", mask)
    
    t2 = time()
    
    print("This entire operation was done in {:.2f} minutes".format((t2-t1)/60))


def main():
    args = get_args()
    perform_inference(args)


if __name__ == "__main__":
    main()
