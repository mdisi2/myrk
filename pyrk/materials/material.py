from pyrk.inp import validation
from pyrk.utilities.ur import units
from pyrk.density_model import DensityModel
from pyrk.conductivity_model import ConductivityModel


class Material(object):
    """This class represents a material. Its attributes are material properties
    and behaviors."""

    def __init__(self,
                 name=None,
                 k=ConductivityModel(),
                 cp=0 * units.joule / units.kg / units.kelvin,
                 dm=DensityModel()):
        """Initalizes a material

        :param name: The name of the component (i.e., "fuel" or "cool")
        :type name: str.
        :param km: The thermal conductivity of the component
        :type km: ConductivityModel object
        :param cp: specific heat capacity, :math:`c_p`, in :math:`J/kg-K`
        :type cp: float, pint.unit.Quantity :math:`J/kg-K`
        :param dm: The density of the material
        :type dm: DensityModel object
        """
        self.name = name
        self.cp = cp.to('joule/kg/kelvin')
        validation.validate_ge(
            "cp", cp, 0 * units.joule / units.kg / units.kelvin)
        self.dm = dm

        if isinstance(k, ConductivityModel):
            self.k = k
        else:
            assert k.units == (units.watts / units.meter / units.kelvin), "k must be watts/meter/kelvin"
            self.k = ConductivityModel(model='constant', 
                                       a=k)

    def rho(self, temp):
        """
        The density of this material as a function of temperature.

        :param temp: the temperature
        :type temp: pint quantity in units.kelvin
        :return: the density of this component
        :rtype: float, in units of :math:`kg/m^3`
        """
        ret = self.dm.rho(temp)
        return ret

    def thermal_conductivity(self, temp):
        """
        The conductivity (k) of of this material as a function of temperature

        :param temp: the temperature
        :type temp: pint quantity in units.kelvin
        :return: the conductivity (k) of this component
        :rtype: pint quantity in units watts / meter / kelvin
        """

        if hasattr(temp, 'units') and temp.units == units.kelvin:
            t = temp
        else:
            t = temp * units.kelvin

        ret = self.k.thermal_conductivity(t)
        return ret