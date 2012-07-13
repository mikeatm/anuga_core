"""Simple water flow example using ANUGA

Will Powers example of a simple sinusoidal wave. 
"""

#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------

import sys
import anuga
from anuga import Domain

#from balanced_dev import *
#from balanced_dev import Domain as Domain

from math import cos
import numpy as num
from time import localtime, strftime, gmtime
from os import sep


#--------------------------------
# Get Default values for basic
# algorithm parameters.
#--------------------------------
from anuga.utilities.argparsing import parse_standard_args
alg, cfl = parse_standard_args()

#-------------------------------------------------------------------------------
# Copy scripts to time stamped output directory and capture screen
# output to file
#-------------------------------------------------------------------------------
time = strftime('%Y%m%d_%H%M%S',localtime())

output_dir = '.'
output_file = 'data_wave'

#copy_code_files(output_dir,__file__)
#start_screen_catcher(output_dir+sep)

interactive_visualisation = False

#------------------------------------------------------------------------------
# Setup domain
#------------------------------------------------------------------------------
dx = 500.
dy = dx
L = 100000.
W = 10*dx

# structured mesh
points, vertices, boundary = anuga.rectangular_cross(int(L/dx), int(W/dy), L, W, (0.0, -W/2))

domain = Domain(points, vertices, boundary) 

domain.set_name(output_file)                
domain.set_datadir(output_dir)  

#------------------------------------------------------------------------------
# Setup Algorithm, either using command line arguments
# or override manually yourself
#------------------------------------------------------------------------------
from anuga.utilities.argparsing import parse_standard_args
alg, cfl = parse_standard_args()
domain.set_flow_algorithm(alg)
domain.set_CFL(cfl)


#------------------------------------------------------------------------------
# Setup initial conditions
#------------------------------------------------------------------------------
domain.set_quantity('elevation',-100.0)
domain.set_quantity('friction', 0.00)
domain.set_quantity('stage', 0.0)            

#-----------------------------------------------------------------------------
# Setup boundary conditions
#------------------------------------------------------------------------------
from math import sin, pi, exp
Br = anuga.Reflective_boundary(domain)      # Solid reflective wall
Bt = anuga.Transmissive_boundary(domain)    # Continue all values on boundary
#Bz = swb2_boundary_conditions.zero_mass_flux_zero_momentum_boundary(domain) # Strong reflections
#Bz1 = swb2_boundary_conditions.zero_mass_flux_zero_t_transmissive_n_momentum_boundary(domain) # Strong reflections
#Bz2 = swb2_boundary_conditions.zero_mass_flux_zero_n_transmissive_t_momentum_boundary(domain) # Strong reflections
Bs = anuga.Transmissive_stage_zero_momentum_boundary(domain) # Strong reflections
Bd = anuga.Dirichlet_boundary([1,0.,0.]) # Constant boundary values
amplitude = 1
wave_length = 300.0
Bw = anuga.Time_boundary(domain=domain,     # Time dependent boundary
## Sine wave
                  f=lambda t: [(-amplitude*sin((1./wave_length)*t*2*pi)), 0.0, 0.0])
## Sawtooth?
#                   f=lambda t: [(-8.0*(sin((1./180.)*t*2*pi))+(1./2.)*sin((2./180.)*t*2*pi)+(1./3.)*sin((3./180.)*t*2*pi)), 0.0, 0.0])
## Sharp rise, linear fall
#                   f=lambda t: [(5.0*(-((t-0.)/300.)*(t<300.)-cos((t-300.)*2.*pi*(1./240.))*(t>=300. and t<420.)+(1.-(t-420.)/300.)*(t>=420. and t <720.))), 0.0, 0.0])
#                   f=lambda t: [amplitude*(1.-2.*(pi*(1./720.)*(t-720.))**2)/exp((pi*(1./720.)*(t-720.))**2) , 0.0, 0.0])
#                   f=lambda t: [(-8.0*sin((1./720.)*t*2*pi))*((t<720.)-0.5*(t<360.)), 0.0, 0.0])
def waveform(t):
    return -amplitude*sin((1./wave_length)*t*2*pi)

Bw2 = anuga.shallow_water.boundaries.Transmissive_n_momentum_zero_t_momentum_set_stage_boundary(domain, waveform)
#Bw3 = swb2_boundary_conditions.Transmissive_momentum_nudge_stage_boundary(domain, waveform)

def zero_fun(t):
    return 0.0                    
Bw0 = anuga.shallow_water.boundaries.Transmissive_n_momentum_zero_t_momentum_set_stage_boundary(domain, zero_fun)


# Associate boundary tags with boundary objects
domain.set_boundary({'left': Bw2, 'right': Bt, 'top': Br, 'bottom': Br})


#===============================================================================
if interactive_visualisation:
    from anuga.visualiser import RealtimeVisualiser
    vis = RealtimeVisualiser(domain)
    vis.render_quantity_height("stage", zScale =10000, dynamic=True)
    vis.colour_height_quantity('stage', (1.0, 0.5, 0.5))
    vis.start()
#===============================================================================


#------------------------------------------------------------------------------
# Evolve system through time
#------------------------------------------------------------------------------

for t in domain.evolve(yieldstep = 10.0, finaltime = 60*60.*3.):
    domain.write_time()
    if interactive_visualisation:
        vis.update()

if interactive_visualisation:
    vis.evolveFinished()

