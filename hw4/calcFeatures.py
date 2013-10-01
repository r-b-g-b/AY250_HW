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

    hogs = np.empty((0, 15876))
    hogfiles = glob(os.path.join(imgdir, 'hog_tmp_*.npz'))
    for hogfile in hogfiles:
        hog_ = np.load(hogfile)['arr_0']
        hogs = np.vstack((hogs, hog_))

    pca = RandomizedPCA(n_components=20)
    hogs2 = pca.fit_transform(hogs)




def map_hog(fpaths=None):

    # load image file paths
    if fpaths is None:
        fpaths = get_fpaths()

    # split paths for parallel processing
    fpaths_split = split_seq(fpaths, numproc)
    
    # initialize pool?
    p = Pool(numproc)
    # map jobs to processors
    result = p.map_async(calc_hog, fpaths_split)
    poolresult = result.get()

    # concatenate results from multiple processes
    x = np.array(poolresult[0])
    for i in range(1, numproc):
        x = np.vstack((x, poolresult[i]))

    # PCA on huge dimensioned features to get just 20 features
    n_components = 20
    pca = PCA(n_components=n_components)
    x2 = pca.fit_transform(x)

    # create file name and category columns for DataFrame
    fnames = [os.path.split(i)[1] for i in fpaths]
    categories = [i.split('_')[0] for i in fnames]

    df = pd.DataFrame(x2, columns=['feat_hog_%2.2u'%i for i in range(1, n_components+1)])
    df['fpath'] = fnames
    df['category'] = categories

    df.to_csv('hog.csv')

def calc_hog(fpaths):

    olddir = os.getcwd()
    os.chdir(imgdir)
    hogs = np.empty((100, 15876))
    
    j=42
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

def calc_spatial_power_ratio(fpaths):

    power_ratio = []
    
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

        df = pd.DataFrame(dict(fft_dist_bin=fft_dist_bin_start,
            img_fft=img_fft))

        distgp = df.groupby('fft_dist_bin').agg({'img_fft': np.sum})

        power_ratio.append(distgp.values)

    np.savetxt('power_ratio.csv', np.array(power_ratio), delimiter=',')
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


def get_fpaths(imgdir=imgdir):
    # get image names
    olddir = os.getcwd()
    os.chdir(imgdir)
    catpaths = glob(os.path.join('*'))
    fpaths = []
    for catpath in catpaths:
        fpaths_ = glob(os.path.join(catpath, '*.jpg'))
        fpaths.extend([os.path.split(i)[1] for i in fpaths_])
        
    os.chdir(olddir)
    fpaths.sort()
    return fpaths
