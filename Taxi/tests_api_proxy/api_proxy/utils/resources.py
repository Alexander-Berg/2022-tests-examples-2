import copy

URL_RESOURCES = '/admin/v1/resources'
URL_RESOURCES_PRESTABLE = '/admin/v1/resources/prestable'
URL_RESOURCES_DOWNGRADE = '/admin/v1/resources/downgrade'
URL_RESOURCES_RELEASE_PRESTABLE = '/admin/v1/resources/release-prestable'


class Failure(Exception):
    def __init__(self, response):
        super().__init__()
        self.response = response


async def fetch_current_stable(taxi_api_proxy, resource_id):
    response = await taxi_api_proxy.get(URL_RESOURCES)
    assert response.status_code == 200
    filtered = [
        i for i in response.json()['resources'] if i['id'] == resource_id
    ]
    current = filtered[0] if filtered else None
    if current:
        current.pop('id')
        current.pop('created')
    return current


async def fetch_current_prestable(taxi_api_proxy, resource_id):
    response = await taxi_api_proxy.get(URL_RESOURCES_PRESTABLE)
    assert response.status_code == 200
    filtered = [
        i
        for i in response.json()['resources']
        if i['item']['id'] == resource_id
    ]
    current = filtered[0] if filtered else None
    if current:
        current['item'].pop('id')
        current['item'].pop('created')
    return current


async def put_resource(
        taxi_api_proxy, testpoint, params, json, prestable=False,
):
    # fetch current state (always stable)
    current = await fetch_current_stable(taxi_api_proxy, params['id'])

    # check change
    url = URL_RESOURCES_PRESTABLE if prestable else URL_RESOURCES
    response = await taxi_api_proxy.put(
        url + '/check-draft', params=params, json=json,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json()['data'] == json
    assert response.json()['diff']['new'] == json
    if current is not None:
        assert response.json()['diff']['current'] == current
    else:
        assert 'current' not in response.json()['diff']

    # apply change
    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def tp_handler(data):
        pass

    response = await taxi_api_proxy.put(url, params=params, json=json)
    if response.status_code != (200 if current and not prestable else 201):
        raise Failure(response)
    assert response.json() == {'status': 'succeeded'}
    tp_data = (await tp_handler.wait_call())['data']
    return response, tp_data


async def delete_resource(taxi_api_proxy, testpoint, params):
    # fetch current state (always stable)
    current = await fetch_current_stable(taxi_api_proxy, params['id'])

    # check change
    response = await taxi_api_proxy.delete(
        URL_RESOURCES + '/check-draft',
        params=params,
        json={'dev_team': 'foo'},
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json()['data']['dev_team'] == 'foo'
    assert response.json()['diff']['current'] == current

    # apply change
    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def tp_handler(data):
        pass

    response = await taxi_api_proxy.delete(URL_RESOURCES, params=params)
    if response.status_code != 200:
        raise Failure(response)
    tp_data = (await tp_handler.wait_call())['data']
    return tp_data


async def downgrade_resource(
        taxi_api_proxy, testpoint, params, expected_new=None,
):
    # fetch current state (always stable)
    current = await fetch_current_stable(taxi_api_proxy, params['id'])

    # check change
    response = await taxi_api_proxy.post(
        URL_RESOURCES_DOWNGRADE + '/check-draft',
        params=params,
        json={'dev_team': 'foo'},
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json()['data'] == {'dev_team': 'foo'}
    diff = response.json()['diff']
    assert diff['current'] == current
    if expected_new:
        expected = copy.deepcopy(expected_new)
        expected['revision'] = current['revision'] + 1
        assert diff['new'] == expected

    # apply change
    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def tp_handler(data):
        pass

    response = await taxi_api_proxy.post(
        URL_RESOURCES_DOWNGRADE, params=params,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json() == {'status': 'succeeded'}
    await tp_handler.wait_call()
    return diff['new']


async def release_prestable_resource(
        taxi_api_proxy, testpoint, params, no_check=False,
):
    # check change
    if not no_check:
        # fetch current state
        stable = await fetch_current_stable(taxi_api_proxy, params['id'])
        prestable = (
            await fetch_current_prestable(taxi_api_proxy, params['id'])
        )['item']

        response = await taxi_api_proxy.post(
            URL_RESOURCES_RELEASE_PRESTABLE + '/check-draft',
            params=params,
            json={'dev_team': 'foo'},
        )
        if response.status_code != 200:
            raise Failure(response)
        assert response.json()['data'] == {'dev_team': 'foo'}
        assert response.json()['diff']['current'] == stable
        assert response.json()['diff']['new'] == prestable

    # apply change
    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def tp_handler(data):
        pass

    response = await taxi_api_proxy.post(
        URL_RESOURCES_RELEASE_PRESTABLE, params=params,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json() == {'status': 'succeeded'}
    tp_data = (await tp_handler.wait_call())['data']
    return tp_data


async def delete_prestable_resource(
        taxi_api_proxy, testpoint, params, no_check=False,
):
    # check change
    if not no_check:
        # fetch current state
        stable = await fetch_current_stable(taxi_api_proxy, params['id'])
        prestable = (
            await fetch_current_prestable(taxi_api_proxy, params['id'])
        )['item']

        response = await taxi_api_proxy.delete(
            URL_RESOURCES_PRESTABLE + '/check-draft',
            params=params,
            json={'dev_team': 'foo'},
        )
        if response.status_code != 200:
            raise Failure(response)
        assert response.json()['data'] == {'dev_team': 'foo'}
        assert response.json()['diff']['current'] == prestable
        assert response.json()['diff']['new'] == stable

    # apply change
    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def tp_handler(data):
        pass

    response = await taxi_api_proxy.delete(
        URL_RESOURCES_PRESTABLE, params=params,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json() == {'status': 'succeeded'}
    tp_data = (await tp_handler.wait_call())['data']
    return tp_data
