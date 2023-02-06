import json

import pytest

from tests_dispatch_airport_view import common
import tests_dispatch_airport_view.utils as utils


DRIVER_META = {
    'dbid_uuid0': {'geobus_ts': '1000', 'updated_ts': 1005},
    'dbid_uuid1': {
        'geobus_ts': '1001',
        'is_hidden': 'false',
        'updated_ts': 1006,
    },
    'dbid_uuid2': {
        'geobus_ts': '1002',
        'is_hidden': 'true',
        'updated_ts': 1007,
    },
}


@pytest.mark.redis_store(
    # driver hashes
    [
        'hmset',
        utils.driver_info_key('dbid_uuid0'),
        {
            **DRIVER_META['dbid_uuid0'],
            'pins': json.dumps([utils.ekb_pin_point(True, 3600)]),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid1'),
        {
            **DRIVER_META['dbid_uuid1'],
            'pins': json.dumps(
                [
                    utils.ekb_pin_point(False, 1000),
                    utils.kamenskuralsky_pin_point(True),
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid2'),
        {**DRIVER_META['dbid_uuid2'], 'pins': json.dumps([])},
    ],
)
async def test_v1_preview(taxi_dispatch_airport_view):
    url = '/v1/preview'
    headers = common.DEFAULT_DISPATCH_AIRPORT_VIEW_HEADER

    for dbid_uuid in ('not_found_driver_id', 'dbid_uuid2'):
        response = await taxi_dispatch_airport_view.get(
            url, headers=headers, params={'dbid_uuid': dbid_uuid},
        )
        assert response.status_code == 404
        r_json = response.json()
        assert r_json == {
            'code': 'no_driver_pins',
            'message': f'Driver {dbid_uuid} without pins',
        }

    response = await taxi_dispatch_airport_view.get(
        url, headers=headers, params={'dbid_uuid': 'dbid_uuid0'},
    )
    r_json = response.json()
    assert r_json == {
        'previews': [
            {
                'airport_id': 'ekb',
                'pin_point': utils.AIRPORT_EKB_POSITION,
                'is_allowed': True,
            },
        ],
        'etag': 1005,
    }

    response = await taxi_dispatch_airport_view.get(
        url, headers=headers, params={'dbid_uuid': 'dbid_uuid1'},
    )
    r_json = response.json()
    assert r_json == {
        'previews': [
            {
                'airport_id': 'ekb',
                'pin_point': utils.AIRPORT_EKB_POSITION,
                'is_allowed': False,
            },
            {
                'airport_id': 'kamenskuralsky',
                'pin_point': utils.AIRPORT_KAMENSKURALSK,
                'is_allowed': True,
            },
        ],
        'etag': 1006,
    }
