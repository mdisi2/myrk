from pyrk.utilities.ur import units
from pyrk.convective_model import ConvectiveModel
from pyrk.materials.liquid_material import LiquidMaterial
from pyrk.conductivity_model import ConductivityModel
from pyrk.viscosity_model import ViscosityModel
from pyrk.density_model import DensityModel


def test_constant_model():
    h_constant = ConvectiveModel(20 * units.W / units.meter**2 / units.kelvin)
    h1_constant = ConvectiveModel(20 * units.W / units.centimeter**2 / units.kelvin)
    assert (h_constant.h0 ==
            20 * units.W / units.meter**2 / units.kelvin)
    assert (h1_constant.h0 ==
            200000 * units.W / units.meter**2 / units.kelvin)


def test_wakao_model():
      
      k = ConductivityModel(a = 2 * units.watt / units.meter / units.kelvin,
                          b = 3 * units.watt / units.meter / units.kelvin / units.kelvin,
                          model='constant')
      mu = ViscosityModel(a=0.0001 * units.pascal * units.second,
                          b=4000 * units.kelvin,
                          model='constnat')
      cp = 1 * units.joule / units.kg / units.kelvin

      rho = DensityModel(a=10 * units.kg / pow(units.meter,3),
                         b=1 *units.kg / pow(units.meter,3) / units.kelvin,
                         model='constant')

      mat = LiquidMaterial(km=k,
                         cp=cp,
                         vm=mu,
                         dm=rho)
      
      h_wakao = ConvectiveModel(mat=mat,
                              m_flow=1 * units.kg / units.g,
                              a_flow=1 * units.meter**2,
                              length_scale=1 * units.meter,
                              model='wakao')
      assert (h_wakao.mu ==
            2 * units.pascal * units.second)
      assert (h_wakao.h(rho, 0 * units.pascal * units.second) ==
        h_wakao.h(rho, 2 * units.pascal * units.second))