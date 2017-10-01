import numpy as np
from sum_conv import sum_conv
def extcoeff_M(x,ME,MM,settings):
    # ME,MM : ME[0],MM[0]
    # x : x[nK]
    nNmax=ME.shape[1]
    n=np.arange(1,nNmax+1)[None,:] # 1 x N
    cc1 = 2*n+1 # 1 x N
    x2inv=1/x**2 # L x 1
    # print(x2inv.shape)
    # scattering efficiency
    tmp1=np.absolute(-ME[:,:,1,0]/ME[:,:,1,1])**2
    tmp2=np.absolute(-MM[:,:,1,0]/MM[:,:,1,1])**2
    tmpMat= tmp1+tmp2 # [L x nNmax]
    Qsca = 2* x2inv* sum_conv( tmpMat*cc1,1,settings) # [L x 1]
       # extinction efficiency
    tmp1=np.real(-ME[:,:,1,0]/ME[:,:,1,1])
    tmp2=np.real(-MM[:,:,1,0]/MM[:,:,1,1])
    tmpMat= tmp1+tmp2 # [L x nNmax]
    Qext = -2* x2inv* sum_conv(tmpMat*cc1,1,settings) # [L x 1]
    # absorption efficiency
    Qabs = Qext - Qsca
    # print(Qext.shape)
    return (np.real(Qext),np.real(Qsca),np.real(Qabs))

def extcoeff_T(x,TE,TM,settings):
    # ME,MM : ME[0],MM[0]
    # x : x[nK]
    nNmax=TE.shape[1]
    n=np.arange(1,nNmax+1)[None,:]
    cc1 = 2*n+1
    x2inv=1/x**2
    
    BE = TE[:,:,1,0]/TE[:,:,0,0];
    BM = TM[:,:,1,0]/TM[:,:,0,0];
    
    # scattering efficiency
    tmpMat= np.abs(BE)**2 + np.abs(BM)**2 # [L x nNmax]
    Qsca = 2* x2inv* sum_conv(tmpMat*cc1,1,settings) # [L x 1]
    
    # extinction efficiency
    tmpMat= np.real(BE)+np.real(BM) # [L x nNmax]
    Qext = -2* x2inv* sum_conv(tmpMat*cc1,1,settings) # [L x 1]
    
    # absorption efficiency
    Qabs = Qext - Qsca
    return (np.real(Qext),np.real(Qsca),np.real(Qabs))

