# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:05:42 2014

@author: Alison Kirkby

Modelling random resistor networks using python.

"""

import numpy as np
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import os
import string
import resistornetworkfunctions as rnf 

class Plot_network():
    """
    plot the results of a model using plt.quiver
    """
    
    def __init__(self, Resistivity_volume, **input_parameters):
        
        self.Resistivity_volume = Resistivity_volume
        self.cmap = dict(fluid='jet', current='jet',
                         permeability='gray',resistance='gray')
        self.clim = dict(fluid=[5.,95.], current=[1.,99.],
#                         permeability=[0.,100.],resistance=[0.,100.],
                         limit_type = 'percent')
        self.plot_range = dict(fluid=[0,100], current=[0,100],
                               permeability = [0,100], resistance = [0,100])
        self.plot_arrowheads = False
        self.arrow_dict = {'widthscale':0.2}
        self.parameters = 'all'
        self.plot_tf = True
    
        update_dict = {}

        #correcting dictionary for upper case keys
        input_parameters_nocase = {}
        for key in input_parameters.keys():
            input_parameters_nocase[key.lower()] = input_parameters[key]

        update_dict.update(input_parameters_nocase)

        for key in update_dict.keys():
            try:
                value = getattr(self,key)
                if type(value) == dict:
                    try:
                        newdict = update_dict[key]
                        for key2 in newdict.keys():
                            try:
                                value[key2] = newdict[key2]
                            except:
                                pass
                    except:
                        pass
                setattr(self,key,value)
            except:
                pass
        
        self.initialise_parameter_arrays()
        if self.plot_range['permeability'] == []:
            k = self.Resistivity_volume.permeability
            self.plot_range['permeability'] = [1.1*np.amin(k[np.isfinite(k)]),
                                               1.1*np.amax(k[np.isfinite(k)])]
        if self.plot_range['resistance'] == []:
            r = self.Resistivity_volume.resistance
            self.plot_range['resistance'] = [0.9*np.amin(r[np.isfinite(r)]),
                                             0.9*np.amax(r[np.isfinite(r)])]
        
        if self.plot_tf:
            self.initialise_plot_parameters()
            self.plot()



    
    def _set_axis_params(self):
        """
        
        """
        
    def initialise_parameter_arrays(self):

        RV = self.Resistivity_volume
        allowed_params = ['resistance','current','permeability','fluid']

        if type(self.parameters) == str:      
            self.parameters = [self.parameters]
        if type(self.parameters) == list:
            tmplist = []
            for p in allowed_params:
                if p in self.parameters:
                    tmplist.append(p)
            self.parameters = tmplist

        else:
            self.parameters = 'all'
        if self.parameters == []:
            print "invalid parameters list, plotting all parameters"
            self.parameters = 'all'
        if self.parameters == 'all':
            self.parameters = allowed_params
            
        parameter_arrays = {}    
        for p in self.parameters:
            if p == 'fluid':
                parameter_arrays['fluid'] = [RV.flowrate[:,:,:,i] for i in [0,1]]
            elif p == 'current':
                parameter_arrays['current'] = [RV.current[:,:,:,i] for i in [0,1]]              
            elif p == 'resistance':
                parameter_arrays[p] = [RV.resistance]
            elif p == 'permeability':
                parameter_arrays[p] = [RV.permeability]
            
        self.parameter_arrays = parameter_arrays
        
        
    def initialise_plot_parameters(self):
        
        self.plot_xzuwc = {}
        RV = self.Resistivity_volume      
        plotxz = rnf.get_meshlocations([RV.dx,RV.dz],
                                       [RV.nx,RV.nz])
        n_subplots = 0
        
        for key in self.parameter_arrays.keys():
            self.plot_xzuwc[key] = []
            value_list = self.parameter_arrays[key]
            for value in value_list:
                X,Z = rnf.get_quiver_origins([RV.dx,RV.dz],
                                                 plotxz,
                                                 value)
                print self.plot_range[key]
                U,W,C = rnf.get_quiver_UW(value,self.plot_range[key])

                self.plot_xzuwc[key].append([X,Z,U,W,C])
                n_subplots += 1
        self.n_subplots = n_subplots
                
    def plot(self):
        """
        
        """
        
        if not hasattr(self,'plot_xzuwc'):
            self.initialise_plot_parameters()
        
        if self.plot_arrowheads:
            hw,hl,hal = 1,2,1.5
        else:
            hw,hl,hal = 0,0,0
        
        RV = self.Resistivity_volume 
        w = min((RV.nx,RV.nz))
            
        sp = 1
        if self.n_subplots < 4:
            sx,sy = 1,self.n_subplots
        elif self.n_subplots == 4:
            sx,sy = 2,2
        elif self.n_subplots <= 6:
            sx,sy = 2,3
        
        for key in self.parameters:
            for X,Z,U,W,C in self.plot_xzuwc[key]:
                print U,W,C
                
#                if key in self.clim.keys():
#                    clim = True
#                    if self.clim['limit_type'] == 'percent':
#                        UW = np.hstack([cc.flatten() for cc in C])
#                        print(UW)
#    #                    print UW,self.clim[key]
#                        clim = np.percentile(UW,self.clim[key][0],
#                                             UW,self.clim[key][1])
#                    else:
#                        clim = self.clim[key]
#                    
#                else:
#                    clim = False

                ax = plt.subplot(sx,sy,sp)
                for i in range(2):
                    plt.quiver(X,Z,U[i],W[i],C[i],
                               scale=RV.dx*(RV.nx+2),
                               width=self.arrow_dict['widthscale']/w,
                               cmap=self.cmap[key],
                               headwidth=hw,
                               headlength=hl,
                               headaxislength=hal)
#                if clim:
#                    plt.clim(clim)
                ax.set_aspect('equal')
                sp += 1