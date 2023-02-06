import hashlib

import pytest

from tests_cargo_crm import const


@pytest.fixture(name='push_salt')
def _push_salt():
    # value like in service.yaml Secdist.settings_override.PUSHES_SALT
    return 'mysalt'


@pytest.mark.parametrize('requester_uid', ['322'])
@pytest.mark.parametrize(
    'interface, flow, client_events_code, expected_code',
    [
        ('b2bweb', 'phoenix', 200, 200),
        ('not_interface_name', 'phoenix', 200, 400),
        ('b2bweb', 'not_flow_name', 200, 400),
        ('b2bweb', 'phoenix', 500, 500),
    ],
)
async def test_func_notify_response_ready(
        taxi_cargo_crm,
        mockserver,
        interface,
        flow,
        requester_uid,
        push_salt,
        client_events_code,
        expected_code,
):
    @mockserver.json_handler('client-events/push')
    def _handler(request):
        assert request.json == {
            'service': 'cargo-crm',
            'event': 'operation:response',
            'event_id': const.TICKET_ID,
            'channel': _get_channel_name(
                interface, flow, requester_uid, push_salt,
            ),
            'payload': {
                'operation_id': 'operation_id_1',
                'server_event_id': 'procaas_event_id',
            },
        }

        body = None
        if client_events_code == 200:
            body = {'version': 'new_version'}
        else:
            body = const.BAD_RESPONSE
        return mockserver.make_response(status=client_events_code, json=body)

    response = await taxi_cargo_crm.post(
        '/functions/notify-response-ready',
        json={
            'name': 'operation:response',
            'interface': interface,
            'flow': flow,
            'ticket_id': const.TICKET_ID,
            'requester_uid': requester_uid,
            'operation_id': 'operation_id_1',
            'server_event_id': 'procaas_event_id',
        },
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {}


def _get_channel_name(
        interface, flow, channel_unhashed_ending, push_salt,
) -> str:
    channel = interface + ':' + flow
    if channel_unhashed_ending:
        channel += ':'
        value = hashlib.sha1()
        value.update(channel_unhashed_ending.encode())
        value.update(push_salt.encode())
        return channel + value.hexdigest()

    return channel
