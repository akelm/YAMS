import numpy as np
from sklearn.utils.extmath import cartesian
from itertools import repeat,product,starmap
from operator import *

def find_ind(listobj,type):
    # find positions in a list: listobj where item is of type: type
    ind_pos=list(map(isinstance,listobj,repeat(type)))
    ind_pos_ind=[] if not True in ind_pos else [i for i, j in enumerate(ind_pos) if j]
    return ind_pos_ind


def check_input(main_dict,mat_dict_keys,mat_sizecor_dict_keys):
    # checking temp, order and theta
    num_vals=('max order of expansion','temperature','theta')
    wave_vals=('from','to')
    attr_set={'size correction','nonlocal correction'}
    except_list=[]
    try:
        # czy 'max order of expansion','temperature','theta' sa wieksze od 0
        except_list.append(all(map(gt,  map(main_dict.get,num_vals) ,repeat(0) )))
        # wavelength sa dodatnie
        except_list.append(all(map(gt,  map(main_dict['wavelength'].get,wave_vals) ,repeat(0) )))
        # value of every, if it exist
        except_list.append('every' in main_dict['wavelength'].keys() and \
                          not eq(main_dict['wavelength']['every'],0) )    
        # enough number of layers 
        except_list.append(len(main_dict['layers'])>=2)
        # material in mat list
        except_list.append(\
        set(map(getitem,main_dict['layers'],repeat('material'))).issubset(mat_dict_keys)) 
        # materials except for medium have correct range values, from is nonnegative
        except_list.append(all( map(ge, \
        starmap(getitem, product(\
        map(getitem,main_dict['layers'][:-1],repeat('range')),('from','to'))\
        ),repeat(0))))
        # every is nonzero
        except_list.append(not all( map(eq, \
        map(getitem, map(getitem,main_dict['layers'][:-1],repeat('range')),repeat('every')),\
        repeat(0))))
        # there is exactly one dipole
        dip_count=0
        # there is a list of materials with nonlocal and size correction
        # mat_sizecor.txt file
        gold_cor=True
        dipole_not_in_gold=True
        dipole_position=True
        for layer in main_dict['layers']:
            if 'attributes' in layer.keys():
                str_pos_ind=find_ind(layer['attributes'],str)
                dic_pos_ind=find_ind(layer['attributes'],dict)
                dic={} if not dic_pos_ind else layer['attributes'][dic_pos_ind[0]]
                if 'dipole' in dic.keys():
                    dip_count+=1
                    lower_bound=float("inf") if not 'range' in layer.keys() \
                        else min(layer['range']['from'],layer['range']['to'])
                    dip_rdict=layer['attributes'][dic_pos_ind[0]]['dipole']['range']
                    if not 0<= dip_rdict['from'] <=lower_bound:
                        dipole_position=False
                    if not 0<= dip_rdict['to'] <=lower_bound:
                        dipole_position=False
                    if dip_rdict['every']==0:
                        dipole_position=False
                if layer['material'] not in mat_sizecor_dict_keys and \
                attr_set.intersection(set(map(layer['attributes'].__getitem__,str_pos_ind))):
                    gold_cor=False
                if layer['material'] in mat_sizecor_dict_keys and 'dipole' in dic.keys():
                    dipole_not_in_gold=False
        except_list.append(dip_count==1)
        except_list.append(gold_cor)
        except_list.append(dipole_not_in_gold)
        except_list.append(dipole_position)
        # dodac jeszcze, ze nie moga graniczyc ze soba warstwy nieliniowe
        # dodac, ze polozenie dipola nie moze wychodzic poza warstwe
    except:
        raise Exception
    else:
        if not all(except_list):
            raise ValueError('test for the values didnt pass at pos: ',except_list.index(False))
        # wavelength
        if not 'every' in main_dict['wavelength'].keys():
            main_dict['wavelength']['every']=1
        main_dict['wavelength'].update(dict(zip(wave_vals,sorted(map(main_dict['wavelength'].get,wave_vals)) )))
#        map(main_dict['wavelength'].__setitem__,wave_vals,\
#            sorted(map(main_dict['wavelength'].get,wave_vals)))
        main_dict['wavelength']['every']=abs(main_dict['wavelength']['every'])
        # layers
        # make every positive, make to and from ordered
        for k in range(0,len(main_dict['layers'])-1):
            main_dict['layers'][k]['range']['every']=abs(main_dict['layers'][k]['range']['every'])
            # dict with sorted 'from' and 'to'
            temp_dict=dict(zip(wave_vals,sorted(map(main_dict['layers'][k]['range'].get, wave_vals))))
            main_dict['layers'][k]['range'].update(temp_dict)
            if 'attributes' in main_dict['layers'][k].keys():
                dic_pos_ind=find_ind(main_dict['layers'][k]['attributes'],dict)
                dic={} if not dic_pos_ind else layer['attributes'][dic_pos_ind[0]]
                if 'dipole' in dic.keys():
