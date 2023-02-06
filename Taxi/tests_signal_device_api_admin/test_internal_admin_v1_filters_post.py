import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'internal-admin/signal-device-api-admin/v1/filters'

FILTER1 = {
    'name': 'test',
    'conditions': [
        {
            'field': 'declared_serial_numbers.hw_id',
            'comparison': 'ge',
            'value': 1,
        },
        {'field': 'devices.id', 'comparison': 'like', 'value': 'nother_park'},
        {'field': 'devices.id', 'comparison': 'ne', 'value': 'another_park'},
    ],
    'conditions_operator': 'and',
}

FILTER2 = {
    'name': 'test2',
    'conditions': [
        {
            'field': 'declared_serial_numbers.hw_id',
            'comparison': 'le',
            'value': 1,
        },
        {'field': 'devices.id', 'comparison': 'like', 'value': 'nother_park'},
        {'field': 'devices.id', 'comparison': 'ne', 'value': 'another_park'},
    ],
    'conditions_operator': 'and',
}

EXPECTED_DB_ROWS = [
    ('test', FILTER1, web_common.PARTNER_HEADERS_1['X-Yandex-UID']),
    ('test2', FILTER2, web_common.PARTNER_HEADERS_1['X-Yandex-UID']),
]


async def test_ok(taxi_signal_device_api_admin, pgsql):
    body = {}
    body['filters'] = [FILTER1, FILTER2]

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers={**web_common.PARTNER_HEADERS_1},
    )
    assert response.status_code == 200, response.text

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        select filter_name, filter_json, x_yandex_uid
        from signal_device_api.internal_filters
        """,
    )
    db_rows = list(db)
    assert utils.unordered_lists_are_equal(db_rows, EXPECTED_DB_ROWS)


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
async def test_duplicate(taxi_signal_device_api_admin, pgsql):
    body = {}
    body['filters'] = [
        {
            'name': 'diveces',
            'conditions': [
                {
                    'field': 'declared_serial_numbers.hw_id',
                    'comparison': 'ge',
                    'value': 1,
                },
            ],
            'conditions_operator': 'and',
        },
    ]

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers={**web_common.PARTNER_HEADERS_1},
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': 'duplicate_error_key',
        'message': 'constraint: internal_filters_name_uid_idx',
        'details': {'filter_name': 'diveces'},
    }
