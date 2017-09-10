import numpy as np
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
	
