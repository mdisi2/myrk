from pyrk.utilities.ur import units
from pyrk.convective_model import ConvectiveModel
from pyrk.materials.liquid_material import LiquidMaterial
from pyrk.conductivity_model import ConductivityModel
from pyrk.viscosity_model import ViscosityModel
from pyrk.density_model import DensityModel
from pyrk.materials.flibe import Flibe
from math import pi


# def test_constant_model():
# h_constant = ConductivityModel(20 * units.W / units.meter**2 / units.kelvin)
# h1_constant = ConductivityModel(20 * units.W / units.centimeter**2 / units.kelvin)
# assert (h_constant.h0 ==
#             20 * units.W / units.meter**2 / units.kelvin)
# assert (h1_constant.h0 ==
#             200000 * units.W / units.meter**2 / units.kelvin)


# def test_wakao_model():
      
#       k = ConductivityModel(a = 2 * units.watt / units.meter / units.kelvin,
#                         b = 3 * units.watt / units.meter / units.kelvin / units.kelvin,
#                         model='constant')
#       mu = ViscosityModel(a=0.0001 * units.pascal * units.second,
#                         b=4000 * units.kelvin,
#                         model='constnat')
#       cp = 1 * units.joule / units.kg / units.kelvin

#       rho = DensityModel(a=10 * units.kg / pow(units.meter,3),
#                         b=1 *units.kg / pow(units.meter,3) / units.kelvin,
#                         model='constant')

#       mat = LiquidMaterial(km=k,
#                         cp=cp,
#                         vm=mu,
#                         dm=rho)
      
#       h_wakao = ConvectiveModel(mat=mat,
#                               m_flow=1 * units.kg / units.g,
#                               a_flow=1 * units.meter**2,
#                               length_scale=1 * units.meter,
#                               model='wakao')
#       assert (h_wakao.mu ==
#             2 * units.pascal * units.second)
#       assert (h_wakao.h(rho, 0 * units.pascal * units.second) ==
#       h_wakao.h(rho, 2 * units.pascal * units.second))
      



Cool = Flibe()
m_flow = 976.0 * units.kg / units.seconds
void_av = 0.4
t_cool = (650 + 273.15) * units.kelvin
r_shell = 1.5 / 100.0 * units.meter
r_reflin = 0.35 * units.meter
r_reflout = 1.05 * units.meter

h_cool = ConvectiveModel(
    mat= Cool,
    m_flow= m_flow,
    a_flow= void_av * pi * (r_reflout**2 - r_reflin**2),
    length_scale= 2.0 * (r_shell),
    T0=t_cool,
    model='wakao')


print(h_cool.h(rho=h_cool.rho(t_cool),
               k=h_cool.k(t_cool),
               mu=h_cool.mu(t_cool)))

13295.138881415622