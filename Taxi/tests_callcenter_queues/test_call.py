import pytest


CURRENT_TIME = '2022-06-08T11:55:24+0000'


def v1_call_response_item(
        call_number, queue, call_guid, endreason, agent_id, yandex_uid,
):
    return {
        'asterisk_call_id': call_number,
        'routing_id': call_number,
        'metaqueue': queue,
        'subcluster': call_number,
        'status': 'completed',
        'last_event_at': CURRENT_TIME,
        'call_guid': call_guid,
        'called_number': '88005553535',
        'abonent_phone_id': call_number,
        'queued_at': CURRENT_TIME,
        'answered_at': CURRENT_TIME,
        'completed_at': CURRENT_TIME,
        'endreason': endreason,
        'transfered_to_number': call_number,
        'sip_username': agent_id,
        'created_at': CURRENT_TIME,
        'yandex_uid': yandex_uid,
        'update_seq': int(call_number),
    }


@pytest.mark.parametrize(
    ['body', 'expected_status', 'expected_response'],
    (
        pytest.param(
            {'call_guid': '1'},
            200,
            {
                'calls': [
                    v1_call_response_item(
                        '1', 'queue1', '1', 'hangup', '111', '1001',
                    ),
                ],
            },
            id='ok',
        ),
        pytest.param(
            {'call_guid': '0'}, 200, {'calls': []}, id='guid_without_calls',
        ),
        pytest.param(
            {'call_guid': '2'},
            200,
            {
                'calls': [
                    v1_call_response_item(
                        '3', 'queue2', '2', 'hangup', '222', '1002',
                    ),
                    v1_call_response_item(
                        '2', 'queue1', '2', 'forward', '111', '1001',
                    ),
                ],
            },
            id='two calls (more recent comes first)',
        ),
        pytest.param(
            {'call_guid': '3'},
            200,
            {
                'calls': [
                    v1_call_response_item(
                        '4', 'queue1', '3', 'hangup', '1000000111', '1111111',
                    ),
                ],
            },
            id='deleted operator',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
async def test_v1_call_handler(
        taxi_callcenter_queues, body, expected_status, expected_response,
):
    response = await taxi_callcenter_queues.post('/v1/call/', json=body)
    assert response.status == expected_status
    assert response.json() == expected_response
