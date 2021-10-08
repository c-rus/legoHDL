################################################################################
#   Project: legohdl
#   Script: gui.py
#   Author: Chase Ruskin
#   Description:
#       This script contains the class describing the settings GUI framework
#   and behavior for interacting, modifying, and saving settings.
################################################################################

import logging as log
import os
from tkinter.constants import ON
from .apparatus import Apparatus as apt

import_success = True
try:
    import tkinter as tk
    from tkinter.ttk import *
except ModuleNotFoundError:
    import_success = False

class GUI:

    def __init__(self):
        '''
        Create a Tkinter object.
        '''
        if(import_success == False):
            log.error("Failed to open GUI for settings (unable to find tkinter).")
            return None
        
        self._window = tk.Tk()
        #add icon
        file_path = os.path.realpath(__file__)
        head,_ = os.path.split(file_path)
        img = tk.Image("photo", file=head+'/data/icon.gif')
        self._window.tk.call('wm','iconphoto', self._window._w, img)
        #set the window size
        self._width,self._height = 800,600
        self._window.geometry(str(self.getW())+"x"+str(self.getH()))
        #constrain the window size
        self._window.wm_resizable(False, False)
        self._window.title("legoHDL settings")
        #center the window
        self._window = self.center(self._window)

        self.initPanes()
        #enter main loop
        try:
            self._window.mainloop()
        except KeyboardInterrupt:
            log.info("Exiting GUI...")
        pass

    def getW(self):
        return self._width

    def getH(self):
        return self._height

    def initPanes(self):
        #divide window into 2 sections
        #m1 = tk.PanedWindow(self._window, orient='horizontal', sashrelief=tk.RAISED)
        #configure size for both sections
        menu_width = int(self.getW()/6)
        field_width = self.getW() - menu_width
        bar_height = int(self.getH()/10)
        field_height = self.getH() - bar_height
        self._field_bg = '#CCCCCC'

        #create the main divisions
        menu_frame = tk.PanedWindow(self._window, width=menu_width, height=self.getH())
        self._field_frame = tk.LabelFrame(self._window, width=field_width, height=field_height, relief=tk.RAISED, padx=20, pady=20)
        bar_frame = tk.Frame(self._window, width=field_width, height=bar_height, relief=tk.SUNKEN)
        # don't resize frames to fit content
        bar_frame.grid_propagate(0)
        self._field_frame.grid_propagate(0)

        #layout all of the frames
        self._window.grid_rowconfigure(1, weight=1)
        self._window.grid_columnconfigure(0, weight=1)

        menu_frame.grid(row=1, sticky='w')
        self._field_frame.grid(row=1, sticky='nse')
        self._field_frame.grid_columnconfigure(0, weight=1)
        bar_frame.grid(row=2, sticky='nsew')
    
        # --- menu pane ---
        #configure side menu
        items = tk.StringVar(value=list(apt.SETTINGS.keys()))
        self._menu_list = tk.Listbox(self._window, listvariable=items, selectmode='single', relief=tk.SUNKEN)
        #configure actions when pressing a menu item
        self._menu_list.bind('<Double-1>', self.select)
        #add to the pane
        menu_frame.add(self._menu_list)

        self._act_ws = tk.StringVar(value=apt.SETTINGS['general']['active-workspace'])
        self._mult_dev = tk.IntVar(value=int(apt.SETTINGS['general']['multi-develop']))
        self._ovlp_rec = tk.IntVar(value=int(apt.SETTINGS['general']['overlap-recursive']))
        self._tgl_labels = tk.IntVar(value=0)
        self._ref_rate = tk.IntVar(value=int(apt.SETTINGS['general']['refresh-rate']))

        # --- field frame ---
        #configure field frame widgets
        self._field_title = tk.Label(self._field_frame, text='general', bg=self._field_bg)
        self._cur_widgets = []
        self.load('market')

        # --- bar frame ---
        #configure bar frame widgets
        btn_save = tk.Button(bar_frame, text='apply', command=self.save, relief=tk.RAISED)
        btn_cancel = tk.Button(bar_frame, text='cancel', command=self._window.quit, relief=tk.RAISED)

        #place on bar frame
        btn_save.place(x=self.offsetW(-0.3),y=self.offsetH(0.2, bar_height))
        btn_cancel.place(x=self.offsetW(-0.18),y=self.offsetH(0.2, bar_height))
        pass

    def clrFieldFrame(self):
        for widgets in self._field_frame.winfo_children():
            widgets.destroy()

    def offsetW(self, f, w=None):
        if(w == None):
            w = self.getW()
        if(f < 0):
            return w+int(w*f)
        else:
            return int(w*f)

    def offsetH(self, f, h=None):
        if(h == None):
            h = self.getH()
        if(f < 0):
            return h-int(h*f)
        else:
            return int(h*f)

    def save(self):
        log.info("Settings saved.")
        pass

    def select(self, event):
        '''
        Based on button click, select which section to present in the fields
        area of the window.
        '''
        i = self._menu_list.curselection()
        if i != ():
            sect = self._menu_list.get(i)  
            self.load(section=sect)
        pass

    def load(self, section):
        print('Loading',section+'...')
        #refresh to get w and h
        self._window.update_idletasks()
        w = self._field_frame.winfo_width()
        h = self._field_frame.winfo_height()
        #clear all widgets from the frame
        self.clrFieldFrame()
        #re-write section title widget
        self._field_frame.config(text=section)

        def display_fields(field_map, i=0):
            for field,value in field_map.items():
                #skip profiles field
                if(field == 'profiles'):
                    continue
                #create widgets
                widg = tk.Label(self._field_frame, text=field)
                widg.grid(row=i, column=0, padx=10, pady=10)
                #widg.place(x=self.offsetW(0.1,w), y=self.offsetH(i,h))
                
                if(isinstance(value, str) or value == None):
                    #special case for 'active-workspace'
                    if(field == 'active-workspace'):
                        #sel = tk.StringVar(master=self._field_frame)
                        #sel.set(apt.SETTINGS['general']['active-workspace'])
                        entry = tk.ttk.Combobox(self._field_frame, textvariable=self._act_ws, values=list(apt.SETTINGS['workspace'].keys()))
                        print(entry.get())
                    else:
                        entry = tk.Entry(self._field_frame, width=40)
                        if(value == None):
                            value = ''
                        entry.insert(tk.END, str(value))
                    entry.grid(row=i, column=2, columnspan=2, padx=10, pady=10, sticky='e')
 
                elif(isinstance(value, bool)):
                    if(field == 'overlap-recursive'):
                        box = tk.Radiobutton(self._field_frame, indicatoron=0, text='on', variable=self._ovlp_rec, value=1, width=8)
                        box2 = tk.Radiobutton(self._field_frame, indicatoron=0, text='off', variable=self._ovlp_rec, value=0, width=8)
                    elif(field == 'multi-develop'):
                        box = tk.Radiobutton(self._field_frame, indicatoron=0, text='on', variable=self._mult_dev, value=1, width=8)
                        box2 = tk.Radiobutton(self._field_frame, indicatoron=0, text='off', variable=self._mult_dev, value=0, width=8)
                    
                    box.grid(row=i, column=2, padx=10, pady=10, sticky='e')
                    box2.grid(row=i, column=3, padx=10, pady=10, sticky='e')
                elif(isinstance(value, int)):
                    #refresh-rate
                    wheel = tk.ttk.Spinbox(self._field_frame, from_=-1, to=1440, textvariable=self._ref_rate, wrap=True)
                    wheel.grid(row=i, column=2, columnspan=2, padx=10, pady=10, sticky='e')
                i += 1
                if(isinstance(value,dict)):
                    #print(value)
                    i = display_fields(value, i)
            return i

        if(section == 'general'):
            #map widgets
            display_fields(apt.SETTINGS[section])
            pass
        elif(section == 'label'):
            #create a new frame for the scripts table
            m_frame = tk.Frame(self._field_frame)
            m_frame.grid(row=1,column=0, columnspan=10, sticky='nsew')
            #create the table object
            tb = Table(m_frame, 'Name (@)', 'File extension')
            
            def loadShallowTable(event=None):
                #clear all records
                tb.clearRecords()
                for key,val in apt.SETTINGS['label']['shallow'].items():
                    tb.insertRecord([key,val])

            def loadRecursiveTable(event=None):
                #clear all records
                tb.clearRecords()
                for key,val in apt.SETTINGS['label']['recursive'].items():
                    tb.insertRecord([key,val])
                
            # radio buttons toggle between recursive table and shallow table  
            btn_shallow = tk.Radiobutton(self._field_frame, indicatoron=0, text='shallow', variable=self._tgl_labels, value=0, width=8, bd=1, command=loadShallowTable)
            btn_depth = tk.Radiobutton(self._field_frame, indicatoron=0, text='recursive', variable=self._tgl_labels, value=1, width=8, bd=1, command=loadRecursiveTable)
            btn_shallow.grid(row=0, column=0, pady=10, padx=10)
            btn_depth.grid(row=0, column=1, pady=10)
            
            tb.mapPeripherals(self._field_frame, 1)
            #load the table elements from the settings
            loadShallowTable()
            
            pass
        elif(section == 'script'):
            #create a new frame for the scripts table
            m_frame = tk.Frame(self._field_frame)
            m_frame.grid(row=0,column=0, columnspan=10, sticky='nsew')
            #create the table object
            tb = Table(m_frame, 'alias', 'command')
            tb.mapPeripherals(self._field_frame, 0)
            #load the table elements from the settings
            for key,val in apt.SETTINGS['script'].items():
                tb.insertRecord([key,val])
            pass
        elif(section == 'workspace'):
            #create a new frame for the scripts table
            m_frame = tk.Frame(self._field_frame)
            m_frame.grid(row=0,column=0, columnspan=10, sticky='nsew')
            #create the table object
            tb = Table(m_frame, 'name', 'path', 'markets')
            tb.mapPeripherals(self._field_frame, 0)
            #load the table elements from the settings
            for key,val in apt.SETTINGS['workspace'].items():
                fields = [key]+list(val.values())
                #convert any lists to strings seperated by commas
                for ii in range(len(fields)):
                    if isinstance(fields[ii], list):
                        str_list = ''
                        for f in fields[ii]:
                            str_list = str_list + str(f) + ','
                        fields[ii] = str_list

                tb.insertRecord(fields)
            pass
        elif(section == 'market'):
            #create a new frame for the scripts table
            m_frame = tk.Frame(self._field_frame)
            m_frame.grid(row=0,column=0, columnspan=10, sticky='nsew')
            #create the table object
            tb = Table(m_frame, 'name', 'remote connection')
            tb.mapPeripherals(self._field_frame, 0)
            #load the table elements from the settings
            for key,val in apt.SETTINGS['market'].items():
                tb.insertRecord([key,val])
            pass

    def center(self, win):
        '''
        Center the tkinter window. Returns the modified tkinter object.
        '''
        #hide window
        win.attributes('-alpha', 0.0)
        
        #update information regarding window size and screen size
        win.update_idletasks()
        s_height = win.winfo_screenheight()
        s_width = win.winfo_screenwidth()
        width = win.winfo_width()
        height = win.winfo_height()
        #compute the left corner point for the window to be center
        center_x = int((s_width/2) - (width/2))
        centery_y = int((s_height/2) - (height/2))

        win.geometry(str(width)+"x"+str(height)+"+"+str(center_x)+"+"+str(centery_y))

        #reveal window
        win.deiconify()
        win.update_idletasks()
        win.attributes('-alpha', 1.0)
        return win

    
    def initialized(self):
        '''
        Return true if the GUI object has a tkinter object.
        '''
        return hasattr(self, "_window")
    pass


