import datetime
import uuid

import pytest

from tests_blocklist import dates
from tests_blocklist import utils

MECHANICS_SETTINGS = {
    'taximeter': {
        'reasons': {
            '22222222-2222-2222-2222-222222222222': [
                'key_without_translation',
            ],
        },
    },
}


def _make_identity(url_prefix):
    if url_prefix == 'admin':
        return dict(id='user777', name='jorka', type='support')
    if url_prefix == 'internal':
        return dict(id='link', name='service', type='script')
    return dict()


def _prepare_request(url_prefix, block, identity):
    headers = dict()
    headers['Content-Type'] = 'application/json'
    headers['X-Idempotency-Token'] = 'token'
    if url_prefix == 'admin':
        headers['X-Yandex-Login'] = identity['name']
        headers['X-Yandex-UID'] = identity['id']
        return block, headers
    if url_prefix == 'internal':
        request = dict(block=block, identity=identity)
        return request, headers

    return dict(), dict()


async def _add_block(taxi_blocklist, url_prefix, block, identity):
    request, headers = _prepare_request(url_prefix, block, identity)
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/add', json=request, headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    block_id = body.pop('block_id')
    assert not body

    return block_id


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_simple(pgsql, taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    block_id = await _add_block(
        taxi_blocklist, url_prefix, add_request, identity,
    )

    assert utils.load_meta(pgsql, block_id) == add_request.get('meta', {})
    assert utils.load_kwargs(pgsql, block_id) == utils.normalize_car_in_kwargs(
        add_request['kwargs'],
    )

    block = utils.load_block(pgsql, block_id)
    assert block.pop('revision')
    assert block == dict(
        id=block_id,
        mechanics=add_request.get('mechanics', 'taximeter'),
        predicate_id=add_request['predicate_id'],
        status='active',
        expires=None,
        reason=add_request['reason'],
    )


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_block_twice(pgsql, taxi_blocklist, add_request, url_prefix):
    blocks = []
    identity = _make_identity(url_prefix)
    for _ in range(2):
        block_id = await _add_block(
            taxi_blocklist, url_prefix, add_request, identity,
        )
        blocks.append(block_id)

    assert len(set(blocks)) == 1

    cursor = pgsql['blocklist'].cursor()
    cursor.execute(
        f'SELECT COUNT(*) FROM blocklist.blocks WHERE id = \'{blocks[0]}\'',
    )
    assert next(cursor)[0] == 1


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_reason_as_message(
        pgsql, taxi_blocklist, add_request, url_prefix,
):
    message = 'My awesome block reason'
    add_request['reason']['message'] = message

    identity = _make_identity(url_prefix)
    block_id = await _add_block(
        taxi_blocklist, url_prefix, add_request, identity,
    )

    assert utils.load_block(pgsql, block_id)['reason']['message'] == message


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_mechanics(pgsql, taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    add_request['mechanics'] = 'qc_dkvu'
    block_id = await _add_block(
        taxi_blocklist, url_prefix, add_request, identity,
    )

    assert utils.load_block(pgsql, block_id)['mechanics'] == 'qc_dkvu'


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_temp_block(pgsql, taxi_blocklist, add_request, url_prefix):
    expires = dates.timestring(dates.utcnow() + datetime.timedelta(days=30))
    add_request['expires'] = expires
    identity = _make_identity(url_prefix)
    block_id = await _add_block(
        taxi_blocklist, url_prefix, add_request, identity,
    )

    assert (
        dates.timestring(utils.load_block(pgsql, block_id)['expires'])
        == expires
    )


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_mechanics_not_supported(
        taxi_blocklist, add_request, url_prefix,
):
    identity = _make_identity(url_prefix)
    add_request['mechanics'] = 'not_allowed'
    request, headers = _prepare_request(url_prefix, add_request, identity)
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/add', json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'MECHANICS_NOT_FOUND'


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_predicate_not_found(taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    add_request['predicate_id'] = str(uuid.uuid4())
    request, headers = _prepare_request(url_prefix, add_request, identity)

    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/add', json=request, headers=headers,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'PREDICATE_NOT_FOUND'


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_predicate_not_allowed(taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    add_request['predicate_id'] = '44444444-4444-4444-4444-444444444444'
    request, headers = _prepare_request(url_prefix, add_request, identity)

    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/add', json=request, headers=headers,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'PREDICATE_NOT_ALLOWED'


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_kwargs_does_not_match(taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    add_request['kwargs'].pop('park_id')
    request, headers = _prepare_request(url_prefix, add_request, identity)
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/add', json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'KWARGS_DOES_NOT_MATCH_PREDICATE'


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_kwargs_are_missing(taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    add_request['kwargs'] = dict(
        park_id=add_request['kwargs']['park_id'],
        license_id=add_request['kwargs']['car_number'],
    )
    request, headers = _prepare_request(url_prefix, add_request, identity)
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/add', json=request, headers=headers,
    )

    assert response.status_code == 400
    body = response.json()
    assert body['code'] == 'KWARGS_ARE_MISSING'
    assert 'car_number' in body['message']


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_reason_is_empty(taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    add_request['reason'] = dict()
    request, headers = _prepare_request(url_prefix, add_request, identity)
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/add', json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'REASON_IS_EMPTY'


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_reason_not_allowed(taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    add_request['reason'] = dict(key='not_allowed_reason')
    request, headers = _prepare_request(url_prefix, add_request, identity)
    response = await taxi_blocklist.post(
        f'{url_prefix}/blocklist/v1/add', json=request, headers=headers,
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'REASON_NOT_ALLOWED'


# test translation


@pytest.mark.translations(
    taximeter_backend_driver_messages=dict(
        block_key_1=dict(ru='Машина %(number)s заблокирована без причин'),
    ),
)
async def test_with_args(taxi_blocklist, add_request, headers):
    add_request['meta'] = dict(number='12345')
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200


@pytest.mark.translations(
    taximeter_backend_driver_messages=dict(
        block_key_1=dict(ru='Машина %(number)s заблокирована без причин'),
    ),
)
async def test_missing_args(taxi_blocklist, add_request, headers):
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 400
    body = res.json()
    assert body['code'] == 'REASON_SUBSTITUTE_ERROR'
    assert 'number' in body['message']


@pytest.mark.disable_config_check
@pytest.mark.config(BLOCKLIST_MECHANICS_SETTINGS=MECHANICS_SETTINGS)
async def test_missing_translation(taxi_blocklist, add_request, headers):
    add_request['reason'] = dict(key='key_without_translation')
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )

    assert res.status_code == 400
    body = res.json()
    assert body['code'] == 'TRANSLATION_FAILED'
    assert 'key_without_translation' in body['message']


@pytest.mark.disable_config_check
@pytest.mark.config(BLOCKLIST_MECHANICS_SETTINGS=MECHANICS_SETTINGS)
async def test_missing_reason(taxi_blocklist, add_request, headers):
    add_request['reason'] = {}
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )

    assert res.status_code == 400
    body = res.json()
    assert body['code'] == 'REASON_IS_EMPTY'


@pytest.mark.parametrize('url_prefix', ['admin', 'internal'])
async def test_kwargs_indexes(pgsql, taxi_blocklist, add_request, url_prefix):
    identity = _make_identity(url_prefix)
    block_id = await _add_block(
        taxi_blocklist, url_prefix, add_request, identity,
    )

    assert utils.load_kwargs_with_indexes(pgsql, block_id) == {
        'car_number': {True, 'NUМВЕR_1'},
        'park_id': {False, 'park_1'},
    }
