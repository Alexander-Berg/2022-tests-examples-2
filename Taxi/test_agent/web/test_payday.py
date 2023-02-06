# pylint: disable=W0612
import pytest


@pytest.mark.parametrize(
    'body,headers,status,expected_db',
    [
        (  # Where X-YaTaxi-Api-Key not in headers, return 403
            {'ticket_key': 'PAYDAY-1', 'login': 'webalex'},
            {},
            403,
            {
                'login': 'webalex',
                'payday_uuid': '3326fb28-32d9-4694-86ef-ee45ea548c01',
                'status': 'pending_documents',
                'card_mask': '4276********3250',
                'phone_pd_id': '7f8d5e36-7bf2-425a-8463-6ed8e61e9e23',
                'ticket_tracker': 'PAYDAY-1',
            },
        ),
        (  # Where ticket_key is null, return 400
            {'login': 'webalex'},
            {'X-YaTaxi-Api-Key': 'SOME_SECRET'},
            400,
            {
                'login': 'webalex',
                'payday_uuid': '3326fb28-32d9-4694-86ef-ee45ea548c01',
                'status': 'pending_documents',
                'card_mask': '4276********3250',
                'phone_pd_id': '7f8d5e36-7bf2-425a-8463-6ed8e61e9e23',
                'ticket_tracker': 'PAYDAY-1',
            },
        ),
        (  # Where login is null, return 400
            {'ticket_key': 'PAYDAY-1'},
            {'X-YaTaxi-Api-Key': 'SOME_SECRET'},
            400,
            {
                'login': 'webalex',
                'payday_uuid': '3326fb28-32d9-4694-86ef-ee45ea548c01',
                'status': 'pending_documents',
                'card_mask': '4276********3250',
                'phone_pd_id': '7f8d5e36-7bf2-425a-8463-6ed8e61e9e23',
                'ticket_tracker': 'PAYDAY-1',
            },
        ),
        (  # Where OK
            {'ticket_key': 'PAYDAY-1', 'login': 'webalex'},
            {'X-YaTaxi-Api-Key': 'SOME_SECRET'},
            201,
            {
                'login': 'webalex',
                'payday_uuid': '3326fb28-32d9-4694-86ef-ee45ea548c01',
                'status': 'active',
                'card_mask': '4276********3250',
                'phone_pd_id': '7f8d5e36-7bf2-425a-8463-6ed8e61e9e23',
                'ticket_tracker': 'PAYDAY-1',
            },
        ),
        (  # Where ticket not found in agent
            {'ticket_key': 'PAYDAY-777', 'login': 'webalex'},
            {'X-YaTaxi-Api-Key': 'SOME_SECRET'},
            201,
            {
                'login': 'webalex',
                'payday_uuid': '3326fb28-32d9-4694-86ef-ee45ea548c01',
                'status': 'pending_documents',
                'card_mask': '4276********3250',
                'phone_pd_id': '7f8d5e36-7bf2-425a-8463-6ed8e61e9e23',
                'ticket_tracker': 'PAYDAY-1',
            },
        ),
    ],
)
@pytest.mark.translations(
    agent={
        'payday.tracker.no_found_ticket': {
            'ru': 'Тикет в агенте отсутствует',
            'en': 'Ticket in agent not found',
        },
    },
)
async def test_payday_tracker_documents_ready(
        web_app_client,
        mock_piecework_mapping_payday,
        web_context,
        patch,
        body,
        headers,
        status,
        expected_db,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
    async def update_status(**kwargs):
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(**kwargs):
        assert kwargs['ticket'] == 'PAYDAY-777'
        assert kwargs['text'] == 'payday.tracker.notfound_ticket_key'
        return {}

    response = await web_app_client.post(
        '/v1/payday/tracker_hook/ready_documents', json=body, headers=headers,
    )
    assert response.status == status
    async with web_context.pg.slave_pool.acquire() as conn:
        payday_users_query = (
            f'SELECT * FROM agent.users_payday WHERE login = \'webalex\''
        )
        payday_users_results = await conn.fetchrow(payday_users_query)
        expected_db['created'] = payday_users_results['created']
        expected_db['updated'] = payday_users_results['updated']
        assert expected_db == dict(payday_users_results)


@pytest.mark.config(
    AGENT_PAYDAY_SETTINGS={
        'enable': True,
        'send_payday': True,
        'org_uid': 'some_org_id',
        'default_percent': 58,
        'projects': [],
        'whitelist_logins': ['whitelist_login_1', 'black_whitelist_login'],
        'blacklist_logins': ['black_whitelist_login'],
        'tracker_settings': {
            'field_phone': 'field_phone',
            'field_mask': 'field_mask',
            'field_person': 'field_person',
        },
    },
)
@pytest.mark.parametrize(
    'headers,status,expected_data',
    [
        (
            {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'},
            200,
            {'status': 'pending_documents'},
        ),
        (
            {'X-Yandex-Login': 'liambaev', 'Accept-Language': 'ru-RU'},
            200,
            {
                'status': 'active',
                'card': {'mask': '3250', 'type': 'visa'},
                'percent_part_salary': {'style': 'percent', 'value': 0.58},
                'phone': '+79000000000',
            },
        ),
        (
            {'X-Yandex-Login': 'device25', 'Accept-Language': 'ru-RU'},
            200,
            {'status': 'not_available'},
        ),
        (
            {
                'X-Yandex-Login': 'whitelist_login_1',
                'Accept-Language': 'ru-RU',
            },
            200,
            {'status': 'available'},
        ),
        (
            {
                'X-Yandex-Login': 'black_whitelist_login',
                'Accept-Language': 'ru-RU',
            },
            200,
            {'status': 'not_available'},
        ),
    ],
)
async def test_payday_info(
        web_app_client,
        personal_phones_fine_mock,
        status,
        expected_data,
        headers,
):
    response = await web_app_client.get('/payday', headers=headers)
    assert response.status == status
    content = await response.json()
    assert content == expected_data


@pytest.mark.config(
    AGENT_PAYDAY_SETTINGS={
        'enable': True,
        'send_payday': True,
        'org_uid': 'some_org_id',
        'default_percent': 58,
        'projects': [],
        'whitelist_logins': ['whitelist_login_1', 'black_whitelist_login'],
        'blacklist_logins': ['black_whitelist_login'],
        'tracker_settings': {
            'field_phone': 'field_phone',
            'field_mask': 'field_mask',
            'field_person': 'field_person',
        },
    },
)
@pytest.mark.parametrize(
    'headers,body,status,expected_response',
    [
        (
            {
                'X-Yandex-Login': 'whitelist_login_1',
                'Accept-Language': 'ru-RU',
            },
            {'card_number': '4276840046393250', 'phone': '79858011671'},
            201,
            {'status': 'pending_documents'},
        ),
        (
            {'X-Yandex-Login': 'liambaev', 'Accept-Language': 'ru-RU'},
            {'card_number': '4276840046393250', 'phone': '79858011671'},
            403,
            {
                'code': 'payday.error.join_error',
                'message': 'Ошибка подключения к payday',
            },
        ),
        (
            {
                'X-Yandex-Login': 'whitelist_login_1',
                'Accept-Language': 'ru-RU',
            },
            {'card_number': '4276840046393251', 'phone': '79858011671'},
            400,
            {
                'code': 'payday.error.card_validate',
                'message': 'Ошибка валидации карты',
            },
        ),
        (
            {
                'X-Yandex-Login': 'whitelist_login_1',
                'Accept-Language': 'ru-RU',
            },
            {'card_number': '4276840046393250', 'phone': 'парапапа'},
            400,
            {
                'code': 'payday.error.phone_validate',
                'message': 'Ошибка валидации телефона',
            },
        ),
    ],
)
@pytest.mark.translations(
    agent={
        'payday.error.join_error': {
            'ru': 'Ошибка подключения к payday',
            'en': 'Error connect to payday',
        },
        'payday.error.card_validate': {
            'ru': 'Ошибка валидации карты',
            'en': 'Error validate card',
        },
        'payday.error.phone_validate': {
            'ru': 'Ошибка валидации телефона',
            'en': 'Error phone number',
        },
    },
)
async def test_payday_join(
        web_app_client,
        mock_personal_store_phones,
        mock_payday_employee_ok,
        patch,
        headers,
        body,
        status,
        expected_response,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(**kwargs):
        return dict(
            key='PAYDAY-1',
            self='https://st.yandex-team.ru/PAYDAY-1',
            id='c0403602-9e82-4506-ba79-29423cb7003c',
        )

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def update_ticket(**kwargs):
        return dict(
            key='PAYDAY-1',
            self='https://st.yandex-team.ru/PAYDAY-1',
            id='c0403602-9e82-4506-ba79-29423cb7003c',
        )

    @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
    async def update_status(**kwargs):
        return []

    response = await web_app_client.post('/payday', json=body, headers=headers)
    assert response.status == status
    assert expected_response == await response.json()
