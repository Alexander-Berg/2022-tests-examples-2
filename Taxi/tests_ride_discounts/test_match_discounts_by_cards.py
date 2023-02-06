import datetime

import pytest

from tests_ride_discounts import common

BIN_SET_NAME = 'test_bin_set_name'
OTHER_BIN_SET_NAME = 'other_bin_set_name'
BIN = '222100'
TAG = 'test_tag'
PARAMETRIZE = pytest.mark.parametrize(
    'rules, expected_response',
    [
        pytest.param(
            [
                {'condition_name': 'tag', 'values': [TAG]},
                {'condition_name': 'bins', 'values': [BIN_SET_NAME]},
                {'condition_name': 'tariff', 'values': ['econom']},
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
            ],
            {
                'discounts': [
                    {
                        'card_id': 'test_card_id',
                        'discount_name': '1',
                        'tariff': 'econom',
                    },
                ],
            },
            id='ok',
        ),
        pytest.param(
            [
                {'condition_name': 'tag', 'values': ['does_not_match']},
                {'condition_name': 'bins', 'values': [BIN_SET_NAME]},
                {'condition_name': 'tariff', 'values': ['econom']},
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
            ],
            {'discounts': []},
            id='tag_does_not_match',
        ),
        pytest.param(
            [
                {'condition_name': 'tag', 'values': [TAG]},
                {'condition_name': 'bins', 'values': [OTHER_BIN_SET_NAME]},
                {'condition_name': 'tariff', 'values': ['econom']},
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
            ],
            {'discounts': []},
            id='bins_does_not_match',
        ),
    ],
)


@PARAMETRIZE
@pytest.mark.config(
    RIDE_DISCOUNTS_FETCHING_DATA_SETTINGS={
        'passenger_tags': {'enabled': True},
    },
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_v1_match_discounts_by_cards(
        add_discount,
        mockserver,
        client,
        mocked_time,
        rules,
        expected_response,
):
    bins_data = ((BIN_SET_NAME, BIN), (OTHER_BIN_SET_NAME, '222101'))
    for bin_set_name, bin_ in bins_data:
        response = await client.post(
            '/v1/admin/prioritized-entity',
            headers=common.get_draft_headers(),
            json={
                'name': bin_set_name,
                'data': {
                    'active_period': {
                        'start': '2019-01-01T00:00:01',
                        'end': '2023-01-01T00:00:03',
                    },
                    'prioritized_entity_type': 'bin_set',
                    'bins': [bin_],
                },
            },
        )
        assert response.status == 200, response.json()
    await add_discount('payment_method_money_discounts', rules)

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def tags_handler(request):
        return {'tags': [TAG]}

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-06-26T18:00:00+00:00'),
    )
    await client.invalidate_caches()

    response = await client.post(
        '/v1/match-discounts/by-cards',
        headers=common.get_headers(),
        json={
            'cards': [{'id': 'test_card_id', 'bin': BIN}],
            'tariffs': ['econom'],
            'has_yaplus': False,
            'waypoints': [[1.0, 2.0]],
            'request_time': '2021-06-26T18:00:00+00:00',
            'client_timezone': 'UTC',
            'tariff_zone': 'moscow',
            'user_info': {
                'user_id': 'user_id',
                'phone_id': 'test_phone_id',
                'phone_hash': '138aa82720f81ba2249011d',
                'personal_phone_id': 'test_personal_phone_id',
                'yandex_uid': 'test_yandex_uid',
            },
        },
    )
    assert response.status == 200, response.json()
    assert response.json() == expected_response
    assert tags_handler.times_called == 1
