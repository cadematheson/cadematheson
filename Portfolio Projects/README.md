This project was done in an attempt to (1) understand what will increase the odds of a photo being downloaded, and (2) predict what photos have the greatest odds of being downloaded.

PhotoHive.pro is a website that my twin brother and I built for my family's company. It is used as a place for endurance race (run, bike, triathlon) photos to be uploaded and stored, such that athletes can easily search for their photos. Each photo, when uploaded, is put through the google-vision api to find the race number of each racer in the photo. This is how athletes will look for their race photos.

We had to manually create our dataset, which included over 600 photos, and 16 predictor variables. The outcome was binary classification. I wrote scripts to pull photos from the database, and show them on the screen one at a time. Then, we had a PhotoHive employee go through each photo, labeling it properly. These scripts are included.

The prediction portion was made before I learned machine learning, which is why it is done without machine learing. When PhotoHive deploys this project for advanced analytics in the future I will update this.
