# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
from glob import glob
import os
import pandas as pd

# <codecell>

from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from scipy import ndimage as ndi
import skimage as ski

# <codecell>

from multiprocessing import cpu_count, Pool

# <codecell>

numproc = cpu_count()

# <codecell>

# get image names
catpaths = glob(os.path.join('50_categories', '*'))
categories, fpaths = [], []
for catpath in catpaths:

    fpaths_ = glob(os.path.join(catpath, '*.jpg'))
    fpaths.extend(fpaths_)
    _, cat = os.path.split(catpath)
    categories.extend([cat]*len(fpaths_))
    
XY = zip(fpaths, categories)

# <codecell>

np.random.seed(0)
np.random.shuffle(XY)

# <codecell>

fpaths, categories = zip(*XY)

# <codecell>

zip(fpaths[:5], categories[:5])

# <codecell>

# load previously calculated features
corr_rgb = pd.read_csv('corr_rgb.csv')

# <codecell>

kf = cross_validation.KFold(nimgs, 10)
# split into train and test sets
for train_ix, test_ix in kf:
    features = calcFeatures(fpaths[train_ix])
    clf.fit(features

# <codecell>


# <codecell>

fpath = fpaths[0]
img = ndi.imread(fpath)
img_g = img.dot([0.299, 0.587, 0.144])
img_g.shape

# <codecell>

def map_rgb_corr(fpaths):
    # split for multiprocessing
    fpaths_split = split_seq(fpaths, numproc)
    
    p = Pool(numproc)
    result = p.map_async(calc_rgb_corr, fpaths_split)
    poolresult = result.get()
    
    df = pd.concat(poolresult)
    
    df.to_csv('corr_rgb2.csv', index=False)

# <codecell>

def calc_rgb_corr(fpaths):
    
    corr_rg, corr_rb, corr_gb = [], [], []
    for fpath in fpaths:
        img = ndi.imread(fpath)
        corr_rg.append(np.corrcoef(img[...,0].flatten(), img[...,1].flatten())[0,1])
        corr_rb.append(np.corrcoef(img[...,0].flatten(), img[...,2].flatten())[0,1])
        corr_gb.append(np.corrcoef(img[...,1].flatten(), img[...,2].flatten())[0,1])
        
    d = dict(fpath=fpaths, corr_rg=corr_rg, corr_rb=corr_rb, corr_gb=corr_gb)
    return pd.DataFrame(d)

# <codecell>

def split_seq(seq, size):
    newseq = []
    splitsize = 1.0/size*len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i*splitsize)):
        int(round((i+1)*splitsize))])
        return newseq

# <codecell>

fpaths[:5]

# <codecell>

map_rgb_corr(fpaths)

# <codecell>


