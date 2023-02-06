import pytest

from test_workforce_management_bot import conftest
from test_workforce_management_bot import data
from workforce_management_bot.commands import commands
from workforce_management_bot.commands import utils


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_BOT_EMOJIES={
        'emoji_sad': 'pensive face',
        'emoji_heart': 'heavy black heart',
        'emoji_calendar': 'calendar',
        'emoji_coffee': 'hot beverage',
        'emoji_lunch': 'fork and knife',
    },
)
@pytest.mark.parametrize(
    'tst_request, wfm_status, wfm_data, expected_answer',
    [
        (
            {
                'message': {
                    'chat': {'id': 1},
                    'from': {'username': 'roma'},
                    'text': '/start',
                },
            },
            200,
            None,
            'Регистрация прошла успешно, показываю меню ❤!',
        ),
        (
            {
                'message': {
                    'chat': {'id': 1},
                    'from': {'username': 'roma'},
                    'text': '/start',
                },
            },
            404,
            None,
            None,
        ),
        (
            {
                'message': {
                    'chat': {'id': 1},
                    'from': {'username': 'roma'},
                    'text': 'random text',
                },
            },
            200,
            None,
            None,
        ),
        (
            {
                'message': {
                    'chat': {'id': 1},
                    'from': {'username': 'roma'},
                    'text': '/start',
                },
            },
            500,
            {
                'code': 'too_many_operators',
                'message': '',
                'details': {
                    'matched_operators': [
                        {'yandex_uid': 'uid1', 'domain': 'taxi'},
                        {'yandex_uid': 'uid1', 'domain': 'eats'},
                    ],
                },
            },
            'К этому аккаунту привязано больше одного оператора',
        ),
        (
            {
                'message': {
                    'chat': {'id': 1},
                    'from': {'username': 'roma'},
                    'text': 'Домен eats',
                },
            },
            200,
            None,
            'Регистрация прошла успешно, показываю меню ❤!',
        ),
    ],
)
async def test_webhook(
        web_app_client,
        mock_bot_class,
        mock_wfm,
        tst_request,
        wfm_status,
        wfm_data,
        expected_answer,
):
    mock_wfm(
        statuses={conftest.OPERATORS_CHECK: wfm_status},
        bodies={conftest.OPERATORS_CHECK: wfm_data},
    )

    await web_app_client.post('/v1/webhook', json=tst_request)
    send_messages = mock_bot_class.calls['send_message']
    if not expected_answer:
        assert not send_messages
        return

    assert send_messages[0]['kwargs']['text'] == expected_answer


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_BOT_EMOJIES={
        'emoji_sad': 'pensive face',
        'emoji_heart': 'heavy black heart',
        'emoji_calendar': 'calendar',
        'emoji_coffee': 'hot beverage',
        'emoji_lunch': 'fork and knife',
    },
)
async def test_shifts(
        web_app_client, mock_bot_class, mock_wfm, registered_operator,
):
    mock_wfm()
    await web_app_client.post(
        '/v1/webhook',
        json={
            'message': {
                'chat': {'id': 1},
                'from': {'username': 'roma'},
                'text': 'смены',
            },
        },
    )
    assert (
        mock_bot_class.calls['send_message'][0]['kwargs']['text']
        == 'Ближайшие смены: 📅 Смена 01 апреля (чт) 06:00 - 12:30'
        ' Обрати внимание, на смену запланировано: '
        'Химиотерапия 03 апреля (сб) 23:00 - 04 апреля (вс) '
        '00:00'
    )


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.parametrize(
    'text, result',
    (
        (
            '\U00002615 Мои перерывы',
            'Смена сегодня 01 апреля (чт) 06:00 - 12:30:'
            ' ☕ Перерыв 01 апреля (чт) 08:45 - 09:00',
        ),
        (
            'Пришли мне два кило перерывов, железяка',
            'Смена сегодня 01 апреля (чт) 06:00 - 12:30:'
            ' ☕ Перерыв 01 апреля (чт) 08:45 - 09:00',
        ),
        (
            'ПЕРЕРЫВЫ ЖЕ',
            'Смена сегодня 01 апреля (чт) 06:00 - 12:30:'
            ' ☕ Перерыв 01 апреля (чт) 08:45 - 09:00',
        ),
    ),
)
@pytest.mark.now('2021-04-01T08:30:40')
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_BOT_EMOJIES={
        'emoji_sad': 'pensive face',
        'emoji_heart': 'heavy black heart',
        'emoji_calendar': 'calendar',
        'emoji_coffee': 'hot beverage',
        'emoji_lunch': 'fork and knife',
    },
)
async def test_breaks(
        web_app_client,
        mock_bot_class,
        mock_wfm,
        registered_operator,
        text,
        result,
):
    mock_wfm()
    await web_app_client.post(
        '/v1/webhook',
        json={
            'message': {
                'chat': {'id': 1},
                'from': {'username': 'roma'},
                'text': text,
            },
        },
    )
    assert mock_bot_class.calls['send_message'][0]['kwargs']['text'] == result


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.now('2021-03-31T08:30:40')
async def test_breaks_next_shift(
        web_app_client, mock_bot_class, mock_wfm, registered_operator,
):
    mock_wfm()

    await web_app_client.post(
        '/v1/webhook',
        json={
            'message': {
                'chat': {'id': 1},
                'from': {'username': 'roma'},
                'text': '\U00002615 Мои перерывы',
            },
        },
    )
    assert (
        mock_bot_class.calls['send_message'][0]['kwargs']['text']
        == 'На данный момент у тебя нет смены. '
        'Ближайшая смена 01 апреля (чт) 06:00 - 12:30'
    )


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.parametrize(
    'bodies, result',
    [
        pytest.param(
            {
                conftest.ADDITIONAL_SHIFTS_JOBS_VALUES: (
                    data.ADDITIONAL_SHIFTS_JOBS
                ),
            },
            'Вам предложены доп. смены:',
            id='at_most_one_job_exists',
        ),
        pytest.param(
            {conftest.ADDITIONAL_SHIFTS_JOBS_VALUES: ({'jobs': []})},
            'Вам не предложено ни одной доп. смены',
            id='no_jobs',
        ),
    ],
)
async def test_additional_shift_offers(
        web_app_client,
        mock_bot_class,
        mock_wfm,
        registered_operator,
        bodies,
        result,
):
    mock_wfm(bodies=bodies)

    await web_app_client.post(
        '/v1/webhook',
        json={
            'message': {
                'chat': {'id': 1},
                'from': {'username': 'roma'},
                'text': '\U0001F4C5 Мои предложения доп. смен',
            },
        },
    )

    assert mock_bot_class.calls['send_message'][0]['kwargs']['text'] == result


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
async def test_confirm_additional_shift_request(
        web_app_client, mock_bot_class, mock_wfm, registered_operator,
):
    mock_wfm()

    await web_app_client.post(
        '/v1/webhook',
        json={
            'callback_query': {
                'id': '345',
                'data': '{"job_id": 1, "type": "ShiftOfferButtonText"}',
                'from': {'username': 'roma'},
                'message': {
                    'message_id': 1,
                    'chat': {'id': 1},
                    'from': {'username': 'bot'},
                    'text': (
                        '{emoji_calendar} Смена 01 апреля (чт) 06:00 - 12:30'
                    ),
                },
            },
        },
    )

    assert (
        mock_bot_class.calls['edit_message_text'][0]['kwargs']['text']
        == 'Вы уверены, что хотите выйти в данную смену?'
    )


