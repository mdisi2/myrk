from pyrk.utilities.ur import units
from pyrk.materials.liquid_material import LiquidMaterial


class ConvectiveModel(object):
    """
    This class defines the model for convective heat transfer coefficient: h

    Only use the Wakao model if convection is between pebbles and coolant,
    the correlation is not for reflector walls or anything that isn't a pebble.  
    """

    def __init__(self,
                 h0=0 * units.watt / units.meter**2 / units.kelvin,
                 mat=LiquidMaterial(),
                 m_flow=None,
                 a_flow=None,
                 length_scale=None,
                 T0 = None,
                 model="constant"):
        """
        Initializes the ConductivityModel object.

        :param h0: convective heat transfer coefficient when it's a constant
        :type h0: double
        :param mat: material of the fluid
        :type mat: Material object
        :param m_flow: mass flow rate
        :type m_flow: double
        :param a_flow: flow cross section surface area
        :type a_flow: double
        :param length_scale: heat transfer length scale
        :type length_scale: double
        :param T0: initial temperature of coolant
        :type T0: quantity with units.kelvin
        :param model: The keyword for a model type, implemented types are
        'constant' and 'wakao'
        :type model: string
        """
        self.h0 = h0
        self.km = mat.km
        self.cp = mat.cp
        self.vm = mat.vm
        self.dm = mat.dm
        self.m_flow = m_flow
        self.a_flow = a_flow
        self.length_scale = length_scale
        self.T0 = T0


        self.implemented = {'constant': self.constant,
                            'wakao': self.wakao}
        
        if T0 is None and model != 'constant' :
            raise ValueError('Convection Model Needs Initial Coolant Temp (K)')

        if model in self.implemented.keys():
            self.model = model
        else:
            self.model = NotImplemented
            msg = "Convective heat transfer model type "
            msg += model
            msg += " is not an implemented convective model. Options are:"
            for m in self.implemented.keys():
                msg += m
            raise ValueError(msg)

    def h(self,
          temp = 0.0 * units.kelvin,
          rho=0 * units.kg / units.meter**3,
          mu=0 * units.pascal * units.second,
          k=0 * units.watt / units.kelvin / units.meter):
        """
        Returns the convective heat transfer coefficient

        If temp is provided, it will use properties from models
        If not, it will use the input properties

        :param temp: the fluid temperature
        :type temp: float
        :param rho: The density of the object
        :type rho: float
        :param mu: The dynamic viscosity of the object
        :type mu: float
        :param k: The thermal conductivity of the object
        :type k: float
        """


        return self.implemented[self.model](temp.to(units.kelvin),
                                            rho.to(units.kg / units.meter**3),
                                            mu.to(units.pascal * units.second),
                                            k.to(units.watt / units.kelvin / units.meter))

    def constant(self, 
                 temp=None, 
                 rho=None, 
                 mu=None,
                 k=None):
        """
        Returns a constant heat transfer coefficient: h0

        """
        return self.h0
    
### ====================================================================================================
### ====================================================================================================
### Wakao Model
### Material Property Attributes
    
    def mu(self,temp):
        """returns the dynamic viscosity of the liquid passed in the
        current convective model at the given temp
        
        :param temp: Temperature at which to query dynamic viscosity
        :temp type: Quantity units.kelvin
        :return: thermal viscosity
        :rtype: Quantity units $Pa /cdot s$ 
        """
        
        return self.vm.mu(temp)

    def k(self,temp):
        """
        returns the thermal conductivity of the fluid passed
        in the current convective model at the given temp

        :param temp: temperature to query conductivity
        :temp type: quantity units.kelvin
        :return: conductivity of fluid
        :rtype: quantity units $W/K/m$
        
        """

        return self.km.k(temp)
    
    def rho(self,temp):
        """
        returns the density of the fluid passed
        in the current convective model at the given temp

        :param temp: temperature to query density
        :temp type: quantity units.kelvin
        :return: density of fluid
        :rtype: quantity units $Kg/m^3$
        
        """

        return self.dm.rho(temp)
    
    def wakao(self,
              temp=None,
              rho=0.0 * (units.kg / units.meter**3),
              mu=0.0* (units.pascal * units.second),
              k=0.0 * (units.watt / units.kelvin / units.meter)):

        """
        This function implements the Wakao correlation for convective heat
        transfer coefficient
        :param temp: The temperature to query the model
        :type temp: float
        :param rho: The density of the object
        :type rho: float
        :param mu: The dynamic viscosity of the object
        :type mu: float
        :param k: the thermal conductivity of the object
        :type k: float
        """
        # Use temperature-dependent properties if temp is provided
        if temp.magnitude == 0.0:
            # First timestep case - use initial temperature
            rho = self.rho(self.T0)
            mu = self.mu(self.T0)
            k = self.k(self.T0)
        else:
            # Use temperature-dependent properties
            rho = self.rho(temp)
            mu = self.mu(temp)
            k = self.k(temp)
        
        u = self.m_flow / self.a_flow / rho
        Re = rho * self.length_scale * u / mu
        Pr = self.cp * mu / k
        Nu = 2 + 1.1 * Pr.magnitude ** (1 / 3.0) * Re.magnitude**0.6
        ret = Nu * k / self.length_scale
        
        return ret