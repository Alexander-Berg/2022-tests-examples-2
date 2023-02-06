import pytest

from replication.common import queue_mongo
from replication.common.queue_mongo import exceptions


@pytest.mark.parametrize(
    ['rule_name', 'input_json', 'expected_status', 'error_text'],
    [
        (
            'example_rule',
            {'items': [{'id': '1', 'data': {'key1': 'value1'}}]},
            200,
            None,
        ),
        (
            'example_rule',
            {
                'items': [
                    {'id': '2', 'data': {'key2': 'value2'}},
                    {'id': '3', 'data': {'key3': 'value3'}},
                ],
            },
            200,
            None,
        ),
        (
            'example_rule',
            {
                'items': [
                    {
                        'id': '4',
                        'data': 'fail',  # "'fail' is not of type 'object'"
                    },
                ],
            },
            400,
            None,
        ),
        (
            'test_api_basestamp',
            {'items': [{'id': '1', 'data': {}}]},
            400,
            'test_api_basestamp rule uninitialized',
        ),
        (
            'not_found',
            {'items': [{'id': '1', 'data': {}}]},
            404,
            'Rule not_found not found',
        ),
    ],
)
async def test_put_data(
        replication_client,
        replication_ctx,
        rule_name,
        input_json,
        expected_status,
        error_text,
):
    response = await replication_client.post(
        f'/data/{rule_name}', json=input_json,
    )

    # check response
    assert response.status == expected_status, await response.text()
    if expected_status != 200:
        if error_text is not None:
            assert await response.text() == error_text
        return

    response_data = await response.json()
    response_items = response_data['items']
    assert len(response_items) == len(input_json['items'])
    for item, input_item in zip(response_items, input_json['items']):
        assert item['id'] == input_item['id']
        assert item['status'] == 'ok'

    # check queue state
    staging_db = replication_ctx.rule_keeper.staging_db
    input_docs = {item['id']: item['data'] for item in input_json['items']}
    docs = {
        doc['_id']: doc['data']
        async for doc in (
            staging_db.get_queue_mongo_shard('example_rule').primary.find()
        )
    }

    assert len(response_items) == len(docs)
    for item_id, input_data in input_docs.items():
        assert item_id in docs
        assert input_data == docs[item_id]


@pytest.mark.config(
    REPLICATION_SERVICE_CTL={
        'quota': {'quotas_enabled': True, 'quotas': {'example_rule': 2}},
    },
)
async def test_quotas(replication_client, replication_app, monkeypatch):
    input_json = {'items': [{'id': '1', 'data': {}}]}
    response = await replication_client.post(
        '/data/example_rule', json=input_json,
    )
    assert response.status == 200

    async def dummy_space(*args, **kwargs):
        return 33.34 * 1024 ** 2

    monkeypatch.setattr(queue_mongo, 'get_occupied_space', dummy_space)
    api_quotas = replication_app.rule_keeper.api_quotas
    await api_quotas.refresh_cache()

    exceeded_info = (
        'Quota exceeded for example_rule: occupied space=33.34 Mb > quota=2 Mb'
    )
    with pytest.raises(exceptions.QuotaExceededError, match=exceeded_info):
        api_quotas.check_exceeded('example_rule')
    response = await replication_client.post(
        '/data/example_rule', json=input_json,
    )
    assert response.status == 403


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(SERVICE_ROLES_ENABLED=True)
@pytest.mark.config(
    SERVICE_ROLES={'replication': {'put_data-example_rule': ['src_service']}},
)
@pytest.mark.parametrize(
    'headers, service_name, expected_code, expected_error',
    [
        (
            {},
            None,
            401,
            {'message': 'TVM header missing', 'code': 'tvm-auth-error'},
        ),
        (
            {'X-Ya-Service-Ticket': 'TVM_bad_key'},
            'src_service',
            401,
            {'message': 'TVM authentication error', 'code': 'tvm-auth-error'},
        ),
        ({'X-Ya-Service-Ticket': 'TVM_key'}, 'src_service', 200, None),
        (
            {'X-Ya-Service-Ticket': 'TVM_key'},
            'bad_src_service',
            403,
            {
                'details': {
                    'reason': (
                        'Service bad_src_service is not '
                        'allowed by role put_data-example_rule'
                    ),
                },
                'message': 'Service is not allowed by role',
                'code': 'tvm-auth-error',
            },
        ),
    ],
)
async def test_auth(
        replication_client,
        headers,
        service_name,
        expected_code,
        expected_error,
        patch_tvm_ticket_check,
):
    patch_tvm_ticket_check('TVM_key', service_name)

    response = await replication_client.post(
        '/data/example_rule', json={'items': []}, headers=headers,
    )
    assert response.status == expected_code, await response.text()
    if expected_error is not None:
        assert await response.json() == expected_error
