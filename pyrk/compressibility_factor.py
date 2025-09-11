### Placeholder for the compressibility factor model

from pyrk.utilities.ur import units

class CompressibilityFactor(object):
    """  
    This class has a public api supporting just one function, cf(temp).
    If the temperature is irrelevant to the model, so be it!!!!!!!!!!!!!
    """

    def __init__(self,k):
        pass

class PvnrtModel(object):
    """  
    This class has a public api supporting just one function, p(temp).
    If the temperature is irrelevant to the model, so be it!!!!!!!!!!!!!
    """


    #### Might have to be written outside the object since 