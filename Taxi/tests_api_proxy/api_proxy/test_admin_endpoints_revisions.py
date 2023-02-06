import pytest


@pytest.mark.parametrize('newer_than', [None, 4])
@pytest.mark.parametrize('older_than', [None, 8])
@pytest.mark.parametrize('order', ['asc', 'desc'])
async def test_admin_endpoints_revisions(
        taxi_api_proxy, endpoints, newer_than, older_than, order,
):
    endpoint_path = '/foo'
    samples = [
        {
            'put_handler': {
                'enabled': True,
                'default-response': 'test-%d' % i,
                'responses': [
                    {'id': 'test-%d' % i, 'content-type': 'application/json'},
                ],
            },
        }
        for i in range(10)
    ]

    # create endpoints
    await endpoints.safely_create_endpoint(endpoint_path, **(samples[0]))
    for i in samples[1:]:
        await endpoints.safely_update_endpoint(endpoint_path, **i)

    # add prestable to make sure it won't be returned
    await endpoints.safely_update_endpoint(
        endpoint_path, put_handler=samples[0]['put_handler'], prestable=10,
    )

    # fetch revisions
    params = {'id': endpoint_path, 'path': endpoint_path, 'order': order}

    if newer_than is not None:
        params.update({'newer_than': newer_than})

    if older_than is not None:
        params.update({'older_than': older_than})

    response = await taxi_api_proxy.get(
        '/admin/v1/endpoints/revisions', params=params,
    )
    assert response.status_code == 200

    # check asserts
    values = [
        {'put_handler': i['handlers']['put']}
        for i in response.json()['revisions']
    ]

    expectation = samples[newer_than + 1 if newer_than else None : older_than]
    if order == 'desc':
        expectation.reverse()

    assert values == expectation, '%s %s' % (values, expectation)
