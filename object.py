from copy import deepcopy
from matplotlib import pyplot as plt

dcol = {'g': 'b', 'r': 'g', 'i': 'gold', 'z': 'r'}
order = ['g', 'r', 'i', 'z']


class Data(object):

    def __init__(self, fName, fKey=None, name=None, mag=True, col=None):
        self.fName = fName
        self.mag = mag
        if col is None:
            col = dcol
        self.col = col
        if name == None:
            name = self.fName.split('.')[0]
        self.name = name
        if fKey is None:
            fKey = {'time': 'time', 'mag': 'mag', 'emag': 'emag', 'flux': 'flux',
                    'eflux': 'eflux', 'filt': 'filt', 'upperlimit': 'upperlimit', 'zp': 'zp', 'ezp': 'ezp', 'check': check}
        self.fKey = fKey
        self.data = {'obs': {}, 'upp': {}}
        self._blank = {'time': [], 'mag': [], 'emag': [], 'flux': [], 'eflux': [], 'zp': [], 'ezp': [
        ]}
        extension = fName.split('.')[-1]
        if extension == 'csv':
            self._csv_load()
        elif extension == 'fits':
            self._fits_load()
        for filt in self.data['obs']:
            for key in self.data['obs'][filt]:
                if key != 'time':
                    Y = self.data['obs'][filt]['time']
                    X = self.data['obs'][filt][key]
                    self.data['obs'][filt][key] = [
                        i for _, i in sorted(zip(Y, X))]
            self.data['obs'][filt]['time'] = sorted(
                self.data['obs'][filt]['time'])
        for filt in self.data['upp']:
            for key in self.data['upp'][filt]:
                if key != 'time':
                    Y = self.data['upp'][filt]['time']
                    X = self.data['upp'][filt][key]
                    self.data['upp'][filt][key] = [
                        i for _, i in sorted(zip(Y, X))]
            self.data['upp'][filt]['time'] = sorted(
                self.data['upp'][filt]['time'])
        self._plot(upper=True)

    def _csv_load(self):
        from astropy.io.ascii import read
        d = read(self.fName, format='csv')
        f = self.fKey['check']
        for i in d:
            filt = i[self.fKey['filt']].lower()
            det = f(i[self.fKey['upperlimit']])
            if det:
                det = 'upp'
            elif det is None:
                return None
            else:
                det = 'obs'
            if filt not in self.data[det]:
                self.data[det][filt] = deepcopy(self._blank)
            for key in self.fKey:
                if key in self._blank:
                    self.data[det][filt][key].append(i[self.fKey[key]])

    def _fits_load(self):
        from astropy.io.fits import getdata
        d = getdata(self.fName)
        f = self.fKey['check']
        for i in d:
            filt = i[self.fKey['filt']]
            det = f(i[self.fKey['upperlimit']])
            if det:
                det = 'upp'
            elif det is None:
                return None
            else:
                det = 'obs'
            if filt not in self.data[det]:
                self.data[det][filt] = deepcopy(self._blank)
            for key in self.fKey:
                if key in self._blank:
                    self.data[det][filt][key].append(i[self.fKey[key]])

    def _plot(self, upper=True, show=True, err=True, spec={}, xoff=0, yoff=0, xstretch=1, ystretch=1):
        if type(xoff) is dict:
            dxoff = xoff
        else:
            dxoff = None
        if type(yoff) is dict:
            dyoff = yoff
        else:
            dyoff = None
        if type(xstretch) is dict:
            dxstretch = xstretch
        else:
            dxstretch = None
        if type(ystretch) is dict:
            dystretch = ystretch
        else:
            dystretch = None
        for filt in order:
            if filt in self.data['obs']:
                spec['c'] = None
                if dxoff is not None:
                    xoff = dxoff[filt]
                if dyoff is not None:
                    yoff = dyoff[filt]
                if dxstretch is not None:
                    xstretch = dxstretch[filt]
                if dystretch is not None:
                    dystretch = dystretch[filt]
                if filt in self.col:
                    spec['c'] = self.col[filt]
                x = [i * xstretch + xoff for i in self.data['obs'][filt]['time']]
                if self.mag:
                    y = [i * ystretch + yoff for i in self.data['obs'][filt]['mag']]
                    dy = self.data['obs'][filt]['emag']
                else:
                    y = [i * ystretch + yoff for i in self.data['obs'][filt]['flux']]
                    dy = self.data['obs'][filt]['eflux']
                if err:
                    plt.errorbar(x, y, yerr=dy, linestyle="None", c=spec['c'])
                plt.scatter(x, y, label=filt, **spec)
        for filt in self.data['obs']:
            if filt not in order:
                spec['c'] = None
                if filt in self.col:
                    spec['c'] = self.col[filt]
                x = [i * xstretch + xoff for i in self.data['obs'][filt]['time']]
                if self.mag:
                    y = [i * ystretch + yoff for i in self.data['obs'][filt]['mag']]
                    dy = self.data['obs'][filt]['emag']
                else:
                    y = [i * ystretch + yoff for i in self.data['obs'][filt]['flux']]
                    dy = self.data['obs'][filt]['eflux']
                if err:
                    plt.errorbar(x, y, yerr=dy, linestyle="None", c=spec['c'])
                plt.scatter(x, y, label=filt, **spec)
        if upper:
            for filt in self.data['upp']:
                ux = [i * xstretch + xoff for i in self.data['upp'][filt]['time']]
                if self.mag:
                    uy = [i * ystretch +
                          yoff for i in self.data['upp'][filt]['mag']]
                    udy = self.data['upp'][filt]['emag']
                else:
                    uy = [i * ystretch +
                          yoff for i in self.data['upp'][filt]['flux']]
                    udy = self.data['upp'][filt]['eflux']
                if err:
                    plt.errorbar(ux, uy, yerr=udy,
                                 linestyle="None", c=spec['c'])
                plt.scatter(ux, uy, marker='*', **spec)
        if self.mag:
            plt.gca().invert_yaxis()
        plt.legend()
        plt.xlabel('MJD')
        if self.mag:
            plt.ylabel('Magnitude')
        else:
            plt.ylabel("Flux")
        if show:
            plt.show()


def fluxToMag(zp, flux):
    return zp - 2.5 * np.log10(flux)


def magToFlux(zp, mag):
    return 10. ** (-(zp + mag) / 2.5)


def check(x):
    if x == 'T':
        return True
    elif x == 'F':
        return False
    else:
        print("Error, unknown upperlimit: %s" % x)
        return None
