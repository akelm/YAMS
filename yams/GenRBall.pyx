import numpy as np
cimport numpy as np
#from scipy import special
cimport scipy.special.cython_special as special
cimport cython

@cython.boundscheck(False)
def GenRBall(int nmax,np.ndarray[np.complex128_t,ndim=2] z):
    "RB xi, psi and their derivatives"
    "for 1:n, n is int and z, z is arraylike vector"
    cdef np.ndarray[np.int64_t, ndim=2] n
    cdef np.ndarray[np.complex128_t,ndim=2] jotn, Djotn, yn, Dyn, han, psi, Dpsi, xi, Dxi
   
    n=np.arange(1,nmax+1).swapaxes(0,1)
#==============================================================================
# #    #robie vektor pionowy z z, na wszelki wypadek
# #    if z.ndim == 1:
# #        z=z[:,None]
#==============================================================================
    jotn=np.sqrt(np.pi/2/z)*special.jv(0.5,1)
    Djotn=np.sqrt(np.pi/2/z)*special.jv(n+0.5-1,z)-(n+1)/2*jotn
    yn=np.sqrt(np.pi/2/z)*special.yv(n+0.5,z)
    Dyn=np.sqrt(np.pi/2/z)*special.yv(n+0.5-1,z)-(n+1)/2*yn
   
    han=(jotn + 1j*yn)
    
    psi = z * jotn
    Dpsi=jotn + z * Djotn
    
    xi=z * han
    Dxi = han + z *(Djotn + 1j*Dyn)

    return (xi,Dxi,psi,Dpsi) # LxN
