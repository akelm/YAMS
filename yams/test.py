#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 17:49:30 2017

@author: ania
"""
import pickle
import numpy as np

with open('/home/ania/Pulpit/publikacja_jpp/YAMS/results/res_2017_9_27_17_47_33/res_2017_9_27_17_47_33.pickle','rb') as f:
    picklecontent = pickle.load(f)
    i=0
    for result in picklecontent['results']:
       for key in result.keys():
           wyn=np.sum(result[key]==None)
           if wyn:
               print("result "+str(i))
               print(key+" "+str(wyn))
               print(result[key])
       i+=1               