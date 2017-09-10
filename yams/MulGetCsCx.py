import numpy as np

def MulGetCsCx(Lambda,Ca,Cepsilon):
	# Cepsilon L x nK, list of Lx1 array
	# Ca nK x 1 list of float
	# Lambda L x 1, array
	Ca=np.asarray(Ca)
	Cepsilon=np.concatenate(Cepsilon,1)
	nK=Ca.size
	Range = np.arange(nK) # 0..nK-1
	
	Cs=sqrt(Cepsilon[:,Range])/sqrt(Cepsilon[:,Range+1] # L x nK
	Cx = 2*np.pi* sqrt(Cepsilon[:,Range+1]) * np.asarray(Ca) / Lambda; # L x nK
	return ( np.hsplit(Cx,nK),np.hsplit(Cs,nK) )
