import numpy as np
def pin_taun(nNmax,nNbtheta=180):

	theta=np.linspace(0,np.pi,nNbtheta)[None,:,None]
	mu=np.cos(theta)
	pinm1=np.zeros([1,nNbtheta,nNmax+1])
	pinm1[:,:,1]=np.ones([1,nNbtheta])
	# Get pi_2 to pi_nNmax by recurrence (see SPlaC guide)
	# pi_n is pinm1(:,n+1)
	for n in range(2,nNmax+1):
		pinm1[:,:,n]=(2*n-1)/(n-1)*mu[:,:,0]*pinm1[:,:,n-1]-n/(n-1)*pinm1[:,:,n-2]
	# return pi_n matrix (except n=0)
	pin=pinm1[:,:,1:] # 1 x T x N
	# return tau_n matrix
	nmat=np.arange(1,nNmax+1)[None,None,:]
	taun=nmat*mu*pin - (nmat+1)*pinm1[:,:,:-1]
	
	bn1mat=1j**(np.swapaxes(nmat,1,2)+1)*np.sqrt(np.pi*(2*n+1))
	return (pin,taun,bn1mat)
