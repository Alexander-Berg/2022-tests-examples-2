import pytest

import tests_candidates.helpers


@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
    CANDIDATES_DISCOUNT_FILTER_RULES={
        'discount_123': {'required_tags': ['discount_econom']},
        'discount_234': {'required_tags': ['discount_vip']},
    },
)
@pytest.mark.tags_v2_index(
    tags_list=[
        # dbid0_uuid0
        ('dbid_uuid', 'dbid0_uuid0', 'discount_econom'),
        # dbid0_uuid1
        ('park_car_id', 'dbid0_car_id1', 'discount_vip'),
    ],
)
async def test_discount(taxi_candidates, driver_positions):

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
            'discount': {
                'by_classes': [
                    {'class': 'econom', 'id': 'discount_123'},
                    {'class': 'vip', 'id': 'discount_234'},
                ],
            },
        },
    }
    response = await taxi_candidates.post('satisfy', json=body)
    assert response.status_code == 200

    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'drivers': [
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'details': {
                        'product/fetch_discount_classes': ['vip by discount'],
                    },
                },
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid1',
                    'details': {
                        'product/fetch_discount_classes': [
                            'econom by discount',
                        ],
                    },
                },
            ],
        },
    )
    assert actual == expected
