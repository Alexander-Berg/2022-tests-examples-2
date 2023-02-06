import copy
import pprint

URL_ENDPOINTS = '/admin/v1/endpoints'
URL_ENDPOINTS_PRESTABLE = '/admin/v1/endpoints/prestable'
URL_ENDPOINTS_DOWNGRADE = '/admin/v1/endpoints/downgrade'
URL_ENDPOINTS_RELEASE_PRESTABLE = '/admin/v1/endpoints/release-prestable'
URL_ENDPOINTS_VALIDATE = '/admin/v1/endpoints/validate'


class Failure(Exception):
    def __init__(self, response):
        super().__init__()
        self.response = response


HANDLERS = 'handlers'
PLAIN_SUFFIX = '_plain'


def remove_plain_yaml_handlers(endpoint):
    for method in ['get', 'post', 'put', 'patch', 'delete']:
        endpoint[HANDLERS].pop(f'{method}{PLAIN_SUFFIX}', None)


def assert_eq_endpoints(left, right):
    # TODO: should be just left == right
    # when no plain handlers will be available (frontend)
    left_handlers = left.pop(HANDLERS)
    right_handlers = right.pop(HANDLERS)
    assert left == right
    left_js_handlers = {
        key: value
        for key, value in left_handlers.items()
        if not key.endswith(PLAIN_SUFFIX)
    }
    right_js_handlers = {
        key: value
        for key, value in right_handlers.items()
        if not key.endswith(PLAIN_SUFFIX)
    }
    assert left_js_handlers == right_js_handlers
    left[HANDLERS] = left_handlers
    right[HANDLERS] = right_handlers


async def fetch_current_stable(taxi_api_proxy, endpoint_id):
    response = await taxi_api_proxy.get(URL_ENDPOINTS)
    assert response.status_code == 200
    filtered = [
        i for i in response.json()['endpoints'] if i['id'] == endpoint_id
    ]
    current = filtered[0] if filtered else None
    if current:
        current.pop('id')
        # current.pop('path')
        current.pop('created')
        current.pop('cluster')
    return current


async def fetch_current_prestable(taxi_api_proxy, endpoint_id):
    response = await taxi_api_proxy.get(URL_ENDPOINTS_PRESTABLE)
    assert response.status_code == 200
    filtered = [
        i
        for i in response.json()['endpoints']
        if i['item']['id'] == endpoint_id
    ]
    current = filtered[0] if filtered else None
    if current:
        current['item'].pop('id')
        # current['item'].pop('path')
        current['item'].pop('created')
        current['item'].pop('cluster')
    return current


async def put_check_draft(taxi_api_proxy, params, json, current, url):
    response = await taxi_api_proxy.put(
        url + '/check-draft', params=params, json=json,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json()['data'] == json, '%s / %s' % (
        pprint.pformat(response.json()['data']),
        pprint.pformat(json),
    )
    # TODO: deprecate path param
    if 'path' in params:
        json['path'] = params['path']
    assert response.json()['diff']['new'] == json
    if current is not None:
        assert response.json()['diff']['current'] == current
    else:
        assert 'current' not in response.json()['diff']


async def put_endpoint(
        taxi_api_proxy,
        testpoint,
        params,
        json,
        prestable=False,
        check_draft=True,
):
    # fetch current state (always stable)
    current = await fetch_current_stable(taxi_api_proxy, params['id'])

    # check change
    url = URL_ENDPOINTS_PRESTABLE if prestable else URL_ENDPOINTS
    if check_draft:
        await put_check_draft(taxi_api_proxy, params, json, current, url)

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


async def delete_endpoint(taxi_api_proxy, testpoint, params):
    # fetch current state (always stable)
    current = await fetch_current_stable(taxi_api_proxy, params['id'])

    # check change
    response = await taxi_api_proxy.delete(
        URL_ENDPOINTS + '/check-draft',
        params=params,
        json={'dev_team': 'foo'},
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json()['data'] == {'dev_team': 'foo'}
    assert response.json()['diff']['current'] == current

    # apply change
    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def tp_handler(data):
        pass

    response = await taxi_api_proxy.delete(URL_ENDPOINTS, params=params)
    if response.status_code != 200:
        raise Failure(response)
    tp_data = (await tp_handler.wait_call())['data']
    return tp_data


async def downgrade_endpoint(
        taxi_api_proxy, testpoint, params, expected_new=None,
):
    # fetch current state (always stable)
    current = await fetch_current_stable(taxi_api_proxy, params['id'])

    # check change
    response = await taxi_api_proxy.post(
        URL_ENDPOINTS_DOWNGRADE + '/check-draft',
        params=params,
        json={'dev_team': 'foo'},
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json()['data'] == {'dev_team': 'foo'}
    diff = response.json()['diff']
    assert_eq_endpoints(diff['current'], current)
    if expected_new:
        expected = copy.deepcopy(expected_new)
        expected['revision'] = current['revision'] + 1
        assert_eq_endpoints(diff['new'], expected)

    # apply change
    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def tp_handler(data):
        pass

    response = await taxi_api_proxy.post(
        URL_ENDPOINTS_DOWNGRADE, params=params,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json() == {'status': 'succeeded'}
    await tp_handler.wait_call()
    return diff['new']


async def release_prestable_endpoint(
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
            URL_ENDPOINTS_RELEASE_PRESTABLE + '/check-draft',
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
        URL_ENDPOINTS_RELEASE_PRESTABLE, params=params,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json() == {'status': 'succeeded'}
    tp_data = (await tp_handler.wait_call())['data']
    return tp_data


async def delete_prestable_endpoint(
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
            URL_ENDPOINTS_PRESTABLE + '/check-draft',
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
        URL_ENDPOINTS_PRESTABLE, params=params,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json() == {'status': 'succeeded'}
    tp_data = (await tp_handler.wait_call())['data']
    return tp_data


async def validate_endpoint(taxi_api_proxy, params, json):
    response = await taxi_api_proxy.post(
        URL_ENDPOINTS_VALIDATE, params=params, json=json,
    )
    if response.status_code != 200:
        raise Failure(response)
    assert response.json() == {}
