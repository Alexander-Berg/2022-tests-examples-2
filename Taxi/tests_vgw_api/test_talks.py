import datetime
import json
import typing

import pytest

INVALID_PHONE = 'invalid_phone'


def _talk_to_db_row(talk: typing.Dict[str, typing.Any]) -> typing.Tuple:
    return (
        talk['id'],
        datetime.datetime.fromisoformat(talk['start']),
        talk['length'],
        talk['redirection_id'],
        talk['caller'],
        f'id{talk["caller"][-3:]}'
        if talk['caller'] != INVALID_PHONE
        else None,
        talk['call_result'].get('succeeded'),
        talk['call_result'].get('status'),
        talk['call_result'].get('dial_time'),
    )


@pytest.mark.config(
    VGW_API_GATEWAY_SHORT_TALKS_CHECK_SETTINGS={
        '__default__': {'short_talk_max_len_s': 50},
        'gateway_id_1': {'short_talk_max_len_s': 20},
    },
)
async def test_post_talks(taxi_vgw_api, mockserver, pgsql, statistics):
    @mockserver.json_handler('/personal/v2/phones/bulk_store')
    def _mock_personal(request):
        request_body = json.loads(request.get_data())
        assert request_body['validate']
        response = {'items': []}
        for item in request_body['items']:
            if item['value'] == INVALID_PHONE:
                response['items'].append(
                    {'value': item['value'], 'error': 'Invalid phone'},
                )
            else:
                response['items'].append(
                    {'value': item['value'], 'id': f'id{item["value"][-3:]}'},
                )
        return response

    talks = [
        {
            'id': 'talk_id_1',
            'start': '2019-03-20T12:40:00+03:00',
            'length': 10,
            'redirection_id': 'fwd_id_1',
            'caller': '+79000000001',
            'callee': '+71111111111',
            'call_result': {
                'succeeded': True,
                'status': 'test status',
                'dial_time': 5,
            },
        },
        {
            'id': 'talk_id_2',
            'start': '2019-03-20T13:20:00+03:00',
            'length': 1,
            'redirection_id': 'fwd_id_1',
            'caller': '+79000000002',
            'callee': '+72222222222',
            'call_result': {
                'succeeded': False,
                'status': 'bad status',
                'dial_time': 15,
            },
        },
        {
            'id': 'talk_id_3',
            'start': '2019-03-20T13:30:00+03:00',
            'length': 3,
            'redirection_id': 'fwd_id_3',
            'caller': INVALID_PHONE,
            'callee': '+72222222222',
            'call_result': {},
        },
        {
            'id': 'talk_id_4',
            'start': '2019-03-20T13:10:00+03:00',
            'length': 23,
            'redirection_id': 'unknown_fwd_id',
            'caller': '+79000000004',
            'callee': '+72222222222',
            'call_result': {
                'succeeded': False,
                'status': 'bad status',
                'dial_time': 15,
            },
        },
        {
            'id': 'talk_id_5',
            'start': '2019-03-20T12:50:00+03:00',
            'length': 42,
            'redirection_id': 'fwd_id_1',
            'caller': '+79000000001',
            'callee': '+71111111111',
            'call_result': {
                'succeeded': False,
                'status': 'bad status',
                'dial_time': 10,
            },
        },
    ]
    async with statistics.capture(taxi_vgw_api) as capture:
        response = await taxi_vgw_api.post('/v1/talks', {'talks': talks})
        assert response.status_code == 200

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT id, created_at, length, forwarding_id, caller_phone, '
        'caller_phone_id, succeeded, status, dial_time '
        'FROM forwardings.talks '
        'ORDER BY id',
    )
    result = cursor.fetchall()
    cursor.close()

    # Regular talk
    assert result[0] == _talk_to_db_row(talks[0])
    # Already exists
    assert result[1] != _talk_to_db_row(talks[1])
    # Invalid phone, null call result and region_id
    assert result[2] == _talk_to_db_row(talks[2])
    # Unknown forwarding
    assert _talk_to_db_row(talks[3]) not in result
    # Check repeated phone
    assert result[3] == _talk_to_db_row(talks[4])

    expected_statistics = {
        'talks.total.gateway.gateway_id_1.region.1': 2,
        'talks.total.gateway.gateway_id_2.region.0': 1,
        'talks.success.gateway.gateway_id_1.region.1': 1,
        'talks.fail.gateway.gateway_id_1.region.1': 1,
        'talks.length.sum.gateway.gateway_id_1': 52,
        'talks.length.sum.gateway.gateway_id_2': 3,
        'talks.short.gateway.gateway_id_1.region.1': 1,
        'talks.short.gateway.gateway_id_2.region.0': 1,
    }
    for key, value in expected_statistics.items():
        assert capture.statistics[key] == value
    null_statistics = [
        'talks.success.gateway.gateway_id_2.region.0',
        'talks.fail.gateway.gateway_id_2.region.0',
    ]
    for key in null_statistics:
        assert key not in capture.statistics
