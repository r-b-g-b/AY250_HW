import numpy as np
from glob import glob
import os
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from scipy import ndimage as ndi
import skimage as ski
from sklearn.metrics import accuracy_score

from multiprocessing import cpu_count, Pool

imgdir = '/Users/robert/Documents/Code/pythonwork/AY250/python-seminar/Homeworks/AY250_HW/hw4'

def get_fpaths(imgdir):
    # get image names
    olddir = os.getcwd()
    os.chdir(imgdir)
    catpaths = glob(os.path.join('*'))
    categories, fpaths = [], []
    ncategories = len(catpaths)
    for catpath in catpaths:

        fpaths_ = glob(os.path.join(catpath, '*.jpg'))
        fpaths.extend(fpaths_)
        _, cat = os.path.split(catpath)
        categories.extend([cat]*len(fpaths_))
        
    os.chdir(olddir)

    return fpaths, categories

fpaths = get_fpaths(imgdir)

numproc = cpu_count()

nimgs = len(fpaths)

XY = zip(fpaths, categories)

np.random.seed(0)
np.random.shuffle(XY)

fpaths, categories = zip(*XY)

# load previously calculated features
corr_rgb = pd.read_csv('corr_rgb.csv')

X = corr_rgb.filter(regex='corr_').values
Y = corr_rgb.category.values

XY = zip(X, Y)
np.random.seed(0)
np.random.shuffle(XY)
X, Y = zip(*XY)
X = np.array(X)
Y = np.array(Y)

clf = RandomForestClassifier(n_estimators=20)
# train, with cross validation
kf = cross_validation.KFold(nimgs, 10)


# split into train and test sets
scores = []
for train_ix, test_ix in kf:
    train_x = X[train_ix]
    train_y = Y[train_ix]
    clf.fit(train_x, train_y)

    test_x = X[test_ix]
    test_y = Y[test_ix]
    Y_hat = clf.predict(test_x)

    scores.append(accuracy_score(test_y, Y_hat))

# fpath = fpaths[0]
# img = ndi.imread(fpath)
# img_g = img.dot([0.299, 0.587, 0.144])
# img_g.shape

def map_rgb_corr(fpaths):
    # split for multiprocessing
    fpaths_split = split_seq(fpaths, numproc)
    
    p = Pool(numproc)
    result = p.map_async(calc_rgb_corr, fpaths_split)
    poolresult = result.get()
    
    df = pd.concat(poolresult)
    
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

map_rgb_corr(fpaths)