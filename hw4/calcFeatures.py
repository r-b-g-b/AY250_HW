from multiprocessing import Pool, cpu_count
import pandas as pd
import os
from glob import glob
import numpy as np
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.feature import hog
from skimage.transform import resize
from sklearn.decomposition import PCA

numproc = cpu_count()

basedir = '/Users/robert/Documents/Code/pythonwork/AY250/python-seminar/Homeworks/AY250_HW/hw4'
imgdir = os.path.join(basedir, '50_categories')

def combine_hog():
    '''
    Combine the many HOG output files into one array and attempt to compute principal components.
    '''

    hogs = np.empty((0, 15876))
    hogfiles = glob(os.path.join('hog_tmp_*.npz'))
    for hogfile in hogfiles:
        hog_ = np.load(hogfile)['arr_0']
        hogs = np.vstack((hogs, hog_))

    pca = RandomizedPCA(n_components=20)
    hogs2 = pca.fit_transform(hogs)

def calc_hog(fpaths):
    '''
    Compute histogram of gradients (HOG). Saves in batches to prevent memory issues.
    Input:
        fpaths : files on which HOG will be computed
    '''
    olddir = os.getcwd()
    os.chdir(imgdir)
    hogs = np.empty((100, 15876))
    
    j=0
    for i, fpath in enumerate(fpaths):
        if i%100==0 and i>0:
            j+=1
            print '%u of %u' % (i, len(fpaths))
            np.savez('hog_tmp_%2.2u.npz'%j, hogs[:i, :])
            hogs = np.empty((100, 15876))
        img = imread(fpath)
        if len(img.shape)==3:
            img = rgb2gray(img)
        # rescale so all feature vectors are the same length
        img_resize = resize(img, (128, 128))
        img_hog = hog(img_resize)
        hogs[i%100, :] = img_hog

    if i%100>0:
        np.savez('hog_tmp_%2.2u.npz'%(j+1), hogs[:(i%100+1), :])

    os.chdir(olddir)
    return hogs

def calc_spatial_power_hist(fpaths):
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
        distgp.index=[fpath]

        if i==0:
            power_hist=distgp
        else:
            power_hist = power_hist.append(distgp)

    power_hist.index.name='fpath'
    power_hist.columns = ['feat_power_%2.2u' % i for i in range(1, 13)]
    power_hist.to_csv('power_hist.csv')
    # pd.DataFrame(dict(fpath=fpaths, power_ratio))
    # np.savetxt('power_hist.csv', np.array(power_ratio), delimiter=',')

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
