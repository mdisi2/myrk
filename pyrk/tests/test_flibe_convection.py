from pyrk.utilities.ur import units
from pyrk.materials.flibe import Flibe
from pyrk.convective_model import ConvectiveModel
import math
import pprint


mat = Flibe()

r_shell = 1.5 / 100 * units.meter
T0 = 900 * units.kelvin
m_flow = 976.0 * units.kg / units.seconds
r_FuelRegion = 1.05 * units.meter
void = 0.40

hm = ConvectiveModel(
    mat= mat,
    m_flow= m_flow,
    a_flow= math.pi * (r_FuelRegion**2) * 0.38,
    length_scale= 2 * r_shell,
    model='wakao')

rho = mat.dm.rho(T0)
mu = mat.vm.mu(T0)
k = mat.km.k(T0)

hv = hm.h(rho=rho,
         mu=mu,
         k=k)

if hv.check("watt / meter**2 / kelvin") == True:
    print("Convection Model Returns Correct Units")

prop_dict = {
    "temperature" : T0.magnitude,
    "specific heat" : mat.cp.magnitude,
    "density" : rho.magnitude,
    "dynamic viscosity" : mu.magnitude,
    "thermal conductivity" : k.magnitude,
    "convection" : hv.magnitude
    }

pprint.pprint(prop_dict)