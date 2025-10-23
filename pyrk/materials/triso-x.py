from pyrk.materials.material import Material
from pyrk.utilities.ur import units
from pyrk.density_model import DensityModel
from pyrk.conductivity_model import ConductivityModel
from pyrk import th_component
from math import pi

# https://www.sciencedirect.com/science/article/pii/S0955221924000244
# https://www.sciencedirect.com/science/article/pii/S2352179123001400
# https://www.sciencedirect.com/science/article/pii/S0029549321002843

### Layers = [outer pyrolitic carbon]
###          [silicon carbide]
###          [inner pyrolytic carbon]
###          [porous carbon buffer]
###          [fuel kernel]

kernel_r = 800 * units.micrometer
buffer_r = 110 * units.micrometer
IPyC_r = 40 * units.micrometer
SiC_r = 57 * units.micrometer
OPyC_r = 35 * units.micrometer

def vol(r):
    return (4/3) * pi * (r**3)

def area(r):
    return 4 * pi * (r**2)

O_PyC = Material(name='outer pyrolitic carbon',
                 cp=  755 * units.joules / units.kg /units.kevlin,
                 dm = DensityModel(model='constant',
                                 a=1700 * units.kg / (units.meter)**3),
                 k =  ConductivityModel(model='constant',
                                      a=8.6 * units.watt / units.meter / units.kelvin))

I_PyC = Material(name='inner pyrolitic carbon',
                 cp=  755 * units.joules / units.kg /units.kevlin,
                 dm = DensityModel(model='constant',
                                 a=1700 * units.kg / (units.meter)**3),
                 k =  ConductivityModel(model='constant',
                                      a=11.0 * units.watt / units.meter / units.kelvin))

Sc = Material(name='silicon carbide',
              cp=  648 * units.joules / units.kg /units.kevlin,
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

kernel = Material(name='fuel kernel',
                  cp= 330 * units.joules / units.kg / units.kelvin,
                  k = ConductivityModel(model='uoc_uo2_kernel'),
                  dm = DensityModel(mode='constant',
                                    a = 11.0 * units.gram / (units.meter**3)))


class Triso_X(th_component):
