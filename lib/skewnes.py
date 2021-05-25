# https://www.pyimagesearch.com/
# https://stackoverflow.com/questions/56905592/automatic-contrast-and-brightness-adjustment-of-a-color-photo-of-a-sheet-of-pape
# https://stackoverflow.com/questions/60867638/methods-for-detecting-a-known-shape-object-in-an-image-using-opencv
import cv2
import numpy as np
import argparse
import os

from matplotlib import pyplot as plt
from skimage import exposure


# Automatic brightness and contrast optimization with optional histogram clipping
# https://stackoverflow.com/questions/56905592/automatic-contrast-and-brightness-adjustment-of-a-color-photo-of-a-sheet-of-pape
def automatic_brightness_and_contrast(image, clip_hist_percent=1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index -1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum/100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size -1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)


# https://stackoverflow.com/questions/60867638/methods-for-detecting-a-known-shape-object-in-an-image-using-opencv
# Detect the font face of the tile
def rectangle_detection(img):
    
    debug_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binarized = cv2.threshold(debug_img, 50, 255, cv2.THRESH_BINARY)    
    contours, _ = cv2.findContours(binarized, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # detect all rectangles
    rois = []
    for contour in contours:
        if len(contour) < 4:
            continue
        cont_area = cv2.contourArea(contour)
        if not 1000 < cont_area < 15000: # roughly filter by the volume of the detected rectangles
            continue
        cont_perimeter = cv2.arcLength(contour, True)
        (x, y), (w, h), angle = rect = cv2.minAreaRect(contour)
        rect_area = w * h
        if cont_area / rect_area < 0.8: # check the 'rectangularity'
            continue        
        rois.append(rect)

    # save intermediate results in the debug folder
    rois_img = cv2.drawContours(image, contours, -1, (0, 0, 230))
    rois_img = cv2.drawContours(rois_img, [cv2.boxPoints(rect).astype('int32') for rect in rois], -1, (0, 230, 0))
    cv2.imshow('rec', rois_img)


def show_image(image):
    cv2.imshow('image',image)
    c = cv2.waitKey()
    if c >= 0 : return -1
    return 0

def handle_folders(brick):
    folder = str(brick)
    #################################
    # create folder, if it does not exist
    if not os.path.isdir('ai'):
        os.makedirs('ai')
        
    if not os.path.isdir('ai/' + folder):
        os.makedirs('ai/' + folder)


# Function to 
def correct(filename):
    try:
        # # Read the image
        image = cv2.imread('database/' + filename)

        # Determine a alpha channel threshold for rectangle detection (some images might need different value)
        # The detection determines the darkness range between minval and 255.  
        minval = 150

        # Start with showing the original image
        # cv2.imshow('original',image)

        # Create grayscale image for edge detection (grayscale works better for edge detection)
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(img_gray, 11, 17, 17)

        # detect edges
        edged = cv2.Canny(gray, 30, 200)

        # Find rectangles. Different images might need different threshold value
        # https://www.pyimagesearch.com/
        ret, im = cv2.threshold(img_gray, minval, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy  = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        epsilon = 0.1*cv2.arcLength(contours[0],True)
        approx = cv2.approxPolyDP(contours[0],epsilon,True)
        rect = cv2.minAreaRect(contours[0])

        # grab contours
        c = max(contours, key=cv2.contourArea)

        # determine the most extreme points (largest contour) along the contour
        extLeft = tuple(c[c[:, :, 0].argmin()][0])
        extRight = tuple(c[c[:, :, 0].argmax()][0])
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        extBot = tuple(c[c[:, :, 1].argmax()][0])

        #print(extLeft, extRight, extTop, extBot)

        # Find the topmost edge points of skewed image 
        pts1 = np.float32([extLeft, extBot, extTop, extRight])
        pts1 = np.float32([extLeft, extBot, extTop, extRight])

        # And correct the skewing to 256x256 image
        pts2 = np.float32([[0,0], [0,256], [256,0], [256,256]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        # Now we have our final image...
        final = cv2.warpPerspective(image, matrix, (256,256))

        # ... but we want to adjust the picture as well
        # sharpen the edges
        blur = cv2.GaussianBlur(final, (0,0), 3)
        sharp = cv2.addWeighted(final, 1.5, blur, -0.5, 0, blur);

        # Adjust exposure
        auto_result, alpha, beta = automatic_brightness_and_contrast(sharp)

        # Show the final corrected image
        # cv2.imshow('final', auto_result)

        # Save the final corrected image. This image will be used in image detection
        cv2.imwrite('ai/' + filename, auto_result)
    except:
        pass

def correct_files(brick):
    files = os.listdir('database/' + str(brick))
    for file in files:
        if file == 'database.json':
            next
        else:
            print(file)

correct('test.jpg')

# handle_folders(3070)
# correct_files(3070)

# ############
# # Most of the inspiration and a bulk of the code is from: https://www.pyimagesearch.com/
# ############
# filename = input("Please enter image name: ")
# # Start the program
# # Read the image
# image = cv2.imread(filename)
# # Determine a alpha channel threshold for rectangle detection (some images might need different value)
# # The detection determines the darkness range between minval and 255.  
# minval = 150
# 
# # Start with showing the original image
# cv2.imshow('original',image)
# 
# # Create grayscale image for edge detection (grayscale works better for edge detection)
# img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# gray = cv2.bilateralFilter(img_gray, 11, 17, 17)
# 
# # detect edges
# edged = cv2.Canny(gray, 30, 200)
# 
# # Find rectangles. Different images might need different threshold value
# # https://www.pyimagesearch.com/
# ret, im = cv2.threshold(img_gray, minval, 255, cv2.THRESH_BINARY_INV)
# contours, hierarchy  = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# epsilon = 0.1*cv2.arcLength(contours[0],True)
# approx = cv2.approxPolyDP(contours[0],epsilon,True)
# rect = cv2.minAreaRect(contours[0])
# 
# # grab contours
# c = max(contours, key=cv2.contourArea)
# 
# # determine the most extreme points (largest contour) along the contour
# extLeft = tuple(c[c[:, :, 0].argmin()][0])
# extRight = tuple(c[c[:, :, 0].argmax()][0])
# extTop = tuple(c[c[:, :, 1].argmin()][0])
# extBot = tuple(c[c[:, :, 1].argmax()][0])
# 
# #print(extLeft, extRight, extTop, extBot)
# 
# # Find the topmost edge points of skewed image 
# pts1 = np.float32([extLeft, extBot, extTop, extRight])
# pts1 = np.float32([extLeft, extBot, extTop, extRight])
# 
# # And correct the skewing to 256x256 image
# pts2 = np.float32([[0,0], [0,256], [256,0], [256,256]])
# matrix = cv2.getPerspectiveTransform(pts1, pts2)
# 
# # Now we have our final image...
# final = cv2.warpPerspective(image, matrix, (256,256))
# 
# # ... but we want to adjust the picture as well
# # sharpen the edges
# blur = cv2.GaussianBlur(final, (0,0), 3)
# sharp = cv2.addWeighted(final, 1.5, blur, -0.5, 0, blur);
# 
# # Adjust exposure
# auto_result, alpha, beta = automatic_brightness_and_contrast(sharp)
# 
# # Show the final corrected image
# cv2.imshow('final', auto_result)
# 
# # Save the final corrected image. This image will be used in image detection
# cv2.imwrite('final_' + filename, auto_result)
# 
# # Wait space key to exit the program 
# cv2.waitKey(0)
