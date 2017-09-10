import numpy as np
from scipy import special

def psi_xi_der(nmax,z):
   "RB xi, psi and their derivatives"
   "for 1:n, n is int and z, z is arraylike vector"
   n=np.tile(np.arange(1,int(nmax)+1),(np.size(z),1))
   "tu zrobic repmat n i repmat z"
   z1=np.tile(z, (nmax, 1))
   jotn=special.spherical_jn(n, z1.T, 0)
   Djotn=special.spherical_jn(n, z1.T, 1)
   han=(jotn + 1j*special.spherical_yn(n, z1.T, 0))
   
   psi = z1.T * jotn
   Dpsi=jotn + z1.T * Djotn
   
   xi=z1.T * han
   Dxi = han + z1.T*(Djotn + 1j*special.spherical_yn(n, z1.T, 1))
   
   return (psi,Dpsi,xi,Dxi)
