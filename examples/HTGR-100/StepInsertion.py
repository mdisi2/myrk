from pyrk.utilities.ur import units
from pyrk import th_component as th
import math
from pyrk.materials.material import Material
from pyrk.conductivity_model import ConductivityModel
from pyrk.viscosity_model import ViscosityModel
from pyrk.density_model import DensityModel
from pyrk.convective_model import ConvectiveModel
from pyrk.materials.helium import Helium
from pyrk.materials.graphite import Graphite
from pyrk.timer import Timer
from pyrk.materials.kernel import Kernel
from pyrk.reactivity_insertion import StepReactivityInsertion

#############################################
#
# User Workspace
#
#############################################

# https://www.sciencedirect.com/science/article/pii/S0955221924000244
# https://www.sciencedirect.com/science/article/pii/S2352179123001400
# https://www.sciencedirect.com/science/article/pii/S0029549321002843

# https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_24839.pdf
# https://info.ornl.gov/sites/publications/Files/Pub196359.pdf 

def vol_sphere(r):
    return (4/3) * math.pi * (r**3)

def area_sphere(r):
    return 4 * math.pi * (r**2)

# Total power, Watts, thermal
power_tot = 200e6 * units.watt # 200 MW thermal output

# Timer instance, based on t0, tf, dt
t0 = 0.00 * units.seconds
dt = 0.005 * units.seconds
tf = 15.0 * units.seconds
ti = Timer(t0=t0, tf=tf, dt=dt)

n_pg = 6
n_dg = 0

# Fissioning Isotope
fission_iso = "u235"
spectrum = "thermal"

feedback = False
nsteps = 10000

#core in input.py is the smear region


## start with feedbacks off and itterate until you get equilibrium temperatures

## run new sim with temps at each component, make sure with feedbacks off it stays flat

## turn on feedbacks, using temperatures, run 15 second and insert at 10 seconds

## look into import dnp consentrations

# Temperature feedbacks of reactivity
alpha_f = -4.4 * units.pcm / units.kelvin
alpha_m = -1.0 * units.pcm / units.kelvin
alpha_r = 1.8 * units.pcm / units.kelvin
alpha_total = -3.6 * units.pcm / units.kelvin
# TODO alpha core
alpha_c = 0.0 * units.pcm / units.kelvin

alpha_f = 0 * units.pcm / units.kelvin
alpha_m = 0 * units.pcm / units.kelvin
alpha_r = 0 * units.pcm / units.kelvin
alpha_total = 0 * units.pcm / units.kelvin

# Temperature
t_fuel = (1650) * units.kelvin
t_cool = (1180) * units.kelvin
t_refl = (625) * units.kelvin
t_mod = (1100) * units.kelvin
t_smear = (1100) * units.kelvin

t_outlet = (750 + 273.15) * units.kelvin
t_inlet = 533.15 * units.kelvin

m_flow = 78.6 * units.kg / units.second
thickness_fuel_matrix = 0.005 * units.meter

kappa = 0.00 #fix omegas
core_height = 8.93 * units.meter
core_inner_radius = 1.20 * units.meter
reflector_thickness = 0.90 * units.meter
core_outer_radius = core_inner_radius + reflector_thickness

n_pebbles = 223000 #Graphite Pebbles with TRISO Particle fuel 

n_particles_per_pebble = 19000
d_pebble = 0.06 * units.meter
r_pebble = 0.03 * units.meter
r_particle = 250 * units.micrometer
r_fuel_region = 0.025 * units.meter
r_shell_region = 0.005 * units.meter

vol_all_pebbles = n_pebbles * vol_sphere(r_pebble)
vol_cool = core_height *\
      (core_inner_radius**2 * math.pi) * 0.6
vol_refl = core_height *\
      (core_outer_radius**2 - core_inner_radius**2)* math.pi
vol_fuel_kernel = n_pebbles * n_particles_per_pebble \
    * vol_sphere(r_particle)
vol_peb_graphite = vol_all_pebbles - vol_fuel_kernel

vol_smear_region = vol_sphere(r_fuel_region) * n_pebbles


