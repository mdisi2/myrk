from pyrk.materials.material import Material
from pyrk.utilities.ur import units
from pyrk.density_model import DensityModel
from pyrk.inp import validation
from pyrk.conductivity_model import ConductivityModel


class LiquidMaterial(Material):
    ''' subclass of material for liquid'''

    def __init__(self,
                 name=None,
                 k=ConductivityModel(),
                 cp=0 * units.joule / units.kg / units.kelvin,
                 dm=DensityModel(),
                 mu=0 * units.pascal * units.seconds):
        """Initalizes a material

        :param name: The name of the component (i.e., "fuel" or "cool")
        :type name: str.
        :param km: The thermal conductivity of the component
        :type km: ConductivityModel object
        :param cp: specific heat capacity, :math:`c_p`, in :math:`J/kg-K`
        :type cp: float, pint.unit.Quantity :math:`J/kg-K`
        :param dm: The density of the material
        :type dm: DensityModel object
        :param mu: dynamic viscosity(for fluid), :math:`mu`, in :math:`Pa.s`
        :type mu: float, pint.unit.Quantity :math:`Pa.s`
        """
        Material.__init__(self, name, k, cp, dm)
        self.mu = mu.to('pascal*seconds')
        validation.validate_ge("mu", mu, 0 * units.pascal * units.seconds)
