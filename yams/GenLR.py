import numpy as np
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
	L=np.zeros([RBz[0].size[0],RBz[0].size[1],6,6) # LxNmx6x6
	PL=L.copy()
	PP=L.copy()
	L2=L.copy()
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
	L[:,:,1,2]=-1j*Ca[0]*1/(xkl1**2)*cc)*RBl1[0]
	L[:,:,2,1]= 1j*( -RBl1[3]*1/xkl1+RBl1[2]*1/(xkl1**2) )
	L[:,:,2,2]= 1j*( -RBl1[1]*1/xkl1+RBl1[0]*1/(xkl1**2) )
	
	L[:,:,3,5]=Lambda/(2*np.pi)*RBz[2]
	L[:,:,3,0]=Lambda/(2*np.pi)*RBz[0]
	L[:,:,4,5]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBz[3]
	L[:,:,4,0]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBz[1]

	L[:,:,4,1]=-1j*Ca[1]* (1/(xkl**2)*cc) *RBl[2]
	L[:,:,4,2]=-1j*Ca[1]* (1/(xkl**2)*cc) *RBl[0]
	L[:,:,5,1]= 1j*( -RBl[3],1/xkl+RBl[2]*1/(xkl**2) )
	L[:,:,5,2]= 1j*( -RBl[1]*1/xkl)+RBl[0]*1/(xkl**2) )
	
	# wsp nielokalna
	
	PL[:,:,range(6),range(6)]=1
	PL[:,:,2,0]=1/(xk1**2)*cc*2*np.pi/Lambda
	PL[:,:,5,3]=1/(xk**2)*cc*2*np.pi/Lambda
	
	PP[:,:,range(6),range(-1,5))]=1
	
	# macierz do przemnozenia

	# granica zewnetrzna, wsp lokalne
	L2[:,:,3,0]=Lambda/(2*np.pi)*Xpsi
	L2[:,:,3,1]=Lambda/(2*np.pi)*Xxi
	L2[:,:,4,0]=Lambda/(2*np.pi*sqrt(Cepsilon[2]))*XDpsi
	L2[:,:,4,1]=Lambda/(2*np.pi*sqrt(Cepsilon[2]))*XDxi
	L2[:,:,5,0]= (1/xk_1**2*cc)*Xpsi
	L2[:,:,5,1]= (1/xk_1**2*cc)*Xxi
	
	# L2=GenLLprzem(Lambda,Cepsilon[kk+1].[:,None],RBx,xk)
	L3=np.matmul(PL,L2)
	(Linv,Ldet)=inw.inv6L(L)
	L4=np.matmul(Linv,L3)/Ldet
	# L4=cellpinv_multi(L,L3)
	L5=np.matmul(PP,L4)
	return(L5)

def inv6L(macierz):
		
	K= macierz[:,:,0:3,0:3]
	L= macierz[:,:,0:3,3:6]
	M= macierz[:,:,3:6,0:3]
	N= macierz[:,:,3:6,3:6]
	macierzinv=zeros[:,:,6,6]

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
	macierzinv[:,:,0:3,0:3]=(Kinv*(s4det*eye(3,3)+L*s4inv*Kinv))/kdet*stos

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
	return (M,mdet[:,:,None,None])
	
def inv3L1(macierz):
	A= macierz[:,:,1,1]*macierz[:,:,2,2]-macierz[:,:,1,2]*macierz[:,:,2,1]
	B=-(macierz[:,:,1,0]*macierz[:,:,2,2]-macierz[:,:,1,2]*macierz[:,:,2,0])
	C= macierz[:,:,1,0]*macierz[:,:,2,1]-macierz[:,:,1,1]*macierz[:,:,2,0]
	D= np.zeros(macierz.shape[0],macierz.shape[1])
	E= macierz[:,:,0,0]*macierz[:,:,2,2]-macierz[:,:,0,2]*macierz[:,:,2,0]
	F= -(macierz[:,:,0,0]*macierz[:,:,2,1]-macierz[:,:,0,1]*macierz[:,:,2,0])
	G= D
	H= -(macierz[:,:,0,0]*macierz[:,:,1,2]-macierz[:,:,0,2]*macierz[:,:,1,0])
	I= macierz[:,:,0,0]*macierz[:,:,1,1]-macierz[:,:,0,1]*macierz[:,:,1,0]
	mdet= macierz[:,:,0,0]*A
	M=np.stack( (np.stack((A, D, G),axis=3),np.stack((B, E, H),axis=3),np.stack((C, F, I),axis=3)),axis=2)
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
	M=np.stack((np.stack((A, D, G),axis=3),np.stack((B, E, H),axis=3),np.stack((C, F, I),axis=3)),axis=2)
	return (M,mdet[:,:,None,None])

