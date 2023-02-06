import uuid

import aiohttp
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_authproxy_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_remote(mockserver):
    def _func(
            url_path, request_body=None, response_code=200, response_body=None,
    ):
        if response_body is None:
            response_body = {}

        if not url_path.startswith('/'):
            url_path = f'/{url_path}'

        @mockserver.json_handler(url_path)
        def handler(request):
            if request.method != 'GET':
                assert request.json == request_body

            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _func


@pytest.fixture
def bank_service(mockserver):
    class Context:
        def __init__(self):
            self.yandex_uid = '123'
            self.bank_uid = '321'
            self.bank_phone_id = 'phone_id'
            self.session_status = 'ok'

            self.phone_id_dict = {}

            self.session_info_handler = None
            self.phone_id_handler = None

        def set_session_info(
                self, bank_uid, yandex_uid, bank_phone_id=None, status='ok',
        ):
            self.bank_uid = bank_uid
            self.yandex_uid = yandex_uid
            self.session_status = status
            if bank_phone_id:
                self.bank_phone_id = bank_phone_id

        def set_phone_id_dict(self, phone_id_dict):
            self.phone_id_dict = phone_id_dict

    context = Context()

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_session_info',
    )
    def _session_info_handler(request):
        assert request.method == 'POST'
        session_uuid = request.json.get('session_uuid')
        assert session_uuid
        return {
            'session_info': {
                'session_uuid': session_uuid,
                'buid': context.bank_uid,
                'yandex_uid': context.yandex_uid,
                'phone_id': context.bank_phone_id,
                'status': context.session_status,
            },
        }

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_id',
    )
    def _phone_id_handler(request):
        assert request.method == 'POST'
        phone = request.json.get('phone')
        assert phone

        if phone not in context.phone_id_dict:
            context.phone_id_dict[phone] = str(uuid.uuid4())

        return {'phone_id': context.phone_id_dict[phone]}

    context.session_info_handler = _session_info_handler
    context.phone_id_handler = _phone_id_handler

    return context
