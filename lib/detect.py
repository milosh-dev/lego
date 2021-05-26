#####################
# This module is detecting the lego's
#####################
import cv2
import numpy as np
import os
import json

path = 'ai/3068'
orb = cv2.ORB_create(nfeatures=1000)
images = []
classNames = []
myList = os.listdir(path)

f = open('database/3068/database.json')
lego = json.load(f)
f.close()

#print('Kokku leitud klasse', len(myList))

for cl in myList:
    imgCur = cv2.imread(f'{path}/{cl}', 0)
    images.append(imgCur)
    classNames.append(os.path.splitext(cl)[0])

#print(classNames)

def findDes(images):
    desList = []
    for img in images:
        kp, des = orb.detectAndCompute(img, None)
        desList.append(des)
    return desList

def findID(img, desList, thres = 15):
    kp2, des2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher()
    matchList = []

    finalVal = -1
    try:
        for des in desList:
            matches = bf.knnMatch(des, des2, k = 2)
            good = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good.append([m])
            matchList.append(len(good))
#    print(matchList)
    except:
        pass

#     if len(good) > 10:
#         print('leitud')
#         query_pts = np.float32([kp[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
#         train_pts = np.float32([kp2[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)
#         matrix, mask = cv2.findHomography(query_pts, train_pts, cv2.RANSAC, 5.0)
#         matches_mask = mask.ravel().tolist()
# 
#         # Perspective transform
#         h, w = img.shape
#         pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
#         dst = cv2.perspectiveTransform(pts, matrix)
# 
#         homography = cv2.polylines(frame, [np.int32(dst)], True, (255, 0, 0), 3)
#         cv2.imshow("Homography", homography)

    if len(matchList) != 0:
        if max(matchList) > thres:
            finalVal = matchList.index(max(matchList))


    return finalVal


def detect(image):
    global images
    global lego
    desList = findDes(images)
    # print(len(desList))
    # cap = cv2.VideoCapture(0)

    # success, img2 = cap.read()
    imgOriginal = image.copy()
    img2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    id = findID(img2, desList)

    # If we found a match
    if id != -1:
        return lego[classNames[id]]
    else:
        return {}
#         cv2.putText(imgOriginal, lego[classNames[id]]['name'], (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)

#     cv2.imshow('img2', imgOriginal)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         quit()