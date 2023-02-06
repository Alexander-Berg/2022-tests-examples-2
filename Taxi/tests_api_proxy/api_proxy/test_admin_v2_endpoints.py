import random
import string

import pytest

from tests_api_proxy.api_proxy.utils import endpoints as utils_endpoints

ENDPOINTS_LIST = 'admin/v2/endpoints/list'

ENDPOINT_STATE = 'admin/v2/endpoints/control/state'
ENDPOINT_INFO = 'admin/v2/endpoints/info'
ENDPOINT_REVISIONS = 'admin/v2/endpoints/revisions'

ENDPOINT_CODE = 'admin/v2/endpoints/code'
ENDPOINT_CTRL_STABLE = 'admin/v2/endpoints/control/stable'
ENDPOINT_CTRL_PRESTABLE = 'admin/v2/endpoints/control/prestable'
ENDPOINT_CTRL_PRESTABLE_RELEASE = (
    'admin/v2/endpoints/control/release-prestable'
)

ENDPOINT_CLUSTERS = 'admin/v2/clusters/list'

API_PROXY_ADMIN_EDIT_API_V2 = {'endpoint_api_v': 2, 'resources_api_v': 1}

META_FIELDS = [
    'cluster',
    'id',
    'path',
    'summary',
    'dev_team',
    'enabled',
    'revision',
    'created',
    'git_commit_hash',
]


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
        'enabled': random.choice([True, False]),
    }


def _make_code(path, git_commit_hash):
    return {
        'path': path,
        'git_commit_hash': git_commit_hash,
        'summary': 'Some test endpoint',
        'dev_team': 'joe',
        'handlers': {
            'get': _make_handler(),
            'post': _make_handler(),
            'put': _make_handler(),
            'patch': _make_handler(),
            'delete': _make_handler(),
        },
    }


def _make_meta(ep_id, revision, code, control, cluster='api-proxy'):
    meta = {'cluster': cluster, 'id': ep_id, 'revision': revision}
    meta.update(code)
    meta.update(control)
    meta = {k: v for k, v in meta.items() if k in META_FIELDS}
    return meta


def _make_request_body(data=None, stable_rev=None):
    request = {'last_state_signature': {}}
    if data is not None:
        request.update(data=data)
    if stable_rev is not None:
        request['last_state_signature'].update(stable_rev=stable_rev)
    return request


async def _init_endpoint(taxi_api_proxy, ep_id, path):
    code_v0 = _make_code(path, '0xdeadbeef')
    control_v0 = {'enabled': False}  # initial control
    meta_v0 = _make_meta(ep_id, 0, code=code_v0, control=control_v0)

    # create initial code / state
    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 0},
        json=_make_request_body(data=code_v0),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    response = await taxi_api_proxy.get(
        ENDPOINT_INFO,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 0},
    )
    assert response.status_code == 200
    meta_v0.update(created=response.json()['created'])

    return code_v0, control_v0, meta_v0


@pytest.mark.config(API_PROXY_ADMIN_EDIT_API=API_PROXY_ADMIN_EDIT_API_V2)
async def test_admin_v2_endpoints_init_revision(taxi_api_proxy):
    ep_id = 'foo-bar'
    path = '/example/foo/bar'
    code_v0 = _make_code(path, '0xdeadbeef')
    control_v0 = {'enabled': False}  # default on initial creation
    meta_v0 = _make_meta(ep_id, 0, code=code_v0, control=control_v0)

    # create initial code / state
    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 0},
        json=_make_request_body(data=code_v0),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    # read the docs
    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST, params={'cluster': 'api-proxy'},
    )
    assert response.status_code == 200
    body = response.json()
    assert [doc['id'] for doc in body['endpoints']] == [ep_id]

    # check meta (stable, pretable, last)
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    meta_v0.update(created=body['stable_meta']['created'])
    assert body == {'stable_meta': meta_v0, 'last_meta': meta_v0}
    assert not body['stable_meta']['enabled']

    # check source
    response = await taxi_api_proxy.get(
        ENDPOINT_INFO,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 0},
    )
    assert response.status_code == 200
    body = response.json()
    utils_endpoints.remove_plain_yaml_handlers(body)
    ep_v0 = {
        'cluster': 'api-proxy',
        'id': ep_id,
        'revision': 0,
        'enabled': False,
        'created': body['created'],
    }
    ep_v0.update(code_v0)
    assert body == ep_v0

    # delete it
    response = await taxi_api_proxy.delete(
        ENDPOINT_CTRL_STABLE,
        params={'cluster': 'api-proxy', 'id': ep_id},
        json=_make_request_body(data=None, stable_rev=0),
    )
    assert response.status_code == 200

    # check that endpoint is deleted
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 404

    response = await taxi_api_proxy.get(
        ENDPOINTS_LIST, params={'cluster': 'api-proxy'},
    )
    assert response.status_code == 200
    assert response.json() == {'endpoints': []}


