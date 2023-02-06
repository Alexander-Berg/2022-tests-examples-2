import bson
import pytest


async def test_create_draft_just_works(taxi_order_core, mongodb, load_json):
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/create-draft',
        headers={'Content-Type': 'application/bson'},
        data=bson.BSON.encode(load_json('create_draft_request.json')),
    )
    assert response.status_code == 200

    resp: dict = bson.BSON.decode(response.content)
    proc_resp = resp['document']
    assert proc_resp
    assert 'updated' in proc_resp
    assert proc_resp['_id'] == proc_resp['order']['_id']
    assert proc_resp['_shard_id'] == proc_resp['order']['_shard_id'] == 0

    proc_db = mongodb.order_proc.find_one()
    assert proc_db == proc_resp


@pytest.mark.experiments3(filename='exp3_order_shards.json')
async def test_create_draft_chooses_shard(taxi_order_core, mongodb, load_json):
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/create-draft',
        headers={'Content-Type': 'application/bson'},
        data=bson.BSON.encode(load_json('create_draft_request.json')),
    )
    assert response.status_code == 200

    resp: dict = bson.BSON.decode(response.content)
    proc_resp = resp['document']
    assert proc_resp
    assert 'updated' in proc_resp
    assert proc_resp['_id'] == proc_resp['order']['_id']
    assert proc_resp['_shard_id'] != 0
    assert proc_resp['order']['_shard_id'] != 0

    proc_db = mongodb.order_proc.find_one()
    assert proc_db == proc_resp


@pytest.mark.experiments3(filename='exp3_order_shards.json')
@pytest.mark.config(
    ORDER_CORE_USE_ALIVE_SHARD={'enabled': True, 'excluded_limit': 4},
)
@pytest.mark.parametrize('not_excluding', [5, 6, 7, 8, 9])
async def test_create_draft_excludes_if_fallback(
        taxi_order_core, mongodb, statistics, not_excluding, load_json,
):

    shards = set([5, 6, 7, 8, 9])
    shards.remove(not_excluding)

    statistics.fallbacks = [
        'order-core.mongo_shard_id{}.fallback'.format(shard)
        for shard in shards
    ]
    await taxi_order_core.invalidate_caches()

    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/create-draft',
        headers={'Content-Type': 'application/bson'},
        data=bson.BSON.encode(load_json('create_draft_request.json')),
    )
    assert response.status_code == 200

    resp: dict = bson.BSON.decode(response.content)
    proc_resp = resp['document']
    assert proc_resp
    assert 'updated' in proc_resp
    assert proc_resp['_id'] == proc_resp['order']['_id']
    assert (
        proc_resp['_shard_id']
        == proc_resp['order']['_shard_id']
        == not_excluding
    )

    proc_db = mongodb.order_proc.find_one()
    assert proc_db == proc_resp


@pytest.mark.experiments3(filename='exp3_order_shards.json')
@pytest.mark.config(
    ORDER_CORE_USE_ALIVE_SHARD={'enabled': True, 'excluded_limit': 4},
)
async def test_create_draft_excluded_limit(
        mongodb, taxi_order_core, statistics, load_json,
):

    statistics.fallbacks = [
        'order-core.mongo_shard_id{}.fallback'.format(shard)
        for shard in [5, 6, 7, 8, 9]
    ]
    await taxi_order_core.invalidate_caches()

    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/create-draft',
        headers={'Content-Type': 'application/bson'},
        data=bson.BSON.encode(load_json('create_draft_request.json')),
    )
    assert response.status_code == 200

    resp: dict = bson.BSON.decode(response.content)
    proc_resp = resp['document']
    assert proc_resp
    assert 'updated' in proc_resp
    assert proc_resp['_id'] == proc_resp['order']['_id']
    assert proc_resp['_shard_id'] == proc_resp['order']['_shard_id'] != 0

    proc_db = mongodb.order_proc.find_one()
    assert proc_db == proc_resp
