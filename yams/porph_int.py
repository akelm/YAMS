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
    enh=np.array(list(map(factor.swapaxes(0,1).__getitem__,indices))).swapaxes(0,1) # D x L
    res=np.sum(enh*spectrum[None,:],1)/np.sum(spectrum) # D x 1
    return res

def porph_int(results=[],data=[],picklefile=[],savename=None,rho_rel=1,dip_range=[],fotof_files=None,settings=None):

    # loading pickle file
    if picklefile:
        with open(picklefile,'rb') as f:
#            print('opening picklefile '+picklefile)
            picklecontent = pickle.load(f)
#            picklecontent=dic['picklecontent']
    if results and data:
        picklecontent={'results':results,'param':data,'rho_rel':rho_rel,'dip_range':dip_range}
        
    if savename:
        dirname=os.path.dirname(savename)
        # create path if nonexistent
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dirname=dirname+'/'
        filename=os.path.basename(savename)
        rawname=os.path.splitext(filename)[0]        
    else:
        dirname='../results/'
    # settings file
    if not settings:
        with open('../pkg_resources/settings.yaml') as stream:
            settings=yaml.load(stream)
    
    
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
    photoph['rho_rel']=picklecontent['rho_rel']
    photoph['dip_range']=picklecontent['dip_range']
    photoph['param']=picklecontent['param']
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
#        print(fotof_file)
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
                # it actually gives vector with length=dip distances
#                print(key)
#                print(result[key].shape)
                result['Fk'+key[1:]]=int_spectrum(spectrum_range,spectrum[:,1],result[key]) # D x 1
#                print(result['Fk'+key[1:]].shape)
            # compute Ftau and FQY for each result
            result_dict['MRad_'+sufix]=\
                  (result['MRadPerp']*fotof['orient'][0] + result['MRadPara']*fotof['orient'][1])/\
                  np.sum(fotof['orient']) # D x L
            result_dict['Fexc_'+sufix]=\
                (result['Fexcperp']*fotof['orient'][0] + result['Fexcpara']*fotof['orient'][1])/\
                  np.sum(fotof['orient'])  # D x L
            result_dict['FkTot_'+sufix]=(result['FkTotPerp']*fotof['orient'][0] + \
                   result['FkTotPara']*fotof['orient'][1])/np.sum(fotof['orient'])
            result_dict['FkRad_'+sufix]=(result['FkRadPerp']*fotof['orient'][0] + \
                   result['FkRadPara']*fotof['orient'][1])/np.sum(fotof['orient'])
            result_dict['Ftau_'+sufix]=1/(1 + (result_dict['FkTot_'+sufix]-1)*fotof['QY']) # D x 1
#            1/fotof['QY']/(1./fotof['QY']-1 +\
#                  (result['FkTotPerp']*fotof['orient'][0] + \
#                   result['FkTotPara']*fotof['orient'][1])/np.sum(fotof['orient']))  # D x 1
            result_dict['FQY_'+sufix]=\
                  result_dict['FkRad_'+sufix]*result_dict['Ftau_'+sufix] # D x 1
#            result_dict['Qext_'+sufix]=result['FkRadPerp']
            results_photoph.append(result_dict)
