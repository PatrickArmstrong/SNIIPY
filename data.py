from copy import deepcopy
from matplotlib import pyplot as plt


class Data(object):

    def __init__(self, fName, fKey=None, name=None, mag=True):
        self.fName = fName
        self.mag = mag
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
        self._plot(upper=True)

    def _csv_load(self):
        from astropy.io.ascii import read
        d = read(self.fName, format='csv')
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

    def _plot(self, upper=True):
        plt.close()
        for filt in self.data['obs']:
            x = self.data['obs'][filt]['time']
            if self.mag:
                y = self.data['obs'][filt]['mag']
                dy = self.data['obs'][filt]['emag']
            else:
                y = self.data['obs'][filt]['flux']
                dy = self.data['obs'][filt]['eflux']
            plt.errorbar(x, y, yerr=dy, linestyle="None")
            plt.scatter(x, y, label=filt)
        if upper:
            for filt in self.data['upp']:
                x = self.data['upp'][filt]['time']
                if self.mag:
                    y = self.data['upp'][filt]['mag']
                    dy = self.data['upp'][filt]['emag']
                else:
                    y = self.data['upp'][filt]['flux']
                    dy = self.data['upp'][filt]['eflux']
                plt.errorbar(x, y, yerr=dy, linestyle="None")
                plt.scatter(x, y, marker='*')
        if self.mag:
            plt.gca().invert_yaxis()
        plt.legend()
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
