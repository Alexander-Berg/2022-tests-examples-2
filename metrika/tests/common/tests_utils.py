import contextlib

import pytest

import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.bishop.utils as bp_utils


class TestUtilsException(Exception):
    pass


@contextlib.contextmanager
def does_not_raise():
    yield


def test_convert_variable_value():
    pairs = {
        'integer': 'adsf',
        'json': '{"hellO:adsf}',
    }
    for _type, value in pairs.items():
        with pytest.raises(dce.ValidationError):
            bp_utils.convert_variable_value(_type, value)

    assert bp_utils.convert_variable_value('integer', '123') == 123
    assert bp_utils.convert_variable_value('string', 123) == '123'
    assert bp_utils.convert_variable_value('json', '["1", "2"]') == ["1", "2"]


def test_split_to_env_parts_calls_validate(monkeypatch):
    def mock_validate_env_string(string):
        raise TestUtilsException("check function was called")

    monkeypatch.setattr(bp_utils, 'validate_env_string', mock_validate_env_string)

    with pytest.raises(TestUtilsException):
        bp_utils.split_to_env_parts('aaa.bbb')


@pytest.mark.parametrize(
    "value,result",
    [
        ('', pytest.raises(dce.ValidationError)),
        (',', pytest.raises(dce.ValidationError)),
        ('..', pytest.raises(dce.ValidationError)),
        ('-aa', pytest.raises(dce.ValidationError)),
        ('-aa.bb', pytest.raises(dce.ValidationError)),
        ('aa-', pytest.raises(dce.ValidationError)),
        ('aa-.bb', pytest.raises(dce.ValidationError)),
        ('a.b', pytest.raises(dce.ValidationError)),
        ('aa.b', pytest.raises(dce.ValidationError)),
        ('.b', pytest.raises(dce.ValidationError)),
        ('b.', pytest.raises(dce.ValidationError)),
        ('.b.', pytest.raises(dce.ValidationError)),
        ('ab.{cd', pytest.raises(dce.ValidationError)),
        ('ab.cd}', pytest.raises(dce.ValidationError)),
        ('ab.c,d', pytest.raises(dce.ValidationError)),
        ('ab.,cb.dd', pytest.raises(dce.ValidationError)),
        ('ab.cb,.dd', pytest.raises(dce.ValidationError)),
        ('a/b.bb.cc', pytest.raises(dce.ValidationError)),
        ('aa.bb', does_not_raise()),
        ('aa.bb.{cc,dd}.aa', does_not_raise()),
    ],
)
def test_get_envs_from_string_checks(value, result):
    with result:
        bp_utils.get_envs_from_string(value)


@pytest.mark.parametrize(
    "value,result",
    [
        ('aa', ['aa']),
        ('aa.aa', ['aa', 'aa.aa']),
        ('{aa,bb}', ['aa', 'bb']),
        ('aa.{aa,bb}', ['aa', 'aa.aa', 'aa.bb']),
        ('aa.{aa,bb}.{cc,dd}', ['aa', 'aa.aa', 'aa.aa.cc', 'aa.aa.dd', 'aa.bb', 'aa.bb.cc', 'aa.bb.dd']),
        ('aa.{aa,bb}.cc', ['aa', 'aa.aa', 'aa.aa.cc', 'aa.bb', 'aa.bb.cc']),
    ],
)
def test_get_envs_from_string_values(value, result):
    assert bp_utils.get_envs_from_string(value) == result
