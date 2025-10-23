from pyrk.utilities.ur import units
from numpy import exp

class ConductivityModel(object):
    """
    This class handles the temperature dependent thermal conductivity
    with the function k(temp).
    """

    def __init__(self,
                 a=0 * units.watt / units.kelvin / units.meter,
                 b=0 * units.watt / units.kelvin / units.meter / units.kelvin,
                 c=None,
                 d=None,
                 model="constant"):
        """
        Initializes the ConductivityModel object.

        :param model: The keyword for a model type.
        :type model: string
        :param a: first coefficient of the model - the constant term 
        :type a: float.
        :param b: first order the temp coefficient T^1.
        :type b: float
        :param c: second order the temp coefficient T^2.
        :type c: float
        :param d: second order the temp coefficient T^3.
        :type d: float
        :param celcius: first order celcius dependent term
        :type celcius: quantity 
        """
        self.a = a.to(units.watt / units.kelvin / units.meter)
        self.b = b.to(units.watt / units.kelvin / units.meter / units.kelvin)
        self.c = c
        self.d = d


        self.implemented = {'constant': self.constant,
                            'linear': self.linear,
                            'sodium': self.sodium,
                            'helium': self.helium,
                            'uoc_uo2_kernel' : self.uoc_uo2_kernel}

        if model in self.implemented.keys():
            self.model = model
        else:
            self.model = NotImplemented
            msg = "Conductivity model type "
            msg += model
            msg += " is not an implemented conductivity model. Options are:"
            for m in self.implemented.keys():
                msg += m
            raise ValueError(msg)
        
    def thermal_conductivity(self, temp=0 * units.kelvin):
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
        return self.a
    
    def linear(self, temp=0.0 * units.kelvin):
        """
        Returns a linear thermal conductivity, a + b * temp (in celcius).

        :param temp: The temperature of the object
        :type temp: float.
        """
        if temp > (273.15*units.kelvin):
            temp_c = temp - (273.15*units.kelvin)
        else:
            return self.a
        
        ret = self.a + self.b * temp_c
        return ret
    
    def sodium(self, temp=0.0 * units.kelvin):

        """Third order thermal conductivity model for the sodium 
        liquid material
        
        ###k &= 124.67 - 0.11381 \, T #b
        # + 5.5226 \times 10^{-5} \, T^2 #c
        # - 1.1842 \times 10^{-8} \, T^3 #d
        """
        
        T = (temp.to('kelvin')).magnitude
        A = 124.67
        B = -0.11381
        C = 5.5226e-5
        D = -1.1842e-8

        ret = A + B*T+ C*(T**2) + D*(T**3)

        return ret * units.watt / units.meter / units.kelvin
    
    def helium(self,T=0*units.kelvin):
        """linear fit for helium thermal conductivity
        
            0.000261 * T + 0.10144
        
        Valid for 600-1200 K

        https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote1334.pdf

        """

        a = 0.000261
        b = 0.10144

        ret = a * T + b
        return ret * (units.watt / units.kelvin / units.meter)
    
    def uoc_uo2_kernel(self,T=0*units.kelvin):
        """
        Returns thermal conductivity of a TRISO UCO/UO2 particle.

        Returns in units W/(K * m)

        T is in celcius

        Taken from https://art.inl.gov/ReportsFolder/MaterialPropertiesReport.pdf Section 5.2 
        """

        temp_c = T.to('degC')
        if temp_c < 1650:
            t_c = temp_c.magnitude
            ret = 0.0132 * exp(0.00188 * t_c) + (4040/(464+t_c))
            return ret * units.watts / units.kelvin / units.meter
        if temp_c >= 1650:
            t_c = temp_c.magnitude
            ret = 0.0132 * exp(0.00188*t_c) + 1.9
            return ret * units.watts / units.kelvin / units.meter