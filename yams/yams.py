from tkinter import *
from tkinter import ttk
import tkinter.filedialog as filedialog
#from tkinter import filedialog
import os
import psutil
import re
import datetime
import numpy as np
from fluoroph1layer2 import *
import yaml
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from itertools import repeat
from parametry1 import check_input,find_ind,zakres
from thread2 import Thread
from Drag_And_Drop_Listbox import Drag_and_Drop_Listbox
from multilistbox import MultiListbox
import glob
import shutil
#import time
import sys
#import subprocess
from multiprocessing import Process
import logging
#paths=[os.getcwd(),\
#os.path.abspath(os.path.join(os.getcwd(), os.pardir))+"/pkg_resources",\
#os.path.abspath(os.path.join(os.getcwd(), os.pardir))+"/pkg_resources/ref_ind",\
#os.path.abspath(os.path.join(os.getcwd(), os.pardir))+"/pkg_resources/photoph"]
#for d in paths:
#    if not d in sys.path:
#        sys.path.append(d)
           
#%%
class LoggingHandlerFrame(ttk.Frame):

    class Handler(logging.Handler):
        def __init__(self, widget):
            logging.Handler.__init__(self)
            self.setFormatter(logging.Formatter(fmt="%(asctime)s - %(levelname)s: %(message)s", datefmt='%d.%m.%Y %H:%M:%S'))
            self.widget = widget
            self.widget.config(state=DISABLED)

        def emit(self, record):
            self.widget.config(state=NORMAL)
            self.widget.insert(END, self.format(record) + "\n")
            self.widget.see(END)
            self.widget.config(state=DISABLED)

    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
#        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)

        self.scrollbar = Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky=(N,S))

        self.text = Text(self, yscrollcommand=self.scrollbar.set,width=98,height=18)
        self.text.grid(row=0, column=0,columnspan=1, sticky=(E,W))

        self.scrollbar.config(command=self.text.yview)

        self.logging_handler = LoggingHandlerFrame.Handler(self.text)
        #%%
class LoggerWriter:
    def __init__(self, level):
        # self.level is really like using log.debug(message)
        # at least in my case
        self.level = level

    def write(self, message):
        # if statement reduces the amount of newlines that are
        # printed to the logger
        if message != '\n':
            self.level(message)

    def flush(self):
        # create a flush method so things can be flushed when
        # the system wants to. Not sure if simply 'printing'
        # sys.stderr is the correct way to do it, but it seemed
        # to work properly for me.
        self.level(sys.stderr)
     #%%   
class MyCheckbutton( ttk.Checkbutton ):
    def __init__(self,master,savename=None,**kwargs):
        super().__init__(master,**kwargs)
        self.savename= savename

class MyCombobox( ttk.Combobox ):

    def __init__(self,master,default_val='',ifdischkbox=False,mat_sizecor=[],objarg=None,**kwargs):
        super().__init__(master,**kwargs)
        self.set(default_val)
        self.bind('<<ComboboxSelected>>', lambda e: self.SelfBind(self,ifdischkbox,objarg))
        self.mat_sizecor=mat_sizecor
        #np.genfromtxt('mat_sizecor.txt', dtype=str, usecols=0,\
        #                  delimiter='\t', skip_header=1, filling_values=' ')
        
    def SelfBind(e,self,ifdischkbox,objarg):
        if ifdischkbox:
            EnableButton(self.get() in self.mat_sizecor,*objarg)
        self.selection_clear()
        
def EnableButton(var,*arg):
    for arrg in arg:
        if var:
            arrg.state(["!disabled"]) 
        else:
            arrg.state(["disabled"])
#%%
class App:
    def __init__(self, master):    
        # loading material files
        with open('../pkg_resources/mat_sizecor.yaml') as stream:
            self.mat_sizecor_dict=yaml.load(stream)
        with open('../pkg_resources/materials.yaml') as stream:
            self.mat_dict=yaml.load(stream)
        with open('../pkg_resources/mat_tempcor.yaml') as stream:
            self.mat_tempcor_dict=yaml.load(stream)

        # list of photophysics def files
        self.foto_files=glob.glob('../pkg_resources/photophysics/*.yaml')
        
        self.master=master
        self.threadhandle=None
        self.threadpid=None
        self.dipole=None
        self.raw_results=''
        self.foto_results=''
#==============================================================================
#          starting gui
#==============================================================================
        # menubar
        self.create_menu(self.master)
        
        # tabs
        self.p = ttk.Notebook(self.master)
#        self.p = ttk.Panedwindow(root, orient=VERTICAL)
        self.p.grid(row=1)          
        
        tab_list=[['Parameters',self.create_params],\
                  ['Geometry',self.create_geom],\
                  ['Photophysics',self.create_photoph],\
                  ['Files',self.create_files],
                  ['Log',self.create_log]]
        
        for item in tab_list:
            key=item[0]
            funct=item[1]
            frame=ttk.Frame(self.p)
            funct(frame)
            item.append(frame)
#            self.p.add(frame,text=key)
            
        tab_list[0],tab_list[1]=tab_list[1],tab_list[0]
        
        
        for item in tab_list:
            key=item[0]
            frame=item[2]
            self.p.add(frame,text=key)
            
            
            
#        self.p.insert(0,)
#        self.create_geom()
#        self.create_params()
#        self.create_photoph()
#        self.create_files()
        #self.create_right()
    def copy(self):
        master=self.master
        obj=master.focus_get()
        try:
            text = obj.selection_get()
            master.clipboard_clear()
            master.clipboard_append(text)
            master.update() # now it stays on the clipboard after the window is closed
        except TclError:
            pass
    def cut(self):
        master=self.master
        obj=master.focus_get()
        try:
            text = obj.selection_get()
            master.clipboard_clear()
            master.clipboard_append(text)
            master.update() # now it stays on the clipboard after the window is closed
            obj.delete(SEL_FIRST, SEL_LAST)
        except TclError:
            pass
    def paste(self):
        master=self.master
        obj=master.focus_get()
        try:
            text=master.selection_get(selection='CLIPBOARD')
            obj.insert(INSERT,text)
        except TclError:
            pass
    def selectall(self):
        master=self.master
        obj=master.focus_get()
        try:
            obj.selection_range(0, END)
        except AttributeError:
            pass
        
    def create_menu(self,master):
        self.menubar=Menu(master)
        # File
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load input file", command=self.LoadFile)
        self.filemenu.add_command(label="Save input file", command=self.SaveFileNow)
        self.filemenu.add_command(label="Load raw results", command=lambda: 
            self.LoadResFile(self.raw_results,"Save raw results as"))
        self.filemenu.add_command(label="Save raw results as", command=lambda:
            self.SaveResNow(self.raw_results),state="disabled")
        self.filemenu.add_command(label="Load photophysics definition", command=self.LoadPhotoFile)
        self.filemenu.add_command(label="Load photophysics results", command=lambda: self.LoadResFile(self.foto_results,"Save photophysics results as"))
        self.filemenu.add_command(label="Save photophysics results as", command=lambda: self.SaveResNow(self.raw_results),\
                                  state="disabled")
