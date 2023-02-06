import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'internal-admin/signal-device-api-admin/v1/filters'


@pytest.mark.parametrize(
    'headers, expected_response',
    [
        (
            web_common.PARTNER_HEADERS_1,
            {
                'filters': [
                    {
                        'filter': {
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
                        'id': 'id-1',
                    },
                    {
                        'filter': {
                            'name': 'test',
                            'conditions': [
                                {
                                    'field': 'declared_serial_numbers.hw_id',
                                    'comparison': 'ne',
                                    'value': 3,
                                },
                            ],
                            'conditions_operator': 'and',
                        },
                        'id': 'id-2',
                    },
                ],
            },
        ),
        (
            web_common.PARTNER_HEADERS_2,
            {
                'filters': [
                    {
                        'filter': {
                            'name': 'diveces',
                            'conditions': [
                                {
                                    'field': 'declared_serial_numbers.hw_id',
                                    'comparison': 'eq',
                                    'value': 2,
                                },
                            ],
                            'conditions_operator': 'and',
                        },
                        'id': 'id-3',
                    },
                ],
            },
        ),
        (web_common.PARTNER_HEADERS_NONEXISTENT, {'filters': []}),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
async def test_ok(
        taxi_signal_device_api_admin, pgsql, headers, expected_response,
):
    response = await taxi_signal_device_api_admin.get(
        ENDPOINT, headers={**headers},
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
