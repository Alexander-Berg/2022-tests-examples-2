from taxi.util import decimal


def assert_decimal_equal(actual_value, expected_value):
    """
    :type actual_value: decimal.Decimal | basestring | None
    :type expected_value: decimal.Decimal | basestring | None
    """
    if expected_value in ['', None]:
        assert actual_value == expected_value
    else:
        assert decimal.Decimal(actual_value) == decimal.Decimal(expected_value)
