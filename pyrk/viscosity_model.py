from pyrk.utilities.ur import units
from numpy import exp

class ViscosityModel(object):
    """
    This class handles the temperature dependent
    dynamic viscosity with the function mu(temp).
    """

    def __init__(self,
                 a=0 * units.pascal * units.second,
                 b=0 * units.kelvin,
                 model="constant"):
        """
        Initializes the ViscosityModel object.

        :param model: The keyword for a model type.
        :type model: string
        :param a: first coefficient of the model
        :type a: float.
        :param b: second coefficient of the model.
        :type b: float
        """
        self.a = a.to(units.pascal * units.second)
        self.b = b.to(units.kelvin)

        self.implemented = {'constant': self.constant,
                            'exponential': self.exponential}

        if model in self.implemented.keys():
            self.model = model
        else:
            self.model = NotImplemented
            msg = "Viscosity model type "
            msg += model
            msg += " is not an implemented viscosity model. Options are:"
            for m in self.implemented.keys():
                msg += m
            raise ValueError(msg)
        
    def mu(self, temp=0 * units.kelvin):
        """
        Returns the dynamic viscosity based on the temperature.

        :param temp: the temperature
        :type temp: float.
        """
        return self.implemented[self.model](temp)
    
    def constant(self, temp=0 * units.kelvin):
        """
        Returns a constant dynamic viscosity, a.

        :param temp: The temperature of the object
        :type temp: float.
        """
        temp = temp.to(units.kelvin)
        ret = self.a * exp(self.b / (950 * units.kelvin) )
        return ret
    
    def exponential(self, temp=0.0 * units.kelvin):
        """
        Returns an exponential dynamic viscosity, a * exp(b / temp).

        :param temp: The temperature of the object
        :type temp: float.
        """
        temp = temp.to(units.kelvin)
        ret = self.a * exp(self.b / temp)
        return ret