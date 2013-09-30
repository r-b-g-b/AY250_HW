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

def calc_hog(fpaths):

    hogs = []
    
    for fpath in fpaths:
        category, _ = os.path.split(fpath)
        img = imread(fpath)
        if len(img.shape)==3:
            img = rgb2gray(img)
        # rescale so all feature vectors are the same length
        img_resize = resize(img, (300, 400))
        img_hog = hog(img_resize)
        hogs.append(img_hog)

    return hogs

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


def calc_spatial_power_ratio(fpaths):
    power_ratio = []

    for fpath in fpaths:
        category, _ = os.path.split(fpath)
        img = imread(fpath)
        if len(img.shape)==3:
            img = rgb2gray(img)
        img_resize = resize(img, (300, 400))
        IMG = np.fft.rfft2(img_resize)


    d = dict(category=categories, fpath=fpaths, feat_hi_lo_ratio=power_ratio)
    return pd.DataFrame(d)

def calc_rgb_corr(fpaths):
    
    corr_rg, corr_rb, corr_gb = [], [], []
    for fpath in fpaths:
        category, _ = os.path.split(fpath)
        img = imread(fpath)
        if len(img.shape)==3:
            corr_rg.append(np.corrcoef(img[...,0].flatten(), img[...,1].flatten())[0,1])
            corr_rb.append(np.corrcoef(img[...,0].flatten(), img[...,2].flatten())[0,1])
            corr_gb.append(np.corrcoef(img[...,1].flatten(), img[...,2].flatten())[0,1])
        elif len(img.shape)==2:
            corr_rg, corr_rb, corr_gb = 0., 0., 0.

    d = dict(category=categories, fpath=fpaths, feat_corr_rg=corr_rg, feat_corr_rb=corr_rb, feat_corr_gb=corr_gb)
    return pd.DataFrame(d)

def map_feature_calculation(func, fpaths, func_name):
    # split fpaths for multiprocessing
    fpaths_split = split_seq(fpaths, numproc)
    
    # initialize pool?
    p = Pool(numproc)
    # map jobs to processors
    result = p.map_async(func, fpaths_split)
    poolresult = result.get()
    
    df = pd.concat(poolresult)
    
    # save to disk
    df.to_csv('%s.csv' % func_name, index=False)

def split_seq(seq, size):
    newseq = []
    splitsize = 1.0/size*len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i*splitsize)):
        int(round((i+1)*splitsize))])
    return newseq


fig, (ax1, ax2) = plt.subplots(1, 2)
for i, fpath in enumerate(fpaths[:3000:100]):
    imread(fpath)
    img = rgb2gray(imread(fpath))
    IMG = np.fft.rfft2(img)
    ax1.imshow(img)
    ax2.imshow(np.log(np.abs(IMG)))
    fig.savefig('tmp_%3.3u.jpg' % i)
    ax1.cla(); ax2.cla()



