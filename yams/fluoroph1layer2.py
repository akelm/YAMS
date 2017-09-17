import numpy as np
from MulSuscepPRST import MulSuscepPRST
from extcoeff import *
from int_wszystko import int_wszystko
from wzm_layer import wzm_layer
#from wzm_layer_matlab import wzm_layer_matlab
from parametry1 import parametry1
import yaml
from porph_int import porph_int
import scipy.io as sio
import os
import multiprocessing as mp
import time
import pickle
#import yaml
from multiprocessing.pool import ThreadPool
#import threading

class LoopObj:
    def __init__(self,params,mat_sizecor_dict):
        [self.dd_init,self.nielokalne_init,self.sizecor_init,self.tempcor_init,\
         self.nK_init,self.Cepsilon_init,self.layers_init,self.dip_pos_init,\
         self.nNmax,self.Lambda,self.T,self.pin,self.taun,self.bn1mat]=params
        self.mat_sizecor_dict=mat_sizecor_dict
        self.keys=('Ca_dict','QextM', 'QscaM', 'QabsM','QextT', 'QscaT', 'QabsT', 'MRadPerp',\
          'MRadPara',  'MNRPerp',  'MNRPara',  'MTotPerp',  'MTotPara', 'Fexcperp','Fexcpara')
    def loop_funct(self,Ca):

#        print(self.parent_tid)
#        print(threading._active.items())

#            print(os.getpid())
        Ca_dict=np.array(Ca) # this will be added to dict
        # the following will remove layer when its size is 0
        # new dipole layer number
        dd=self.dd_init-np.count_nonzero(np.array(np.where(Ca_dict==0))<self.dd_init)
        # new numbers of nonlocal layer
        nielokalne=[n - np.count_nonzero(np.array(np.where(Ca_dict==0))<n) for n in self.nielokalne_init \
                    if (n - np.count_nonzero(np.array(np.where(Ca_dict==0))<n))>=0]
        sizecorr=[n - np.count_nonzero(np.array(np.where(Ca_dict==0))<n) for n in self.sizecor_init \
                    if (n - np.count_nonzero(np.array(np.where(Ca_dict==0))<n))>=0]
        tempcorr=[n - np.count_nonzero(np.array(np.where(Ca_dict==0))<n) for n in self.tempcor_init \
                    if (n - np.count_nonzero(np.array(np.where(Ca_dict==0))<n))>=0]
        # new list layer sizes
        niezera=np.where(Ca)[0].tolist()
        Ca=list(map(Ca.__getitem__,niezera))
        # actual position of interfaces
        Ca=np.cumsum(Ca).tolist()
        # new number of interfaces
#        nK=len(Ca)
        # new list of dielectric constants
        niezera.append(self.nK_init)
        Cepsilon=list(map(self.Cepsilon_init.__getitem__,niezera))
        layers=list(map(self.layers_init.__getitem__,niezera))
        
        # default dipole position, this will be improved
        dip_pos=self.dip_pos_init if dd==0 else Ca[dd-1]+self.dip_pos_init
        
        # transition matrices for fields
        (ME,MM,TE,TM,Cepsilon,kL,RBx,RBz,RBl,xk,zk,xkl)=\
        MulSuscepPRST(self.nNmax,Ca,self.Lambda,nielokalne,sizecorr,tempcorr,\
                      Cepsilon,layers,self.T,self.mat_sizecor_dict)
        
        # extinction,absorption and scattering coefficients by two methods
        (QextM, QscaM, QabsM)=extcoeff_M(xk[-1],ME[0],MM[0])
        (QextT, QscaT, QabsT)=extcoeff_T(xk[-1],TE[-1],TM[-1])
        
        # dipole emission
        (MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara)=\
        int_wszystko(Ca, Cepsilon, dd, dip_pos ,kL, self.Lambda, RBx,RBz,xk,zk,ME,MM,TE,TM)
        
        # excitation enhancement with plane-wave excitation
        (Fexcperp,  Fexcpara)=wzm_layer(ME[0],MM[0], ME[dd], MM[dd],self.Lambda,\
            dip_pos, Cepsilon[dd],self.pin, self.taun,self.bn1mat)
#        matlab_keys=['Lambda','dip_pos','pin', 'taun','bn1mat']
        out_dict=dict(zip(self.keys,map(locals().get,self.keys)))
        return out_dict    


def fluoroph1layer2(parfile=[],data=[],savename=None,mat_dict=None,\
                    mat_sizecor_dict=None,mat_tempcor_dict=None,fotof_files=None):
#    print(parent_tid)
    if (parfile and data):
        raise Exception("two param input sources")
    if not (parfile or data):
        raise Exception("no sources for param")
    if not data:
        try:
           # open the file with parameters
           myfile=open(parfile)
        except FileNotFoundError:
            print("Path for param file: "+parfile+"is invalid")
        else:
            # importing yaml file
            #data=myfile.read()
            data=yaml.load(myfile)
    # loading materials file if necessary
    if not mat_sizecor_dict:    
        with open('../pkg_resources/mat_sizecor.yaml') as stream:
            self.mat_sizecor_dict=yaml.load(stream)
    if not mat_dict:        
        with open('../pkg_resources/materials.yaml') as stream:
            self.mat_dict=yaml.load(stream)
    if not mat_tempcor_dict:
        with open('../pkg_resources/mat_tempcor.yaml') as stream:
            self.mat_tempcor_dict=yaml.load(stream)
    
    # function extracting variables from the file contents
    (nNmax,Lambda,Cepsilon_init,Camat,dd_init,nielokalne_init,sizecor_init,\
     tempcor_init,T,pin,taun,bn1mat,layers_init,dip_pos_init,rho_rel)=\
     parametry1(data, mat_dict, mat_sizecor_dict,mat_tempcor_dict) 
    # initial number of interfaces
    nK_init=Camat.shape[1]

    param_loop=[dd_init,nielokalne_init,sizecor_init,tempcor_init,nK_init,\
                Cepsilon_init,layers_init,dip_pos_init,nNmax,Lambda,T,pin, taun,bn1mat]
    loop_obj=LoopObj(param_loop,mat_sizecor_dict)
    
#    start_time = time.time()
    num_jobs = mp.cpu_count()
#    num_jobs = 2
    with mp.Pool(processes=num_jobs) as pool:
        results = pool.map_async(loop_obj.loop_funct, Camat.tolist())
        results.wait()

#    pool=ThreadPool(num_jobs)
#    results = pool.map(loop_obj.loop_funct, Camat.tolist())
#    #close the pool and wait for the work to finish 
#    pool.close() 
#    pool.join() 
#    print(str(time.time() - start_time))
        
    save_dic={'results':results.get(),'param':data,'rho_rel':rho_rel}
    

    if savename:
        dirname=os.path.dirname(savename)
        # create path if nonexistent
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dirname=dirname+'/'
#        filename=os.path.basename(savename)        
#        picklefile=savename+'.pickle'
        with open(savename+'.pickle','wb') as f:
            pickle.dump(save_dic,f)
            # saving obj to .mat file
        sio.savemat(savename+'.mat',save_dic) 
    if fotof_files!=None:
        porph_int(results=results.get(),data=data,savename=savename,rho_rel=rho_rel,fotof_files=fotof_files)
    
    
