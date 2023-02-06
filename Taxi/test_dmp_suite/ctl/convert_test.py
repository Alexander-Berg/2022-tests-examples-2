# coding: utf-8
import inspect

import pytest
from dmp_suite.ctl.convert.string_based import (
    skip_null, create_service, TRUE_STRING, FALSE_STRING,
    StringBasedConversionService)
from dmp_suite.ctl import types
from dmp_suite.ctl.exceptions import ConversionError, ConverterNotFoundError
from datetime import datetime


def get_one(v):
    if v is None:
        raise ValueError
    return 1


def test_skip_null():
    with pytest.raises(ValueError):
        get_one(None)

    decorated_fn = skip_null(get_one)
    assert decorated_fn(None) is None
    assert decorated_fn(0) == 1
    assert decorated_fn(1) == 1


@pytest.fixture(scope="module")
def conversion_service():
    return create_service()


@pytest.mark.parametrize('parameter_type, value, output', [
    (None, None, ConversionError),
    (None, 10, ConversionError),
    (None, 'some string', ConversionError),

    (types.Boolean, None, None),
    (types.Boolean, '', None),
    (types.Boolean, True, TRUE_STRING),
    (types.Boolean, 1, TRUE_STRING),
    (types.Boolean, False, FALSE_STRING),
    (types.Boolean, 0, FALSE_STRING),
    (types.Boolean, 'some string', TRUE_STRING),

    (types.Integer, None, None),
    (types.Integer, '', None),
    (types.Integer, 10, '10'),
    (types.Integer, -10, '-10'),
    (
        types.Integer,
        123456789012345678901234567890,
        '123456789012345678901234567890'
    ),

    (types.Double, None, None),
    (types.Double, '', None),
    (types.Double, 10.5, '10.5'),
    (types.Double, -10.5, '-10.5'),
    (types.Double, 123456.789, '123456.789'),

    (types.String, None, None),
    (types.String, '', None),
    (types.String, '10', '10'),
    (types.String, '-10', '-10'),
    (types.String, '10.2', '10.2'),
    (types.String, 'some string', 'some string'),
    (types.String, '2019-05-06', '2019-05-06'),

    (types.Date, None, None),
    (types.Date, '', None),
    (types.Date, datetime(2019, 5, 6), '2019-05-06'),

    (types.DateTime, None, None),
    (types.DateTime, '', None),
    (types.DateTime, datetime(2019, 5, 6), '2019-05-06 00:00:00'),
    (types.DateTime, datetime(2019, 5, 6, 10, 0, 20), '2019-05-06 10:00:20'),

    (types.DatetimeMicroseconds, None, None),
    (types.DatetimeMicroseconds, '', None),
    (
        types.DatetimeMicroseconds,
        datetime(2019, 5, 6),
        '2019-05-06 00:00:00.000000'
    ),
    (
        types.DatetimeMicroseconds,
        datetime(2019, 5, 6, 10, 0, 20),
        '2019-05-06 10:00:20.000000'
    ),
    (
        types.DatetimeMicroseconds,
        datetime(2019, 5, 6, 10, 0, 20, 123456),
        '2019-05-06 10:00:20.123456'
    ),
])
def test_encode(conversion_service, parameter_type, value, output):
    if output is None:
        assert conversion_service.encode(parameter_type, value) is None
    elif inspect.isclass(output):
        with pytest.raises(output):
            conversion_service.encode(parameter_type, value)
    else:
        assert output == conversion_service.encode(parameter_type, value)


