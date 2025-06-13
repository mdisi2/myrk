from pyrk.materials.material import Material
from pyrk.utilities.ur import units
from pyrk.density_model import DensityModel
from pyrk.inp import validation
from pyrk.viscosity_model import ViscosityModel
from pyrk.conductive_model import ConductiveModel


class LiquidMaterial(Material):
    ''' subclass of material for liquid'''

    def __init__(self,
                 name=None,
                 km=ConductiveModel,
                 cp=0 * units.joule / units.kg / units.kelvin,
                 dm=DensityModel(),
                 vm=ViscosityModel()):
        """Initalizes a material

        :param name: The name of the component (i.e., "fuel" or "cool")
        :type name: str.
        :param k: The thermal conductivity of the component
        :type k: float, pint.unit.Quantity :math:'watt/meter/K'
        :param cp: specific heat capacity, :math:`c_p`, in :math:`J/kg-K`
        :type cp: float, pint.unit.Quantity :math:`J/kg-K`
        :param dm: The density of the material
        :type dm: DensityModel object
        :param mu: dynamic viscosity(for fluid), :math:`mu`, in :math:`Pa.s`
        :type mu: float, pint.unit.Quantity :math:`Pa.s`
        """
        Material.__init__(self, name, km, cp, dm)
        self.vm = vm

    def mu(self, temp):
        """
        The dynamic viscosity of this material as a function of temperature.

        :param temp: the temperature at which to query the dynamic viscosity
        :type temp: float, pint.unit.Quantity :math:`K`
        :return: the dynamic viscosity of this component
        :rtype: float, in units of :math:`Pa.s`
        """
        ret = self.vm.mu(temp)
        return ret
