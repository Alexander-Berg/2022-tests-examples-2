import pytest

from tests_user_statistics import utils_orders


HANDLE_PATH = '/v1/recent-orders'
DB_NAME = 'user-statistics'

OK_TIMERANGE = {
    'from': '2019-12-01T00:00:00+0300',
    'to': '2020-01-01T00:00:00+0300',
}
WRONG_TIMERANGE = {
    'from': '2019-03-01T00:00:00+0300',
    'to': '2019-04-01T00:00:00+0300',
}


@pytest.mark.parametrize('group_by', [None, ([])])
async def test_no_counters(taxi_user_statistics, load_json, group_by):
    request = utils_orders.make_request(
        yandex_uid='0123456789', timerange=OK_TIMERANGE, group_by=group_by,
    )

    response = await taxi_user_statistics.post(HANDLE_PATH, json=request)
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    expected_json = utils_orders.get_sorted_response(
        load_json('empty_counters.json'),
    )
    assert response_json == expected_json


@pytest.mark.pgsql(DB_NAME, files=['fill_data.sql'])
async def test_counters_ok_interval(taxi_user_statistics, load_json):
    request = utils_orders.make_request(
        yandex_uid='0123456789', group_by=[], timerange=OK_TIMERANGE,
    )

    response = await taxi_user_statistics.post(HANDLE_PATH, json=request)
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    expected_json = utils_orders.get_sorted_response(
        load_json('ok_interval_counters.json'),
    )
    assert response_json == expected_json


@pytest.mark.pgsql(DB_NAME, files=['fill_data.sql'])
async def test_counters_wrong_interval(taxi_user_statistics, load_json):
    request = utils_orders.make_request(
        yandex_uid='0123456789', timerange=WRONG_TIMERANGE,
    )

    response = await taxi_user_statistics.post(HANDLE_PATH, json=request)
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    expected_json = utils_orders.get_sorted_response(
        load_json('empty_counters.json'),
    )
    assert response_json == expected_json
