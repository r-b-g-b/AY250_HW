
import pymc
import pandas as pd

def calc_alpha_beta(mu=0.255, sigma2=0.011):
    '''
    For a desired mean and variance, calculate the
    alpha and beta parameters for the Beta distribution
    '''
    k = mu/(1-mu)
    beta = (k-(sigma2*((1+k)**2))) / (sigma2*((1+k)**3))
    alpha = k*beta
    return alpha, beta

# read the data
df = pd.read_csv('laa_2011_april.txt', sep='\t')
atbats = df.AB
hits_obs = df.H

# league batting average and variance
mu = 0.255
sigma2 = 0.011
alpha, beta = calc_alpha_beta(mu=mu, sigma2=sigma2)

# define batting average prior as a Beta distribution
avg = pymc.Beta('avg', alpha=alpha, beta=beta, size=len(df))
    
# likelihood
hits_pred = pymc.Binomial('hits_pred', n=atbats, p=avg, value=hits_obs, observed=True)