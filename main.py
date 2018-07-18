from object import *
from fitter import *
from model import *

fitters = {'MCMC': MCMCFitter}
models = {'peak': Peak, 'rad': Radiation}


class Main(object):

    def __init__(self, fName, filt, fitter='MCMC', model='peak', residual=None, fKey=None, name=None, mag=True, col=None):
        self.object = Data(fName, fKey=fKey, name=name, mag=mag, col=col)
        self.filt = filt
        if fitter in fitters:
            fitter = fitters[fitter]
        else:
            print("Unknown fitting technique: %s" % fitter)
        if model in models:
            f = models[model]
            self.model = f(self.object, filt)

            self.fitter = fitter(self.model, residual=residual, mag=mag)
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
        self.fitter.fit(x, y, self.model.ndim, dy=dy, args=args,
                        nwalkers=nwalkers, burnphase=burnphase, runphase=runphase, p0=p0)
        return self.fitter.param, self.fitter.paramErr

    def plot(self, upper=True, show=True, err=True, spec={}, xoff=0, yoff=0, xstretch=1, ystretch=1):
        self.object._plot(upper=upper, show=show, err=err, spec=spec,
                          xoff=xoff, yoff=yoff, xstretch=xstretch, ystretch=ystretch)

    def __getitem__(self, key):
        if key in self.object.data:
            return self.object.data[key]
        elif key in self.object.data['obs']:
            return self.object.data['obs'][key]
        else:
            rtn = {}
            for filt in self.object.data['obs']:
                if key in self.object.data['obs'][filt]:
                    rtn[filt] = self.object.data['obs'][filt][key]
        if rtn != {}:
            return rtn
