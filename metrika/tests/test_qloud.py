import os

import metrika.pylib.qloud as muq
import metrika.pylib.structures.dotdict as mdd


def test_am_i_in_qloud(monkeypatch):
    environ = {'QLOUD_DISCOVERY_INSTANCE': 'Awesome'}
    monkeypatch.setattr(os, 'environ', environ)

    assert muq.am_i_in_qloud() is True

    environ = mdd.DotDict()
    monkeypatch.setattr(os, 'environ', environ)

    assert muq.am_i_in_qloud() is False


def test_get_qloud_info(monkeypatch):
    environ = {
        'QLOUD_DISCOVERY_INSTANCE': 'Awesome',
        'QLOUD_QLOUD_HELLO': 'World',
    }
    monkeypatch.setattr(os, 'environ', environ)

    info = muq.get_qloud_info()

    assert type(info) is mdd.DotDict
    assert info.discovery_instance == 'Awesome'
    assert info.qloud_hello == 'World'