a_pebbles = n_pebbles * area_sphere(r_pebble)
a_fuel_region = n_pebbles * area_sphere(r_fuel_region)
a_refl = 2 * math.pi * core_outer_radius * core_height
a_flow = (core_inner_radius**2) * math.pi * 0.4
a_fuel = area_sphere(r_particle) * n_pebbles * n_particles_per_pebble
a_smear = area_sphere(r_fuel_region) * n_pebbles

### Materials and THcomponents 

Refl = Graphite(name='refl')
Cool = Helium(name='cool')
Pebble_graph = Graphite(name='pebgraphite')
Fuel = Kernel(name="fuelkernel")

Smear = Material(name='smear',
                 k=ConductivityModel(model='constant',
                                     a =  0.26 * units.watt / units.meter / units.kelvin),
                 rho=DensityModel(model='constant',
                                  a =  1740 * units.kg / units.meter**3),
                cp = 1650.0 * units.joule / units.kg / units.kelvin)

Comp_Fuel = th.THComponent(name="fuel",
                      mat=Fuel,
                      vol=vol_fuel_kernel,
                      T0=t_fuel,
                      alpha_temp=alpha_f,
                      timer=ti,
                      heatgen=True,
                      power_tot=power_tot)

Comp_Mod = th.THComponent(name='mod',
                           mat=Pebble_graph,
                           vol=vol_peb_graphite,
                           T0=t_mod,
                           alpha_temp=alpha_m,
                           timer=ti)

Comp_Refl = th.THComponent(name='refl',
                           mat=Refl,
                           vol= vol_refl,
                           T0=t_refl,
                           alpha_temp=alpha_r,
                           timer=ti)

Comp_Cool = th.THComponent(name='cool',
                           mat=Cool,
                           vol= vol_cool,
                           T0 = t_cool,
                           alpha_temp = 0 * units.pcm / units.kelvin,
                           timer = ti)

Comp_Smear = th.THComponent(name='smear',
                            mat=Smear,
                            vol= vol_smear_region,
                            T0 = t_smear,
                            alpha=alpha_total,
                            timer=ti)

components = [Comp_Cool,Comp_Refl,Comp_Mod,Comp_Fuel,Comp_Smear]

h_cool = ConvectiveModel(
        mat=Cool,
        m_flow=m_flow,
        a_flow=a_flow,
        length_scale=d_pebble,
        model='wakao')

h_cool_c = ConvectiveModel(h0=7456 * units.watt / units.meter**2 / units.kelvin)

h_refl = ConvectiveModel(h0= 400 * units.watt / 
                         units.meter**2 / units.kelvin)


# # Fuel / Graphite blob conduction
# Comp_Fuel.add_conduction('mod', area=a_fuel_region,
#                             L=5*units.millimeter)
# Comp_Mod.add_conduction('fuel', area=a_fuel_region,
#                         L=5*units.millimeter)

# # graphite bloob / Coolant Convection
# Comp_Mod.add_convection('cool', h=h_cool, area=a_pebbles)
# Comp_Cool.add_convection('mod', h=h_cool, area=a_pebbles)

# # Coolant / Reflector Convection
# Comp_Cool.add_convection('refl', h=h_cool, area=a_refl)
# Comp_Refl.add_convection('cool', h=h_cool, area=a_refl)


# External Reactivity Insetion
rho_ext = StepReactivityInsertion(timer=ti,
                                  t_step=1.0 * units.seconds,
                                  rho_init=0.0 * units.delta_k,
                                  rho_final=0.0 * units.delta_k)


# Fuel only conducts to the smear
Comp_Fuel.add_conduction('smear', area=a_smear, L=5 * units.millimeter)

# The moderator graphite conducts to the smear and convects to the coolant    
Comp_Mod.add_conduction('smear', area=a_smear, L=25 * units.millimeter)
Comp_Mod.add_convection('cool', h=h_cool, area=a_pebbles)

# The smear conducts to the moderator graphite
Comp_Smear.add_conduction('mod', area=a_smear, L=25 * units.centimeter)
Comp_Smear.add_conduction('fuel', area=a_smear, L=5 * units.millimeter)


# The coolant convects accross the graphite pebbles
Comp_Cool.add_convection('mod', h=h_cool, area=a_pebbles)
Comp_Cool.add_convection('refl', h=h_refl, area=a_refl)

# The reflector convects with the coolant
Comp_Refl.add_convection('cool', h=h_refl, area=a_refl)
