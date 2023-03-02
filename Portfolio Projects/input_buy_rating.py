# import image processing tools
from developer_specific_addins import conn as conn
cursor = conn.cursor()

# AWS tool imports
import boto3
from developer_specific_addins import s3bucketname

# imports for blur function
import io
from PIL import Image

# credentials for Amazon S3 bucket
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket = s3.Bucket(s3bucketname)

keys = []
cursor.execute("SELECT PhotoID FROM PHOTO WHERE BuyRating IS NULL;")
for x in cursor:  # print updated record
    keys.append(x[0])

# for each photo
for key in keys:
    # get image from s3 and display
    full_key = 'unwatermarked/' + str(key) + '.png'
    image = bucket.Object(full_key)
    photo = image.get().get('Body').read()
    s3photo = Image.open(io.BytesIO(photo))
    s3photo.show()

    # manually enter qualities
    while True:
        buy = int(input("Buy Rating (0,1)>> "))
        if buy not in (0, 1):
            True
        else:
            break

    # update database with manual data
    query = "UPDATE PHOTO SET BuyRating = %d WHERE PhotoID = %d;" % (buy, key)
    cursor.execute(query)
    conn.commit()
