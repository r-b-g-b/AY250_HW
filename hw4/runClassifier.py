import numpy as np
from glob import glob
import os
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from scipy import ndimage as ndi
import skimage as ski
from sklearn.metrics import accuracy_score

basedir = '/Users/robert/Documents/Code/pythonwork/AY250/python-seminar/Homeworks/AY250_HW/hw4'
imgdir = os.path.join(basedir, '50_categories')

def get_fpaths(imgdir=imgdir):
    # get image names
    olddir = os.getcwd()
    os.chdir(imgdir)
    catpaths = glob(os.path.join('*'))
    fpaths = []
    for catpath in catpaths:
        fpaths_ = glob(os.path.join(catpath, '*.jpg'))
        fpaths.extend(fpaths_)
        
    os.chdir(olddir)

    return fpaths

if __name__=='__main__':

    categories = [os.path.split(i)[1] for i in glob(os.path.join(basedir, '50_categories', '*'))]
    ncategories = len(categories)

    fpaths = get_fpaths(os.path.join(basedir, '50_categories'))
    nimgs = len(fpaths)

    # load previously calculated features
    corr_rgb = pd.read_csv('corr_rgb.csv')
    df = corr_rgb

    # load additional features...
    # df = pd.merge(corr_rgb, ...)

    X = df.filter(regex='corr_').values
    Y = df.category.values

    # shuffle dataset
    XY = zip(X, Y)
    np.random.seed(0)
    np.random.shuffle(XY)
    X, Y = zip(*XY)
    X = np.array(X)
    Y = np.array(Y)

    # initialize RFC
    clf = RandomForestClassifier(n_estimators=20)

    # train and evaluate, with cross validation
    kf = cross_validation.KFold(nimgs, 10)
    scores = []
    for train_ix, test_ix in kf:
        train_x = X[train_ix]
        train_y = Y[train_ix]
        clf.fit(train_x, train_y)

        test_x = X[test_ix]
        test_y = Y[test_ix]
        Y_hat = clf.predict(test_x)

        scores.append(accuracy_score(test_y, Y_hat))

    print 'Mean accuracy score: %.4f +/- %.4f %%' % (100*np.mean(scores), 100*np.std(scores))
    print 'Accuracy with random guessing: %.4f %%' % (100./ncategories)