#        self.filemenu.add_command(label="Export .bib references", command=[])
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=master.destroy)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        # Edit
        self.editmenu = Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Cut", command=self.cut)
        self.editmenu.add_command(label="Copy", command=self.copy)
        self.editmenu.add_command(label="Paste", command=self.paste)
        self.editmenu.add_command(label="Select all", command=self.selectall)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)
        # Run
        self.runmenu = Menu(self.menubar, tearoff=0)
        self.runmenu.add_command(label="Preview", command=self.create_window)
        self.runmenu.add_command(label="Check integrity", command=self.results_size)
        self.runmenu.add_command(label="Run Mie calc", command=self.Run)
        self.runmenu.add_command(label="Run photophysics", command=self.RunFoto,state="disabled")
        self.runmenu.add_command(label="Run all", command=lambda: self.Run(fotof_files=self.mlb.getcurselection(0)))
        self.runmenu.add_command(label="Stop", command=self.stop,state="disabled")
        self.menubar.add_cascade(label="Run", menu=self.runmenu)
        # Help
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="README", command=[])
        self.helpmenu.add_command(label="Licence", command=[])
        self.helpmenu.add_command(label="References", command=[])
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        # display the menu
        master.config(menu=self.menubar)
        
        
        
    
        
           #%%      
    def create_geom(self,frame):
        
#        self.frame_left = ttk.LabelFrame(self.p,text='Geometry',\
#            padding=(3,3,12,12),relief='groove')
#        self.p.add(self.frame_left)
#        self.frame_left = ttk.Frame(master)
#        master.add(self.frame_left,text='Geometry')

        ttk.Label(frame,text='Select material...',\
                  padding=(5,5,10,10)).grid(column=0,row=1)
        ttk.Label(frame,text='from /nm',padding=(5,5,10,10))\
            .grid(column=1,row=1)
        ttk.Label(frame,text='to /nm',padding=(5,5,10,10))\
        .grid(column=2,row=1)
        ttk.Label(frame,text='every /nm',padding=(5,5,10,10))\
        .grid(column=3,row=1)
         # CHECKBUTTONS
        self.ifsizecor=StringVar()
        self.check_sizecor = ttk.Checkbutton(frame, text='size correction',\
            variable=self.ifsizecor,offvalue='',onvalue=' size correction,')
        self.check_sizecor.grid(column=0,row=3)
        self.ifnonlocal=StringVar()
        self.check_nonlocal = ttk.Checkbutton(frame, text='nonlocal correction',\
            variable=self.ifnonlocal,offvalue='',onvalue=' nonlocal correction,')
        self.check_nonlocal.grid(column=1,row=3)       
        
        # import refractive index dictionary
        self.mat_list=list(self.mat_dict.keys())
        self.materials= MyCombobox(frame, values=self.mat_list,\
            state='readonly',default_val='gold',ifdischkbox=True,\
            objarg=(self.check_sizecor,self.check_nonlocal),\
            mat_sizecor=self.mat_sizecor_dict.keys())
        self.materials.grid(column=0,row=2)
        
        self.from_list=tuple(range(1,11))
        self.fromm= MyCombobox(frame, values=self.from_list,default_val=1)
        self.fromm.grid(column=1,row=2)
        
        self.to_list=tuple(range(10,50,5))
        self.too= MyCombobox(frame, values=self.to_list,default_val=10)
        self.too.grid(column=2,row=2)
        
        self.every_list=(1,2,5,10)
        self.everyy= MyCombobox(frame, values=self.every_list,default_val=1)
        self.everyy.grid(column=3,row=2)
        
        ttk.Separator(frame, orient=HORIZONTAL).grid(row=4, \
                     columnspan=4,sticky="ew",pady=5)
        # LEFT DOWN
        self.l = Drag_and_Drop_Listbox(frame, height=1 ,dipole=self.dipole)
        self.l.grid(column=0,row=5,rowspan=5,columnspan=3,sticky="ewns")
        # ADD BUTTON
        self.button_add = ttk.Button(frame, text='ADD',padding=(5,5,10,10),\
                                command=lambda: self.AddButtonCommand())
        self.button_add.grid(column=2,row=3,columnspan=2)
        # AddButtonCommand(l,materials.get(),ifsizecor.get(),ifnonlocal.get(),fromm.get(),too.get(),everyy.get())
        ttk.Label(frame,text='core side',padding=(5,5,10,10))\
                .grid(column=3,row=5,sticky=(NW))
        self.button_up = ttk.Button(frame, text='up',padding=(5,5,10,10), \
                               command=lambda: self.ShiftSel('Up'))
        self.button_up.grid(column=3,row=6,sticky=(W))
        self.button_down = ttk.Button(frame, text='down',padding=(5,5,10,10), \
                                 command=lambda: self.ShiftSel('Down'))
        self.button_down.grid(column=3,row=7,sticky=(W))
        self.button_delete = ttk.Button(frame, text='remove',padding=(5,5,10,10), \
                                   command=lambda: self.RemoveButtonCommand())
        self.button_delete.grid(column=3,row=8,sticky=(W))
        ttk.Label(frame,text='medium side',padding=(5,5,10,10))\
            .grid(column=3,row=9,sticky=(SW))
        
        ttk.Scrollbar(self.l, orient='vertical')
        
    def create_params(self,frame):   
        self.dipole= MyCombobox(frame, values=[],\
                    state='readonly',postcommand=lambda: self.l.UpdateNumbering())
        self.dipole.grid(column=3,row=6)
        
        ttk.Label(frame,text='Wavelength range: ',padding=(5,5,10,10))\
        .grid(column=0,row=2,columnspan=1,sticky="w")
        ttk.Label(frame,text='from / nm',padding=(5,5,10,10))\
        .grid(column=1,row=1,sticky="w")
        
        self.wavestart_list=tuple(range(300,550,50))
        self.wavestart= MyCombobox(frame, values=self.wavestart_list\
                                   ,default_val=350)
        self.wavestart.grid(column=1,row=2)
        
        ttk.Label(frame,text='to / nm',padding=(5,5,10,10))\
        .grid(column=2,row=1)
        self.wavestop_list=tuple(range(600,900,50))
        self.wavestop= MyCombobox(frame, values=self.wavestop_list,\
                                  default_val=850)
        self.wavestop.grid(column=2,row=2)
        
        ttk.Label(frame,text='every / nm',padding=(5,5,10,10))\
        .grid(column=3,row=1)
        self.waveevery_list=(1,2,3,4,5,10)
        self.waveevery= MyCombobox(frame, values=self.waveevery_list,\
                                   default_val=1)
        self.waveevery.grid(column=3,row=2)
        
        ttk.Label(frame,text='Order of VSH expansion: ',padding=(5,5,10,10))\
                .grid(column=0,row=3,columnspan=3,sticky="w")
        self.order_list=tuple(range(1,11))
        self.order= MyCombobox(frame, values=self.order_list,default_val=5)
        self.order.grid(column=3,row=3)
        
        ttk.Label(frame,text='Number of point for integration in theta: ',\
                  padding=(5,5,10,10)).grid(column=0,row=4,columnspan=3,sticky="w")
        self.theta_list=(90, 180, 360)
        self.theta= MyCombobox(frame, values=self.theta_list,default_val=180)
        self.theta.grid(column=3,row=4)
        
        ttk.Label(frame,text='Temperature of the system / K: ',\
                  padding=(5,5,10,10)).grid(column=0,row=5,columnspan=3,sticky="w")
        self.temp_list=(77, 100, 120, 150, 170, 200, 250, 298, 300, 350)
        self.temp= MyCombobox(frame, values=self.temp_list,default_val=298)
        self.temp.grid(column=3,row=5)
        
        ttk.Label(frame,text='Layer containing dipole: ',\
          padding=(5,5,10,10)).grid(column=0,row=6,columnspan=3,sticky="w")

        ttk.Label(frame,text='Dipole distance from its inner bonduary (or origin) :',\
          padding=(5,5,10,10)).grid(column=0,row=7,columnspan=3,sticky="w")
        
        ttk.Label(frame,text='from /nm',padding=(5,5,10,10))\
            .grid(column=1,row=8)
        ttk.Label(frame,text='to /nm',padding=(5,5,10,10))\
        .grid(column=2,row=8)
        ttk.Label(frame,text='every /nm',padding=(5,5,10,10))\
        .grid(column=3,row=8)
        
        self.dipfrom_list=tuple(range(1,11))
        self.dipfromm= MyCombobox(frame, values=self.dipfrom_list,default_val=1)
        self.dipfromm.grid(column=1,row=9)
        
        self.dipto_list=tuple(range(10,50,5))
        self.diptoo= MyCombobox(frame, values=self.dipto_list,default_val=10)
        self.diptoo.grid(column=2,row=9)
        
        self.dipevery_list=(1,2,5,10)
        self.dipeveryy= MyCombobox(frame, values=self.dipevery_list,default_val=1)
        self.dipeveryy.grid(column=3,row=9)
        
