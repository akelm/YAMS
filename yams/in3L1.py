import numpy as np
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
