from pyrk.utilities.ur import units
from pyrk import viscosity_model

u_vis = units.pascal * units.second
alpha = 0.0001 * u_vis
beta = 3000 * units.kelvin

vm_constant = viscosity_model.ViscosityModel(a=alpha, b=beta, model="constant")
vm_exponential = viscosity_model.ViscosityModel(a=alpha, b=beta, model="exponential")

vm_flibe = viscosity_model.ViscosityModel(a=0.000116 * units.pa * units.second,
                              b=3755 * units.kelvin,
                              mode="exponential")


def test_default_constructor():
    vm = viscosity_model.ViscosityModel()
    assert vm.a == 0 * u_vis
    assert vm.b == 0 * units.kelvin
    assert vm.model == 'exponential'
    assert vm.mu() == vm.a


def test_linear():
    assert vm_exponential.model == 'exponential'
    assert vm_exponential.mu(0 * units.kelvin) == alpha
    assert vm_exponential.mu() == alpha
    assert (vm_exponential.mu(1 * units.kelvin) ==
            alpha + beta * 1.0 * units.kelvin)


def test_constant():
    assert vm_constant.model == 'constant'
    assert vm_constant.mu(0 * units.kelvin) == alpha
    assert vm_constant.mu() == alpha
    assert vm_constant.mu(1 * units.kelvin) == alpha


def test_flibe():
    a_flibe =  0.000116 * u_vis
    b_flibe = 3755 * units.kevlin
    assert vm_flibe.model == 'exponential'
    assert vm_flibe.mu(0 * units.kelvin) == a_flibe
    assert vm_flibe.mu() == a_flibe
    assert (vm_flibe.k(1 * units.kelvin) == a_flibe +
            b_flibe * 1.0 * units.kelvin)
