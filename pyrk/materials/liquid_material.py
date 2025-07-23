from pyrk.materials.material import Material
from pyrk.utilities.ur import units
from pyrk.density_model import DensityModel
from pyrk.viscosity_model import ViscosityModel
from pyrk.conductivity_model import ConductivityModel
from pint.errors import DimensionalityError


class LiquidMaterial(Material):
    ''' 
    Subclass of material for liquid.
    Has an additional attribute for 
    dynamic viscosity (mu).
        '''

    def __init__(self,
                 name=None,
                 km=ConductivityModel(),
                 cp=0 * units.joule / units.kg / units.kelvin,
                 dm=DensityModel(),
                 vm=ViscosityModel()):
        """Initalizes a material

        :param name: The name of the component (i.e., "fuel" or "cool")
        :type name: str.
        :param km: The thermal conductivity of the component
        :type km: ConductivityModel object, pint.unit.Quantity :math:'watt/meter/K'
        :param cp: specific heat capacity, :math:`c_p`, in :math:`J/kg-K`
        :type cp: float, pint.unit.Quantity :math:`J/kg-K`
        :param dm: The density of the material
        :type dm: DensityModel object
        :param vm: dynamic viscosity(for fluid), :math:`mu`, in :math:`Pa.s`
        :type vm: ViscosityModel object, pint.unit.Quantity :math:`Pa.s`
        """
        Material.__init__(self, name, km, cp, dm)
        
        # Quantity Case
        if not isinstance(vm,ViscosityModel):
            if hasattr(vm,'units'):
                try:
                    vm.to('pascal * second')
                except DimensionalityError:
                    raise ValueError("Dynamic Viscosity must have units of" \
                    " \n pascal *  second")
            self.vm = ViscosityModel(a=vm,
                                    model='constant')
        else:
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