#        self.dipsep_list=(1,2,5,10,20,30,40,50)
#        self.dipsep= MyCombobox(frame, values=self.dipsep_list,default_val=1)
#        self.dipsep.grid(column=3,row=9)
        
    def create_photoph(self,frame):
        
        ttk.Label(frame,text='Photophysical data loaded from files:',\
          padding=(5,5,10,10)).grid(column=0,row=0,columnspan=5,sticky="w")
        
        self.mlb = MultiListbox(frame, (('definition file', 30), ('QY', 12), ('TDM || r', 12),('emission file',30)))
#       for i in range(1000):
#          mlb.insert(END, 
#              ('Important Message: %d' % i, 'John Doe', '10/10/%04d' % (1900+i)))
        self.mlb.grid(column=0,row=1,columnspan=5,sticky="ew") 
        for file in self.foto_files:
            with open(file) as stream:
                foto_dict=yaml.load(stream)
            self.mlb.insert(END, 
              (os.path.basename(file), foto_dict['QY'], foto_dict['orient'][0],foto_dict['emission']))
        
        ttk.Label(frame,text='Add a chromophore:',\
          padding=(5,5,10,10)).grid(column=0,row=2,columnspan=4,sticky="w")   
        
        self.foto_add = ttk.Button(frame, text='ADD',padding=(5,5,10,10),\
                                command=self.AddFoto)
        self.foto_add.grid(column=3,row=2,columnspan=2,sticky="e")
        
        self.foto_clear = ttk.Button(frame, text='CLEAR',padding=(5,5,10,10),\
                                command=self.clear_entries)
        self.foto_clear.grid(column=3,row=2,columnspan=2,sticky="w")
        
        self.fotoname_entry=ttk.Entry(frame,width=30)
        self.fotoname_entry.grid(column=0,row=3,columnspan=1,sticky="w")
        
        self.fotoqy_entry=ttk.Entry(frame,width=12)
        self.fotoqy_entry.grid(column=1,row=3,columnspan=1,sticky="w")
        
        self.fototdm_entry=ttk.Entry(frame,width=12)
        self.fototdm_entry.grid(column=2,row=3,columnspan=1,sticky="w")
        
        self.fotoem_entry=ttk.Entry(frame,width=24)
        self.fotoem_entry.grid(column=3,row=3,columnspan=1,sticky="w")
        
        self.fotoem_add = ttk.Button(frame, text='...',padding=(0,0,0,0),width=4,\
                                command=lambda: self.OpenFile(self.fotoem_entry) )
        self.fotoem_add.grid(column=4,row=3,columnspan=1,sticky="e")
        

        
