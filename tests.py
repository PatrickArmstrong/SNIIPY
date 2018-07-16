from fitter import *
import collections


class MCMCPolynomial(object):

    def __init__(self, deg):
        self.deg = deg + 1
        self.func = self.polyFunc()
        self.x = np.linspace(-100., 100.)
        self.param = [i * np.random.choice([-1, 1])
                      for i in np.random.rand(deg + 1) * 10.]
        self.y = [i + (i * 0.1 * np.random.choice([-1, 1]))
                  for i in self.func(self.x, self.param)]

    def polyFunc(self):
        def poly(x, param):
            if isinstance(x, collections.Iterable):
                dy = [0 for i in range(len(x))]
            else:
                dy = 0
            for i in range(self.deg):
                if isinstance(x, collections.Iterable):
                    for j in range(len(x)):
                        dy[j] += param[i] * (x[j] ** i)
                else:
                    dy += param[i] * (x ** i)
            return dy
        return poly

    def fit(self):
        print(self.param)
        self.mcmcFit = MCMCFitter(self.func, residual=None)
        self.mcmcFit.fit(self.x, self.y, self.deg)
        print((self.mcmcFit.param, self.mcmcFit.paramErr))
        print([self.mcmcFit.param[i] / self.param[i] for i in range(self.deg)])
        self.mcmcFit.plot_samples_hist()
        self.mcmcFit.plot()
