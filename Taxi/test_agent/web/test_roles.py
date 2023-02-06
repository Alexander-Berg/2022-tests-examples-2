import pytest

GOOD_HEADERS: dict = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'}
EMPTY_HEADERS: dict = {}


@pytest.mark.translations(
    agent={
        'news_not_found': {
            'ru': 'Новость {id} не найдена',
            'en': 'News {id} not found',
        },
    },
)
@pytest.mark.parametrize(
    'body,headers,status,error_key',
    [
        (
            {
                'key': 'can_edit_post',
                'ru_name': 'Редактор новостей',
                'en_name': 'Editor post',
                'ru_description': 'Может редактировать новости',
                'en_description': 'User can edit posts',
            },
            GOOD_HEADERS,
            201,
            '',
        ),
        ({}, GOOD_HEADERS, 400, 'REQUEST_VALIDATION_ERROR'),
        (
            {
                'key': 'can_edit_post',
                'ru_name': 'Редактор новостей',
                'en_name': 'Editor post',
                'ru_description': 'Может редактировать новости',
                'en_description': 'User can edit posts',
            },
            EMPTY_HEADERS,
            400,
            'REQUEST_VALIDATION_ERROR',
        ),
        (
            {
                'key': 'can_edit_post',
                'en_name': 'Editor post',
                'ru_description': 'Может редактировать новости',
                'en_description': 'User can edit posts',
            },
            GOOD_HEADERS,
            400,
            'REQUEST_VALIDATION_ERROR',
        ),
    ],
)
async def test_create_new_permission(
        web_app_client, body, headers, status, error_key,
):
    response = await web_app_client.post(
        '/permissions/create', headers=headers, json=body,
    )
    assert response.status == status
    if status != 201:
        content = await response.json()
        assert content['code'] == error_key


async def test_list_permissions(web_app_client):
    response = await web_app_client.get(
        '/permissions/list', headers=GOOD_HEADERS,
    )
    assert response.status == 200
    content = await response.json()
    assert len(content) == 5


@pytest.mark.parametrize(
    'body,status',
    [
        ({'key': 'approve_piecework'}, 200),
        ({'key': 'no_key_in_system'}, 404),
        ({}, 400),
    ],
)
async def test_delete_permission(web_app_client, body, status):
    response = await web_app_client.delete(
        '/permissions/delete', json=body, headers=GOOD_HEADERS,
    )
    assert response.status == status


async def test_list_roles(web_app_client):
    response = await web_app_client.get('/roles/list', headers=GOOD_HEADERS)
    assert response.status == 200
    content = await response.json()
    assert len(content) == 2
    roles = [x['key'] for x in content]
    assert ['yandex_eda_agent', 'yandex_taxi_agent'].sort() == roles.sort()
    assert content == [
        {
            'created': '2021-01-01 00:00:00+03',
            'creator': 'webalex',
            'en_description': 'Support Yandex taxi',
            'en_name': 'support taxi',
            'key': 'yandex_taxi_agent',
            'permissions': ['approve_piecework_logistic'],
            'ru_description': 'Агент поддержки яндекс такси',
            'ru_name': 'Агент поддержки яндекс такси',
            'visible': True,
        },
        {
            'created': '2021-01-01 00:00:00+03',
            'creator': 'webalex',
            'en_description': 'Support Yandex eda',
            'en_name': 'support eda',
            'key': 'yandex_eda_agent',
            'permissions': ['approve_piecework', 'approve_piecework_logistic'],
            'ru_description': 'Агент поддержки яндекс еда',
            'ru_name': 'Агент поддержки яндекс еда',
            'visible': False,
        },
    ]


