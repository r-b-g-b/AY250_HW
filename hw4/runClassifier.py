import numpy as np
from glob import glob
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score, KFold
import calcFeatures

basedir = '/Users/robert/Documents/Code/pythonwork/AY250/python-seminar/Homeworks/AY250_HW/hw4'
imgdir = os.path.join(basedir, '50_categories')

def run_final_classifier(imgdir):

    fpaths = glob(os.path.join(imgdir, '*.jpg'))
    for fpath in fpaths:
        hogs = calcFeatures.calc_hog(fpaths)
        power_hist = calcFeatures.calc_spatial_power_hist(fpaths)
        corr_rgb = calcFeatures.calc_corr_rgb(fpaths)


def run(load_precomputed=True):

    '''
    Load the computed features (corr_rgb, power_hist, and HOG), compile them
    into a DataFrame, build and test the classifier with cross-validation
    '''

    categories = [os.path.split(i)[1] for i in glob(os.path.join(basedir, '50_categories', '*'))]
    ncategories = len(categories)

    fpaths = calcFeatures.get_fpaths(os.path.join(basedir, '50_categories'))

    df = pd.DataFrame()
    if load_precomputed:
        # load previously calculated features
        featpaths = glob('feat_*.csv')
        for featpath in featpaths:
            df = df.join(pd.read_csv(featpath, index_col=0), how='outer')
    else:
        df.join(map_hog(fpaths), how='outer')

    nimgs = len(df)
    X = df.filter(regex='feat_').values
    Y = df.category.values

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

