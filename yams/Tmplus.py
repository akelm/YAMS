import numpy as np
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
