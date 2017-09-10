import numpy as np
from scipy import constants


def gamma_calc(T,omega,mat_sizecor_subdict):
    pi=constants.pi
    kB = constants.value("Boltzmann constant in eV/K") # Boltzmann constant
    h = constants.value("Planck constant over 2 pi in eV s")/constants.femto # eV * fs
    
    # electron-electron dumping constant
    gamma_ee = (pi**3*mat_sizecor_subdict['L']*mat_sizecor_subdict['D'])/\
    (12*h*mat_sizecor_subdict['EF'])*((kB*T)**2 + (omega*h/2/pi)**2 )
    # electron-phonon dumping constant
    arg = mat_sizecor_subdict['TD']/T
    x=np.linspace(0,arg,400)
    dx=x[1]-x[0]
    x=x[1:]-0.5*dx
    cz = 2/5+4/(arg)**5* np.sum( x**4/(np.exp(x)-1) ) *np.absolute(dx)
    gamma_eph = 1/30*cz
    # total gamma
    gamma = gamma_ee + gamma_eph
    return gamma_ee,gamma_eph,gamma

def sizecor_nanoshell(eps,Lambda,ifsizecor,ifnonlocal,r1,r2,T,mat_sizecor_dict):
    # constants
    h = constants.value("Planck constant over 2 pi in eV s")/constants.femto # eV * fs
    c = constants.value("speed of light in vacuum")*constants.femto/constants.nano # nm / fs
    omega=2*constants.pi*c/Lambda
    
#    # loading material data
#    mat=np.genfromtxt('mat_sizecor.txt', \
#        dtype='float', usecols=range(1,8),\
#        delimiter='\t', skip_header=1, filling_values=' ').tolist()
#    mat1=np.genfromtxt('mat_sizecor.txt', \
#        dtype='U15', usecols=0,\
#        delimiter='\t', skip_header=1, filling_values=' ').tolist()
#    if type(mat1)==str:
#        mat1=[mat1]
#        mat=[mat]
#    mat_sizecor=dict(zip(mat1,mat)) # files
#    # obj rozszrzalnosc zlota Kittel 2005
#    (omegap, vF, TD, EF, L, D, Beta)=mat_sizecor[material]
    
    list_subdict=['L','D','EF','TD']
    mat_sizecor_subdict=dict(zip(list_subdict,list(map(mat_sizecor_dict.__getitem__,list_subdict))))
    # units of angular frequency
    omegap=mat_sizecor_dict['omegap']/h;

    # poprawka stad: J. Phys. Chem. C 2008, 112, 10641–10652
    
    # drude damping constants
    (gamma_ee298,gamma_eph298,gamma)=gamma_calc(298,omega,mat_sizecor_subdict)
    
    # drude part of dielectric function
    eps_drude = 1 - omegap**2/(omega*(omega+1j*gamma))
    # interband transistion in the dielectric function
    eps_ib = eps - eps_drude
    
    ### temperature correction
    # to z temp jest wziete z:
    # liu 2009
    # konrad2013
    # spore niedomówienia są w pracach:
    # alabastri, yeshchenko, 
    if T != 298:
        # r(T)
        deltaT = T-298 # K
        if ifsizecor:
            r1 = r1*(1+mat_sizecor_dict['Beta']*deltaT)**(1/3) 
            r2 = r2*(1+mat_sizecor_dict['Beta']*deltaT)**(1/3) 
    
        # omegap dependence on temp
        omegap=omegap/np.sqrt(1+mat_sizecor_dict['Beta']*deltaT) 
        
        # wielkosci z liu2009 maja jakikolwiek sens
        (gamma_eeT,gamma_ephT,gamma)=gamma_calc(T,omega,mat_sizecor_subdict)
    
    
    ### surface scattering correction
    if ifsizecor:
        ### surface scattering damping
        Leff= 4*np.absolute(r2**3-r1**3)/3/(r1**2+r2**2) 
        #print(Leff)
        A=1/3  # to musi byc bo inaczej nie skleja sie z badaniami
        # nanoczastek
        # jedn. rad/fs
        gamma_surf = A*mat_sizecor_dict['vF']/Leff 
        gamma = gamma + gamma_surf 
        
    ### applying gamma corrections to dielectric function
    eps_drude = 1 - omegap**2/(omega*(omega+1j*gamma)) 
    eps = eps_ib + eps_drude 
    
    ### nonlocal correction
    if ifnonlocal:
        # pressure in the hydrodynamic model
        beta2=3/5*(mat_sizecor_dict['vF'])**2 
        kLon = omegap*np.sqrt(1/beta2*(1/(1-eps_drude)-1/(eps_ib+1) ))   #moja wer
    else:
        kLon=np.zeros(omega.shape)
        
    return (eps,kLon)
