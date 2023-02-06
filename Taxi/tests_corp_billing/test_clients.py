import random


async def test_idempotent_client_insertion(load_json, request_create_client):
    client = load_json('client_with_services_ya_taxi_team.json')
    revisions = []
    for dummy_i in range(3):
        response = await request_create_client(
            client['external_ref'], client['payment_method_name'],
        )
        assert response.status_code == 200
        revisions.append(response.json()['revision'])

    assert len(set(revisions)) == 1 and revisions[0] == 1


async def test_idempotent_client_update(load_json, add_client_with_services):
    client = load_json('client_with_services_ya_taxi_team.json')
    revisions = []
    for dummy_i in range(3):
        response = await add_client_with_services(client)
        revisions.append(response.json()['revision'])

    assert len(set(revisions)) == 1 and revisions[0] == 2


async def test_revision_increment_on_update(
        load_json, add_client_with_services,
):
    client = load_json('client_with_services_ya_taxi_team.json')
    revisions = []
    for dummy_i in range(5):
        _update_all_client_fields(client)
        response = await add_client_with_services(client)
        revisions.append(response.json()['revision'])

    assert len(revisions) == len(set(revisions))


async def test_update_unknown_client(load_json, request_update_client):
    client = load_json('client_with_services_ya_taxi_team.json')
    response = await request_update_client(client)
    assert response.status_code == 404


async def test_old_revision(
        load_json, add_client_with_services, request_update_client,
):
    client = load_json('client_with_services_ya_taxi_team.json')
    response = await add_client_with_services(client)
    client['revision'] = response.json()['revision'] - 1
    _update_all_client_fields(client)
    response = await request_update_client(client)
    assert response.status_code == 409


async def test_repeated_services(
        load_json, add_client_with_services, request_update_client,
):
    client = load_json('client_with_services_ya_taxi_team.json')
    response = await add_client_with_services(client)
    client['revision'] = response.json()['revision']
    client['services'].append(client['services'][0])
    response = await request_update_client(client)
    assert response.status_code == 400
    assert response.json()['code'] == 'SERVICES_REPEATED'


async def test_removed_services(
        load_json, add_client_with_services, request_update_client,
):
    client = load_json('client_with_services_ya_taxi_team.json')
    response = await add_client_with_services(client)
    client['revision'] = response.json()['revision']
    del client['services'][0]
    response = await request_update_client(client)
    assert response.status_code == 400
    assert response.json()['code'] == 'CANNOT_DISABLE_SERVICE'


def _update_all_client_fields(client):
    client['payment_method_name'] += ' new'
    client['all_services_suspended'] = not client['all_services_suspended']
    random.shuffle(client['services'])
    for item in client['services']:
        item['suspended'] = not item['suspended']


async def test_update_yandex_uid(
        load_json, add_client_with_services, request_update_client,
):
    client = load_json('client_with_services_ya_taxi_team.json')
    response = await add_client_with_services(client)
    assert response.status_code == 200
    client = response.json()
    assert client.get('yandex_uid') is None

    client['yandex_uid'] = '123'
    response = await request_update_client(client)
    assert response.status_code == 200
    client = response.json()
    assert client['yandex_uid'] == '123'

    client['yandex_uid'] = None
    response = await request_update_client(client)
    assert response.status_code == 200
    client = response.json()
    assert not client.get('yandex_uid')


async def _update_client(request_update_client, client, is_test):
    response = await request_update_client(client)
    assert response.status_code == 200
    client = response.json()
    eats_rus = next(
        item for item in client['services'] if item['type'] == 'eats/rus'
    )
    assert eats_rus['is_test'] == is_test
    return client


async def test_update_is_test(
        load_json, add_client_with_services, request_update_client,
):
    client = load_json('client_with_services_ya_taxi_team.json')
    response = await add_client_with_services(client)
    assert response.status_code == 200
    client = response.json()

    await _update_client(request_update_client, client, True)

    for service in client['services']:
        if service['type'] == 'eats/rus':
            assert service['is_test']
            service['is_test'] = not service['is_test']
            break
    await _update_client(request_update_client, client, False)
