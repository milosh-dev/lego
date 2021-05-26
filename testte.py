import tkinter as tk
import os, cv2, json
from PIL import Image
from PIL import ImageTk
from shutil import copyfile

root = tk.Tk()
root.withdraw()

brick = '3068'
files = os.listdir('database/' + brick)

f = open('database/' + brick + '/database.json', 'r')
lego = json.load(f)
f.close()
    
current_window = None
counter = -1

def  replace_window(root):
    """Destroy current window, create new window"""
    global current_window
    if current_window is not None:
        current_window.destroy()
    current_window = tk.Toplevel(root)

    # if the user kills the window via the window manager,
    # exit the application. 
    current_window.wm_protocol("WM_DELETE_WINDOW", root.destroy)

    return current_window


def delete_file(file):
    global counter
    os.remove(file)
    counter -= 1
    new_window()
    

def copy_file(src, dst):
    global counter
    copyfile(src, dst)
    counter -= 1
    new_window()

def new_window():
    global counter
    global files
    global brick
    global lego
    counter += 1

    window = replace_window(root)
    label = tk.Label(window, text="This is window %s" % counter)
    
#     print(files[counter])
    try:
        image = cv2.imread('database/' + str(brick) + '/' + files[counter])
        corrected = cv2.imread('ai/' + str(brick) + '/' + files[counter])



        orig = 'database/' + str(brick) + '/' + files[counter]
        corr = 'ai/' + str(brick) + '/' + files[counter]
        
        if image is not None:
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            # the first panel will store our original image
            panelA = tk.Label(window, image=image)
            panelA.image = image
            panelA.pack(side="left", padx=10, pady=10)

        if corrected is not None:
            corrected = Image.fromarray(corrected)
            corrected = ImageTk.PhotoImage(corrected)
            # while the second panel will store the edge map
            panelB = tk.Label(window, image=corrected)
            panelB.image = corrected
            panelB.pack(side="right", padx=10, pady=10)
        
        btn_frame = tk.Frame(window)
        
        next = tk.Button(btn_frame, text="Next", command=new_window)
        label.pack(fill="both", expand=True, padx=20, pady=20)
        next.pack(side="bottom", padx=10, pady=10)
        
        delete = tk.Button(btn_frame, text="Delete")
        delete['command'] = lambda f = corr: delete_file(f)
        delete.pack(side="bottom", padx=10, pady=10)        
 
        copy = tk.Button(btn_frame, text="Copy")
        copy['command'] = lambda src = orig, dst = corr: copy_file(src, dst)
        copy.pack(side="bottom", padx=10, pady=10)        

        btn_frame.pack()
    except:
        pass

def copy():
    return

window = new_window()

