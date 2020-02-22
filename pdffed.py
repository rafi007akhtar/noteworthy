import pdf2image
import json
import os
import shutil

def pdf_to_images():
    '''
    Takes the PDF file, and converts each page into a PDF.
    Returns the number of images retrieved and the image objects.
    '''
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
    '''
    Takes the image objects as parameter and saves them onto a temp folder
    '''
    if os.path.isdir(".tmp"):
        remove_temp()
        
    os.mkdir(".tmp")
    for i in range(len(images)):
        image = images[i]
        image.save(".tmp/img-{}.jpeg".format(i))

def remove_image(index):
    '''
    Remove one of the images, identified by its index
    '''
    os.remove(".tmp/img-{}.jpeg".format(index))
    
def remove_temp():
    '''
    Removes the temp folder along with all its contents
    '''
    shutil.rmtree(".tmp")

# dry run the above functions
# images = pdf_to_images()
# save_images(images)


