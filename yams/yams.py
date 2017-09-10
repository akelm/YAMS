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
#import time
#import sys
#import subprocess
from multiprocessing import Process

#paths=[os.getcwd(),\
#os.path.abspath(os.path.join(os.getcwd(), os.pardir))+"/pkg_resources",\
#os.path.abspath(os.path.join(os.getcwd(), os.pardir))+"/pkg_resources/ref_ind",\
#os.path.abspath(os.path.join(os.getcwd(), os.pardir))+"/pkg_resources/photoph"]
#for d in paths:
#    if not d in sys.path:
#        sys.path.append(d)
                
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
        
        self.master=master
        self.threadhandle=None
        self.threadpid=None
        self.dipole=None
        
#==============================================================================
#          starting gui
#==============================================================================
        # menubar
        self.create_menu(self.master)
        
        # tabs
        self.p = ttk.Notebook(self.master)
#        self.p = ttk.Panedwindow(root, orient=VERTICAL)
        self.p.grid(row=1)          
        
        tab_dict=[('Parameters',self.create_params),\
                  ('Geometry',self.create_geom),\
                  ('Photophysics',self.create_photoph),\
                  ('Files',self.create_files),
                  ('Log',self.create_log)]
        
        for item in tab_dict:
            key=item[0]
            funct=item[1]
            frame=ttk.Frame(self.p)
            funct(frame)
            self.p.add(frame,text=key)
        self.p.insert(0,)
#        self.create_geom()
#        self.create_params()
#        self.create_photoph()
#        self.create_files()
        #self.create_right()
    def create_menu(self,master):
        pass

        
        
        
        
    
        
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
                               command=lambda: self.l.shiftSelectionDown())
        self.button_up.grid(column=3,row=6,sticky=(W))
        self.button_down = ttk.Button(frame, text='down',padding=(5,5,10,10), \
                                 command=lambda: self.l.shiftSelectionUp())
        self.button_down.grid(column=3,row=7,sticky=(W))
        self.button_delete = ttk.Button(frame, text='remove',padding=(5,5,10,10), \
                                   command=lambda: self.l.DeleteSelection())
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

        ttk.Label(frame,text='Dipole distance from the inner bonduary (or origin) / nm:',\
          padding=(5,5,10,10)).grid(column=0,row=7,columnspan=3,sticky="w")
        
        self.dipsep_list=(1,2,5,10,20,30,40,50)
        self.dipsep= MyCombobox(frame, values=self.dipsep_list,default_val=1)
        self.dipsep.grid(column=3,row=7)
        
    def create_photoph(self,frame):
        
        self.ifphotoph=BooleanVar()
        self.ifphotoph.set(False)
 
        self.check_photoph = ttk.Checkbutton(frame, text='Photophysics',\
            variable=self.ifphotoph, \
            command=lambda: EnableButton(self.ifphotoph.get(),*obj_list))
        self.check_photoph.grid(column=0,row=8,columnspan=1,sticky="w")
        
        self.mb=  ttk.Menubutton ( frame,width=4,text='...',padding=(5,5,10,10))
        self.mb.grid(column=2,row=8,columnspan=1,sticky="w")
        self.mb.menu  =  Menu ( self.mb, tearoff = 0 )
        self.mb["menu"]  =  self.mb.menu

        self.ifmenu=BooleanVar()
        self.ifmenu.set(True)
        self.radio_list=ttk.Radiobutton(frame, text="Choose chromophores: ",variable=self.ifmenu,\
                value=True, command=EnableButton(self.ifmenu.get(),self.mb))
        self.radio_list.grid(column=1,row=8,columnspan=1,sticky="w")
        
        ## tutaj wczytuje zawartosc /home/ania/Pulpit/publikacja_jpp/YAMS/pkg_resources/photophysics/
