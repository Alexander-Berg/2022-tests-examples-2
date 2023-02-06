DEFAULT_NAMESPACE = None


async def get_consumers(
        taxi_exp_client, service=None, name=None, namespace=DEFAULT_NAMESPACE,
):
    params = {}
    if service is not None:
        params['service'] = service
    if name is not None:
        params['name'] = name
    if namespace is not None:
        params['tplatform_namespace'] = namespace

    response = await taxi_exp_client.get(
        '/v1/experiments/filters/consumers/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    result = await response.json()
    return result['consumers']


async def get_applications(taxi_exp_client):
    response = await taxi_exp_client.get(
        '/v1/experiments/filters/applications/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    return result['applications']


async def remove_consumer(taxi_exp_client, name):
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/consumers/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': name},
    )
    assert response.status == 200


async def add_consumer(
        taxi_exp_client, name, namespace=DEFAULT_NAMESPACE, service=None,
):
    params = {'name': name}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    if service is not None:
        params['service'] = service
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )
    return response


async def add_application(taxi_exp_client, name):
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/applications/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': name},
    )
    assert response.status == 200


async def remove_application(taxi_exp_client, name):
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/applications/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': name},
    )
    assert response.status == 200
