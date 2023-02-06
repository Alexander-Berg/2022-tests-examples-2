# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from bank_agreements_plugins import *  # noqa: F403 F401
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401

DEFAULT_YANDEX_BUID = 'buid_1'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YABANK_SUPPORT_ID = 'support_id_1'


@pytest.fixture(name='userinfo_mock')
async def _userinfo_mock(mockserver):
    class Context:
        def __init__(self):
            self.get_buid_info_handler = None
            self.response_code = 200

    context = Context()

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _get_buid_info(request):
        if context.response_code != 200:
            return mockserver.make_response(status=context.response_code)
        if request.json.get('buid') and request.json.get('uid'):
            return mockserver.make_response(
                status=400, json={'code': 'BadRequest', 'message': 'Ony one'},
            )
        if request.json.get('buid') or request.json.get('uid'):
            return {
                'buid_info': {
                    'buid': DEFAULT_YANDEX_BUID,
                    'yandex_uid': DEFAULT_YANDEX_UID,
                    'phone_id': DEFAULT_YABANK_PHONE_ID,
                },
            }
        return None

    context.get_buid_info_handler = _get_buid_info

    return context
