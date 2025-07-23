from pyrk.materials.material import Material
from pyrk.conductivity_model import ConductivityModel
from pyrk.density_model import DensityModel
from pyrk.materials.liquid_material import LiquidMaterial
from pyrk.viscosity_model import ViscosityModel
from pyrk.utilities.ur import units
from pprint import pprint


### The purpose of this test is to see if the logic in the
### Material Classes correctly converts the quantities to the models
### Doing this so I don't have to manually change every single example

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

if isinstance(SolidMatNone.dm,DensityModel) and isinstance(SolidMatModel.dm,DensityModel):
    print("density models passed")

if isinstance(SolidMatNone.km,ConductivityModel) and isinstance(SolidMatModel.km,ConductivityModel):
    print('Ks model passed')

### Liquid Material Check

vis = ViscosityModel(a=10 * units.pascal * units.second,
                     model = 'constant')

LMMod = LiquidMaterial(name='lmmod',
                              km = cond,
                              cp = 10 * units.joule / units.kg / units.kelvin,
                              dm = dens,
                              vm = vis)

LMNone = LiquidMaterial(name='lmodnon',
                               km = 10 * units.watt / units.kelvin / units.meter ,
                               cp = 10 * units.joule / units. kg / units.kelvin,
                               dm = 10 * units.kg / (units.meter ** 3), 
                               vm = 10 * units.pascal * units.second)

if isinstance(LMMod.km, ConductivityModel) and isinstance(LMMod.dm,DensityModel) and isinstance(LMMod.vm,ViscosityModel):
    print('LMMod passed')

if isinstance(LMNone.km, ConductivityModel):
    print("lnone km pass")

if isinstance(LMNone.dm,DensityModel):
    print('lmnone dm pass')

if isinstance(LMNone.vm,ViscosityModel):
    print('LMNone vm pass')