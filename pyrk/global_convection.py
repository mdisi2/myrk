from pyrk.utilities.ur import units
from pyrk.convective_model import ConvectiveModel
from pyrk.materials.liquid_material import LiquidMaterial


class GlobalConvection(object):
    
    """
    This class is meant to 'hold' and store convection model information
    and array for refrence in other classes

    example: THComponent of moderator and fuel needs the convection coeff 
    but hm is being loaded in coolant THComponent - easy since all pebbles should
    be same radius and have the same h, it can be stored here for use of all pebbles 


    So this class would be set in the input file connected to the coolant, and then it would 
    be passed into the solid pebble material thermal component classes for refrence.   

    Probably will be called after update_temp or something 
    """

    def __init__(self,
                 name='cool',
                 mat =LiquidMaterial(),
                 rad =0.0 * units.meter,
                 hm  =ConvectiveModel()):
        
        self.name = name
        self.mat  = mat
        self.dm   = mat.dm
        self.vm   = mat.vm
        self.km   = mat.km
        self.rad  = rad
        self.hm   = hm
        
        """
        :param name: Name of component
        :type name: Stirng
        :param mat: Liquid Material (Coolant)
        :type mat: Object Class LiquidMaterial
        :param T0: Initial fluid temperature
        :type T0: Quantity 
        :param rad: radius of pebble 
        :type rad: Quantity * units.meter
        :param timer: The timer instance for the sim
        :type timer: Timer() object
        :param hm: Convective Model
        :type hm: Convection Object 
        """

    # Will not be using property arrays, simply return the calculation
    # when asked. You thought about it and can't really articulate it, but
    # this is the best way. Storing it as an array forces uniform temperature
    # while just being a method that returns the correct h value for any temp when
    # called. There will be no notion of time or timestep, all we WANT is 
    # value by its self. Trust


    def fluid_mu(self,temp=0.0*units.kelvin):
        """returns the coolant's dynamic viscosity at the provided temp
        
        :param temp: temperature to query mu
        :param type: pint quantity units.kelvin
        :rtype: pint qunatity pascal * seconds
        """

        ret = self.vm.mu(temp)
        return ret
    
    def fluid_k(self,temp=0.0*units.kelvin):
        """returns the coolant's thermal conduction at the provided temp
        
        :param temp: temperature to query k
        :param type: pint quantity units.kelvin
        :rtype: pint quantity units watt / meter / kelvin
        """

        ret = self.km.k(temp)
        return ret
    
    def fluid_rho(self,temp=0.0*units.kelvin):
        """returns the coolant's density at the provided temp
        
        :param temp: temperature to query rho
        :param type: pint quantity units.kelvin
        :rtype: pint qunatity units kg / meter^3
        """

        ret = self.dm.rho(temp)
        return ret
        
    def fluid_h(self,temp=0.0*units.kelvin):
        """returns the convection coefficient (h) at the provided temp
        
        :param temp: temperature to query (h)
        :param type: pint quantity units.kelvin
        :rtype: pint qunatity units watt / meter^2 / kelvin
        """

        ret = self.hm.h(rho = self.dm.rho(temp),
                        mu = self.vm.mu(temp),
                        k = self.km.k(temp))
        return ret