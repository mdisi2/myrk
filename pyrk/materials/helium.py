from pyrk.utilities.ur import units
from pyrk.density_model import DensityModel
from pyrk.conductivity_model import ConductivityModel
from pyrk.materials.liquid_material import LiquidMaterial
from pyrk.viscosity_model import ViscosityModel

class Helium(LiquidMaterial):
    """https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote1334.pdf
    
    https://x-energy.com/reactors/xe-100
    """

    def __init__(self, name="helium"):
        """Initalizes a material

        :param name: The name of the component (i.e., "fuel" or "cool")
        :type name: str.
        """
        LiquidMaterial.__init__(self,
                                name=name,
                                k=self.thermal_conductivity(),
                                cp=self.specific_heat_capacity(),
                                dm=self.density())

    def thermal_conductivity(self):
        """helium thermal conductivity in [W/m-K]
        """
        return ConductivityModel(model='helium')

    def specific_heat_capacity(self):
        """Specific heat capacity of helium [J/kg/K]
        """
        return 5.190 * units.joule / (units.kg * units.kelvin)

    def density(self):
        """
        Helium density as a funciton of T. [kg/m^3]

        """
        return DensityModel(model="helium")
    
    def dynamic_viscosiy(self):
        """
        FLiBE dynamic viscosity as a function of T. [Pa * s]
        """
        return ViscosityModel(model='helium')
    
    #TODO pressure 
    #def pressure(self):
    #   return pv = nrt
    # Pressure in Xe-100 is meant to be 6 MPa