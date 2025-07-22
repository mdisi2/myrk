from pyrk.materials.material import Material
from pyrk.conductivity_model import ConductivityModel
from pyrk.density_model import DensityModel
from pyrk.materials.liquid_material import LiquidMaterial
from pyrk.utilities.ur import units
from pprint import pprint


### The purpose of this test is to see if the logic in the
### Material Classes correctly converts the 

cond = ConductivityModel(a=10* units.watt / units.kelvin / units.meter,
                         model='constant')
dens = DensityModel(a= 10 * units.kg / units.meter**3 )

SolidMatModel = Material(name='Solid Mat Model',
               km=cond,
               cp = 10*units.joule / units.kg / units.kelvin,
               dm=dens)

SolidMatNone = Material(name='Solid Mat None',
                        km = 100 * units.watt / units.kelvin / units.meter,
                        cp =  10*units.joule / units.kg / units.kelvin,
                        dm = 10 * units.kg / units.meter**3)

if type(SolidMatNone.dm) == type(SolidMatModel.dm):
    print("density models passed")
if type(SolidMatNone.km) == type(SolidMatModel.km):
    print('K model passed')