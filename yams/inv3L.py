import numpy as np
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
	M=np.stack(( np.stack((A,D,G),axis=3),np.stack((B,E,H),axis=3),np.stack([C,F,I]),axis=3),axis=2)
	return (M,mdet[:,:,None,None])
	
