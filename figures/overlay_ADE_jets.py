#!/usr/bin/env python
# Copyright (C) 2015-2016 James Clark <james.clark@physics.gatech.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
import cPickle as pickle
import numpy as np
from matplotlib import pyplot as pl
import grbeams_utils

pl.style.use('/home/daniel/repositories/burst-style/burst.mplstyle')

resultsfiles = sys.argv[1].split('|')
epoch=sys.argv[2]
rate=sys.argv[3]
if len(sys.argv)==5: injvalue=float(sys.argv[4])
else: injvalue=None

f, ax = pl.subplots()

if len(resultsfiles)==4:
    labels=[r"\delta(0.5)", r"\delta(1.0)", r"U(0,1)", r"\beta(\frac{1}{2},\frac{1}{2})"]
if len(resultsfiles)==3:
    labels=[r"\delta(0.5)", r"U(0,1)", r"\beta(0,1)"]

linestyles=['-', '--', ':', '-.']

for r,result in enumerate(resultsfiles):

    data = pickle.load(open(result,'rb'))

    #theta_bin_size = 3.5*data.stdev / len(data.samples)**(1./3)
    #theta_bins = np.arange(data.samples.min(), data.samples.max(),
    #        theta_bin_size)
    #theta_bin_size = 1
    #theta_bins = np.arange(0, 90+theta_bin_size, theta_bin_size)

    theta_bw = 1.06*data.stdev*\
            len(data.samples)**(-1./5)

    theta_grid = np.arange(0, 90, 0.1)

    theta_pdf = grbeams_utils.kde_sklearn(data.samples, theta_grid,
            bandwidth=theta_bw)

    intervals = data.prob_interval([0.9])
    LL = np.percentile(data.samples, 10) 
    #mode = theta_grid[np.argmin(abs((np.diff(theta_pdf)/np.diff(theta_grid))))]
    mode = theta_grid[np.argmax(theta_pdf)]


    if r==2: linewidth=2 
    else: linewidth=1 
    #    ax.hist(data.samples, bins=theta_bins, normed=True, histtype='stepfilled', 
    #            alpha=0.5) 
    #labelstr=r'$p(\theta|I)=%s$, $\langle \theta_{\rm jet} \rangle_{1/2}=%.2f^{+%.2f}_{-%.2f}$'%(\
    #        labels[r], data.median, intervals[0][1]-data.median,
    #        data.median-intervals[0][0])
    labelstr=r'$p(\epsilon|I)=%s$, $\theta_{\rm jet}^{\rm MAP}=%.2f^{+%.2f}_{-%.2f}$'%(\
            labels[r], mode, intervals[0][1]-mode,
            mode-intervals[0][0])
    #labelstr=r'$p(\theta|I)=%s$, lower limmit=%.2f'%(labels[r], LL)

    ax.semilogy(theta_grid, theta_pdf, color='k', linestyle=linestyles[r],
            linewidth=linewidth, label=labelstr)

#    ax.axvline(intervals[0][0], color='k', linestyle=linestyles[r])
#    ax.axvline(intervals[0][1], color='k', linestyle=linestyles[r])
#    ax.axvline(data.median, color='k', linestyle=linestyles[r])
#    ax.axvline(mode, color='k', linestyle=linestyles[r])
#    ax.axvline(LL, color='k', linestyle=linestyles[r])

if injvalue is not None:
    ax.axvline(injvalue, label="`True' value", color='r')

if injvalue is None:
    ax.set_xlim(0,30)
ax.set_ylim(1e-3,1)
ax.legend()
ax.minorticks_on()

ax.set_xlabel(r'Jet Angle, $\theta_{\rm jet}$ [deg]')
ax.set_ylabel(r'$p(\theta|D,I)$')
f.tight_layout()

#sys.exit()

if result.find('sim') > -1:
    pl.savefig('jet_angle_posterior_aligo_%s_%s.eps'%(epoch,rate))
#    pl.savefig('jet_angle_posterior_aligo_%s_%s.png'%(epoch,rate))
#    pl.savefig('jet_angle_posterior_aligo_%s_%s.pdf'%(epoch,rate))
else:
    pl.savefig('jet_angle_posterior_aligo_%s_%s_real.eps'%(epoch,rate))
#    pl.savefig('jet_angle_posterior_aligo_%s_%s_real.png'%(epoch,rate))
#    pl.savefig('jet_angle_posterior_aligo_%s_%s_real.pdf'%(epoch,rate))

#pl.show()



