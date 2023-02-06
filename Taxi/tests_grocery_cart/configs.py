import pytest

GROCERY_CURRENCY = pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'RUB': {'__default__': 0.01, 'grocery': 0.01},
        '__default__': {'__default__': 0.01, 'grocery': 0.01},
    },
    CURRENCY_FORMATTING_RULES={
        'RUB': {
            '__default__': 2,
            'grocery': 2,  # проверяем что возьмется именно grocery
        },
        '__default__': {
            '__default__': 2,
            'grocery': 2,  # проверяем что возьмется именно grocery
        },
    },
    CURRENCY_KEEP_TRAILING_ZEROS={
        'RUB': {
            '__default__': True,
            'grocery': True,  # проверяем что возьмется именно grocery
        },
        '__default__': {
            '__default__': True,
            'grocery': True,  # проверяем что возьмется именно grocery
        },
    },
)
