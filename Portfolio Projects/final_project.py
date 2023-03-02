# imports
import numpy as np
from developer_specific_addins import conn as conn
from functions import color_properties, quantify_blur
cursor = conn.cursor()

# get stage data
stage_dct = {}
cursor.execute("""SELECT Stage, SUM(BuyRating)/COUNT(*) as BuyRate
FROM PHOTO
WHERE BuyRating IS NOT NULL
GROUP BY Stage
ORDER BY BuyRate desc;""")
for x in cursor:
    y = ''
    if x[0] == 's':
        y = 'start'
    elif x[0] == 'u':
        y = 'uphill'
    elif x[0] == 'e':
        y = 'flat'
    elif x[0] == 'd':
        y = 'downhill'
    elif x[0] == 'f':
        y = 'finish'
    stage_dct[y] = float(x[1])

# get obstacle data
obstacle_dct = {}
cursor.execute("""SELECT Obstacle, SUM(BuyRating)/COUNT(*) as BuyRate
FROM PHOTO
WHERE BuyRating IS NOT NULL
GROUP BY Obstacle
ORDER BY BuyRate desc;""")
for x in cursor:
    if x[0] == 'y':
        y = 'yes'
    elif x[0] == 'n':
        y = 'no'
    obstacle_dct[y] = float(x[1])

# get horizontal angle data
horizontal_dct = {}
cursor.execute("""SELECT Horizontal, SUM(BuyRating)/COUNT(*) as BuyRate
FROM PHOTO
WHERE BuyRating IS NOT NULL
GROUP BY Horizontal
ORDER BY BuyRate desc;""")
for x in cursor:
    if x[0] == 'f':
        y = 'front'
    elif x[0] == 'd':
        y = 'diagonal'
    elif x[0] == 's':
        y = 'side'
    elif x[0] == 'b':
        y = 'back'
    horizontal_dct[y] = float(x[1])

# get vertical angle data
vertical_dct = {}
cursor.execute("""SELECT Vertical, SUM(BuyRating)/COUNT(*) as BuyRate
FROM PHOTO
WHERE BuyRating IS NOT NULL
GROUP BY Vertical
ORDER BY BuyRate desc;""")
for x in cursor:
    if x[0] == 'l':
        y = 'low'
    elif x[0] == 'm':
        y = 'mid'
    elif x[0] == 'h':
        y = 'high'
    vertical_dct[y] = float(x[1])

# get and sort blue data
blue_dct = {}
marks = [0, 25, 50, 75, 100, 255]
for i in range(len(marks)-1):
    cursor.execute("""SELECT SUM(BuyRating)/COUNT(PhotoID)
    FROM PHOTO
    WHERE BuyRating IS NOT NULL AND Blue BETWEEN %f AND %f;""" % (marks[i], marks[i+1]))
    for x in cursor:
        blue_dct[str(marks[i]) + ' to ' + str(marks[i+1])] = float(x[0])
blue_dct = dict(sorted(blue_dct.items(), reverse=True, key=lambda item: item[1]))

# get and sort green data
green_dct = {}
marks = [0, 25, 50, 75, 100, 255]
for i in range(len(marks)-1):
    cursor.execute("""SELECT SUM(BuyRating)/COUNT(PhotoID)
    FROM PHOTO
    WHERE BuyRating IS NOT NULL AND Green BETWEEN %f AND %f;""" % (marks[i], marks[i+1]))
    for x in cursor:
        green_dct[str(marks[i]) + ' to ' + str(marks[i+1])] = float(x[0])
green_dct = dict(sorted(green_dct.items(), reverse=True, key=lambda item: item[1]))

# get and sort red data
red_dct = {}
marks = [0, 25, 50, 75, 100, 255]
for i in range(len(marks)-1):
    cursor.execute("""SELECT SUM(BuyRating)/COUNT(PhotoID)
    FROM PHOTO
    WHERE BuyRating IS NOT NULL AND Red BETWEEN %f AND %f;""" % (marks[i], marks[i+1]))
    for x in cursor:
        red_dct[str(marks[i]) + ' to ' + str(marks[i+1])] = float(x[0])
red_dct = dict(sorted(red_dct.items(), reverse=True, key=lambda item: item[1]))

# get and sort blur data
blur_dct = {}
marks = [0, 500, 1000, 1500, 2000, 3000, 10000]
for i in range(len(marks)-1):
    cursor.execute("""SELECT SUM(BuyRating)/COUNT(PhotoID)
    FROM PHOTO
    WHERE BuyRating IS NOT NULL AND Blur BETWEEN %f AND %f;""" % (marks[i], marks[i+1]))
    for x in cursor:
        blur_dct[str(marks[i]) + ' to ' + str(marks[i+1])] = float(x[0])
blur_dct = dict(sorted(blur_dct.items(), reverse=True, key=lambda item: item[1]))

# get data for number of riders in photo when there are <= 5 riders, grouped by the number of riders
riders_dct = {}
for i in range(len(marks)-1):
    cursor.execute("""SELECT Riders, SUM(BuyRating)/COUNT(PhotoID) as BuyRating
    FROM PHOTO
    WHERE BuyRating IS NOT NULL AND Riders <= 5
    GROUP BY Riders
    ORDER BY Riders desc;""")
    for x in cursor:
        riders_dct[str(x[0])] = float(x[1])

