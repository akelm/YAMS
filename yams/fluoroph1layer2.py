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
#import time
import pickle
#import yaml
#from multiprocessing.pool import ThreadPool
#import threading

class LoopObj:
    def __init__(self,params,mat_sizecor_dict,settings):
        [self.dd_init,self.nielokalne_init,self.sizecor_init,self.tempcor_init,\
         self.nK_init,self.Cepsilon_init,self.layers_init,self.dip_range_init,\
         self.nNmax,self.Lambda,self.T,self.pin,self.taun,self.bn1mat]=params
        self.mat_sizecor_dict=mat_sizecor_dict
        self.settings=settings
        self.keys=('Ca_dict','dip_range','QextM', 'QscaM', 'QabsM','QextT', 'QscaT', 'QabsT', 'MRadPerp',\
          'MRadPara',  'MNRPerp',  'MNRPara',  'MTotPerp',  'MTotPara', 'Fexcperp','Fexcpara')
    def loop_funct(self,Ca):

#        print(self.parent_tid)
#        print(threading._active.items())

#            print(os.getpid())
        Ca_dict=np.array(Ca) # this will be added to dict
#        print(Ca_dict)
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
        dip_range=self.dip_range_init if dd==0 else Ca[dd-1]+self.dip_range_init
        
        # transition matrices for fields
        (ME,MM,TE,TM,Cepsilon,kL,RBx,RBz,RBl,xk,zk,xkl)=\
        MulSuscepPRST(self.nNmax,Ca,self.Lambda,nielokalne,sizecorr,tempcorr,\
                      Cepsilon,layers,self.T,self.mat_sizecor_dict)
        
        # extinction,absorption and scattering coefficients by two methods
        (QextM, QscaM, QabsM)=extcoeff_M(xk[-1],ME[0],MM[0],self.settings)
        (QextT, QscaT, QabsT)=extcoeff_T(xk[-1],TE[-1],TM[-1],self.settings)
        # enh factors
        fargs=(Ca, Cepsilon, dd ,kL, self.Lambda, RBx,RBz,xk,zk,
                  ME,MM,TE,TM,self.pin,self.taun,self.bn1mat,self.settings)
        ffact=self.factor(fargs)
        num_jobs= mp.cpu_count()
        multiproc=self.settings['multiprocessing']  and (dip_range.size>1)
        if multiproc:
            with mp.Pool(processes=num_jobs) as pool2:
                res2 = pool2.map_async(ffact.run, dip_range.tolist())
                res2.wait()
            ress=res2.get()
        else:
            ress=[]
            for dip_pos in dip_range.tolist():
                ress.append(ffact.run(dip_pos)) # D x 8 x L
        # translating list of results into array
        ress_array=np.array(ress).swapaxes(1,2) # D x L x 8
#        (MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara,Fexcperp,\
#         Fexcpara)=[np.zeros([dip_range.size,self.Lambda.size])]*8
        [MRadPerp,  MRadPara,  MNRPerp,  MNRPara,MTotPerp,  MTotPara,Fexcperp,\
         Fexcpara]=[ress_array[:,:,ind1] for ind1 in range(8)]
#
#        print(MRadPerp.shape)
#        print(Fexcperp.shape)
        out_dict=dict(zip(self.keys,map(locals().get,self.keys)))
        return out_dict
    
    class factor:
        def __init__(self,params):
            (self.Ca, self.Cepsilon, self.dd ,self.kL, self.Lambda, self.RBx,
             self.RBz,self.xk,self.zk,self.ME,self.MM,self.TE,self.TM,self.pin, 
             self.taun,self.bn1mat,self.settings)=params
        def run(self,dip_pos):
            (MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara)=\
            int_wszystko(self.Ca, self.Cepsilon, self.dd ,dip_pos,self.kL, self.Lambda, 
                         self.RBx,self.RBz,self.xk,self.zk,self.ME,self.MM,self.TE,self.TM,self.settings)
            (Fexcperp,  Fexcpara)=\
            wzm_layer(self.ME[0],self.MM[0], self.ME[self.dd],self.MM[self.dd],self.Lambda,
                      dip_pos, self.Cepsilon[self.dd],self.pin, self.taun,self.bn1mat,self.settings)
