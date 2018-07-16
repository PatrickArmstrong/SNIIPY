from data import *
from fitter import *
from model import *

fitters = {'MCMC': MCMCFitter}
models = {'peak': Peak}


class Main(object):

    def __init__(self, fName, filt, fitter='MCMC', model='peak', residual=None, fKey=None, name=None, mag=True):
        self.object = Data(fName, fKey=fKey, name=name, mag=mag)
        self.filt = filt
        if fitter in fitters:
            fitter = fitters[fitter]
        else:
            print("Unknown fitting technique: %s" % fitter)
        if model in models:
            f = models[model]
            self.model = f(self.object, filt)

            def fit(x, param):
                return self.model.prior(param) * self.model.model(x, param)
            self.fitter = fitter(fit, residual=residual, mag=mag)
        else:
            print("Unknown model: %s" % model)

    def doFit(self, nwalkers=150, burnphase=400, runphase=1000, p0=None, args=None):
        x = self.object.data['obs'][self.filt]['time']
        if self.object.mag:
            y = self.object.data['obs'][self.filt]['mag']
            dy = self.object.data['obs'][self.filt]['emag']
            if len(dy) == 0:
                dy = None
        else:
            y = self.object.data['obs'][self.filt]['flux']
            dy = self.object.data['obs'][self.filt]['eflux']
            if len(dy) == 0:
                dy = None
        self.fitter.fit(x, y, self.model.ndim, dy=None, args=args,
                        nwalkers=nwalkers, burnphase=burnphase, runphase=runphase, p0=p0)
        return self.fitter.param, self.fitter.paramErr
