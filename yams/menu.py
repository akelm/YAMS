#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 10:57:53 2017

@author: ania
"""

#==============================================================================
# MENU
#==============================================================================
class menubar(self,master):
    def __init__(self,master):
        pass
    # menu
        menuBar = Menu(master)
        fileMenu = Menu(menuBar)
        fileMenu.add_command(label="Open MPC file", command=open_mpc_file)
        fileMenu.add_command(label="Save", command=save_file)
        fileMenu.add_command(label="Save As...", command=save_as)
        fileMenu.add_separator()
        fileMenu.add_command(label="Quit", command=master.quit)
        menuBar.add_cascade(label="File", menu=fileMenu)
        
        editMenu = Menu(menuBar)
        editMenu.add_command(label="Copy", command=copy)
        editMenu.add_command(label="Cut", command=cut)
        editMenu.add_command(label="Paste", command=paste)
        editMenu.add_command(label="Select All", command=select_all)
        menuBar.add_cascade(label="Edit", menu=editMenu)
        
        rightClick = Menu(master, tearoff=0)
        rightClick.add_command(label="Copy", command=copy)
        rightClick.add_command(label="Cut", command=cut)
        rightClick.add_command(label="Paste", command=paste)
        rightClick.add_separator()
        rightClick.add_command(label="Select All", command=select_all)
        
        calcMenu = Menu(menuBar)
        calcMenu.add_command(label="Preview", command=copy)
        calcMenu.add_command(label="Start", command=cut)
        calcMenu.add_command(label="Stop", command=paste)
        menuBar.add_cascade(label="Calculation", menu=calcMenu)
        
        helpMenu = Menu(menuBar)
        helpMenu.add_command(label="Help contents", command=copy)
        helpMenu.add_command(label="References", command=cut)
        helpMenu.add_command(label="About", command=paste)
        menuBar.add_cascade(label="Help", menu=helpMenu)
        
        
    def copy(event=None):
        global clipboard
        sel = text.selection_get()
        clipboard = sel


    def cut(event=None):
        global clipboard
        sel = text.selection_get()
        clipboard = sel
        text.delete(SEL_FIRST, SEL_LAST)
    
    
    def paste(event=None):
        global clipboard
        try:
            text.insert(INSERT, clipboard)
        except:
            pass
        highlight()
    
    
    def select_all(event=None):
        text.tag_add(SEL, "1.0", END)
        text.mark_set(0.0, END)
        text.see(INSERT)
        return 'break'
    
    def quit(event=None):
        root.quit()
        root.destroy()
        
#        # Keybindings
#        text.bind("<Button-3>", popup)
#        text.bind("<Button-1>", deselect_all)
#        text.bind("<Control-c>", copy)
#        text.bind("<Control-v>", paste)
#        text.bind("<Control-x>", cut)
#        text.bind("<Control-s>", save_file)
#        text.bind("<Control-S>", save_as)
#        text.bind("<Control-n>", new_file)
#        text.bind("<Control-a>", select_all)
#        text.bind("<Control-q>", quit)
#        master.bind("<KeyPress>", highlight)
        
        master.config(menu=menuBar)
    

from tkinter.filedialog import *
from tkinter.messagebox import *
from CustomText import *
from parser import *
import subprocess
import os

filename = None
data_filename = None
generated_c = False
clipboard = None
start_file = """parameters
    
