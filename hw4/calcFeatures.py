from multiprocessing import Pool, cpu_count
import pandas as pd
import os
from glob import glob
import numpy as np
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.feature import hog
from skimage.transform import resize
from sklearn.preprocessing import scale
from sklearn.decomposition import RandomizedPCA

numproc = cpu_count()

basedir = '/Users/robert/Documents/Code/pythonwork/AY250/python-seminar/Homeworks/AY250_HW/hw4'
imgdir = os.path.join(basedir, '50_categories')

def calc_hog(fpaths, save=False):
    '''
    Compute histogram of gradients (HOG). Saves in batches to prevent memory issues.
    Input:
        fpaths : files on which HOG will be computed
    '''

    hogs = np.empty((len(fpaths), 15876))

    for i, fpath in enumerate(fpaths):
        img = imread(os.path.join(imgdir, fpath))
        if len(img.shape)==3:
            img = rgb2gray(img)
        # rescale so all feature vectors are the same length
        img_resize = resize(img, (128, 128))
        img_hog = hog(img_resize)

        hogs[i, :] = img_hog

    hogs_sc = scale(hogs)
    n_components = 15
    pca = RandomizedPCA(n_components=n_components)
    hogs_decomp = pca.fit_transform(hogs_sc)

    df = pd.DataFrame(hogs_decomp, index=[os.path.split(i)[1] for i in fpaths])
    df.index.name='fpath'
    df.columns = ['feat_hog_%2.2u' % i for i in range(1, n_components+1)]
    if save: df.to_csv('hog.csv')
    
    return df

def calc_spatial_power_hist(fpaths, save=False):
    '''
    A set of features that attempts to represent the distributions of 
    spatial frequencies present in the image. Calculates a 2-D FFT
    and then creates a histogram of power in different frequencies.
    Disregards horizontal/vertical orientation of frequency, but 
    preserves the frequency.
    Input:
        fpaths : the files for which this feature is computed

    Output is saved to a file
    '''

    fft_shape = (200, 101)
    X, Y = np.meshgrid(np.arange(fft_shape[1]), np.arange(fft_shape[0]))
    fft_dist = ((X**2)+(Y**2))**0.5
    fft_dist = fft_dist.flatten()[1:]
    fft_dist_bin = pd.cut(fft_dist, bins=np.arange(0, 260, 20))
    fft_dist_bin_start = [int(i[1:].split(',')[0]) for i in fft_dist_bin]

    power_hist = pd.DataFrame()
    for i, fpath in enumerate(fpaths):
        print '%u of %u: %s' % (i+1, len(fpaths), fpath)

        img = imread(os.path.join(imgdir, fpath))
        img = rgb2gray(img)
        img2 = resize(img, (200, 200))
        img_fft = np.abs(np.fft.rfft2(img2).flatten()[1:])
        img_fft = img_fft / img_fft.sum()

        df_ = pd.DataFrame(dict(fft_dist_bin=fft_dist_bin_start,
            img_fft=img_fft))

        distgp = df_.groupby('fft_dist_bin').agg({'img_fft': np.sum}).T
        distgp.index=[os.path.split(fpath)[1]]

        power_hist = power_hist.append(distgp)

    power_hist.index.name='fpath'
    power_hist.columns = ['feat_power_%2.2u' % i for i in range(1, 13)]
    
    if save: power_hist.to_csv('power_hist.csv')
    return power_hist

def run_rgb_corr(fpaths, save=False):

    tmp = calc_rgb_corr(fpaths[:50])
    fpaths2, corr_rgb = zip(*tmp)

    corr_rgb = np.array(corr_rgb)
    df = pd.DataFrame(corr_rgb, index=fpaths2)
    df.index.name = 'fpath'
    df.columns = ['feat_corr_rgb_%2.2u'%i for i in range(1, len(df.columns)+1)]

    if save: df.to_csv('corr_rgb.csv')

    return df

def calc_rgb_corr(fpaths):
    '''
    A simple feature of the correlation coefficient between R, G, and B channels of the image.
    Input:
        fpaths : file paths
    Output
        corr_rgb : length 3 tuple with RG, RB, and GB correlation coefficients
    '''
    corr_rg, corr_rb, corr_gb = [], [], []
    for fpath in fpaths:
        img = imread(os.path.join(imgdir, fpath))
        if len(img.shape)==3:
            corr_rg.append(np.corrcoef(img[...,0].flatten(), img[...,1].flatten())[0,1])
            corr_rb.append(np.corrcoef(img[...,0].flatten(), img[...,2].flatten())[0,1])
            corr_gb.append(np.corrcoef(img[...,1].flatten(), img[...,2].flatten())[0,1])
        elif len(img.shape)==2:
            corr_rg, corr_rb, corr_gb = 0., 0., 0.

    corr_rgb = zip(corr_rg, corr_rb, corr_gb)
    return zip([os.path.split(i)[1] for i in fpaths], corr_rgb)

def map_feature_calculation(func, fpaths, func_name):
    '''
    General function that maps out a function over a bunch of file paths.
    Input:
    func : the function to be run of the file paths
    fpaths : a list of file paths to be processed
    func_name : str, used to name to output file
    '''
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
    '''
    splits a sequence into roughly equal "size" equal size lists
    '''
    newseq = []
    splitsize = 1.0/size*len(seq)
    for i in range(size):
        newseq.append(seq[int(round(i*splitsize)):
        int(round((i+1)*splitsize))])
    return newseq


def get_fpaths(imgdir=imgdir):
    '''
    Returns the file paths for all of the images in imgdir.
    Images should organized into category folders.
    '''
    # get image names
    olddir = os.getcwd()
    os.chdir(imgdir)
    catpaths = glob(os.path.join('*'))
    fpaths = []
    for catpath in catpaths:
        fpaths_ = glob(os.path.join(catpath, '*.jpg'))
        fpaths.extend(fpaths_)
        
    os.chdir(olddir)
    fpaths.sort()
    return fpaths
