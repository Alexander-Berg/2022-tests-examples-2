import random
import string

import pytest
import yaml

from tests_api_proxy.api_proxy.utils import admin as utils_admin
from tests_api_proxy.api_proxy.utils import endpoints as utils_endpoints

ENDPOINTS_LIST = 'admin/v2/endpoints/list'
ENDPOINTS_INFO = 'admin/v2/endpoints/info'
ENDPOINTS_REVS = 'admin/v2/endpoints/revisions'
ENDPOINTS_CTRL = 'admin/v2/endpoints/control'
ENDPOINTS_CTRL_STATE = 'admin/v2/endpoints/control/state'

CURSOR_NEXT = 'next_cursor'
CURSOR_PREV = 'previous_cursor'


def _make_handler():
    default_response = ''.join(
        random.choice(string.ascii_lowercase) for i in range(15)
    )

    return {
        'default-response': default_response,
        'responses': [
            {
                'id': default_response,
                'status-code': random.choice([200, 201, 202, 203]),
                'body#string': 'hello',
                'content-type': 'application/json',
            },
        ],
        'enabled': True,
    }


@pytest.fixture(name='db_endpoints')
async def _load_endpoints(endpoints):
    random.seed(42)
    db_endpoints = {
        '/bar': [
            dict(
                put_handler=_make_handler(),
                dev_team='looney.tunes',
                duty_group_id='looney.tunes-taxi-group-id',
                duty_abc='looney.tunes-abc',
                prestable=30 if idx % 3 == 2 else None,
            )
            for idx in range(4)
        ],
        '/bazooka': [
            dict(
                put_handler=_make_handler(),
                dev_team='bugs.bunny',
                duty_group_id='bugs.bunny-taxi-group-id',
                duty_abc='bugs.bunny-abc',
                prestable=1 if idx % 3 == 1 else None,
            )
            for idx in range(2)
        ],
        '/foo': [
            dict(
                put_handler=_make_handler(),
                dev_team='acme.inc',
                duty_group_id='acme.inc-taxi-group-id',
                duty_abc='acme.inc-abc',
                prestable=5 if (idx % 3 == 0 and idx > 0) else None,
            )
            for idx in range(10)
        ],
    }

    for path, eps in db_endpoints.items():
        await endpoints.safely_create_endpoint(
            path, endpoint_id=path, **eps[0],
        )
        for ep_prev, ep_curr in zip(eps, eps[1:]):
            if ep_prev['prestable'] is not None:
                await endpoints.finalize_endpoint_prestable(
                    path, resolution='release',
                )
            await endpoints.safely_update_endpoint(
                path, endpoint_id=path, **ep_curr,
            )
    return db_endpoints


@pytest.fixture(name='db_latest_endpoints')
async def _make_db_latest_endpoints(db_endpoints):
    db_latest_endpoinst = [
        {
            'path': path,
            'summary': 'bar',  # from conftest.py,
            'dev_team': eps[-1]['dev_team'],
            'duty_group_id': eps[-1]['duty_group_id'],
            'duty_abc': eps[-1]['duty_abc'],
            'enabled': True,
            'revision': len(eps) - 1,
        }
        for path, eps in db_endpoints.items()
    ]
    for ep_def in db_latest_endpoinst:
        eps = db_endpoints[ep_def['path']]
        if eps[-1]['prestable']:
            ep_def.update(
                prestable=dict(
                    percent=eps[-1]['prestable'], revision=len(eps) - 1,
                ),
                revision=len(eps) - 2,
            )
    return db_latest_endpoinst


def filter_redundant_fields(endpoint_defs):
    for ep_def in endpoint_defs:
        ep_def.pop('created')
        ep_def.pop('id')
        ep_def.pop('cluster')


async def test_endpoints_blank_db(taxi_api_proxy):
    response = await taxi_api_proxy.get(ENDPOINTS_LIST)
    assert response.status_code == 200
    body = response.json()
    assert body == {'endpoints': []}


