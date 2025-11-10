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

#############################################
#
# User Workspace
#
#############################################

def vol_sphere(r):
    return (4/3) * math.pi * (r**3)

def area_sphere(r):
    return 4 * math.pi * (r**2)

def vol_shell(r_outer,r_inner):
    return (4/3) * math.pi * (r_outer**3 - r_inner**3)

# Total power, Watts, thermal
power_tot = 200e6 * units.watt # 200 MW thermal output

# Timer instance, based on t0, tf, dt
t0 = 0.00 * units.seconds
dt = 0.005 * units.seconds
tf = 5.0 * units.seconds
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

nsteps = 1000

# Thermal hydraulic params
# Temperature feedbacks of reactivity
# https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_24839.pdf
# https://info.ornl.gov/sites/publications/Files/Pub196359.pdf 
alpha_f = -4.4e-5 * units.pcm / units.kelvin
alpha_c = 1 * units.pcm / units.kelvin # Placeholder
alpha_m = -1.0e-5 * units.pcm / units.kelvin
alpha_r = 1.8e-5 * units.pcm / units.kelvin

# # modified alphas for mod
# vol_mod_tot = vol_mod + vol_graph_peb + vol_core
# alpha_mod = alpha_m * vol_mod / vol_mod_tot
# alpha_core = alpha_m * vol_core / vol_mod_tot
# alpha_graph_peb = alpha_m * vol_graph_peb / vol_mod_tot

# Cumulative radii from center of triso pebble
r_fuel   = 425e-6 * units.meter
r_buffer = r_fuel + 95e-6 * units.meter
r_ipyc   = r_buffer + 40e-6 * units.meter
r_sic    = r_ipyc + 35e-6 * units.meter
r_opyc   = r_sic + 40e-6 * units.meter

# Temperature
t_fuel = 2000 * units.kelvin
t_cool = (750 + 273.15) * units.kelvin
t_refl = 623.15 * units.kelvin
t_core = (750 + 273.15) * units.kelvin

m_flow = 64.9 * units.kg / units.second
t_inlet = 533.15 * units.kelvin
thickness_fuel_matrix = 0.005 * units.meter
kappa = 0.00  # TODO if you fix omegas
core_height = 893 * units.cm
core_inner_radius = 120 * units.cm
reflector_thickness = 90 * units.cm
core_outer_radius = (120 + 90 ) * units.cm

n_pebbles = 223000 #Graphite Pebbles with TRISO Particle fuel 

n_particles_per_pebble = 19000 # 19k UCO 
r_pebble = 0.015 * units.meter  # [m] diam = 3cm
r_core = 0.0125 * units.meter  # [m] diam = 2.5cm
r_particle = 200 * units.micrometer

vol_cool = core_height * (core_inner_radius)**2 * math.pi - (n_pebbles * vol_sphere(r_pebble))
vol_fuel = n_pebbles * n_particles_per_pebble * vol_sphere(r_particle)
vol_core = (n_pebbles) * (vol_sphere(r_core))
vol_mod = (n_pebbles) * (vol_sphere(r_pebble) - vol_sphere(r_core)) - vol_fuel
vol_pebble = (n_pebbles) * (vol_sphere(r_pebble))
vol_fuel = n_pebbles * n_particles_per_pebble * vol_sphere(r_particle)
vol_refl = core_height * (core_outer_radius**2 - core_inner_radius**2) * math.pi

a_core = area_sphere(r_core) * n_pebbles
a_graph_peb = area_sphere(r_pebble) * n_pebbles
a_fuel = area_sphere(r_particle) * n_pebbles * n_particles_per_pebble
a_refl = 2 * math.pi * core_outer_radius * core_height

#IDK if these are like areas per instance or areas of each buffer region summed accross the entire core
a_buffer = area_sphere(r_buffer) * n_pebbles
a_sc = area_sphere(r_buffer) * n_pebbles
a_sic = area_sphere(r_sic) * n_pebbles
a_ipyc = area_sphere(r_ipyc) * n_pebbles
a_opyc = area_sphere(r_opyc) * n_pebbles
a_pebble = a_opyc

# https://www.sciencedirect.com/science/article/pii/S0955221924000244
# https://www.sciencedirect.com/science/article/pii/S2352179123001400
# https://www.sciencedirect.com/science/article/pii/S0029549321002843

### Layers = [outer pyrolitic carbon]
###          [silicon carbide]
###          [inner pyrolytic carbon]
###          [porous carbon buffer]
###          [fuel kernel]


O_PyC = Material(name='outer pyrolitic carbon',
                 cp=  755 * units.joules / units.kg /units.kelvin,
                 dm = DensityModel(model='constant',
                                 a=1700 * units.kg / (units.meter)**3),
                 k =  ConductivityModel(model='constant',
                                      a=8.6 * units.watt / units.meter / units.kelvin))

