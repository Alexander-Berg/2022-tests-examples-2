import pytest


@pytest.fixture(name='chatterbox_uservices')
def mock_chatterbox(mockserver):
    class Context:
        def __init__(self):
            self.request_id = None
            self.user_id = None
            self.yandex_uid = None
            self.platform = None
            self.message = None
            self.macro_id = None

            self.response_code = None
            self.already_opened = None

        def check_request(
                self,
                *,
                request_id=None,
                user_id=None,
                yandex_uid=None,
                platform=None,
                message=None,
                macro_id=None,
                already_opened=False,
        ):
            self.request_id = request_id
            self.user_id = user_id
            self.yandex_uid = yandex_uid
            self.platform = platform
            self.message = message
            self.macro_id = macro_id
            self.already_opened = already_opened

        def set_init_with_tvm_response_code(self, response_code):
            self.response_code = response_code

        def times_create_chat_lavka_called(self):
            return mock_init_with_tvm_lavka.times_called

        def times_create_chat_market_called(self):
            return mock_init_with_tvm_market.times_called

        def times_create_messenger_called(self):
            return mock_init_with_tvm_messenger.times_called

    context = Context()

    @mockserver.json_handler(
        '/chatterbox-uservices/v2/tasks/init_with_tvm/lavka',
    )
    def mock_init_with_tvm_lavka(request):
        body = request.json

        if context.platform is not None:
            assert body['platform'] == context.platform
        if context.request_id is not None:
            assert body['request_id'] == context.request_id
        if context.user_id is not None:
            assert body['user_id'] == context.user_id
        if context.yandex_uid is not None:
            assert body['yandex_uid'] == context.yandex_uid
        if context.message is not None:
            assert body['message'] == context.message
            assert 'macro_id' not in body
        if context.macro_id is not None:
            assert body['macro_id'] == context.macro_id
            assert 'message' not in body

        if context.already_opened:
            return mockserver.make_response(
                '{"task_id": "ticket_id", "status": "Chat already opened"}',
                status=409,
            )

        if context.response_code is not None:
            return mockserver.make_response('{}', status=context.response_code)

        return {'id': 'ticket_id', 'status': 'OK'}

    @mockserver.json_handler(
        '/chatterbox-uservices/v2/tasks/init_with_tvm/market',
    )
    def mock_init_with_tvm_market(request):
        body = request.json

        if context.platform is not None:
            assert body['platform'] == context.platform
        if context.request_id is not None:
            assert body['request_id'] == context.request_id
        if context.user_id is not None:
            assert body['user_id'] == context.user_id
        if context.yandex_uid is not None:
            assert body['yandex_uid'] == context.yandex_uid
        if context.message is not None:
            assert body['message'] == context.message
            assert 'macro_id' not in body
        if context.macro_id is not None:
            assert body['macro_id'] == context.macro_id
            assert 'message' not in body

        if context.response_code is not None:
            return mockserver.make_response('{}', status=context.response_code)

        return {'id': 'ticket_id', 'status': 'OK'}

    @mockserver.json_handler(
        '/chatterbox-uservices/v2/tasks/init_with_tvm/lavka_messenger',
    )
    def mock_init_with_tvm_messenger(request):
        body = request.json
        assert body['platform'] == context.platform
        assert body['request_id'] == context.request_id
        assert body['user_id'] == context.user_id
        assert body['yandex_uid'] == context.yandex_uid
        assert body['message'] == context.message

        return {'id': 'ticket_id', 'status': 'OK'}

    return context
