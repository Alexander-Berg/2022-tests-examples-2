from . import endpoints
from . import resources


# Resources


async def _put_resource(
        taxi_api_proxy,
        testpoint,
        resource_id,
        url,
        method,
        summary=None,
        dev_team=None,
        duty_group_id=None,
        duty_abc=None,
        tvm_name=None,
        qos_taxi_config=None,
        timeout=None,
        timeout_taxi_config=None,
        max_retries=None,
        max_retries_taxi_config=None,
        new_revision=0,
        last_revision=None,
        prestable=None,
        caching_enabled=False,
        rps_limit=None,
        use_envoy=False,
):
    resource = {
        'revision': new_revision,
        'url': url,
        'method': method,
        'summary': summary or 'foo bar summary',
        'dev_team': dev_team or 'foo',
        'duty_group_id': duty_group_id or 'foo-duty-group-id',
        'duty_abc': duty_abc or 'foo-abc',
        'caching-enabled': caching_enabled,
    }
    resource_optionals = {
        'tvm-name': tvm_name,
        'qos-taxi-config': qos_taxi_config,
        'timeout': timeout,
        'timeout-taxi-config': timeout_taxi_config,
        'max-retries': max_retries,
        'max-retries-taxi-config': max_retries_taxi_config,
        'rps-limit': rps_limit,
        'use_envoy': use_envoy,
    }
    resource.update(
        {k: v for k, v in resource_optionals.items() if v is not None},
    )

    params = {'id': resource_id}
    if prestable is not None:
        params.update(
            {'percent': prestable, 'stable_revision': last_revision or 0},
        )
    elif last_revision is not None:
        params.update({'last_revision': last_revision})

    is_prestable = prestable is not None
    await resources.put_resource(
        taxi_api_proxy,
        testpoint,
        params=params,
        json=resource,
        prestable=is_prestable,
    )

    # return

    if prestable:
        db_prestable = await resources.fetch_current_prestable(
            taxi_api_proxy, resource_id,
        )
        assert db_prestable
        db_resource = db_prestable['item']
        assert db_prestable['prestable_options']['percent'] == prestable
    else:
        db_resource = await resources.fetch_current_stable(
            taxi_api_proxy, resource_id,
        )

    loaded = db_resource and db_resource['revision'] == new_revision
    assert loaded, 'Failed to create resource "%s"' % resource_id
    assert db_resource == resource, '%s != %s' % (db_resource, resource)


async def create_resource(*args, **kwargs):
    await _put_resource(*args, **kwargs)


async def update_resource(taxi_api_proxy, testpoint, resource_id, **kwargs):
    current_resource = await resources.fetch_current_stable(
        taxi_api_proxy, resource_id,
    )
    revision = current_resource['revision']
    await _put_resource(
        taxi_api_proxy,
        testpoint,
        resource_id,
        new_revision=revision + 1,
        last_revision=revision,
        **kwargs,
    )


async def delete_resource(taxi_api_proxy, testpoint, resource_id):
    current = await resources.fetch_current_stable(taxi_api_proxy, resource_id)
    revision = current['revision']
    await resources.delete_resource(
        taxi_api_proxy,
        testpoint,
        params={'id': resource_id, 'revision': revision},
    )


