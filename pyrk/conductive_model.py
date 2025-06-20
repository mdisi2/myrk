from pyrk.utilities.ur import units

class ConductiveModel(object):
    """
    This class handles the temperature dependent thermal conductivity
    with the function k(temp).
    """

    def __init__(self,
                 a=0 * units.watt / units.kelvin / units.meter,
                 b=0 * units.watt / pow(units.kelvin, 2) / units.meter,
                 model="constant"):
        """
        Initializes the ConductiveModel object.

        :param model: The keyword for a model type.
        :type model: string
        :param a: first coefficient of the model
        :type a: float.
        :param b: second coefficient of the model.
        :type b: float
        """
        self.a = a.to(units.watt / units.kelvin / units.meter)
        self.b = b.to(units.watt / units.kelvin / units.meter / units.celcius)

        self.implemented = {'constant': self.constant,
                            'linear': self.linear}

        if model in self.implemented.keys():
            self.model = model
        else:
            self.model = NotImplemented
            msg = "Conductive model type "
            msg += model
            msg += " is not an implemented conductive model. Options are:"
            for m in self.implemented.keys():
                msg += m
            raise ValueError(msg)
        
    def k(self, temp=0 * units.kelvin):
        """
        Returns the thermal conductivity based on the temperature.

        :param temp: the temperature
        :type temp: float.
        """
        return self.implemented[self.model](temp)
    
    def constant(self, temp=0 * units.kelvin):
        """
        Returns a constant thermal conductivity, a.

        :param temp: The temperature of the object
        :type temp: float.
        """
        return 1 * units.watt / units.meter / units.kelvin
    
    def linear(self, temp=0.0 * units.kelvin):
        """
        Returns a linear thermal conductivity, a + b * temp (in celcius).

        :param temp: The temperature of the object
        :type temp: float.
        """

        T_celcius = (temp.magnitude - 273.15) * units.celcius
        ret = self.a + self.b * T_celcius
        return ret 