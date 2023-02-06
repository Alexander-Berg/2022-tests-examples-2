from __future__ import unicode_literals

import pytest

from taxi import config

from taxi.core import db

from taxi_maintenance.stuff import use_extra_thresholds


@pytest.mark.parametrize(
    'use_extra_thresholds_conf,extra_thresholds_by_countries_conf,expected', [
        (
            True, {
                '__default__': -10 ** 8,
                'kaz': -10 ** 7
            },
            {
                'park_1': {
                    'use_extra_thresholds': True,
                    'threshold_dynamic': -100,
                    'deactivated': None
                },
                'park_2': {
                    'use_extra_thresholds': True,
                    'threshold_dynamic': -10 ** 8,
                    'deactivated': None
                },
                'park_3': {
                    'use_extra_thresholds': True,
                    'threshold_dynamic': -10,
                    'deactivated': {
                        'reason': 'smth'
                    }
                },
                'park_4': {
                    'use_extra_thresholds': True,
                    'threshold_dynamic': -10 ** 7 - 10,
                    'deactivated': None
                },
            }
        ), (
            False, {
                '__default__': -10 ** 8,
                'kaz': -10 ** 7
            },
            {
                'park_1': {
                    'use_extra_thresholds': None,
                    'threshold_dynamic': -100,
                    'deactivated': None
                },
                'park_2': {
                    'use_extra_thresholds': None,
                    'threshold_dynamic': None,
                    'deactivated': {
                        'reason': 'low balance'
                    }
                },
                'park_3': {
                    'use_extra_thresholds': None,
                    'threshold_dynamic': -10,
                    'deactivated': {
                        'reason': 'smth'
                    }
                },
                'park_4': {
                    'use_extra_thresholds': None,
                    'threshold_dynamic': -10,
                    'deactivated': None
                },
            }
        )
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_use_extra_thresholds(
        use_extra_thresholds_conf, extra_thresholds_by_countries_conf, expected
):
    config.USE_EXTRA_THRESHOLDS.get = config.USE_EXTRA_THRESHOLDS.get_fresh
    config.EXTRA_THRESHOLDS_BY_COUNTRIES.get = (
        config.EXTRA_THRESHOLDS_BY_COUNTRIES.get_fresh
    )
    config.USE_EXTRA_THRESHOLDS_GLOBAL.get = (
        config.USE_EXTRA_THRESHOLDS_GLOBAL.get_fresh
    )
    yield config.USE_EXTRA_THRESHOLDS.save(use_extra_thresholds_conf)
    yield config.EXTRA_THRESHOLDS_BY_COUNTRIES.save(
        extra_thresholds_by_countries_conf
    )
    yield config.USE_EXTRA_THRESHOLDS_GLOBAL.save(True)

    yield use_extra_thresholds.do_stuff()

    check_fields = ['use_extra_thresholds', 'threshold_dynamic', 'deactivated']
    parks = yield db.parks.find().run()
    print len(parks)
    for park in parks:
        account = park.get('account', {})
        expected_park = expected.get(park['_id'])
        print park['_id'], account, expected_park
        if expected_park:
            for field in check_fields:
                assert account.get(field) == expected_park.get(field)
