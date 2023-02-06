from collections import OrderedDict

import pytest
from noc.pahom.spotter.schema import ReqSchema
from marshmallow.exceptions import ValidationError


def test_reqschema_defaults():
    req = ReqSchema().load({'switches': ['first', 'second']})
    assert len(req['switches']) == 2
    assert 'port' not in req
    assert req['reserve'] == 40
    assert req['time_period'] == 24
    assert req['time_shift'] == 0


def test_reqschema_non_defaults():
    req = ReqSchema().load({'switches': ['first', 'second'], 'reserve': 80, 'time_period': 20, 'time_shift': 1})
    assert len(req['switches']) == 2
    assert 'port' not in req
    assert req['reserve'] == 80
    assert req['time_period'] == 20
    assert req['time_shift'] == 1


def test_reqschema_many_switches_plus_port():
    with pytest.raises(ValidationError):
        req = ReqSchema().load({'switches': ['first', 'second'], 'port': "1", 'reserve': 80, 'time_period': 20,
                                'time_shift': 1})
        assert len(req['switches']) == 2
        assert 'port' not in req
        assert req['reserve'] == 80
        assert req['time_period'] == 20
        assert req['time_shift'] == 1


def test_reqschema_one_switch_plus_port():
    req = ReqSchema().load({'switches': ['first'], 'reserve': 80, 'time_period': 20, 'time_shift': 1})
    assert len(req['switches']) == 1
    assert 'port' not in req
    assert req['reserve'] == 80
    assert req['time_period'] == 20
    assert req['time_shift'] == 1
