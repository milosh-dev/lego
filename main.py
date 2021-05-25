########################
# This is for the main GUI
########################
import tkinter as tk
from tkinter import *
from tkinter.ttk import Progressbar

from lib import scraper
from lib import skewnes

import time
import json # used for creating json database
import os # usef for creating list of scraped images

# We use multiple windows, hence we are using classes
# The solution is based on the following source:
# https://stackoverflow.com/questions/16115378/tkinter-example-code-for-multiple-windows-why-wont-buttons-load-correctly
class StartPage(tk.Frame):
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
#         self.title("OpenCV database creating app")
#         self.geometry("900x600")
        self.label = tk.Label(self.frame,
                              text = "This app will create database of lego 2x2 tile bricks from brickowl.com website.\n" +
                              "After creating a database, a skewness of the photos is automatically corrected.\n" +
                              "Then user has a possibility to review all the corrected photos and adjust them, if needed. \n" +
                              "Finally the database is used via OpenCV for feature maching to find a brick type from user photo or video stream.\n\n" +
                              "The code is easily adjustable to other brick types as well.\n\nGeorgios Kontis\nRaoul Lättemäe")
        self.label.pack(side="top", padx=40, pady=40)
        self.frame.pack()
        self.buttons = tk.Frame(self.master)
        self.btn_scrape = tk.Button(self.buttons, text = '1. Scrape Lego Bricks', command = self.scrapingPage)
        self.btn_scrape.pack(side=LEFT, padx=20, pady=20)
        self.btn_correct = tk.Button(self.buttons, text = '2. Process Lego Images', command = self.correctingPage)
        self.btn_correct.pack(side=LEFT, padx=20, pady=20)
        self.btn_find = tk.Button(self.buttons, text = '3. Use for PhotoMatching', command = self.scrapingPage)
        self.btn_find.pack(side=LEFT, padx=20, pady=20)
        self.buttons.pack()

    def clean(self):
        self.button1 = tk.Button(self.frame, text = 'End', width=200, command = self.test)
        self.frame.pack()

    def scrapingPage(self):
        self.master.withdraw()
        self.newWindow = tk.Toplevel(self.master)
        self.newWindow.geometry("600x400")
        self.newWindow.title("Let's start scraping")
        self.app = StartScrapingPage(self.newWindow)

    def correctingPage(self):
        self.master.withdraw()
        self.newWindow = tk.Toplevel(self.master)
        self.newWindow.geometry("600x400")
        self.newWindow.title("Correct Images")
        self.app = CorrectPage(self.newWindow)


# Scraping page
class StartScrapingPage(tk.Frame):
    def __init__(self, master):
        self.master = master
        self.brick = StringVar(self.master)
        self.frame = tk.Frame(self.master)
        self.label = tk.Label(self.frame, text="Start scraping brick data").pack(side = TOP, padx=20, pady=20)
        self.label = tk.Label(self.frame, text="Enter the code of the brick (e.g 3068)").pack(side = LEFT, padx=20, pady=20)
        self.entry = tk.Entry(self.frame, textvariable=self.brick).pack(side = LEFT, padx=20, pady=20)
        self.frame.pack()

        self.progress_frame = tk.Frame(self.master)
        self.progress = Progressbar(self.progress_frame, value = 0, orient=HORIZONTAL, length=400, mode='determinate')
        self.prolabel = tk.Label(self.progress_frame, text="Wait. Downloading data...")
        self.progress_frame.pack()
#         self.prolabel.pack(side = BOTTOM, padx=20, pady=20)
        
#         self.button = tk.Button(self.frame_b, text = 'Start', width=200)
#         self.button['command'] = lambda idx = 1, binst=self.button: self.test(idx, binst)
                
        self.buttons = tk.Frame(self.master)
        self.button = tk.Button(self.buttons, text = 'Start', width=20, command = self.scrape)
        self.button.pack(side = LEFT, padx=20, pady=20)
        self.btn_home = tk.Button(self.buttons, text = 'Back to main screen', width=20, command = self.homePage)
        self.btn_home.pack(side = RIGHT, padx=20, pady=20)
#         self.progress
        self.buttons.pack()

    def homePage(self):
        self.master.withdraw()
        self.newWindow = tk.Toplevel(self.master)
        self.newWindow.geometry("800x400")
        self.newWindow.title("OpenCV database creating app")
        self.app = StartPage(self.newWindow)

    def test1(self):
        self.button.config(state = DISABLED)
        self.btn_home.config(state = DISABLED)
        self.update()
    
    def test(self, idx, binst):
#        binst.master.prolabel = tk.Label(self.frame_b, text="Downloading data...").pack(side = TOP, padx=20, pady=20)
#         binst.master.progress = Progressbar(self.frame_b, value = self.pr, orient=HORIZONTAL, length=400, mode='determinate')
        binst.destroy()
        self.run()