# get data for number of riders in photo when there are > 5 riders
for i in range(len(marks)-1):
    cursor.execute("""SELECT SUM(BuyRating)/COUNT(PhotoID) as BuyRating
    FROM PHOTO
    WHERE BuyRating IS NOT NULL AND Riders >= 6
    ORDER BY Riders asc;""")
    for x in cursor:
        riders_dct["6+"] = float(x[0])
riders_dct = dict(sorted(riders_dct.items(), reverse=True, key=lambda item: item[1]))

# create data dictionary to store all dictionaries
probabilities = {
    "stage": stage_dct,
    "obstacle": obstacle_dct,
    "horizontal": horizontal_dct,
    "vertical": vertical_dct,
    "blue": blue_dct,
    "green": green_dct,
    "red": red_dct,
    "blur": blur_dct,
    "riders": riders_dct
}

# format data output
output = "stage: {stage}\n" \
      "obstacle: {obstacle}\n" \
      "horizontal: {horizontal}\n" \
      "vertical: {vertical}\n" \
      "blue: {blue}\n" \
      "green: {green}\n" \
      "red: {red}\n" \
      "blur: {blur}\n" \
      "riders: {riders}".format(**probabilities)

# print data to file
file = open("output_probabilities.json", 'w')
file.write(output)

# get a photo from user to check likelihood of it selling
user_photo = input("Enter the file path of the photo you want to check >> ")

# check photo for color and blur properties
red, green, blue = color_properties(user_photo)
blur = quantify_blur(user_photo)

# get keys to reference correct dictionary values
if red < 25:
    red_key = '0 to 25'
elif red < 50:
    red_key = '25 to 50'
elif red < 75:
    red_key = '50 to 75'
elif red < 100:
    red_key = '75 to 100'
elif red <= 255:
    red_key = '100 to 255'

if green < 25:
    green_key = '0 to 25'
elif green < 50:
    green_key = '25 to 50'
elif green < 75:
    green_key = '50 to 75'
elif green < 100:
    green_key = '75 to 100'
elif green <= 255:
    green_key = '100 to 255'

if blue < 25:
    blue_key = '0 to 25'
elif blue < 50:
    blue_key = '25 to 50'
elif blue < 75:
    blue_key = '50 to 75'
elif blue < 100:
    blue_key = '75 to 100'
elif blue <= 255:
    blue_key = '100 to 255'

if blur < 500:
    blur_key = '0 to 500'
elif blur < 1000:
    blur_key = '500 to 1000'
elif blur < 1500:
    blur_key = '1000 to 1500'
elif blur < 2000:
    blur_key = '1500 to 2000'
elif blur <= 3000:
    blur_key = '2000 to 3000'
elif blur <= 10000:
    blur_key = '3000 to 10000'

# have user input photo qualities for analysis
correct = 0
while correct < 6:
    correct = 0
    # input stage
    stage_key = input("stage: start,finish,uphill,downhill,flat>> ")
    if stage_key == 'start' or 'front' or 'uphill' or 'downhill' or 'flat':
        correct += 1
    # input obstacle
    obstacle_key = input("obstacle: yes, no>> ")
    if obstacle_key == 'yes' or 'no':
        correct += 1
    # input horizontal
    horizontal_key = input("horizontal angle: front,diagonal,side,back>> ")
    if horizontal_key == 'front' or 'diagonal' or 'side' or 'back':
        correct += 1
    # input vertical
    vertical_key = input("vertical angle: low,mid,high>> ")
    if vertical_key == 'low' or 'mid' or 'high':
        correct += 1
    #input riders
    riders_key = input("number of riders >> ")
    try:
        riders_key = int(riders_key)
        if riders_key >= 6:
            riders_key = '6+'
        else:
            riders_key = str(riders_key)
        correct += 1
    except:
        correct += 0
    # was everything entered correctly
    redo = input("redo entry? yes, no>> ")
    if redo == 'no':
        correct += 1

# list keys to use in searching probabilities dictionary and initialize list of probabilities
keys1 = ['red', 'green', 'blue', 'blur', 'stage', 'obstacle', 'horizontal', 'vertical']
keys2 = [red_key, green_key, blue_key, blur_key, stage_key, obstacle_key, horizontal_key, vertical_key]
prob_lst = []
try:
    prob_lst.append(probabilities['riders'][riders_key])
    keys1.append('riders')
    keys2.append(riders_key)
except:
    pass

# find which quality was the worst and what it's probability of sale is
min_prob = 1
idx = -1
for key1 in keys1:
    idx += 1
    prob = probabilities[key1][keys2[idx]]
    prob_lst.append(prob)
    if prob < min_prob:
        min_prob = prob
        poorest_quality = "%s: %s" % (key1, keys2[idx])

# define the probability that the photo sells
sale_prob = np.mean(prob_lst)

# output the probability of sale and the poorest quality in the photo
print("Probability of sale: ", sale_prob*100, "%")
print("your photos weakest quality is '" + str(poorest_quality) + "' which has a purchase rate of " + str(min_prob*100) + "%")


# C:/Users/light/Pictures/8.png