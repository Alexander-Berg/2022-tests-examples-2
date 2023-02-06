import pytest

EATS_PLUS_ENABLED_CURRENCIES = pytest.mark.config(
    EATS_PLUS_ENABLED_CURRENCIES=['RUB', 'BYN', 'KZT'],
)

EATS_PLUS_CURRENCY_FOR_PLUS = pytest.mark.config(
    EATS_PLUS_CURRENCY_FOR_PLUS={
        '__default__': 0,
        'RUB': 1,
        'BYN': 1,
        'KZT': 1,
    },
)
