# pylint: disable=protected-access

import pytest

from replication.plugins.personal import exceptions
from replication.plugins.personal import normalization
from replication.plugins.personal.models import driver_license_normalization
from replication.plugins.personal.models import phone_normalization


@pytest.mark.parametrize(
    'function, source, expected',
    [
        (normalization._as_is, '7495555555', '7495555555'),
        (normalization._as_is, 'trash-7495555555', 'trash-7495555555'),
        (normalization._as_is, 'trash', 'trash'),
        (phone_normalization.norm_phone_add_plus, '7495555555', '+7495555555'),
        (
            phone_normalization.norm_phone_add_plus,
            ' 7495555555',
            '+7495555555',
        ),
        (
            phone_normalization.norm_phone_add_plus,
            ' 7495555555 trash',
            '+7495555555 trash',
        ),
        (phone_normalization._remove_non_digits, '7495555555', '7495555555'),
        (
            phone_normalization._remove_non_digits,
            ' tel:7495555555-and-trash',
            '7495555555',
        ),
        (phone_normalization._remove_non_digits, 'trash', ''),
    ],
)
def test_simple_phone_normalization(function, source, expected):
    assert function(source) == expected


@pytest.mark.parametrize(
    'source, expected, raise_on_incorrect_type, raise_error',
    [
        ('777', '777', True, False),
        (b'777', '777', True, False),
        (777, '777', True, False),
        (None, None, False, False),
        (None, None, True, True),
        ([777], None, True, True),
    ],
)
def test_type_phone_handler(
        source, expected, raise_on_incorrect_type, raise_error,
):
    if raise_error:
        with pytest.raises(exceptions.NormalizationError):
            assert phone_normalization._type_phone_handler(
                source, raise_on_incorrect_type,
            )
    else:
        assert (
            phone_normalization._type_phone_handler(
                source, raise_on_incorrect_type,
            )
            == expected
        )


@pytest.mark.parametrize(
    'source, expected, raise_on_extension_phone, raise_error',
    [
        ('777', '777', True, False),
        ('777ext77', None, True, True),
        ('777доб77', None, True, True),
        ('777доб77', '777', False, False),
    ],
)
def test_extension_phone_handler(
        source, expected, raise_on_extension_phone, raise_error,
):
    if raise_on_extension_phone:
        if raise_error:
            with pytest.raises(exceptions.NormalizationError):
                assert phone_normalization._extension_phone_handler(
                    source, raise_on_extension_phone,
                )
        else:
            assert (
                phone_normalization._extension_phone_handler(
                    source, raise_on_extension_phone,
                )
                == expected
            )
    else:
        assert (
            phone_normalization._extension_phone_handler(
                source, raise_on_extension_phone,
            )
            == expected
        )


@pytest.mark.parametrize(
    'source, expected, assume_russian_format, raise_on_incorrect_pattern, '
    'raise_error',
    [
        ('89991234567', '79991234567', True, True, False),
        ('9991234567', '79991234567', True, True, False),
        ('69991234567', '69991234567', True, True, False),
        ('69991234567', '69991234567', False, True, False),
        ('777', None, True, True, True),
        ('777', None, True, False, False),
    ],
)
def test_russian_format_handler(
        source,
        expected,
        assume_russian_format,
        raise_on_incorrect_pattern,
        raise_error,
):
    if raise_error:
        with pytest.raises(exceptions.NormalizationError):
            assert phone_normalization._russian_format_handler(
                source,
                min_phone_length=11,
                assume_russian_format=assume_russian_format,
                raise_on_incorrect_pattern=raise_on_incorrect_pattern,
            )
    else:
        assert (
            phone_normalization._russian_format_handler(
                source,
                min_phone_length=11,
                assume_russian_format=assume_russian_format,
                raise_on_incorrect_pattern=raise_on_incorrect_pattern,
            )
            == expected
        )


@pytest.mark.parametrize(
    'source, expected',
    [
        ('918-371-06-64', '+9183710664'),
        ('+79991234567', '+79991234567'),
        ('89991234567', '+89991234567'),
        ('9000276644', '+9000276644'),
        ('8 9991234567', '+89991234567'),
        ('+7 999 1234567', '+79991234567'),
        ('+7 999 123 4 567', '+79991234567'),
        ('+7(999)-123-45-67', '+79991234567'),
        ('8-999-123-45-67', '+89991234567'),
        ('+7-9991234567', '+79991234567'),
        ('8-999-123-45-67', '+89991234567'),
        ('79991234567', '+79991234567'),
        ('+3721234567', '+3721234567'),
        ('+8611234567890', '+8611234567890'),
        ('+998123456789', '+998123456789'),
        (998123456789, '+998123456789'),
        ('+ +99812 3456   789', '+998123456789'),
        ('+79271961916                       ', '+79271961916'),
        ('79991234567 доб. 789', '+79991234567'),
        ('79991234567ext789', '+79991234567'),
        ('ip 11:11:11:11', None),
        ('', None),
    ],
)
def test_normalize_phone_number(source, expected):
    assert phone_normalization.normalize_phone_number(source) == expected


@pytest.mark.parametrize(
    'source',
    [
        '+123456789123456789123456789',
        'e1e7ad08-f7d7',
        'e1e7ad08-f7d7-4082-b049-37954e3a3a1d',
        '+123456789 доб 5',
        '+123456789\f5',
        '+7927196191666666666666666666666666',
    ],
)
def test_normalize_phone_number_invalid(source):
    with pytest.raises(exceptions.NormalizationError):
        assert phone_normalization.normalize_phone_number(
            source,
            raise_on_incorrect_type=True,
            raise_on_extension_phone=True,
            raise_on_invalid_phone_chars=True,
            raise_on_max_phone=True,
            assume_russian_format=True,
            raise_on_incorrect_pattern=True,
        )


@pytest.mark.parametrize(
    'source, expected',
    [
        ('license', 'LICENSE'),
        ('ХУТОР386', 'XYTOP386'),
        ('!!! li сe nse ???', 'LICENSE'),
        ('', ''),
        (None, None),
    ],
)
def test_normalize_driver_license(source, expected):
    assert (
        driver_license_normalization.normalize_driver_license(
            source, do_normalize=True,
        )
        == expected
    )


@pytest.mark.parametrize('source', ['???', '???,,,license'])
def test_normalize_driver_license_raises(source):
    with pytest.raises(exceptions.NormalizationError):
        assert driver_license_normalization.normalize_driver_license(
            source, raise_on_non_alphanumeric=True,
        )
