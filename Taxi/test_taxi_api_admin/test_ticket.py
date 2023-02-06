# pylint: disable=protected-access
# pylint: disable=unused-variable
import json

import pytest

from taxi.util import audit


SERVICE_WITH_REQUIRED_TICKET_SCHEMA_NAME = 'service_with_ticket'
URL = SERVICE_WITH_REQUIRED_TICKET_SCHEMA_NAME + '/v1/tariffs/145557cdf01a3/'


@pytest.mark.parametrize(
    'data,headers,valid_ticket_key,expected',
    [
        ({}, {}, None, 400),
        ('some_data', {}, None, 400),
        pytest.param(
            {},
            {'X-YaTaxi-Ticket': 'TAXITEST-420'},
            None,
            400,
            id='force_invalid_ticket_key',
        ),
        (
            {'some_data': '228'},
            {'X-YaTaxi-Ticket': 'TAXITEST-228'},
            'TAXITEST-228',
            200,
        ),
        pytest.param(
            {},
            {'Some-Test-Header': 'test'},
            None,
            400,
            id='headers_without_ticket_invalid',
        ),
        ({}, {'X-YaTaxi-Ticket': ''}, None, 400),
        ({}, {'X-YaTaxi-Ticket': 'https://st.test.yandex-team.ru'}, None, 400),
        (
            {},
            {'X-YaTaxi-Ticket': 'https://st.test.yandex-team.ru/'},
            None,
            400,
        ),
        ({}, {'X-YaTaxi-Ticket': 'TAXIPLATFORM-123'}, 'TAXIPLATFORM-123', 200),
        ({}, {'X-YaTaxi-Ticket': '/TAXIPLATFORM-123'}, None, 400),
        ({}, {'X-YaTaxi-Ticket': 'TAXIPLATFORM-123/'}, None, 400),
        ({}, {'X-YaTaxi-Ticket': '/TAXIPLATFORM-123/'}, None, 400),
        (
            {},
            {
                'X-YaTaxi-Ticket': (
                    'https://st.test.yandex-team.ru/TAXIPLATFORM-123'
                ),
            },
            'TAXIPLATFORM-123',
            200,
        ),
        (
            {},
            {
                'X-YaTaxi-Ticket': (
                    'https://st.test.yandex-team.ru/TAXIPLATFORM-123/'
                ),
            },
            'TAXIPLATFORM-123',
            200,
        ),
        (
            {},
            {
                'X-YaTaxi-Ticket': (
                    'https://st.not-yandex-team.ru/TAXIPLATFORM-123'
                ),
            },
            None,
            400,
        ),
        (
            {},
            {
                'X-YaTaxi-Ticket': (
                    'https://not-st.yandex-team.ru/TAXIPLATFORM-123'
                ),
            },
            None,
            400,
        ),
    ],
)
async def test_service_with_no_response(
        patch,
        data,
        headers,
        valid_ticket_key,
        expected,
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        patch_audit_log,
):
    @patch_aiohttp_session('http://unstable-service.yandex.net')
    def patch_request(*args, **kwargs):
        return response_mock(read=b'ok')

    @patch('taxi.util.audit.TicketChecker.check')
    async def ticket_check_mock(ticket_key, *args, **kwargs):
        if valid_ticket_key:
            assert ticket_key == valid_ticket_key
            return None
        raise audit.TicketError('Wrong ticket')

    @patch('taxi.stq.client.put')
    # pylint: disable=unused-variable
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    data_as_str = json.dumps(data) if isinstance(data, dict) else data
    response = await taxi_api_admin_client.request(
        'POST', URL, data=data_as_str, headers=headers,
    )
    assert response.status == expected
    if expected == 200:
        audit_action_request = patch_audit_log.only_one_request()
        assert audit_action_request['ticket'] == valid_ticket_key
        request_data = json.loads(patch_request.calls[0]['kwargs']['data'])
        assert request_data == data
    if headers.get('X-YaTaxi-Ticket') is not None:
        assert len(ticket_check_mock.calls) == 1
    else:
        assert not ticket_check_mock.calls