async def finalize_resource_prestable(
        taxi_api_proxy,
        testpoint,
        resource_id,
        resolution,
        force_prestable_revision=None,
        force_recall=1,
):
    assert resolution in ['release', 'dismiss']

    current_resource = await resources.fetch_current_stable(
        taxi_api_proxy, resource_id,
    )
    last_revision = current_resource['revision']

    prestable_revision = (
        force_prestable_revision
        or (
            await resources.fetch_current_prestable(
                taxi_api_proxy, resource_id,
            )
        )['item']['revision']
    )

    if resolution == 'release':
        for call in range(force_recall):
            tp_data = await resources.release_prestable_resource(
                taxi_api_proxy,
                testpoint,
                params={
                    'id': resource_id,
                    'last_revision': last_revision,
                    'prestable_revision': prestable_revision,
                },
                no_check=call > 0,
            )
    else:
        for call in range(force_recall):
            tp_data = await resources.delete_prestable_resource(
                taxi_api_proxy,
                testpoint,
                params={
                    'id': resource_id,
                    'stable_revision': last_revision,
                    'prestable_revision': prestable_revision,
                },
                no_check=call > 0,
            )

    # ensure resource not in prestable anymore
    assert not [
        i
        for i in tp_data['state']['resources_prestable']
        if i['item']['id'] == resource_id
    ]
    # ensure stable revision advanced
    new_revision = (
        [i for i in tp_data['state']['resources'] if i['id'] == resource_id]
    )[0]['revision']
    # ensure revision changed as expected
    if resolution == 'release':
        assert new_revision > last_revision, '%s > %s' % (
            new_revision,
            last_revision,
        )
    else:
        assert new_revision == last_revision, '%s > %s' % (
            new_revision,
            last_revision,
        )


# Endpoints


async def _put_endpoint(
        taxi_api_proxy,
        testpoint,
        path,
        endpoint_id=None,
        dev_team=None,
        duty_group_id=None,
        duty_abc=None,
        put_handler=None,
        put_plain_handler=None,
        post_handler=None,
        post_plain_handler=None,
        get_handler=None,
        get_plain_handler=None,
        patch_handler=None,
        patch_plain_handler=None,
        delete_handler=None,
        delete_plain_handler=None,
        new_revision=0,
        last_revision=None,
        prestable=None,
        tests=None,
        check_draft=True,
        enabled=True,
):
    handlers = {
        key: value
        for key, value in [
            ('put', put_handler),
            ('put_plain', put_plain_handler),
            ('post', post_handler),
            ('post_plain', post_plain_handler),
            ('get', get_handler),
            ('get_plain', get_plain_handler),
            ('patch', patch_handler),
            ('patch_plain', patch_plain_handler),
            ('delete', delete_handler),
            ('delete_plain', delete_plain_handler),
        ]
        if value is not None
    }

    # TODO: handle it after frontend migration
    endpoint_id = endpoint_id or path
    params = {'path': path, 'id': endpoint_id}

    if prestable is not None:
        params.update(
            {'percent': prestable, 'stable_revision': last_revision or 0},
        )
    elif last_revision is not None:
        params.update({'last_revision': last_revision})

    json = {
        'revision': new_revision,
        'enabled': enabled,
        'summary': 'bar',
        'dev_team': dev_team or 'foo',
        'duty_group_id': duty_group_id or 'foo-duty-group-id',
        'duty_abc': duty_abc or 'foo-abc',
        'handlers': handlers,
    }
    if tests is not None:
        json['tests'] = [
            {'name': test['id'], 'test': str(test)} for test in tests
        ]

    _, tp_data = await endpoints.put_endpoint(
        taxi_api_proxy,
        testpoint,
        params=params,
        json=json,
        prestable=prestable is not None,
        check_draft=check_draft,
    )

    # wait until internal state reload
    if prestable:
        filtered = [
            i['item']
            for i in tp_data['state']['endpoints_prestable']
            if i['item']['id'] == endpoint_id
        ]
    else:
        filtered = [
            i for i in tp_data['state']['endpoints'] if i['id'] == endpoint_id
        ]
    loaded = filtered and filtered[0]['revision'] == new_revision
    assert loaded, f'Failed to create handler id="{endpoint_id}" path="{path}"'
    if prestable is not None:
        current_prestable = await endpoints.fetch_current_prestable(
            taxi_api_proxy, endpoint_id,
        )
        assert current_prestable
        assert current_prestable['prestable_options']['percent'] == prestable
        assert current_prestable['item']['revision'] == new_revision


async def create_endpoint(*args, **kwargs):
    await _put_endpoint(*args, **kwargs)


