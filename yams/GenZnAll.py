def GenZnAll(nNmax,rho,sBessel):

	nm1=np.arange(0,nNmax+1)[None,:]
	f=special.spherical_jn(nm1,rho)
	
	if sBessel=='h1':
		f=f+1j*special.spherical_yn(nm1,rho)
	
	stZnAll_Z0=f[:,1:]
	stZnAll_Z1=stZnAll_Z0/rho
	stZnAll_Z2=f[:,:-1] - nm1[:,1:]*stZnAll_Z1
	
	return (stZnAll_Z0,stZnAll_Z1,stZnAll_Z2)

