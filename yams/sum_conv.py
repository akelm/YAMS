#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 15:35:29 2017

@author: ania
"""
import numpy as np
from sklearn.utils.extmath import cartesian

def sum_conv(macierz,kierunek):
    """
    find convergent part of the series
    and sums the elements using Kahan summation algorithm
    """
    # size of matrix without direction kierunek
    size_m=list(macierz.shape)
    seq_len=size_m[kierunek]
    size_m[kierunek]=1
    
#==============================================================================
#     # checking where to end summation
#==============================================================================
    # matrix with consecutive sums of elements
    macierz_c=np.cumsum(macierz,kierunek)
    # normalized gradient
    diff_mat=np.abs(np.gradient(macierz_c,axis=kierunek)/macierz_c)
    slices=list(map(slice,size_m))
    # reverse order for axis kierunek
    slices[kierunek]=slice(seq_len,-1,-1)
    # indices where to end summation
    index_mat=np.expand_dims( # expanding dims to match dimensions of macierz
        seq_len-1-np.nanargmax( # translating indice to non-reverse direciton
                              # nargmax find first largest element, here: 1
        (diff_mat<=0.01)      # norm gradient must be below 0.01 at the end of series
              ,axis=kierunek),
                    kierunek).repeat(seq_len,kierunek) # matching size of macierz
#==============================================================================
#     # masking the non-convergent tail
#==============================================================================
    # shape for placing vector on the rigth position
    new_shape=np.ones(len(size_m),dtype=int)
    new_shape[kierunek]=seq_len
    # matrix with range(seq) in the axis kierunek
    cmp_mat=np.ones(size_m)*(np.arange(seq_len).reshape(new_shape))
    # bool mask to multiply matrix
    index_mask= (cmp_mat <=index_mat)
    # zeroes the non-convergent tail
    matrix_for_multi=index_mask*macierz
#==============================================================================
#     # Kahan summation
#==============================================================================
    macierz_res=kahansum_mat(matrix_for_multi,kierunek)

        
    
#    macierz_c=np.cumsum(macierz,kierunek)
#    macierz_c_abs=np.abs(macierz_c)
#    macierz_res=np.zeros(size_m)
#    slices=list(map(slice,size_m))
#    slices[kierunek]=slice(seq_len,-1,-1)
#    
#    diff_mat=(macierz_c_abs-np.roll(macierz_c_abs,1,kierunek))>0
#    # najwyzszy numer, ktory jest zerem
#    indeks_mat=np.expand_dims(seq_len-1-np.nanargmin(diff_mat[slices], axis=kierunek),kierunek)\
#                .repeat(seq_len,kierunek)
#                
#    new_shape=np.ones(seq_len)
#    new_shape[kierunek]=seq_len
#    cmp_mat=np.ones(size_m)*(np.arange(seq_len).reshape(newshape))
#    macierz_res=(indeks_mat*cmp_mat).sum(kierunek)
#    
    return macierz_res


def kahansum(l):
    """
    This function will find the sum
    of a given list without compromising
    on the accuracy
    from: http://radiusofcircle.blogspot.com/2016/10/kahan-summation-algorithm.html"""
    summation = 0.0
    c = 0.0
    for i in l:
        y = i - c
        t = summation + y
        c = (t - summation) - y
        summation = t
    return summation

def kahansum_mat(mat,axis=0):
    """
    Kahan summation algorithm for numpy arrays
    mat - the matrix
    axis - axis along which to sum"""
    mat_shape=list(mat.shape)
    seq_len=mat_shape[axis]
    mat_shape[axis]=1
    
    summation = np.zeros(mat_shape)
    c = np.zeros(mat_shape)
    slices=list(map(slice,mat_shape))
    for i in range(seq_len):
        slices[axis]=slice(i,i+1)
        y = mat[slices] - c
        t = summation + y
        c = (t - summation) - y
        summation = t.copy()
    return summation