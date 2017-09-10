def GenLLprzem(Lambda,Cepsilon1,RBx,xk)
	L2=np.zeros([RBx[0].size[0],RBx[0].size[1],6,6) # LxNmx6x6

	# granica zewnetrzna, wsp lokalne
	L2[:,:,3,0]=Lambda/(2*np.pi)*Xpsi
	L2[:,:,3,1]=Lambda/(2*np.pi)*Xxi
	L2[:,:,4,0]=Lambda/(2*np.pi*sqrt(Cepsilon1))*XDpsi
	L2[:,:,4,1]=Lambda/(2*np.pi*sqrt(Cepsilon1))*XDxi
	L2[:,:,5,0]= (1/xk**2*cc)*Xpsi
	L2[:,:,5,1]= (1/xk**2*cc)*Xxi
	return(L2)
            
