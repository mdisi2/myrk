''' changed from the initial input file
to represent a simplified model for the FHR core

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
from pyrk.density_model import DensityModel
from pyrk.convective_model import ConvectiveModel
import random
from pyrk.timer import Timer
import numpy as np

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
tf = 100.0 * units.seconds
# Thermal hydraulic params
# Temperature feedbacks of reactivity
alpha_fuel = random.gauss(-3.19, 0.1595) * units.pcm / units.kelvin
alpha_mod = -0.7 * units.pcm / units.kelvin
alpha_shell = 0 * units.pcm / units.kelvin
alpha_cool = random.gauss(0.23, 0.11) * units.pcm / units.kelvin

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
# power_tot = 0.0*units.watt

# Timer instance, based on t0, tf, dt
ti = Timer(t0=t0, tf=tf, dt=dt)

# Number of precursor groups
n_pg = 6

# Number of decay heat groups
n_dg = 0

# Fissioning Isotope
fission_iso = "u235"

# Spectrum
spectrum = "thermal"

# two-point model
n_ref = 0
Lambda_ref = 0
ref_lambda = []
ref_rho = []

# Feedbacks, False to turn reactivity feedback off. True otherwise.
feedback = True

# External Reactivity
from pyrk.reactivity_insertion import RampReactivityInsertion
rho_ext = RampReactivityInsertion(timer=ti,
                                  t_start=60.0 * units.seconds,
                                  t_end=70.0 * units.seconds,
                                  rho_init=0.0 * units.delta_k,
                                  rho_rise=600.0 * units.pcm,
                                  rho_final=600.0 * units.pcm)

# maximum number of internal steps that the ode solver will take
nsteps = 5000

k_mod = random.gauss(17, 17 * 0.05) * units.watt / (units.meter * units.kelvin)
cp_mod = random.gauss(1650.0, 1650.0 * 0.05) * \
    units.joule / (units.kg * units.kelvin)
rho_mod = DensityModel(a=1740. * units.kg / (units.meter**3), model="constant")
Moderator = Material('mod', k_mod, cp_mod, dm=rho_mod)

k_fuel = random.uniform(15.0, 19.0) * units.watt / (units.meter * units.kelvin)
cp_fuel = random.gauss(
    1818.0,
    1818 * 0.05) * units.joule / units.kg / units.kelvin  # [J/kg/K]
rho_fuel = DensityModel(a=2220.0 * units.kg /
                        (units.meter**3), model="constant")
Fuel = Material('fuel', k_fuel, cp_fuel, dm=rho_fuel)

k_shell = random.gauss(17, 17 * 0.05) * units.watt / \
    (units.meter * units.kelvin)
cp_shell = random.gauss(1650.0, 1650.0 * 0.05) * units.joule / (
    units.kg * units.kelvin)
rho_shell = DensityModel(a=1740. * units.kg /
                         (units.meter**3), model="constant")
Shell = Material('shell', k_shell, cp_shell, dm=rho_shell)

k_cool = 1 * units.watt / (units.meter * units.kelvin)
cp_cool = random.gauss(
    2415.78, 2415.78 * 0.05) * units.joule / (units.kg * units.kelvin)
rho_cool = DensityModel(a=2415.6 *
                        units.kg /
                        (units.meter**3), b=0.49072 *
                        units.kg /
                        (units.meter**3) /
                        units.kelvin, model="linear")

mu0 = 0 * units.pascal * units.second
cool = LiquidMaterial('cool', k_cool, cp_cool, rho_cool, mu0)

# Coolant flow properties
h_cool_rd = random.gauss(
    4700.0,
    4700.0 * 0.05) * units.watt / units.kelvin / units.meter**2
h_cool = ConvectiveModel(h0=h_cool_rd,
                         mat=cool,
                         model='constant')
m_flow = 976.0 * units.kg / units.second
t_inlet = units.Quantity(600.0, units.degC)  # degrees C


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
                      mat=cool,
                      vol=vol_cool,
                      T0=t_cool,
                      alpha_temp=alpha_cool,
                      timer=ti)
# The coolant convects to the shell
cool.add_convection('pebble', h=h_cool, area=a_pb)
cool.add_advection('cool', m_flow / n_pebbles, t_inlet, cp=cool.cp)

components = []
for i in range(0, len(pebble.sub_comp)):
    components.append(pebble.sub_comp[i])
components.extend([pebble, cool])

uncert = [
    alpha_cool,
    alpha_fuel,
    k_mod,
    k_fuel,
    k_shell,
    cp_mod,
    cp_fuel,
    cp_shell,
    cp_cool,
    h_cool.h()]
uncertainty_param = np.array([o.magnitude for o in uncert])
