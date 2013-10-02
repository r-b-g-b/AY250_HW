import numpy as np
from glob import glob
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score, KFold
from sklearn.grid_search import GridSearchCV
import calcFeatures; reload(calcFeatures)
import pickle

basedir = '/Users/robert/Documents/Code/pythonwork/AY250/python-seminar/Homeworks/AY250_HW/hw4'
imgdir = os.path.join(basedir, '50_categories')

def run_final_classifier(testimgdir):


    f = open('model.p')
    clf = pickle.load(f)
    f.close()

    fpaths = glob(os.path.join(testimgdir, '*.jpg'))
    fpaths = fpaths[:30]
    hogs = calcFeatures.calc_hog(fpaths, save=False)
    power_hist = calcFeatures.calc_spatial_power_hist(fpaths, save=False)
    corr_rgb = calcFeatures.run_rgb_corr(fpaths, save=False)
    df = pd.DataFrame()
    df = df.join(hogs, how='outer')
    df = df.join(power_hist, how='outer')
    df = df.join(corr_rgb, how='outer')

    X = df.filter(regex='feat_').values

    Y_hat = clf.predict(X)
    print '%25s | %-20s' % ('filename', 'predicted_class')
    print '-'*50
    for fpath, y_hat in zip(df.index, Y_hat):
        print '%25s | %-20s' % (fpath, y_hat)

def load_features():
    
    df = pd.DataFrame()

    featpaths = glob('feat_*.csv')
    for i, featpath in enumerate(featpaths):
        print 'Loading %u of %u features: %s' % (i, len(featpaths), featpath)
        df = df.join(pd.read_csv(featpath, index_col=0), how='outer')
    return df

def compute_features():

    df = pd.DataFrame()

    df = df.join(calcFeatures.run_rgb_corr(fpaths, save=False), how='outer')
    df = df.join(calcFeatures.calc_hog(fpaths, save=False), how='outer')
    df = df.join(calcFeatures.calc_spatial_power_hist(fpaths, save=False), how='outer')

    return df

def train(load_precomputed=True):

    '''
    Load the computed features (corr_rgb, power_hist, and HOG), compile them
    into a DataFrame, build and test the classifier with cross-validation
    '''

    categories = [os.path.split(i)[1] for i in glob(os.path.join(basedir, '50_categories', '*'))]
    ncategories = len(categories)

    fpaths = calcFeatures.get_fpaths(os.path.join(basedir, '50_categories'))

    if load_precomputed:
        # load previously calculated features
        df = load_features()
    else:
        df = compute_features()

    df['category'] = [i.split('_')[0] for i in df.index]

    nimgs = len(df)
    feat_df = df.filter(regex='feat_')
    X = feat_df.values
    Y = df.category.values

    # shuffle dataset
    XY = zip(X, Y)
    np.random.seed(0)
    np.random.shuffle(XY)
    X, Y = zip(*XY)
    X = np.array(X)
    Y = np.array(Y)

    # initialize RFC
    # print 'Running grid search on parameters.'
    # parameters = {'n_estimators':[20,50,100],  'max_features':[8,10]}
    # clf = GridSearchCV(RandomForestClassifier(), param_grid=parameters, cv=5, refit=True)
    clf = RandomForestClassifier(n_estimators=50)

    # train and evaluate, with cross validation
    scores = cross_val_score(clf, X, Y, cv=KFold(n=nimgs, n_folds=5))

    print 'Fitting the model.'
    # fit the model
    clf.fit(X, Y)

    print 'Mean accuracy score: %.4f +/- %.4f %%' % (100*np.mean(scores), 100*np.std(scores))
    print 'Accuracy with random guessing: %.4f %%' % (100./ncategories)

    # find the 3 most important features
    top3_features_ix = clf.feature_importances_.argsort()[::-1][:3]
    top3_features_importances = clf.feature_importances_[top3_features_ix]
    top3_features = feat_df.columns[top3_features_ix]

    print '%11s %-12s %s' % ('', 'name', 'importance')
    print ' '*8+'-'*40
    for i, (feat_name, feat_imp) in enumerate(zip(top3_features, top3_features_importances)):
        print '%10u. %s  %-.7f' % (i+1, feat_name, feat_imp)


    print 'Saving the model.'
    # save the model to a pickle
    f = open('model.p', 'w')
    pickle.dump(clf, f)
    f.close()


