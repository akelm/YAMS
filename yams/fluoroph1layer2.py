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
        (QextM, QscaM, QabsM)=extcoeff_M(xk[-1],ME[0],MM[0])
        (QextT, QscaT, QabsT)=extcoeff_T(xk[-1],TE[-1],TM[-1])
        num_jobs= mp.cpu_count()
        multiproc=self.settings['multiprocessing']  and (dip_range.size>1)
        if multiproc:
            fargs=(Ca, Cepsilon, dd ,kL, self.Lambda, RBx,RBz,xk,zk,
                              ME,MM,TE,TM,self.pin,self.taun,self.bn1mat)
            ffact=self.factor(fargs)
            with mp.Pool(processes=num_jobs) as pool2:
                res2 = pool2.map_async(ffact.run, dip_range.tolist())
                res2.wait()
            ress=res2.get()
            resE=ress[slice(0,dip_range.size)][0:6]
            resX=ress[slice(0,dip_range.size)][6:8]
#            results=np.asarray(ress).swapaxes(0,1).tolist()
#            (MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara, 
#             Fexcperp,  Fexcpara)=results
        else:
            (MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara)=([],[],[],[],[],[])
            (Fexcperp,  Fexcpara)=([],[])
            resE=[]
            resX=[]
            for k in range(dip_range.size):
                print(k)
                dip_pos=dip_range[k]
                # dipole emission
                resE.append(int_wszystko(Ca, Cepsilon, dd, dip_pos ,kL, self.Lambda, RBx,RBz,xk,zk,ME,MM,TE,TM))
                # excitation enhancement with plane-wave excitation
                resX.append(wzm_layer(ME[0],MM[0], ME[dd], MM[dd],self.Lambda,\
                    dip_pos, Cepsilon[dd],self.pin, self.taun,self.bn1mat))
        (MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara)=\
                                    np.asarray(resE).swapaxes(0,1).tolist()
        (Fexcperp,  Fexcpara)=np.asarray(resX).swapaxes(0,1).tolist()
#                i=0
#                for item in (MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara):
#                    item.append(res[i])
#                    i+=1
#                
#                # excitation enhancement with plane-wave excitation
#                res1=wzm_layer(ME[0],MM[0], ME[dd], MM[dd],self.Lambda,\
#                    dip_pos, Cepsilon[dd],self.pin, self.taun,self.bn1mat)
#                i=0
#                for item in (Fexcperp,  Fexcpara):
#                    item.append(res1[i])
#                    i+=1
#    #        print('MRadPerp')
#    #        print(np.asarray(MRadPerp).shape)
#            [MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara, Fexcperp,  Fexcpara]=\
#            self.matswapaxes(MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara, Fexcperp,  Fexcpara,ax1=0,ax2=0)

                
         # in fact i don't swap axes   
#        matlab_keys=['Lambda','dip_pos','pin', 'taun','bn1mat']
        out_dict=dict(zip(self.keys,map(locals().get,self.keys)))
        return out_dict    
#    def matswapaxes(self,*matrices,ax1=0,ax2=0):
#        results=[]
#        for matrix in matrices:
#            results.append( np.asarray(matrix).swapaxes(ax1,ax2))
#        return results
    class factor:
        def __init__(self,params):
            (self.Ca, self.Cepsilon, self.dd ,self.kL, self.Lambda, self.RBx,
             self.RBz,self.xk,self.zk,self.ME,self.MM,self.TE,self.TM,self.pin, 
             self.taun,self.bn1mat)=params
        def run(self,dip_pos):
            (MRadPerp,  MRadPara,  MNRPerp,  MNRPara,  MTotPerp,  MTotPara)=\
            int_wszystko(self.Ca, self.Cepsilon, self.dd ,dip_pos,self.kL, self.Lambda, 
                         self.RBx,self.RBz,self.xk,self.zk,self.ME,self.MM,self.TE,self.TM)
            (Fexcperp,  Fexcpara)=\
            wzm_layer(self.ME[0],self.MM[0], self.ME[self.dd],self.MM[self.dd],self.Lambda,
                      dip_pos, self.Cepsilon[self.dd],self.pin, self.taun,self.bn1mat)
            print(MRadPerp.shape)
            print(Fexcperp.shape)
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
            self.mat_sizecor_dict=yaml.load(stream)
    if not mat_dict:        
        with open('../pkg_resources/materials.yaml') as stream:
            self.mat_dict=yaml.load(stream)
    if not mat_tempcor_dict:
        with open('../pkg_resources/mat_tempcor.yaml') as stream:
            self.mat_tempcor_dict=yaml.load(stream)
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
    multiproc=settings['multiprocessing'] and (Camat.shape[0]>=num_jobs or Camat.shape[0]>dip_range_init.size)
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
        porph_int(results=results,data=data,savename=savename,rho_rel=rho_rel,dip_range=dip_range_init,fotof_files=fotof_files)
    
    
