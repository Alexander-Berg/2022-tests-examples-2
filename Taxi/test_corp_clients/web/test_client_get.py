async def test_client_get_unknown(web_app_client):
    response = await web_app_client.get('/v1/clients/unknown')
    assert response.status == 404


async def test_client_get(web_app_client, personal_mock):
    response = await web_app_client.get(
        '/v1/clients', params={'client_id': 'client_id_1'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'billing_id': '100001',
        'city': 'Москва',
        'country': 'rus',
        'created': '2021-07-01T13:00:00+03:00',
        'email': 'email@ya.ru',
        'features': [],
        'id': 'client_id_1',
        'is_trial': False,
        'name': 'corp_client_1',
        'billing_name': 'OOO Client1',
        'yandex_login': 'yandex_login_1',
        'tz': 'Europe/Moscow',
        'yandex_id': 'yandex_uid_1',
        'description': 'corp_client_1 description',
        'without_vat_contract': False,
    }


async def test_client_get_max_fields(web_app_client, personal_mock):
    response = await web_app_client.get(
        '/v1/clients',
        params={
            'client_id': 'client_id_1',
            'fields': (
                'billing_id,billing_name,country,created,description,'
                'email,features,is_trial,name,tz,yandex_login,'
                'without_vat_contract,yandex_id'
            ),
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'billing_id': '100001',
        'country': 'rus',
        'created': '2021-07-01T13:00:00+03:00',
        'email': 'email@ya.ru',
        'features': [],
        'id': 'client_id_1',
        'is_trial': False,
        'name': 'corp_client_1',
        'billing_name': 'OOO Client1',
        'yandex_login': 'yandex_login_1',
        'tz': 'Europe/Moscow',
        'yandex_id': 'yandex_uid_1',
        'description': 'corp_client_1 description',
        'without_vat_contract': False,
    }


async def test_get_tz(web_app_client):
    response = await web_app_client.get(
        '/v1/clients', params={'client_id': 'client_id_1', 'fields': 'tz'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {'id': 'client_id_1', 'tz': 'Europe/Moscow'}


async def test_client_get_collateral_accept(web_app_client, personal_mock):
    response = await web_app_client.get(
        '/v1/clients', params={'client_id': 'client_id_2'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'country': 'rus',
        'billing_id': '100002',
        'features': ['multi_available'],
        'cabinet_only_role_id': '12312wef23423',
        'city': 'Москва',
        'collateral_accept': {
            'accepted': True,
            'updated': '2021-07-04T10:00:00+03:00',
            'performer': 'test_login',
        },
        'tanker_collateral_accept': {
            'accepted': True,
            'updated': '2022-01-04T10:00:00+03:00',
            'performer': 'test_login_tanker',
        },
        'id': 'client_id_2',
        'is_trial': True,
        'name': 'corp_client_2',
        'yandex_login': 'yandex_login_2',
        'yandex_id': 'yandex_uid_2',
        'tmp_common_contract': True,
        'without_vat_contract': False,
    }