#        self.ifphotoph=BooleanVar()
#        self.ifphotoph.set(False)
# 
#        self.check_photoph = ttk.Checkbutton(frame, text='Photophysics',\
#            variable=self.ifphotoph, \
#            command=lambda: EnableButton(self.ifphotoph.get(),*obj_list))
#        self.check_photoph.grid(column=0,row=8,columnspan=1,sticky="w")
#        
#        self.mb=  ttk.Menubutton ( frame,width=4,text='...',padding=(5,5,10,10))
#        self.mb.grid(column=2,row=8,columnspan=1,sticky="w")
#        self.mb.menu  =  Menu ( self.mb, tearoff = 0 )
#        self.mb["menu"]  =  self.mb.menu
#
#        self.ifmenu=BooleanVar()
#        self.ifmenu.set(True)
#        self.radio_list=ttk.Radiobutton(frame, text="Choose chromophores: ",variable=self.ifmenu,\
#                value=True, command=EnableButton(self.ifmenu.get(),self.mb))
#        self.radio_list.grid(column=1,row=8,columnspan=1,sticky="w")
#        
#        ## tutaj wczytuje zawartosc /home/ania/Pulpit/publikacja_jpp/YAMS/pkg_resources/photophysics/
##        Item0 = IntVar()
##        Item1 = IntVar()
##        Item2 = IntVar()
##        
##        self.mb.menu.add_checkbutton ( label="Item0", variable=Item0)
##        self.mb.menu.add_checkbutton ( label="Item1", variable=Item1)
##        self.mb.menu.add_checkbutton ( label="Item2", variable=Item2)
##        self.mb.configure(width=1)
#        
#
#        self.emission_label=ttk.Label(frame, text='emission file: ')
#        self.emission_label.grid(column=3,row=8,columnspan=1,sticky="w")
#        self.load_emission = ttk.Button(frame, text="...",padding=(5,5,10,10),\
#                        command=lambda: self.create_window(),width=8)
#        self.load_emission.grid(column=3,row=8,columnspan=1,sticky="e")        
#        
#        self.qy_label=ttk.Label(frame, text='QY: ')
#        self.qy_label.grid(column=0,row=9,columnspan=1,sticky="w")
#        self.qy_entry=ttk.Entry(frame,width=10)
#        self.qy_entry.grid(column=0,row=9,columnspan=1,sticky="e")
#        
#        self.or_label=ttk.Label(frame, text=' orientation: ')
#        self.or_label.grid(column=1,row=9,columnspan=1,sticky="w")
#        self.or_label1=ttk.Label(frame, text='perpendicular: ')
#        self.or_label1.grid(column=1,row=9,columnspan=1,sticky="e")
#        self.or_perp=ttk.Entry(frame,width=10)
#        self.or_perp.grid(column=2,row=9,columnspan=1,sticky="w")
#        
#        self.or_label2=ttk.Label(frame, text='parallel: ')
#        self.or_label2.grid(column=2,row=9,columnspan=1,sticky="e")
#        self.or_para=ttk.Entry(frame,width=10)
#        self.or_para.grid(column=3,row=9,columnspan=1,sticky="w")
#        
#        self.add_photoph = ttk.Button(frame, text="Save",padding=(5,5,10,10),\
#                        command=lambda: self.create_window(),width=8)
#        self.add_photoph.grid(column=3,row=9,columnspan=1,sticky="e")
#        
#
#        
#        obj_custom=[self.add_photoph,self.or_para,self.or_label2,self.or_perp,self.or_label1,
#                  self.or_label,self.qy_entry,self.qy_label,self.load_emission,
#                  self.emission_label]
#        self.radio_custom=ttk.Radiobutton(frame, variable=self.ifmenu,\
#            value=False,text='Custom: ', command=EnableButton( not self.ifmenu.get(),*obj_custom))
#        self.radio_custom.grid(column=2,row=8,columnspan=1,sticky="e")
#        
#        
#        obj_list=[self.add_photoph,self.or_para,self.or_label2,self.or_perp,self.or_label1,
#                  self.or_label,self.qy_entry,self.qy_label,self.load_emission,
#                  self.emission_label,self.radio_custom,self.radio_list,self.mb]        
#        
#        for obj in obj_list:
#            obj.state(["disabled"])
             #%%   
#        self.frame_bottom = ttk.LabelFrame(self.p,text='Files',\
#                                         padding=(3,3,12,12),relief='groove')
#        self.p.add(self.frame_bottom) 
#        return self.frame_photoph

    def create_files(self,frame):
#        self.frame_bottom = ttk.Frame(master)
#        master.add(self.frame_bottom,text='Files') 
        self.refresh_button = ttk.Button(frame, text="Refresh names",padding=(5,5,10,10),\
                                command=lambda: self.refresh_names(),state='enabled')
        self.refresh_button.grid(column=4,row=9,columnspan=2,sticky="ew")
        
        self.butt_check=ttk.Button(frame, text='Check integrity and update size',padding=(5,5,10,10),
        command=self.results_size ,\
            state='enabled')
        self.butt_check.grid(column=3,row=9,columnspan=1,sticky="e")
        
        
        self.res_size=StringVar()
        self.res_size.set('Approximate size of results is 0 MB')
        ttk.Label(frame,textvariable=self.res_size,relief='flat',background='white',\
                  padding=(10,5,10,5)).grid(column=0,row=9,columnspan=2,sticky="e")

#        ttk.Label(frame, textvariable=self.res_size,padding=(5,5,10,10)).grid(column=2,row=9,columnspan=2,sticky="w")
        
        ttk.Separator(frame, orient=HORIZONTAL).grid(row=10, \
             columnspan=5,sticky="ew",pady=5)
        # SAVE PARAMS AND RES

        now='_'.join(map(str,datetime.datetime.now().timetuple()[0:6]))
        direct='../results/res_'+now        
        
        
        self.ifsavepar=BooleanVar()
        self.ifsavepar.set(False)
        
        self.butt_savepar=ttk.Button(frame, text='...',padding=(-10,5,-10,5),
        command=lambda: self.SaveFile(self.entry_savepar), state='disabled')
        self.butt_savepar.grid(column=5,row=11,columnspan=1,sticky="e")
        
        self.check_savepar = MyCheckbutton(frame, text='Auto save parameters as: ',\
            variable=self.ifsavepar, savename='par',\
            command=lambda: EnableButton(self.ifsavepar.get(),self.butt_savepar,self.entry_savepar))
        self.check_savepar.grid(column=0,row=11,columnspan=1,sticky="w")

        self.entry_savepar=ttk.Entry(frame,width=58)
        self.entry_savepar.grid(column=1,columnspan=4,row=11,sticky="we",padx=4)
        self.entry_savepar.insert(0,direct+'/par_'+now+'.yaml')
        self.entry_savepar.state(["disabled"])
        
        self.saveres_default=direct+'/res_'+now
#        self.ifsaveres=BooleanVar()
#        self.ifsaveres.set(True)
        
        self.butt_saveres=ttk.Button(frame, text='...',padding=(-10,5,-10,5),
            command=lambda: self.SaveFile(self.entry_saveres) ,state='enabled')
        self.butt_saveres.grid(column=5,row=12,columnspan=1,sticky="e")
        
#        self.check_saveres = MyCheckbutton(frame, text='Save results as: ',\
#            variable=self.ifsaveres,savename='res',
#            command=lambda: EnableButton(self.ifsaveres.get(),self.butt_saveres,self.entry_saveres))
#        self.check_saveres.grid(column=0,row=11,columnspan=1,sticky="w")

        Label(frame, text='Save results as: ').grid(column=0,row=12,columnspan=1,sticky="w")
        self.entry_saveres=ttk.Entry(frame)
        self.entry_saveres.grid(column=1,columnspan=4,row=12,sticky="we",padx=4)
        self.entry_saveres.insert(0,self.saveres_default+'.pickle')
        
        self.savefoto_default=self.saveres_default+'_photoph.pickle'
