# coding: utf-8
import pytest
import dmp_suite.ctl as ctl
from dmp_suite.ctl import Parameter, types
from dmp_suite.ctl.exceptions import CtlError


def test_parameter():

    parameter = Parameter('load_id', types.Integer)
    assert parameter.name == 'load_id'
    assert parameter.type == types.Integer

    with pytest.raises(CtlError):
        parameter = Parameter('load_id', None)

    with pytest.raises(CtlError):
        parameter = Parameter('', types.Integer)

    parameter2 = Parameter('load_id', types.Integer)
    parameter3 = Parameter('id', types.Integer)

    assert parameter == parameter2
    assert parameter is not parameter2

    assert parameter != parameter3
    assert parameter is not parameter3


class TestDomainProvider(ctl.SimpleDomainProvider):
    def to_storage_entity(self, entity):
        return entity


class _BatchAssert(object):

    def __init__(self, expected):
        self.data = []
        self.expected = expected

    def __enter__(self):
        self.data = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.expected == self.data
        self.data = []

    def set_param(self, entity, parameter, value):
        self.data.append((entity, parameter, value))


class MockStorage(object):

    def __init__(self, expected):
        self.expected = expected

    def batch(self):
        return _BatchAssert(self.expected)


def test_implicit_batch_setter():
    entity1 = type("", (), {})()
    int_parameter1 = Parameter('parameter1', types.Integer)
    double_parameter1 = Parameter('parameter1', types.Double)

    value = 1
    mock_storage = MockStorage([(entity1, int_parameter1, value)])
    ctl_ = ctl.Ctl(mock_storage)
    # notice: each setter create and close batch object
    ctl_.set_param(entity1, int_parameter1, value)
    ctl_.set_param(
        entity1, 'parameter1', value, parameter_type=types.Integer
    )
    # change parameter type
    ctl_.set_param(
        entity1, double_parameter1, value, parameter_type=types.Integer
    )


def test_setter_with_batch():
    entity1 = type("", (), {})()
    int_parameter1 = Parameter('parameter1', types.Integer)
    double_parameter1 = Parameter('parameter1', types.Double)

    entity2 = type("", (), {})()
    int_parameter2 = Parameter('parameter2', types.Integer)
    value = 1

    mock_storage = MockStorage([
        (entity1, int_parameter1, value),
        (entity1, double_parameter1, value),
        (entity2, int_parameter2, value)
    ])
    ctl_ = ctl.Ctl(mock_storage)

    with ctl_.batch() as ctl_bach:
        ctl_.set_param(entity1, int_parameter1, value, ctl_batch=ctl_bach)
        ctl_.set_param(entity1, double_parameter1, value, ctl_batch=ctl_bach)
        ctl_.set_param(entity2, int_parameter2, value, ctl_batch=ctl_bach)

    with ctl_.batch() as ctl_bach:
        ctl_bach.set_param(entity1, int_parameter1, value)
        ctl_bach.set_param(entity1, double_parameter1, value)
        ctl_bach.set_param(entity2, int_parameter2, value)

    with ctl_.batch() as ctl_bach:
        ctl_.set_param(entity1, int_parameter1, value, ctl_batch=ctl_bach)
        ctl_.set_param(entity1, double_parameter1, value, ctl_batch=ctl_bach)
        ctl_bach.set_param(entity2, int_parameter2, value)

