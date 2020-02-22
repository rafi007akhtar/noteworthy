import pdf2image
import json
import os
import shutil

def pdf_to_images():
    options = None
    with open("options.json", "r") as f:
        options = json.load(f)
    
    images = None
    with open(options["input"], "rb") as pdf:
        images = pdf2image.convert_from_bytes(
            pdf.read(), 
            jpegopt=options["jpegopt"],
            fmt="jpeg"
        )
    
    return len(images), images
    
def save_images(images):
    path = os.getcwd() + "/.temp"
    os.mkdir(path)
    for i in range(len(images)):
        image = images[i]
        image.save(".temp/img-{}.jpeg".format(i))

def remove_temp():
    shutil.rmtree(os.getcwd() + "/.temp")

# dry run the above functions
# images = pdf_to_images()
# save_images(images)


