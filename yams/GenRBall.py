import numpy as np
from scipy import special
#from mpmath import mp,fp
def GenRBall(nmax,z,bigz=False,dps=100):
	"RB xi, psi and their derivatives"
	"for 1:n, n is int and z, z is arraylike vector"

	#if bigz:
		#n=(np.arange(1.5,int(nmax)+1.5,1)).tolist()
		#nNlambda=z.shape[0]
		#z=z.reshape(nNlambda).tolist()
		#xi=np.zeros([nNlambda,nmax],dtype=complex)
		#Dxi=xi.copy()
		#psi=xi.copy()
		#Dpsi=xi.copy()
		
		#mp.dps=dps
		#Dh1_f = lambda nn,xx: mp.besselj(nn,xx,1) + 1j*mp.bessely(nn,xx,1)
		
		#xi_f = lambda nn,xx: fp.mpc(mp.sqrt(np.pi*xx/2)* mp.hankel1(nn,xx))
		#Dxi_f = lambda nn,xx: fp.mpc(mp.sqrt(np.pi*xx/2)* mp.fadd( mp.fdiv(mp.hankel1(nn,xx),2*xx) , Dh1_f(nn,xx) ))
		#psi_f = lambda nn,xx: fp.mpc(mp.sqrt(np.pi*xx/2)* mp.besselj(nn,xx))
		#Dpsi_f = lambda nn,xx: fp.mpc(mp.sqrt(np.pi*xx/2)* mp.fadd( mp.fdiv(mp.besselj(nn,xx),2*xx) , mp.besselj(nn,xx,1) ))
		
		#for (n1,z1) in [(n1,z1) for n1 in range(nmax) for z1 in range(nNlambda)]:
			#xi[z1,n1] = xi_f(n[n1],z[z1])
			#Dxi[z1,n1] = Dxi_f(n[n1],z[z1])
			#psi[z1,n1] = psi_f(n[n1],z[z1])
			#Dpsi[z1,n1] = Dpsi_f(n[n1],z[z1])
	#else:
	n=np.arange(1,int(nmax)+1)[None,:]
	#robie vektor pionowy z z, na wszelki wypadek
	if z.ndim == 1:
		z=z[:,None]
	jotn=special.spherical_jn(n, z, 0)
	Djotn=special.spherical_jn(n, z, 1)
	han=(jotn + 1j*special.spherical_yn(n, z, 0))
	
	psi = z * jotn
	Dpsi=jotn + z * Djotn
	
	xi=z * han
	Dxi = han + z *(Djotn + 1j*special.spherical_yn(n, z, 1))

	return (xi,Dxi,psi,Dpsi) # LxN
