import asyncio
import datetime
import typing

import pytest

from taxi.clients import experiments3
from taxi.clients import integration_api

from taxi_corp.internal import consts
from test_taxi_corp import request_util as util


NOW = datetime.datetime.utcnow().replace(microsecond=0)
CLASS_EXPRESS = 'express'
CLASS_COURIER = 'courier'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+7'],
            'matches': ['^7'],
        },
    ],
    CORP_ENABLE_LOOKUP_TTL_CONTROL=True,
)
@pytest.mark.parametrize(
    'client, prefix',
    [
        ('taxi_corp_real_auth_client', ''),
        ('taxi_corp_tvm_client', '/internal'),
    ],
    indirect=['client'],
)
@pytest.mark.parametrize(
    'passport_mock, client_id, post_content',
    [
        pytest.param(
            'client1',
            'client1',
            util.make_order_request(),
            id='client_postpaid',
        ),
        pytest.param(
            'client2',
            'client2',
            util.make_order_request(),
            id='client_prepaid',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.usefixtures('pd_patch')
@pytest.mark.config(
    CORP_TARIFFS_HIDDEN_REQUIREMENTS=[
        'internal_hidden_requirement1',
        'internal_hidden_requirement2',
    ],
)
async def test_create_draft(
        patch,
        db,
        load_json,
        client,
        prefix,
        passport_mock,
        client_id,
        post_content,
):
    app = client.server.app
    await app.phones.refresh_cache()

    if prefix:
        auth_login = None
        auth_uid = 'external_service'
    else:
        auth_login = passport_mock + '_login'
        auth_uid = passport_mock + '_uid'

    @patch('taxi_corp.clients.protocol.ProtocolClient.geosearch')
    async def _geosearch(*args, **kwargs):
        return [
            {
                'short_text': 'short text',
                'short_text_from': 'short text from',
                'short_text_to': 'short text to',
            },
        ]

    @patch('taxi.clients.experiments3.Experiments3Client.get_config_values')
    async def _get_config_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name='corp_control_lookup_ttl',
                value={'lookup_ttl_sec': 1800, 'reason': 'thats why'},
            ),
        ]

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi.clients.integration_api.IntegrationAPIClient.profile')
    async def _order_profile(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'user_id': 'user_id'}, headers={},
        )

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_estimate')
    async def _order_estimate(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'offer': 'offer_id'}, headers={},
        )

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_draft')
    async def _order_draft(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'orderid': 'SomeOrderId'}, headers={},
        )

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch(
        'taxi_corp.clients.corp_integration_api.'
        'CorpIntegrationApiClient.corp_paymentmethods',
    )
    async def _corp_paymentmethods(*args, **kwargs):
        return {
            'methods': [
                {
                    'id': 'corp-{}'.format(client_id),
                    'can_order': True,
                    'zone_available': True,
                },
            ],
        }

    request_data = dict(
        path=f'{prefix}/1.0/client/{client_id}/order',
        json=post_content,
        headers={'X-Real-IP': '127.0.0.1', 'User-Agent': ''},
    )
    responses = await asyncio.gather(
        client.post(**request_data), client.post(**request_data),
    )

    response = responses[0]
    response_json = await response.json()
    assert response.status == responses[1].status
    assert response_json == await responses[1].json()

    assert response.status == 200, response_json
    assert response_json['_id'] == 'SomeOrderId'

    db_item = await db.corp_orders.find_one({'_id': 'SomeOrderId'})
    assert db_item['_id'] == 'SomeOrderId'
    assert db_item['created_by']['uid'] == auth_uid

    client = await db.corp_clients.find_one(
        {'_id': client_id}, projection=['features'],
    )
    if consts.ClientFeature.NEW_LIMITS in client['features']:
        assert len(_put.calls) == 3
    else:
        assert len(_put.calls) == 2

    if auth_login == 'manager1_login':
        db_user = await db.corp_users.find_one(
            {'_id': db_item['corp_user']['user_id']},
        )
        department_id = None
        for access_data in load_json('mock_access_data.json'):
            if access_data['yandex_uid'] == auth_uid:
                department_id = access_data['department_id']

        assert db_user.get('department_id') == department_id

        db_history = await db.corp_history.find_one({'p': auth_login})
        assert db_history['e']['_id'] == db_user['_id']

    # check experiments call
    exp3_calls = list(_get_config_values.calls)
    assert len(exp3_calls) == 2

    exp3_args_raw: typing.List[experiments3.ExperimentsArg] = (
        exp3_calls[0]['kwargs'].get('experiments_args', [])
    )

    exp3_args = {arg.name: arg.value for arg in exp3_args_raw}
    assert exp3_args == {
        'corp_client_id': client_id,
        'country': 'rus',
        'taxi_class': post_content['class'],
        'has_due': 'due' in post_content,
    }