#            print(MRadPerp.shape)
#            print(Fexcperp.shape)
            return [MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara,Fexcperp,  Fexcpara]
        
def fluoroph1layer2(parfile=[],data=[],savename=None,mat_dict=None,\
                    mat_sizecor_dict=None,mat_tempcor_dict=None,fotof_files=None):
#    print("started fluoroph1layer2")
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
            mat_sizecor_dict=yaml.load(stream)
    if not mat_dict:        
        with open('../pkg_resources/materials.yaml') as stream:
            mat_dict=yaml.load(stream)
    if not mat_tempcor_dict:
        with open('../pkg_resources/mat_tempcor.yaml') as stream:
            mat_tempcor_dict=yaml.load(stream)
    # settings file
    with open('../pkg_resources/settings.yaml') as stream:
        settings=yaml.load(stream)
    # function extracting variables from the file contents
    (nNmax,Lambda,Cepsilon_init,Camat,dd_init,nielokalne_init,sizecor_init,\
     tempcor_init,T,pin,taun,bn1mat,layers_init,dip_range_init,rho_rel)=\
     parametry1(data, mat_dict, mat_sizecor_dict,mat_tempcor_dict) 
    # initial number of interfaces
    nK_init=Camat.shape[1]
    
    num_jobs = mp.cpu_count()
#   check if can go multiproc now
    multiproc=settings['multiprocessing'] and (Camat.shape[0]>=num_jobs or Camat.shape[0]>dip_range_init.size)
#   disables multiproc inside loop
    if multiproc: settings['multiprocessing']=False
        
    param_loop=[dd_init,nielokalne_init,sizecor_init,tempcor_init,nK_init,\
                Cepsilon_init,layers_init,dip_range_init,nNmax,Lambda,T,pin, taun,bn1mat]
    loop_obj=LoopObj(param_loop,mat_sizecor_dict,settings)
    
#    start_time = time.time()
#    print(type(mp.cpu_count()))
#    print(Camat.shape[0])
# multiprocessing


#    num_jobs = 2
#    free_cpus = np.maximum( np.round(mp.cpu_count()-num_jobs)/num_jobs,0)
    #multiproc=settings['multiprocessing'] and (Camat.shape[0]>=num_jobs or Camat.shape[0]>dip_range_init.size)
    if multiproc:
        
        with mp.Pool(processes=num_jobs) as pool:
            res = pool.map_async(loop_obj.loop_funct, Camat.tolist())
            res.wait()
        results=res.get()
    else:
 # no multiprocessing or one job
         results=[]
         for Ca in Camat.tolist():
             results.append(loop_obj.loop_funct(Ca))
             
#    pool=ThreadPool(num_jobs)
#    results = pool.map(loop_obj.loop_funct, Camat.tolist())
#    #close the pool and wait for the work to finish 
#    pool.close() 
#    pool.join() 
#    print(str(time.time() - start_time))
#    print(type(results.get()))    
    save_dic={'results':results,'param':data,'rho_rel':rho_rel, 'dip_range':dip_range_init}
    

    if savename:
        dirname=os.path.dirname(savename)
        filename=os.path.basename(savename)
        rawname=os.path.splitext(filename)[0]
        # create path if nonexistent
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        dirname=dirname+'/'
#        filename=os.path.basename(savename)        
#        picklefile=savename+'.pickle'
        with open(dirname+rawname+'.pickle','wb') as f:
            pickle.dump(save_dic,f)
            # saving obj to .mat file
        sio.savemat(dirname+rawname+'.mat',save_dic) 
    if fotof_files!=None:
        porph_int(results=results,data=data,savename=savename,rho_rel=rho_rel,dip_range=dip_range_init,fotof_files=fotof_files,settings=settings)
    
    
