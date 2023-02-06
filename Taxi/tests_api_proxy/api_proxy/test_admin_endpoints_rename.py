import pytest

from tests_api_proxy.api_proxy.utils import endpoints as utils_endpoints

ENDPOINTS_LIST = 'admin/v2/endpoints/list'
ENDPOINTS_REVS = 'admin/v2/endpoints/revisions'


async def test_change_endpoint_path(taxi_api_proxy, endpoints, load_yaml):
    async def assert_ok(path):
        response = await taxi_api_proxy.post(path, json={'code': 200})
        assert response.status_code == 200
        assert response.json() == {'result': 'Ok'}

    async def assert_404(path):
        response = await taxi_api_proxy.post(path, json={'code': 200})
        assert response.status_code == 404

    async def check_ep_list(ep_revs):
        resp = await taxi_api_proxy.get(
            ENDPOINTS_LIST, params={'cluster': 'api-proxy'},
        )
        assert resp.status_code == 200
        db_eps = resp.json()['endpoints']
        db_ids = [db_ep['id'] for db_ep in db_eps]
        assert db_ids == list(ep_revs.keys())

        for ep_id, revisions in ep_revs.items():
            resp = await taxi_api_proxy.get(
                ENDPOINTS_REVS,
                params={'cluster': 'api-proxy', 'id': ep_id, 'order': 'asc'},
            )
            assert resp.status_code == 200
            db_eps = resp.json()['revisions']

            db_ids = [db_ep['id'] for db_ep in db_eps]
            db_meta_revs = [
                {'path': db_ep['path'], 'revision': db_ep['revision']}
                for db_ep in db_eps
            ]

            assert len(set(db_ids)) == 1, db_ids
            assert db_meta_revs == revisions

    handler_def = load_yaml('simple_post_handler.yaml')
    endpoint_id = 'X Æ A-12'
    init_path = '/endpoint'
    new_path = '/brand_new_endpoint'
    one_more_path = '/yet_another_path'

    revs = []

    # create endpoint
    await endpoints.safely_create_endpoint(
        endpoint_id=endpoint_id, path=init_path, post_handler=handler_def,
    )
    revs.append({'revision': 0, 'path': init_path})
    await check_ep_list({endpoint_id: revs})
    await assert_ok(init_path)

    # enabled endpoints can't be renamed
    with pytest.raises(utils_endpoints.Failure) as err:
        await endpoints.safely_update_endpoint(
            endpoint_id=endpoint_id, path=new_path, post_handler=handler_def,
        )
    assert err.value.response.json() == {
        'code': 'path_change_for_enabled_endpoint',
        'message': 'Forbidden to change path for enabled endpoint',
    }
    await check_ep_list({endpoint_id: revs})

    # turning off first, then rename
    await endpoints.safely_update_endpoint(
        endpoint_id=endpoint_id,
        path=init_path,
        enabled=False,
        post_handler=handler_def,
    )
    revs.append({'revision': 1, 'path': init_path})
    await check_ep_list({endpoint_id: revs})
    await assert_404(init_path)

    await endpoints.safely_update_endpoint(
        endpoint_id=endpoint_id,
        path=new_path,
        enabled=True,
        post_handler=handler_def,
    )
    revs.append({'revision': 2, 'path': new_path})
    await check_ep_list({endpoint_id: revs})
    await assert_ok(new_path)
    await assert_404(init_path)

    # off, then try prestable when renaming
    await endpoints.safely_update_endpoint(
        endpoint_id=endpoint_id,
        path=new_path,
        enabled=False,
        post_handler=handler_def,
    )
    revs.append({'revision': 3, 'path': new_path})
    await check_ep_list({endpoint_id: revs})
    await assert_404(new_path)

    with pytest.raises(utils_endpoints.Failure) as err:
        await endpoints.safely_update_endpoint(
            endpoint_id=endpoint_id,
            path=one_more_path,
            prestable=15,
            post_handler=handler_def,
        )
    assert err.value.response.json() == {
        'code': 'path_change_on_prestable',
        'message': 'Forbidden to change path when creating endpoint prestable',
    }
    await check_ep_list({endpoint_id: revs})


async def test_change_endpoint_path_collision(
        taxi_api_proxy, endpoints, load_yaml,
):
    handler_def = load_yaml('simple_post_handler.yaml')
    fst_id = 'X Æ A-13'
    snd_id = 'X Æ A-14'
    path_tesla = '/tesla'
    path_spacex = '/spacex'

    # create endpoints
    await endpoints.safely_create_endpoint(
        endpoint_id=fst_id, path=path_tesla, post_handler=handler_def,
    )
    await endpoints.safely_create_endpoint(
        endpoint_id=snd_id, path=path_spacex, post_handler=handler_def,
    )

    # off, then try to rename tesla to spacex
    await endpoints.safely_update_endpoint(
        endpoint_id=fst_id,
        path=path_tesla,
        enabled=False,
        post_handler=handler_def,
    )

    with pytest.raises(utils_endpoints.Failure) as err:
        await endpoints.safely_update_endpoint(
            endpoint_id=fst_id,
            path=path_spacex,
            enabled=True,
            post_handler=handler_def,
        )
    assert err.value.response.json() == {
        'code': 'path_change_to_existing_url',
        'message': 'Collision during path change: target path already exists',
    }
