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

        def reset(self):
            return None

        def prior(self, param):
            return 1

        def model(self, t, param):
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

    def reset(self):
        return None

    def model(self, t, param):
        peak, zpx, zpy, a1, a2, b2 = param
        b1 = b2 - a1 * peak + a2 * peak
        c = -b1 * zpx - a1 * zpx * zpx + zpy
        if t <= peak:
            return a1 * t ** 2. + b1 * t + c
        else:
            return a2 * t ** 2. + b2 * t + c


class Radiation(Model):

    def __init__(self, object, filt):
        super().__init__(object, filt)
        self.lim = [0]
        self.val3 = [0]
        self.val4 = [0]
        self.ndim = 8

    def prior(self, param):
        return 1

    def reset(self):
        self.lim = [0]
        self.val3 = [0]
        self.val4 = [0]

    def model(self, t, param):
        from scipy.integrate import quad
        M, v, A, R0, t0, d, dt, m0 = param
        if t <= dt:
            return m0
        M = M * 1.989 * 10**30
        td = (((R0 * t0) / v) ** 0.5) / (120 * 3 ** 0.5)
        eNi = 3.9 * 10 ** 13
        eCo = 6.8 * 10 ** 12
        tNi = 8.8
        tCo = 111.3

        def integral(tp, rad):
            return ((R0 / (v * td * 86400)) + (tp / td)) * np.exp((tp ** 2. / td ** 2.) +
                                                                  ((2 * R0 * tp) / (86400 * v * td ** 2.))) * np.exp(-tp / rad)
        step1 = (2 * M / (td * 86400))
        if np.isinf(step1) or np.isnan(step1):
            return -np.inf
        step2 = np.exp(-(((t - dt) ** 2. / td ** 2.) +
                         ((2. * R0 * (t - dt)) / (86400. * v * td ** 2.))))
        if np.isinf(step2) or np.isnan(step2):
            return -np.inf
        step3 = quad(integral, self.lim[-1],
                     t - dt, args=(tNi,))[0] + self.val3[-1]
        # step3 = (eNi - eCo) * quad(integral, 0, t - dt, args=(tNi,))[0]
        if np.isinf(step3) or np.isnan(step3):
            return -np.inf
        self.val3.append(step3)
        step3 = (eNi - eCo) * step3
        step4 = quad(integral, self.lim[-1],
                     t - dt, args=(tCo,))[0] + self.val4[-1]
        # step4 = eCo * quad(integral, 0, t - dt, args=(tCo,))[0]
        if np.isinf(step4) or np.isnan(step4):
            return -np.inf
        # print(t - dt, stmep3, step4)
        self.val4.append(step4)
        self.lim.append(t - dt)
        step4 = eCo * step4
        step5 = 1 - np.exp(-A * (t - dt) ** -2.)
        if np.isinf(step5) or np.isnan(step5):
            return -np.inf
        if self.object.mag:
            return m0 - 2.5 * np.log10(abs(step1 * step2 * (step3 + step4) * step5 / (4 * np.pi * d)))
        return step1 * step2 * (step3 + step4) * step5
