'''Sampling script. Uses pymc3 to fit demand data.
I used a stochastic volatility model, but other methods exist.
Uncomment lines to plot.'''

import pymc3 as pm
import numpy as np
# import matplotlib.pyplot as plt
# plt.style.use('ggplot')


def sample_pymc(s, slot_objects_list):
    ''' Inputs:
            s                   :: int, scenario number
            slot_objects_list   :: list of Slot objects.
    Returns: 
        demands[0]              :: sample demand
        leave_samples           :: realisations for leaving glovers
        np.random.uniform(0, 1) :: probability associated with scenario s.'''
    y = [float(slot.demand) for slot in slot_objects_list]
    size = len(y)
    x = range(size)
    with pm.Model() as model:
        nu = pm.Exponential('nu', 1/10., testval=5.)
        sigma = pm.Exponential('sigma', 1/0.02, testval=.1)
        s = pm.GaussianRandomWalk('s', sd=sigma, shape=size)
        volatility_process = pm.Deterministic(
            'volatility_process', pm.math.exp(-2*s)**0.5)
        r = pm.StudentT('r', nu=nu, sd=volatility_process, observed=y)
    with model:
        trace = pm.sample(size)
    # demand_var = 1/np.exp(trace['s', ::5].T)
    sliced_trace = trace[size-1:]
    demands = 1/np.exp(sliced_trace.get_values('s', chains=1))
    leave_samples = [np.random.binomial(1, slot.leave)
                     for slot in slot_objects_list]
    # plt.scatter(x, y, label='Data')
    # # plt.plot(x, demand_var, 'C3', alpha=.03)
    # plt.scatter(x, demands, label='Sample')
    # plt.title("MCMC Sample with variance")
    # plt.legend()
    # plt.savefig('./output/demand_sample.eps', dpi=300,
    #             papertype='a4', format='eps')
    return demands[0], leave_samples, np.random.uniform(0, 1)