@pytest.mark.config(API_PROXY_ADMIN_EDIT_API=API_PROXY_ADMIN_EDIT_API_V2)
async def test_admin_v2_endpoints_git_flood(taxi_api_proxy):
    ep_id = 'foo-bar'
    path = '/example/foo/bar'
    _, control_v0, meta_v0 = await _init_endpoint(taxi_api_proxy, ep_id, path)

    # create release candidate (from git)
    code_v1 = _make_code(path, '0xalivebeaf')
    meta_v1_rc = _make_meta(ep_id, 1, code_v1, control_v0)
    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=code_v1, stable_rev=0),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    # retry the action (e.g. network timeout)
    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=code_v1, stable_rev=0),
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'succeeded'}

    # try to create one more release candidate (from git)
    code_v2 = _make_code(path, '0xresurrectedbeaf')
    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=code_v2, stable_rev=0),
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'release_candidate_already_exist'

    response = await taxi_api_proxy.get(
        ENDPOINT_REVISIONS, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    meta_v1_rc['created'] = body['revisions'][1]['created']
    assert body == {'revisions': [meta_v0, meta_v1_rc]}


@pytest.mark.config(API_PROXY_ADMIN_EDIT_API=API_PROXY_ADMIN_EDIT_API_V2)
async def test_admin_v2_endpoints_rc_dismiss(taxi_api_proxy):
    ep_id = 'foo-bar'
    path = '/example/foo/bar'
    _, control_v0, meta_v0 = await _init_endpoint(taxi_api_proxy, ep_id, path)

    # try to dismiss when there are no RC version
    response = await taxi_api_proxy.delete(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 0},
        json=_make_request_body(data=None, stable_rev=0),
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'release_candidate_not_found'

    # create release candidate (from git)
    code_v1 = _make_code(path, '0xalivebeaf')
    meta_v1_rc = _make_meta(ep_id, 1, code_v1, control_v0)

    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=code_v1, stable_rev=0),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    # check RC is available
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    meta_v1_rc.update(created=body['last_meta']['created'])
    assert body == {
        'stable_meta': meta_v0,
        'rc_meta': meta_v1_rc,
        'last_meta': meta_v1_rc,
    }
    assert body['stable_meta']['revision'] == 0
    assert body['last_meta']['revision'] == 1

    # try to dismiss wrong revision (not RC)
    response = await taxi_api_proxy.delete(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 0},
        json=_make_request_body(data=None, stable_rev=0),
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'race_condition'

    # dismiss RC
    response = await taxi_api_proxy.delete(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=None, stable_rev=0),
    )
    assert response.status_code == 200

    # check RC is dismissed
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body == {'stable_meta': meta_v0, 'last_meta': meta_v0}