#        photoph['results']=results_photoph

        # obtainting results as matrix
        # single value results
        photoph['Ftau_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('Ftau_'+sufix)))).reshape([*matrix_size,photoph['dip_range'].size])
        photoph['FQY_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('FQY_'+sufix)))).reshape([*matrix_size,photoph['dip_range'].size])
        photoph['FkRad_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('FkRad_'+sufix)))).reshape([*matrix_size,photoph['dip_range'].size])
        photoph['FkTot_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('FkTot_'+sufix)))).reshape([*matrix_size,photoph['dip_range'].size])
        # spectra
        photoph['Frad_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('MRad_'+sufix)))).\
            reshape([*matrix_size,photoph['dip_range'].size,Lambda.size])
        # with effect of higher concentration because of contraction
        photoph['Fexc_'+sufix]=\
            np.array(tuple(map(getitem,results_photoph,repeat('Fexc_'+sufix)))).\
            reshape([*matrix_size,photoph['dip_range'].size,Lambda.size])*photoph['rho_rel']
        photoph['FGamma_'+sufix]=\
            photoph['Fexc_'+sufix]*(photoph['FQY_'+sufix].reshape([*matrix_size,photoph['dip_range'].size,1]))
        
#        # dictionary for saving
#        dict_keys=('Ftau','FQY','Frad','Fexc','FGamma')
#        dict_keys1=('Ftau_'+sufix,'FQY_'+sufix,'Frad_'+sufix,'Fexc_'+sufix,'FGamma_'+sufix)
#        mat_dict=dict(zip(dict_keys,map(locals().get,dict_keys)))
#        mat_dict1=dict(zip(dict_keys1,map(locals().get,dict_keys)))
        if settings['images']:
            # so much plots, so much fun
            
            labels={'FQY_'+sufix:'Quantum efficiency enhancement','Ftau_'+sufix:'Excited state lifetime reduction',\
                    'Frad_'+sufix:'Radiative decay rate enhancement','Fexc_'+sufix:'Excitation rate enhancement',\
                    'FGamma_'+sufix:'Total emission enhancement'}
            ifspectra={'Frad_'+sufix:settings['em'],'Fexc_'+sufix:settings['exc'],'FGamma_'+sufix:settings['exc']}
#            print(type(settings['em'][0]))
            
            w_start=Lambda[0]
            w_every=Lambda[1]-Lambda[0] 
            # checking what to plot
            plt.ioff()
            if sum(list(map(gt,[*matrix_size,photoph['dip_range'].size],repeat(1))))==1:
                # normal 2D plot
                # looking for which dimension
                indd=list(map(gt,[*matrix_size,photoph['dip_range'].size],repeat(1))).index(True)
                slice_1=np.zeros(len(matrix_size)+1,dtype=int).tolist()
                slice_1[indd]=slice(0,[*matrix_size,photoph['dip_range'].size][indd])
                if indd==len(matrix_size):
                    matx='dipole distance'
                    x_range=photoph['dip_range']
                else:
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
                            if wave in Lambda.tolist():
                                slice1=[*slice_1,int((wave-w_start)/w_every)]
    #                            print(slice1)
    #                            print(photoph[key].shape)
    #                            print(np.transpose(photoph[key][slice1]).shape)
                                img_list.append(np.transpose(photoph[key][slice1]))
                                title.append(labels[key]+' at '+str(wave)+' nm')
                                fig_sufix.append(str(wave)+'_')
                    else:
                        img_list=[np.transpose(photoph[key][slice_1])]
                        title=[labels[key]]
                        fig_sufix=['']
                
                    for obj in zip(img_list,title,fig_sufix):
    #                    print(x_range)
    #                    print(obj[0].shape)
    #                    print(obj[1])
    #                    print(obj[2])
                        imgplot = plt.plot(x_range,obj[0],'-k')
                        ax.set_title(obj[1])
                        ax.set_xlabel(matx+' core radius / nm' if indd==0 else matx+' layer thickness / nm')
                        figname=key+'_'+obj[2] if not savename else dirname+key+'_'+obj[2]+rawname
                        plt.savefig(figname+'.svg')
                        plt.cla()
    #                    print(plt.get_fignums())
                plt.close('all')
    #            print(plt.get_fignums())
            if sum(list(map(gt,[*matrix_size,photoph['dip_range'].size],repeat(1))))>1:
                # slices list, populated by all zeros
                slice_1=np.zeros(len(matrix_size)+1,dtype=int).tolist()
                # checking which two layers have most sizes
                (largest_ind,largest_values)=\
                zip(*sorted(list(enumerate([*matrix_size,photoph['dip_range'].size])),key=itemgetter(1),reverse=True))
                # updating slice matrix with two most populated slices
                slice_1[largest_ind[0]]=slice(0,largest_values[0])
                slice_1[largest_ind[1]]=slice(0,largest_values[1])
#                # two largest ind
#                largest_ind=largest_ind[0:2]
#                largest_slice=[slice(0,largest_values[0]),slice(0,largest_values[1])]
#                # other indices
#                other_ind=largest_ind[2:]
#                matrix_size_other=largest_values[2:]
#                other_slice=list(map(round,(map(mul,repeat(0.5),matrix_size_other))))
#                comb_slices=[*largest_slice,*other_slice]
#                (_,sorted_slices)=zip(*sorted(list(zip([largest_ind,other_ind],comb_slices)),key=itemgetter(0)))
#                largest_sorted=sorted(largest_ind)

                    
#                matx='';maty='';x_from=0;y_from=0;x_to=0;y_to=0
#                llx=list(zip([largest_ind[0:2],['',''],[0,0],[0,0]]))
                mat=[]
                extent_list=[]
                for d in largest_ind[0:2]:
                    if d==len(matrix_size):
                        mat.append('dipole distance')
                        extent_list.append(photoph['dip_range'][0])
                        extent_list.append(photoph['dip_range'][-1])
                    else:
                        mat.append(picklecontent['param']['layers'][d]['material'])
                        extent_list.append(picklecontent['param']['layers'][d]['range']['from'])
                        extent_list.append(picklecontent['param']['layers'][d]['range']['to'])
#                extent_list=[*llx[0][1:],*llx[1][1:]]
                (matx,maty)=mat
                (x_from,x_to,y_from,y_to)=extent_list
#                extent_list[1],extent_list[2]=extent_list[2],extent_list[1]
                
#                (matx,x_fom,x_to)=llx[0][1:]
#                (maty,y_fom,y_to)=llx[1][1:]
#                print(llx)
#                for (d,mat,ffrom,tto) in llx:
#                    # index is dipole range
#                    if d==len(matrix_size):
#                        mat='dipole distance' 
#                        ffrom=photoph['dip_range'][0]
#                        tto=photoph['dip_range'][-1]
#                    else:
#                        mat=picklecontent['param']['layers'][d]['material']
#                        ffrom=picklecontent['param']['layers'][d]['range']['from']
#                        tto=picklecontent['param']['layers'][d]['range']['to']
#                        print(ffrom,tto)
#                extent_list=[x_from,x_to,y_from,y_to]
#                print(llx)
                
                fig = plt.figure(figsize=(8+1.7,8*(y_to-y_from)/(x_to-x_from)))  
                ax = fig.add_subplot(111)
#                plt.colorbar()
                for key in labels.keys():
                    img_list=[]
                    title=[]
                    fig_sufix=[]    
                    if key in ifspectra.keys():
                        for wave in ifspectra[key]:
                            if wave in Lambda:
                                slice1=[*slice_1,int((wave-w_start)/w_every)]
                                img_list.append(np.transpose(photoph[key][slice1]))
                                title.append(labels[key]+' at '+str(wave)+' nm')
                                fig_sufix.append(str(wave)+'_')
                    else:
                        img_list=[np.transpose(photoph[key][slice_1])]
                        title=[labels[key]]
                        fig_sufix=['']
                        
                    for obj in zip(img_list,title,fig_sufix):
                        #print(extent_list)
                        #print(slice_1)
#                        imgplot = plt.imshow(obj[0],cmap="jet", interpolation="bicubic",\
#                                             extent=extent_list)
                        imgplot = plt.imshow(obj[0],cmap="jet", interpolation="bicubic")
                        cb=plt.colorbar()
                        ax.set_title(obj[1])
                        imgplot.set_extent([x_from,x_to,y_to,y_from])
                        ax.invert_yaxis()
                        ax.set_xlabel(matx+' core radius / nm' if largest_ind[0]==0 else matx+' layer thickness / nm')
                        ax.set_ylabel('dipole position / nm' if largest_ind[1]==len(matrix_size) else maty+' layer thickness / nm')
#                        plt.colorbar()
                        figname=key+'_'+obj[2] if not savename else dirname+key+'_'+obj[2]+rawname
                        plt.savefig(figname+'.svg')
                        cb.remove()
                        plt.cla()
                        
    #                    print(plt.get_fignums())
                plt.close('all')
    #            print(plt.get_fignums())
    if savename:
        picklefile=dirname+rawname+'_photoph'+'.pickle'
        with open(picklefile,'wb') as f:
                pickle.dump(photoph,f)
        # saving obj to .mat file
        sio.savemat(dirname+rawname+'_photoph'+'.mat',photoph)
        
        


    

    
    
    
        