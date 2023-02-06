import pytest


@pytest.mark.parametrize(
    'provider, status, expected_provider, exp_code',
    [
        (
            {
                'name': 'test_name',
                'tvm_id': 123,
                'hostname': 'http://hostname.ru',
            },
            200,
            {
                'id': 1,
                'name': 'test_name',
                'tvm_id': 123,
                'hostname': 'http://hostname.ru',
            },
            None,
        ),
        (
            {
                'name': 'test_name',
                'tvm_id': 123,
                'hostname': 'http://hostname.ru',
            },
            404,
            {'id': 2, 'name': '404', 'tvm_id': 404},
            'PROVIDER_NOT_FOUND',
        ),
    ],
)
async def test_providers_get(
        web_app_client,
        add_providers,
        provider,
        status,
        expected_provider,
        exp_code,
):
    await add_providers(
        provider['name'], provider['tvm_id'], provider['hostname'],
    )
    response = await web_app_client.get(
        '/v1/providers/', params={'id': expected_provider['id']},
    )
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content == expected_provider
    else:
        assert content['code'] == exp_code


async def test_providers_get_all(web_app_client, add_providers):
    await add_providers('provider1', 123, 'http://hostname.ru')
    await add_providers('provider2', 456, 'http://hostname.com')
    response = await web_app_client.post('/v1/providers/retrieve/')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'providers': [
            {'id': 1, 'name': 'provider1', 'tvm_id': 123},
            {'id': 2, 'name': 'provider2', 'tvm_id': 456},
        ],
    }


@pytest.mark.parametrize(
    'handle, provider_data, status, expected',
    [
        (
            '/v1/providers/create/',
            {'name': 'manager', 'hostname': 'http://test.yandex.net'},
            200,
            {
                'id': 2,
                'name': 'manager',
                'tvm_id': 123,
                'hostname': 'http://test.yandex.net',
            },
        ),
        (
            '/v1/providers/create/check/',
            {
                'name': 'first_manager',
                'tvm_name': 'manager',
                'hostname': 'http://test.yandex.net',
            },
            200,
            {
                'data': {
                    'name': 'first_manager',
                    'tvm_name': 'manager',
                    'hostname': 'http://test.yandex.net',
                },
            },
        ),
        (
            '/v1/providers/create/',
            {'name': 'tvm_no', 'hostname': 'http://test.yandex.net'},
            404,
            'CHECK_PROVIDER_ERROR',
        ),
        (
            '/v1/providers/create/check/',
            {'name': 'tvm_no', 'hostname': 'http://test.yandex.net'},
            404,
            'CHECK_PROVIDER_ERROR',
        ),
        (
            '/v1/providers/create/',
            {'name': 'already_exist', 'hostname': 'http://test.yandex.net'},
            409,
            'ALREADY_EXIST',
        ),
        (
            '/v1/providers/create/check/',
            {'name': 'already_exist', 'hostname': 'http://test.yandex.net'},
            409,
            'ALREADY_EXIST',
        ),
    ],
)
@pytest.mark.config(TVM_SERVICES={'manager': 123, 'already_exist': 409})
async def test_providers_create(
        web_app_client, add_providers, handle, provider_data, status, expected,
):
    await add_providers('already_exist', 409, 'taxi.yandex.net')
    response = await web_app_client.post(handle, json=provider_data)
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content == expected
    else:
        assert content['code'] == expected


@pytest.mark.parametrize(
    'provider_id, status, expected_code',
    [(1, 200, None), (2, 404, 'NOT_FOUND')],
)
async def test_delete_provider(
        web_app_client,
        add_providers,
        get_providers,
        provider_id,
        status,
        expected_code,
):
    await add_providers('trash', 666, '666.net')
    response = await web_app_client.post(
        '/v1/providers/delete/check/', json={'id': provider_id},
    )
    assert response.status == status
    if response.status == 200:
        content = await response.json()
        assert content == {'data': {'id': provider_id}}

        provider = await get_providers(provider_id)
        assert provider

    response = await web_app_client.post(
        '/v1/providers/delete/', json={'id': provider_id},
    )
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content == {'id': provider_id, 'name': 'trash', 'tvm_id': 666}
        provider = await get_providers(provider_id)
        assert not provider
    else:
        assert content['code'] == expected_code


@pytest.mark.parametrize(
    'provider_id, status, expected_cubes, name,cubes_names, limit',
    [
        (
            1,
            200,
            ['elrussoCube1'],
            'el',
            ['test1', 'TEST2', 'Test3', 'teSt4', 'tesT5', 'elrussoCube1'],
            2,
        ),
        (
            1,
            200,
            ['test1', 'TEST2', 'Test3', 'teSt4', 'tesT5', 'elrussoCube1'],
            '',
            ['test1', 'TEST2', 'Test3', 'teSt4', 'tesT5', 'elrussoCube1'],
            6,
        ),
        (
            1,
            200,
            ['test1'],
            '',
            ['test1', 'TEST2', 'Test3', 'teSt4', 'tesT5', 'elrussoCube1'],
            1,
        ),
        (2, 200, [], '', ['test1'], 4),
        (
            1,
            200,
            ['test1', 'TEST2', 'Test3', 'teSt4', 'tesT5'],
            'est',
            ['test1', 'TEST2', 'Test3', 'teSt4', 'tesT5', 'elrussoCube1'],
            5,
        ),
        (
            1,
            200,
            ['test1', 'TEST2', 'Test3', 'teSt4', 'tesT5'],
            'test',
            ['test1', 'TEST2', 'Test3', 'teSt4', 'tesT5', 'elrussoCube1'],
            0,
        ),
        (3, 404, 'NOT_FOUND', '', [], 1),
    ],
)
async def test_cubes_retrieve(
        web_app_client,
        add_providers,
        add_cube,
        provider_id,
        status,
        expected_cubes,
        name,
        cubes_names,
        limit,
):
    await add_providers('elrusso_provider', 1, '1.net')
    await add_providers('test_provider', 2, '2.net')

    for cube_name in cubes_names:
        await add_cube(
            name=cube_name,
            provider_id=1,
            needed_parameters=['need_test'],
            optional_parameters=['optional'],
            output_parameters=['output'],
        )

    response = await web_app_client.post(
        '/v1/cubes/retrieve/',
        json={'provider_id': provider_id, 'limit': limit, 'name': name},
    )
    assert response.status == status
    content = await response.json()
    if status == 200:
        assert response.status == 200
        cubes = content['cubes']
        _cubes_names = [cube['name'] for cube in cubes]
        assert _cubes_names == expected_cubes
