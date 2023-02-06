import pytest


@pytest.mark.parametrize('newer_than', [None, 4])
@pytest.mark.parametrize('older_than', [None, 8])
@pytest.mark.parametrize('order', ['asc', 'desc'])
async def test_admin_resources_revisions(
        taxi_api_proxy, resources, newer_than, older_than, order,
):
    resource_id = 'foo'
    samples = [
        {'url': 'http://url-%d' % i, 'method': 'post'} for i in range(10)
    ]

    # create resources
    await resources.safely_create_resource(resource_id, **(samples[0]))
    for i in samples[1:]:
        await resources.safely_update_resource(resource_id, **i)

    # add prestable to make sure it won't be returned
    await resources.safely_update_resource(
        resource_id, url='http://url-pre', method='post', prestable=10,
    )

    # fetch revisions
    params = {'id': resource_id, 'order': order}

    if newer_than is not None:
        params.update({'newer_than': newer_than})

    if older_than is not None:
        params.update({'older_than': older_than})

    response = await taxi_api_proxy.get(
        '/admin/v1/resources/revisions', params=params,
    )
    assert response.status_code == 200

    # check asserts
    values = [
        {'url': i['url'], 'method': i['method']}
        for i in response.json()['revisions']
    ]

    expectation = samples[newer_than + 1 if newer_than else None : older_than]
    if order == 'desc':
        expectation.reverse()

    assert values == expectation, '%s %s' % (values, expectation)
