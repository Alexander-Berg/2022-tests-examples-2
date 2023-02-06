import pytest

from testsuite.utils import ordered_object


@pytest.mark.parametrize(
    'test_data_json',
    (
        'single_counter.json',
        'two_counters.json',
        'past_the_end_period.json',
        'tz_with_dst.json',
    ),
)
async def test_v2_by_driver_returns_payoffs_for_counters_demanded(
        taxi_billing_subventions_x,
        mockserver,
        load_json,
        test_data_json,
        rules,
):
    test_data = load_json(test_data_json)

    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _v2_balances_select(request):
        return mockserver.make_response(json=test_data['balances_response'])

    response = await taxi_billing_subventions_x.post(
        '/v2/by_driver', test_data['query'],
    )
    assert response.status_code == 200, response.json()
    ordered_object.assert_eq(
        test_data['balances_request'],
        _v2_balances_select.next_call()['request'].json,
        ['accrued_at', 'accounts'],
    )
    ordered_object.assert_eq(
        response.json(),
        test_data['expected'],
        ['subventions', 'period.start'],
    )


async def test_v2_by_driver_returns_empty_payoffs_when_counters_not_found(
        taxi_billing_subventions_x, mockserver, load_json,
):
    data = load_json('absent_counter.json')

    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _v2_balances_select(request):
        return mockserver.make_response(status=400)

    response = await taxi_billing_subventions_x.post(
        '/v2/by_driver', data['query'],
    )
    assert response.status_code == 200, response.json()
    assert response.json() == data['expected']


@pytest.fixture(name='rules')
def _add_rules(a_goal, create_rules):
    counters = {
        'schedule': [
            {'counter': 'A', 'start': '12:00', 'week_day': 'mon'},
            {'counter': '0', 'start': '13:00', 'week_day': 'mon'},
            {'counter': 'B', 'start': '18:00', 'week_day': 'mon'},
            {'counter': '0', 'start': '19:00', 'week_day': 'mon'},
        ],
        'steps': [
            {
                'id': 'A',
                'steps': [
                    {'amount': '100.0000', 'nrides': 10},
                    {'amount': '250.0000', 'nrides': 20},
                ],
            },
            {'id': 'B', 'steps': [{'amount': '200', 'nrides': 20}]},
        ],
    }
    create_rules(
        a_goal(
            id='37eb74e8-810d-11eb-ac59-7f87bf34e5a6',
            tariff_class='business',
            start='2020-12-31T21:00:00+00:00',
            end='2021-02-04T21:00:00+00:00',
            counters=counters,
            unique_driver_id='<udid>',
        ),
        a_goal(
            id='2d8e0d52-1767-402d-a572-3976bbcb29a9',
            start='2020-12-31T21:00:00+00:00',
            end='2021-02-04T21:00:00+00:00',
            counters=counters,
            unique_driver_id='<udid>',
        ),
        draft_id='12345',
    )

    counters = {
        'schedule': [
            {'counter': 'C', 'start': '12:00', 'week_day': 'mon'},
            {'counter': '0', 'start': '13:00', 'week_day': 'mon'},
        ],
        'steps': [
            {
                'id': 'C',
                'steps': [
                    {'amount': '50', 'nrides': 5},
                    {'amount': '150', 'nrides': 15},
                ],
            },
        ],
    }
    create_rules(
        a_goal(
            id='af23a504-8115-11eb-9b53-4f0d94f30c29',
            tariff_class='business',
            start='2020-12-31T21:00:00+00:00',
            end='2021-02-07T21:00:00+00:00',
            counters=counters,
            window_size=1,
        ),
        a_goal(
            id='b862735c-8115-11eb-8862-e7ed9ce85029',
            start='2020-12-31T21:00:00+00:00',
            end='2021-02-07T21:00:00+00:00',
            counters=counters,
            window_size=1,
        ),
        draft_id='22222',
    )
    create_rules(
        a_goal(
            start='2021-10-01T00:00:00+0300',
            end='2021-12-01T00:00:00+0200',
            counters={
                'schedule': [
                    {'counter': 'D', 'start': '00:00', 'week_day': 'mon'},
                ],
                'steps': [
                    {'id': 'D', 'steps': [{'amount': '10', 'nrides': 10}]},
                ],
            },
            window_size=1,
        ),
        draft_id='33333',
    )
