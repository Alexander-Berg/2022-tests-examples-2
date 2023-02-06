import datetime

import pytest

from tests_ride_discounts import common

CREATING_DATA = {
    'data': {
        'discount': {
            'description': 'Тестирование сервиса номер 2',
            'discount_meta': {
                'is_price_strikethrough': True,
                'update_meta_info': {
                    'date': '2021-06-25T11:17:34',
                    'tickets': ['EFFICIENCYDEV-13253'],
                    'user_login': 'iantropov',
                },
            },
            'name': 'team_test_2',
            'values_with_schedules': [
                {
                    'money_value': {
                        'discount_value': {
                            'value': {
                                'hyperbola_lower': {'a': 0, 'c': 1, 'p': 5},
                                'hyperbola_upper': {'a': 0, 'c': 1, 'p': 5},
                                'threshold': 1000,
                            },
                            'value_type': 'hyperbolas',
                        },
                        'max_absolute_value': 5,
                    },
                    'schedule': {
                        'intervals': [
                            {'day': [1, 2, 3, 4, 5, 6, 7], 'exclude': False},
                            {
                                'daytime': [{'to': '23:59:59'}],
                                'exclude': False,
                            },
                        ],
                        'timezone': 'UTC',
                    },
                },
            ],
        },
        'hierarchy_name': 'payment_method_money_discounts',
    },
    'affected_discount_ids': [],
    'series_id': '78563307-7501-42c2-9468-e63f727ddaa4',
    'rules': [
        {'condition_name': 'tariff', 'values': ['econom', 'vip']},
        {
            'condition_name': 'zone',
            'values': [
                {
                    'is_prioritized': False,
                    'name': 'br_moscow',
                    'type': 'geonode',
                },
            ],
        },
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'end': '2021-07-08T15:00:00+00:00',
                    'is_end_utc': False,
                    'is_start_utc': False,
                    'start': '2021-06-25T18:00:00+00:00',
                },
            ],
        },
        {
            'condition_name': 'tag',
            'values': 'Other',
            'exclusions': ['excluded_tag'],
        },
    ],
}

EXPECTED_DATA = {
    'hierarchy_name': 'payment_method_money_discounts',
    'meta_info': {
        'create_draft_id': 'ride_discounts_draft_id',
        'create_tickets': ['ticket-1'],
        'replaced': False,
    },
    'discount': {
        'description': 'Тестирование сервиса номер 2',
        'discount_meta': {
            'is_price_strikethrough': True,
            'update_meta_info': {
                'date': '2021-06-25T11:17:34',
                'tickets': ['EFFICIENCYDEV-13253'],
                'user_login': 'iantropov',
            },
        },
        'name': 'team_test_2',
        'values_with_schedules': [
            {
                'money_value': {
                    'discount_value': {
                        'value': {
                            'hyperbola_lower': {'a': 0.0, 'c': 1.0, 'p': 5.0},
                            'hyperbola_upper': {'a': 0.0, 'c': 1.0, 'p': 5.0},
                            'threshold': 1000.0,
                        },
                        'value_type': 'hyperbolas',
                    },
                    'max_absolute_value': 5.0,
                },
                'schedule': {
                    'intervals': [
                        {'day': [1, 2, 3, 4, 5, 6, 7], 'exclude': False},
                        {'daytime': [{'to': '23:59:59'}], 'exclude': False},
                    ],
                    'timezone': 'UTC',
                },
            },
        ],
    },
    'discount_id': common.START_DATA_ID,
    'rules': [
        {'condition_name': 'intermediate_point_is_set', 'values': 'Other'},
        {
            'condition_name': 'zone',
            'values': [
                {
                    'is_prioritized': False,
                    'name': 'br_moscow',
                    'type': 'geonode',
                },
            ],
        },
        {'condition_name': 'order_type', 'values': 'Other'},
        {
            'condition_name': 'tag',
            'values': 'Other',
            'exclusions': ['excluded_tag'],
        },
        {'condition_name': 'payment_method', 'values': 'Other'},
        {'condition_name': 'bins', 'values': ['Other']},
        {'condition_name': 'application_brand', 'values': 'Other'},
        {'condition_name': 'application_platform', 'values': 'Other'},
        {'condition_name': 'application_type', 'values': 'Other'},
        {'condition_name': 'has_yaplus', 'values': 'Other'},
        {'condition_name': 'tariff', 'values': ['econom', 'vip']},
        {'condition_name': 'point_b_is_set', 'values': 'Other'},
        {'condition_name': 'trips_restriction', 'values': 'Other'},
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'end': '2021-07-08T15:00:00+00:00',
                    'is_end_utc': False,
                    'is_start_utc': False,
                    'start': '2021-06-25T18:00:00+00:00',
                },
            ],
        },
    ],
}


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'need_add_discount, expected_status, expected_data',
    (
        (True, 200, EXPECTED_DATA),
        (
            False,
            404,
            {'code': 'NOT_FOUND', 'message': 'Not found discount with id'},
        ),
    ),
)
async def test_admin_load_discount(
        client,
        reset_data_id,
        mocked_time,
        need_add_discount,
        expected_status,
        expected_data,
):
    if need_add_discount:
        response = await client.post(
            'v1/admin/match-discounts/add-rules',
            headers=common.get_draft_headers(),
            json=CREATING_DATA,
        )
        assert response.status == 200, response.json()

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-06-26T18:00:00+00:00'),
    )
    response = await client.post(
        '/v1/admin/match-discounts/load-discount',
        headers=common.get_headers(),
        json={'discount_id': common.START_DATA_ID},
    )
    assert response.status == expected_status
    response_data = response.json()
    response_data.pop('series_id', None)
    assert response_data == expected_data
