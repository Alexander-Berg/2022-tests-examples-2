import uuid

import pytest

from tests_blocklist import utils


async def _add_block(taxi_blocklist, add_request, headers):
    response = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert response.status_code == 200
    return add_request['predicate_id'], response.json()['block_id']


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_delete(
        pgsql, load_json, taxi_blocklist, add_request, headers, url_prefix,
):
    predicate_id, block_id = await _add_block(
        taxi_blocklist, add_request, headers,
    )

    delete_request = load_json(f'{url_prefix}_delete_request.json')
    delete_request['block']['block_id'] = block_id
    delete_request['predicate_id'] = predicate_id
    delete_request['mechanics'] = 'taximeter'
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/delete',
        json=delete_request,
        headers=headers,
    )
    assert response.status_code == 200
    assert utils.load_block(pgsql, block_id)['status'] == 'inactive'


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_delete_already_deleted(
        load_json, taxi_blocklist, add_request, headers, url_prefix,
):
    predicate_id, block_id = await _add_block(
        taxi_blocklist, add_request, headers,
    )

    delete_request = load_json(f'{url_prefix}_delete_request.json')
    delete_request['block']['block_id'] = block_id
    delete_request['predicate_id'] = predicate_id
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/delete',
        json=delete_request,
        headers=headers,
    )
    assert response.status_code == 200

    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/delete',
        json=delete_request,
        headers=headers,
    )
    assert response.status_code == 204


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_delete_non_existent(
        load_json, taxi_blocklist, headers, url_prefix,
):
    delete_request = load_json(f'{url_prefix}_delete_request.json')
    delete_request['block']['block_id'] = str(uuid.uuid4())
    delete_request['predicate_id'] = '22222222-2222-2222-2222-222222222222'
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/delete',
        json=delete_request,
        headers=headers,
    )
    assert response.status_code == 404


async def test_delete_incorrect_predicate_id(
        pgsql, load_json, taxi_blocklist, add_request, headers,
):
    _, block_id = await _add_block(taxi_blocklist, add_request, headers)

    delete_request = load_json(f'admin_delete_request.json')
    delete_request['block']['block_id'] = block_id
    delete_request['predicate_id'] = str(uuid.uuid4())
    response = await taxi_blocklist.post(
        'admin/blocklist/v1/delete', json=delete_request, headers=headers,
    )
    assert response.status_code == 404
    assert utils.load_block(pgsql, block_id)['status'] == 'active'
