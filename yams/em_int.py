import numpy as np
def em_int(wspE,wspM,k,RB,xp2inv,d_el,d_m,Dd_el,cc4,cc3,Cepsilon):
	fi_el=(wspE[0]*RB[2] + wspE[1]*RB[0])/k
	Dfi_el=(wspE[0]*RB[3] + wspE[1]*RB[1])/k
	fi_m=(wspM[0]*RB[2] + wspM[1]*RB[0])/k
	Dfi_m=(wspM[0]*RB[3] + wspM[1]*RB[1])/k
	int_perp = xp2inv**2* np.matmul(np.nan_to_num(-Dfi_el*fi_el.conj()*d_el),cc4)
	int_para = xp2inv*np.matmul(np.nan_to_num(-Dfi_el*fi_el.conj()*Dd_el+fi_m*Dfi_m.conj()*d_m),cc3)
	perp = -(1j*np.sqrt(Cepsilon.conj())*int_perp).real
	para = -0.5*(1j*np.sqrt(Cepsilon.conj())*int_para).real
	return (perp,para)

def wsp(M,T,RB):
	T=list(np.rollaxis(T,2,0))
	M=list(np.rollaxis(M,2,0))
	w= (T[0]*RB[0]+T[1]*RB[1])/(T[0]*M[0]-T[1]*M[1])
	return np.nan_to_num(w.conj()*w)
