''' Follows along with the pbfhr prt_pke
example however has been edited to use
temperature dependent models for density,
conductivity, convection, and viscosity

The simulation has 3 stages:
- initial temperature without feedback
- turn on feedback
- turn on external reactivity
'''

from pyrk.utilities.ur import units
from pyrk import th_component as th
import math
from pyrk.materials.material import Material
from pyrk.materials.liquid_material import LiquidMaterial
from pyrk.convective_model import ConvectiveModel
from pyrk.density_model import DensityModel
from pyrk.conductive_model import ConductiveModel
from pyrk.timer import Timer

#############################################
#
# User Workspace
#
#############################################

# Simulation parameters

# Initial time
t0 = 0.00 * units.seconds
# Timestep
dt = 0.02 * units.seconds
# Final Time
tf = 250.0 * units.seconds
# Time to turn on feedback
t_feedback = 150.0 * units.seconds

# Thermal hydraulic params
# Temperature feedbacks of reactivity
alpha_fuel = -3.19 * units.pcm / units.kelvin
alpha_mod = -0.7 * units.pcm / units.kelvin
alpha_shell = -0.7 * units.pcm / units.kelvin
alpha_cool = 0.23 * units.pcm / units.kelvin

# initial temperature
t_mod = (800 + 273.15) * units.kelvin
t_fuel = (800 + 273.15) * units.kelvin
t_shell = (770 + 273.15) * units.kelvin
t_cool = (650 + 273.15) * units.kelvin

kappa = 0.0


def area_sphere(r):
    assert(r >= 0 * units.meter)
    return (4.0) * math.pi * pow(r.to('meter'), 2)


def vol_sphere(r):
    assert(r >= 0 * units.meter)
    return (4. / 3.) * math.pi * pow(r.to('meter'), 3)


# volumes
n_pebbles = 470000
r_mod = 1.25 / 100.0 * units.meter
r_fuel = 1.4 / 100.0 * units.meter
r_shell = 1.5 / 100.0 * units.meter

vol_mod = vol_sphere(r_mod)
vol_fuel = vol_sphere(r_fuel) - vol_sphere(r_mod)
vol_shell = vol_sphere(r_shell) - vol_sphere(r_fuel)
vol_cool = (vol_mod + vol_fuel + vol_shell) * 0.4 / 0.6
a_pb = area_sphere(r_shell)


#############################################
#
# Required Input
#
#############################################

# Total power, Watts, thermal
power_tot = 234000000.0 * units.watt

# Timer instance, based on t0, tf, dt
ti = Timer(t0=t0, tf=tf, dt=dt, t_feedback=t_feedback)

# Number of precursor groups
n_pg = 6

# Number of decay heat groups
n_dg = 0

# Fissioning Isotope
fission_iso = "fhr"
# Spectrum
spectrum = "thermal"

# Feedbacks, False to turn reactivity feedback off. True otherwise.
feedback = True

# External Reactivity
from pyrk.reactivity_insertion import StepReactivityInsertion
rho_ext = StepReactivityInsertion(timer=ti,
                                  t_step=t_feedback + 10.0 * units.seconds,
                                  rho_init=0.0 * units.delta_k,
                                  rho_final=650.0 * 2 * units.pcm)

# maximum number of internal steps that the ode solver will take
nsteps = 5000

# Moderator Initialization
k_mod = ConductiveModel(a=17 * units.watt 
                        / (units.meter * units.kelvin), model="constant")
cp_mod = 1650.0 * units.joule / (units.kg * units.kelvin)
rho_mod = DensityModel(a=1740. * units.kg / (units.meter**3), model="constant")
Moderator = Material('mod', k_mod, cp_mod, rho_mod)


# Fuel Initialization
k_fuel = ConductiveModel(a=15*units.watt 
                         /(units.meter * units.kelvin), model="constant")
cp_fuel = 1818.0 * units.joule / units.kg / units.kelvin
rho_fuel = DensityModel(a=2220.0 * units.kg /
                        (units.meter**3), model="constant")
Fuel = Material('fuel', k_fuel, cp_fuel, rho_fuel)


# Shell Initialization
k_shell = ConductiveModel(a=17*units.watt 
                          /(units.meter * units.kelvin), model="constant")
cp_shell = 1650.0 * units.joule / (units.kg * units.kelvin)
rho_shell = DensityModel(a=1740. * units.kg /
                         (units.meter**3), model="constant")
Shell = Material('shell', k_shell, cp_shell, rho_shell)


# Coolant Initializations
from pyrk.materials.flibe import Flibe
Cool = Flibe()


# Coolant flow properties
m_flow_cool = 976.0 * units.kg / units.seconds
length_scale_cool = 2.0 * r_fuel
a_flow_cool = 0.40 * (math.pi * r_shell**2) # assuming porosity is 40% & packing is 60%

h_cool = ConvectiveModel(
    mat=Cool,
    m_flow=m_flow_cool,
    a_flow=a_flow_cool,
    length_scale=length_scale_cool,
    model='wakao')

t_inlet = units.Quantity(600.0, units.degC)

mod = th.THComponent(name="mod",
                     mat=Moderator,
                     vol=vol_mod,
                     T0=t_mod,
                     alpha_temp=alpha_mod,
                     timer=ti,
                     sph=True,
                     ri=0.0 * units.meter,
                     ro=r_mod)

fuel = th.THComponent(name="fuel",
                      mat=Fuel,
                      vol=vol_fuel,
                      T0=t_fuel,
                      alpha_temp=alpha_fuel,
                      timer=ti,
                      heatgen=True,
                      power_tot=power_tot / n_pebbles,
                      sph=True,
                      ri=r_mod,
                      ro=r_fuel
                      )

shell = th.THComponent(name="shell",
                       mat=Shell,
                       vol=vol_shell,
                       T0=t_shell,
                       alpha_temp=alpha_shell,
                       timer=ti,
                       sph=True,
                       ri=r_fuel,
                       ro=r_shell)

# mesh size for the fuel pebble FVM calculation
l = 0.0005 * units.meter
comp_list = mod.mesh(l)
comp_list.extend(fuel.mesh(l))
comp_list.extend(shell.mesh(l))
pebble = th.THSuperComponent('pebble', t_shell, comp_list, timer=ti)
# Add convective boundary condition to the pebble
pebble.add_conv_bc('cool', h=h_cool)

cool = th.THComponent(name="cool",
                      mat=Cool,
                      vol=vol_cool,
                      T0=t_cool,
                      alpha_temp=alpha_cool,
                      timer=ti,
                      hm=h_cool)

# The coolant convects to the shell
cool.add_convection('pebble', h=h_cool, area=a_pb)
cool.add_advection('cool', m_flow_cool / n_pebbles, t_inlet, cp=cool.cp)

components = []
for i in range(0, len(pebble.sub_comp)):
    components.append(pebble.sub_comp[i])
components.extend([pebble, cool])
