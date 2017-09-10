import numpy as np
import re
def zakres(line):
	# finds numbers in the line
	l_ran=re.findall(r'\b\d+\b',line)
	if len(l_ran)==0: # no numbers
		raise Exception('no number in the line')
	if len(l_ran)==1: # one number in the line
		return l_ran[0]
	else: # two or more numbers
		if l_ran[0]>l_ran[1]: # checks the ordering
			(l_ran[0],l_ran[1])=(l_ran[1],l_ran[0])
		if len(l_ran)==2: # just two numbers
			return np.arange(l_ran[0],l_ran[1]+1)
		else: # step given
			l_ran[2]=np.abs(l_ran[2])
			return np.arange(l_ran[0],l_ran[1]+l_ran[2],l_ran[2])
