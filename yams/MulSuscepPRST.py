import GenRBall
import numpy as np
from sizecor_nanoshell import *

from scipy import constants
# zmiana konwencji - wszystko iterowane po interfejsach/warstwach jest listą
def MulSuscepPRST(nNmax,Ca,Lambda,nielokalne,sizecorr,tempcorr,Cepsilon,layers,temp,mat_sizecor_dict):
    # function [Cst,Cepsilon,kL,ext_coeffM,ext_coeffT]=MulSuscepPRST(nNmax,Ca,Lambda,warNL,Cepsilon,T)
        # nMax - max number of bessel function expansion
        # Ca list with interface radii
        # Lambda Lx1x1x1 array, wavelength
        # nielokalne nKx1 list, nonlocality
        # Cepsilon nKx1 list of Lx1 arrays, refractive indices
        # temperatura - float or None
    nK=len(Ca)
    
    nNLambda=Lambda.shape[0]
    
    kL=np.split(np.zeros([nNLambda,nK+1],dtype=complex),nK+1,1)
    
    tmp=np.zeros([nNLambda,nNmax,4,4],dtype=complex)
    tmp[:,:,range(4),range(4)]=1
    ME=[tmp.copy() for n in range(nK+1)]
    TE=ME.copy()
    MM=[tmp[:,:,0:2,0:2].copy() for n in range(nK+1)]
    TM=MM.copy()
    # MM rozmiar LxNx2x2

    RBx=[]
    RBz=[]
    RBl=[]
    xk=[]
    zk=[]
    xkl=[]

         
    # indeksy granic po ktorych trzeba bedzie iterowac
    # podwojne dla warstw nielokalnych
    lokalne=np.setdiff1d(range(nK),nielokalne)[::-1]
    l_iter=[ np.array([item+1,item]) if (item+1 in nielokalne) \
                   else np.array([item]) for item in lokalne]
    if 0 in nielokalne: l_iter.append(np.array([0,0]))
    
    # layers for which sizecor_nanoshell has to be run
    indeksy=set([*nielokalne,*sizecorr,*tempcorr]) 
    for k in indeksy:
        (Cepsilon[k],kL[k])=sizecor_nanoshell(Cepsilon[k],Lambda,\
         bool(k in sizecorr),bool(k in nielokalne),Ca[k],Ca[k-1] if k>0 else 0,\
         temp,mat_sizecor_dict[layers[k]])
