import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from selfemployed_fns_profiles_plugins import *  # noqa: F403 F401

DEFAULT_PHONE = '+71230000000'


def _passport_headers(passport_uid: str) -> dict:
    return {
        'X-Yandex-UID': passport_uid,
        'X-Request-Language': 'ru',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '11.00 (12345)',
        'X-Request-Platform': 'android',
        'X-Request-Platform-Version': '11.1.0',
        'X-Request-Application-Brand': 'yandex',
        'X-Request-Application-Build-Type': '',
    }


@pytest.fixture(scope='session')
def prepare_get_rq():
    def _prepare_get_rq(step, passport_uid: str) -> dict:
        return {
            'headers': _passport_headers(passport_uid),
            'path': f'/driver/v1/se-fns-profiles/v1/{step}',
        }

    return _prepare_get_rq


@pytest.fixture(scope='session')
def prepare_post_rq():
    def _prepare_post_rq(step, passport_uid: str) -> dict:
        return {
            'headers': _passport_headers(passport_uid),
            'path': f'/driver/v1/se-fns-profiles/v1/{step}',
        }

    return _prepare_post_rq


@pytest.fixture()
def personal_mock(mockserver):
    class Context:
        def __init__(self) -> None:
            self.inn = '000000000000'
            self.phone = DEFAULT_PHONE
            self.inn_pd_id = 'INN_PD_ID'
            self.phone_pd_id = 'PHONE_PD_ID'
            self.v1_tins_store = None
            self.v1_tins_retrieve = None
            self.v1_phones_store = None
            self.v1_phones_retrieve = None

    context = Context()

    @mockserver.json_handler('/personal/v1/tins/store')
    async def _store_inn_pd(request):
        assert request.json['value'] == context.inn
        return {'id': context.inn_pd_id, 'value': context.inn}

    @mockserver.json_handler('/personal/v1/tins/retrieve')
    async def _retrieve_inn_pd(request):
        assert request.json['id'] == context.inn_pd_id
        return {'id': context.inn_pd_id, 'value': context.inn}

    @mockserver.json_handler('/personal/v1/phones/store')
    async def _store_phone_pd(request):
        assert request.json['value'] == context.phone
        return {'id': context.phone_pd_id, 'value': context.phone}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _retrieve_phone_pd(request):
        assert request.json['id'] == context.phone_pd_id
        return {'id': context.phone_pd_id, 'value': context.phone}

    context.v1_tins_store = _store_inn_pd
    context.v1_tins_retrieve = _retrieve_inn_pd
    context.v1_phones_store = _store_phone_pd
    context.v1_phones_retrieve = _retrieve_phone_pd
    return context


@pytest.fixture()
def passport_internal_mock(mockserver):
    class Context:
        def __init__(self) -> None:
            self.phone = DEFAULT_PHONE
            self.track_id = 'TRACK_ID'
            self.code = '0000'
            self.phone_confirm_submit = None
            self.phone_confirm_commit = None

    context = Context()

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _phone_confirm_submit(request):
        assert request.query['consumer'] == 'taxi-selfemployed'
        assert request.form == {
            'confirm_method': 'by_sms',
            'display_language': 'ru',
            'number': context.phone,
            'route': 'taxiauth',
        }
        return {'status': 'ok', 'track_id': context.track_id}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    async def _phone_confirm_commit(request):
        assert request.query['consumer'] == 'taxi-selfemployed'
        expect_request = {'track_id': context.track_id, 'code': context.code}
        if request.form == expect_request:
            return {'status': 'ok'}
        return {'status': 'fail', 'errors': ['code.invalid']}

    context.phone_confirm_submit = _phone_confirm_submit
    context.phone_confirm_commit = _phone_confirm_commit
    return context
