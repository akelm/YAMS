#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:19:57 2017

@author: ania
"""
import scipy.io as sio
import yaml
import pickle
from parametry1 import zakres
from operator import *
import re
import numpy as np
from itertools import repeat
import matplotlib.pyplot as plt
import os

def int_spectrum(indices,spectrum,factor):
    enh=np.array(list(map(factor.__getitem__,indices)))
    res=np.sum(enh*spectrum)/np.sum(spectrum)
    return res

def porph_int(results=[],data=[],picklefile=[],savename=None,rho_rel=1,fotof_files=None):
    # loading pickle file
    if picklefile:
        with open(picklefile,'rb') as f:
            dic = pickle.load(f)
            picklecontent=dic['picklecontent']
    if results and data:
        picklecontent={'results':results,'param':data,'rho_rel':rho_rel}
        
    if savename:
        dirname=os.path.dirname(savename)
        # create path if nonexistent
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dirname=dirname+'/'
        filename=os.path.basename(savename)        
    else:
        dirname='../results/'
      
    
    # wavelenghts from calculation
    Lambda=zakres(picklecontent['param']['wavelength'])
    Lambda_dic=dict(zip(Lambda, np.arange(Lambda.size)))
    # for iteration in results
    Mpattern=re.compile('(\\bM\\w+)')
    # list with files with fotophysical data
    # finding shape of geometry parameters
    Camat=np.array(tuple(map(getitem,picklecontent['results'],repeat('Ca_dict'))))
    matrix_size=list(map(len,(map(set,np.swapaxes(Camat,1,0)))))
    photoph={}
    photoph['rho_rel']=rho_rel
    # putting Q into matrix
    qkeys=('QextM', 'QscaM', 'QabsM','QextT', 'QscaT', 'QabsT')
    for key in qkeys:
        # coeffients scaled by rho_rel, just to notice the changes of concentration
        # on the spectra
        photoph[key]=\
            np.array(tuple(map(getitem,picklecontent['results'],repeat(key)))).\
            reshape(([*matrix_size,Lambda.size]))*photoph['rho_rel']

#    fotof_files=['tpp.yaml','pdtppF.yaml','pdtppP.yaml']
    # loading photophysics
    for fotof_file in fotof_files:
        with open('../pkg_resources/photophysics/'+fotof_file) as stream:
            fotof=yaml.load(stream)
        spectrum=np.genfromtxt('../pkg_resources/photophysics/'+fotof['emission'],dtype=float)
        # indices of wavelengths of emission
        spectrum_range=list(map(Lambda_dic.get,spectrum[:,0]))
        # to distingiush fotof file
        sufix=fotof_file.split('.')[0]
        # list with temp photophysics results
        results_photoph=[]
        # for every iteration from fluoroph1layer2
        for result in picklecontent['results']:
            result_dict={}
            # for every result for emission
            for key in Mpattern.findall(' '.join(result.keys())):    
                # integrate with emission of flurophore
                # it actually gives single value
                result['Fk'+key[1:]]=int_spectrum(spectrum_range,spectrum[:,1],result[key][:,0])
            # compute Ftau and FQY for each result
            result_dict['MRad_'+sufix]=\
                  (result['MRadPerp']*fotof['orient'][0] + result['MRadPara']*fotof['orient'][1])/\
                  np.sum(fotof['orient'])
            result_dict['Fexc_'+sufix]=\
                (result['Fexcperp']*fotof['orient'][0] + result['Fexcpara']*fotof['orient'][1])/\
                  np.sum(fotof['orient'])
            result_dict['Ftau_'+sufix]=1/fotof['QY']/(1./fotof['QY']-1 +\
                  (result['FkTotPerp']*fotof['orient'][0] + \
                   result['FkTotPara']*fotof['orient'][1])/np.sum(fotof['orient']))
            result_dict['FQY_'+sufix]=\
                  (result['FkRadPerp']*fotof['orient'][0] + result['FkRadPara']*fotof['orient'][1])/\
                  np.sum(fotof['orient'])*result_dict['Ftau_'+sufix]
#            result_dict['Qext_'+sufix]=result['FkRadPerp']
            results_photoph.append(result_dict)
#        photoph['results']=results_photoph

        # obtainting results as matrix
        # single value results
        photoph['Ftau_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('Ftau_'+sufix)))).reshape(matrix_size)
        photoph['FQY_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('FQY_'+sufix)))).reshape(matrix_size)
        # spectra
        photoph['Frad_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('MRad_'+sufix)))).\
            reshape([*matrix_size,Lambda.size])
        # with effect of higher concentration because of contraction
        photoph['Fexc_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('Fexc_'+sufix)))).\
            reshape([*matrix_size,Lambda.size])*photoph['rho_rel']
        photoph['FGamma_'+sufix]=\
            photoph['Fexc_'+sufix]*(photoph['FQY_'+sufix].reshape([*matrix_size,1]))
    
        # dictionary for saving
        dict_keys=('Ftau','FQY','Frad','Fexc','FGamma')
        dict_keys1=('Ftau_'+sufix,'FQY_'+sufix,'Frad_'+sufix,'Fexc_'+sufix,'FGamma_'+sufix)
        mat_dict=dict(zip(dict_keys,map(locals().get,dict_keys)))
        mat_dict1=dict(zip(dict_keys1,map(locals().get,dict_keys)))
        # so much plots, so much fun
        
        labels={'FQY_'+sufix:'Quantum efficiency enhancement','Ftau_'+sufix:'Excited state lifetime reduction',\
                'Frad_'+sufix:'Radiative decay rate enhancement','Fexc_'+sufix:'Excitation rate enhancement',\
                'FGamma_'+sufix:'Total emission enhancement'}
        ifspectra={'Frad_'+sufix:[550,650,720],'Fexc_'+sufix:[418,520,550],'FGamma_'+sufix:[418,520,550]}
        
        
        w_start=Lambda[0]
        w_every=Lambda[1]-Lambda[0] 
        # checking what to plot
        plt.ioff()
        if sum(list(map(gt,matrix_size,repeat(1))))==1:
            # normal 2D plot
            # looking for which dimension
            indd=list(map(gt,matrix_size,repeat(1))).index(True)
            slice_1=np.zeros(len(matrix_size),dtype=int).tolist()
            slice_1[indd]=slice(0,matrix_size[indd])
            matx=picklecontent['param']['layers'][indd]['material']
            x_range=zakres(picklecontent['param']['layers'][indd]['range'])
      
            fig = plt.figure(figsize=(8,8*9/16))
            ax = fig.add_subplot(111)
            for key in labels.keys():
                img_list=[]
                title=[]
                fig_sufix=[]
                if key in ifspectra.keys():
                    for wave in ifspectra[key]:
                        slice1=[*slice_1,int((wave-w_start)/w_every)]
                        img_list.append(np.transpose(photoph[key][slice1]))
                        title.append(labels[key]+' at '+str(wave)+' nm')
                        fig_sufix.append(str(wave)+'_')
                else:
                    img_list=[np.transpose(photoph[key][slice_1])]
                    title=[labels[key]]
                    fig_sufix=['']
            
                for obj in zip(img_list,title,fig_sufix):
                    imgplot = plt.plot(x_range,obj[0],'-k')
                    ax.set_title(obj[1])
                    ax.set_xlabel(matx+' core radius / nm' if indd==0 else matx+' layer thickness / nm')
                    figname=key+'_'+obj[2] if not savename else dirname+key+'_'+obj[2]+filename
                    plt.savefig(figname+'.svg')
                    plt.cla()
#                    print(plt.get_fignums())
            plt.close('all')
#            print(plt.get_fignums())
        if sum(list(map(gt,matrix_size,repeat(1))))>1:
            # checking which two layers have most sizes
            (largest_ind,largest_values)=zip(*sorted(list(enumerate(matrix_size)),key=itemgetter(1),reverse=True))
            # two largest ind
            largest_ind=largest_ind[0:2]
            largest_slice=[slice(0,largest_values[0]),slice(0,largest_values[1])]
            # other indices
            other_ind=largest_ind[2:]
            matrix_size_other=largest_values[2:]
            other_slice=list(map(round,(map(mul,repeat(0.5),matrix_size_other))))
            comb_slices=[*largest_slice,*other_slice]
            (_,sorted_slices)=zip(*sorted(list(zip(largest_ind,comb_slices)),key=itemgetter(0)))
            largest_sorted=sorted(largest_ind)
            matx=picklecontent['param']['layers'][largest_sorted[0]]['material']
            maty=picklecontent['param']['layers'][largest_sorted[1]]['material']
            x_from=picklecontent['param']['layers'][largest_sorted[0]]['range']['from']
            x_to=picklecontent['param']['layers'][largest_sorted[0]]['range']['to']
            y_from=picklecontent['param']['layers'][largest_sorted[1]]['range']['from']
            y_to=picklecontent['param']['layers'][largest_sorted[1]]['range']['to']
            extent_list=[x_from,x_to,y_from,y_to]
    
            fig = plt.figure(figsize=(8+1.7,8*(y_to-y_from)/(x_to-x_from)))  
            ax = fig.add_subplot(111)
            for key in labels.keys():
                img_list=[]
                title=[]
                fig_sufix=[]    
                if key in ifspectra.keys():
                    for wave in ifspectra[key]:
                        slice1=[*sorted_slices,int((wave-w_start)/w_every)]
                        img_list.append(np.transpose(photoph[key][slice1]))
                        title.append(labels[key]+' at '+str(wave)+' nm')
                        fig_sufix.append(str(wave)+'_')
                else:
                    img_list=[np.transpose(photoph[key][sorted_slices])]
                    title=[labels[key]]
                    fig_sufix=['']
                    
                for obj in zip(img_list,title,fig_sufix):
                    imgplot = plt.imshow(obj[0],cmap="jet", interpolation="bicubic",\
                                         extent=extent_list)
                    ax.set_title(obj[1])
                    ax.invert_yaxis()
                    ax.set_xlabel(matx+' core radius / nm' if largest_sorted[0]==0 else matx+' layer thickness / nm')
                    ax.set_ylabel(maty+' layer thickness / nm')
                    plt.colorbar()
                    figname=key+'_'+obj[2] if not savename else dirname+key+'_'+obj[2]+filename
                    plt.savefig(figname+'.svg')
                    plt.cla()
#                    print(plt.get_fignums())
            plt.close('all')
#            print(plt.get_fignums())
    if savename:
        picklefile=dirname+filename+'_photoph'+'.pickle'
        with open(picklefile,'wb') as f:
                pickle.dump(photoph,f)
        # saving obj to .mat file
        sio.savemat(dirname+filename+'_photoph'+'.mat',photoph)
        
        


    

    
    
    
        