#         bool(k in sizecorr),bool(k in nielokalne),Ca[k],Ca[k-1] if k>0 else 0,298)


    Ll=len(l_iter)
    for nn in range(Ll):
        # print('nn=')
        # print(nn)
        kk=l_iter[nn][0]
        #     ['minus ', num2str(kk)]
        sk=np.sqrt(Cepsilon[kk]/Cepsilon[kk+1])
        xk.insert(0,2*np.pi*np.sqrt(Cepsilon[kk+1])*Ca[kk]/Lambda) # [L x 1] zew
        zk.insert(0,sk*xk[0]) # [L x 1] wew
        RBz.insert(0,GenRBall.GenRBall(nNmax,zk[0])) # L x N
        RBx.insert(0,GenRBall.GenRBall(nNmax,xk[0]))
        # np.savetxt('results/RBX_0.txt', RBx[0], fmt='%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj', delimiter='\t', newline='\n')
        
        if l_iter[nn].size==2:
            xkl.insert(0,(Ca[kk]*kL[kk]))
            # print('tutaj')
            #print(xkl[0][2])
            RBl.insert(0,GenRBall.GenRBall(nNmax,xkl[0],bigz=False,dps=50))
            # print(RBl[0][0][2,3])
            if l_iter[nn][0]!=0: # nie jest rdzeniem
                # dodatkowe wsp stojace przy polach dla warstw lokalnych
                sk1=np.sqrt(Cepsilon[kk-1]/Cepsilon[kk])
                xk.insert(0,2*np.pi* np.sqrt(Cepsilon[kk])*Ca[kk-1]/Lambda)
                zk.insert(0,sk1*xk[0]) # [L x 1] wew
                RBz.insert(0,GenRBall.GenRBall(nNmax,zk[0])) # L x N
                RBx.insert(0,GenRBall.GenRBall(nNmax,xk[0]))

                # wsp dla warstw nielokalnych 
                # granica wewnetrzna
                xkl.insert(0,Ca[kk-1]*kL[kk])
                RBl.insert(0,GenRBall.GenRBall(nNmax,xkl[0],bigz=False))
 
                L5minus=GenLL(Lambda,list(map(Cepsilon.__getitem__,[kk-1,kk,kk+1])),
                                     list(map(Ca.__getitem__,[kk-1,kk])),
                RBz[0],RBx[0],RBl[0],RBz[1],RBl[1],RBx[1],xk[0],zk[0],xkl[0],xkl[1],xk[1],xk[1])
                TEminus=L5minus[:,:,0:4,0:4].copy()
                TMminus=Tmminus(RBx[1],RBz[1],sk)

                L5plus=GenLL(Lambda,list(map(Cepsilon.__getitem__,[kk+1,kk,kk-1])),
                                    list(map(Ca.__getitem__,[kk,kk-1])),
                RBx[1],RBz[1],RBl[1],RBx[0],RBl[0],RBz[0],zk[1],xk[1],xkl[1],xkl[0],xk[0],zk[0])
                TEplus=L5plus[:,:,0:4,0:4].copy()
                TMplus=Tmplus(RBx[1],RBz[1],sk)
                
                ME[kk]=np.matmul(TEminus,ME[kk+1])
                MM[kk]=np.matmul(TMminus,MM[kk+1])

                for x in range(nK,kk,-1):
                    TM[x]=np.matmul(TM[x], TMplus )

                # przez 2 warstwy
                TEminus2=np.zeros([nNLambda,nNmax,4,4],dtype=complex)
                TEminus2[:,:,2:4,2:4]=1    
                TEplus2=TEminus2.copy()

                TEminus2[:,:,0:2,0:2]=L5minus[:,:,4:6,0:2].copy()
                TEplus2[:,:,0:2,0:2]=L5plus[:,:,4:6,0:2].copy()

                ME[kk-1]=np.matmul(TEminus2,ME[kk+1])

                for x in range(nK,kk,-1):
                    TE[x]=np.matmul(TE[x], TEplus2)


                ## kolejna warstwa
                TMminus=Tmminus(RBx[0],RBz[0],sk1)
                TMplus=Tmplus(RBx[0],RBz[0],sk1)

                TEminus=np.matmul(TEminus,TEplus2)
                MM[kk-1]=np.matmul(TMminus,MM[kk]) 

                TEplus=np.matmul(TEminus2,TEplus)
                TE[kk]=np.matmul(TE[kk],TEplus)
                    
                for x in range(nK,kk-1,-1):
                    TM[x]=np.matmul(TM[x], TMplus)

                # kk=kk-1

            else: #             ['rdzen']
                (TEminus,TEplus)=GenLR(Lambda,Cepsilon[kk+1],Cepsilon[kk],Ca[kk],RBx[0],RBz[0],RBl[0],xk[0],xkl[0],zk[0])
                #print(RBl[0][0][2,3])
                #print(TEplus[2,3,1,1])
                #print(TEminus[2,3,0,1])
#                np.savetxt('results/TEminus.txt', TEminus[:,:,0,0], fmt='%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj', delimiter='\t', newline='\n')
                # nielokalnosc nie wplywa na mody magnetyczne
                TMminus=Tmminus(RBx[0],RBz[0],sk)
                TMplus=Tmplus(RBx[0],RBz[0],sk)
                ME[kk]=np.matmul(TEminus,ME[kk+1])
                MM[kk]=np.matmul(TMminus,MM[kk+1])
                
                for x in range(nK,kk,-1):
                    TE[x]=np.matmul(TE[x], TEplus )
                    TM[x]=np.matmul(TM[x], TMplus )
                

        else: #  ['lokalna granica ', num2str(kk)]
            xkl.insert(0,[])
            RBl.insert(0,[])
            TEminus=Teminus(RBx[0],RBz[0],sk)
            TMminus=Tmminus(RBx[0],RBz[0],sk)
            # np.savetxt('results/TMminus.txt', TMminus[:,:,0,0], fmt='%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj\t%.6f%+.6fj', delimiter='\t', newline='\n')
            TEplus=Teplus(RBx[0],RBz[0],sk) # LxNx4x4
            TMplus=Tmplus(RBx[0],RBz[0],sk)

            ME[kk]=np.matmul(TEminus,ME[kk+1])
            MM[kk]=np.matmul(TMminus,MM[kk+1])
            for x in range(nK,kk,-1):
                TE[x]=np.matmul(TE[x], TEplus )
                TM[x]=np.matmul(TM[x], TMplus )

    return (ME,MM,TE,TM,Cepsilon,kL,RBx,RBz,RBl,xk,zk,xkl)



