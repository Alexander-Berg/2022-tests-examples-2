import pytest

from tests_cargo_crm import const


@pytest.mark.parametrize(
    'interface, flow, client_events_code, expected_code',
    [
        ('b2bweb', 'phoenix', 200, 200),
        ('not_interface_name', 'phoenix', 200, 400),
        ('b2bweb', 'not_flow_name', 200, 400),
        ('b2bweb', 'phoenix', 500, 500),
    ],
)
async def test_func_notify_ticket_update(
        taxi_cargo_crm,
        mockserver,
        interface,
        flow,
        client_events_code,
        expected_code,
):
    @mockserver.json_handler('client-events/push')
    def _handler(request):
        assert request.json == {
            'service': 'cargo-crm',
            'event': 'ticket:updated',
            'event_id': const.TICKET_ID,
            'channel': interface + ':' + flow,
            'payload': {'server_event_id': 'procaas_event_id_1'},
        }

        body = None
        if client_events_code == 200:
            body = {'version': 'new_version'}
        else:
            body = const.BAD_RESPONSE
        return mockserver.make_response(status=client_events_code, json=body)

    response = await taxi_cargo_crm.post(
        '/functions/notify-ticket-updated',
        json={
            'name': 'ticket:updated',
            'interface': interface,
            'flow': flow,
            'ticket_id': const.TICKET_ID,
            'server_event_id': 'procaas_event_id_1',
        },
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {}