class Table:

    def __init__(self, tk_frame, *headers):
        '''
        Create an editable tkinter treeview object as a table containing records.
        '''
        scroll_y = tk.Scrollbar(tk_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = tk.Scrollbar(tk_frame, orient='horizontal')
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self._tv = tk.ttk.Treeview(tk_frame, column=tuple(headers), show='headings', xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set, selectmode='browse')
        self._tv.pack(fill='both',expand=1)

        self._tv.tag_configure('gray', background='#dddddd')

        scroll_y.config(command=self._tv.yview)
        scroll_x.config(command=self._tv.xview)

        #define columns
        self._tv.column("#0", width=0, stretch=tk.NO)
        for h in headers:
            if(h == headers[0]):
                self._tv.column(h, width=0, anchor='w')
            else:
                self._tv.column(h, anchor='w')

        #create headings
        self._tv.heading("#0", text="", anchor='center')
        
        for h in headers:
            self._tv.heading(h, text=h, anchor='w')

        self._headers = headers
        self._entries = []
        self._size = 0
        self._id_tracker = 0
        pass

    def getSize(self):
        return self._size

    def getHeaders(self):
        return self._headers

    def getEntries(self):
        return self._entries

    def assignID(self):
        #always increment id so every table element is unique
        self._id_tracker += 1
        return self._id_tracker

    def insertRecord(self, data, index=-1):
        '''
        Inserts a new record at specified index. Default is the appended to end
        of table.
        '''
        if(index == -1):
            index = self.getSize()
        if(self.getSize() % 2 == 0):
            tag = 'white'
        else:
            tag = 'gray'
        self._tv.insert(parent='', index=index, iid=self.assignID(), text='', values=tuple(data), tag=tag)
        self._size += 1
        pass

    def replaceRecord(self, data, index):
        self._tv.item(index, text='', values=tuple(data))

    def removeRecord(self, index=-1):
        '''
        Removes a record from the specified index. Default is the last record.
        Also returns the popped value if successful.
        '''
        popped_val = None
        if(index == -1):
            index = self.getSize()-1
        if(self.getSize() > 0):
            popped_val = self.getValues(index)
            self._tv.delete(index)
            self._size -= 1
        return popped_val

    def clearRecords(self):
        self._tv.delete(*self._tv.get_children())
        self._size = 0

    def clearEntries(self):
        #clear any old values from entry boxes
        for ii in range(len(self.getEntries())):
            self.getEntries()[ii].delete(0,tk.END)

    def getValues(self, index):
        '''
        Returns the data values at the specified index from the table.
        '''
        fields = []
        for value in self._tv.item(index)['values']:
            fields += [value]
        return fields

    def mapPeripherals(self, field_frame, table_row, editable=True):
        padx = 10
        pady = 10
        #addition button
        button = tk.Button(field_frame, text='+', command=self.handleAppend)
        button.grid(row=table_row+1, column=0, padx=padx, pady=pady, sticky='w')

        if(editable):
            #update button
            button = tk.Button(field_frame, text='update', command=self.handleUpdate)
            button.grid(row=table_row+1, column=1, padx=padx, pady=pady, sticky='w')
            #edit button
            button = tk.Button(field_frame, text='edit', command=self.handleEdit)
            button.grid(row=table_row+1, column=2, padx=padx, pady=pady, sticky='w')
        #delete button
        button = tk.Button(field_frame, text='-', command=self.handleRemove)
        button.grid(row=table_row+1, column=3, padx=padx, pady=pady, sticky='w')
        #divide up the entries among the frame width
        #text entries for editing
        for ii in range(len(self.getHeaders())):
            columnspan = 1
            if(ii == len(self.getHeaders())-1):
                columnspan = 10
            
            self._entries.append(tk.Entry(field_frame, text=''))
            self._entries[-1].grid(row=table_row+2, column=ii, columnspan=columnspan, sticky='ew')

        #return the next availble row for the field_frame
        return table_row+3

    def handleUpdate(self):
        #get what record is selected
        sel = self._tv.focus()
        if(sel == ''): return

        #get the fields from the entry boxes
        data = []
        for ii in range(len(self.getEntries())):
            data += [self.getEntries()[ii].get()]
            # :todo: define rules for updating data fields

        #print(data,int(sel[0]))
        #now plug into selected space
        self.replaceRecord(data, index=sel)
        self.clearEntries()
        pass

    def handleAppend(self):
        #get the fields from the entry boxes
        data = []
        for ii in range(len(self.getEntries())):
            data += [self.getEntries()[ii].get()]
        self.insertRecord(data)
        self.clearEntries()

    def handleRemove(self):
        sel = self._tv.focus()
        if(sel == ''): return
        self.removeRecord(int(sel))
        #now reapply the toggle colors
        i = 0
        for it in list(self._tv.get_children()):
            if(i % 2 == 0):
                tag = 'white'
            else:
                tag = 'gray'
            self._tv.item(it, tag=tag)
            i += 1

    def handleEdit(self):
        sel = self._tv.focus()
        if(sel == ''): return

        data = self.getValues(sel)
        #clear any old values from entry boxes
        self.clearEntries()
        #load the values into the entry boxes
        for ii in range(len(data)):
            self.getEntries()[ii].insert(0,str(data[ii]))
            pass
        
        pass

    def getTreeview(self):
        return self._tv

    pass