#        self.ifsavefoto=BooleanVar()
#        self.ifsavefoto.set(True)
        
        self.butt_savefoto=ttk.Button(frame, text='...',padding=(-10,5,-10,5),
            command=lambda: self.SaveFile(self.entry_savefoto) ,state='enabled')
        self.butt_savefoto.grid(column=5,row=13,columnspan=1,sticky="e")
        
#        self.check_savefoto = MyCheckbutton(frame, text='Save results as: ',\
#            variable=self.ifsavefoto,savename='res',
#            command=lambda: EnableButton(self.ifsavefoto.get(),self.butt_savefoto,self.entry_savefoto))
#        self.check_savefoto.grid(column=0,row=12,columnspan=1,sticky="w")
        Label(frame, text='Save photophysics as: ').grid(column=0,row=13,columnspan=1,sticky="w")
        
        self.entry_savefoto=ttk.Entry(frame)
        self.entry_savefoto.grid(column=1,columnspan=4,row=13,sticky="we",padx=4)
        self.entry_savefoto.insert(0,self.savefoto_default)
        
        
#        self.load_button = ttk.Button(frame, text="Load parameters",padding=(5,5,10,10),\
#                                command=lambda: self.LoadFile(),state='enabled')
#        self.load_button.grid(column=2,row=12,columnspan=1,sticky="ew")
        

        
        
#        self.about_button = ttk.Button(frame, text="About",padding=(5,5,10,10),\
#                                command=lambda: self.about(),state='enabled')
#        self.about_button.grid(column=0,row=12,columnspan=1,sticky="w")
        

        
#        self.savenow_button = ttk.Button(frame, text="Save parameters NOW",padding=(5,5,10,10),\
#                                command=lambda: self.SaveFileNow(),state='enabled')
#        self.savenow_button.grid(column=3,row=12,columnspan=1,sticky="ew")
        
#        self.img_button = ttk.Button(frame, text="Preview",padding=(5,5,10,10),\
#                                command=lambda: self.create_window(),state='enabled')
#        self.img_button.grid(column=4,row=12,columnspan=1,sticky="ew")
        
#        self.butt_run=ttk.Button(frame, text='RUN',padding=(5,5,10,10),
#            command=lambda: self.Run() ,\
#            state='enabled')
#        self.butt_run.grid(column=5,row=12,columnspan=1,sticky="ew")
        #%%
    def create_log(self,frame):
        self.logs=LoggingHandlerFrame(frame)
        self.logs.grid(column=0,row=0,sticky='ew')
#        self.logs.logging_handler.emit(logging.logRecord('dd'))
        self.logger = logging.getLogger('test')
        self.logger.setLevel(logging.DEBUG) 
        self.logger.addHandler(self.logs.logging_handler)
#        sys.stdout = LoggerWriter(self.logger.debug)
#        sys.stderr = LoggerWriter(self.logger.warning)
        self.logger.info('Program started')        
        
        


        

    def give_plot(self):
        def circle(r):
            delta=r/1000
            x=np.arange(-r,r+delta,delta,dtype=complex)
            y=np.sqrt(r**2-x**2,dtype=complex)
            x=np.concatenate((np.real(x), np.real(x[::-1])), axis=0)
            y=np.concatenate((np.real(y), np.real(-y)), axis=0)
            return x,y  
        
        plt.ioff()
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111)
        wheredipole=float(re.search('^\d+',self.dipole.get()).group(0)) if self.dipole.get() else 0
#        wheredipole=0
        nlayer=self.l.size()
        # layers
        for k in range(1,nlayer):
            x,y=circle(k)
            ax.plot(x,y,'b-')
            plt.fill_between(x,y,facecolor='grey',alpha=0.2)
            ax.text((k-0.7)/np.sqrt(2)-0.3,(k-0.7)/np.sqrt(2),self.dipole['values'][k-1],color=(0.7,0,0))
        # medium
        k=nlayer
        ax.text((k-0.7)/np.sqrt(2)-0.3,(k-0.7)/np.sqrt(2),\
                '' if not self.dipole.get() else self.dipole['values'][-1],color=(0.7,0,0))
        # point with dipole
        ax.scatter(0,0 if wheredipole==0 else (wheredipole-0.5),marker='*',color="white", alpha=0)
        ax.text(0.05,0 if wheredipole==0 else (wheredipole-0.5),u'\u2600'+' dipole',color=(0.7,0,0))
        
        #some stuff about formatting
        plt.axes().set_aspect('equal', 'datalim')
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off') # labels along the bottom edge are off
        plt.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left='off',      # ticks along the bottom edge are off
            right='off',         # ticks along the top edge are off
            labelleft='off') # labels along the bottom edge are off
        return fig
        
   #%% 
    def create_window(self):

        fig=self.give_plot()
        self.newwindow = Toplevel(root)
        self.newwindow.wm_title("Image of the system")
 
        canvas = FigureCanvasTkAgg(fig, master=self.newwindow)
        canvas.get_tk_widget().grid(column=1,row=1,columnspan=1)
        canvas.draw()
        self.logger.info('Shown system preview')


        #%%
        
    def make_dict(self):
        datastr1={}
        if self.l.size()>1:
            # tworzy slownik z parametrami
            datastr1['theta']=int(self.theta.get())
            datastr1['max order of expansion']=int(self.order.get())
            datastr1['temperature']=float(self.temp.get())
            datastr1['wavelength']={'from':float(self.wavestart.get()),'to':float(self.wavestop.get()),\
            'every':float(self.waveevery.get())}
            layerslist=[]
            str1=r"""
            ^(\d+)\W+                        
            (\b[a-z]+\b)                     
            (?:\W*(\bsize\scorrection\b))?
            (?:\W*(\bnonlocal\scorrection\b))?
            (?:\W*\bfrom\s(\d+\.?\d*)\snm\b)?
            (?:\W*\bto\s(\d+\.?\d*)\snm\b)?
            (?:\W*\bevery\s(\d+\.?\d*)\snm\b)?
            """
            pattern=re.compile(str1,re.VERBOSE)
            dipolenum=re.search('^\d+',self.dipole.get()).group(0)
            keyes=('from','to','every')
            for item in self.l.get(0,END):
                ldict={}
                lsplit=list(pattern.search(item).groups())
                if lsplit[0]==dipolenum:
                    rdict={'from':float(self.dipfromm.get()),'to':float(self.diptoo.get()),\
                           'every':float(self.dipeveryy.get())}
                    dipdict={'range':rdict}
#                    inserting dipole right after nonlocal correction
                    lsplit.insert(4,{'dipole':dipdict})    
                else:
                    lsplit.insert(4,None)
