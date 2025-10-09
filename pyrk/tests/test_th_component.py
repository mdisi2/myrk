from __future__ import print_function
import pytest

import pyrk.th_component as th
from pyrk.utilities.ur import units
from pyrk.timer import Timer
from pyrk.materials.material import Material
from pyrk import density_model
from pyrk import conductivity_model

name = "testname"
vol = 20 * units.meter**3
k = conductivity_model.ConductivityModel(a=1 * units.watt / units.meter /
                                         units.kelvin,
                                         b=1 * units.watt / units.meter /
                                         units.kelvin / units.kelvin,
                                         model='linear')
cp = 10 * units.joule / units.kg / units.kelvin
dm = density_model.DensityModel(a=0 * units.kg / units.meter**3,
                                b=100 * units.kg / units.kelvin /
                                pow(units.meter, 3),
                                model='linear')
mat = Material(k=k, cp=cp, dm=dm)


kappa = 0
T0 = 700 * units.kelvin
t0 = 0 * units.seconds
tf = 10 * units.seconds
tfeedback = 5 * units.seconds
dt = 0.1 * units.seconds
ti = Timer(t0=t0, tf=tf, dt=dt, t_feedback=tfeedback)
tester = th.THComponent(name=name, mat=mat, vol=vol, T0=T0, timer=ti)
tester_sph = th.THComponent(name=name, mat=mat, vol=vol, T0=T0, timer=ti,
                            sph=True, ri=0 * units.meter, ro=1 * units.meter)


def test_constructor():
    assert tester.name == name
    assert tester.vol == vol
    assert tester.k(0) == k.thermal_conductivity(T0)
    assert tester.rho(0) == dm.rho(T0)
    assert tester.T0 == T0


def test_temp():
    assert tester.temp(0) == T0


def test_update_temp():
    assert tester.temp(0) == T0
    T1 = 10 * units.kelvin
    T2 = 20 * units.kelvin
    tester.update_temp(1, T1)
    assert tester.temp(1) == T1
    tester.update_temp(2, T2)
    assert tester.temp(2) == T2


def test_dtemp():
    T1 = 20 * units.kelvin
    tester.update_temp(ti.t_idx_feedback, T1)
    time1 = ti.t_idx(4 * units.seconds)
    assert tester.dtemp(time1) == tester.T[time1] - T1

    T2 = 50 * units.kelvin
    tester.update_temp(time1 - 1, T2)
    print(tester.T[time1 - 1])
    assert tester.dtemp(time1) == T2 - tester.T[ti.t_idx_feedback]


def test_meshing():
    with pytest.raises(TypeError) as excinfo:
        tester.mesh(2)
    assert excinfo.type is TypeError
    with pytest.raises(ValueError) as excinfo:
        tester_sph.mesh(2)
    assert excinfo.type is ValueError
    l = 0.2 * units.meter
    mesh_list = tester_sph.mesh(l)
    assert mesh_list[0].ro - mesh_list[0].ri == l