def Tmplus(RBx,RBz,smat):
    TMplus=np.zeros([RBx[0].shape[0],RBx[0].shape[1],2,2],dtype=complex) # LxNmx2x2
    # Xxi RBx[0]
    # XDxi RBx[1]
    # Xpsi RBx[2]
    # XDpsi RBx[3]
    # Zxi RBz[0]
    # ZDxi RBz[1]
    # Zpsi RBz[2]
    # ZDpsi RBz[3]
    TMplus[:,:,0,0]=-1j*(RBx[1]*RBz[2]/smat - RBx[0]*RBz[3])
    TMplus[:,:,0,1]=-1j*(RBx[1]*RBz[0]/smat - RBx[0]*RBz[1])
    TMplus[:,:,1,0]=-1j*(-RBx[3]*RBz[2]/smat + RBx[2]*RBz[3])
    TMplus[:,:,1,1]=-1j*(-RBx[3]*RBz[0]/smat + RBx[2]*RBz[1])
    return TMplus
    
def Tmminus(RBx,RBz,smat):
    TMminus=np.zeros([RBx[0].shape[0],RBx[0].shape[1],2,2],dtype=complex) # LxNmx2x2
    TMminus[:,:,0,0]=-1j*(smat*RBz[1]*RBx[2] - RBz[0]*RBx[3])
    TMminus[:,:,0,1]=-1j*(smat*RBz[1]*RBx[0] - RBz[0]*RBx[1])
    TMminus[:,:,1,0]=-1j*(-smat*RBz[3]*RBx[2] + RBz[2]*RBx[3])
    TMminus[:,:,1,1]=-1j*(-smat*RBz[3]*RBx[0] + RBz[2]*RBx[1])
    return TMminus    

def Teplus(RBx,RBz,smat):
    TEplus=np.zeros([RBx[0].shape[0],RBx[0].shape[1],4,4],dtype=complex) # LxNmx4x4
    TEplus[:,:,range(4),range(4)]=1
    TEplus[:,:,0,0]=-1j*(RBx[1]*RBz[2] - RBx[0]*RBz[3]/smat)
    TEplus[:,:,0,1]=-1j*RBz[0]*(RBx[1] - (RBx[0]/RBz[0])*RBz[1]/smat)
    TEplus[:,:,1,0]=-1j*(-RBx[3]*RBz[2] + RBx[2]*RBz[3]/smat)
    TEplus[:,:,1,1]=-1j*(-RBx[3]*RBz[0] + RBx[2]*RBz[1]/smat)
    return TEplus
    
def Teminus(RBx,RBz,smat):
    TEminus=np.zeros([RBx[0].shape[0],RBx[0].shape[1],4,4],dtype=complex) # LxNmx4x4
    TEminus[:,:,range(4),range(4)]=1
    TEminus[:,:,0,0]=-1j*(RBz[1]*RBx[2] - RBz[0]*RBx[3]*smat)
    TEminus[:,:,0,1]=-1j*RBz[1]*(RBx[0] - RBz[0]*(RBx[1]/RBz[1])*smat)
    TEminus[:,:,1,0]=-1j*(-RBz[3]*RBx[2] + RBz[2]*RBx[3]*smat)
    TEminus[:,:,1,1]=-1j*(-RBz[3]*RBx[0] + RBz[2]*RBx[1]*smat)
    return TEminus    


