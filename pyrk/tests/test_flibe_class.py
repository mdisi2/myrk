from pyrk.utilities.ur import units
from pyrk.materials.material import Material
from pyrk.materials.flibe import Flibe


mat = Flibe()
T0 = 1400 * units.kelvin
T1 = 1500 * units.kelvin

print(f"k0 = {mat.km.k(T0)} \n k1 = {mat.km.k(T1)}")