#        Item0 = IntVar()
#        Item1 = IntVar()
#        Item2 = IntVar()
#        
#        self.mb.menu.add_checkbutton ( label="Item0", variable=Item0)
#        self.mb.menu.add_checkbutton ( label="Item1", variable=Item1)
#        self.mb.menu.add_checkbutton ( label="Item2", variable=Item2)
#        self.mb.configure(width=1)
        

        self.emission_label=ttk.Label(frame, text='emission file: ')
        self.emission_label.grid(column=3,row=8,columnspan=1,sticky="w")
        self.load_emission = ttk.Button(frame, text="...",padding=(5,5,10,10),\
                        command=lambda: self.create_window(),width=8)
        self.load_emission.grid(column=3,row=8,columnspan=1,sticky="e")        
        
        self.qy_label=ttk.Label(frame, text='QY: ')
        self.qy_label.grid(column=0,row=9,columnspan=1,sticky="w")
        self.qy_entry=ttk.Entry(frame,width=10)
        self.qy_entry.grid(column=0,row=9,columnspan=1,sticky="e")
        
        self.or_label=ttk.Label(frame, text=' orientation: ')
        self.or_label.grid(column=1,row=9,columnspan=1,sticky="w")
        self.or_label1=ttk.Label(frame, text='perpendicular: ')
        self.or_label1.grid(column=1,row=9,columnspan=1,sticky="e")
        self.or_perp=ttk.Entry(frame,width=10)
        self.or_perp.grid(column=2,row=9,columnspan=1,sticky="w")
        
        self.or_label2=ttk.Label(frame, text='parallel: ')
        self.or_label2.grid(column=2,row=9,columnspan=1,sticky="e")
        self.or_para=ttk.Entry(frame,width=10)
        self.or_para.grid(column=3,row=9,columnspan=1,sticky="w")
        
        self.add_photoph = ttk.Button(frame, text="Save",padding=(5,5,10,10),\
                        command=lambda: self.create_window(),width=8)
        self.add_photoph.grid(column=3,row=9,columnspan=1,sticky="e")
        

        
        obj_custom=[self.add_photoph,self.or_para,self.or_label2,self.or_perp,self.or_label1,
                  self.or_label,self.qy_entry,self.qy_label,self.load_emission,
                  self.emission_label]
        self.radio_custom=ttk.Radiobutton(frame, variable=self.ifmenu,\
            value=False,text='Custom: ', command=EnableButton( not self.ifmenu.get(),*obj_custom))
        self.radio_custom.grid(column=2,row=8,columnspan=1,sticky="e")
        
        
        obj_list=[self.add_photoph,self.or_para,self.or_label2,self.or_perp,self.or_label1,
                  self.or_label,self.qy_entry,self.qy_label,self.load_emission,
                  self.emission_label,self.radio_custom,self.radio_list,self.mb]        
        
        for obj in obj_list:
            obj.state(["disabled"])
             #%%   
#        self.frame_bottom = ttk.LabelFrame(self.p,text='Files',\
#                                         padding=(3,3,12,12),relief='groove')
#        self.p.add(self.frame_bottom) 
#        return self.frame_photoph

    def create_files(self,frame):
