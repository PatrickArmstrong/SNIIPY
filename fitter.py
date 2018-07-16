import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import emcee


class Fitter(object):

    def __init__(self, func, residual=None, mag=True):
        '''
        Parent Fitting Class

        Inputs:
        func (function):
            The function being fit to the data. Must be of the form f(x, param), param is a list of the values to be fit.
        residual (function, optional):
            A function to be minimized to fit func to the data. Must be of the form f(param, func, x, y, *args) where args are additional arguments that can be passed such as uncertainty. Will default to chi squared if no residual is given.
        '''

        self.func = func
        self.mag = mag
        if residual is None:
            residual = chi_squared
        self.residual = residual

    def plot(self):
        '''
        Plot the best fit model against the original data. Note that this will not work without first peforming a fit.
        '''
        fx = np.linspace(min(self.x), max(self.x))
        fy = [self.func(i, self.param) for i in fx]
        plt.plot(fx, fy, zorder=10)
        plt.scatter(self.x, self.y, zorder=10)
        plt.errorbar(self.x, self.y, yerr=self.dy, linestyle="None", zorder=15)
        if self.mag:
            plt.gca().invert_yaxis()
        plt.show()


class MCMCFitter(Fitter):

    def __init__(self, func, residual=None, mag=True):
        super().__init__(func, residual=residual, mag=mag)

    def fit(self, x, y, ndim, dy=None, args=None, nwalkers=150, burnphase=400, runphase=1000, p0=None):
        '''
        Fitting function which minimises the given residual function.

        Inputs:
        x (Iterable):
            The x data to be fit to.
        y (Iterable):
            The y data to be fit to.
        ndim (int):
            The number of parameters to be find
        dx (Iterable, optional):
            Uncertainty in x data, defaults to 10% error
        dy (Iterable, optional):
            Uncertainty in y data, defaults to 10% error
        args (list, optional):
            Additional arguments to be passed to the residual function
        nwalkers (int, optional):
            The number of seperate 'walkers' assigned to each parameter. More walkers tend to give a better fit but take longer.
        burnphase (int, optional):
            The length of the initial burn in phase
        runphase (int, optional):
            The length of the MCMC fitting phase
        p0 (Iterable, optional):
            A list of best guess initial parameters, must be of size [ndim : nwalkers]. Defaults to random numbers between 0 and 1.
        '''

        self.x = x
        self.y = y
        if dy is None:
            dy = [i * 0.1 for i in self.y]
        self.dy = dy
        if args is None:
            args = [dy]
        self.ndim = ndim
        self.nwalkers = nwalkers
        self.burnphase = burnphase
        self.runphase = runphase
        if p0 is None:
            p0 = [np.random.rand(ndim) * 0.01
                  for i in range(nwalkers)]
        else:
            p0 = [np.array(p0) * np.random.rand()
                  for i in range(nwalkers)]
        self.sampler = emcee.EnsembleSampler(
            nwalkers, ndim, self.residual, a=3.0, args=[self.func, x, y] + args)
        # Run a burn-in.
        print("Burning-in ...")
        pos, prob, state = self.sampler.run_mcmc(p0, self.burnphase)

        # Reset the chain to remove the burn-in samples.
        self.sampler.reset()

        # Starting from the final position in the burn-in chain, sample for 1500
        # steps. (rstate0 is the state of the internal random number generator)
        print("Running MCMC ...")
        pos, prob, state = self.sampler.run_mcmc(
            pos, self.runphase, rstate0=state)

        # Print out the mean acceptance fraction.
        af = self.sampler.acceptance_fraction
        print("Mean acceptance fraction: %s" % np.mean(af))

        # Get the index with the highest probability
        maxprob_index = np.argmax(prob)

        # Get the best parameters and their respective errors
        self.param = pos[maxprob_index]
        self.paramErr = [self.sampler.flatchain[:, i].std()
                         for i in range(ndim)]
        self.plot_samples_hist()
        self.plot()

    def plot_samples_hist(self):
        '''
        Plots the sampling history of each parameter. Useful to see how well MCMC fit the given parameter.
        '''

        samples = [self.sampler.flatchain[:, i] for i in range(self.ndim)]

        for i, sample in enumerate(samples):
            plt.hist(sample, 150)
            plt.title("Sample of parameter Nr %i" % i)
            plt.show()


def chi_squared(param, fitfunc, x, y, e):
    '''
    Default residual function to be minimised.

    Input:
    param (Iterable):
        The parameters of the function being fit
    fitfunc (function):
        The function being fit to the data
    x (Iterable):
        The x data to be fit to.
    y (Iterable):
        The y data to be fit to.
    e (Iterable):
        The combined uncertainty of each (x, y) data point.
    '''

    return -0.5 * sum([((fitfunc(x[i], param) - y[i]) ** 2.) / (e[i] ** 2.) for i in range(len(x))])
