import numpy as np


class Model(object):

    def __init__(self, object, filt):
        if filt not in object.data['obs']:
            print("Unknown filter: %s, available filters are: %s" %
                  (filt, object.data['obs'].keys()))
            return None
        self.object = object
        self.filt = filt
        self.ndim = 0

        def prior(self, param):
            return 1

        def model(self, x, param):
            return None


class Peak(Model):

    def __init__(self, object, filt):
        super().__init__(object, filt)
        self.ndim = 6

    def prior(self, param):
        # peak, zpx, zpy, a1, a2, b2 = param
        # if zpx >= peak:
        #     return -np.inf
        # obs = self.object.data['obs'][self.filt]['time']
        # if peak >= max(obs) or peak <= min(obs):
        #     return -np.inf
        # maxx = min(obs)
        # if zpx > maxx:
        #     return -np.inf
        # if self.filt in self.object.data['upp']:
        #     upp = self.object.data['upp'][self.filt]['time']
        #     minx = max([i for i in upp if i < maxx])
        #     if zpx < minx:
        #         return -np.inf
        return 1.

    def model(self, x, param):
        peak, zpx, zpy, a1, a2, b2 = param
        b1 = b2 - a1 * peak + a2 * peak
        c = -b1 * zpx - a1 * zpx * zpx + zpy
        if x <= peak:
            return a1 * x * x + b1 * x + c
        else:
            return a2 * x * x + b2 * x + c