#        self.frame_bottom = ttk.Frame(master)
#        master.add(self.frame_bottom,text='Files') 
        
        self.butt_check=ttk.Button(frame, text='check integrity and update size',padding=(5,5,10,10),
        command=lambda: self.res_size.set(self.results_size()) ,\
            state='enabled')
        self.butt_check.grid(column=3,row=9,columnspan=3,sticky="e")
        ttk.Label(frame,text='Approximate size of results is / MB: ',\
                  padding=(5,5,10,10)).grid(column=0,row=9,columnspan=2,sticky="w")
        self.res_size=StringVar()
        self.res_size.set('0')
        ttk.Label(frame, textvariable=self.res_size,padding=(5,5,10,10)).grid(column=2,row=9,sticky="w")
        

        # SAVE PARAMS AND RES
        self.ifsavepar=BooleanVar()
        self.ifsavepar.set(False)
        
        self.butt_savepar=ttk.Button(frame, text='...',padding=(5,5,10,10),
        command=lambda: self.SaveFile(self.entry_savepar), state='disabled')
        self.butt_savepar.grid(column=5,row=10,columnspan=1,sticky="ew")
        
        self.check_savepar = MyCheckbutton(frame, text='Save parameters as: ',\
            variable=self.ifsavepar, savename='par',\
            command=lambda: EnableButton(self.ifsavepar.get(),self.butt_savepar,self.entry_savepar))
        self.check_savepar.grid(column=0,row=10,columnspan=1,sticky="w")

        now='_'.join(map(str,datetime.datetime.now().timetuple()[0:6]))
        direct=os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'/results/res_'+now
        self.entry_savepar=ttk.Entry(frame)
        self.entry_savepar.grid(column=1,columnspan=4,row=10,sticky="we",padx=4)
        self.entry_savepar.insert(0,direct+'/par_'+now+'.yaml')
        self.entry_savepar.state(["disabled"])
        
        self.ifsaveres=BooleanVar()
        self.ifsaveres.set(True)
        
        self.butt_saveres=ttk.Button(frame, text='...',padding=(5,5,10,10),
            command=lambda: self.SaveFile(self.entry_saveres) ,state='enabled')
        self.butt_saveres.grid(column=5,row=11,columnspan=1,sticky="ew")
        

        self.check_saveres = MyCheckbutton(frame, text='Save results as: ',\
            variable=self.ifsaveres,savename='res',
            command=lambda: EnableButton(self.ifsaveres.get(),self.butt_saveres,self.entry_saveres))
        self.check_saveres.grid(column=0,row=11,columnspan=1,sticky="w")
        self.entry_saveres=ttk.Entry(frame)
        self.entry_saveres.grid(column=1,columnspan=4,row=11,sticky="we",padx=4)
        self.entry_saveres.insert(0,direct+'/res_'+now)
        
        
        self.load_button = ttk.Button(frame, text="Load parameters",padding=(5,5,10,10),\
                                command=lambda: self.LoadFile(),state='enabled')
        self.load_button.grid(column=2,row=12,columnspan=1,sticky="ew")
        
        self.refresh_button = ttk.Button(frame, text="Refresh names",padding=(5,5,10,10),\
                                command=lambda: self.refresh_names(),state='enabled')
        self.refresh_button.grid(column=0,row=12,columnspan=2,sticky="e")
        
        
        self.about_button = ttk.Button(frame, text="About",padding=(5,5,10,10),\
                                command=lambda: self.about(),state='enabled')
        self.about_button.grid(column=0,row=12,columnspan=1,sticky="w")
        

        
        self.savenow_button = ttk.Button(frame, text="Save parameters NOW",padding=(5,5,10,10),\
                                command=lambda: self.SaveFileNow(),state='enabled')
        self.savenow_button.grid(column=3,row=12,columnspan=1,sticky="ew")
        
        self.img_button = ttk.Button(frame, text="Preview",padding=(5,5,10,10),\
                                command=lambda: self.create_window(),state='enabled')
        self.img_button.grid(column=4,row=12,columnspan=1,sticky="ew")
        
        self.butt_run=ttk.Button(frame, text='RUN',padding=(5,5,10,10),
            command=lambda: self.Run() ,\
            state='enabled')
        self.butt_run.grid(column=5,row=12,columnspan=1,sticky="ew")
        #%%
    def create_log(self,frame):
        pass
    
    
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
            str1=r'''
            ^(\d+)\W+                         # begining of string, number of the layer and nonalphanum
            (\b[a-z]+\b)                      # first word is a material
            (?:\W*(\bsize\scorrection\b))?
            (?:\W*(\bnonlocal\scorrection\b))?
            (?:\W*\bfrom\s(\d+\.?\d*)\snm\b)?
            (?:\W*\bto\s(\d+\.?\d*)\snm\b)?
            (?:\W*\bevery\s(\d+\.?\d*)\snm\b)?
            '''
            pattern=re.compile(str1,re.VERBOSE)
            dipolenum=re.search('^\d+',self.dipole.get()).group(0)
            for item in self.l.get(0,END):
                lsplit=list(pattern.search(item).groups())
                lsplit.insert(4,{'dipole':float(self.dipsep.get())} if lsplit[0]==dipolenum else None )
                ldict={}
                ldict['material']=lsplit[1]
                list_attr=list(filter(None,lsplit[2:5]))
                if list_attr:
                    ldict['attributes']=list_attr
                if list(filter(None,lsplit[5:8])):
                    keyes=('from','to','every')
                    rdict=dict(zip(keyes,list(map(float,lsplit[5:]))))
                    ldict['range']=rdict
                layerslist.append(ldict)
            datastr1['layers']=layerslist        
            return datastr1
    #%%
    def results_size(self):
        datastr1=self.make_dict()
        datastr1=check_input(datastr1,dict(zip(self.mat_list,repeat(0))),self.mat_sizecor_dict.keys())
        Lambda=[]
        Lambda.append(zakres(datastr1['wavelength']).shape[0])
        for dic in datastr1['layers'][:-1]:
            # range of layer
            Lambda.append(zakres(dic['range']).shape[0])
        how_many=np.prod(np.array(Lambda))
        unit_size=841/(501*81*51)
        total_size=np.round(unit_size*how_many,decimals=2)
        return str(total_size)
        
      #%%  
    def Run(self):
        def run_code(self):