@pytest.mark.config(API_PROXY_ADMIN_EDIT_API=API_PROXY_ADMIN_EDIT_API_V2)
async def test_admin_v2_endpoints_rc_stable(taxi_api_proxy):
    ep_id = 'foo-bar'
    path = '/example/foo/bar'
    _, control_v0, meta_v0 = await _init_endpoint(taxi_api_proxy, ep_id, path)

    # create release candidate (from git)
    code_v1 = _make_code(path, '0xalivebeaf')
    meta_v1_rc = _make_meta(ep_id, 1, code_v1, control_v0)

    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=code_v1, stable_rev=0),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    # check RC is available
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    meta_v1_rc.update(created=body['last_meta']['created'])
    assert body == {
        'stable_meta': meta_v0,
        'rc_meta': meta_v1_rc,
        'last_meta': meta_v1_rc,
    }

    # try to stabilize wrong RC
    control_v1_wrong = {
        'code_revision': 1,
        'git_commit_hash': '0xunknown',
        'enabled': True,
    }
    response = await taxi_api_proxy.put(
        ENDPOINT_CTRL_STABLE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=control_v1_wrong, stable_rev=0),
    )
    assert response.status_code == 409

    # stabilize RC
    control_v1 = {
        'code_revision': 1,
        'git_commit_hash': '0xalivebeaf',
        'enabled': True,
    }
    meta_v1 = _make_meta(ep_id, 1, code_v1, control_v1)
    response = await taxi_api_proxy.put(
        ENDPOINT_CTRL_STABLE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=control_v1, stable_rev=0),
    )
    assert response.status_code == 200

    # check RC is stabilized
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    meta_v1.update(created=body['stable_meta']['created'])
    assert body == {'stable_meta': meta_v1, 'last_meta': meta_v1}


@pytest.mark.config(API_PROXY_ADMIN_EDIT_API=API_PROXY_ADMIN_EDIT_API_V2)
async def test_admin_v2_endpoints_rc_prestable(taxi_api_proxy):
    ep_id = 'foo-bar'
    path = '/example/foo/bar'
    _, _, meta_v0 = await _init_endpoint(taxi_api_proxy, ep_id, path)

    # create release candidate
    code_v1 = _make_code(path, '0xalivebeaf')

    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=code_v1, stable_rev=0),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    # turn RC endpoint on via prestable
    control_v1 = {
        'code_revision': 1,
        'git_commit_hash': '0xalivebeaf',
        'enabled': True,
    }
    meta_v1 = _make_meta(ep_id, 1, code_v1, control_v1)

    response = await taxi_api_proxy.put(
        ENDPOINT_CTRL_PRESTABLE,
        params={
            'cluster': 'api-proxy',
            'id': ep_id,
            'revision': 1,
            'percent': 30,
        },
        json=_make_request_body(data=control_v1, stable_rev=0),
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'succeeded'}

    # check meta
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    meta_v1.update(created=body['prestable']['meta']['created'])
    assert body == {
        'stable_meta': meta_v0,
        'prestable': {'meta': meta_v1, 'percent': 30},
        'last_meta': meta_v1,
    }

    # release prestable
    response = await taxi_api_proxy.put(
        ENDPOINT_CTRL_PRESTABLE_RELEASE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=None, stable_rev=0),
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'succeeded'}

    # check meta
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body == {'stable_meta': meta_v1, 'last_meta': meta_v1}


@pytest.mark.config(API_PROXY_ADMIN_EDIT_API=API_PROXY_ADMIN_EDIT_API_V2)
async def test_admin_v2_endpoints_prestable_dismiss(taxi_api_proxy):
    ep_id = 'foo-bar'
    path = '/example/foo/bar'
    code_v0, _, meta_v0 = await _init_endpoint(taxi_api_proxy, ep_id, path)

    # change control on prestable
    control_v1 = {
        'code_revision': 0,
        'git_commit_hash': '0xdeadbeef',
        'enabled': True,
    }
    meta_v1 = _make_meta(ep_id, 1, code_v0, control_v1)

    response = await taxi_api_proxy.put(
        ENDPOINT_CTRL_PRESTABLE,
        params={
            'cluster': 'api-proxy',
            'id': ep_id,
            'revision': 1,
            'percent': 30,
        },
        json=_make_request_body(data=control_v1, stable_rev=0),
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'succeeded'}

    # check meta
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    meta_v1.update(created=body['prestable']['meta']['created'])
    assert body == {
        'stable_meta': meta_v0,
        'prestable': {'meta': meta_v1, 'percent': 30},
        'last_meta': meta_v1,
    }

    # dismiss prestable
    response = await taxi_api_proxy.delete(
        ENDPOINT_CTRL_PRESTABLE,
        params={'cluster': 'api-proxy', 'id': ep_id, 'revision': 1},
        json=_make_request_body(data=None, stable_rev=0),
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'succeeded'}

    # check meta
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': 'api-proxy', 'id': ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body == {'stable_meta': meta_v0, 'last_meta': meta_v0}


