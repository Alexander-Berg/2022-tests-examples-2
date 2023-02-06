# pylint: disable=protected-access
import json

import pytest


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(SERVICE_ROLES_ENABLED=True)
@pytest.mark.config(
    SERVICE_ROLES={
        'replication': {'sync_data-test_map_data': ['src_service']},
    },
)
@pytest.mark.parametrize(
    'parallel_insert',
    [
        pytest.param(False, id='not parallel_insert'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                REPLICATION_QUEUE_MONGO_PARALLEL_INSERT={
                    'sync_data': {'__default__': True},
                },
            ),
            id='parallel_insert',
        ),
    ],
)
@pytest.mark.parametrize(
    'data_file,expected_inserted',
    [
        ('sync_data.json', {'foo'}),
        pytest.param(
            'sync_data_no_check_hash.json',
            None,
            marks=pytest.mark.config(
                REPLICATION_QUEUE_MONGO_SETTINGS={
                    'sync_data_check_hash': {'test_map_data': False},
                },
            ),
        ),
    ],
)
async def test_sync_data(
        replication_client,
        replication_app,
        patch_tvm_ticket_check,
        dummy_sha1,
        load_py_json,
        data_file,
        expected_inserted,
        parallel_insert,
):
    patch_tvm_ticket_check('TVM_key', 'src_service')
    data = load_py_json(data_file)
    rule_name = data['rule_name']
    union_staging_db = replication_app.rule_keeper.union_staging_db.get_queue(
        rule_name,
    )
    if expected_inserted:
        docs = await union_staging_db.union_find({}).to_list()
        ids_before = {doc['_id'] for doc in docs}
        assert not expected_inserted & ids_before

    response = await replication_client.post(
        f'/sync_data/{rule_name}',
        data=json.dumps(data['request']),
        headers={'X-Ya-Service-Ticket': 'TVM_key'},
    )
    assert response.status == 200, await response.text()
    assert await response.json() == data['response']

    if expected_inserted:
        docs = await union_staging_db.union_find({}, raw=True).to_list()
        ids = {doc['_id'] for doc in docs}
        assert ids - ids_before == expected_inserted
        assert all(isinstance(doc['data'], bytes) for doc in docs)
