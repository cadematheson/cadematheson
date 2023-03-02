# imports for Google Cloud Vision
import os
from google.cloud import vision

# import image processing tools
from developer_specific_addins import conn
import io
cursor = conn.cursor()

# AWS tool imports
import boto3
from developer_specific_addins import s3bucketname

# imports for blur function
from PIL import Image
from Helpers import *

# credentials for Google Vision API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "empyrean-bridge-339005-a9bfe6a20ac5.json"
client = vision.ImageAnnotatorClient()

# credentials for Amazon S3 bucket
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket = s3.Bucket(s3bucketname)

# function to detect the color properties of the photo
def color_properties(image_file):
    """Detects color properties in the image"""

    # prep image for google vision
    image_file = io.open(image_file, 'rb')
    content = image_file.read()
    image = vision.Image(content=content)

    # set up client for google cloud vision
    client = vision.ImageAnnotatorClient()
    response = client.image_properties(image=image)
    props = response.image_properties_annotation

    # initialize global color variables
    red = 0
    green = 0
    blue = 0

    # define color variables
    for color in props.dominant_colors.colors:
        fraction = float(format(color.pixel_fraction))
        r = float(format(color.color.red))
        red += fraction * r
        g = float(format(color.color.green))
        green += fraction * g
        b = float(format(color.color.blue))
        blue += fraction * b

    # errors
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return red, green, blue


# function to count the number of tags(riders recognized) in the photo
def count_tags(key):
    """counts the number of tags in each photo as recorded in the database"""
    query = "SELECT COUNT(Tag) FROM PHOTO as P JOIN PHOTO_ATHLETE as PA ON P.PhotoID = PA.PhotoID WHERE P.PhotoID = %d;" % key
    cursor.execute(query)
    for x in cursor:
        count = x[0]
    return count


def quantify_blur(image_file):
    """quantifies the amount of blur is in the photo
    lower blur number = more blur"""
    with io.open(image_file, 'rb') as image_file:
        filestr = image_file.read()
    npimg = np.frombuffer(filestr, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
    image = Helpers.resize(image, height=500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    print(blur)
    return blur


def get_data():
    # retrieve each photos s3 key from rds
    keys = []
    cursor.execute("SELECT PhotoID FROM PHOTO WHERE Blur <= 200;")
    for x in cursor:
        keys.append(x[0])

    # for each photo
    for key in keys:
        # get image from s3 and save
        print(key)
        full_key = 'unwatermarked/'+str(key)+'.png'
        image = bucket.Object(full_key)
        photo = image.get().get('Body').read()
        s3photo = Image.open(io.BytesIO(photo))
        path = ("C:/Users/light/Pictures/%d.png" % key)
        s3photo.save(path)
        s3photo.show()

        # run color_properties function
        red, green, blue = color_properties(path)

        #update database with all automated data
        query = "UPDATE PHOTO SET Red = '%d', Green = %d, Blue = %d, Riders = %d, Blur = %d WHERE PhotoID = %d;" % (red, green, blue, count_tags(key), quantify_blur(path), key)
        cursor.execute(query)
        conn.commit()
    return

get_data()




# end