def GenLR(Lambda,Cepsilon1,Cepsilon,Ca,RBx,RBz,RBl,xk,xkl,zk):
    TEminus=np.zeros([RBx[0].shape[0],RBx[0].shape[1],4,4],dtype=complex)
    TEminus[:,:,2:4,2:4]=1
    TEplus=TEminus.copy()
    L_zew=TEminus[:,:,0:3,0:3].copy()
    L_wew=L_zew.copy()
    P=L_zew.copy()
    P[:,:,range(3),range(3)]=1
    M1=L_zew[:,:,0:2,0:2].copy()
    cc=np.sqrt(  np.arange(1,RBx[0].shape[1]+1)*np.arange(2,RBx[0].shape[1]+2)   )
    
    M1[:,:,0,0]=Lambda/(2*np.pi)*RBx[2]
    M1[:,:,0,1]=Lambda/(2*np.pi)*RBx[0]
    M1[:,:,1,0]=Lambda/(2*np.pi*np.sqrt(Cepsilon1))*RBx[3]
    M1[:,:,1,1]=Lambda/(2*np.pi*np.sqrt(Cepsilon1))*RBx[1]
    
    L_wew[:,:,0,0]=Lambda/(2*np.pi)*RBz[2]
    L_wew[:,:,0,1]=Lambda/(2*np.pi)*RBz[0]
    L_wew[:,:,1,0]=Lambda/(2*np.pi*np.sqrt(Cepsilon))*RBz[3]
    L_wew[:,:,1,1]=Lambda/(2*np.pi*np.sqrt(Cepsilon))*RBz[1]

    L_wew[:,:,1,2]=-1j*Ca*(1/(xkl**2)*cc)*RBl[2]
    L_wew[:,:,2,2]= -1j*( RBl[3]*1/xkl-RBl[2]*1/(xkl**2) )

    # minus
    L_zew_m=L_zew.copy()
    L_zew_m[:,:,2,0]= 1/(xk**2)*cc*RBx[2]
    L_zew_m[:,:,2,1]= 1/(xk**2)*cc*RBx[0]
    L_zew_m[:,:,0:2,0:2]=M1
    P_m=P.copy()
    P_m[:,:,2,0]=-1/(zk**2)*cc*2*np.pi/Lambda
    # print(P_m[0,0,:,:])
    L_zew1=np.matmul(P_m,L_zew_m)
    #print(L_zew1)
    (L_wewinv,L_wewdet)=inv3L(L_wew)
    TEminus[:,:,0:3,0:3]=np.matmul(L_wewinv,L_zew1)/L_wewdet    
        
    # plus
    (M1[:,:,0,0],M1[:,:,1,1])=(M1[:,:,1,1].copy(),M1[:,:,0,0].copy())
    Mobr=1j*np.sqrt(Cepsilon1)[:,:,None,None]*((2*np.eye(2,dtype=complex)-np.ones([2,2],dtype=complex))[None,None,:,:])
    M1=Mobr*M1
    L_wew[:,:,2,0]= 1/(zk**2)*cc*RBz[2]
    L_wew[:,:,2,1]= 1/(zk**2)*cc*RBz[0]
    L_zew[:,:,0:2,0:2]=M1
    P[:,:,2,0]=-1/(xk**2)*cc*2*np.pi/Lambda
    L_zew1=np.matmul(L_zew,P)
    TEplus[:,:,0:3,0:3]=np.matmul(L_zew1,L_wew)    
        
    return (TEminus,TEplus)

