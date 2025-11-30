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
tf = 5.0 * units.seconds
ti = Timer(t0=t0, tf=tf, dt=dt)

n_pg = 6
n_dg = 0

# Fissioning Isotope
fission_iso = "u235"
spectrum = "thermal"

feedback = True
nsteps = 10000

# Temperature feedbacks of reactivity
# alpha_f = -4.4 * units.pcm / units.kelvin
# alpha_m = -1.0 * units.pcm / units.kelvin
# alpha_r = 1.8 * units.pcm / units.kelvin
# alpha_t = -3.6 * units.pcm / units.kelvin

alpha_f = 0 * units.pcm / units.kelvin
alpha_m = 0 * units.pcm / units.kelvin
alpha_r = 0 * units.pcm / units.kelvin
alpha_t = 0 * units.pcm / units.kelvin

# Temperature
t_fuel = (873 + 273.15) * units.kelvin
t_cool = (775 + 273.15) * units.kelvin
t_refl = (623.15) * units.kelvin
t_mod = (750 + 273.15) * units.kelvin
t_pebble = (1000) * units.kelvin
t_inlet = (260 + 273.15) * units.kelvin
t_outlet = (750 + 273.15) * units.kelvin

m_flow = 78.6 * units.kg / units.second
t_inlet = 533.15 * units.kelvin
thickness_fuel_matrix = 0.005 * units.meter

kappa = 0.00
core_height = 8.93 * units.meter
core_inner_radius = 1.20 * units.meter
reflector_thickness = .90 * units.meter
core_outer_radius = core_inner_radius + reflector_thickness

n_pebbles = 223000 #Graphite Pebbles with TRISO Particle fuel 

n_particles_per_pebble = 19000
d_pebble = 0.06 * units.meter
r_pebble = 0.03 * units.meter
r_particle = 250 * units.micrometer
r_fuel_region = 0.025 * units.meter
r_shell_region = 0.005 * units.meter

vol_all_pebbles = n_pebbles * vol_sphere(r_pebble)
vol_cool = core_height * (core_inner_radius**2 * math.pi) - vol_all_pebbles
vol_cool = core_height * (core_inner_radius**2 * math.pi) * 0.6 # 40% porosity

vol_refl = core_height * (core_outer_radius**2 - core_inner_radius**2) * math.pi
vol_kernel = vol_sphere(r_particle)

a_pebble = n_pebbles * area_sphere(r_pebble)
a_fuel_region = n_pebbles * area_sphere(r_fuel_region)
a_refl = 2 * math.pi * core_outer_radius * core_height

Refl = Graphite(name='refl')

Cool = Helium(name='cool')

Pebble_graph = Graphite(name='graph_pebble')

Comp_Fuel = th.THComponent(name="fuel",
                      mat=Kernel(name="fuelkernel"),
                      vol=vol_all_pebbles,
                      T0=t_fuel,
                      alpha_temp=alpha_f,
                      timer=ti,
                      heatgen=True,
                      power_tot=power_tot)

Comp_Core = th.THComponent(name='core',
                           mat=Graphite(name='pebgraphite'),
                           vol=vol_all_pebbles,
                           T0=t_pebble,
                           alpha_temp=alpha_t,
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
                           alpha_temp = alpha_t,
                           timer = ti)

components = [Comp_Cool,Comp_Refl,Comp_Core,Comp_Fuel]

h_pebble = ConvectiveModel(mat=Cool,
                          m_flow=m_flow,
                          a_flow= (core_inner_radius**2 * math.pi) * 0.4,
                          length_scale= d_pebble,
                          model= 'wakao')

h_core = ConvectiveModel(h0=442 * units.watt / units.meter**2 / units.kelvin)

h_refl = ConvectiveModel(h0= 600 * units.watt / 
                         units.meter**2 / units.kelvin)


Comp_Fuel.add_conduction('core', area=a_fuel_region,
                            L=5 * units.millimeter)
Comp_Core.add_conduction('fuel', area=a_fuel_region,
                         L = 5*units.millimeter)

# Moderator / Coolant Convection
Comp_Core.add_convection('cool', h=h_pebble, area=a_pebble)
Comp_Cool.add_convection('core', h=h_pebble, area=a_pebble)

# Coolant / Reflector Convection
Comp_Cool.add_convection('refl', h=h_refl, area=a_refl)
Comp_Refl.add_convection('cool', h=h_refl, area=a_refl)


# External Reactivity Insetion
from pyrk.reactivity_insertion import StepReactivityInsertion
rho_ext = StepReactivityInsertion(timer=ti,
                                  t_step=0.0 * units.seconds,
                                  rho_init=0.0 * units.delta_k,
                                  rho_final=0.000 * units.delta_k)

