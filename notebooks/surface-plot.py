import pymc3 as pm
import numpy as np
import theano

from theano.compile.ops import as_op
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
plt.style.use("/home/daniel/papers/thesis/thesis-style.mpl")

import matplotlib
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

matplotlib.rc('font', **font)

def background_rate_f(b, T, n):
    """
    
    """
    out = 0
    #n = int(n)
    for i in range(n+1):
        out += ((b*T)**i * np.exp(- b*T)) / np.math.factorial(i)
    return out

def log_background_rate(b, T, n):
    return np.log(background_rate_f(b, T, n))

def signal_rate_part(s, n, b, T):
    top_a = T * ((s + b) * T)**n 
    top_b = np.exp(-(s + b)*T)
    p = (top_a * top_b) / np.math.factorial(n)
    return theano.tensor.switch(theano.tensor.le(s, 0), 0, p)

#@as_op(itypes=[T.dscalar, T.dscalar, T.dscalar, T.dscalar], otypes=[T.dscalar])
def log_signal_rate(s,n,b,T):
    #if theano.tensor.lt(0, s): return np.array([[0.0]])
    p = -log_background_rate(b,T,n) + np.log(signal_rate_part(s,n,b,T))
    return p

def number_mweg(volume):
    """
    Calculates the number of MWEGs in a volume, given in units of Mpc^3
    """
    return volume * (0.0116) 

import theano.tensor as T
from pymc3 import DensityDist, Uniform, Normal
from pymc3 import Model
from pymc3 import distributions

def grb_model(number_events, background_rate, 
              observation_time, horizon, grb_rate,
             efficiency_prior = "uniform"):
    with Model() as model:
        signal_rate = pm.DensityDist('signal_rate', 
                            logp=lambda value: log_signal_rate(value, number_events, background_rate, observation_time),
                           testval=50)

        volume = (4.0 / 3.0) * np.pi * horizon**3
        print "volume: {}".format(volume)
        n_galaxy = number_mweg(volume)
    
        cbc_rate = pm.Deterministic('cbc_rate', signal_rate / n_galaxy)
        
        grb_rate = (grb_rate / number_mweg(1e9)) #/ n_galaxy


        
        # Allow the efficiency prior to be switched-out
        if efficiency_prior == "uniform":
            efficiency = pm.Uniform('efficiency', 0,1)
        elif efficiency_prior == "jeffreys":
            efficiency = pm.Beta('efficiency', 0.5, 0.5)
        elif isinstance(efficiency_prior, float):
            efficiency = efficiency_prior
        
        def cosangle(cbc_rate, efficiency, grb_rate):
            return T.switch((grb_rate >= cbc_rate*efficiency), -np.Inf, 
                                 (1.0 - ((grb_rate/(cbc_rate*efficiency)))))
        
        costheta = pm.Deterministic('cos_angle', cosangle(cbc_rate, efficiency, grb_rate))                            

        angle = pm.Deterministic("angle", theano.tensor.arccos(costheta))
        
        return model

horizon_int = 10 #200
events_max = 20

# make a plot of the beaming angle as a function of observation volume against number of detections
# O1 Scenarios
scenarios = []
for events in range(events_max):
    for horizon in np.linspace(10, 1000, horizon_int):

        #print "Horizon: {}\t Events: {}".format(horizon, events)
        
        number_events = events # There were no BNS detections in O1
        background_rate = 0.01 # We take the FAR to be 1/100 yr
        observation_time = 1.  # Years
        grb_rate = 10.0
        o1_models = []
        #for prior in priors:
        scenarios.append( grb_model(number_events, background_rate, observation_time, horizon, grb_rate, efficiency_prior='jeffreys'))


traces = []
angles975 = []
angles025 = []
angles500 = []
uppers = []
lowers = []
samples = 100000
for model in scenarios:
    with model:
        step = pm.Metropolis()
        trace = pm.sample(samples, step, )
        #trace = pm.sample(samples, step, )
        traces.append(trace)
        t_data = trace[10000:]['angle'][np.isfinite(trace[10000:]['angle'])]
        try:
            lower, upper = pm.stats.hpd(t_data, alpha=0.05, transform=np.rad2deg)
        except ValueError:
            lower, upper = np.nan, np.nan
            print "There weren't enough samples."
            #angles975.append(np.nanpercentile(trace['angle'][10000:], 97.5))
        #angles025.append(np.nanpercentile(trace['angle'][10000:], 2.5))
        angles500.append(np.nanpercentile(trace['angle'][10000:], 50))
        lowers.append(lower)
        uppers.append(upper)
        np.savetxt("upper.dat", uppers)
        np.savetxt("lower.dat", lowers)
        np.savetxt("500perc.dat", angles500)

np.savetxt("upper.dat", uppers)
np.savetxt("lower.dat", lowers)
np.savetxt("975perc", angles975)
np.savetxt("500perc", angles500)
np.savetxt("025perc", angles025)