def GenLL(Lambda,Cepsilon,Ca,RBz1,RBx1,RBl1,RBz,RBl,RBx,xk1,zk1,xkl1,xkl,xk,xk_1):
    # Ca1 to Ca[kk-1]
    # Ca to Ca[kk]
    L=np.zeros([RBz[0].shape[0],RBz[0].shape[1],6,6],dtype=complex) # LxNmx6x6
    PL=L.copy()
    PP=L.copy()
    L2=L.copy()
    cc=np.sqrt(  np.arange(1,RBx[0].shape[1]+1)*np.arange(2,RBx[0].shape[1]+2)   )
    L[:,:,0,3]=-Lambda/(2*np.pi)*RBz1[2]
    L[:,:,0,4]=-Lambda/(2*np.pi)*RBz1[0]
    L[:,:,1,3]=-Lambda/(2*np.pi*np.sqrt(Cepsilon[0]))*RBz1[3]
    L[:,:,1,4]=-Lambda/(2*np.pi*np.sqrt(Cepsilon[0]))*RBz1[1]
    L[:,:,2,3]= (1/(xk1**2)-1/(zk1**2))*cc*RBz1[2]
    L[:,:,2,4]= (1/(xk1**2)-1/(zk1**2))*cc*RBz1[0]
    
    L[:,:,0,5]=Lambda/(2*np.pi)*RBx1[2]
    L[:,:,0,0]=Lambda/(2*np.pi)*RBx1[0]
    L[:,:,1,5]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBx1[3]
    L[:,:,1,0]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBx1[1]

    L[:,:,1,1]=-1j*Ca[0]*1/(xkl1**2)*cc*RBl1[2]
    L[:,:,1,2]=-1j*Ca[0]*1/(xkl1**2)*cc*RBl1[0]
    L[:,:,2,1]= 1j*( -RBl1[3]*1/xkl1+RBl1[2]*1/(xkl1**2) )
    L[:,:,2,2]= 1j*( -RBl1[1]*1/xkl1+RBl1[0]*1/(xkl1**2) )
    
    L[:,:,3,5]=Lambda/(2*np.pi)*RBz[2]
    L[:,:,3,0]=Lambda/(2*np.pi)*RBz[0]
    L[:,:,4,5]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBz[3]
    L[:,:,4,0]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBz[1]

    L[:,:,4,1]=-1j*Ca[1]* (1/(xkl**2)*cc) *RBl[2]
    L[:,:,4,2]=-1j*Ca[1]* (1/(xkl**2)*cc) *RBl[0]
    L[:,:,5,1]= 1j*( -RBl[3]*1/xkl+RBl[2]*1/(xkl**2) )
    L[:,:,5,2]= 1j*( -RBl[1]*1/xkl+RBl[0]*1/(xkl**2) )
    
    # wsp nielokalna
    
    PL[:,:,range(6),range(6)]=1
    PL[:,:,2,0]=1/(xk1**2)*cc*2*np.pi/Lambda
    PL[:,:,5,3]=1/(xk**2)*cc*2*np.pi/Lambda
    
    PP[:,:,range(6),range(-1,5)]=1
    
    # macierz do przemnozenia
    # xi, psi
    # granica zewnetrzna, wsp lokalne
    L2[:,:,3,0]=Lambda/(2*np.pi)*RBx[2]#Xpsi
    L2[:,:,3,1]=Lambda/(2*np.pi)*RBx[0]#Xxi
    L2[:,:,4,0]=Lambda/(2*np.pi*np.sqrt(Cepsilon[2]))*RBx[3]#XDpsi
    L2[:,:,4,1]=Lambda/(2*np.pi*np.sqrt(Cepsilon[2]))*RBx[1]#XDxi
    L2[:,:,5,0]= (1/xk_1**2*cc)*RBx[2]#Xpsi
    L2[:,:,5,1]= (1/xk_1**2*cc)*RBx[0]#Xxi
    
    # L2=GenLLprzem(Lambda,Cepsilon[kk+1].[:,None],RBx,xk)
    L3=np.matmul(PL,L2)
    (Linv,Ldet)=inv6L(L)
    L4=np.matmul(Linv,L3)/Ldet
    # L4=cellpinv_multi(L,L3)
    L5=np.matmul(PP,L4)
    return(L5)

def inv6L(macierz):
        
    K= macierz[:,:,0:3,0:3]
    L= macierz[:,:,0:3,3:6]
    M= macierz[:,:,3:6,0:3]
    N= macierz[:,:,3:6,3:6]
    macierzinv=np.zeros(macierz.shape).astype('complex128')

    (Kinv,kdet)=inv3L1(K)

    # kdet LxNm
    (Minv,mdet)=inv3L1(M)

    sM=Minv*N
    sK=Kinv*L

    s3=sK*mdet/kdet+sM
    (s3inv,s3det)=inv3(s3)
    macierzinv[:,:,3:6,3:6]=s3inv*Minv
    
    s4=sK+sM*kdet/mdet
    (s4inv,s4det)=inv3(s4)
    stos=s3det/s4det
    macierzinv[:,:,3:6,0:3]=(s4inv*Kinv)*stos

    macierzinv[:,:,0:3,3:6]=-(Kinv*L*s3inv*Minv)/(kdet)
    macierzinv[:,:,0:3,0:3]=(Kinv*(s4det*np.eye(3,3)+L*s4inv*Kinv))/kdet*stos

    return (macierzinv,s3det)
    
