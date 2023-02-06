import dataclasses

import pytest

import test_contractor_merch_payments_bot.mocks.common as common


TELEGRAM_DEFAULT_RESPONSE = {'ok': True}


@pytest.fixture(name='mock_telegram_send_message')
def _mock_telegram_send_message(mockserver):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mockserver.json_handler('/telegram/bot123456:test_token/sendMessage')
        def handler(request):
            return context.response

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@pytest.fixture(name='mock_telegram_send_photo')
def _mock_telegram_send_photo(mockserver):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mockserver.json_handler('/telegram/bot123456:test_token/sendPhoto')
        def handler(request):
            return context.response

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@pytest.fixture(name='mock_telegram_edit_message_media')
def _mock_telegram_edit_message_media(mockserver):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mockserver.json_handler(
            '/telegram/bot123456:test_token/editMessageMedia',
        )
        def handler(request):
            return context.response

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@pytest.fixture(name='mock_telegram_download_file')
def _mock_telegram_download_file(mockserver, load_binary):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mockserver.json_handler(
            '/telegram/file/bot123456:test_token/file_path',
        )
        def handler(request):
            image_bytes = load_binary(context.image)

            return mockserver.make_response(
                response=image_bytes,
                status=200,
                content_type='application/octet-stream',
            )

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@pytest.fixture(name='mock_telegram_get_file')
def _mock_telegram_get_file(mockserver, load_json):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mockserver.json_handler('/telegram/bot123456:test_token/getFile')
        def handler(request):
            return load_json('telegram_get_file_response.json')

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@pytest.fixture(name='mock_telegram_answer_callback_query')
def _mock_telegram_answer_callback_query(mockserver):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mockserver.json_handler(
            '/telegram/bot123456:test_token/answerCallbackQuery',
        )
        def handler(request):
            return context.response

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@dataclasses.dataclass
class MockedTelegramServiceContext:
    send_message: common.MockedHandlerContext
    send_photo: common.MockedHandlerContext
    edit_message_media: common.MockedHandlerContext
    get_file: common.MockedHandlerContext
    download_file: common.MockedHandlerContext
    answer_callback_query: common.MockedHandlerContext


@pytest.fixture(name='mock_telegram_service')
def _mock_telegram_service(
        mock_telegram_send_message,
        mock_telegram_send_photo,
        mock_telegram_edit_message_media,
        mock_telegram_get_file,
        mock_telegram_download_file,
        mock_telegram_answer_callback_query,
):
    return MockedTelegramServiceContext(
        send_message=mock_telegram_send_message(TELEGRAM_DEFAULT_RESPONSE),
        send_photo=mock_telegram_send_photo(TELEGRAM_DEFAULT_RESPONSE),
        edit_message_media=mock_telegram_edit_message_media(
            TELEGRAM_DEFAULT_RESPONSE,
        ),
        get_file=mock_telegram_get_file(TELEGRAM_DEFAULT_RESPONSE),
        download_file=mock_telegram_download_file(TELEGRAM_DEFAULT_RESPONSE),
        answer_callback_query=mock_telegram_answer_callback_query(
            TELEGRAM_DEFAULT_RESPONSE,
        ),
    )