#               creating dict to every layer
                
                ldict['material']=lsplit[1]               
                list_attr=list(filter(None,lsplit[2:5]))
                if list_attr:
                    ldict['attributes']=list_attr
                if list(filter(None,lsplit[5:8])):
                    rdict=dict(zip(keyes,list(map(float,lsplit[5:]))))
                    ldict['range']=rdict
                layerslist.append(ldict)
            datastr1['layers']=layerslist
#            print(datastr1)
            return datastr1
    #%%
    def results_size(self):
        datastr1=self.make_dict()
        datastr1=check_input(datastr1,dict(zip(self.mat_list,repeat(0))),self.mat_sizecor_dict.keys())
        Lambda=[]
        Lambda.append(zakres(datastr1['wavelength']).shape[0])
        # dodaje liczby warstw
        for dic in datastr1['layers'][:-1]:
            # range of layer
#            print(dic['range'])
#            print(zakres(dic['range']).shape[0])
            Lambda.append(zakres(dic['range']).shape[0])
        how_many=np.prod(np.array(Lambda))
        unit_size=841/(501*81*51)
        total_size=np.round(unit_size*how_many,decimals=2)
        pattern=re.compile(r'\b\d+(\.\d+)?\b')
        newsize=re.sub(pattern,str(total_size),self.res_size.get())
#        print(newsize)
        self.res_size.set(newsize)
        self.logger.info('Checked integrity and updated size')
#        return str(total_size)
        
    #%%
    def RunFoto(self):
        def run_code(self):
#            print(self.threadhandle)
#            self.butt_run.state(["disabled"])
            self.runmenu.entryconfigure("Run all",state="disabled")
            self.runmenu.entryconfigure("Run Mie calc",state="disabled")
            self.runmenu.entryconfigure("Run photophysics",state="disabled")
            self.runmenu.entryconfigure("Stop",state="normal")
            self.toplev=Toplevel(root)
            self.toplev.wm_title('YAMS, processing...')
            self.toplev.protocol("WM_DELETE_WINDOW", self.stop)
            self.progress_bar = ttk.Progressbar(self.toplev,
                                                orient=HORIZONTAL,
                                                mode='indeterminate',
                                                takefocus=True,
                                                length=200)
            self.progress_bar.grid(column=0,row=0,padx=5,pady=5)
            self.butt_stop = ttk.Button(self.toplev, text="STOP",padding=(5,5,5,5),\
                                        command=self.stop)
            self.butt_stop.grid(column=1,row=0,columnspan=1,sticky="w")
            self.labelrun=StringVar()
            self.labelrun.set('Running calculations...')
            self.runlabel=ttk.Label(self.toplev,textvariable=self.labelrun,\
                  padding=(5,5,10,10)).grid(column=0,row=1,columnspan=2,sticky="w")
            self.progress_bar.start()    
#            datastr1=self.make_dict()
#            if self.ifsavepar.get():
#                direct=os.path.dirname(self.entry_savepar.get())
#                # create path if nonexistent
#                if not os.path.exists(direct):
#                    os.makedirs(direct)
#                # save params
#                with open(self.entry_savepar.get(), 'w', encoding='utf8') as outfile:
#                    yaml.dump(datastr1, outfile, default_flow_style=False, allow_unicode=True)
            savename=self.entry_savefoto.get()
            if not savename:
                savename=self.raw_results
#            print('raw_results '+self.raw_results)
            kwargs={'picklefile':self.raw_results,\
                            'savename':savename,\
                            'fotof_files':self.mlb.getcurselection(0)}
            p = Process(target=porph_int, kwargs=kwargs)
            p.start()
            self.subproc_pid=p.pid
            p.join() # this blocks until the process terminates
#            fluoroph1layer2(data=datastr1,\
#                            savename=self.ifsaveres.get() and self.entry_saveres.get() or [],\
#                            mat_dict=self.mat_dict,mat_sizecor_dict=self.mat_sizecor_dict,\
#                            mat_tempcor_dict=self.mat_tempcor_dict)
            
#            self.butt_run.state(["!disabled"])

#            self.butt_stop.state(["disabled"])
            self.toplev.destroy()
            self.runmenu.entryconfigure("Run all",state="normal")
            self.runmenu.entryconfigure("Run Mie calc",state="normal")
            self.runmenu.entryconfigure("Run photophysics",state="normal")
            self.runmenu.entryconfigure("Stop",state="disabled")
            self.filemenu.entryconfigure("Save photophysics results as",state="normal")
            self.foto_results=savename
            self.logger.info('Photophysics calculation finished')
#        subproc=subprocess.run(["ls", "-l"])
#        print(subproc.pid)
#        self.subproc_pid=subproc.pid
        self.threadhandle=Thread(target=run_code,args=(self,))
        self.logger.info('Photophysics calculation started')
#        print(self.threadhandle)
        self.threadhandle.start()
        
#        porph_int(picklefile=self.picklefile,savename=self.ifsaveres.get() and self.entry_saveres.get() or [])
      #%%  
    def Run(self,fotof_files=None):
        
        def run_code(self):
#            print(self.threadhandle)
#            self.butt_run.state(["disabled"])
            self.runmenu.entryconfigure("Run all",state="disabled")
            self.runmenu.entryconfigure("Run Mie calc",state="disabled")
            self.runmenu.entryconfigure("Run photophysics",state="disabled")
            self.runmenu.entryconfigure("Stop",state="normal")
            self.toplev=Toplevel(root)
            self.toplev.wm_title('YAMS, processing...')
            self.toplev.protocol("WM_DELETE_WINDOW", self.stop)
            self.progress_bar = ttk.Progressbar(self.toplev,
                                                orient=HORIZONTAL,
                                                mode='indeterminate',
                                                takefocus=True,
                                                length=200)
            self.progress_bar.grid(column=0,row=0,padx=5,pady=5)
            self.butt_stop = ttk.Button(self.toplev, text="STOP",padding=(5,5,5,5),\
                                        command=self.stop)
            self.butt_stop.grid(column=1,row=0,columnspan=1,sticky="w")
            self.labelrun=StringVar()
            self.labelrun.set('Running calculations...')
            self.runlabel=ttk.Label(self.toplev,textvariable=self.labelrun,\
                  padding=(5,5,10,10)).grid(column=0,row=1,columnspan=2,sticky="w")
            self.progress_bar.start()    
            datastr1=self.make_dict()
            if self.ifsavepar.get():
                direct=os.path.dirname(self.entry_savepar.get())
                # create path if nonexistent
                if not os.path.exists(direct):
                    os.makedirs(direct)
                # save params
                with open(self.entry_savepar.get(), 'w', encoding='utf8') as outfile:
                    yaml.dump(datastr1, outfile, default_flow_style=False, allow_unicode=True)
            savename=self.entry_saveres.get()
            if not savename:
                savename=self.saveres_default
            kwargs={'data':datastr1,\
                            'savename':savename,\
                            'mat_dict':self.mat_dict,'mat_sizecor_dict':self.mat_sizecor_dict,\
                            'mat_tempcor_dict':self.mat_tempcor_dict,'fotof_files':fotof_files}
            p = Process(target=fluoroph1layer2, args=(),kwargs=kwargs)
            
            p.start()
            self.subproc_pid=p.pid
            p.join() # this blocks until the process terminates
