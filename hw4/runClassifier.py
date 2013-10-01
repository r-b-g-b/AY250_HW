import numpy as np
from glob import glob
import os
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score, KFold
from scipy import ndimage as ndi
import skimage as ski
from sklearn.metrics import accuracy_score

import calcFeatures

basedir = '/Users/robert/Documents/Code/pythonwork/AY250/python-seminar/Homeworks/AY250_HW/hw4'
imgdir = os.path.join(basedir, '50_categories')

if __name__=='__main__':

    categories = [os.path.split(i)[1] for i in glob(os.path.join(basedir, '50_categories', '*'))]
    ncategories = len(categories)

    fpaths = calcFeatures.get_fpaths(os.path.join(basedir, '50_categories'))
    nimgs = len(fpaths)

    # load previously calculated features
    corr_rgb = pd.read_csv('corr_rgb.csv', index_col=0)
    # corr_rgb['fpath']=corr_rgb.index
    power_ratio = pd.read_csv('power_ratio.csv', header=None)
    power_ratio.columns = ['feat_power_%2.2u' % i for i in range(1, 13)]
    power_ratio.index = fpaths

    df = corr_rgb.join(power_ratio)

    X = df.filter(regex='feat_').values
    Y = df.category.values

    Y_shuff = np.random.permutation(Y)

    # shuffle dataset
    XY = zip(X, Y)
    np.random.seed(0)
    np.random.shuffle(XY)
    X, Y = zip(*XY)
    X = np.array(X)
    Y = np.array(Y)

    # initialize RFC
    clf = RandomForestClassifier(n_estimators=50, n_jobs=-1)

    # train and evaluate, with cross validation
    scores = cross_val_score(clf, X, Y, cv=KFold(n=nimgs, n_folds=5))

    print 'Mean accuracy score: %.4f +/- %.4f %%' % (100*np.mean(scores), 100*np.std(scores))
    print 'Accuracy with random guessing: %.4f %%' % (100./ncategories)

