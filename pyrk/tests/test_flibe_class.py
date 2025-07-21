from pyrk.utilities.ur import units
from pyrk.materials.flibe import Flibe
from pyrk.materials.liquid_material import LiquidMaterial
from pyrk.materials.material import Material 
from pyrk.density_model import DensityModel
from pyrk.conductivity_model import ConductivityModel

import math

mat = Flibe()

if (isinstance(mat, LiquidMaterial)):
    print('Flibe is a LiquidMaterial')
else:
    print("Epic Fail Buddy")

if getattr(mat,'vm'):
    print('has vm')
else:
    print("no vm")

if getattr(mat,'km'):
    print("has convection model")
else:
    print('no convection model')

T0 = 873.15 * units.kelvin
T1 = 973.15 * units.kelvin

# Model Check
print(f"k0 = {mat.km.k(T0)} \n k1 = {mat.km.k(T1)}")
print(f"m0 = {mat.vm.mu(T0)} \n m1 = {mat.vm.mu(T1)}")
print(f"rho0 = {mat.dm.rho(T0)} \n rho2 = {mat.dm.rho(T1)}")



# Solid Mateiral
k_mod = ConductivityModel(a=17*units.watt 
                        / (units.meter * units.kelvin), model="constant")
cp_mod = 1650.0 * units.joule / (units.kg * units.kelvin)
rho_mod = DensityModel(a=1740. * units.kg / (units.meter**3), model="constant")
Moderator = Material('mod', k_mod, cp_mod, rho_mod)

if (isinstance(Moderator, Material)):
    print('Moderator is a Material')
else:
    print("Moderator failed material check")

if getattr(Moderator, 'dm') and getattr(Moderator, 'km'):
    print('Moderator passed model check')
else:
    print("Moderator failed model check")

if getattr(Moderator, 'vm', None):
    print('Why does a solid have viscosity')
else:
    print('Solid Moderator has no viscosity model - Good!')