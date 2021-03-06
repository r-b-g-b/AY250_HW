# Markov Chain Monte Carlo (MCMC) using pymc
## The problem
Given batting statistics for one month of the season, compute an estimate of the player's batting average.

## The solution
Run a MCMC to simulate many samples for each player. Characterize the resulting distribution by calculating the mean and 95% confidence interval. To validate, compare the result to actual performance for the entire season

## How to run
### IPython notebook
The simplest way to run/visualize the data is to simply load the IPython notebook, hw11.ipynb. From the terminal, navigate to the directory /hw11 and run
> ipython notebook

Select "hw11" from the notebook list and advance through using `Shift+Enter`

### .py python script
If you'd like to run it as a .py python script, you should start up IPython from the terminal by typing
> ipthon --pylab

From the python prompt, type
> run hw11.py

The text and figure outputs will answer all of your questions.
