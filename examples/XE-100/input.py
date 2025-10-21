from pyrk.utilities.ur import units
from pyrk import th_component as th
import math
from pyrk.materials.graphite import Graphite
from pyrk.materials.helium import Helium
from pyrk.materials.kernel import Kernel
from pyrk.timer import Timer

#############################################
#
# User Workspace
#
#############################################

# Thermal hydraulic params
# Temperature feedbacks of reactivity
alpha_f =
alpha_c = 
alpha_m = 
alpha_r = 

# Temperature
t_fuel = 
t_cool = (750 + 273.15) * units.kelvin
t_refl = 
t_mod = 
t_graph_peb = 
t_core =

# TODO triso particles


vel_cool = 
t_inlet = 
thickness_fuel_matrix = 
kappa = 0.00  # TODO if you fix omegas
core_height = 
core_inner_radius = 
core_outer_radius = 

# Timer Treatment
t0 = 0.00 * units.seconds
dt = 0.005 * units.seconds
tf = 5.0 * units.seconds


def area_sphere(r):
    assert(r >= 0 * units.meter)
    return (4.0) * math.pi * pow(r.to('meter'), 2)


def vol_sphere(r):
    assert(r >= 0 * units.meter)
    return (4. / 3.) * math.pi * pow(r.to('meter'), 3)


# TODO maybe make an entire triso-x partical class
n_pebbles = 220000 #Graphite Pebbles with TRISO Particle fuel 
n_graph_peb = 218000
n_particles_per_pebble = 



r_pebble =
r_core =
r_particle = 

# vol of 4730 kernels per pebble, each 400 micrometer diameter
vol_fuel = n_pebbles * n_particles_per_pebble * vol_sphere(r_particle)
vol_core = (n_pebbles) * (vol_sphere(r_core))
vol_mod = (n_pebbles) * (vol_sphere(r_pebble) - vol_sphere(r_core)) - vol_fuel
vol_graph_peb = (n_graph_peb) * (vol_sphere(r_pebble))

# from design report
vol_cool = 7.20 * units.meter**3
mass_inner_refl = 43310.0 * units.kg
mass_outer_refl = 5940.0 * units.kg
mass_refl = mass_inner_refl + mass_outer_refl
rho_refl = 1740.0 * units.kg / units.meter**3
vol_refl = mass_refl / rho_refl

a_core = area_sphere(r_core) * n_pebbles
a_mod = area_sphere(r_pebble) * n_pebbles
a_graph_peb = area_sphere(r_pebble) * n_graph_peb
a_fuel = area_sphere(r_particle) * n_pebbles * n_particles_per_pebble
a_refl = 2 * math.pi * core_outer_radius * core_height

# TODO implement h(T) model
h_mod = 4700 * units.watt / units.kelvin / units.meter**2
# TODO placeholder
h_refl = 600 * units.watt / units.kelvin / units.meter**2

# modified alphas for mod
vol_mod_tot = vol_mod + vol_graph_peb + vol_core
alpha_mod = alpha_m * vol_mod / vol_mod_tot
alpha_core = alpha_m * vol_core / vol_mod_tot
alpha_graph_peb = alpha_m * vol_graph_peb / vol_mod_tot

#############################################
#
# Required Input
#
#############################################

# Total power, Watts, thermal
power_tot = 200e6 * units.watt # 200 MW thermal output

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

# Feedbacks, False to turn reactivity feedback off. True otherwise.
feedback = True

# External Reactivity
from pyrk.reactivity_insertion import StepReactivityInsertion
rho_ext = StepReactivityInsertion(timer=ti, t_step=1.0 * units.seconds,
                                  rho_init=0.0 * units.delta_k,
                                  rho_final=0.005 * units.delta_k)

# maximum number of internal steps that the ode solver will take
nsteps = 1000


fuel = th.THComponent(name="fuel",
                      mat=Kernel(name="fuelkernel"),
                      vol=vol_fuel,
                      T0=t_fuel,
                      alpha_temp=alpha_f,
                      timer=ti,
                      heatgen=True,
                      power_tot=power_tot)

cool = th.THComponent(name="cool",
                      mat=Helium(name="helium"),
                      vol=vol_cool,
                      T0=t_cool,
                      alpha_temp=alpha_c,
                      timer=ti)

refl = th.THComponent(name="refl",
                      mat=Graphite(name="reflgraphite"),
                      vol=vol_refl,
                      T0=t_refl,
                      alpha_temp=alpha_r,
                      timer=ti)

mod = th.THComponent(name="mod",
                     mat=Graphite(name="pebgraphite"),
                     vol=vol_mod,
                     T0=t_mod,
                     alpha_temp=alpha_mod,
                     timer=ti)

core = th.THComponent(name="core",
                      mat=Graphite(name="pebgraphite"),
                      vol=vol_core,
                      T0=t_core,
                      alpha_temp=alpha_core,
                      timer=ti)

graph_peb = th.THComponent(name="graph_peb",
                           mat=Graphite(name="pebgraphite"),
                           vol=vol_mod,
                           T0=t_graph_peb,
                           alpha_temp=alpha_graph_peb,
                           timer=ti)

components = [fuel, cool, refl, mod, graph_peb, core]


# The fuel conducts to the moderator graphite
fuel.add_conduction('mod', area=a_fuel, L=4 * units.millimeter)

# The moderator graphite conducts to the core graphite
mod.add_conduction('core', area=a_core, L=25 * units.millimeter)
# The moderator graphite conducts to the fuel
mod.add_conduction('fuel', area=a_mod, L=25 * units.millimeter)
# The moderator graphite convects to the coolant
mod.add_convection('cool', h=h_mod, area=a_mod)

# The core graphite conducts to the moderator graphite
core.add_conduction('mod', area=a_core, L=25 * units.centimeter)

# The graphite pebbles convect to the coolant
graph_peb.add_convection('cool', h=h_mod, area=a_graph_peb)

# The coolant convects accross the graphite pebbles
cool.add_convection('graph_peb', h=h_mod, area=a_graph_peb)
# The coolant convects accross the graphite pebbles
cool.add_convection('mod', h=h_mod, area=a_mod)
# The coolant convects accross the reflector
cool.add_convection('refl', h=h_refl, area=a_refl)

# The reflector convects with the coolant
refl.add_convection('cool', h=h_refl, area=a_refl)
