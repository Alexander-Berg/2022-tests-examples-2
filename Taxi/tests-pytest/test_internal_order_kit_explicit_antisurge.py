# -*- coding: utf-8 -*-
'''
taxi.internal.order_kit.explicit_antisurge tests
'''

import pytest

from taxi.internal import dbh
from taxi.internal.order_kit import explicit_antisurge


@pytest.inline_callbacks
@pytest.mark.config(
    EXPLICIT_ANTISURGE_ENABLED=True,
    EXPLICIT_ANTISURGE_SETTINGS={
        '__default__': {
            'MIN_ABS_GAIN': 20,     # unused here, but required
            'MIN_REL_GAIN': 0.2,    # unused here, but required
            'MIN_SURGE_B': 0.9,     # unused here, but required
            'SKIP_FIELDS': 'rnop',
            'SHOW_FIXED_PRICE': False,
            'HIDE_DEST': True,
            'OFFER_TIMEOUT': 20,
        },
        'spb': {
            'MIN_ABS_GAIN': 20,     # unused here, but required
            'MIN_REL_GAIN': 0.2,    # unused here, but required
            'MIN_SURGE_B': 0.9,     # unused here, but required
            'SKIP_FIELDS': 'rno',
            'SHOW_FIXED_PRICE': False,
            'HIDE_DEST': True,
            'OFFER_TIMEOUT': 20,
        }
    }
)
@pytest.mark.parametrize(
    'order_id,expected_skip_fields',
    [
        ('order_with_explicit_antisurge', 'rnop'),
        ('order_with_explicit_antisurge_spb', 'rno'),
        ('order_with_altpin', ''),
        ('order_with_no_alternative', ''),
        ('order_with_no_calc', ''),
    ]
)
def test_explicit_antisurge(order_id, expected_skip_fields):
    order = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    assert expected_skip_fields == (yield explicit_antisurge.get_skip_fields(
        order, None
    ))
