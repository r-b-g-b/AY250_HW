from multiprocessing import Pool, cpu_count
import pandas as pd
import os
from glob import glob
import numpy as np
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.feature import hog
from skimage.transform import rescale
from sklearn.decomposition import PCA

numproc = cpu_count()

def map_hog(fpaths):

    fpaths_split = split_seq(fpaths, numproc)
    
    # initialize pool?
    p = Pool(numproc)
    # map jobs to processors
    result = p.map_async(calc_hog, fpaths_split)
    poolresult = result.get()

    x = np.array(poolresult[0])
    for i in range(1, numproc):
        x = np.vstack((x, poolresult[i]))

    n_components = 20
    pca = PCA(n_components=n_components)
    x2 = pca.fit_transform(x)
    fnames = [os.path.split(i)[1] for i in fpaths]
    categories = [i.split('_')[0] for i in fnames]

    df = pd.DataFrame(x2, columns=['feat_hog_%2.2u'%i for i in range(1, n_components+1)])
    df['fpath'] = fnames
    df['category'] = categories

    df.to_csv('hog.csv')


def calc_hog(fpaths):

    hogs = []
    
    for fpath in fpaths:
        img = imread(fpath)
        if len(img.shape)==3:
            img = rgb2gray(img)
        # rescale so all feature vectors are the same length
        img_resize = resize(img, (150, 200))
        img_hog = hog(img_resize)
        hogs.append(img_hog)

    return hogs

def calc_spatial_power_ratio(fpaths):
    power_ratio = []

    for fpath in fpaths:
        category, _ = os.path.split(fpath)
        img = imread(fpath)
        if len(img.shape)==3:
            img = rgb2gray(img)
        img_resize = resize(img, (300, 400))
        IMG = np.fft.rfft2(img_resize)

    return power_ratio

def calc_rgb_corr(fpaths):
    
    corr_rg, corr_rb, corr_gb = [], [], []
    for fpath in fpaths:
        img = imread(fpath)
        if len(img.shape)==3:
            corr_rg.append(np.corrcoef(img[...,0].flatten(), img[...,1].flatten())[0,1])
            corr_rb.append(np.corrcoef(img[...,0].flatten(), img[...,2].flatten())[0,1])
            corr_gb.append(np.corrcoef(img[...,1].flatten(), img[...,2].flatten())[0,1])
        elif len(img.shape)==2:
            corr_rg, corr_rb, corr_gb = 0., 0., 0.

    corr_rgb = zip(corr_rg, corr_rb, corr_gb)
    return corr_rgb

def map_feature_calculation(func, fpaths, func_name):
    # split fpaths for multiprocessing
    fpaths_split = split_seq(fpaths, numproc)
    
    # initialize pool?
    p = Pool(numproc)
    # map jobs to processors
    result = p.map_async(func, fpaths_split)
    poolresult = result.get()
    
    feature = poolresult[0]
    for i in range(1, numproc):
        feature.extend(poolresult[i])
    
    return feature

def split_seq(seq, size):
    newseq = []
    splitsize = 1.0/size*len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i*splitsize)):
        int(round((i+1)*splitsize))])
    return newseq

