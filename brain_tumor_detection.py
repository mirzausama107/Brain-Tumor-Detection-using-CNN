import cv2
import imutils
import numpy as np
import matplotlib.pyplot as plt

def crop_brain_contour(image, plot=False):
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)
    
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    extTop = tuple(c[c[:, :, 1].argmin()][0])
    extBot = tuple(c[c[:, :, 1].argmax()][0])
    
    new_image = image[extTop[1]:extBot[1], extLeft[0]:extRight[0]]            

    if plot:
        plt.figure()

        plt.subplot(1, 2, 1)
        plt.imshow(image)
        
        plt.tick_params(axis='both', which='both', 
                        top=False, bottom=False, left=False, right=False,
                        labelbottom=False, labeltop=False, labelleft=False, labelright=False)
        
        plt.title('Original Image')
            
        plt.subplot(1, 2, 2)
        plt.imshow(new_image)

        plt.tick_params(axis='both', which='both', 
                        top=False, bottom=False, left=False, right=False,
                        labelbottom=False, labeltop=False, labelleft=False, labelright=False)

        plt.title('Cropped Image')
        
        plt.show()
    
    return new_image
"""
from keras.models import load_model
new_model = load_model('brain-tumor-detection-CNN.h5')
#new_model.summary()

image = cv2.imread("2.jpeg")
#image.shape #(630,630,3)
image_size = (240,240)
image_width, image_height = image_size
image = crop_brain_contour(image, plot=False)
image = cv2.resize(image, dsize=(image_width, image_height), interpolation=cv2.INTER_CUBIC)
image = image / 255.
image = np.array(image).reshape(1,240,240,3)
#image.reshape(1,image_width, image_height,3)
image.shape #(240,240,3)
prediction = new_model.predict(image ,batch_size=32, verbose = 0)

#print(prediction)
"""