async def test_endpoinst_list(taxi_api_proxy, db_latest_endpoints):
    # 1. fetch all
    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST, params=dict(cluster='api-proxy'),
    )
    assert response.status_code == 200
    body = response.json()
    filter_redundant_fields(body['endpoints'])
    assert body == {'endpoints': db_latest_endpoints}

    # 2. fetch by chunks
    response = await taxi_api_proxy.get(ENDPOINTS_LIST, params=dict(size='2'))
    assert response.status_code == 200
    body = response.json()
    filter_redundant_fields(body['endpoints'])
    assert body['endpoints'] == db_latest_endpoints[:2]
    assert CURSOR_PREV not in body
    assert CURSOR_NEXT in body

    cursor_fwd = body[CURSOR_NEXT]

    # continue fetching all the rest
    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST, params=dict(cluster='api-proxy', cursor=cursor_fwd),
    )
    assert response.status_code == 200
    body = response.json()
    filter_redundant_fields(body['endpoints'])
    assert body['endpoints'] == db_latest_endpoints[2:]
    assert CURSOR_PREV in body
    assert CURSOR_NEXT not in body

    # get first chunk in backward direction
    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST,
        params=dict(
            cluster='api-proxy', size='2', cursor=cursor_fwd, order='desc',
        ),
    )
    assert response.status_code == 200
    body = response.json()
    filter_redundant_fields(body['endpoints'])
    assert body['endpoints'] == db_latest_endpoints[:2][::-1]
    assert CURSOR_PREV in body
    assert CURSOR_NEXT not in body

    # 3. fetch by chunks from behind
    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST,
        params=dict(cluster='api-proxy', size='2', order='desc'),
    )
    assert response.status_code == 200
    body = response.json()
    filter_redundant_fields(body['endpoints'])
    assert body['endpoints'] == db_latest_endpoints[-2:][::-1]
    assert CURSOR_PREV not in body
    assert CURSOR_NEXT in body

    cursor_bwd = body[CURSOR_NEXT]

    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST,
        params=dict(
            cluster='api-proxy', size='100', cursor=cursor_bwd, order='desc',
        ),
    )
    assert response.status_code == 200
    body = response.json()
    filter_redundant_fields(body['endpoints'])
    assert body['endpoints'] == db_latest_endpoints[:-2][::-1]
    assert CURSOR_PREV in body
    assert CURSOR_NEXT not in body


async def test_endpoints_info(taxi_api_proxy, db_endpoints):
    for path, eps in db_endpoints.items():
        for rev, ep_def in enumerate(eps):
            params = dict(cluster='api-proxy', id=path, revision=str(rev))
            response = await taxi_api_proxy.get(ENDPOINTS_INFO, params=params)
            assert response.status_code == 200, response.content
            body = response.json()
            utils_endpoints.remove_plain_yaml_handlers(body)
            assert body['id'] == path
            assert body['path'] == path
            assert body['dev_team'] == ep_def['dev_team']
            assert body['revision'] == rev
            assert body['handlers'] == {'put': ep_def['put_handler']}

    response = await taxi_api_proxy.get(
        ENDPOINTS_INFO,
        params=dict(cluster='api-proxy', id='/foo', revision='42'),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'endpoint_revision_not_found',
        'message': 'Endpoint \'/foo\' of revision \'42\' not found',
    }

    response = await taxi_api_proxy.get(
        ENDPOINTS_INFO,
        params=dict(cluster='api-proxy', id='/blabla', revision='0'),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'endpoint_not_found',
        'message': 'Endpoint not found',
    }

    response = await taxi_api_proxy.get(
        ENDPOINTS_INFO, params=dict(cluster='api-proxy', id='/foo'),
    )
    assert response.status_code == 200, response.content
    body = response.json()
    assert body['path'] == '/foo'
    assert body['revision'] == 8


async def test_plain_endpoint_handler_info(taxi_api_proxy, testpoint, load):
    plain_def = load('simple_formatted_get_handler.yaml')
    path = '/pretty'
    await utils_admin.create_endpoint(
        taxi_api_proxy, testpoint, path=path, get_plain_handler=plain_def,
    )

    response = await taxi_api_proxy.get(
        ENDPOINTS_INFO, params=dict(cluster='api-proxy', id=path, revision=0),
    )
    body = response.json()
    assert 'get' in body['handlers']
    assert 'get_plain' in body['handlers']
    assert body['handlers']['get_plain'] == plain_def
    assert body['handlers']['get'] == yaml.load(plain_def)


