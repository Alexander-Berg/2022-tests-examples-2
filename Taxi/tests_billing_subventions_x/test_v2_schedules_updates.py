import pytest


@pytest.mark.parametrize(
    'rule_type,start,end,expected',
    (
        (
            'goal',
            '2021-06-30T00:00:00+03:00',
            '2021-07-01T00:00:00+03:00',  # too early
            'empty.json',
        ),
        (
            'goal',
            '2021-07-01T00:00:01+03:00',  # too late
            '2021-07-01T00:00:02+03:00',
            'empty.json',
        ),
        (
            'goal',
            '2021-07-01T00:00:00+03:00',
            '2021-07-01T00:00:01+03:00',
            'goals.json',
        ),
        (
            'single_ride',
            '2021-07-01T00:00:00+03:00',
            '2021-07-01T00:00:01+03:00',
            'single_rides.json',
        ),
        (
            'single_ontop',
            '2021-07-01T00:00:00+03:00',
            '2021-07-01T00:00:01+03:00',
            'single_ontops.json',
        ),
    ),
)
async def test_v2_schedules_updates_returns_expected(
        load_json, with_response, with_query, rule_type, start, end, expected,
):
    query = with_query(rule_type=rule_type, start=start, end=end)
    response = await with_response(query)
    assert response['schedules'] == load_json(expected)


@pytest.mark.parametrize(
    'cursor,limit,expected_refs,expected_cursor',
    (
        (None, 3, ['goal_schedule_ref', 'goal_schedule_ref_2'], None),
        (
            None,
            1,
            ['goal_schedule_ref'],
            {'2021-06-30T21:00:00+0000': 'goal_schedule_ref'},
        ),
        (
            {'2021-06-30T21:00:00+0000': 'goal_schedule_ref'},
            1,
            ['goal_schedule_ref_2'],
            {'2021-06-30T21:00:00+0000': 'goal_schedule_ref_2'},
        ),
        ({'2021-06-30T21:00:00+0000': 'goal_schedule_ref_2'}, 1, [], None),
    ),
)
async def test_v2_schedules_updates_paginated(
        with_response,
        with_query,
        cursor,
        limit,
        expected_refs,
        expected_cursor,
):
    query = with_query(
        rule_type='goal',
        start='2021-07-01T00:00:00+03:00',
        end='2021-07-01T00:00:01+03:00',
        limit=limit,
        cursor=cursor,
    )
    response = await with_response(query)
    assert [s['schedule_ref'] for s in response['schedules']] == expected_refs
    assert response.get('next_cursor') == expected_cursor


@pytest.mark.parametrize(
    'is_personal,expected_refs',
    (
        (None, ['goal_schedule_ref', 'goal_schedule_ref_2']),
        (False, ['goal_schedule_ref']),
        (True, ['goal_schedule_ref_2']),
    ),
)
async def test_v2_schedules_updates_filters_personal_rules(
        with_response, with_query, is_personal, expected_refs,
):
    query = with_query(
        rule_type='goal',
        start='2021-07-01T00:00:00+03:00',
        end='2021-07-01T00:00:01+03:00',
        is_personal=is_personal,
    )
    response = await with_response(query)
    assert [s['schedule_ref'] for s in response['schedules']] == expected_refs


@pytest.fixture(name='with_response')
def _with_response(taxi_billing_subventions_x):
    async def _builder(query):
        url = '/v2/schedules/updates'
        response = await taxi_billing_subventions_x.post(url, query)
        assert response.status_code == 200, response.json()
        return response.json()

    return _builder


@pytest.fixture(name='with_query', scope='module')
def _with_query():
    def _builder(
            *, rule_type, start, end, limit=100, cursor=None, is_personal=None,
    ):
        query = {
            'time_range': {'start': start, 'end': end},
            'rule_type': rule_type,
            'limit': limit,
        }
        if cursor is not None:
            query['cursor'] = cursor
        if is_personal is not None:
            query['is_personal'] = is_personal
        return query

    return _builder


@pytest.fixture(autouse=True)
def _fill_db(create_rules, a_single_ride, a_single_ontop, a_goal):
    create_rules(
        a_goal(
            schedule_ref='goal_schedule_ref',
            tariff_class='econom',
            geonode='br_root/br_moscow_region',
            start='2021-07-02T00:00:00+03:00',
            end='2021-07-09T00:00:00+03:00',
            geoarea='pol-1',
            tag='a_tag',
            branding='sticker',
            points=50,
            currency='RUB',
            window_size=7,
            updated_at='2021-07-01T00:00:00+03:00',
        ),
        a_goal(
            schedule_ref='goal_schedule_ref',
            tariff_class='comfort',
            geonode='br_root/br_moscow',
            start='2021-07-02T00:00:00+03:00',
            end='2021-07-09T00:00:00+03:00',
            geoarea='pol-2',
            tag='a_tag',
            branding='sticker',
            points=50,
            currency='RUB',
            window_size=7,
            updated_at='2021-07-01T00:00:00+03:00',
        ),
        a_goal(
            schedule_ref='goal_schedule_ref_2',
            start='2021-07-02T00:00:00+03:00',
            end='2021-07-05T00:00:00+03:00',
            geonode='br_root/br_minsk',
            currency='BYN',
            window_size=1,
            unique_driver_id='5df5238d-948e-4bcf-adf9-a89680cdfa5b',
            updated_at='2021-07-01T00:00:00+03:00',
        ),
        a_single_ride(
            schedule_ref='single_ride_schedule_ref',
            start='2021-07-02T00:00:00+03:00',
            end='2021-07-03T00:00:00+03:00',
            geoarea='pol-1',
            tag='tag',
            branding='full_branding',
            points=75,
            updated_at='2021-07-01T00:00:00+03:00',
        ),
        a_single_ride(
            schedule_ref='single_ride_schedule_ref_2',
            start='2021-07-02T00:00:00+03:00',
            end='2021-07-03T00:00:00+03:00',
            updated_at='2021-07-01T00:00:00+03:00',
        ),
        a_single_ontop(
            schedule_ref='single_ontop_schedule_ref',
            start='2021-07-02T00:00:00+03:00',
            end='2021-07-03T00:00:00+03:00',
            geoarea='pol-1',
            tag='tag',
            branding='full_branding',
            points=75,
            updated_at='2021-07-01T00:00:00+03:00',
        ),
        a_single_ontop(
            schedule_ref='single_ontop_schedule_ref_2',
            start='2021-07-02T00:00:00+03:00',
            end='2021-07-03T00:00:00+03:00',
            updated_at='2021-07-01T00:00:00+03:00',
        ),
    )