#            print(self.threadhandle)
            self.butt_run.state(["disabled"])
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
                                        command=lambda: self.stop())
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
            kwargs={'data':datastr1,\
                            'savename':self.ifsaveres.get() and self.entry_saveres.get() or [],\
                            'mat_dict':self.mat_dict,'mat_sizecor_dict':self.mat_sizecor_dict,\
                            'mat_tempcor_dict':self.mat_tempcor_dict}
            p = Process(target=fluoroph1layer2, kwargs=kwargs)
            p.start()
            self.subproc_pid=p.pid
            p.join() # this blocks until the process terminates
#            fluoroph1layer2(data=datastr1,\
#                            savename=self.ifsaveres.get() and self.entry_saveres.get() or [],\
#                            mat_dict=self.mat_dict,mat_sizecor_dict=self.mat_sizecor_dict,\
#                            mat_tempcor_dict=self.mat_tempcor_dict)
            
            self.butt_run.state(["!disabled"])
#            self.butt_stop.state(["disabled"])
            self.toplev.destroy()
            

#        subproc=subprocess.run(["ls", "-l"])
#        print(subproc.pid)
#        self.subproc_pid=subproc.pid
        self.threadhandle=Thread(target=run_code,args=(self,))
#        print(self.threadhandle)
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
            self.butt_run.state(["!disabled"])
            self.toplev.destroy()
 
     
        if self.threadhandle.isAlive() and self.toplev.winfo_exists():
            self.butt_stop.state(["disabled"])
            self.labelrun.set('Terminating calculations...')
            Thread(target=stoop,args=(self,)).start()
        
        
           #%%
    def refresh_names(self):
            now='_'.join(map(str,datetime.datetime.now().timetuple()[0:6]))
            direct=os.path.abspath(os.path.join(os.getcwd(), os.pardir))+'/results/res_'+now
            self.entry_savepar.delete(0,END)
            self.entry_savepar.insert(0,direct+'/par_'+now+'.yaml')
            self.entry_saveres.delete(0,END)
            self.entry_saveres.insert(0,direct+'/res_'+now+'.yaml')
            
            #%%
    def about(self):
        pass
        
        
 #%%       
    def SaveFile(self,entry):
        f = filedialog.asksaveasfilename(defaultextension=".yaml",)
        if f:
            entry.delete(0, END)
            entry.insert(f)
    def SaveFileNow(self):
        f = filedialog.asksaveasfilename(defaultextension=".yaml",initialdir="../input_files/",\
                                       filetypes=(("yaml files","*.yaml"),("all files","*.*")))
        if f:
           datastr1=self.make_dict()
           datastr1=check_input(datastr1,dict(zip(self.mat_list,repeat(0))),self.mat_sizecor_dict.keys())
           with open(f, 'w', encoding='utf8') as outfile:
              yaml.dump(datastr1, outfile, default_flow_style=False, allow_unicode=True) 
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
                        self.dipsep.set(str(dip_dict['dipole']))
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
        
        
#%%
if __name__ == "__main__":
    root = Tk()
    App(root)
    root.wm_title('YAMS, yet another Mie simulator')
    root.mainloop()

    