end
dimensions
end
settings
end
variables
end
minimize 
subject to
end """


def new_file(event=None):
    global filename
    global edit_data

    text.delete(0.0, END)
    text.insert(0.0, start_file)
    edit_data = text.get(0.0, END)
    root.title("New file")
    highlight()


def save_file(event=None):
    global filename
    try:
        t = text.get(0.0, END)
        f = open(filename, 'w')
        f.write(t.rstrip())
        f.close()
    except:
        save_as()


def save_as(event=None):
    global filename
    try:
        f = asksaveasfile(mode='w', defaultextension='.qopt')
        t = text.get(0.0, END)
        filename = f.name
        f.write(t.rstrip())
        root.title(filename)
    except:
        showerror(title="Something went wrong",
                        message="Unable to save file...")


def open_mpc_file(event=None):
    global filename
    try:
        f = askopenfile(mode='r')
        t = f.read()
        filename = f.name

        text.delete(0.0, END)
        text.insert(0.0, t)
        root.title(filename)
        highlight()
    except:
        pass

def open_data_file(event=None):
    global data_filename
    try:
        f = askopenfile(mode='r')
        data_filename = f.name
    except:
        pass

def init_text(event=None):
    global filename
    try:
        f = open("mpc.qopt")
        t = f.read()
        filename = f.name

        text.delete(0.0, END)
        text.insert(0.0, t)
        root.title(filename)
        highlight()
    except:
        pass


def popup(event):
    rightClick.post(event.x_root, event.y_root)


def copy(event=None):
    global clipboard
    sel = text.selection_get()
    clipboard = sel


def cut(event=None):
    global clipboard
    sel = text.selection_get()
    clipboard = sel
    text.delete(SEL_FIRST, SEL_LAST)


def paste(event=None):
    global clipboard
    try:
        text.insert(INSERT, clipboard)
    except:
        pass
    highlight()


def select_all(event=None):
    text.tag_add(SEL, "1.0", END)
    text.mark_set(0.0, END)
    text.see(INSERT)
    return 'break'


def deselect_all(event=None):
    text.tag_remove(SEL, "1.0", END)


def highlight(event=None):
    # make a tag for change the color.
    text.tag_configure("blue", foreground="#48d")

    # apply the tag.
    text.highlight_pattern("parameters", "blue")
    text.highlight_pattern("variables", "blue")
    text.highlight_pattern("limits", "blue")
    text.highlight_pattern("minimize", "blue")
    text.highlight_pattern("subject to", "blue")
    text.highlight_pattern("end", "blue")
    text.highlight_pattern("dimensions", "blue")
    text.highlight_pattern("settings", "blue")


def generate_c(event=None):
    global filename
    global data_filename
    global generated_c
    problem_file = filename
    res_file = "solution.c"
    data_file = data_filename
    try:
        parse_mpc(problem_file, res_file, data_file )

        showinfo(title="C code generation",
                 message="The generated C code was written to " + res_file)
        generated_c = True
    except:
        showerror(title="Error", message="Something went wrong!")


def run_code(event=None):
    global filename
    global data_filename
    if None in (filename, data_filename):
        showerror(title="Error", message="Both a data file and MPC file must be specified!")
        return
    elif not generated_c:
        generate_c()
    cmd_line = "make && ./solution"
    os.system(cmd_line)


def quit(event=None):
    root.quit()
    root.destroy()


root = Tk()

# main label
mainLabel = Label(root, text="QuadOpt Alpha", font="Verdana 12 bold",
                  fg="#305080", bg="#f6f6f6")
mainLabel.pack(expand=False, fill="x")

# sidebar
sideBar = Frame(root, width=150, bg="#f6f6f6", height=400, relief="sunken",
                borderwidth=2)
sideBar.pack(expand=False, fill="both", side="left", anchor="nw")

# main content area and scrollbar
scrollbar = Scrollbar()
scrollbar.pack(side=RIGHT, fill=Y)

mainArea = Frame(root, bg="white", width=600, height=400, relief="sunken",
                 borderwidth=2)
mainArea.pack(expand=True, fill="both", side="right")

text = CustomText(mainArea, yscrollcommand=scrollbar.set, undo=True)
text.pack(expand=True, fill="both")

scrollbar.config(command=text.yview)

blankLabel = Label(sideBar, text=" ", font="Verdana 12 bold",
                   fg="#305080", bg="#f6f6f6")
blankLabel.pack()

codegenLabel = Label(sideBar, text="CODEGEN", font="Verdana 12 bold",
                     fg="#305080", bg="#f6f6f6")
codegenLabel.pack()
cButton = Button(sideBar, text="C code", width=15, command=generate_c)
cButton.pack()

runButton = Button(sideBar, text="Run code", width=15, command=run_code)
runButton.pack()

exitButton = Button(sideBar, text="Exit", width=15, command=quit)   
exitButton.pack(side=BOTTOM)

# menu
menuBar = Menu(root)
fileMenu = Menu(menuBar)
fileMenu.add_command(label="New", command=new_file)
fileMenu.add_command(label="Open MPC file", command=open_mpc_file)
fileMenu.add_command(label="Open data file", command=open_data_file)
fileMenu.add_command(label="Save", command=save_file)
fileMenu.add_command(label="Save As...", command=save_as)
fileMenu.add_separator()
fileMenu.add_command(label="Quit", command=root.quit)
menuBar.add_cascade(label="File", menu=fileMenu)

editMenu = Menu(menuBar)
editMenu.add_command(label="Copy", command=copy)
editMenu.add_command(label="Cut", command=cut)
editMenu.add_command(label="Paste", command=paste)
editMenu.add_command(label="Select All", command=select_all)
menuBar.add_cascade(label="Edit", menu=editMenu)

rightClick = Menu(root, tearoff=0)
rightClick.add_command(label="Copy", command=copy)
rightClick.add_command(label="Cut", command=cut)
rightClick.add_command(label="Paste", command=paste)
rightClick.add_separator()
rightClick.add_command(label="Select All", command=select_all)

# Keybindings
text.bind("<Button-3>", popup)
text.bind("<Button-1>", deselect_all)
text.bind("<Control-c>", copy)
text.bind("<Control-v>", paste)
text.bind("<Control-x>", cut)
text.bind("<Control-s>", save_file)
text.bind("<Control-S>", save_as)
text.bind("<Control-n>", new_file)
text.bind("<Control-a>", select_all)
text.bind("<Control-q>", quit)
root.bind("<KeyPress>", highlight)

root.config(menu=menuBar)
root.wm_title("QuadOpt Solver")
root.protocol("WM_DELETE_WINDOW", quit)
root.geometry("700x620")

init_text()
root.mainloop()