#         self.scrape()

    def run(self):
        self.prolabel.pack(side = TOP, padx=20, pady=20)
        self.progress.pack(padx=20, pady=10)
        self.button.config(state = DISABLED)
        self.btn_home.config(state = DISABLED)
        self.progress['maximum'] = 100
        for i in range(0, 100, 5):
            time.sleep(0.05)
            self.progress["value"] = i
            self.progress.update()
            self.progress["value"] = 0
        self.progress["value"] = 100

    def update(self):
        self.prolabel.pack(side = TOP, padx=20, pady=20)
        self.progress.pack(padx=20, pady=10)
        if self.progress['value'] < 100:
            self.progress['value'] += 0
            self.master.after(100, self.update)
        else:
            self.progress.destroy()
            self.prolabel['text'] = "Done: " + self.brick.get()
            
    # This function is scraping the page
    def scrape(self):
        brick = str(self.brick.get())
        if len(brick) == 0:
            return

        self.prolabel.pack(side = TOP, padx=20, pady=20)
        self.progress.pack(padx=20, pady=10)
        self.button.config(state = DISABLED)
        self.btn_home.config(state = DISABLED)
        self.progress['maximum'] = 100

        self.progress['value'] = 0
        self.progress.update()

        # Get number of pages
        last = scraper.get_pages(brick) + 1
        i = 1

        lego = scraper.handle_folders(brick)
        database = 'database/' + str(brick) + '/database.json'

        # Calculate progress step
        step = 100 / last

#         self.progress['value'] = step
#         self.progress.update()

        while i < last:
            scraper.iterator(brick, i, lego)
            self.progress['value'] += step
            self.progress.update()
            i += 1
        
        self.progress["value"] = 100
        
        # create a json file for database
        lego_json = json.dumps(lego)
        f = open(database, 'w')
        f.write(lego_json)
        f.close()

#         self.progress.destroy()
        self.prolabel['text'] = "Done! Downloaded information for " + str(len(lego)) + " bricks."        
        self.button.config(state = NORMAL)
        self.btn_home.config(state = NORMAL)

    # Return to the main screen
    def startPage(self):
        self.master.withdraw()
        self.newWindow = tk.Toplevel(self.master)
        self.newWindow.geometry("600x400")
        self.newWindow.title("Let's start")
        self.app = StartPage(self.newWindow)

# Correction page
class CorrectPage(tk.Frame):
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.label = tk.Label(self.frame, width=30, text="Select tile for skewness correction:").pack(side = LEFT, padx=20, pady=20)
        
        # Create dropdown list
        files = os.listdir('database')
        files.sort()
        self.file = StringVar()
        self.file.set(files[0]) # default value
        self.drop = tk.OptionMenu(self.frame, self.file, *files)
        self.drop.configure(width=20)
        self.drop.pack(side = RIGHT, padx=20, pady=20)
        self.frame.pack()
        # Progress bar
        self.progress_frame = tk.Frame(self.master)
        self.progress = Progressbar(self.progress_frame, value = 0, orient=HORIZONTAL, length=400, mode='determinate')
        self.prolabel = tk.Label(self.progress_frame, text="Wait. Correcting images...")
        self.progress_frame.pack()
        
        # Buttons
        self.buttons = tk.Frame(self.master)
        self.button = tk.Button(self.buttons, text = 'Start', width=20, command = self.process)
        self.button.pack(side = LEFT, padx=20, pady=20)
        self.btn_home = tk.Button(self.buttons, text = 'Back to main screen', width=20, command = self.homePage)
        self.btn_home.pack(side = RIGHT, padx=20, pady=20)
        self.buttons.pack()

    def process(self):
        self.prolabel.pack(side = TOP, padx=20, pady=20)
        self.progress.pack(padx=20, pady=10)
        self.button.config(state = DISABLED)
        self.btn_home.config(state = DISABLED)
        self.progress['maximum'] = 100
        
        # Get the selected brick
        brick = self.file.get()
        # Create folders for correcting bricks
        skewnes.handle_folders(brick)
        
        # Read a list of images from downloaded bricks
        files = os.listdir('database/' + str(brick))
        
        # Create step size for number of files
        step = 100 / len(files)
        
        # Handle files
        for file in files:
            # Skip the database file
            if file == 'database.json':
                next
            else:
                skewnes.correct(brick + '/' + file)
            # update progress bar
            self.progress['value'] += step
            self.progress.update()
            
#         for i in range(0, 100, 5):
#             time.sleep(0.05)
#             self.progress["value"] = i
#             self.progress.update()
#             self.progress["value"] = 0
#             
        self.progress["value"] = 100        
        self.prolabel['text'] = f"Done! Corrected {len(files)} bricks."        
        self.button.config(state = NORMAL)
        self.btn_home.config(state = NORMAL)
        

    # Return to the main screen
    def homePage(self):
        self.master.withdraw()
        self.newWindow = tk.Toplevel(self.master)
        self.newWindow.geometry("800x400")
        self.newWindow.title("OpenCV database creating app")
        self.app = StartPage(self.newWindow)
        
# Start with the main page
def main():
    window = Tk()
    app = StartPage(window)
    window.title("OpenCV database creating app")
    window.geometry("800x400")
    window.mainloop()

# Start with main window
main()
# print(os.getcwd())
# if name
# 
# # Button; function sayHello is associated with a button
# but = Button(window, text="Say Hello!", command=scraper.test)
# but.place(x=70, y=40, width=150)
# 
# window.mainloop()