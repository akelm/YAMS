import numpy as np
from scipy import special
from sum_conv import sum_conv

def wzm_layer(ME1,MM1, MEdd, MMdd,Lambda,odl, Ceps,pin, taun, bn1mat,settings):
## wzmocnienie pola w srodku warstwy
# (Cst{1}.ME,Cst{1}.MM, Cst{dd}.ME, Cst{dd}.MM,...
#            lambda, dip_pos ,Cepsilon{dd},theta,stPinTaun )
    nNbtheta=pin.shape[1]
    
    theta=np.linspace(0,np.pi,nNbtheta)[None,:,None]
    (Ecr_j,Ect_j,Esf_j)=PweEgenThetaAllPhi(Lambda,Ceps,\
    bn1mat*(MMdd[:,:,0,0] - MMdd[:,:,0,1]*MM1[:,:,1,0]/MM1[:,:,1,1])[:,:,None],\
    bn1mat*(MEdd[:,:,0,0] - MEdd[:,:,0,1]*ME1[:,:,1,0]/ME1[:,:,1,1])[:,:,None],\
    odl,theta,'j',pin,taun,settings) # [L x 1 x T]

    (Ecr_h,Ect_h,Esf_h)=PweEgenThetaAllPhi(Lambda,Ceps,\
    bn1mat*(MMdd[:,:,1,0]- MMdd[:,:,1,1]*MM1[:,:,1,0]/MM1[:,:,1,1])[:,:,None],\
    bn1mat*(MEdd[:,:,1,0] - MEdd[:,:,1,1]*ME1[:,:,1,0]/ME1[:,:,1,1])[:,:,None],\
    odl,theta,'h1',pin,taun,settings) # [L x 1 x T]


    Fexcperp= 3/2*np.matmul(np.absolute(Ecr_j+Ecr_h)**2, np.sin(theta)) \
    /np.sum(np.sin(theta)) # L
#    print(np.max(np.abs(MEdd[:,:,1,0]- MEdd[:,:,1,1]*ME1[:,:,1,0]/ME1[:,:,1,1]))) # L

    Fexcpara = 3/4*(np.matmul(np.absolute(Ect_j+Ect_h)**2 + np.absolute(Esf_j+Esf_h)**2, \
    np.sin(theta)) ) /np.sum(np.sin(theta))

    
    
    return (Fexcperp[:,0,0],Fexcpara[:,0,0])

def PweEgenThetaAllPhi(Lambda,epsilon,cn1,dn1,r0,theta,sBessel,pin,taun,settings):
    nNmax=cn1.shape[1]
    
    nm1=np.arange(0,nNmax+1)[None,:,None] # 1 x nNmax+1
    n=nm1[:,1:,:] # 1 x nNmax

    cffnr=np.sqrt((2*n+1)/(4*np.pi))  # 1 x nNmax
    mun=cffnr/(n*(n+1)) # 1 x nNmax
    
    if r0==0:
        Esf= (dn1[:,0,:]/np.sqrt(3*np.pi))[:,None]
        Ecr=-Esf * np.sin(theta)
        Ect=-Esf * np.cos(theta) 
    else:
        # get Zn(rho) for radial dependence and derived functions
        if np.isinf(r0):
            # for far-field radiation profile
            dn1Z1=0 # [L x 1]
            icn1Z0=cn1 # [L x nNmax]
            dn1Z2=dn1 # [L x nNmax]
            mun=mun*((-1j)**(n+1)) # 1 x nNmax
        else:
            rho=(2*np.pi* np.sqrt(epsilon)/Lambda*r0)[:,:,None] # column [L x 1]
            f=special.spherical_jn(nm1,rho) # [L x nNmax+1]
            
            if sBessel=='h1':
                f=f+1j*special.spherical_yn(nm1,rho) # [L x nNmax+1]
            
            stZnAll_Z0=f[:,1:,:] # [L x nNmax]
            stZnAll_Z1=stZnAll_Z0/rho # [L x nNmax]
            stZnAll_Z2=f[:,:-1,:] - nm1[:,1:,:]*stZnAll_Z1 # [L x nNmax]
        
            dn1Z1=dn1*stZnAll_Z1 # [L x nNmax]
            icn1Z0=1j*cn1*stZnAll_Z0 # [L x nNmax]
            dn1Z2=dn1*stZnAll_Z2 # [L x nNmax]
        # pin   1 x T x N
#        vecNdep=dn1Z1*cffnr  # [L x nNmax x 1]
#        Ersum=np.matmul(pin,vecNdep) 
        vecNdep=(dn1Z1*cffnr).swapaxes(1,2)  # [L x 1 x nNmax]
        Ersum=sum_conv(pin*vecNdep,2,settings) 
        
#        vecNdep=icn1Z0*mun # [L x nNmax]
#        vecNdep2=dn1Z2*mun # [L x nNmax]
        vecNdep=(icn1Z0*mun).swapaxes(1,2)  # [L x 1 x nNmax]
        vecNdep2=(dn1Z2*mun).swapaxes(1,2)  # [L x 1 x nNmax]
        
#        tmp1=np.matmul(pin, vecNdep)
#        tmp2=np.matmul(taun, vecNdep2)
        tmp1=sum_conv(pin*vecNdep,2,settings) 
        tmp2=sum_conv(taun*vecNdep2,2,settings)
        Etsum=tmp1+tmp2
        
#        tmp1=np.matmul(taun, vecNdep)
#        tmp2=np.matmul(pin, vecNdep2)
        tmp1=sum_conv(pin*vecNdep2,2,settings) 
        tmp2=sum_conv(taun*vecNdep,2,settings)
        Efsum=tmp1+tmp2
        
        Ecr=-2*np.sin(theta)*Ersum
        Ect=-2*Etsum # corresponds to S_2 if r0==Inf
        Esf=2*Efsum # corresponds to (-S_1) if r0==Inf
    
    return (np.swapaxes(Ecr,1,2),np.swapaxes(Ect,1,2),np.swapaxes(Esf,1,2)) # Lx1xT
