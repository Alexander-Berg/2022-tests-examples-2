import collections
import uuid

import pytest


async def test_empty(taxi_blocklist):
    res = await taxi_blocklist.post('/blocklist/v1/list', json={})
    assert res.status_code == 400


async def test_simple(taxi_blocklist, list_request):
    res = await taxi_blocklist.post('/blocklist/v1/list', json=list_request)
    assert res.status_code == 200


async def test_list_full_response(taxi_blocklist, list_request, load_json):
    res = await taxi_blocklist.post('/blocklist/v2/list', json=list_request)
    body = res.json()
    assert len(body['blocks']) == 9

    expected_body = load_json('list_response.json')
    assert body == expected_body


async def test_limit(taxi_blocklist, list_request):
    limit = 5
    list_request['limit'] = limit
    res = await taxi_blocklist.post('/blocklist/v1/list', json=list_request)
    assert res.status_code == 200
    res_body = res.json()
    assert len(res_body['blocks']) == limit


async def test_from(taxi_blocklist, list_request):
    revision = '4'
    list_request['revision'] = revision
    res = await taxi_blocklist.post('/blocklist/v1/list', json=list_request)
    assert res.status_code == 200
    res_body = res.json()
    assert len(res_body['blocks']) == 5


# prevent default blocks population
@pytest.mark.pgsql('blocklist', files=['pg_blocklist.sql'])
@pytest.mark.suspend_periodic_tasks('block-expiration')
async def test_blocks_expire(
        taxi_blocklist, add_request, list_request, headers,
):
    expires = [
        '2000-01-01T00:00:01Z',  # past
        '2000-01-01T00:00:01Z',  # past
        '2000-01-01T00:00:01Z',  # past
        None,  # never
        '3000-01-01T00:00:01Z',  # future
    ]
    for expire_time in expires:
        headers['X-Idempotency-Token'] = uuid.uuid4().hex
        add_request['expires'] = expire_time
        res = await taxi_blocklist.post(
            '/admin/blocklist/v1/add', json=add_request, headers=headers,
        )
        assert res.status_code == 200
    await taxi_blocklist.run_periodic_task('block-expiration')
    res = await taxi_blocklist.post('/blocklist/v1/list', json=list_request)
    assert res.status_code == 200
    res_body = res.json()
    assert len(res_body['blocks']) == 5
    assert collections.Counter(
        [block['status'] for block in res_body['blocks']],
    ) == {'active': 2, 'inactive': 3}


async def test_list_empty_response(taxi_blocklist, list_request):
    res = await taxi_blocklist.post('/blocklist/v1/list', json=list_request)
    assert res.status_code == 200

    last_revision = res.json()['revision']
    list_request['revision'] = last_revision
    res = await taxi_blocklist.post('/blocklist/v1/list', json=list_request)
    assert res.status_code == 200

    assert res.json()['revision'] == last_revision


async def test_list_with_meta(taxi_blocklist, list_request):
    list_request['revision'] = '0'
    list_request['with_meta'] = True
    res = await taxi_blocklist.post('/blocklist/v1/list', json=list_request)
    assert res.status_code == 200
    assert res.json()['blocks'][0].get('meta') and res.json()['blocks'][0].get(
        'kwargs',
    )


@pytest.mark.pgsql('blocklist', files=['pg_blocklist.sql'])
async def test_list_with_meta_empty(taxi_blocklist, list_request):
    list_request['with_meta'] = True
    del list_request['revision']
    res = await taxi_blocklist.post('/blocklist/v1/list', json=list_request)
    assert res.json()['revision'] == '0'


async def test_list_kwarg_indexes(taxi_blocklist, list_request):
    limit = 1
    list_request['limit'] = limit
    res = await taxi_blocklist.post('/blocklist/v2/list', json=list_request)
    blocks = res.json()['blocks']
    assert len(blocks) == 1
    assert blocks[0]['kwargs']['car_number']['indexible']
    assert not blocks[0]['kwargs']['park_id']['indexible']
