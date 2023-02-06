import pytest

import tests_candidates.helpers


@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
    CANDIDATES_DRIVER_FUNDED_DISCOUNT_TAGS=['discount1', 'discount2'],
)
@pytest.mark.tags_v2_index(
    tags_list=[
        # dbid0_uuid0
        ('dbid_uuid', 'dbid0_uuid0', 'discount1'),
        # dbid0_uuid1
        ('car_number', 'Х495НК77', 'discount_vip'),
    ],
)
async def test_discount(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        taxi_config,
        dispatch_settings,
):

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625129, 55.757644]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625129, 55.757644]},
        ],
    )

    body = {
        'driver_ids': [
            {'uuid': 'uuid0', 'dbid': 'dbid0'},
            {'uuid': 'uuid1', 'dbid': 'dbid0'},
        ],
        'allowed_classes': ['econom', 'vip'],
        'order_id': 'test-order-1',
        'zone_id': 'moscow',
        'order': {
            'pricing_data': {
                'user': {'meta': {'driver_funded_discount_value': 7.6}},
            },
        },
    }
    response = await taxi_candidates.post('satisfy', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'drivers': [
                {'dbid': 'dbid0', 'uuid': 'uuid0', 'is_satisfied': True},
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid1',
                    'is_satisfied': False,
                    'reasons': {'product/driver_funded_discount_tags': []},
                },
            ],
        },
    )
    assert actual == expected
