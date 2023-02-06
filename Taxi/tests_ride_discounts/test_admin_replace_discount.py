import dateutil
import discounts_match  # pylint: disable=E0401
import pytest

from tests_ride_discounts import common

ACTIVE_PERIOD_IN_2020_YEAR_FROM_JANUARY = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T12:00:01+00:00',
            'is_start_utc': True,
            'end': '2021-01-01T00:00:00+00:00',
            'is_end_utc': True,
        },
    ],
}
ACTIVE_PERIOD_IN_2020_YEAR_FROM_JULY = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-07T12:00:01+00:00',
            'is_start_utc': True,
            'end': '2021-01-01T00:00:00+00:00',
            'is_end_utc': True,
        },
    ],
}
BR_MOSCOW_CONDITION = {
    'condition_name': 'zone',
    'values': [
        {'name': 'br_moscow', 'type': 'geonode', 'is_prioritized': False},
    ],
}

TIME_IN_THE_PAST_ERROR = (
    'Time in the past for {}. The start time of the discount '
    'must be no earlier than the start time of the draft + delta. '
    'Delta: {} seconds.\nStart time of the draft + delta: {}. '
    'Discount start time: {}'
)


@pytest.mark.parametrize(
    'hierarchy_name, discount_id_to_close, existing_discount_rules, '
    'request_time, request_rules, expected_status, expected_data',
    (
        pytest.param(
            'full_money_discounts',
            common.START_DATA_ID,
            [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JANUARY, BR_MOSCOW_CONDITION],
            '2020-01-02T12:00:01+00:00',
            [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JULY, BR_MOSCOW_CONDITION],
            200,
            None,
            id='ok_full_discounts',
        ),
        pytest.param(
            'experimental_money_discounts',
            common.START_DATA_ID,
            [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JANUARY, BR_MOSCOW_CONDITION],
            '2020-01-02T12:00:01+00:00',
            [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JULY, BR_MOSCOW_CONDITION],
            200,
            None,
            id='ok_experimental_discounts',
        ),
        pytest.param(
            'full_money_discounts',
            '1',
            [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JANUARY, BR_MOSCOW_CONDITION],
            '2020-01-02T12:00:01+00:00',
            [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JULY, BR_MOSCOW_CONDITION],
            404,
            {
                'code': 'NOT_FOUND',
                'message': 'Not found discount with id \'1\'',
            },
            id='not_found_discount_id',
        ),
        pytest.param(
            'full_money_discounts',
            common.START_DATA_ID,
            [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JANUARY, BR_MOSCOW_CONDITION],
            '2022-01-02T12:00:01+00:00',
            [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JULY, BR_MOSCOW_CONDITION],
            400,
            {
                'code': 'Validation error',
                'message': (
                    TIME_IN_THE_PAST_ERROR.format(
                        'Any/Other',
                        '43200',
                        '2022-01-03T00:00:01+0000',
                        '2020-01-07T12:00:01+0000',
                    )
                ),
            },
            id='start_in_past',
        ),
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.param('v1/admin/match-discounts/replace-discount', id='apply'),
        pytest.param(
            'v1/admin/match-discounts/replace-discount/check', id='check',
        ),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.usefixtures('reset_data_id')
async def test_replace_discount_v2(
        client,
        add_discount,
        mocked_time,
        hierarchy_name,
        discount_id_to_close,
        existing_discount_rules,
        request_time,
        request_rules,
        expected_status,
        expected_data,
        url,
):
    await add_discount(hierarchy_name, existing_discount_rules)
    headers = common.get_draft_headers()
    mocked_time.set(dateutil.parser.parse(request_time))
    request: dict = {
        'hierarchy_name': hierarchy_name,
        'affected_discount_ids': [discount_id_to_close],
        'close_discount_data': {'discount_id': discount_id_to_close},
        'add_discount_data': {
            'rules': request_rules,
            'data': {
                'hierarchy_name': hierarchy_name,
                'discount': common.make_discount(
                    hierarchy_name=hierarchy_name,
                ),
            },
            'update_existing_discounts': False,
        },
    }
    response = await client.post(url, request, headers=headers)
    assert response.status_code == expected_status, response.json()
    if expected_status == 200:
        if 'check' not in url:
            old_discount = await common.load_discount(
                client, discount_id_to_close,
            )
            assert old_discount
            assert 'end_time_draft_id' in old_discount['meta_info']
            assert old_discount['meta_info']['replaced']
    else:
        assert response.json() == expected_data


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.usefixtures('reset_data_id')
async def test_replace_discount_affected_discount_ids_does_not_match(
        client, add_discount,
):
    rules = [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JANUARY, BR_MOSCOW_CONDITION]
    await add_discount('full_money_discounts', rules)
    headers = common.get_draft_headers()
    request: dict = {
        'hierarchy_name': 'full_money_discounts',
        'affected_discount_ids': ['1'],
        'close_discount_data': {'discount_id': common.START_DATA_ID},
        'add_discount_data': {
            'rules': rules,
            'data': {
                'hierarchy_name': 'full_money_discounts',
                'discount': common.make_discount(
                    hierarchy_name='full_money_discounts',
                ),
            },
            'update_existing_discounts': True,
        },
    }
    response = await client.post(
        'v1/admin/match-discounts/replace-discount', request, headers=headers,
    )
    assert response.status_code == 400, response.json()
    assert response.json() == {
        'code': 'Validation error',
        'message': 'Affected data ids (size 1) do not match expected ones',
    }


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.usefixtures('reset_data_id')
async def test_replace_discount_twice(client, add_discount):
    await add_discount(
        'full_money_discounts',
        [ACTIVE_PERIOD_IN_2020_YEAR_FROM_JANUARY, BR_MOSCOW_CONDITION],
    )
    response = None
    for tag in ['first_tag', 'second_tag']:
        request: dict = {
            'hierarchy_name': 'full_money_discounts',
            'affected_discount_ids': [common.START_DATA_ID],
            'close_discount_data': {'discount_id': common.START_DATA_ID},
            'add_discount_data': {
                'rules': [
                    ACTIVE_PERIOD_IN_2020_YEAR_FROM_JULY,
                    BR_MOSCOW_CONDITION,
                    {'condition_name': 'tag', 'values': [tag]},
                ],
                'data': {
                    'hierarchy_name': 'full_money_discounts',
                    'discount': common.make_discount(
                        hierarchy_name='full_money_discounts',
                    ),
                },
                'update_existing_discounts': False,
            },
        }
        response = await client.post(
            'v1/admin/match-discounts/replace-discount',
            request,
            headers=common.get_draft_headers(f'draft_{tag}'),
        )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'Validation error',
        'message': 'Intersecting rules with same series_id found. ids: [124]',
    }
