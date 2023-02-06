import pytest

Q_SELECT_EVENTS = (
    'SELECT amount, driver_id, event_ref, aggregation_key FROM bte.events;'
)
Q_SELECT_PAYLOADS = 'SELECT aggregation_key, payload FROM bte.payloads;'


@pytest.mark.parametrize(
    'testcase_json',
    [
        pytest.param('noactivities.json'),
        pytest.param('one_activity.json'),
        pytest.param('more_than_minute.json'),
        pytest.param('multiple_activities.json'),
        pytest.param(
            'the_same_event.json',
            marks=pytest.mark.pgsql(
                'billing_time_events@0', files=['the_same_event.sql'],
            ),
        ),
    ],
)
@pytest.mark.now('2020-06-02T19:00:00')
async def test_push(
        testcase_json, *, pgsql, taxi_billing_time_events, load_json,
):
    testcase = load_json(testcase_json)
    request = testcase['request']
    expected_events = testcase['expected_events']
    expected_payloads = testcase['expected_payloads']

    response = await taxi_billing_time_events.post(
        'v1/push',
        json=request,
        headers={'X-Idempotency-Token': '1234567890123456'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    actual_events, actual_payloads = [], []
    for shard in 'billing_time_events@0', 'billing_time_events@1':
        cursor = pgsql[shard].cursor()
        cursor.execute(Q_SELECT_EVENTS)
        actual_events.extend(list(cursor))
        cursor.execute(Q_SELECT_PAYLOADS)
        actual_payloads.extend(list(cursor))
    assert tuples_to_lists(actual_payloads) == expected_payloads
    assert tuples_to_lists(actual_events) == expected_events


def tuples_to_lists(tuples):
    return [list(tpl) for tpl in tuples]


@pytest.mark.parametrize(
    'testcase_json',
    [
        'too_old_activity.json',
        'too_far_in_future_activity.json',
        'start_greater_end_activity.json',
    ],
)
@pytest.mark.config(
    BILLING_TIME_EVENTS_EVENTS_MAINTENANCE_SETTINGS={
        'partitions-in-future-hours': 1,
        'partitions-in-past-hours': 1,
    },
)
@pytest.mark.now('2020-07-01T00:00:00+03:00')
async def test_bad_request_validation(
        testcase_json, *, pgsql, taxi_billing_time_events, load_json,
):
    testcase = load_json(testcase_json)
    response = await taxi_billing_time_events.post(
        'v1/push',
        json=testcase['request'],
        headers={'X-Idempotency-Token': '1234567890123456'},
    )
    assert response.status_code == 400
    resp_body = response.json()
    assert resp_body['code'] == 'Bad request'
    assert resp_body['message'] == testcase['error_reason']
