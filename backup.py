class StartScrapingPage(tk.Frame):
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.label = tk.Label(self.frame, text="Enter the code of the brick (e.g 3068)")
#         self.label.place(x = 40, y = 40)
        self.label.pack(side=LEFT, padx=40)
        vcmd = (master.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry = tk.Entry(self.master, validate = 'key', validatecommand = vcmd)
#         self.entry.pack(side="top", pady=40)
#         self.entry.place(x= 320, y = 40)
        self.label.pack(side=LEFT)
        self.button = tk.Button(self.frame, text = 'Create database from brickowl.com', width=200, command = self.test)
        self.button.pack(side=BOTTOM, padx=40, pady=80)
#         self.button.place(y = 80, x = 40)
        self.frame.pack()
        self.progress = Progressbar(self.frame, orient=HORIZONTAL,length=400,  mode='indeterminate')
        self.progress.pack()
#         self.progress.grid_forget()

    # This function is scraping the page
    # def scrape(self):



    def traitement(self):
        self.progress.grid()
        self.progress.start()
        time.sleep(15) 
        ## Just like you have many, many code lines...

        self.progress.stop()
        
    def test(self):
        print("Testing")

    # Source: https://stackoverflow.com/questions/8959815/restricting-the-value-in-tkinter-entry-widget
    def validate(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):

        if len(value_if_allowed) == 0:
            return True
        
        if value_if_allowed:
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False
        

