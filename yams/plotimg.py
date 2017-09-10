#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 20:12:55 2017

@author: ania
"""
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pickle
from parametry1 import zakres

picklefile='res_2017_08_07_16_21_47_577351.pickle'
with open(picklefile,'rb') as f:
    data = pickle.load(f)
    
    labels={'FQY':'Quantum efficiency enhancement','Ftau':'Excited state lifetime reduction',\
            'Frad':'Radiative decay rate enhancement','Fexc':'Excitation rate enhancement'}
    ifspectra={'Frad':[550,650,720],'Fexc':[418,520,550]}
    matx=data['picklecontent']['param']['layers'][0]['material']
    maty=data['picklecontent']['param']['layers'][1]['material']
    x_from=data['picklecontent']['param']['layers'][0]['range']['from']
    x_span=data['picklecontent']['param']['layers'][0]['range']['to']-x_from
    y_from=data['picklecontent']['param']['layers'][1]['range']['from']
    y_span=data['picklecontent']['param']['layers'][1]['range']['to']-y_from
    w_start=data['picklecontent']['param']['wavelength']['from']
    w_every=data['picklecontent']['param']['wavelength']['every']

    x_tick_label=np.arange(x_from,x_from+x_span+10,10)
    y_tick_label=np.arange(y_from,y_from+y_span+10,10)

    xstr=list(map(str,x_tick_label))
    ystr=list(map(str,y_tick_label))
    

    for key in labels.keys():
        img_list=[]
        title=[]
            
        if key in ifspectra.keys():
            for wave in ifspectra[key]:
                img_list.append(np.transpose(data[key][:,:,int((wave-w_start)/w_every)]))
                title.append(labels[key]+' at '+str(wave)+' nm')
            
        else:
            img_list=[np.transpose(data[key])]
            title=[labels[key]]
            
        for obj in zip(img_list,title):
            fig = plt.figure(figsize=(8+1.7,8*y_span/x_span))
            ax = fig.add_subplot(111)
                
            imgplot = plt.imshow(obj[0],cmap="jet", interpolation="bicubic")
            ax.set_title(obj[1])
            ax.set_xticks(np.arange(0,x_span+10,10))
            ax.set_yticks(np.arange(0,y_span+10,10))
            
            ax.set_xticklabels(xstr)
            ax.set_yticklabels(ystr)
            ax.invert_yaxis()
            ax.set_xlabel(matx+' core radius / nm')
            ax.set_ylabel(maty+' layer thickness / nm')
        
            plt.colorbar()
            plt.savefig(obj[1]+'.svg')