I_PyC = Material(name='inner pyrolitic carbon',
                 cp=  755 * units.joules / units.kg /units.kelvin,
                 dm = DensityModel(model='constant',
                                 a=1700 * units.kg / (units.meter)**3),
                 k =  ConductivityModel(model='constant',
                                      a=11.0 * units.watt / units.meter / units.kelvin))

Sc = Material(name='silicon carbide',
              cp=  648 * units.joules / units.kg /units.kelvin,
              dm = DensityModel(model='constant',
                                 a=3200 * units.kg / (units.meter)**3),
              k =  ConductivityModel(model='constant',
                                    a=166 * units.watt / units.meter / units.kelvin))

Cb = Material(name='carbon buffer',
              cp=  755 * units.joules / units.kg /units.kelvin,
              dm = DensityModel(model='constant',
                                 a=1700 * units.kg / (units.meter)**3),
              k =  ConductivityModel(model='constant',
                                    a=10.5 * units.watt / units.meter / units.kelvin))

Fuel = Material(name='fuel',
                  cp= 330 * units.joules / units.kg / units.kelvin,
                  k = ConductivityModel(model='uoc_uo2_kernel'),
                  dm = DensityModel(model='constant',
                                    a = 11.0 * units.gram / (units.meter**3)))

Refl = Graphite()


Comp_Cool = th.THComponent(name='helium',
                           mat=Helium(),
                           vol= vol_cool,
                           T0=t_cool,
                           alpha_temp=alpha_c,
                           timer=ti)

Comp_O_PyC = th.THComponent(name="outer pyrolitic carbon",
                      mat=O_PyC,
                      vol=vol_shell(r_opyc, r_ipyc),
                      T0= 900*units.kelvin,
                      alpha_temp=alpha_m,
                      timer=ti)

Comp_I_PyC = th.THComponent(name="inner pyrolitic carbon",
                      mat=I_PyC,
                      vol=vol_shell(r_ipyc,r_sic),
                      T0= 900*units.kelvin,
                      alpha_temp=alpha_m,
                      timer=ti)

Comp_Sc = th.THComponent(name="silicon carbide",
                      mat=Sc,
                      vol=vol_shell(r_sic,r_buffer),
                      T0=900*units.kelvin,
                      alpha_temp=alpha_m,
                      timer=ti)

Comp_C_B = th.THComponent(name="carbon buffer",
                      mat=Cb,
                      vol= vol_shell(r_buffer,r_fuel),
                      T0=900*units.kelvin,
                      alpha_temp=alpha_m,
                      timer=ti)


Comp_Fuel = th.THComponent(name="fuel",
                      mat=Fuel,
                      vol= vol_sphere(r_fuel),
                      T0= 900 * units.kelvin,
                      alpha_temp=alpha_f,
                      timer=ti)

Comp_Refl = th.THComponent(name='refl',
                           mat=Refl,
                           vol= vol_refl,
                           T0= 623.15 * units.kelvin,
                           alpha_temp=alpha_r,
                           timer=ti)

components = [Comp_Cool,Comp_O_PyC, Comp_I_PyC, Comp_Sc, Comp_C_B, Comp_Fuel,Comp_Refl]

h_triso = ConvectiveModel(mat=Helium(),
                          m_flow=m_flow,
                          a_flow= a_pebble,
                          length_scale= r_pebble * 2,
                          model= 'wakao')


h_refl = ConvectiveModel(mat=Helium(),
                         m_flow=m_flow,
                         a_flow= a_refl,
                         length_scale=core_inner_radius * 2,
                         model='wakao')

# External Reactivity
from pyrk.reactivity_insertion import StepReactivityInsertion
rho_ext = StepReactivityInsertion(timer=ti, t_step=1.0 * units.seconds,
                                  rho_init=0.0 * units.delta_k,
                                  rho_final=0.000 * units.delta_k)

##################################
#
# Fuel/ Triso-x Pebble Treatment
#
##################################

# The fuel conducts to the Carbon Buffer
Comp_Fuel.add_conduction('carbon buffer', area=a_fuel,
                           r_env=r_fuel)

# The Carbon Buffer conducts to the Silicon Carbide
Comp_C_B.add_conduction('silicon carbide', area=a_buffer,
                        r_env=r_buffer)

# The Silicon Carbide conducts to the Inner Pyrolitic Carbon
Comp_Sc.add_conduction('inner pyrolitic carbon', area=a_sic,
                       r_env=r_sic)

#The Inner Pyrolitic Carbon conducts to the Outer Pyrolitic Carbon
Comp_I_PyC.add_conduction('outer pyrolitic carbon', area = a_ipyc,
                          r_env = r_ipyc)

#The Outer Pyrolitic Carbon convects with the coolant
Comp_O_PyC.add_convection('helium', area = a_opyc, h=h_triso)


#############################
#
# Reflector Treatment
#
#############################

# The reflector convects with the coolant
Comp_Refl.add_convection('helium', h=h_refl, area=a_refl)
