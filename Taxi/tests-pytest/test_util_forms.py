from django import forms

import pytest

from taxi.util import decimal
from taxi.util import forms as forms_util


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('value, expected_python_value', [
    (None, None),
    ('', None),
    ('1.1', decimal.Decimal('1.1')),
])
@pytest.mark.asyncenv('blocking')
def test_cdecimal_field_to_python(value, expected_python_value):
    field = forms_util.CDecimalField()
    actual_python_value = field.to_python(value)
    assert actual_python_value == expected_python_value


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('value', [
    'tada',
])
@pytest.mark.asyncenv('blocking')
def test_cdecimal_field_to_python_failure(value):
    field = forms_util.CDecimalField()
    with pytest.raises(forms.ValidationError):
        field.to_python(value)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('init_kwargs,value', [
    (
        {},
        '3.4'
    ),
    (
        {'required': False},
        ''
    ),
    (
        {'max_value': decimal.Decimal('3.4')},
        '3.4'
    ),
    (
        {'min_value': decimal.Decimal('0.0')},
        '0.0'
    ),
    (
        {'decimal_places': 4},
        '0.1234'
    ),
])
@pytest.mark.asyncenv('blocking')
def test_cdecimal_field_validate(init_kwargs, value):
    field = forms_util.CDecimalField(**init_kwargs)
    python_value = field.to_python(value)
    assert field.validate(python_value) == python_value
    field.run_validators(python_value)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('init_kwargs,value', [
    (
        {'required': True},
        ''
    ),
    (
        {},
        'nan'
    ),
    (
        {},
        'inf'
    ),
    (
        {},
        '-inf'
    ),
    (
        {'max_value': decimal.Decimal('3.4')},
        '3.41'
    ),
    (
        {
            'min_value': decimal.Decimal('0.0'),
        },
        '-0.1'
    ),
    (
        {'decimal_places': 4},
        '0.12345'
    ),
])
@pytest.mark.asyncenv('blocking')
def test_cdecimal_field_validate_failure(init_kwargs, value):
    field = forms_util.CDecimalField(**init_kwargs)
    python_value = field.to_python(value)
    with pytest.raises(forms.ValidationError):
        field.validate(python_value)
        field.run_validators(python_value)