@pytest.mark.parametrize(
    'body,headers,status,response',
    [
        (
            {
                'key': 'quality_contol_agent',
                'ru_name': 'Сотрудник качества',
                'en_name': 'Quality support',
                'ru_description': (
                    'Может проверять тикеты саппорта на качество'
                ),
                'en_description': 'Can check ticket quality',
                'visible': True,
            },
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            201,
            {},
        ),
        (
            {
                'key': 'yandex_eda_agent',
                'ru_name': 'Саппорт еды',
                'en_name': 'Support eda',
                'ru_description': 'Саппорт еды',
                'en_description': 'Support eda',
                'visible': True,
            },
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            409,
            {},
        ),
        (
            {
                'key': 'yandex_eda_agent',
                'ru_name': 'Саппорт еды',
                'en_name': 'Support eda',
                'ru_description': 'Саппорт еды',
                'en_description': 'Support eda',
                'visible': True,
                'permissions': ['aaa', 'bbb', 'ccc'],
            },
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            409,
            {},
        ),
        (
            {
                'key': 'quality_contol_agent',
                'ru_name': 'quality_contol_agent',
                'en_name': 'quality_contol_agent',
                'ru_description': 'quality_contol_agent',
                'en_description': 'quality_contol_agent',
                'visible': True,
                'permissions': ['test1'],
            },
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
            201,
            {},
        ),
        ({}, {}, 400, {}),
    ],
)
async def test_create_role(web_app_client, body, headers, status, response):
    response = await web_app_client.post(
        '/roles/create', headers=headers, json=body,
    )
    assert response.status == status
    if response.status == 201:
        response_content = await response.json()
        assert response_content['key'] == body['key']
        if 'permissions' in body:
            assert response_content['permissions'] == body['permissions']
        else:
            assert response_content['permissions'] == []


@pytest.mark.parametrize(
    'body,status',
    [
        ({}, 400),
        ({'key': 'missing_key'}, 404),
        ({'key': 'yandex_eda_agent'}, 200),
        ({'key': 'yandex_taxi_agent'}, 409),
    ],
)
async def test_delete_role(web_app_client, body, status):
    response = await web_app_client.delete(
        '/roles/delete', json=body, headers=GOOD_HEADERS,
    )
    assert response.status == status


DATA_INPUT_ADD_ROLE_1 = {
    'login': 'webalex',
    'role': '{"role": "yandex_eda_agent"}',
}
DATA_INPUT_ADD_ROLE_2 = {
    'login': 'webalex',
    'role': '{"role":"yandex_taxi_agent"}',
}

DATA_INPUT_ADD_ROLE_3 = {
    'login': 'mikh-vasily',
    'role': '{"role": "yandex_eda_agent"}',
}


DATA_RESPONSE_GET_ALL_ROLES = {
    'code': 0,
    'users': [{'login': 'webalex', 'roles': [{'role': 'yandex_taxi_agent'}]}],
}


async def test_get_idm_system_roles(web_app_client):
    response = await web_app_client.get('/roles/idm/info')
    assert response.status == 200
    response_content = await response.json()
    assert response_content['code'] == 0
    assert len(response_content['roles']['values']) == 2


@pytest.mark.parametrize(
    'body,status_code,code',
    [
        (DATA_INPUT_ADD_ROLE_1, 200, 0),
        (DATA_INPUT_ADD_ROLE_2, 200, 1),
        (DATA_INPUT_ADD_ROLE_3, 200, 0),
    ],
)
async def test_add_role_from_idm(
        web_context, web_app_client, body, status_code, code,
):
    response = await web_app_client.post('/roles/idm/add-role', data=body)
    assert response.status == status_code
    response_content = await response.json()
    assert response_content['code'] == code
    if body['login'] == 'mikh-vasily':
        async with web_context.pg.slave_pool.acquire() as conn:
            query = 'SELECT * FROM agent.users ' 'WHERE login=\'{}\';'.format(
                body['login'],
            )
            result = await conn.fetchrow(query)
            assert result['login'] == body['login']
            assert result['first_name'] == body['login']
            assert result['last_name'] == body['login']


@pytest.mark.parametrize(
    'body,status_code,code',
    [(DATA_INPUT_ADD_ROLE_1, 200, 0), (DATA_INPUT_ADD_ROLE_2, 200, 0)],
)
async def test_remove_role_from_idm(web_app_client, body, status_code, code):
    response = await web_app_client.post('/roles/idm/remove-role', data=body)
    assert response.status == status_code
    response_content = await response.json()
    assert response_content['code'] == code


