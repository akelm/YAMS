import numpy as np
import GenRBall
import scipy.io as sio

def int_wszystko(Ca, Cepsilon, dd, dip_pos ,kL, Lambda, RBx,RBz,xk,zk,ME,MM,TE,TM):
    
    
    # dd - warstwa z dipolem
    nK=len(Ca)
    kd=2*np.pi/Lambda*np.sqrt(Cepsilon[dd]) # L  x 1
    xp=kd*dip_pos
    nNmax=ME[0].shape[1]
    RBd=GenRBall.GenRBall(nNmax,xp)
    xp2inv=1/(xp.conj()*xp) # L x 1
    n=np.arange(1,nNmax+1)[:,None] # Nx1
    cc3 = (2*n+1) # 
    cc4 = cc3 *(n+1)*n # 
    st=3/2 * kd*kd.conj()/np.sqrt(np.absolute(Cepsilon[-1]))

    
    # fields expressed as
    ######### total emitted energy, both inwards and outwards
    
    # inwards energy flow
    # fields above dipole position should be expressed as a function 
    # of the field in the core see eq. 53
    a_el=wsp(-TE[dd][:,:,1::-1,0],ME[dd][:,:,0:2,1],[RBd[2],RBd[0]])
    Da_el=wsp(-TE[dd][:,:,1::-1,0],ME[dd][:,:,0:2,1],[RBd[3],RBd[1]])
    a_ml=wsp(-TM[dd][:,:,1::-1,0],ME[dd][:,:,0:2,1],[RBd[2],RBd[0]])

    if dd>0: # there is a layer beneeth the dipole
        # sprawdzam, czy warstwa ponizej dipola nie jest zlotem...
        if type(kL[dd-1]==np.ndarray): # integration is on the dipole inner layer
            # below dipole there is gold
            wspEx=[TE[dd][:,:,0,0],TE[dd][:,:,1,0]]
            wspMx=[TM[dd][:,:,0,0],TM[dd][:,:,1,0]]

            (zperp,zpara)=st*em_int(wspEx,wspMx,kd,RBx[dd-1],xp2inv,a_el,a_ml, Da_el,cc4,cc3,Cepsilon[dd])
        else: # integration is outside the dipole layer, no gold, only poverty
            kz=zk[dd-1]/Ca[dd-1]
            wspEz=[TE[dd-1][:,:,0,0],TE[dd-1][:,:,1,0]]
            wspMz=[TM[dd-1][:,:,0,0],TM[dd-1][:,:,1,0]]

            (zperp,zpara)=st*em_int(wspEz,wspMz,kz,RBz[dd-1],xp2inv,a_el,a_ml, Da_el,cc4,cc3,Cepsilon[dd-1])
    else: # integrate 2 nm beneeth dipole, if necessary
        if (dip_pos>=5 and np.sum(np.abs(a.imag))>0):
            # create artificial layer 2 nm beneeth the dipole
            x=kd*(dip_pos-2)
            RB=GenRBall.GenRBall(nNmax,x)
            wspEx=[TE[dd][:,:,0,0],TE[dd][:,:,1,0]]
            wspMx=[TM[dd][:,:,0,0],TM[dd][:,:,1,0]]
            
            (zperp,zpara)=st*em_int(wspEx,wspMx,kd,RB,xp2inv,a_el,a_ml, Da_el,cc4,cc3,Cepsilon[dd])
        else: # dipole is in the center or almost in the center
            (zperp,zpara)=(0,0)
        
    # general solution for radiative decay rates, moroz2005, eq. 69, eq. 126
    d_el=wsp(ME[dd][:,:,1::-1,1],TE[dd][:,:,0:2,0],[RBd[2],RBd[0]])
    Dd_el=wsp(ME[dd][:,:,1::-1,1],TE[dd][:,:,0:2,0],[RBd[3],RBd[1]])
    d_ml=wsp(MM[dd][:,:,1::-1,1],TM[dd][:,:,0:2,0],[RBd[2],RBd[0]])

    MRadPerp = (3/2*(np.absolute(Cepsilon[dd])/Cepsilon[-1])\
    *xp2inv**2 * np.matmul(d_el,cc4)).real # [L x 1]
    
    MRadPara =(3/4*(np.absolute(Cepsilon[dd])/Cepsilon[-1])\
    *xp2inv * np.matmul(d_ml+Dd_el,cc3)).real # [L x 1]
    
    # power radiated outwards from the dipole layer 
    # fields above dipole position should be expressed as a function of outer field
    # see eq. 54
    if dd<nK: # there is outer layer

        # sprawdzam, czy warstwa powyzej dipola nie jest zlotem...
        if type(kL[dd+1]==np.ndarray): # outer layer is gold, which means
            # it is reasonable to integrate power on the dipole side
            wspEz=[ME[dd][:,:,0,1],ME[dd][:,:,1,1]]
            wspMz=[MM[dd][:,:,0,1],MM[dd][:,:,1,1]]
            
            (xperp,xpara)=-st*em_int(wspEz,wspMz,kd,RBz[dd],xp2inv,d_el,d_ml,Dd_el,cc4,cc3,Cepsilon[dd])
        else: # not gold that is nonlocal, so the energy flow is calculated
            # outside the dipole layer
            kx=xk[dd]/Ca[dd]
            wspEx=[ME[dd+1][:,:,0,1],ME[dd+1][:,:,1,1]]
            wspMx=[MM[dd+1][:,:,0,1],MM[dd+1][:,:,1,1]]
            
            (xperp,xpara)=-st*em_int(wspEx,wspMx,kx,RBx[dd],xp2inv,d_el,d_ml,Dd_el,cc4,cc3,Cepsilon[dd+1])
    else: # dipole outside any layer, outer radiated power is radiation,
        # as the medium is non absorptive
        xperp=MRadPerp
        xpara=MRadPara
    
#    matlab_dict={'zperp':zperp,'zpara':zpara,'xperp':xperp,'xpara':xpara}
#    sio.savemat('test.mat',matlab_dict)
    
    MTotPerp=np.real(zperp+xperp)
    MNRPerp=MTotPerp-MRadPerp
    MTotPara=np.real(zpara+xpara)
    MNRPara=MTotPara-MRadPara
    
    
    return (MRadPerp, MRadPara,MNRPerp,MNRPara,MTotPerp,MTotPara)  
 
def em_int(wspE,wspM,k,RB,xp2inv,d_el,d_m,Dd_el,cc4,cc3,Cepsilon):
    fi_el=(wspE[0]*RB[2] + wspE[1]*RB[0])/k #
    Dfi_el=(wspE[0]*RB[3] + wspE[1]*RB[1])/k
    fi_m=(wspM[0]*RB[2] + wspM[1]*RB[0])/k
    Dfi_m=(wspM[0]*RB[3] + wspM[1]*RB[1])/k
    int_perp = xp2inv**2* np.matmul(np.nan_to_num(-Dfi_el*fi_el.conj()*d_el),cc4)
    int_para = xp2inv*np.matmul(np.nan_to_num(-Dfi_el*fi_el.conj()*Dd_el+fi_m*Dfi_m.conj()*d_m),cc3)
    perp = -(1j*np.sqrt(Cepsilon.conj())*int_perp).real
    para = -0.5*(1j*np.sqrt(Cepsilon.conj())*int_para).real
    return (perp,para)

def wsp(M,T,RB):
    T=list(np.rollaxis(T,2,0))
    M=list(np.rollaxis(M,2,0))
    w= (T[0]*RB[0]+T[1]*RB[1])/(T[0]*M[0]-T[1]*M[1])
    return np.nan_to_num(w.conj()*w)
