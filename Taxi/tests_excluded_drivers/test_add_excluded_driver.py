import datetime

import bson
import pytest


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(EXCLUDED_DRIVERS_DELTA=100)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractors_exclusion_time',
    consumers=['excluded_drivers/drivers'],
    clauses=[],
    default_value={'feedback': -10},
    is_config=True,
)
async def test_add_driver(taxi_excluded_drivers, mongodb, load_json):
    request = load_json('request.json')
    response = await taxi_excluded_drivers.post(
        '/excluded-drivers/v1/drivers', request,
    )
    assert response.status_code == 200
    record = mongodb.excluded_drivers.find_one(
        {'i': bson.ObjectId('5888d2cc468c89a15b3e1387')},
    )
    assert record['p_i'] == 'p_5888d2cc468c89a15b3e1387'
    assert record['p_id'] == 'driver_license_pd_id'
    assert record['r'] == 'feedback'
    assert record['o'] == 'order_id'
    assert 't' not in record


@pytest.mark.now('2020-01-01T00:00:00+0000')
@pytest.mark.config(EXCLUDED_DRIVERS_DELTA=100)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractors_exclusion_time',
    consumers=['excluded_drivers/drivers'],
    clauses=[],
    default_value={'feedback': -10, 'test': 10},
    is_config=True,
)
@pytest.mark.parametrize(
    'reason, expected_response_code, expected_record',
    (
        pytest.param(
            'test',
            200,
            {'t': datetime.datetime(2020, 1, 1, 00, 11, 40)},
            id='excluded_not_4ever',
        ),
        pytest.param('zero_test', 200, None, id='zero_time'),
        pytest.param('feedback', 200, {}, id='excluded_4ever'),
    ),
)
async def test_different_exclusion_reasons(
        taxi_excluded_drivers,
        mongodb,
        load_json,
        reason,
        expected_response_code,
        expected_record,
):

    request = load_json('request.json')
    request['reason'] = reason
    response = await taxi_excluded_drivers.post(
        '/excluded-drivers/v1/drivers', request,
    )
    assert response.status_code == expected_response_code
    record = mongodb.excluded_drivers.find_one(
        {'i': bson.ObjectId('5888d2cc468c89a15b3e1387')}, {'t': 1, '_id': 0},
    )
    assert record == expected_record
