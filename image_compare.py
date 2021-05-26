# USAGE
# tkinter_test.py

# import the necessary packages
from tkinter import *
from PIL import Image
from PIL import ImageTk
import cv2, os, time

def  replace_window(root):
    """Destroy current window, create new window"""
    global current_window
    if current_window is not None:
        current_window.destroy()
    current_window = Toplevel(root)

    # if the user kills the window via the window manager,
    # exit the application. 
    current_window.wm_protocol("WM_DELETE_WINDOW", root.destroy)

    return current_window

def select_image():
    # grab a reference to the image panels
#     root = Tk()
    window = replace_window(root)
    global panelA, panelB
    brick = 'test'
    
#     print(os.getcwd())

    # open a file chooser dialog and allow the user to select an input
    # image
    # path = 'test' #tkFileDialog.askopenfilename()
    
    files = os.listdir('database/' + str(brick))
    for file in files:
        if file == 'database.json':
            next
        else:
            image = cv2.imread('database/' + str(brick) + '/' + file)
            corrected = cv2.imread('ai/' + str(brick) + '/' + file)

        # convert the images to PIL format...
        image = Image.fromarray(image)
        corrected = Image.fromarray(corrected)

        # ...and then to ImageTk format
        image = ImageTk.PhotoImage(image)
        corrected = ImageTk.PhotoImage(corrected)
        
        if image is not None:
            # the first panel will store our original image
            panelA = Label(window, image=image)
            panelA.image = image
            panelA.pack(side="left", padx=10, pady=10)

        if corrected is not None:
            # while the second panel will store the edge map
            panelB = Label(window, image=corrected)
            panelB.image = corrected
            panelB.pack(side="right", padx=10, pady=10)
            
#         root.mainloop()
        #key = cv2.waitKey(3000)#pauses for 3 seconds before fetching next image
        time.sleep(1)
        print("n")
#         root.quit()
#         if key == 27:#if ESC is pressed, exit loop
#             cv2.destroyAllWindows()
#             break

 
# initialize the window toolkit along with the two image panels
# root = Tk()
panelA = None
panelB = None

root = Tk()
root.withdraw()
current_window = None

select_image()

# create a button, then when pressed, will trigger a file chooser
# dialog and allow the user to select an input image; then add the
# button the GUI
# btn = Button(root, text="Alusta", command=select_image)
# btn.pack(side="bottom", fill="both", expand="yes", padx="10", pady="10")

# kick off the GUI
# root.mainloop()