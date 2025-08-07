from pyrk.utilities.ur import units
from pyrk.convective_model import ConvectiveModel
from pyrk.materials.flibe import Flibe
from math import pi
import matplotlib.pyplot as plt


Cool = Flibe()
m_flow = 976.0 * units.kg / units.seconds
void_av = 0.4
t_cool = (650 + 273.15) * units.kelvin
r_shell = 1.5 / 100.0 * units.meter
r_reflin = 0.35 * units.meter
r_reflout = 1.05 * units.meter

h_cool = ConvectiveModel(
    mat=Flibe(),
    m_flow= m_flow,
    a_flow= void_av * pi * (r_reflout**2 - r_reflin**2),
    length_scale= 2.0 * (r_shell),
    T0=t_cool,
    model='wakao')

print(h_cool.h(temp=t_cool))

t = [700 * units.kelvin, 
     800 * units.kelvin,
     900 * units.kelvin,
     1000 * units.kelvin]

h_ar = []
for i in t:
    h_ar.append(h_cool.h(temp=i).magnitude)

plt.rcParams['font.family'] = 'serif'
plt.plot([i.magnitude for i in t], h_ar, label='Heat Transfer Coefficient')
plt.xlabel('Temperature [K]')
plt.ylabel(r'h $\frac{W}{K \cdot m^2}$')
plt.title('Heat Transfer Coefficient at Different Temperatures')
plt.grid()
plt.legend()
plt.savefig('convective_model_test.png', dpi=300, format='png')
plt.show()