#                    print(main_dict['layers'][k]['attributes'])
#                    print(abs(dic['dipole']['range']['every']))
                    main_dict['layers'][k]['attributes'][dic_pos_ind[0]]['dipole']['range']['every']=\
                    abs(dic['dipole']['range']['every'])
                    # dict with sorted 'from' and 'to'
                    temp_dict=dict(zip(wave_vals,sorted(map(dic['dipole']['range'].get, wave_vals))))
                    main_dict['layers'][k]['attributes'][dic_pos_ind[0]]['dipole']['range'].update(temp_dict)
        if 'attributes' in main_dict['layers'][-1].keys():
            dic_pos_ind=find_ind(main_dict['layers'][-1]['attributes'],dict)
            dic={} if not dic_pos_ind else layer['attributes'][dic_pos_ind[0]]
            if 'dipole' in dic.keys():
                main_dict['layers'][-1]['attributes'][dic_pos_ind[0]]['dipole']['range']['every']=abs(dic['dipole']['range']['every'])
                # dict with sorted 'from' and 'to'
                temp_dict=dict(zip(wave_vals,sorted(map(main_dict['layers'][-1]['attributes'][dic_pos_ind[0]]['dipole']['range'].get, wave_vals))))
                main_dict['layers'][-1]['attributes'][dic_pos_ind[0]]['dipole']['range'].update(temp_dict)
            
#            map(main_dict['layers'][k]['range'].__setitem__, wave_vals,
#            sorted(map(main_dict['layers'][k]['range'].get, wave_vals)))
            
        return main_dict    

def parametry1(data, mat_dict, mat_sizecor_dict,mat_tempcor_dict):
    # import refractive index dictionary
#    mat=np.genfromtxt('materials.txt', dtype=str, delimiter='\t', skip_header=1, \
#                      filling_values=' ')
#    mat_n=dict(zip(mat[:,0],mat[:,1])) # files
#    #mat_ref=dict(zip(mat[:,0],mat[:,2])) # lit references
#    # matrials with size correction, temp corrections and nonlocal corrections
#    mat_sizecor_dict=np.genfromtxt('mat_sizecor.txt', dtype=str, usecols=0,\
#                                   delimiter='\t', skip_header=1, filling_values=' ')
#    # temp correction for solvent RI, due to different density
#    mat_tempcor_dict=np.genfromtxt('mat_tempcor.txt', dtype=str, usecols=0,\
#                                   delimiter='\t', skip_header=1, filling_values=' ')
    #mat_tempcor=mat_tempcor_file[:,0]
#    with open('../pkg_resource/mat_tempcor.yaml') as stream:
#        mat_tempcor_dict=yaml.load(stream)
#    with open('../pkg_resource/mat_sizecor.yaml') as stream:
#        mat_sizecor_dict=yaml.load(stream)
#    with open('../pkg_resource/materials.yaml') as stream:
#        mat_dict=yaml.load(stream)

        
    layers=[]
    Ca_init=[]
    nielokalne_init=[]
    sizecor_init=[]
    tempcor_init=[]
    Cepsilon_init=[]
    dd_init=None
    dip_range_init=None
    rho_rel=1
    # dictionary with default parameters, by search keys
    
    main_dict={'layers': [],\
                  'max order of expansion': 5,\
                  'temperature': 298,\
                  'theta': 180,\
                  'wavelength': {'every': 1, 'from': 300, 'to': 850}}
    #dict_num={'theta': 180, 'temp': 298, 'order': 5}
    main_dict.update(data)
    # checking the values
    main_dict=check_input(main_dict,mat_dict.keys(),mat_sizecor_dict.keys())
    
    # assigning values for inner layers
    Lambda=zakres(main_dict['wavelength'])[:,None] # Lx1
    nNmax=main_dict['max order of expansion']
    (pin,taun,bn1mat)=pin_taun(nNmax,main_dict['theta'])
    T=main_dict['temperature']
    # for every layer but medium
    for k in range(0,len(main_dict['layers'])-1):
        dic=main_dict['layers'][k]
        # name of the layer
        layers.append(dic['material'])
        # ref ind
        Cepsilon_init.append( give_eps(mat_dict[dic['material']]['file'],Lambda) ) # L x 1
        # range of layer
        Ca_init.append(zakres(dic['range']))
        
        if 'attributes' in dic.keys():
            str_pos_ind=find_ind(dic['attributes'],str)
            dic_pos_ind=find_ind(dic['attributes'],dict)
            dip_dict={} if not dic_pos_ind else dic['attributes'][dic_pos_ind[0]]
            if 'dipole' in dip_dict.keys():
                dd_init=k
                dip_range_init=zakres(dip_dict['dipole']['range'])
            if 'nonlocal correction' in map(dic['attributes'].__getitem__,str_pos_ind):
                nielokalne_init.append(k)
            if 'size correction' in map(dic['attributes'].__getitem__,str_pos_ind):
                sizecor_init.append(k)
            if T!=298 and dic['material'] in mat_sizecor_dict.keys():
                tempcor_init.append(k)
    # medium
    dic=main_dict['layers'][-1]
    # name of the layer
    layers.append(dic['material'])
    # ref ind
    if T!=298 and dic['material'] in mat_tempcor_dict.keys():
        ceps,rho_rel=give_eps(mat_dict[dic['material']]['file'],\
                              Lambda,T=T,mat_dict=mat_tempcor_dict[dic['material']])
        Cepsilon_init.append( ceps )
    else:
        Cepsilon_init.append( give_eps(mat_dict[dic['material']]['file'],Lambda) )
    # last layer
    if 'attributes' in dic.keys():
        dic_pos_ind=find_ind(dic['attributes'],dict)
        dip_dict={} if not dic_pos_ind else dic['attributes'][dic_pos_ind[0]]
        if 'dipole' in dip_dict.keys():
            dd_init=len(layers)-1;
            dip_range_init=zakres(dip_dict['dipole']['range'])
    
    # generuje liste interfejsow
    Camat=cartesian(Ca_init)
    Camat=Camat[np.nonzero(np.sum(Camat,1))]   
    
    #print(nNmax,Lambda[0],Cepsilon_init[0][0],Camat[0][0],dd_init,\
    #            nielokalne_init,sizecor_init,T,layers) 
    return (nNmax,Lambda,Cepsilon_init,Camat,dd_init,\
                nielokalne_init,sizecor_init,tempcor_init,T,pin,taun,bn1mat,layers,dip_range_init,rho_rel)    


