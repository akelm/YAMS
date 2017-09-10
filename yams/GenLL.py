import inwersje_macierzy as inw
def GenLL(Lambda,Cepsilon,Ca,RBz1,RBx1,RBl1,RBz,RBl,RBx,xk1,zk1,xkl1,xkl,xk,xk_1):
	# Ca1 to Ca[kk-1]
	# Ca to Ca[kk]
	L=np.zeros([RBz[0].size[0],RBz[0].size[1],6,6) # LxNmx6x6
	PL=L.copy()
	PP=L.copy()
	L2=L.copy()
	L[:,:,0,3]=-Lambda/(2*np.pi)*RBz1[2]
	L[:,:,0,4]=-Lambda/(2*np.pi)*RBz1[0]
	L[:,:,1,3]=-Lambda/(2*np.pi*np.sqrt(Cepsilon[0]))*RBz1[3]
	L[:,:,1,4]=-Lambda/(2*np.pi*np.sqrt(Cepsilon[0]))*RBz1[1]
	L[:,:,2,3]= (1/(xk1**2)-1/(zk1**2))*cc*RBz1[2]
	L[:,:,2,4]= (1/(xk1**2)-1/(zk1**2))*cc*RBz1[0]
	
	L[:,:,0,5]=Lambda/(2*np.pi)*RBx1[2]
	L[:,:,0,0]=Lambda/(2*np.pi)*RBx1[0]
	L[:,:,1,5]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBx1[3]
	L[:,:,1,0]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBx1[1]

	L[:,:,1,1]=-1j*Ca[0]*1/(xkl1**2)*cc*RBl1[2]
	L[:,:,1,2]=-1j*Ca[0]*1/(xkl1**2)*cc)*RBl1[0]
	L[:,:,2,1]= 1j*( -RBl1[3]*1/xkl1+RBl1[2]*1/(xkl1**2) )
	L[:,:,2,2]= 1j*( -RBl1[1]*1/xkl1+RBl1[0]*1/(xkl1**2) )
	
	L[:,:,3,5]=Lambda/(2*np.pi)*RBz[2]
	L[:,:,3,0]=Lambda/(2*np.pi)*RBz[0]
	L[:,:,4,5]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBz[3]
	L[:,:,4,0]=Lambda/(2*np.pi*np.sqrt(Cepsilon[1]))*RBz[1]

	L[:,:,4,1]=-1j*Ca[1]* (1/(xkl**2)*cc) *RBl[2]
	L[:,:,4,2]=-1j*Ca[1]* (1/(xkl**2)*cc) *RBl[0]
	L[:,:,5,1]= 1j*( -RBl[3],1/xkl+RBl[2]*1/(xkl**2) )
	L[:,:,5,2]= 1j*( -RBl[1]*1/xkl)+RBl[0]*1/(xkl**2) )
	
	# wsp nielokalna
	
	PL[:,:,range(6),range(6)]=1
	PL[:,:,2,0]=1/(xk1**2)*cc*2*np.pi/Lambda
	PL[:,:,5,3]=1/(xk**2)*cc*2*np.pi/Lambda
	
	PP[:,:,range(6),range(-1,5))]=1
	
	# macierz do przemnozenia

	# granica zewnetrzna, wsp lokalne
	L2[:,:,3,0]=Lambda/(2*np.pi)*Xpsi
	L2[:,:,3,1]=Lambda/(2*np.pi)*Xxi
	L2[:,:,4,0]=Lambda/(2*np.pi*sqrt(Cepsilon[2]))*XDpsi
	L2[:,:,4,1]=Lambda/(2*np.pi*sqrt(Cepsilon[2]))*XDxi
	L2[:,:,5,0]= (1/xk_1**2*cc)*Xpsi
	L2[:,:,5,1]= (1/xk_1**2*cc)*Xxi
	
	# L2=GenLLprzem(Lambda,Cepsilon[kk+1].[:,None],RBx,xk)
	L3=np.matmul(PL,L2)
	(Linv,Ldet)=inw.inv6L(L)
	L4=np.matmul(Linv,L3)/Ldet
	# L4=cellpinv_multi(L,L3)
	L5=np.matmul(PP,L4)
	return(L5)
	
	
	