@pytest.mark.config(
    API_PROXY_ADMIN_EDIT_API=API_PROXY_ADMIN_EDIT_API_V2,
    API_PROXY_CLUSTER_ALIASES={
        'api-proxy-critical': {'display_name': 'taxi-critical'},
    },
)
async def test_admin_v2_clusters(taxi_api_proxy):
    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy', 'id': 'foo', 'revision': 0},
        json=_make_request_body(data=_make_code('/foo', '0xdeadbeef')),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'api-proxy-critical', 'id': 'foo', 'revision': 0},
        json=_make_request_body(
            data=_make_code('/critical/foo', '0xprimebeef'),
        ),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': 'common-api-proxy', 'id': 'foo', 'revision': 0},
        json=_make_request_body(data=_make_code('/foo', '0xrefbeef')),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    response = await taxi_api_proxy.get(ENDPOINT_CLUSTERS)
    assert response.status_code == 200
    assert response.json() == {
        'clusters': [
            {'id': 'api-proxy', 'display_name': 'api-proxy'},
            {'id': 'api-proxy-critical', 'display_name': 'taxi-critical'},
            {'id': 'common-api-proxy', 'display_name': 'common-api-proxy'},
        ],
    }


@pytest.mark.config(API_PROXY_ADMIN_EDIT_API=API_PROXY_ADMIN_EDIT_API_V2)
@pytest.mark.parametrize('cluster', ['api-proxy', 'api-proxy-critical'])
async def test_admin_v2_endpoints_crud_no_cluster_on_front(
        taxi_api_proxy, cluster,
):
    ep_id = 'foo-bar'
    old_front_ep_id = f'{cluster}::{ep_id}'
    path = '/example/foo/bar'
    code_v0 = _make_code(path, '0xdeadbeef')
    control_v0 = {'enabled': False}  # default on initial creation
    meta_v0 = _make_meta(
        old_front_ep_id, 0, code=code_v0, control=control_v0, cluster=cluster,
    )

    # create initial code / state
    response = await taxi_api_proxy.put(
        ENDPOINT_CODE,
        params={'cluster': cluster, 'id': ep_id, 'revision': 0},
        json=_make_request_body(data=code_v0),
    )
    assert response.status_code == 201
    assert response.json() == {'status': 'succeeded'}

    # read the docs
    response = await taxi_api_proxy.get(ENDPOINTS_LIST)
    assert response.status_code == 200
    body = response.json()
    assert [doc['id'] for doc in body['endpoints']] == [old_front_ep_id]

    # check meta (stable, pretable, last)
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'id': old_front_ep_id},
    )
    assert response.status_code == 200
    body = response.json()
    meta_v0.update(created=body['stable_meta']['created'])
    assert body == {'stable_meta': meta_v0, 'last_meta': meta_v0}
    assert not body['stable_meta']['enabled']

    # check source
    response = await taxi_api_proxy.get(
        ENDPOINT_INFO, params={'id': old_front_ep_id, 'revision': 0},
    )
    assert response.status_code == 200
    body = response.json()
    utils_endpoints.remove_plain_yaml_handlers(body)
    ep_v0 = {
        'cluster': cluster,
        'id': old_front_ep_id,
        'revision': 0,
        'enabled': False,
        'created': body['created'],
    }
    ep_v0.update(code_v0)
    assert body == ep_v0

    # delete it
    response = await taxi_api_proxy.delete(
        ENDPOINT_CTRL_STABLE,
        params={'id': old_front_ep_id},
        json=_make_request_body(data=None, stable_rev=0),
    )
    assert response.status_code == 200

    # check that endpoint is deleted
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'id': old_front_ep_id},
    )
    assert response.status_code == 404
    response = await taxi_api_proxy.get(
        ENDPOINT_STATE, params={'cluster': cluster, 'id': ep_id},
    )
    assert response.status_code == 404
    response = await taxi_api_proxy.get(ENDPOINTS_LIST, params={})
    assert response.status_code == 200
    assert response.json() == {'endpoints': []}