async def test_endpoints_over_revisions(taxi_api_proxy, db_endpoints):
    # 1. try to get all noname revs
    path = '/fgup_nii_rosgostech_voentorg'
    response = await taxi_api_proxy.get(
        ENDPOINTS_REVS, params=dict(cluster='api-proxy', id=path),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'endpoint_not_found',
        'message': 'Endpoint not found',
    }

    # 2. get all /foo revs
    path = '/foo'
    response = await taxi_api_proxy.get(
        ENDPOINTS_REVS, params=dict(cluster='api-proxy', id=path),
    )
    assert response.status_code == 200
    body = response.json()
    assert [rev['revision'] for rev in body['revisions']] == list(
        range(len(db_endpoints[path])),
    )

    # since we want to check 'created' field later
    db_revisions = body['revisions']

    # 3. fetch by chunks
    response = await taxi_api_proxy.get(
        ENDPOINTS_REVS, params=dict(cluster='api-proxy', id=path, size='3'),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['revisions'] == db_revisions[:3]
    assert CURSOR_PREV not in body
    assert CURSOR_NEXT in body

    cursor_fwd_3 = body[CURSOR_NEXT]

    # continue fetching all the rest
    response = await taxi_api_proxy.get(
        ENDPOINTS_REVS,
        params=dict(cluster='api-proxy', id=path, cursor=cursor_fwd_3),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['revisions'] == db_revisions[3:]
    assert CURSOR_PREV in body
    assert CURSOR_NEXT not in body

    # or continue chunking
    response = await taxi_api_proxy.get(
        ENDPOINTS_REVS,
        params=dict(
            cluster='api-proxy', id=path, size='3', cursor=cursor_fwd_3,
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['revisions'] == db_revisions[3:6]
    assert CURSOR_PREV in body
    assert CURSOR_NEXT in body

    cursor_fwd_6 = body[CURSOR_NEXT]

    # reverse the chunk
    response = await taxi_api_proxy.get(
        ENDPOINTS_REVS,
        params=dict(
            cluster='api-proxy',
            id=path,
            size='3',
            cursor=cursor_fwd_6,
            order='desc',
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['revisions'] == db_revisions[3:6][::-1]
    assert CURSOR_PREV in body
    assert CURSOR_NEXT in body

    # 4. fetch by chunks from behind
    response = await taxi_api_proxy.get(
        ENDPOINTS_REVS,
        params=dict(cluster='api-proxy', id=path, size='3', order='desc'),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['revisions'] == db_revisions[-3:][::-1]
    assert CURSOR_PREV not in body
    assert CURSOR_NEXT in body

    cursor_bwd = body[CURSOR_NEXT]

    response = await taxi_api_proxy.get(
        ENDPOINTS_REVS,
        params=dict(
            cluster='api-proxy',
            id=path,
            size='100',
            cursor=cursor_bwd,
            order='desc',
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['revisions'] == db_revisions[:-3][::-1]
    assert CURSOR_PREV in body
    assert CURSOR_NEXT not in body


async def test_endpoints_control(taxi_api_proxy, db_endpoints):
    response = await taxi_api_proxy.get(
        ENDPOINTS_CTRL, params=dict(cluster='api-proxy', id='/foo'),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['revision'] == 8
    assert 'prestable' in body
    assert body['prestable'] == {'revision': 9, 'percent': 5}

    response = await taxi_api_proxy.get(
        ENDPOINTS_CTRL, params=dict(cluster='api-proxy', id='/bar'),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['revision'] == 3
    assert 'prestable' not in body


async def test_endpoints_list_filters(taxi_api_proxy, db_endpoints):
    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST,
        params=dict(cluster='api-proxy', dev_team_filter='looney.tunes'),
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body['endpoints']) == 1
    assert body['endpoints'][0]['path'] == '/bar'

    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST,
        params=dict(
            cluster='api-proxy', dev_team_filter='looney.tunes,acme.inc',
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body['endpoints']) == 2
    assert [ep_def['path'] for ep_def in body['endpoints']] == ['/bar', '/foo']

    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST, params=dict(cluster='api-proxy', search_filter='ba'),
    )
    assert response.status_code == 200
    body = response.json()
    # /bar, /bazooka matched by path, /foo matched by summary "bar"
    assert len(body['endpoints']) == 3
    assert [ep_def['path'] for ep_def in body['endpoints']] == [
        '/bar',
        '/bazooka',
        '/foo',
    ]

    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST, params=dict(cluster='api-proxy', search_filter='oo'),
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body['endpoints']) == 2
    assert [ep_def['path'] for ep_def in body['endpoints']] == [
        '/bazooka',
        '/foo',
    ]


async def test_endpoints_control_state(taxi_api_proxy, db_endpoints):
    response = await taxi_api_proxy.get(
        ENDPOINTS_CTRL_STATE, params=dict(cluster='api-proxy', id='/foo'),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['stable_meta']['revision'] == 8
    assert 'prestable' in body
    assert body['prestable']['meta']['revision'] == 9
    assert body['prestable']['percent'] == 5
    assert body['last_meta']['revision'] == 9

    response = await taxi_api_proxy.get(
        ENDPOINTS_CTRL_STATE, params=dict(cluster='api-proxy', id='/bar'),
    )
    assert response.status_code == 200
    body = response.json()
    assert body['stable_meta']['revision'] == 3
    assert 'prestable' not in body
