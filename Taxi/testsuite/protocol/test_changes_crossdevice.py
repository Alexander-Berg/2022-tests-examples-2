import dateutil.parser
import pytest


@pytest.mark.now('2017-07-19T17:15:15+0000')
@pytest.mark.parametrize('crossdevice_user_first', [True, False])
@pytest.mark.parametrize(
    'handler, change, change_alias',
    [
        ('3.0/changecomment', {'comment': 'some_comment'}, None),
        ('3.0/changeporchnumber', {'porchnumber': '4'}, None),
        (
            '3.0/changeclientgeosharing',
            {'client_geo_sharing_enabled': True},
            ('client_geo_sharing', True),
        ),
        ('3.0/changeaction', {'action': 'user_ready'}, ('user_ready', True)),
        ('3.0/changecorpcostcenter', {'corp_cost_center': 'corp-123'}, None),
    ],
)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_crossdevice_common(
        taxi_protocol,
        load,
        db,
        now,
        crossdevice_user_first,
        handler,
        change,
        change_alias,
        mockserver,
):
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'
    orderid = '8c83b49edb274ce0992f337061043333'
    crossdevice_user_id = 'crossdeviceuser00000000000000000'

    @mockserver.json_handler(
        '/corp_integration_api/cost_centers/check/by_user_id',
    )
    def mock_cost_centers_check_by_user_id(r):
        return {'can_use': True}

    change_name, change_value = list(change.items())[0]
    if change_alias is not None:
        change_name, change_value = change_alias
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {'orderid': orderid, 'created_time': created_time.isoformat()}
    request.update(change)
    sequence = [user_id, crossdevice_user_id]
    responses = []
    if crossdevice_user_first:
        sequence = reversed(sequence)
    for user_id in sequence:
        request['id'] = user_id
        responses.append(taxi_protocol.post(handler, request))
    for i, resp in enumerate(responses):
        assert resp.status_code == 200, (resp.text, user_id, i)
        change_json = resp.json()
        change_json.pop('change_id')
        assert change_json == {
            'status': 'success',
            'name': change_name,
            'value': change_value,
        }
