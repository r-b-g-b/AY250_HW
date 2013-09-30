from multiprocessing import Pool, cpu_count
import pandas as pd
import os
from glob import glob
import numpy as np


def map_rgb_corr(fpaths):
    # split fpaths for multiprocessing
    fpaths_split = split_seq(fpaths, numproc)
    
    # initialize pool?
    p = Pool(numproc)
    # map jobs to processors
    result = p.map_async(calc_rgb_corr, fpaths_split)
    poolresult = result.get()
    
    df = pd.concat(poolresult)
    
    # save to disk
    df.to_csv('corr_rgb2.csv', index=False)

def calc_rgb_corr(fpaths):
    
    corr_rg, corr_rb, corr_gb = [], [], []
    for fpath in fpaths:
        category, _ = os.path.split(fpath)
        img = ndi.imread(fpath)
        if len(img.shape)==3:
            corr_rg.append(np.corrcoef(img[...,0].flatten(), img[...,1].flatten())[0,1])
            corr_rb.append(np.corrcoef(img[...,0].flatten(), img[...,2].flatten())[0,1])
            corr_gb.append(np.corrcoef(img[...,1].flatten(), img[...,2].flatten())[0,1])
        elif len(img.shape)==2:
            corr_rg, corr_rb, corr_gb = 0., 0., 0.

    d = dict(category=categories, fpath=fpaths, corr_rg=corr_rg, corr_rb=corr_rb, corr_gb=corr_gb)
    return pd.DataFrame(d)

def split_seq(seq, size):
    newseq = []
    splitsize = 1.0/size*len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i*splitsize)):
        int(round((i+1)*splitsize))])
    return newseq
