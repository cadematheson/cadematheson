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
cursor.execute("SELECT PhotoID FROM PHOTO WHERE Horizontal IS NULL;")
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
        stage = input("stage (s,f,u,d,e)>>")
        obstacle = input("obstacle (y,n)>>")
        horizontal = input("horizontal (f,d,s,b)>>")
        vertical = input("vertical (l,m,h)>>")
        gender = input("gender (m,f)>>")
        redo = input("redo entry? (y,n)")
        if stage not in ('s', 'f', 'u', 'd', 'e') or obstacle not in ('y', 'n') or horizontal not in ('f', 'd', 's', 'b') or vertical not in ('l', 'm', 'h') or gender not in ('m', 'f') or redo not in ('y', 'n'):
            redo = 'y'
        if redo == 'y':
            print("redo the photo")
            True
        else:
            break

    # update database with manual data
    query = "UPDATE PHOTO SET Stage = '%s', Obstacle = '%s', Horizontal = '%s', Vertical = '%s', Gender = '%s' WHERE PhotoID = %d;" % (
    stage, obstacle, horizontal, vertical, gender, key)
    cursor.execute(query)
    conn.commit()
