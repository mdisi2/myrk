from pyrk.utilities.ur import units
from pyrk import conductivity_model

u_cond = units.watt / units.meter / units.kelvin
alpha = 2.0 * u_cond
beta = 3.0 * u_cond / units.kelvin

km_constant = conductivity_model.ConductivityModel(a=alpha, b=beta, model="constant")
km_linear = conductivity_model.ConductivityModel(a=alpha, b=beta, model="linear")

km_flibe = conductivity_model.ConductivityModel(a = 0.7662 * units.watt / (units.meter * units.kelvin),
                               b = 0.0005 * units.watt / (units.meter * units.kelvin * units.kelvin),
                               model="linear")


def test_default_constructor():
    km = conductivity_model.ConductivityModel()
    assert km.a == 0 * u_cond
    assert km.b == 0 * u_cond / units.kelvin
    assert km.model == 'linear'
    assert km.k() == km.a


def test_linear():
    assert km_linear.model == 'linear'
    assert km_linear.k(0 * units.kelvin) == alpha
    assert km_linear.k() == alpha
    assert (km_linear.k(1 * units.kelvin) ==
            alpha + beta * 1.0 * units.kelvin)


def test_constant():
    assert km_constant.model == 'constant'
    assert km_constant.k(0 * units.kelvin) == alpha
    assert km_constant.k() == alpha
    assert km_constant.k(1 * units.kelvin) == alpha


def test_flibe():
    a_flibe =  0.7662 * u_cond
    b_flibe = 0.0005 * u_cond / units.kelvin
    assert km_flibe.model == 'linear'
    assert km_flibe.k(0 * units.kelvin) == a_flibe
    assert km_flibe.k() == a_flibe
    assert (km_flibe.k(1 * units.kelvin) == a_flibe +
            b_flibe * 1.0 * units.kelvin)
    