#            fluoroph1layer2(data=datastr1,\
#                            savename=self.ifsaveres.get() and self.entry_saveres.get() or [],\
#                            mat_dict=self.mat_dict,mat_sizecor_dict=self.mat_sizecor_dict,\
#                            mat_tempcor_dict=self.mat_tempcor_dict)
            
#            self.butt_run.state(["!disabled"])

#            self.butt_stop.state(["disabled"])
            self.toplev.destroy()
            self.runmenu.entryconfigure("Run all",state="normal")
            self.runmenu.entryconfigure("Run Mie calc",state="normal")
            self.runmenu.entryconfigure("Run photophysics",state="normal")
            self.runmenu.entryconfigure("Stop",state="disabled")           
            self.filemenu.entryconfigure("Save raw results as",state="normal")
            self.raw_results=savename
            self.logger.info('Mie theory calculation finished')
#        subproc=subprocess.run(["ls", "-l"])
#        print(subproc.pid)
#        self.subproc_pid=subproc.pid
        self.threadhandle=Thread(target=run_code,args=(self,))
#        print(self.threadhandle)
        self.logger.info('Mie theory calculation started')
        self.threadhandle.start()
#        curpid=os.getpid()
#        print('currpid ',curpid)
#        parent = psutil.Process(curpid)
#        for child in parent.children(recursive=True):  # or parent.children() for recursive=False
#            print(child)
        
     #%%
    def stop(self):
        def stoop(self):
            ### kill children
#            curpid=os.getpid()
            curpid=self.subproc_pid
#            print('currpid ',curpid)
            parent = psutil.Process(curpid)
#            print('par chld ',parent.children(recursive=True))
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
#                print('child ',child.pid)
                child.kill()
            parent.kill()
#            print('killing ',self.threadhandle)

            ### kill thread
#            self.threadhandle.terminate()
##            print('joining ',self.threadhandle)
#            self.threadhandle.join()
#            self.butt_run.state(["!disabled"])

            self.toplev.destroy()
            self.runmenu.entryconfigure("Run all",state="normal")
            self.runmenu.entryconfigure("Run Mie calc",state="normal")
            self.runmenu.entryconfigure("Run photophysics",state="normal")
            self.runmenu.entryconfigure("Stop",state="disabled") 
            self.logger.info('Stopped')
        self.logger.info('Stopping')
        if self.threadhandle.isAlive() and self.toplev.winfo_exists():
            self.butt_stop.state(["disabled"])
            self.labelrun.set('Terminating calculations...')
            Thread(target=stoop,args=(self,)).start()
        
        
           #%%
    def refresh_names(self):
            now='_'.join(map(str,datetime.datetime.now().timetuple()[0:6]))
            direct='../results/res_'+now
            self.entry_savepar.delete(0,END)
            self.entry_savepar.insert(0,direct+'/par_'+now+'.yaml')
            self.entry_saveres.delete(0,END)
            self.entry_saveres.insert(0,direct+'/res_'+now+'.pickle')
            self.entry_savefoto.delete(0,END)
            self.entry_savefoto.insert(0,direct+'/res_'+now+'_photoph.pickle')
            self.logger.info('Names refreshed')
            #%%
    def about(self):
        pass
        
        
 #%%       
    def OpenFile(self,entry):
        f = filedialog.askopenfilename(initialdir='../pkg_resources/photophysics')
        if f:
            entry.delete(0, END)
            entry.insert(0,f)
            self.logger.info('Emission file selected')
 
    def SaveFile(self,entry):
        f = filedialog.asksaveasfilename(defaultextension=".yaml",initialdir='../results/')
        if f:
            entry.delete(0, END)
            entry.insert(0,f)
            self.logger.info('Savename selected')
    def SaveFileNow(self):
        f = filedialog.asksaveasfilename(defaultextension=".yaml",initialdir="../input_files/",\
                                       filetypes=(("yaml files","*.yaml"),("all files","*.*")))
        if f:
           datastr1=self.make_dict()
