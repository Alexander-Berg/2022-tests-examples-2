import pytest


class AnyInt(int):
    def __eq__(self, other):
        return isinstance(other, int)


def _recipe(
        name,
        *stages,
        provider_id=1,
        provider_name=None,
        job_vars=None,
        with_id=False,
):
    result = {
        'name': name,
        'provider_id': provider_id,
        'job_vars': job_vars or [],
        'stages': [*stages],
    }
    if with_id:
        result['id'] = AnyInt()
    if provider_name:
        result['provider_name'] = provider_name
    return result


def _stage(name, input_mapping=None, output_mapping=None, provider_name=None):
    result = {'name': name}
    if input_mapping is not None:
        result['input'] = input_mapping
    if output_mapping is not None:
        result['output'] = output_mapping
    if provider_name:
        result['provider_name'] = provider_name
    return result


@pytest.mark.parametrize(
    'data, status, expected_recipe, exp_code',
    [
        (
            {
                'provider_id': 2,
                'name': 'already_exist_recipe',
                'provider_name': 'deoevgen',
            },
            200,
            {
                'id': 2,
                'job_vars': [],
                'name': 'already_exist_recipe',
                'provider_id': 2,
                'provider_name': 'deoevgen',
                'stages': [
                    {
                        'input': {},
                        'name': 'testCube',
                        'output': {},
                        'provider_name': 'deoevgen',
                    },
                ],
            },
            None,
        ),
        (
            {'provider_id': 2, 'name': 'not_exist'},
            404,
            None,
            'RECIPE_NOT_FOUND',
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_add_cubes.sql'])
@pytest.mark.config(TASK_PROCESSOR_ENABLED=False)
async def test_recipes_get(
        web_app_client, data, status, expected_recipe, exp_code,
):
    response = await web_app_client.get('/v1/recipes/', params=data)
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content == expected_recipe
    else:
        assert content['code'] == exp_code


@pytest.mark.parametrize(
    'provider_id, status, expected',
    [
        (
            2,
            200,
            {
                'recipes': [
                    {
                        'id': 2,
                        'provider_id': 2,
                        'name': 'already_exist_recipe',
                        'job_vars': [],
                        'stages': [
                            {
                                'name': 'testCube',
                                'output': {},
                                'input': {},
                                'provider_name': 'deoevgen',
                            },
                        ],
                    },
                    {
                        'id': 3,
                        'provider_id': 2,
                        'name': 'new_meta',
                        'job_vars': [],
                        'stages': [
                            {
                                'name': 'testCube',
                                'output': {},
                                'input': {},
                                'provider_name': 'deoevgen',
                            },
                            {
                                'name': 'CubeNoOptional',
                                'output': {},
                                'input': {},
                                'provider_name': 'deoevgen',
                            },
                            {
                                'name': 'CubeNoOptional',
                                'output': {},
                                'input': {},
                                'provider_name': 'clownductor',
                            },
                        ],
                    },
                ],
            },
        ),
        (3, 404, 'PROVIDER_NOT_FOUND'),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_add_cubes.sql'])
@pytest.mark.config(TASK_PROCESSOR_ENABLED=False)
async def test_recipes_retrieve(web_app_client, provider_id, status, expected):
    response = await web_app_client.get(
        '/v1/recipes/retrieve/', params={'provider_id': provider_id},
    )
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content == expected
    else:
        assert content['code'] == expected


@pytest.mark.parametrize(
    'handle, recipe_data, status, expected',
    [
        pytest.param(
            '/v1/recipes/create/',
            {
                'name': 'first_recipe',
                'job_vars': ['var1', 'var2'],
                'stages': [
                    {
                        'name': 'testCube',
                        'provider_name': 'deoevgen',
                        'input': {'service_id': 'var1', 'job_id': 'var2'},
                    },
                    {'name': 'CubeNoOptional', 'input': {'token': None}},
                ],
                'provider_name': 'deoevgen',
            },
            200,
            {
                'id': 4,
                'name': 'first_recipe',
                'job_vars': ['var1', 'var2'],
                'stages': [
                    {
                        'name': 'testCube',
                        'provider_name': 'deoevgen',
                        'input': {'service_id': 'var1', 'job_id': 'var2'},
                    },
                    {
                        'name': 'CubeNoOptional',
                        'provider_name': 'deoevgen',
                        'input': {'token': None},
                    },
                ],
                'provider_id': 2,
            },
            id='created_successfully',
        ),
        pytest.param(
            '/v1/recipes/create/check/',
            {
                'name': 'first_recipe',
                'job_vars': ['var1', 'var2'],
                'stages': [
                    {
                        'name': 'testCube',
                        'input': {'service_id': 'var1', 'job_id': 'var2'},
                    },
                    {'name': 'CubeNoOptional', 'input': {'token': None}},
                ],
                'provider_name': 'deoevgen',
            },
            200,
            {
                'change_doc_id': 'task-processor_2_first_recipe',
                'data': {
                    'job_vars': ['var1', 'var2'],
                    'name': 'first_recipe',
                    'provider_name': 'deoevgen',
                    'stages': [
                        {
                            'input': {'job_id': 'var2', 'service_id': 'var1'},
                            'name': 'testCube',
                            'provider_name': 'deoevgen',
                        },
                        {
                            'input': {'token': None},
                            'name': 'CubeNoOptional',
                            'provider_name': 'deoevgen',
                        },
                    ],
                },
            },
            id='checked_ok',
        ),
        pytest.param(
            '/v1/recipes/create/check',
            {
                'name': 'first_recipe',
                'job_vars': ['var1', 'var2'],
                'stages': [{'name': 'testCube'}, {'name': 'CubeNoOptional'}],
                'provider_name': 'not exist',
            },
            404,
            'NOT_FOUND',
            id='non_existing_provider',
        ),
        pytest.param(
            '/v1/recipes/create/check',
            {
                'name': 'already_exist_recipe',
                'job_vars': ['var1', 'var2'],
                'stages': [{'name': 'testCube'}, {'name': 'CubeNoOptional'}],
                'provider_name': 'deoevgen',
            },
            409,
            'ALREADY_EXIST',
            id='recipe_already_created',
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_add_cubes.sql'])
@pytest.mark.config(
    TVM_SERVICES={'deoevgen': 1234}, TASK_PROCESSOR_ENABLED=False,
)
async def test_recipes_create(
        web_app_client, handle, recipe_data, status, expected,
):
    response = await web_app_client.post(handle, json=recipe_data)
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content == expected
    else:
        assert content['code'] == expected


@pytest.mark.parametrize(
    'handle, recipe_data, status, expected',
    [
        pytest.param(
            '/v1/recipes/update/',
            {
                'name': 'already_exist_recipe',
                'job_vars': ['var1', 'var2', 'var3'],
                'stages': [
                    {
                        'name': 'testCube',
                        'provider_name': 'deoevgen',
                        'input': {'service_id': 'var1', 'job_id': 'var2'},
                    },
                    {
                        'name': 'testCube',
                        'input': {'service_id': 'var1', 'job_id': None},
                    },
                    {'name': 'CubeNoOptional', 'input': {'token': None}},
                ],
                'provider_id': 2,
            },
            200,
            {
                'id': 4,
                'job_vars': ['var1', 'var2', 'var3'],
                'name': 'already_exist_recipe',
                'provider_id': 2,
                'stages': [
                    {
                        'input': {'job_id': 'var2', 'service_id': 'var1'},
                        'name': 'testCube',
                        'provider_name': 'deoevgen',
                    },
                    {
                        'input': {'job_id': None, 'service_id': 'var1'},
                        'name': 'testCube',
                        'provider_name': 'deoevgen',
                    },
                    {
                        'input': {'token': None},
                        'name': 'CubeNoOptional',
                        'provider_name': 'deoevgen',
                    },
                ],
            },
            id='updated_successfully',
        ),
        pytest.param(
            '/v1/recipes/update/check',
            _recipe(
                'already_exist_recipe',
                _stage(
                    'testCube',
                    input_mapping={'service_id': 'var1', 'job_id': None},
                ),
                _stage(
                    'testCube',
                    input_mapping={'service_id': 'var1', 'job_id': None},
                ),
                _stage('CubeNoOptional', input_mapping={'token': None}),
                job_vars=['var1', 'var2', 'var3'],
                provider_id=2,
            ),
            200,
            {
                'change_doc_id': 'task-processor_2_already_exist_recipe',
                'data': _recipe(
                    'already_exist_recipe',
                    _stage(
                        'testCube',
                        input_mapping={'service_id': 'var1', 'job_id': None},
                        provider_name='deoevgen',
                    ),
                    _stage(
                        'testCube',
                        input_mapping={'service_id': 'var1', 'job_id': None},
                        provider_name='deoevgen',
                    ),
                    _stage(
                        'CubeNoOptional',
                        input_mapping={'token': None},
                        provider_name='deoevgen',
                    ),
                    job_vars=['var1', 'var2', 'var3'],
                    provider_id=2,
                ),
                'diff': {
                    'current': _recipe(
                        'already_exist_recipe',
                        _stage(
                            'testCube',
                            provider_name='deoevgen',
                            input_mapping={},
                            output_mapping={},
                        ),
                        job_vars=[],
                        provider_id=2,
                        provider_name='deoevgen',
                        with_id=True,
                    ),
                    'new': _recipe(
                        'already_exist_recipe',
                        _stage(
                            'testCube',
                            input_mapping={
                                'service_id': 'var1',
                                'job_id': None,
                            },
                            provider_name='deoevgen',
                        ),
                        _stage(
                            'testCube',
                            input_mapping={
                                'service_id': 'var1',
                                'job_id': None,
                            },
                            provider_name='deoevgen',
                        ),
                        _stage(
                            'CubeNoOptional',
                            input_mapping={'token': None},
                            provider_name='deoevgen',
                        ),
                        job_vars=['var1', 'var2', 'var3'],
                        provider_id=2,
                        provider_name='deoevgen',
                    ),
                },
            },
            id='checked_ok',
        ),
        pytest.param(
            '/v1/recipes/update/check',
            {
                'name': 'already_exist_recipe',
                'job_vars': ['var1', 'var2', 'var3'],
                'stages': [
                    {'name': 'testCube'},
                    {'name': 'testCube', 'input': {'a': 'b'}},
                    {'name': 'CubeNoOptional'},
                ],
                'provider_id': 42,
            },
            404,
            'NOT_FOUND',
            id='provider_not_found',
        ),
        pytest.param(
            '/v1/recipes/update/check',
            {
                'name': 'not_exist',
                'job_vars': ['var1', 'var2', 'var3'],
                'stages': [
                    {'name': 'testCube'},
                    {'name': 'testCube', 'input': {'a': 'b'}},
                    {'name': 'CubeNoOptional'},
                ],
                'provider_id': 2,
            },
            404,
            'RECIPE_NOT_FOUND',
            id='recipe_not_found',
        ),
        pytest.param(
            '/v1/recipes/update/check',
            {
                'name': 'already_exist_recipe',
                'job_vars': ['var1', 'var2', 'var3'],
                'stages': [
                    {'name': 'testCube'},
                    {'name': 'not_exist', 'input': {'a': 'b'}},
                    {'name': 'CubeNoOptional'},
                ],
                'provider_id': 2,
            },
            404,
            'NOT_FOUND',
            id='cubic_not_found',
        ),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_add_cubes.sql'])
@pytest.mark.config(TASK_PROCESSOR_ENABLED=False)
async def test_recipes_update(
        web_app_client, handle, recipe_data, status, expected,
):
    response = await web_app_client.post(handle, json=recipe_data)
    assert response.status == status, await response.text()
    content = await response.json()
    if response.status == 200:
        assert content == expected
    else:
        assert content['code'] == expected


@pytest.mark.parametrize(
    'data, status, expected_code',
    [
        ({'provider_id': 2, 'name': 'already_exist_recipe'}, 200, None),
        ({'provider_id': 2, 'name': 'not_exist'}, 404, 'NOT_FOUND'),
    ],
)
@pytest.mark.pgsql('task_processor', files=['test_add_cubes.sql'])
async def test_delete_recipe(
        web_app_client, get_recipe, data, status, expected_code,
):
    response = await web_app_client.post(
        '/v1/recipes/delete/check/', json=data,
    )
    assert response.status == status
    if response.status == 200:
        content = await response.json()

        assert content == {
            'change_doc_id': 'task-processor_2_already_exist_recipe',
            'data': {'name': 'already_exist_recipe', 'provider_id': 2},
        }

        recipe = await get_recipe(1)
        assert recipe

    response = await web_app_client.post('/v1/recipes/delete/', json=data)
    assert response.status == status
    if response.status == 200:
        recipe = await get_recipe(1)
        assert not recipe
    else:
        content = await response.json()
        assert content['code'] == expected_code


@pytest.mark.config(TASK_PROCESSOR_ENABLED=False)
@pytest.mark.pgsql('task_processor', files=['base.sql'])
@pytest.mark.parametrize('use_draft', [True, False])
@pytest.mark.parametrize(
    'base_url',
    [
        pytest.param('/v1/recipes/create'),
        pytest.param(
            '/v1/recipes/update',
            marks=[
                pytest.mark.pgsql('task_processor', files=['test_data.sql']),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'recipe, expected_status, expected_response',
    [
        pytest.param(
            _recipe('A', _stage('A', input_mapping={'in_param1': None})),
            200,
            _recipe(
                'A',
                _stage(
                    'A',
                    input_mapping={'in_param1': None},
                    provider_name='clown',
                ),
                with_id=True,
            ),
            id='all_ok',
        ),
        pytest.param(
            _recipe('A', _stage('A', input_mapping={'param1': 'some_param'})),
            400,
            {
                'code': 'RECIPE_VALIDATION_ERROR',
                'message': (
                    'Some stages has some errors: '
                    '(A, clown, 0) param "param1" from input mapping '
                    'is missing in needed or optional params of cube; '
                    '(A, clown, 0) "in_param1" needed params '
                    'are not presented in input mappings'
                ),
            },
            id='missing_param_in_job_vars',
        ),
        pytest.param(
            _recipe(
                'A',
                _stage(
                    'A',
                    input_mapping={'in_param1': None},
                    output_mapping={'some_param': 'non_existed'},
                ),
            ),
            400,
            {
                'code': 'RECIPE_VALIDATION_ERROR',
                'message': (
                    'Some stages has some errors: (A, clown, 0) param '
                    '"non_existed" from output mapping is missing in '
                    'output params of cube'
                ),
            },
            id='non_existing_output_param',
        ),
        pytest.param(
            _recipe(
                'A',
                _stage(
                    'A',
                    input_mapping={'in_param1': 'var1'},
                    output_mapping={'var2': 'out_param1'},
                ),
                _stage('A', input_mapping={'in_param1': 'non_exists'}),
                job_vars=['var1'],
            ),
            400,
            {
                'code': 'RECIPE_VALIDATION_ERROR',
                'message': (
                    '"non_exists" not in job variables on stage 1 '
                    '(cube A, provider clown)'
                ),
            },
            id='broken_recipe',
        ),
    ],
)
async def test_recipe_validation(
        web_app_client,
        use_draft,
        base_url,
        recipe,
        expected_status,
        expected_response,
):
    if not use_draft:
        response = await web_app_client.post(base_url, json=recipe)
        assert response.status == expected_status, await response.text()
        assert (await response.json()) == expected_response
        return

    response = await web_app_client.post(base_url + '/check', json=recipe)
    assert response.status == expected_status, await response.text()
    data = await response.json()
    if expected_status != 200:
        assert data == expected_response
        return

    response = await web_app_client.post(base_url, json=data['data'])
    assert response.status == expected_status, await response.text()
    assert (await response.json()) == expected_response


@pytest.mark.pgsql('task_processor', files=['test_add_cubes.sql'])
@pytest.mark.config(TASK_PROCESSOR_ENABLED=False)
async def test_create_and_update(web_app_client):
    response = await web_app_client.post(
        '/v1/recipes/create/',
        json=_recipe(
            'TestRecipe',
            _stage(
                'testCube',
                input_mapping={'service_id': 'var1', 'job_id': 'var2'},
            ),
            job_vars=['var1', 'var2'],
            provider_id=2,
        ),
    )
    assert response.status == 200, await response.text()

    response = await web_app_client.post(
        '/v1/recipes/update/check/',
        json=_recipe(
            'TestRecipe',
            _stage(
                'testCube',
                input_mapping={'service_id': 'var1', 'job_id': 'var2'},
            ),
            _stage('CubeNoOptional', input_mapping={'token': 'var3'}),
            job_vars=['var1', 'var2', 'var3'],
            provider_id=2,
        ),
    )
    assert response.status == 200, await response.text()
    data = await response.json()

    assert data == {
        'change_doc_id': 'task-processor_2_TestRecipe',
        'data': _recipe(
            'TestRecipe',
            _stage(
                'testCube',
                input_mapping={'service_id': 'var1', 'job_id': 'var2'},
                provider_name='deoevgen',
            ),
            _stage(
                'CubeNoOptional',
                input_mapping={'token': 'var3'},
                provider_name='deoevgen',
            ),
            job_vars=['var1', 'var2', 'var3'],
            provider_id=2,
        ),
        'diff': {
            'current': _recipe(
                'TestRecipe',
                _stage(
                    'testCube',
                    input_mapping={'service_id': 'var1', 'job_id': 'var2'},
                    provider_name='deoevgen',
                ),
                job_vars=['var1', 'var2'],
                provider_id=2,
                provider_name='deoevgen',
                with_id=True,
            ),
            'new': _recipe(
                'TestRecipe',
                _stage(
                    'testCube',
                    input_mapping={'service_id': 'var1', 'job_id': 'var2'},
                    provider_name='deoevgen',
                ),
                _stage(
                    'CubeNoOptional',
                    input_mapping={'token': 'var3'},
                    provider_name='deoevgen',
                ),
                job_vars=['var1', 'var2', 'var3'],
                provider_id=2,
                provider_name='deoevgen',
            ),
        },
    }

    response = await web_app_client.post(
        '/v1/recipes/update/', json=data['data'],
    )
    assert response.status == 200, await response.text()

    response = await web_app_client.get(
        '/v1/recipes/', params={'provider_id': 2, 'name': 'TestRecipe'},
    )
    assert response.status == 200, await response.text()
    data = await response.json()
    assert data == _recipe(
        'TestRecipe',
        _stage(
            'testCube',
            input_mapping={'service_id': 'var1', 'job_id': 'var2'},
            provider_name='deoevgen',
        ),
        _stage(
            'CubeNoOptional',
            input_mapping={'token': 'var3'},
            provider_name='deoevgen',
        ),
        job_vars=['var1', 'var2', 'var3'],
        provider_id=2,
        provider_name='deoevgen',
        with_id=True,
    )