def zakres(dic):
    return np.arange(dic['from'], dic['to']+dic['every'],dic['every'])

def give_eps(filename,Lambda,mat_dict=None,T=None):
    ceps=dict(np.genfromtxt('../pkg_resources/ref_ind/'+filename+'.txt',dtype=complex))
        # reducing RI vector to desired wavelengths
    ceps1=np.array([*map(ceps.get,Lambda[:,0].tolist())])
    
    if mat_dict:
        # loading densities for T
        rho_array=np.genfromtxt('../pkg_resources/rho/'+mat_dict['file']+'.txt', \
            dtype=float,delimiter='\t')
        temp_range=rho_array[:,0]
        if not min(temp_range)<=T<=max(temp_range):
            print('temp of solvent outise range')
        # searching for closest temp (index) in the temp_range
        temp_val=list(abs(temp_range-T))
        closest_index_T=temp_val.index(min(temp_val))
        # closest rho
        rho=rho_array[closest_index_T,1]
        # loooking for 298 K index
        temp_val298=list(abs(temp_range-298))
        closest_index_298=temp_val298.index(min(temp_val298))
        rho298=rho_array[closest_index_298,1]
        rho_rel=rho/rho298
        # calculating b from Eyckmann's formula
        # after Mantulin1972
        brho=(ceps1**2-1)/(ceps1+0.4)*rho_rel
        # new refractive index from Eyckmann formula
        ceps2=( 0.5*(brho+np.sqrt(brho**2+4+1.6*brho)) )**2
        return ceps2[:,None],rho_rel
    else:         
        ceps2=ceps1**2
        return ceps2[:,None]

#def give_RI_temp(mat_dict,Lambda,T):
#    temp_range=zakres(mat_dict['temp_range'])
#    wave_range=zakres(mat_dict['wavelength'])
#    
#    if not min(temp_range)<=T<=max(temp_range):
#        print('temp of solvent outise range')
#    # searching for closest temp (index) in the temp_range
#    temp_val=abs(temp_range-T)
#    closest_index_T=temp_val.index(min(temp_val))
#    # loading apropriate column from file
#    ceps=np.genfromtxt('../pkg_resources/ref_ind/'+mat_dict['file']+'.txt', \
#    dtype=complex, usecols=closest_index_T,delimiter='\t')
#    ceps_dict=dict(zip(wave_range,ceps))
#    # reducing RI vector to desired wavelengths
#    ceps1=np.array(list(map(ceps_dict.get,Lambda[:,0].tolist())))**2
#    
#    return ceps1[:,None]

def pin_taun(nNmax,nNbtheta=180):

    theta=np.linspace(0,np.pi,nNbtheta)[None,:,None]
    mu=np.cos(theta)
    pinm1=np.zeros([1,nNbtheta,nNmax+1])
    pinm1[:,:,1]=np.ones([1,nNbtheta])
    # Get pi_2 to pi_nNmax by recurrence (see SPlaC guide)
    # pi_n is pinm1(:,n+1)
    for n in range(2,nNmax+1):
        pinm1[:,:,n]=(2*n-1)/(n-1)*mu[:,:,0]*pinm1[:,:,n-1]-n/(n-1)*pinm1[:,:,n-2]
    # return pi_n matrix (except n=0)
    pin=pinm1[:,:,1:] # 1 x T x N
    # return tau_n matrix
    nmat=np.arange(1,nNmax+1)[None,None,:]
    taun=nmat*mu*pin - (nmat+1)*pinm1[:,:,:-1]
    
#    # matlab
#    n=1:nNmax;
#    stIncEabn1.bn1 = i.^(n+1) .* sqrt(pi*(2*n+1));
    nn=np.swapaxes(nmat,1,2) # 1 do nNmax
    bn1mat=1j**(nn+1)*np.sqrt(np.pi*(2*nn+1))
    return (pin,taun,bn1mat)


    
    
    
    
    
    