@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.parametrize(
    'text, handler_response, handler_status, result',
    [
        pytest.param(
            commands.ACCEPT_TK,
            {},
            200,
            'Доп. смена выбрана успешно',
            id='shift_accept_succeed',
        ),
        pytest.param(
            commands.ACCEPT_TK,
            data.ACCEPT_SHIFT_ERRORS[0],
            404,
            'Такой кандидат на доп. смену не найден',
            id='candidate_not_found',
        ),
        pytest.param(
            commands.ACCEPT_TK,
            data.ACCEPT_SHIFT_ERRORS[1],
            400,
            'У вас есть другие смены в период доп. смены',
            id='busy_operator',
        ),
        pytest.param(
            commands.ACCEPT_TK,
            data.ACCEPT_SHIFT_ERRORS[2],
            400,
            'Извините, все доступные доп. смены распределены',
            id='all_shifts_distributed',
        ),
        pytest.param(
            commands.ACCEPT_TK,
            data.ACCEPT_SHIFT_ERRORS[3],
            400,
            'Не удалось расставить перерывы',
            id='breaks_build_failed',
        ),
        pytest.param(
            commands.ACCEPT_TK,
            data.ACCEPT_SHIFT_ERRORS[4],
            500,
            'Ошибка сервера',
            id='server_error',
        ),
        pytest.param(
            commands.REJECT_TK,
            {},
            200,
            'Ваш выбор отменен',
            id='user_pressed_no',
        ),
    ],
)
async def test_confirm_additional_shift(
        web_app_client,
        mock_bot_class,
        mock_wfm,
        registered_operator,
        text,
        handler_response,
        handler_status,
        result,
):
    mock_wfm(
        statuses={conftest.ADDITIONAL_SHIFT_ACCEPT: handler_status},
        bodies={conftest.ADDITIONAL_SHIFT_ACCEPT: handler_response},
    )

    await web_app_client.post(
        '/v1/webhook',
        json={
            'callback_query': {
                'id': '345',
                'from': {'username': 'roma'},
                'message': {
                    'chat': {'id': 1},
                    'from': {'username': 'bot'},
                    'text': text,
                },
                'data': utils.make_callback_data(
                    utils.add_command_to_data({'job_id': 1}, text),
                ),
            },
        },
    )

    assert (
        mock_bot_class.calls['answer_callback_query'][0]['kwargs']['text']
        == result
    )


@pytest.mark.filldb()
@pytest.mark.translations(wfm_backend_tg_bot=data.DEFAULT_TRANSLATION)
@pytest.mark.parametrize(
    'tst_request, wfm_status, wfm_data, expected_answer',
    [
        pytest.param(
            {
                'message': {
                    'chat': {'id': 222},
                    'from': {'username': 'neroma', 'language_code': 'ru'},
                    'text': 'смены',
                },
            },
            200,
            {'yandex_uid': '1234', 'state': 'ready', 'domain': 'taxi'},
            'Ближайшие смены:  Смена 01 апреля (чт) 06:00 - 12:30 Обрати '
            'внимание, на смену запланировано: Химиотерапия 03 апреля (сб) '
            '23:00 - 04 апреля (вс) 00:00',
            id='locale_is_changed',
        ),
    ],
)
async def test_locale_change(
        web_app_client,
        mock_bot_class,
        mock_wfm,
        tst_request,
        wfm_status,
        wfm_data,
        expected_answer,
        mongodb,
):
    mock_wfm(
        statuses={conftest.OPERATORS_CHECK: wfm_status},
        bodies={conftest.OPERATORS_CHECK: wfm_data},
    )

    await web_app_client.post('/v1/webhook', json=tst_request)
    send_messages = mock_bot_class.calls['send_message']
    if not expected_answer:
        assert not send_messages
        return

    assert send_messages[0]['kwargs']['text'] == expected_answer

    res = mongodb.workforce_management_bot_operators_bounds.find_one(
        {'yandex_uid': '1234'},
    )

    assert res['locale'] == 'ru'
