import pytest

from tests_user_statistics import utils_orders


HANDLE_PATH = '/v1/orders'

DB_NAME = 'user-statistics'


async def test_no_counters(taxi_user_statistics):
    request = utils_orders.make_request(phone_id='000000000000000000000000')

    response = await taxi_user_statistics.post(HANDLE_PATH, json=request)
    assert response.status_code == 200

    response_json = response.json()
    assert response_json == {
        'data': [
            {
                'identity': {
                    'type': 'phone_id',
                    'value': '000000000000000000000000',
                },
                'counters': [],
            },
        ],
    }


@pytest.mark.pgsql(DB_NAME, files=['fill_data.sql'])
async def test_raw_counters(taxi_user_statistics, load_json):
    request = utils_orders.make_request(
        phone_id='000000000000000000000001',
        yandex_uid='0000000001',
        card_persistent_id='00000000000000000000000000000001',
        device_id='00000000-0000-0000-0000-000000000001',
    )

    response = await taxi_user_statistics.post(HANDLE_PATH, json=request)
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    expected_json = utils_orders.get_sorted_response(
        load_json('raw_counters.json'),
    )
    assert response_json == expected_json


@pytest.mark.parametrize(
    'group_by, expected_response',
    [
        (['payment_type'], 'groupby_payment_type.json'),
        ([], 'groupby_none.json'),
    ],
)
@pytest.mark.pgsql(DB_NAME, files=['fill_data.sql'])
async def test_groupby_counters(
        taxi_user_statistics, load_json, group_by, expected_response,
):
    request = utils_orders.make_request(
        phone_id='000000000000000000000002',
        card_persistent_id='00000000000000000000000000000002',
        group_by=group_by,
    )

    response = await taxi_user_statistics.post(HANDLE_PATH, json=request)
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    expected_json = utils_orders.get_sorted_response(
        load_json(expected_response),
    )
    assert response_json == expected_json


@pytest.mark.pgsql(DB_NAME, files=['fill_data.sql'])
async def test_filter_counters(taxi_user_statistics, load_json):
    request = utils_orders.make_request(
        phone_id='000000000000000000000002',
        card_persistent_id='00000000000000000000000000000002',
        filters=utils_orders.make_filters(
            payment_type=['cash', 'card'], tariff_class=['comfort'],
        ),
    )

    response = await taxi_user_statistics.post(HANDLE_PATH, json=request)
    assert response.status_code == 200

    response_json = utils_orders.get_sorted_response(response.json())
    expected_json = utils_orders.get_sorted_response(
        load_json('filter_payment_type_tariff_class.json'),
    )
    assert response_json == expected_json
