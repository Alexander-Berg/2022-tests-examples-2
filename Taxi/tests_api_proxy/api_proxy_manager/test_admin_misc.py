import pytest


_HELLO_WORLD_AGL = """
    default-response: main
    enabled: true
    allow-unauthorized: true
    responses:
      - id: main
        content-type: text/plain
        body: "Hello world!"
"""


async def test_find_enpoints_by_url_by_url_empty_db(taxi_api_proxy_manager):
    response = await taxi_api_proxy_manager.get(
        '/admin/v2/misc/find-endpoints-by-url-prefix',
        params={
            'path_prefix': '/4.0/eda-superapp/lavka/v1/',
            'tvm': 'foo-bar',
        },
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'non_api_proxy_cluster'


@pytest.mark.parametrize(
    'url,tvm,expected_error_code',
    [
        ('/bar', 'another-api-proxy', 'non_api_proxy_cluster'),
        ('/foo', 'another-api-proxy', 'non_api_proxy_cluster'),
        ('/bar', 'some-cluster', 'no_endpoints_matched'),
        ('/foo', 'some-cluster', None),
    ],
)
@pytest.mark.config(
    API_PROXY_ADMIN_EDIT_API={'endpoint_api_v': 2, 'resources_api_v': 1},
)
async def test_find_enpoints_by_url_bad_enpoint(
        taxi_api_proxy_manager, url, tvm, expected_error_code,
):
    response = await taxi_api_proxy_manager.put(
        '/admin/v2/endpoints/code',
        params={'cluster': 'some-cluster', 'id': 'foo', 'revision': 0},
        json={
            'last_state_signature': {},
            'data': {
                'git_commit_hash': '42',
                'path': '/foo',
                'summary': 'this is foo',
                'handlers': {'get_plain': _HELLO_WORLD_AGL},
                'dev_team': 'bar',
            },
            'dev_team': 'bar',
        },
    )
    assert response.status_code == 201
    await taxi_api_proxy_manager.invalidate_caches()

    response = await taxi_api_proxy_manager.get(
        '/admin/v2/misc/find-endpoints-by-url-prefix',
        params={'path_prefix': url, 'tvm': tvm},
    )

    if expected_error_code:
        assert response.status_code == 404
        assert response.json()['code'] == expected_error_code
    else:
        assert response.status_code == 200
        resp_item = response.json()['match'][0]
        assert resp_item['cluster'] == 'some-cluster'
        assert resp_item['id'] == 'foo'
        assert not resp_item['enabled']  # endpoint disabled by default
        assert resp_item['original-path'] == '/foo'
        assert not resp_item['prestable']


@pytest.mark.config(
    API_PROXY_ADMIN_EDIT_API={'endpoint_api_v': 2, 'resources_api_v': 1},
)
async def test_find_enpoints_by_url_disable(taxi_api_proxy_manager):
    response = await taxi_api_proxy_manager.put(
        '/admin/v2/endpoints/code',
        params={'cluster': 'some-cluster', 'id': 'foo', 'revision': 0},
        json={
            'last_state_signature': {},
            'data': {
                'git_commit_hash': '42',
                'path': '/foo',
                'summary': 'this is foo',
                'enabled': True,
                'handlers': {'get_plain': _HELLO_WORLD_AGL},
                'dev_team': 'bar',
            },
            'dev_team': 'bar',
        },
    )
    assert response.status_code == 201

    response = await taxi_api_proxy_manager.put(
        '/admin/v2/endpoints/code',
        params={'cluster': 'some-cluster', 'id': 'foo', 'revision': 1},
        json={
            'last_state_signature': {'stable_rev': 0},
            'data': {
                'git_commit_hash': '42',
                'path': '/foo',
                'summary': 'this is foo',
                'enabled': False,
                'handlers': {'get_plain': _HELLO_WORLD_AGL},
                'dev_team': 'bar',
            },
            'dev_team': 'bar',
        },
    )
    assert response.status_code == 201

    response = await taxi_api_proxy_manager.put(
        '/admin/v2/endpoints/control/prestable',
        params={
            'cluster': 'some-cluster',
            'id': 'foo',
            'revision': 1,
            'percent': 11,
        },
        json={
            'last_state_signature': {'stable_rev': 0},
            'data': {'code_revision': 1, 'enabled': True},
        },
    )
    assert response.status_code == 200

    await taxi_api_proxy_manager.invalidate_caches()

    response = await taxi_api_proxy_manager.get(
        '/admin/v2/misc/find-endpoints-by-url-prefix',
        params={'path_prefix': '/foo', 'tvm': 'some-cluster'},
    )
    assert response.status_code == 200
    assert response.json()['match'][0]['id'] == 'foo'
    assert not response.json()['match'][0]['enabled']


@pytest.mark.config(
    API_PROXY_ADMIN_EDIT_API={'endpoint_api_v': 2, 'resources_api_v': 1},
)
@pytest.mark.parametrize(
    'path_prefix,expected_ids',
    [
        ('/bar', None),
        ('/bar/buz', None),
        ('/foo', ['id0', 'id1', 'id2', 'id3']),
        ('/foo/', ['id0', 'id1', 'id2', 'id3']),
        ('/foo/a', ['id0', 'id1']),
        ('/foo/a/z', ['id0']),
        ('/foo/a/z/x/y', ['id0']),
        ('/foo/a/b', ['id0', 'id1']),
        ('/foo/a/b/c', ['id1', 'id0']),
        ('/foo/b', ['id2']),
        ('/foo/b/c/d', ['id2']),
        ('/foo/c', None),
    ],
)
async def test_find_enpoints_by_path_prefix(
        taxi_api_proxy_manager, path_prefix, expected_ids,
):
    test_handlers = {
        'id0': '/foo/a/(?<path>.*)',
        'id1': '/foo/a/b/(?<path>.*)',
        'id2': '/foo/b/(?<path>.*)',
        'id3': '/foo/',
    }

    for ep_id, ep_path in test_handlers.items():
        response = await taxi_api_proxy_manager.put(
            '/admin/v2/endpoints/code',
            params={'cluster': 'some-cluster', 'id': ep_id, 'revision': 0},
            json={
                'last_state_signature': {},
                'data': {
                    'git_commit_hash': '42',
                    'path': ep_path,
                    'summary': 'this is foo',
                    'enabled': True,
                    'handlers': {'get_plain': _HELLO_WORLD_AGL},
                    'dev_team': 'bar',
                },
                'dev_team': 'bar',
            },
        )
        assert response.status_code == 201
    await taxi_api_proxy_manager.invalidate_caches()

    response = await taxi_api_proxy_manager.get(
        '/admin/v2/misc/find-endpoints-by-url-prefix',
        params={'path_prefix': path_prefix, 'tvm': 'some-cluster'},
    )

    if expected_ids:
        assert response.status_code == 200
        assert {i['id'] for i in response.json()['match']} == set(expected_ids)
    else:
        assert response.status_code == 404
        assert response.json()['code'] == 'no_endpoints_matched'