async def update_endpoint(
        taxi_api_proxy, testpoint, path, endpoint_id, **kwargs,
):
    current = await endpoints.fetch_current_stable(
        taxi_api_proxy, endpoint_id or path,
    )
    revision = current['revision']
    await _put_endpoint(
        taxi_api_proxy,
        testpoint,
        path,
        endpoint_id=endpoint_id,
        new_revision=revision + 1,
        last_revision=revision,
        **kwargs,
    )


async def delete_endpoint(taxi_api_proxy, testpoint, endpoint_id):
    current = await endpoints.fetch_current_stable(taxi_api_proxy, endpoint_id)
    revision = current['revision']
    await endpoints.delete_endpoint(
        taxi_api_proxy,
        testpoint,
        params={'id': endpoint_id, 'revision': revision},
    )


async def finalize_endpoint_prestable(
        taxi_api_proxy,
        testpoint,
        endpoint_id,
        resolution,
        force_prestable_revision=None,
        force_recall=1,
):
    assert resolution in ['release', 'dismiss']

    current_endpoint = await endpoints.fetch_current_stable(
        taxi_api_proxy, endpoint_id,
    )
    last_revision = current_endpoint['revision']

    prestable_revision = (
        force_prestable_revision
        or (
            await endpoints.fetch_current_prestable(
                taxi_api_proxy, endpoint_id,
            )
        )['item']['revision']
    )

    if resolution == 'release':
        for call in range(force_recall):
            tp_data = await endpoints.release_prestable_endpoint(
                taxi_api_proxy,
                testpoint,
                params={
                    'id': endpoint_id,
                    'last_revision': last_revision,
                    'prestable_revision': prestable_revision,
                },
                no_check=call > 0,
            )
    else:
        for call in range(force_recall):
            tp_data = await endpoints.delete_prestable_endpoint(
                taxi_api_proxy,
                testpoint,
                params={
                    'id': endpoint_id,
                    'stable_revision': last_revision,
                    'prestable_revision': prestable_revision,
                },
                no_check=call > 0,
            )

    # ensure endpoint not in prestable anymore
    assert not [
        i
        for i in tp_data['state']['endpoints_prestable']
        if i['item']['id'] == endpoint_id
    ]
    # ensure stable revision advanced
    new_revision = (
        [i for i in tp_data['state']['endpoints'] if i['id'] == endpoint_id]
    )[0]['revision']
    # ensure revision changed as expected
    if resolution == 'release':
        assert new_revision > last_revision, '%s > %s' % (
            new_revision,
            last_revision,
        )
    else:
        assert new_revision == last_revision, '%s > %s' % (
            new_revision,
            last_revision,
        )


async def _validate_endpoint(
        taxi_api_proxy,
        path,
        endpoint_id=None,
        dev_team=None,
        duty_group_id=None,
        duty_abc=None,
        put_handler=None,
        post_handler=None,
        get_handler=None,
        patch_handler=None,
        delete_handler=None,
        new_revision=0,
        tests=None,
):
    handlers = {
        key: value
        for key, value in [
            ('put', put_handler),
            ('post', post_handler),
            ('get', get_handler),
            ('patch', patch_handler),
            ('delete', delete_handler),
        ]
        if value is not None
    }
    params = {'path': path}
    if endpoint_id:
        params.update(id=endpoint_id)
    json = {
        'revision': new_revision,
        'enabled': True,
        'summary': 'bar',
        'dev_team': dev_team or 'foo',
        'duty_group_id': duty_group_id or 'foo-duty-group-id',
        'duty_abc': duty_abc or 'foo-abc',
        'handlers': handlers,
    }
    if tests is not None:
        json['tests'] = [
            {'name': test['id'], 'test': str(test)} for test in tests
        ]

    await endpoints.validate_endpoint(taxi_api_proxy, params=params, json=json)


async def validate_endpoint(*args, **kwargs):
    await _validate_endpoint(*args, **kwargs)
