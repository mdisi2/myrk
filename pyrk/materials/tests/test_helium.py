from pyrk.utilities.ur import units
from pyrk.density_model import DensityModel
from pyrk.conductivity_model import ConductivityModel
from pyrk.viscosity_model import ViscosityModel
from pyrk.materials.helium import Helium
from pyrk.convective_model import ConvectiveModel
from math import pi

### Density Test

d_pebble = 0.06 * units.meter
a_flow = (1.20 * units.meter)**2 * pi * 0.4
m_flow = 78.6 * units.kg / units.second
t_0 = (775 + 273.15) * units.kelvin
H = Helium(name='helium')

def Test_Density():
    a = 4.35833333e-06 * (units.kg / units.meter**3 / units.kelvin**2)
    b = -1.16810714e-02 *  (units.kg / units.meter**3 / units.kelvin)
    c = 1.01620952e+01 *  (units.kg / units.meter**3)
    dens_at_t0 = a*t_0**2 + b*t_0 + c

    dens_t0 = H.dm.rho(t_0)
    dens_model = DensityModel(model='helium')
    d_0 = dens_model.rho(t_0)

    assert abs((dens_at_t0 - dens_t0).magnitude) < 1e-12
    assert abs((d_0 - dens_t0).magnitude) < 1e-12

def Test_Cp():
    cp_0 = 5.190e3 * units.joule / (units.kg * units.kelvin)
    cp_h = H.cp

    print(cp_h, cp_0)
    assert abs((cp_h - cp_0).magnitude) < 1e-5

def Test_Conduction():
    a = 0.000261 * (units.watt / units.kelvin**2 / units.meter)
    b = 0.10144 * (units.watt / units.kelvin / units.meter)

    k_at_t0 = a * t_0 + b
    k_t0 = H.k.thermal_conductivity(t_0)

    k_model = ConductivityModel(model='helium')
    k_0 = k_model.thermal_conductivity(t_0)

    print("calc =", k_at_t0)
    print("helium.k =", k_t0)
    print("model =", k_0)

    assert abs((k_at_t0 - k_t0).magnitude) < 1e-5
    assert abs((k_0 - k_t0).magnitude) < 1e-5

def Test_viscosity(t_0):
    a = 3.3717e-08 * units.pascal * units.second / units.kelvin
    b = 1.23625e-5 * units.pascal * units.second
    
    mu_t0 = H.mu.dynamic_viscosity(t_0)
    mu_at_t0 = a * t_0 + b 

    mu_model = ViscosityModel(model='helium')
    mu_0 = mu_model.dynamic_viscosity(t_0)

    assert abs((mu_t0 - mu_at_t0).magnitude) < 1e-12
    assert abs((mu_0 - mu_at_t0).magnitude) < 1e-12

def Test_Convection():
    h_pebble = ConvectiveModel(
        mat=H,
        m_flow=m_flow,
        a_flow=a_flow*0.4,
        length_scale=d_pebble,
        model='wakao')
    
    h_val = h_pebble.h(rho = H.dm.rho(t_0),
                       k = H.k.thermal_conductivity(t_0),
                       mu = H.mu.dynamic_viscosity(t_0))
    
    print(h_val)

Test_Convection()
Test_Density()
Test_Conduction()
Test_Cp()