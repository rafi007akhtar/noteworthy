import argparse
import cv2
from inference import Network

INPUT_STREAM = "input.mp4"
# CPU_EXTENSION = "/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so"
CPU_EXTENSION = None
# fourcc = 0X00000021
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
# fourcc = cv2.cv.CV_FOURCC(*'H264')

def get_args():
    '''
    Gets the arguments from the command line.
    '''
    parser = argparse.ArgumentParser("Run inference on an input video")
    # -- Create the descriptions for the commands
    m_desc = "The location of the model XML file"
    i_desc = "The location of the input file"
    d_desc = "The device name, if not 'CPU'"
    ### TODO: Add additional arguments and descriptions for:
    ###       1) Different confidence thresholds used to draw bounding boxes
    ###       2) The user choosing the color of the bounding boxes
    c_desc = "The color of the bounding box to draw: RED, GREEN, or BLUE"
    ct_desc = "The confidence threshold"

    # -- Add required and optional groups
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    # -- Create the arguments
    required.add_argument("-m", help=m_desc, required=True)
    optional.add_argument("-i", help=i_desc, default=INPUT_STREAM)
    optional.add_argument("-d", help=d_desc, default='CPU')
    optional.add_argument("-c", help=c_desc, default="RED")
    optional.add_argument("-ct", help=ct_desc, default=0.5)
    args = parser.parse_args()

    return args

def convert_color(color):
    colors = {"RED": (0, 0, 255), "GREEN": (0, 255, 0), "BLUE": (255, 0, 0)}
    converted_color = colors[color]
    if converted_color:
        return converted_color
    return colors["RED"]
    
def draw_boxes(frame, res, args, width, height):
    """
    Draw the bouding boxes on the frame
    """
    for box in res[0][0]:
        conf = box[2]
        if conf >= float(args.ct):
            xmin = int(box[3] * width)
            ymin = int(box[4] * height)
            xmax = int(box[5] * width)
            ymax = int(box[6] * height)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), convert_color(args.c), 1)
    return frame


def infer_on_video(args):
    ### TODO: Initialize the Inference Engine
    plugin = Network()

    ### TODO: Load the network model into the IE
    exec_net = plugin.load_model(model=args.m, device=args.d, cpu_extension=CPU_EXTENSION)
    shape = plugin.get_input_shape()

    # Get and open video capture
    cap = cv2.VideoCapture(args.i)
    cap.open(args.i)

    # Grab the shape of the input 
    width = int(cap.get(3))
    height = int(cap.get(4))

    # Create a video writer for the output video
    # The second argument should be `cv2.VideoWriter_fourcc('M','J','P','G')`
    # on Mac, and `0x00000021` on Linux
    out = cv2.VideoWriter('out.mp4', fourcc, 30, (width,height))
    
    # Process frames until the video ends, or process is exited
    while cap.isOpened():
        # Read the next frame
        flag, frame = cap.read()
        if not flag:
            break
        key_pressed = cv2.waitKey(60)

        ### TODO: Pre-process the frame
        prepro = cv2.resize(frame, (shape[3], shape[2]))
        prepro = prepro.transpose((2,0,1))
        prepro = prepro.reshape(1, *prepro.shape)

        ### TODO: Perform inference on the frame
        plugin.async_inference(prepro)

        ### TODO: Get the output of inference
        if plugin.wait() == 0:
            res = plugin.extract_output()
            ### TODO: Update the frame to include detected bounding boxes
            frame = draw_boxes(frame, res, args, width, height)
            # Write out the frame
            out.write(frame)
        
        # Break if escape key pressed
        if key_pressed == 27:
            break

    # Release the out writer, capture, and destroy any OpenCV windows
    out.release()
    cap.release()
    cv2.destroyAllWindows()


def main():
    args = get_args()
    infer_on_video(args)


if __name__ == "__main__":
    main()
