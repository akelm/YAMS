#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 18:15:36 2017

taken from internets
"""
import tkinter as tk
#from tkinter import ttk
import numpy as np

class Drag_and_Drop_Listbox(tk.Listbox):
    """ A tk listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, dipole=None,**kw):
        kw['selectmode'] = tk.MULTIPLE
        kw['activestyle'] = 'none'
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.getState, add='+')
        self.bind('<Button-1>', self.setCurrent, add='+')
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None
        self.curState = None
        self.dipole=dipole
        self.medium_par=None
    def setCurrent(self, event):
        ''' gets the current index of the clicked item in the listbox '''
        self.curIndex = self.nearest(event.y)
    def getState(self, event):
        ''' checks if the clicked item in listbox is selected '''
        i = self.nearest(event.y)
        self.curState = self.selection_includes(i)
    def shiftSelection(self, event):
        # adds param to the last one
        self.AddParams()
        ''' shifts item up or down in listbox '''
        selected=None
        i = self.nearest(event.y)
        if self.curState == 1:
            self.selection_set(self.curindex)
        else:
            self.selection_clear(self.curIndex)
        if i < self.curIndex:
            # Moves up
            x = self.get(i)
            selected = self.selection_includes(i)
            self.delete(i)
            self.insert(i+1, x)
        if selected:
            self.selection_set(i+1)
            self.curIndex = i
        elif i > self.curIndex:
            # Moves down
            x = self.get(i)
            selected = self.selection_includes(i)
            self.delete(i)
            self.insert(i-1, x)
        if selected:
            self.selection_set(i-1)
            self.curIndex = i
        self.UpdateNumbering()

    def shiftSelectionUp(self):
        self.AddParams()
        ''' shifts item up or down in listbox '''
        #i = self.nearest(event.y)
        sel_items = self.curselection()
        
        for k in sel_items:
            if k>0 & ~self.selection_includes(k-1):
                # checks if k can be moved without swapping
               x = self.get(k)
               self.delete(k)
               self.insert(k-1, x)
               self.selection_set(k-1)

        self.UpdateNumbering()
        

              
    def shiftSelectionDown(self):
        self.AddParams()
        ''' shifts item up or down in listbox '''
        #i = self.nearest(event.y)
        sel_items = self.curselection()
        for k in sel_items[::-1]:
            if k<(self.size()-1) & ~self.selection_includes(k+1):
                # checks if k can be moved without swapping
               x = self.get(k)
               self.delete(k)
               self.insert(k+1, x)
               self.selection_set(k+1)
        self.UpdateNumbering()
               
    def DeleteSelection(self) :
        self.AddParams()
        rozm=self.size()
        items = list(map(int,self.curselection()))
        nonsel_items=list(set(range(rozm)) - set(items))
        for i in items[::-1] :
            self.delete( i,i )
        if nonsel_items:
            next_sel= max(items)+1 if max(items)+1<rozm else max(nonsel_items)
            next_sel=next_sel-np.count_nonzero(np.array(items)<next_sel)
            self.selection_set(next_sel)
        self.UpdateNumbering()
        
                
    def UpdateNumbering(self):
        if self.size()>0:
            for i in range(self.size()):
                ifsel=self.selection_includes(i)
                x=''.join(self.get(i).split('. ')[1:])
                x=str(i+1)+'. '+''.join(x)
                self.delete(i)
                self.insert(i,x)
                if ifsel:
                    self.selection_set(i)
            self.dipole['values'] = [x.split(",")[0] for x in self.get(0,tk.END)]
            self.dipole.set(self.dipole['values'][-1])
            ifsel=self.selection_includes(tk.END)
            x=self.get(tk.END)
            self.delete(tk.END)
            self.medium_par=''.join(x.split(',')[1:])
            self.insert(tk.END,x.split(', ')[0])
            if ifsel:
                self.selection_set(tk.END)
        
    def AddParams(self):
        if self.size()>0:
            ifsel=self.selection_includes(tk.END)
            x=self.get(tk.END)
            self.delete(tk.END)
            if self.medium_par:
                x=x+','+self.medium_par
            self.insert(tk.END,x)
            if ifsel:
                self.selection_set(tk.END)