async def test_idm_get_all_roles(web_app_client):
    response = await web_app_client.get('/roles/idm/get-all-roles')
    assert response.status == 200
    response_content = await response.json()
    assert response_content == DATA_RESPONSE_GET_ALL_ROLES


@pytest.mark.parametrize(
    'input_data,headers,status',
    [
        ({}, {}, 400),
        ({}, GOOD_HEADERS, 400),
        ({'key': 'one_role'}, GOOD_HEADERS, 409),
        (
            {
                'key': 'yandex_taxi_agent',
                'ru_name': 'Обновлённая',
                'en_name': 'Updated',
                'ru_description': 'Обновёенное описание',
                'en_description': 'Updated_description',
            },
            GOOD_HEADERS,
            201,
        ),
        (
            {
                'key': 'yandex_taxi_agent',
                'ru_name': 'Обновлённая',
                'en_name': 'Updated',
                'ru_description': 'Обновёенное описание',
                'en_description': 'Updated_description',
                'permissions': [],
            },
            GOOD_HEADERS,
            201,
        ),
        (
            {
                'key': 'yandex_taxi_agent',
                'ru_name': 'Обновлённая',
                'en_name': 'Updated',
                'ru_description': 'Обновёенное описание',
                'en_description': 'Updated_description',
                'permissions': [
                    'test1',
                    'test2',
                    'approve_piecework_logistic',
                ],
            },
            GOOD_HEADERS,
            201,
        ),
        ({'key': 'yandex_taxi_agent', 'visible': True}, GOOD_HEADERS, 201),
        ({'key': 'yandex_taxi_agent', 'visible': False}, GOOD_HEADERS, 201),
        (
            {'key': 'yandex_taxi_agent', 'permissions': ['blablabla']},
            GOOD_HEADERS,
            409,
        ),
    ],
)
async def test_update_role(
        web_context, web_app_client, input_data, headers, status,
):
    response = await web_app_client.post(
        '/roles/update', json=input_data, headers=headers,
    )
    assert response.status == status
    if response.status == 201:
        response_content = await response.json()
        async with web_context.pg.slave_pool.acquire() as conn:
            query = 'SELECT * FROM agent.roles WHERE key=\'{id}\';'.format(
                id=input_data['key'],
            )
            result = await conn.fetchrow(query)

            if 'ru_name' in input_data:
                assert (
                    result['ru_name']
                    == input_data['ru_name']
                    == response_content['ru_name']
                )
            if 'en_name' in input_data:
                assert (
                    result['en_name']
                    == input_data['en_name']
                    == response_content['en_name']
                )
            if 'ru_description' in input_data:
                assert (
                    result['ru_description']
                    == input_data['ru_description']
                    == response_content['ru_description']
                )
            if 'en_description' in input_data:
                assert (
                    result['en_description']
                    == input_data['en_description']
                    == response_content['en_description']
                )
            if 'visible' in input_data:
                assert result['visible'] == input_data['visible']
                assert result['visible'] == response_content['visible']
                assert input_data['visible'] == response_content['visible']

            if 'permissions' in input_data:
                query_test = (
                    'SELECT key_permission FROM '
                    'agent.roles_permissions WHERE key_role=\'{key}\';'.format(
                        key=input_data['key'],
                    )
                )

                result_permissions = await conn.fetch(query_test)

                list_permissions_from_db = [
                    x['key_permission'] for x in result_permissions
                ]

                res_permissions_list_from_db = sorted(list_permissions_from_db)
                res_permissions_list_response = sorted(
                    response_content['permissions'],
                )
                res_permissions_list_input_data = sorted(
                    input_data['permissions'],
                )

                assert (
                    res_permissions_list_from_db
                    == res_permissions_list_input_data
                )
                assert (
                    res_permissions_list_from_db
                    == res_permissions_list_response
                )
                assert (
                    res_permissions_list_input_data
                    == res_permissions_list_response
                )
