def inv6L(macierz):
		
	K= macierz[:,:,0:3,0:3]
	L= macierz[:,:,0:3,3:6]
	M= macierz[:,:,3:6,0:3]
	N= macierz[:,:,3:6,3:6]
	macierzinv=zeros[:,:,6,6]

	(Kinv,kdet)=inv3L1(K)
	# kdet LxNm
	(Minv,mdet)=inv3L1(M)

	sM=Minv*N
	sK=Kinv*L

	s3=sK*mdet/kdet+sM
	(s3inv,s3det)=inv3(s3)
	macierzinv[:,:,3:6,3:6]=s3inv*Minv
	
	s4=sK+sM*kdet/mdet
	(s4inv,s4det)=inv3(s4)
	stos=s3det/s4det
	macierzinv[:,:,3:6,0:3]=(s4inv*Kinv)*stos

	macierzinv[:,:,0:3,3:6]=-(Kinv*L*s3inv*Minv)/(kdet)
	macierzinv[:,:,0:3,0:3]=(Kinv*(s4det*eye(3,3)+L*s4inv*Kinv))/kdet*stos

	return (macierzinv,s3det)
