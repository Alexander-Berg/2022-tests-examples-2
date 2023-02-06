import uuid

import pydantic
import pytest

from taxi.robowarehouse.lib.misc import models


@pytest.mark.parametrize('value', ('', 'qwerty', '1234'))
def test_uuid_str_not_valid(value):
    class A(pydantic.BaseModel):
        s: models.UUIDStr

    with pytest.raises(pydantic.ValidationError) as e:
        A(s=value)

    assert 'badly formed hexadecimal UUID string' in str(e.value)


@pytest.mark.parametrize('value', (
    224611949310867850787498811024988546668,
    uuid.UUID('cd32d87bd28a4fa9a4ccb87b5c791ede'),
))
def test_uuid_str_not_string(value):
    class A(pydantic.BaseModel):
        s: models.UUIDStr

    with pytest.raises(pydantic.ValidationError) as e:
        A(s=value)

    assert 'string required' in str(e.value)


def test_uuid_str_invalid_format():
    class A(pydantic.BaseModel):
        s: models.UUIDStr

    with pytest.raises(pydantic.ValidationError) as e:
        A(s='cd32d87bd28a4fa9a4ccb87b5c791ede')

    assert 'invalid uuid format' in str(e.value)


def test_uuid_str_valid():
    class A(pydantic.BaseModel):
        s: models.UUIDStr

    value = '570d8a53-9cf6-4680-922e-9d864e509cd7'

    result = A(s=value)

    assert result.s == value


def test_base_schema_model_camel_case_default():
    class A(models.BaseSchemaModel):
        a_b: str = 'value_1'

    result = A().dict()

    assert result == {'a_b': 'value_1'}


def test_base_schema_model_camel_case_true():
    class A(models.BaseSchemaModel):
        a_b: str = 'value_1'

    result = A().dict(by_alias=True)

    assert result == {'aB': 'value_1'}


def test_base_schema_model_camel_case_false():
    class A(models.BaseSchemaModel):
        a_b: str = 'value_1'

    result = A().dict(by_alias=False)

    assert result == {'a_b': 'value_1'}