def inv3L(macierz):
    # macierz LxNx3x3
    stos=macierz[:,:,2,2]/macierz[:,:,1,2]
    A= macierz[:,:,1,1]*stos
    B=-macierz[:,:,1,0]*stos
    C= np.zeros(B.shape)
    D= -macierz[:,:,0,1]*stos
    E= macierz[:,:,0,0]*stos
    F= C;
    G= macierz[:,:,0,1]
    H= -macierz[:,:,0,0]
    I= (macierz[:,:,0,0]*macierz[:,:,1,1]-macierz[:,:,0,1]*macierz[:,:,1,0])/macierz[:,:,1,2]
    mdet= stos*(macierz[:,:,0,0]*macierz[:,:,1,1] -macierz[:,:,0,1]*macierz[:,:,1,0])
    # M=np.stack( [np.stack([A,D,G],axis=3),np.stack([B,E,H],axis=3),np.stack([C,F,I],axis=3)],axis=2)
    M=np.stack( [np.stack([A,B,C],axis=2),np.stack([D,E,F],axis=2),np.stack([G,H,I],axis=2)],axis=3)
    # znajduje mdet ktore sa 0 i zamieniam na jakas mala liczbe
    mdet[np.where(mdet==0)]=np.nextafter(0,1)
    return (M,mdet[:,:,None,None])
    
def inv3L1(macierz):
    A= macierz[:,:,1,1]*macierz[:,:,2,2]-macierz[:,:,1,2]*macierz[:,:,2,1]
    B=-(macierz[:,:,1,0]*macierz[:,:,2,2]-macierz[:,:,1,2]*macierz[:,:,2,0])
    C= macierz[:,:,1,0]*macierz[:,:,2,1]-macierz[:,:,1,1]*macierz[:,:,2,0]
    D= np.zeros(macierz.shape[0:2])
    E= macierz[:,:,0,0]*macierz[:,:,2,2]-macierz[:,:,0,2]*macierz[:,:,2,0]
    F= -(macierz[:,:,0,0]*macierz[:,:,2,1]-macierz[:,:,0,1]*macierz[:,:,2,0])
    G= D
    H= -(macierz[:,:,0,0]*macierz[:,:,1,2]-macierz[:,:,0,2]*macierz[:,:,1,0])
    I= macierz[:,:,0,0]*macierz[:,:,1,1]-macierz[:,:,0,1]*macierz[:,:,1,0]
    mdet= macierz[:,:,0,0]*A
    M=np.stack( [np.stack([A,B,C],axis=2),np.stack([D,E,F],axis=2),np.stack([G,H,I],axis=2)],axis=3)
    # znajduje mdet ktore sa 0 i zamieniam na jakas mala liczbe
    mdet[np.where(mdet==0)]=np.nextafter(0,1)
    return(M,mdet[:,:,None,None])
    
def inv3(macierz):
    # zwykla inversja
    A= macierz[:,:,1,1]*macierz[:,:,2,2]-macierz[:,:,1,2]*macierz[:,:,2,1]
    B=-(macierz[:,:,1,0]*macierz[:,:,2,2]-macierz[:,:,1,2]*macierz[:,:,2,0])
    C= macierz[:,:,1,0]*macierz[:,:,2,1]-macierz[:,:,1,1]*macierz[:,:,2,0]
    D= -(macierz[:,:,0,1]*macierz[:,:,2,2]-macierz[:,:,0,2]*macierz[:,:,2,1])
    E= macierz[:,:,0,0]*macierz[:,:,2,2]-macierz[:,:,0,2]*macierz[:,:,2,0]
    F= -(macierz[:,:,0,0]*macierz[:,:,2,1]-macierz[:,:,0,1]*macierz[:,:,2,0])
    G= macierz[:,:,0,1]*macierz[:,:,1,2]-macierz[:,:,0,2]*macierz[:,:,1,1]
    H= -(macierz[:,:,0,0]*macierz[:,:,1,2]-macierz[:,:,0,2]*macierz[:,:,1,0])
    I= macierz[:,:,0,0]*macierz[:,:,1,1]-macierz[:,:,0,1]*macierz[:,:,1,0]
    mdet= macierz[:,:,0,0]*A+macierz[:,:,0,1]*B+macierz[:,:,0,2]*C
    M=np.stack( [np.stack([A,B,C],axis=2),np.stack([D,E,F],axis=2),np.stack([G,H,I],axis=2)],axis=3)
    # znajduje mdet ktore sa 0 i zamieniam na jakas mala liczbe
    mdet[np.where(mdet==0)]=np.nextafter(0,1)
    return (M,mdet[:,:,None,None])

