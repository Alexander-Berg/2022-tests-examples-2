import pytest

from tests_cashbox_integration import utils

ENDPOINT = '/v1/drivers/receipts/autocreation'

AUTH_HEADERS = {
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '123',
    'X-Remote-Ip': '1.1.1.1',
}


async def test_ok(taxi_cashbox_integration, fleet_parks, pgsql, mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock_dispatcher_access_control(request):
        return {
            'users': [
                {
                    'id': '1',
                    'display_name': 'Disp',
                    'park_id': '1',
                    'is_enabled': True,
                    'is_confirmed': True,
                    'is_superuser': True,
                    'is_usage_consent_accepted': True,
                },
            ],
        }

    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_driver_work_rules(request):
        return {}

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': 'park_123', 'driver_id': 'driver_123'},
        json={'is_enabled': True},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'autocreation': {'driver_id': 'driver_123', 'is_enabled': True},
        'is_changeable': True,
    }

    request = _mock_dispatcher_access_control.next_call()['request'].json
    assert request == {
        'query': {
            'park': {'id': 'park_123'},
            'user': {'passport_uid': ['123']},
        },
        'offset': 0,
    }

    request = _mock_driver_work_rules.next_call()['request'].json
    assert request['park_id'] == 'park_123'
    assert request['change_info'] == {
        'object_id': 'driver_123',
        'object_type': 'Taximeter.Core.Models.Driver',
        'diff': [
            {
                'field': 'Automatic Receipt Creation',
                'old': 'false',
                'new': 'true',
            },
        ],
    }
    assert request['author'] == {
        'dispatch_user_id': '1',
        'display_name': 'Disp',
        'user_ip': '1.1.1.1',
    }

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': 'park_123', 'driver_id': 'driver_456'},
        json={'is_enabled': True},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'autocreation': {'driver_id': 'driver_456', 'is_enabled': True},
        'is_changeable': True,
    }

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': 'park_123', 'driver_id': 'driver_123'},
        json={'is_enabled': False},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'autocreation': {'driver_id': 'driver_123', 'is_enabled': False},
        'is_changeable': True,
    }

    cursor = pgsql['cashbox_integration'].cursor()
    cursor.execute(
        'SELECT * from cashbox_integration.drivers ORDER BY driver_id',
    )
    rows = utils.pg_response_to_dict(cursor)
    cursor.close()

    assert len(rows) == 2
    assert rows[0] == {
        'park_id': 'park_123',
        'driver_id': 'driver_123',
        'force_receipt': False,
    }
    assert rows[1] == {
        'park_id': 'park_123',
        'driver_id': 'driver_456',
        'force_receipt': True,
    }


@pytest.mark.experiments3(filename='exp3_config.json')
async def test_autocreation_by_park_id(
        taxi_cashbox_integration, fleet_parks, pgsql, mockserver,
):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': 'park_123', 'driver_id': 'driver_123'},
        json={'is_enabled': True},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'autocreation': {'driver_id': 'driver_123', 'is_enabled': True},
        'is_changeable': False,
    }

    cursor = pgsql['cashbox_integration'].cursor()
    cursor.execute(
        'SELECT * from cashbox_integration.drivers ORDER BY driver_id',
    )
    rows = utils.pg_response_to_dict(cursor)
    cursor.close()
    assert not rows
