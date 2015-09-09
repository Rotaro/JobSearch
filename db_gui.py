import tkinter as tk
import textwrap
import sys
from collections import OrderedDict



class JobSearchGUI(tk.Frame):
    """
    Application with GUI for classifying search results.

    db_data - Database data as a 2D-array or -tuple.
    """

    #db_data structure
    db_data_columns = ['site', 'search term', 'id', 'title', 'url', 
                           'description', 'date','language', 'relevant',
                           'recommendation']
    #options to show for classification
    language_options = [None, 'English', 'Finnish']
    relevant_options = [None, 0, 1]

    def __init__(self, db_data):
        if (len(db_data) == 0):
            sys.exit()
        #make dictionary of data
        self.dataStorage = OrderedDict()
        for entry in db_data:
            self.dataStorage[entry[2]] = list(entry)
        
        #init window, canvas needed for scrollbars
        self.parent = tk.Tk() #=root
        tk.Frame.__init__(self, self.parent)
        self.canvas = tk.Canvas(self.parent, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#000000")
        self.vsb = tk.Scrollbar(self.parent, orient="vertical", 
                                command=self.canvas.yview)
        self.hsb = tk.Scrollbar(self.parent, orient="horizontal", 
                                command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.configure(xscrollcommand=self.hsb.set)
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", 
                                  tags="self.frame")
        self.frame.bind("<Configure>", self.onFrameConfigure)

        #store the table (grid) widgets for access later
        self.frame._widgets = []
        self.populateTable()

        

    def populateTable(self):
        """
        Populates GUI table with database information stored in the object's
        dataStorage variable. Should only be called while GUI is active.
        """
        if (self.dataStorage == None or self.frame == None):
            return 
        #clear old widgets if necessary
        if (len(self.frame._widgets) != 0):
            for row in self.frame._widgets:
                for widget in row:
                    widget.destroy()
        self.frame._widgets = []

        #table headers
        current_row = []
        for column in range(0, len(self.db_data_columns)):
            label = tk.Label(self.frame, text = "%s" % self.db_data_columns[column],
                              borderwidth=0)
            label.grid(row=0, column=column, sticky="nsew", padx=1, pady=1)
            current_row.append(label)
            # set weights for columns
            if(column == 6):
                self.frame.grid_columnconfigure(column, weight=2)
            else:
                self.frame.grid_columnconfigure(column, weight=1)
        self.frame._widgets.append(current_row)

        #Buttons
        button = tk.Button(self.frame,text="Store data and reload", 
                           command=self.storeReloadData)
        button.grid(row=1, column=len(self.db_data_columns), sticky="nsew", 
                    padx=1, pady=1)
        button = tk.Button(self.frame,text="Store data and exit", 
                           command=self.storeDataExit)
        button.grid(row=2, column=len(self.db_data_columns), sticky="nsew", 
                    padx=1, pady=1)
        
        #process database data     
        i=1
        for id in self.dataStorage:
            current_row = []
            print(self.dataStorage[id][8])
            #if not classified
            if (self.dataStorage[id][8] == None):
                for column in range(0, len(self.dataStorage[id])):
                    #Divide table text into lines and set widths of columns. Also 
                    #initialize optionmenus for language and relevant columns.
                    if(self.db_data_columns[column] == "url"):
                        label = tk.Label(self.frame, text = "%s" % "\n".join(
                            textwrap.wrap(self.dataStorage[id][column], 100)),
                            borderwidth=0,width=1)
                        label.grid(row=i, column=column, sticky="nsew", padx=1, pady=1)
                    elif(self.db_data_columns[column] == "description"):
                        label = tk.Label(self.frame, text = "%s" %
                            "\n".join(textwrap.wrap(self.dataStorage[id][column], 100)),
                            borderwidth=0)
                        label.grid(row=i, column=column, sticky="nsew", padx=1, pady=1)
                    elif(self.db_data_columns[column] == "language"):
                        variable = tk.StringVar(self.frame)
                        variable.set(self.dataStorage[id][column])
                        label = tk.OptionMenu(self.frame, variable,
                                              *self.language_options)
                        #store as attribute to access later (might be another way?)
                        label.variable = variable
                        label.grid(row=i, column=column, sticky="nsew", padx=1, pady=1)
                    elif(self.db_data_columns[column] == "relevant"):
                        variable = tk.StringVar(self.frame)
                        variable.set(self.dataStorage[id][column])
                        label = tk.OptionMenu(self.frame, variable, 
                                              *self.relevant_options)
                        #store as attribute to access later (might be another way?)
                        label.variable = variable
                        label.grid(row=i, column=column, sticky="nsew", padx=1, pady=1)
                    else:
                        label = tk.Label(self.frame, text = "%s" % 
                                         (self.dataStorage[id][column]), borderwidth=0)
                        label.grid(row=i, column=column, sticky="nsew", padx=1, pady=1)
                    current_row.append(label)
                self.frame._widgets.append(current_row)
                print(i)
                i = i + 1
               

    def onFrameConfigure(self, event):
        """
        Reset the scroll region to encompass the inner frame.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def collectTableData(self):
        """
        Collects data from GUI table nd stores it in the object variable
        dataStorage. Should only be called while GUI is active.
        """
        if (self.dataStorage == None or self.frame == None):
            return 
        else:
            for i in range(1, len(self.frame._widgets)):
                id = self.frame._widgets[i][2]["text"]
                if (self.frame._widgets[i][7].variable.get() == 'None'):
                    self.dataStorage[id][7] = None
                else:
                    self.dataStorage[id][7] = self.frame._widgets[i][7].variable.get();
                if (self.frame._widgets[i][8].variable.get() == 'None'):
                    self.dataStorage[id][8] = None
                else:
                    self.dataStorage[id][8] = self.frame._widgets[i][8].variable.get();

     
    def storeReloadData(self):
        """
        Stores data from GUI table and reloads entries which haven't been
        classified. Should only be called while GUI is active.
        """
        if (self.dataStorage == None or self.frame == None):
            return 
        print("length ", len(self.frame._widgets), len(self.dataStorage))
        self.collectTableData()
        print("collected")
        print("length ", len(self.frame._widgets), len(self.dataStorage))
        self.populateTable()
        print("populated")
        print("length ", len(self.frame._widgets), len(self.dataStorage))

    def storeDataExit(self):
        """
        Stores data from GUI table and exits.
        """
        if (self.dataStorage == None or self.frame == None):
            return 
        self.collectTableData()
        self.parent.destroy()
        