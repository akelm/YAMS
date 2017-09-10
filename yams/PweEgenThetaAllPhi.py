import numpy as np
from scipy import special
def PweEgenThetaAllPhi(Lambda,epsilon,cn1,dn1,r0,theta,sBessel,pin,taun):
	nNmax=cn1.shape[1]
	
	nm1=np.arange(0,nNmax+1)[None,:,None]
	n=nm1[:,1:,:]

	cffnr=np.sqrt((2*n+1)/(4*np.pi)) 
	mun=cffnr/(n*(n+1))
	
	if r0==0:
		Esf= (dn1[:,0,:]/np.sqrt(3*np.pi))[:,None,None]
		Ecr=-Esf * np.sin(theta)
		Ect=-Esf * np.cos(theta) 
	else:
		# get Zn(rho) for radial dependence and derived functions
		if np.isinf(r0):
			# for far-field radiation profile
			dn1Z1=0 # [L x 1]
			icn1Z0=cn1 # [L x nNmax]
			dn1Z2=dn1 # [L x nNmax]
			mun=mun*((-1j)**(n+1))
		else:
			rho=(2*np.pi* np.sqrt(epsilon)/Lambda*r0)[:,:,None] # column [L x 1]
			f=special.spherical_jn(nm1,rho)
			
			if sBessel=='h1':
				f=f+1j*special.spherical_yn(nm1,rho)
			
			stZnAll_Z0=f[:,1:,:]
			stZnAll_Z1=stZnAll_Z0/rho
			stZnAll_Z2=f[:,:-1,:] - nm1[:,1:,:]*stZnAll_Z1
		
			dn1Z1=dn1*stZnAll_Z1 # [L x nNmax]
			icn1Z0=1j*cn1*stZnAll_Z0 # [L x nNmax]
			dn1Z2=dn1*stZnAll_Z2 # [L x nNmax]
		
		vecNdep=dn1Z1*cffnr
		Ersum=np.matmul(pin,vecNdep)
		
		vecNdep=icn1Z0*mun
		vecNdep2=dn1Z2*mun
		
		tmp1=np.matmul(pin, vecNdep)
		tmp2=np.matmul(taun, vecNdep2)
		Etsum=tmp1+tmp2
		
		tmp1=np.matmul(taun, vecNdep)
		tmp2=np.matmul(pin, vecNdep2)
		Efsum=tmp1+tmp2
		
		Ecr=-2*np.sin(theta)*Ersum
		Ect=-2*Etsum # corresponds to S_2 if r0==Inf
		Esf=2*Efsum # corresponds to (-S_1) if r0==Inf
	
	return (np.swapaxes(Ecr,1,2),np.swapaxes(Ect,1,2),np.swapaxes(Esf,1,2)) # Lx1xT
