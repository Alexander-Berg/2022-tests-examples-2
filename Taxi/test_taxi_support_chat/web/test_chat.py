import http

import pytest


TRANSLATIONS = {
    'ivan': {'ru': 'Иван', 'en': 'Ivan'},
    'petr': {'ru': 'Петр', 'en': 'Petr'},
}

CLIENT_CHAT_ID = '5e285103779fb3831c8b4bd8'
DRIVER_CHAT_ID = '5e285103779fb3831c8b4bd9'
DRIVER_CHAT_ALREADY_INITIAL_ID = '5e285103779fb3831c8b4bda'
DRIVER_CHAT_WAITING_AMAZING_REASON = '5e285103779fb3831c8b4bdb'
DRIVER_CHAT_WAITING_FINISH = '5e285103779fb3831c8b4bdd'
DRIVER_CHAT_COMPLETE = '5e285103779fb3831c8b4bdc'
DRIVER_CHAT_COMPLETE_TOO = '5e285103779fb3831c8b4bdf'


async def test_invalid_id(web_app_client):
    response = await web_app_client.get('/v1/chat/not_found_id')
    assert response.status == http.HTTPStatus.BAD_REQUEST


async def test_not_found(web_app_client):
    response = await web_app_client.get('/v1/chat/5b436c16779fb3302cc784b9')
    assert response.status == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'service_ticket,chat_id,expected_status',
    [
        (
            'backend_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.OK,
        ),
        (
            'backend_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.OK,
        ),
        (
            'disp_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            'disp_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.OK,
        ),
        (
            'corp_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            'corp_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.FORBIDDEN,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_chat_type_access(
        web_app_client,
        service_ticket,
        chat_id,
        mock_tvm_keys,
        expected_status,
):
    response = await web_app_client.get(
        '/v1/chat/{}'.format(chat_id),
        headers={'X-Ya-Service-Ticket': service_ticket},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'chat_id, params, expected_result',
    [
        (
            '5b436ca8779fb3302cc784ba',
            {},
            {
                'id': '5b436ca8779fb3302cc784ba',
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'message_12',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'client_support',
                'metadata': {
                    'created': '2018-07-10T10:09:50+0000',
                    'updated': '2018-07-11T12:15:50+0000',
                    'ask_csat': False,
                    'last_message_from_user': False,
                    'new_messages': 2,
                    'user_locale': 'ru',
                    'csat_value': 'good',
                    'csat_reasons': ['fast answer', 'thank you'],
                    'chatterbox_id': 'chatterbox_id',
                    'metadata_field_1': 'value_1',
                },
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': 4,
                        'nickname': 'Иван',
                    },
                    {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
            },
        ),
        (
            '5b436ece779fb3302cc784bb',
            {},
            {
                'id': '5b436ece779fb3302cc784bb',
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'message_25',
                'status': {'is_open': False, 'is_visible': False},
                'type': 'client_support',
                'metadata': {
                    'created': '2018-07-05T10:59:50+0000',
                    'updated': '2018-07-06T13:44:50+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                },
                'participants': [
                    {
                        'id': 'some_support',
                        'role': 'support',
                        'avatar_url': 2,
                        'nickname': 'Петр',
                    },
                    {
                        'id': 'another_support',
                        'role': 'support',
                        'avatar_url': 2,
                        'nickname': 'Петр',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
            },
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {},
            {
                'id': '5b436ca8779fb3302cc784bf',
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'message_72',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'driver_support',
                'metadata': {
                    'created': '2018-07-05T10:59:50+0000',
                    'updated': '2018-07-11T12:15:50+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 2,
                    'user_locale': 'ru',
                    'csat_reasons': ['fast answer', 'thank you'],
                    'csat_value': 'good',
                    'chatterbox_id': 'chatterbox_id',
                },
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Иван',
                        'avatar_url': 4,
                    },
                    {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'driver',
                        'is_owner': True,
                    },
                ],
            },
        ),
        (
            '5b436ca8779fb3302cc784b0',
            {},
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'ask_csat': False,
                    'created': '2018-11-30T12:34:00+0000',
                    'last_message_from_user': False,
                    'new_messages': 0,
                    'updated': '2018-11-30T12:34:00+0000',
                    'user_locale': 'ru',
                },
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'message_32',
                'participants': [
                    {
                        'avatar_url': 2,
                        'id': 'support',
                        'nickname': 'Петр',
                        'role': 'support',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26154',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': False},
                'type': 'client_support',
            },
        ),
        (
            '5b436ca8779fb3302cc784b0',
            {'include_history': 'true'},
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'ask_csat': False,
                    'created': '2018-11-30T12:34:00+0000',
                    'last_message_from_user': False,
                    'new_messages': 0,
                    'updated': '2018-11-30T12:34:00+0000',
                    'user_locale': 'ru',
                },
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'message_32',
                'participants': [
                    {
                        'avatar_url': 2,
                        'id': 'support',
                        'nickname': 'Петр',
                        'role': 'support',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26154',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': False},
                'type': 'client_support',
                'messages': [
                    {
                        'id': 'message_31',
                        'metadata': {'created': '2018-11-30T12:34:00+0000'},
                        'sender': {
                            'id': 'user',
                            'role': 'client',
                            'sender_type': 'client',
                        },
                        'text': 'text_1',
                    },
                    {
                        'id': 'message_32',
                        'metadata': {'created': '2018-11-30T12:34:00+0000'},
                        'sender': {
                            'id': 'support',
                            'role': 'support',
                            'sender_type': 'support',
                        },
                        'text': 'text_2',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(USER_CHAT_MESSAGES_USE_ARCHIVE_API=True, TVM_ENABLED=False)
async def test_chat(web_app_client, chat_id, params, expected_result):
    response = await web_app_client.get('/v1/chat/%s' % chat_id, params=params)
    assert response.status == http.HTTPStatus.OK
    assert await response.json() == expected_result


@pytest.mark.parametrize(
    'chat_id, data, lang_map',
    [
        (
            '5b436ece779fb3302cc784bb',
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'date': {'newer_than': '2018-01-01', 'limit': 1},
            },
            {None: 'Иван', 'ru': 'Иван', 'en': 'Ivan'},
        ),
        (
            '5b436ece779fb3302cc784bd',
            {
                'owner': {'id': '5b4f5092779fb332fcc26155', 'role': 'client'},
                'type': 'visible',
            },
            {None: 'Петр', 'ru': 'Петр', 'en': 'Petr'},
        ),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.filldb(user_chat_messages='translation')
async def test_chat_translations(web_app_client, chat_id, data, lang_map):

    for lang, support_name in lang_map.items():
        headers = {}
        if lang:
            headers['Accept-Language'] = lang
        response = await web_app_client.get(
            '/v1/chat/{}'.format(chat_id), headers=headers,
        )
        assert response.status == http.HTTPStatus.OK
        chat = await response.json()

        assert chat['participants'][0]['nickname'] == support_name


@pytest.mark.translations(
    client_messages={
        'user_chat_csat.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'user_chat_csat.bad': {'ru': 'Плохо', 'en': 'Bad'},
        'user_chat_csat.normal': {'ru': 'Нормально', 'en': 'Normal'},
        'user_chat_csat.good': {'ru': 'Хорошо', 'en': 'Good'},
        'user_chat_csat.amazing': {'ru': 'Отлично', 'en': 'Amazing'},
        'user_chat_csat_reasons.template_answer': {
            'ru': 'Ответ шаблоном',
            'en': 'Template answer',
        },
        'user_chat_csat_reasons.problem_not_solved': {
            'ru': 'Проблема не решена',
            'en': 'Problem not solved',
        },
        'user_chat_csat_reasons.disagree_solution': {
            'ru': 'Не согласен с решением',
            'en': 'Disagree solution',
        },
        'user_chat_csat_reasons.long_answer': {
            'ru': 'Долгий ответ',
            'en': 'Long answer',
        },
        'user_chat_csat_reasons.new_key': {
            'ru': 'Другая причина',
            'en': 'Another reason',
        },
        'user_chat_csat_reasons.long_initial_answer': {
            'ru': 'Долгий первичный ответ',
            'en': 'Long initial response',
        },
        'user_chat_csat_reasons.long_interval_answer': {
            'ru': 'Задержка между сообщениями',
            'en': 'Long interval between messages',
        },
        'user_chat_csat.quality_score': {
            'ru': 'Оцените качество службы поддержки сервиса',
            'en': 'Score the quality of the service support',
        },
        'user_chat_csat.response_speed_score': {
            'ru': 'Оцените скорость ответа специалиста поддержки',
            'en': 'Score the response speed of the support specialist',
        },
        'csat.value.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'csat.value.normal': {'ru': 'Нормально', 'en': 'Normal'},
        'csat.value.amazing': {'ru': 'Восхитительно', 'en': 'Amazing'},
        'csat.exit.cancel': {
            'ru': 'Проблему не решили',
            'en': 'Problem not solved',
        },
        'csat.exit.finish': {'ru': 'Готово', 'en': 'Ready'},
        'csat.questions.ask_quality': {
            'ru': 'Оцените качество поддержки',
            'en': 'How do you like support quality?',
        },
        'csat.questions.ask_amazing_reason': {
            'ru': 'Почему так клёво?',
            'en': 'Why so amazing?',
        },
        'csat.reason.thank_you': {'ru': 'Спасибо', 'en': 'Thank you'},
        'csat.transition.change_rating': {
            'ru': 'Поменять оценку',
            'en': 'Change rating',
        },
    },
)
@pytest.mark.config(SUPPORT_CHAT_CSAT_CONTROL_ENABLED=True)
@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.parametrize(
    'exp3_response_key, chat_id, expected_meta_key, '
    'expected_dialog_key, expected_exp3_args',
    [
        pytest.param(
            None,
            CLIENT_CHAT_ID,
            'client_support_old_version',
            None,
            None,
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=False,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=False,
            ),
        ),
        pytest.param(
            'no_dialog',
            CLIENT_CHAT_ID,
            'client_support_experiments',
            None,
            {'user_locale': 'ru', 'csat_dialog_state': 'initial'},
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=True,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
            ),
        ),
        pytest.param(
            None,
            DRIVER_CHAT_ID,
            'driver_support_old_version',
            None,
            None,
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=False,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=False,
            ),
        ),
        pytest.param(
            'no_dialog',
            DRIVER_CHAT_ID,
            'driver_support_experiments',
            None,
            {'user_locale': 'ru', 'csat_dialog_state': 'initial'},
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=True,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
            ),
        ),
        pytest.param(
            'waiting_qa_rating',
            DRIVER_CHAT_ID,
            'driver_support_no_csat',
            'driver_support_waiting_qa',
            {'user_locale': 'ru', 'csat_dialog_state': 'initial'},
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=True,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
            ),
        ),
        pytest.param(
            'waiting_qa_rating',
            DRIVER_CHAT_ALREADY_INITIAL_ID,
            'driver_support_no_csat',
            'driver_support_already_initial',
            {'user_locale': 'ru', 'csat_dialog_state': 'initial'},
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=True,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
            ),
        ),
        pytest.param(
            'waiting_qa_amazing_reason',
            DRIVER_CHAT_WAITING_AMAZING_REASON,
            'driver_support_no_csat',
            'driver_support_waiting_amazing_reason',
            {
                'user_locale': 'ru',
                'csat_dialog_state': 'waiting_qa_amazing_reason',
            },
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=True,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
            ),
        ),
        pytest.param(
            None,
            DRIVER_CHAT_COMPLETE,
            'driver_support_complete',
            'driver_support_complete',
            None,
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=True,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
            ),
        ),
        pytest.param(
            None,
            DRIVER_CHAT_COMPLETE_TOO,
            'driver_support_complete_too',
            'driver_support_complete_too',
            None,
            marks=pytest.mark.config(
                USER_CHAT_USE_EXPERIMENTS_CSAT=True,
                DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True,
            ),
        ),
    ],
)
async def test_csat_control(
        web_app_client,
        load_json,
        mock_uuid4,
        mock_exp3_get_values,
        exp3_response_key,
        chat_id,
        expected_meta_key,
        expected_dialog_key,
        expected_exp3_args,
):
    exp3_response_map = load_json('exp3_responses.json')
    mocked_exp3 = None
    if exp3_response_key:
        mocked_exp3 = mock_exp3_get_values(
            exp3_response_map[exp3_response_key],
        )
    expected_metadata = load_json('expected_metadata.json')
    expected_dialog = load_json('expected_csat_dialog.json')
    response = await web_app_client.get(
        f'/v1/chat/{chat_id}', params={'include_history': 'true'},
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body['metadata'] == expected_metadata[expected_meta_key]
    if mocked_exp3:
        exp3_calls = mocked_exp3.calls
        exp3_args = {
            arg.name: arg.value for arg in exp3_calls[0]['experiments_args']
        }
        assert expected_exp3_args.items() <= exp3_args.items()
    if expected_dialog_key:
        assert (
            response_body['csat_dialog']
            == expected_dialog[expected_dialog_key]
        )
    else:
        assert 'csat_dialog' not in response_body