#           print(datastr1)
           datastr1=check_input(datastr1,dict(zip(self.mat_list,repeat(0))),self.mat_sizecor_dict.keys())
           with open(f, 'w', encoding='utf8') as outfile:
              yaml.dump(datastr1, outfile, default_flow_style=False, allow_unicode=True)
           self.logger.info('Input file saved')   
    def SaveResNow(self,resfile):
        if resfile:
            f = filedialog.asksaveasfilename(defaultextension=".pickle",initialdir="../results/",\
                                           filetypes=(("pickle files","*.pickle"),("MATLAB files","*.mat"),("all files","*.*")))
            if f:
               extensionf = '.mat' if os.path.splitext(f)[1]=='.mat' else '.pickle'
               extensionr = os.path.splitext(resfile)[1]
               if extensionf==extensionr:
                   shutil.copyfile(resfile,f)
               else:
                   if extensionr=='.pickle':
                       with open('GenLL.py','rb') as file:
                           dic = pickle.load(file)
                       sio.savemat(f,dic)
                   if extensionr=='.mat':
                       dic=sio.loademat(resfile)
                       with open(f,'wb') as file:
                           pickle.dump(dic,file)
                   if not extensionr:
                       dic={}
                       try:
                           with open(resfile,'rb') as file:
                               dic = pickle.load(file)
                       except pickle.UnpicklingError:
                           try:
                               dic=sio.loademat(resfile)
                           except ValueError:
                               print('Results file is neither .pickle nor .mat file! Will not save.')
                       if dic:
                           if extensionf=='.mat':
                               sio.savemat(f,dic)
                           else:
                              with open(f,'wb') as file:
                                  pickle.dump(dic,file)
               self.logger.info('Saved results')                            
           
    def LoadResFile(self,varobj,sstr):
        f = filedialog.askopenfilename(initialdir="../results/",\
                                       filetypes=(("pickle files","*.pickle"),("MATLAB files","*.mat"),("all files","*.*")))
        varobj=f
        if varobj:
            self.filemenu.entryconfigure(sstr,state="normal")
            if sstr=="Save raw results as":
                self.runmenu.entryconfigure("Run photophysics",state="normal")
                self.raw_results=f
            if sstr=="Save photophysics results as":
                self.foto_results=f
            self.logger.info('Loaded results file')
    
    def clear_entries(self):
        for obj in (self.fotoqy_entry,self.fotoname_entry,self.fotoem_entry,self.fototdm_entry):
            obj.delete(0, 'end')
        
    def LoadPhotoFile(self):
        f = filedialog.askopenfilename(initialdir="../pkg_resources/photophysics",\
                                       filetypes=(("yaml files","*.yaml"),("all files","*.*")))
        if f:
            self.clear_entries()
            try:
                with open(f, 'r') as outfile:
                      data=yaml.load(outfile)
                      self.fototdm_entry.insert(0,data['orient'][0])
                      self.fotoqy_entry.insert(0,data['QY'])
                      emname=data['emission']
                      if not os.path.isabs(emname):
                          dir1=os.path.dirname(f)
                          emname = os.path.join(dir1, emname)
                          emname=os.path.abspath(emname)
                      self.fotoem_entry.insert(0,emname)
                      self.fotoname_entry.insert(0,os.path.basename(f))
                self.AddFoto()
            except:
                pass
        self.logger.info('Loaded photophysics definition file')
                
     #%%         
    def LoadFile(self):
        
        f = filedialog.askopenfilename(initialdir="../input_files/",\
                                       filetypes=(("yaml files","*.yaml"),("all files","*.*")))
        if f:
           with open(f, 'r') as outfile:
              data=yaml.load(outfile)
              # checking integrity od data
              data=check_input(data,dict(zip(self.mat_list,repeat(0))),self.mat_sizecor_dict.keys())
              #max order of exp
              self.order.set(str(data['max order of expansion']))   
              #temperature
              self.temp.set(str(data['temperature']))   
              #theta int
              self.theta.set(str(data['theta']))
              #wavelength
              self.wavestart.set(str(data['wavelength']['from']))
              self.wavestop.set(str(data['wavelength']['to']))
              self.waveevery.set(str(data['wavelength']['every']))
              # layers
              # removes items in self.l
              self.l.delete(0, END)
              self.dipole.set('')
              k=0
              dipnum=None
              for layer in data['layers']:
                  strr='0. '+layer['material']
                  if 'range' in layer.keys():
                      strr+=' ,'
                  if 'attributes' in layer.keys():
                     dic_pos_ind=find_ind(layer['attributes'],dict)
                     dip_dict={} if not dic_pos_ind else layer['attributes'][dic_pos_ind[0]]
                     if 'dipole' in dip_dict.keys():
                        dip_num=k
                        self.dipfromm.set(dip_dict['dipole']['range']['from'])
                        self.diptoo.set(dip_dict['dipole']['range']['to'])
                        self.dipeveryy.set(dip_dict['dipole']['range']['every'])
#                        self.dipsep.set(str(dip_dict['dipole']))
                     str_pos_ind=find_ind(layer['attributes'],str)
                     if 'size correction' in map(layer['attributes'].__getitem__,str_pos_ind):
                         strr+=' size correction'
                     if 'nonlocal correction' in map(layer['attributes'].__getitem__,str_pos_ind):
                         strr+=' nonlocal correction'
                  if 'range' in layer.keys():
                      strr+=' from '+str(layer['range']['from'])+' nm'
                      strr+=' to '+str(layer['range']['to'])+' nm'
                      strr+=' every '+str(layer['range']['every'])+' nm'
                  self.l.insert(END,strr)
                  k+=1   
              self.l.UpdateNumbering()
              if dipnum!=None:
                  self.dipole.set(self.dipole['values'][dip_num])
           self.logger.info('Loaded input parameters')                 
#%%
    def AddButtonCommand(self):
        self.l.AddParams()
        String1=self.materials.get()+','
        if self.materials.get() in self.mat_sizecor_dict.keys():
            String1=String1+ self.ifsizecor.get()+self.ifnonlocal.get()
        String=str(self.l.size()+1)+'. '+String1+' from '+self.fromm.get()+\
        ' nm to '+self.too.get()+\
        ' nm every '+self.everyy.get()+' nm'
        self.l.insert(END, String)
        self.l.UpdateNumbering()
        self.logger.info('Added layer')
        
    def RemoveButtonCommand(self):
        self.l.DeleteSelection()
        self.logger.info('Removed layer')
        
    def ShiftSel(self,direction):
        str1='self.l.shiftSelection'+direction+'()'
        eval(str1)
        self.logger.info('Moved layer '+direction)
        
    def AddFoto(self):
        try:
            qy=float(self.fotoqy_entry.get())
            if qy>1: raise ValueError('QY must be <=1')
            tdm=float(self.fototdm_entry.get())
            if tdm>1: raise ValueError('TDM || r must be <=1')
            emname=self.fotoem_entry.get()
            if not os.path.isfile(emname): raise FileNotFoundError
            # kopiuje em file
            try: 
                shutil.copy2(emname,'../pkg_resources/photophysics/')
            except shutil.SameFileError:
                pass
            emname=os.path.basename(emname)
            param_name=self.fotoname_entry.get()
            if not param_name:
                max_num=0
                pattern=re.compile('^chromophore(\d+).yaml$')
                for s in self.mlb.get(0,last=END,collist=0)[0]:
                    found=re.findall(pattern,s)
                    if found:
                        max_num=max_num if max_num>int(found[0]) else int(found[0])
                param_name='chromophore'+str(max_num+1)+'.yaml'
#                self.foto_files.append(param_name)
            else:
#                if not re.findall(r'^.(\.yaml)$',param_name): param_name+='.yaml'
                if not os.path.splitext(param_name)[1]=='.yaml': param_name+='.yaml'
#                print(param_name)
#                print(self.mlb.get(0,last=END,collist=0)[0])
                if param_name in self.mlb.get(0,last=END,collist=0)[0]: raise FileExistsError
            self.mlb.insert(END, 
              (os.path.basename(param_name), qy, tdm,emname))
            # tutaj dodaje plik
            foto_dict={'QY':qy,'orient':[tdm,1-tdm],'emission':emname}
            with open('../pkg_resources/photophysics/'+param_name, 'w', encoding='utf8') as outfile:
                yaml.dump(foto_dict, outfile, default_flow_style=False, allow_unicode=True)
            # clear the entry fields    
            self.clear_entries()
            self.logger.info('Added photophysics entry')
        except (ValueError,FileNotFoundError,FileExistsError):
            pass
        
        
        
        
#%%
if __name__ == "__main__":
    root = Tk()
    App(root)
    root.wm_title('YAMS, yet another Mie simulator')
    root.mainloop()

    







