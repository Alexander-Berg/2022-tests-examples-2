# pylint: disable=redefined-outer-name

import pytest
from telegram import error

from test_taxi_antifraud.utils import utils


TELEGRAM_TOKEN = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override'][
        'ANTIFRAUD_EATS_TELEGRAM_BOT_TOKEN'
    ] = TELEGRAM_TOKEN
    simple_secdist['settings_override'][
        'ANTIFRAUD_TAXI_TELEGRAM_BOT_TOKEN'
    ] = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew22'
    return simple_secdist


@pytest.fixture
def mock_telegram_api(patch):
    @patch('telegram.Bot.send_message')
    def _(*args, **kwargs):
        pass


async def _check_response_code(
        web_app_client, request_params, expected_response_code,
):
    response = await web_app_client.post(
        '/v1/send_telegram_message', json=request_params,
    )

    assert response.status == expected_response_code


async def _check_response_code_and_mock_calls(
        web_app_client,
        request_params,
        expected_response_code,
        mock,
        expected_mock_subdicts_list,
):
    await _check_response_code(
        web_app_client, request_params, expected_response_code,
    )

    mock_dicts_list = mock.calls
    assert len(mock_dicts_list) == len(expected_mock_subdicts_list)
    for dict_, subdict in zip(mock_dicts_list, expected_mock_subdicts_list):
        utils.check_dict_is_subdict(dict_, subdict)


async def _check_response_code_and_content(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
):
    response = await web_app_client.post(
        '/v1/send_telegram_message', json=request_params,
    )

    assert response.status == expected_response_code
    assert await response.json() == expected_response_content


@pytest.mark.parametrize(
    'request_params,expected_response_code',
    [
        ({'chat_id': '123456', 'text': 'Hey!', 'bot_id': 'eats'}, 200),
        ({'chat_id': '123456', 'text': '', 'bot_id': 'eats'}, 400),
        ({'chat_id': '123456', 'bot_id': 'eats'}, 400),
        ({'text': 'Hey!', 'bot_id': 'eats'}, 400),
        ({'chat_id': '123456', 'text': 'Hey!', 'bot_id': 'not_exist'}, 400),
    ],
)
async def test_send_telegram_message(
        web_app_client,
        mock_secdist,
        mock_telegram_api,
        request_params,
        expected_response_code,
):
    await _check_response_code(
        web_app_client, request_params, expected_response_code,
    )


@pytest.mark.parametrize(
    'token,request_params,expected_response_code,expected_response_content',
    [
        (
            'bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
            {'chat_id': '123456', 'text': 'Hey!', 'bot_id': 'eats'},
            500,
            {
                'error': (
                    'Error while sending request to Telegram API: '
                    'Invalid token'
                ),
            },
        ),
    ],
)
async def test_send_telegram_message_invalid_token(
        web_app_client,
        simple_secdist,
        mock_telegram_api,
        token,
        request_params,
        expected_response_code,
        expected_response_content,
):
    simple_secdist['settings_override'][
        'ANTIFRAUD_EATS_TELEGRAM_BOT_TOKEN'
    ] = token

    await _check_response_code_and_content(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
    )


def _make_expected_calls_subdict_from_request(
        request, simple_secdist, taxi_config,
):
    return {
        'chat_id': request['chat_id'],
        'message': request['text'],
        'bot_api_key': simple_secdist['settings_override'][
            taxi_config.get('AFS_BOT_IDS_TO_SECRET_NAMES')[request['bot_id']]
        ],
    }


@pytest.mark.parametrize(
    'request_params,expected_response_code',
    [({'chat_id': '123456', 'text': 'Hey!', 'bot_id': 'eats'}, 200)],
)
async def test_send_telegram_message_check_parameters(
        web_app_client,
        mock_secdist,
        patch,
        request_params,
        expected_response_code,
        taxi_config,
        simple_secdist,
):
    @patch('taxi.clients.telegram_bot.send_message')
    async def mock_telegram_message(
            _, chat_id, message, bot_api_key, **kwargs,
    ):
        pass

    await _check_response_code_and_mock_calls(
        web_app_client,
        request_params,
        expected_response_code,
        mock_telegram_message,
        [
            _make_expected_calls_subdict_from_request(
                request_params, simple_secdist, taxi_config,
            ),
        ],
    )


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {'chat_id': '123456', 'text': 'Hey!', 'bot_id': 'eats'},
            500,
            {
                'error': (
                    'Error while sending request to Telegram API: '
                    'Connection refused'
                ),
            },
        ),
    ],
)
async def test_send_telegram_message_connection_refused(
        web_app_client,
        patch,
        mock_secdist,
        request_params,
        expected_response_code,
        expected_response_content,
):
    @patch('telegram.Bot.send_message')
    def _(*args, **kwargs):
        raise error.NetworkError('Connection refused')

    await _check_response_code_and_content(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
    )


@pytest.mark.config(
    AFS_BOT_IDS_TO_SECRET_NAMES={
        'eats': 'ANTIFRAUD_EATS_TELEGRAM_BOT_TOKEN',
        'taxi': 'ANTIFRAUD_TAXI_TELEGRAM_BOT_TOKEN',
    },
)
@pytest.mark.parametrize(
    'request_params,expected_response_code',
    [
        ({'chat_id': '123456', 'text': 'Hey!', 'bot_id': 'eats'}, 200),
        ({'chat_id': '123456', 'text': 'Hey!', 'bot_id': 'taxi'}, 200),
    ],
)
async def test_send_telegram_message_different_bots(
        web_app_client,
        mock_secdist,
        patch,
        simple_secdist,
        request_params,
        expected_response_code,
        taxi_config,
):
    @patch('taxi.clients.telegram_bot.send_message')
    async def mock_telegram_message(
            _, chat_id, message, bot_api_key, **kwargs,
    ):
        pass

    await _check_response_code_and_mock_calls(
        web_app_client,
        request_params,
        expected_response_code,
        mock_telegram_message,
        [
            _make_expected_calls_subdict_from_request(
                request_params, simple_secdist, taxi_config,
            ),
        ],
    )