@pytest.mark.parametrize('parameter_type, value, output', [
    (None, None, ConversionError),
    (None, 10, ConversionError),
    (None, 'some string', ConversionError),

    (types.Boolean, None, None),
    (types.Boolean, '', None),
    (types.Boolean, TRUE_STRING, True),
    (types.Boolean, FALSE_STRING, False),
    (types.Boolean, 'some string', ConversionError),
    (types.Boolean, 10, ConversionError),
    (types.Boolean, 10.0, ConversionError),
    (types.Boolean, True, ConversionError),

    (types.Integer, None, None),
    (types.Integer, '', None),
    (types.Integer, '10', 10),
    (types.Integer, '-10', -10),
    (types.Integer, '10.0', ConversionError),
    (types.Integer, 10, ConversionError),
    (types.Integer, 10.0, ConversionError),
    (types.Integer, True, ConversionError),
    (types.Integer, 'some string', ConversionError),

    (types.Double, None, None),
    (types.Double, '', None),
    (types.Double, '10', 10.0),
    (types.Double, '10.2', 10.2),
    (types.Double, 10, ConversionError),
    (types.Double, 10.0, ConversionError),
    (types.Double, True, ConversionError),
    (types.Double, 'some string', ConversionError),

    (types.String, None, None),
    (types.String, '', None),
    (types.String, '10', '10'),
    (types.String, '-10', '-10'),
    (types.String, '10.2', '10.2'),
    (types.String, 'some string', 'some string'),
    (types.String, '2019-05-06', '2019-05-06'),
    (types.String, 10, ConversionError),
    (types.String, 10.0, ConversionError),
    (types.String, True, ConversionError),

    (types.Date, None, None),
    (types.Date, '', None),
    (types.Date, '2019-05-06', datetime(2019, 5, 6)),
    (types.Date, '2019-50-06', ConversionError),
    (types.Date, '04-06-2019', ConversionError),
    (types.Date, 'some string', ConversionError),
    (types.Date, '12345', ConversionError),
    (types.Date, 10, ConversionError),
    (types.Date, 10.0, ConversionError),
    (types.Date, True, ConversionError),

    (types.DateTime, None, None),
    (types.DateTime, '', None),
    (types.DateTime, '2019-05-06', datetime(2019, 5, 6)),
    (types.DateTime, '2019-05-06 10:00:20', datetime(2019, 5, 6, 10, 0, 20)),
    (types.DateTime, '2019-50-06', ConversionError),
    (types.DateTime, '04-06-2019', ConversionError),
    (types.DateTime, 'some string', ConversionError),
    (types.DateTime, '12345', ConversionError),
    (types.DateTime, 10, ConversionError),
    (types.DateTime, 10.0, ConversionError),
    (types.DateTime, True, ConversionError),

    (types.DatetimeMicroseconds, None, None),
    (types.DatetimeMicroseconds, '', None),
    (types.DatetimeMicroseconds, '2019-05-06', datetime(2019, 5, 6)),
    (
        types.DatetimeMicroseconds,
        '2019-05-06 10:00:20',
        datetime(2019, 5, 6, 10, 0, 20)
    ),
    (
        types.DatetimeMicroseconds,
        '2019-05-06 10:00:20.123456',
        datetime(2019, 5, 6, 10, 0, 20, 123456)
    ),
    (types.DatetimeMicroseconds, '2019-50-06', ConversionError),
    (types.DatetimeMicroseconds, '04-06-2019', ConversionError),
    (types.DatetimeMicroseconds, 'some string', ConversionError),
    (types.DatetimeMicroseconds, '12345', ConversionError),
    (types.DatetimeMicroseconds, 10, ConversionError),
    (types.DatetimeMicroseconds, 10.0, ConversionError),
    (types.DatetimeMicroseconds, True, ConversionError),
])
def test_decode(conversion_service, parameter_type, value, output):
    if output is None:
        assert conversion_service.decode(parameter_type, value) is None
    elif inspect.isclass(output):
        with pytest.raises(output):
            conversion_service.decode(parameter_type, value)
    else:
        assert output == conversion_service.decode(parameter_type, value)


def test_wrap_converter_error():
    service = StringBasedConversionService()

    def generate_error(v):
        raise RuntimeError()

    parameter_type = types.String
    service.register(
        parameter_type=parameter_type,
        decoder=generate_error,
        encoder=generate_error
    )

    with pytest.raises(ConversionError):
        service.decode(parameter_type, 'some string')

    with pytest.raises(ConversionError):
        service.encode(parameter_type, 'some string')

    # do not wrap system exception
    with pytest.raises(TypeError):
        service.encode(parameter_type) # skip value (required)


def test_string_contract():
    service = StringBasedConversionService()
    parameter_type = types.Integer
    service.register(
        parameter_type=parameter_type,
        decoder=lambda v: v,
        encoder=lambda v: 0
    )

    with pytest.raises(ConversionError):
        service.decode(parameter_type, 1)

    with pytest.raises(ConversionError):
        service.encode(parameter_type, 'some string')


def test_register_type():
    service = StringBasedConversionService()

    with pytest.raises(Exception):
        service.register(
            parameter_type=None,
            decoder=skip_null(int),
            encoder=skip_null(str)
        )

    with pytest.raises(Exception):
        service.register_converter(
            parameter_type=types.Integer,
            converter=None
        )

    with pytest.raises(Exception):
        service.unregister(None)

    assert not service.is_supported(types.Integer)
    with pytest.raises(ConverterNotFoundError):
        service.encode(types.Integer, 10)

    assert not service.is_supported(types.Double)
    with pytest.raises(ConverterNotFoundError):
        service.encode(types.Double, 10.0)

    service.register(
        parameter_type=types.Integer,
        decoder=skip_null(int),
        encoder=skip_null(str)
    )

    assert service.is_supported(types.Integer)
    assert service.encode(types.Integer, 10)

    assert not service.is_supported(types.Double)
    with pytest.raises(ConverterNotFoundError):
        service.encode(types.Double, 10.0)

    service.unregister(types.Integer)
    assert not service.is_supported(types.Integer)
    with pytest.raises(ConverterNotFoundError):
        service.encode(types.Integer, 10)
