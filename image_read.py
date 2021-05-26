# Source:
# https://stackoverflow.com/questions/46671348/make-a-pause-between-images-display-in-opencv
import cv2
import os



folder_path = 'database/test'#folder path to your images

for path in os.listdir(folder_path):#loop to read one image at a time 
    imgpath = os.path.join(folder_path, path)

    frame = cv2.imread(imgpath, 1)

    cv2.imshow('Window', frame)

    key = cv2.waitKey(3000)#pauses for 3 seconds before fetching next image
    if key == 27:#if ESC is pressed, exit loop
        cv2.destroyAllWindows()
        break
