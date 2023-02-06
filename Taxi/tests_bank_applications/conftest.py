# pylint: disable=too-many-lines
import datetime
import json
import random
import string
import urllib.parse

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_applications_plugins import *  # noqa: F403 F401
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401

from tests_bank_applications import common

# try:
#     import library.python.resource  # noqa: F401

#     _IS_ARCADIA = True
# except ImportError:
#     _IS_ARCADIA = False

# if _IS_ARCADIA:
#     import logging
#     import dataclasses

#     @pytest.fixture(autouse=True)
#     async def service_logs(taxi_bank_applications):
#         levels = {
#             'INFO': logging.INFO,
#             'DEBUG': logging.DEBUG,
#             'ERROR': logging.ERROR,
#             'WARNING': logging.WARNING,
#             'CRITICAL': logging.CRITICAL,
#         }

#         # Each log record is captured as a dictionary,
#         # so we need to turn it back into a string
#         def serialize_tskv(row):
#             # these two will only lead to data duplication
#             skip = {'timestamp', 'level'}

#             # reorder keys so that 'text' is always in front
#             keys = list(row.keys())
#             keys.remove('text')
#             keys.insert(0, 'text')

#             return '\t'.join(
#                 [f'{k}={row[k]}' for k in keys if k not in skip]
#             )

#         async with taxi_bank_applications.capture_logs() as capture:
#             # This hack tricks the client into thinking that
#             # caches still need to be invalidated on the first call
#             # so as not to break tests that depend on this behaviour
#             # pylint: disable=protected-access
#             taxi_bank_applications._client._state_manager._state = (
#                 dataclasses.replace(
#                     # pylint: disable=protected-access
#                     taxi_bank_applications._client._state_manager._state,
#                     caches_invalidated=False,
#                 )
#             )

#             @capture.subscribe()
#             # pylint: disable=unused-variable
#             def log(**row):
#                 logging.log(
#                     levels.get(row['level'], logging.DEBUG),
#                     serialize_tskv(row),
#                 )

#             yield capture


# old buid - new buid
# '1111' - '67754336-d4d1-43c1-aadb-cabd06674ea6'
# 'no_sid_phone_buid' - '22222222-d4d1-43c1-aadb-cabd06674ea6'
# 'no_passport_phone' - '33333333-d4d1-43c1-aadb-cabd06674ea6'
# 'wrong_phone' - '44444444-d4d1-43c1-aadb-cabd06674ea6'


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


@pytest.fixture
def bank_agreements_mock(mockserver):
    class Context:
        def __init__(self):
            self.agreements = {
                'ru': {
                    'REGISTRATION': {
                        'agreement_text': (
                            'Нажимая на кнопку, вы принимаете <a href'
                            + '="some_url1">условия использования сервиса</a>'
                        ),
                        'version': 0,
                    },
                    'SIMPLIFIED_IDENTIFICATION': {
                        'agreement_text': (
                            'Нажимая на кнопку, вы принимаете <a href'
                            + '="some_url2">условия использования сервиса</a>'
                        ),
                    },
                    'DIGITAL_CARD_ISSUE': {
                        'agreement_text': 'http://digitalcard.fom/',
                        'version': 0,
                    },
                    'SPLIT_CARD_ISSUE': {
                        'agreement_text': 'Это карта сплита',
                        'version': 0,
                    },
                    'PRODUCT': {
                        'agreement_text': 'Открытие продукта',
                        'version': 0,
                    },
                },
                'en': {
                    'REGISTRATION': {
                        'agreement_text': (
                            'By pressing the button, you agree with '
                            + '<a href="some_url1">terms of service use</a>'
                        ),
                        'version': 0,
                    },
                    'SIMPLIFIED_IDENTIFICATION': {
                        'agreement_text': (
                            'By pressing the button, you agree with '
                            + '<a href="some_url2">terms of service use</a>'
                        ),
                    },
                    'DIGITAL_CARD_ISSUE': {
                        'agreement_text': 'http://digitalcard.fom/',
                        'version': 0,
                    },
                    'SPLIT_CARD_ISSUE': {
                        'agreement_text': 'This is split card',
                        'version': 0,
                    },
                },
            }
            self.http_status_code = 200
            self.get_agreement_handler = None
            self.accept_agreement_handler = None

        def set_agreements(self, agreements):
            self.agreements = agreements

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler('/bank-agreements/v1/agreements/v1/get_agreement')
    def _get_agreement_handler(request):
        locale = request.headers['X-Request-Language']
        assert locale
        if locale not in ['ru', 'en']:
            locale = 'ru'

        data = json.loads(request.get_data())
        title = data['title']
        if (
                locale not in context.agreements
                or title not in context.agreements[locale]
        ):
            return mockserver.make_response(
                status=404,
                json={'code': '404', 'message': 'ne nashel\' :\'('},
            )
        return mockserver.make_response(
            status=context.http_status_code,
            json=context.agreements[locale][title],
        )

    @mockserver.json_handler(
        '/bank-agreements/v1/agreements/v1/accept_agreement',
    )
    def _accept_agreement_handler(request):
        return mockserver.make_response(status=200)

    context.get_agreement_handler = _get_agreement_handler
    context.accept_agreement_handler = _accept_agreement_handler

    return context


@pytest.fixture
def bank_userinfo_mock(mockserver):
    class Context:
        def __init__(self):
            self.create_buid_handler = None
            self.get_buid_info_handler = None
            self.phone_number_handler = None
            self.get_phone_id_handler = None
            self.get_phone_by_phone_id_handler = None
            self.http_status_code = 200
            self.buid_status = common.STATUS_FINAL
            self.phone_id = common.DEFAULT_YABANK_PHONE_ID

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler('/bank-userinfo/userinfo-internal/v1/create_buid')
    def _create_buid_handler(request):
        assert request.json.get('uid')
        if context.http_status_code == 200:
            return {'buid': common.DEFAULT_YANDEX_BUID}
        return mockserver.make_response(
            status=context.http_status_code,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _get_buid_info_handler(request):
        yandex_uid = common.DEFAULT_YANDEX_UID
        if 'phone_id' not in request.json:
            if 'uid' not in request.json:
                assert 'buid' in request.json
                buid = request.json.get('buid')
                buid_map = {
                    '22222222-d4d1-43c1-aadb-cabd06674ea6': 'no_sid_phone_uid',
                    '44444444-d4d1-43c1-aadb-cabd06674ea6': (
                        common.DEFAULT_YANDEX_UID
                    ),
                    '33333333-d4d1-43c1-aadb-cabd06674ea6': (
                        common.DEFAULT_YANDEX_UID
                    ),
                    '67754336-d4d1-43c1-aadb-cabd06674ea6': (
                        common.DEFAULT_YANDEX_UID
                    ),
                }
                assert buid in buid_map
                yandex_uid = buid_map[buid]
        else:
            phone_id = request.json.get('phone_id')
            if phone_id == common.DEFAULT_NEW_PHONE_ID:
                return mockserver.make_response(
                    status=404,
                    json={'code': 'error_code', 'message': 'error_message'},
                )
            context.phone_id = request.json.get('phone_id')
        if context.http_status_code == 200:
            return mockserver.make_response(
                status=context.http_status_code,
                json={
                    'buid_info': {
                        'yandex_uid': yandex_uid,
                        'buid': common.DEFAULT_YANDEX_BUID,
                        'status': context.buid_status,
                        'phone_id': context.phone_id,
                    },
                },
            )
        return mockserver.make_response(
            status=context.http_status_code,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    def make_response_phone_number(buid: str):
        phones = {
            '33333333-d4d1-43c1-aadb-cabd06674ea6': {'phone': '+70987654321'},
            '22222222-d4d1-43c1-aadb-cabd06674ea6': {'phone': '+79999999999'},
            '67754336-d4d1-43c1-aadb-cabd06674ea6': {'phone': '+71234567890'},
        }

        no_phones = set(['44444444-d4d1-43c1-aadb-cabd06674ea6'])
        phone_not_found_error = {
            'code': 'NotFound',
            'message': 'phone not found',
        }

        if buid in no_phones:
            return mockserver.make_response(json=phone_not_found_error)
        return mockserver.make_response(json=phones[buid], status=200)

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_number',
    )
    def _mock_get_phone_number(request):
        assert request.method == 'POST'
        return make_response_phone_number(request.json.get('buid'))

    def make_response_phone_id(phone: str):
        phones = {
            common.DEFAULT_PHONE: {'phone_id': common.DEFAULT_YABANK_PHONE_ID},
        }

        new_phone = {'phone_id': common.DEFAULT_NEW_PHONE_ID}

        if phone in phones:
            return mockserver.make_response(json=phones[phone], status=200)
        return mockserver.make_response(json=new_phone, status=200)

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_id',
    )
    def _get_phone_id_handler(request):
        assert request.method == 'POST'
        return make_response_phone_id(request.json.get('phone'))

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_number_by_phone_id',
    )
    def _get_phone_by_phone_id_handler(request):
        assert request.method == 'POST'
        assert request.json.get('phone_id')
        if context.http_status_code == 200:
            return {'phone': common.DEFAULT_PHONE}
        return mockserver.make_response(status=context.http_status_code)

    context.create_buid_handler = _create_buid_handler
    context.get_buid_info_handler = _get_buid_info_handler
    context.phone_number_handler = _mock_get_phone_number
    context.get_phone_id_handler = _get_phone_id_handler
    context.get_phone_by_phone_id_handler = _get_phone_by_phone_id_handler

    return context


@pytest.fixture
def taxi_processing_mock(mockserver):
    class Context:
        def __init__(self):
            self.response = {'event_id': 'abc123'}
            self.http_status_code = 200
            self.create_event_handler = None
            self.payloads = []

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response(self, response):
            self.response = response

    context = Context()

    @mockserver.json_handler('/processing/v1/bank/applications/create-event')
    def _create_event_handler(request):
        assert request.headers.get('X-Idempotency-Token')
        context.payloads.append(
            (request.headers['X-Idempotency-Token'], request.json),
        )
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.create_event_handler = _create_event_handler

    return context


@pytest.fixture
def bank_forms_mock(mockserver):
    class Context:
        def __init__(self):
            self.http_status_code = 200
            self.get_registration_form_handler = None
            self.get_simplified_form_handler = None
            self.set_registration_form_handler = None
            self.set_simplified_form_handler = None
            self.set_kyc_form = None
            self.forms = {
                'REGISTRATION': {
                    'passport_phone_id': '2',
                    'masked_phone': '+7***1**2*2*',
                    'phone': common.DEFAULT_PHONE,
                },
                'SIMPLIFIED_IDENTIFICATION': {
                    'last_name': 'Петров',
                    'first_name': 'Пётр',
                    'birthday': '2000-07-02',
                },
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-forms/forms-internal/v1/get_registration_form',
    )
    def _get_registration_form_handler(request):
        return mockserver.make_response(
            status=context.http_status_code,
            json=context.forms['REGISTRATION'],
        )

    @mockserver.json_handler(
        '/bank-forms/forms-internal/v1/get_simplified_identification_form',
    )
    def _get_simplified_form_handler(request):
        return mockserver.make_response(
            status=context.http_status_code,
            json=context.forms['SIMPLIFIED_IDENTIFICATION'],
        )

    @mockserver.json_handler('/bank-forms/v1/forms/v1/set_registration_form')
    def _set_registration_form_handler(request):
        if context.http_status_code == 200:
            context.forms['REGISTRATION'] = request.json
        return mockserver.make_response(status=context.http_status_code)

    @mockserver.json_handler(
        '/bank-forms/v1/forms/v1/set_simplified_identification_form',
    )
    def _set_simplified_form_handler(request):
        if context.http_status_code == 200:
            context.forms['SIMPLIFIED_IDENTIFICATION'] = request.json
        return mockserver.make_response(status=context.http_status_code)

    @mockserver.json_handler('/bank-forms/v1/forms/v1/set_kyc_form')
    def _set_kyc_form_handler(request):
        return mockserver.make_response(status=context.http_status_code)

    context.get_registration_form_handler = _get_registration_form_handler
    context.get_simplified_form_handler = _get_simplified_form_handler
    context.set_registration_form_handler = _set_registration_form_handler
    context.set_simplified_form_handler = _set_simplified_form_handler
    context.set_kyc_form = _set_kyc_form_handler

    return context


@pytest.fixture
def passport_internal_mock(mockserver, mocked_time):
    class Context:
        def __init__(self):
            self.submit_handler = None
            self.commit_handler = None
            self.limits_handler = None
            self.remove_passport_phone_handler = None
            self.remove_sid_handler = None

            self.sms_remained = 3
            self.time_to_resend = 5
            self.submit_status_code = 200
            self.submit_response = {
                'status': 'ok',
                'track_id': common.TRACK_ID,
                'deny_resend_until': int(
                    mocked_time.now()
                    .replace(tzinfo=datetime.timezone.utc)
                    .timestamp()
                    + self.time_to_resend,
                ),
            }
            self.commit_status_code = 200
            self.commit_response = {
                'status': 'ok',
                'track_id': common.TRACK_ID,
            }
            self.expect_user_tickets = False
            self.gps_package_name_send = False

        def set_expect_user_tickets(self, flag):
            self.expect_user_tickets = flag

        def set_submit_status_code(self, code):
            self.submit_status_code = code

        def set_submit_response(self, response):
            self.submit_response = response

        def update_ts_in_submit_response(self):
            self.submit_response['deny_resend_until'] = int(
                mocked_time.now()
                .replace(tzinfo=datetime.timezone.utc)
                .timestamp()
                + self.time_to_resend,
            )

        def set_commit_response(self, response):
            self.commit_response = response

        def set_commit_status_code(self, code):
            self.commit_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/passport-internal/2/bundle/'
        'phone/bind_simple_or_confirm_bound/submit/',
    )
    def _submit_handler(request):
        data = [it.split('=') for it in request.get_data().decode().split('&')]
        has_number = False
        has_display_language = False
        has_gps_package_name = False
        for item in data:
            if item[0] == 'number':
                has_number = True
                assert isinstance(item[1], str)
                assert item[1] != ''
            elif item[0] == 'display_language':
                has_display_language = True
                assert isinstance(item[1], str)
                assert item[1] != ''
            elif item[0] == 'gps_package_name':
                has_gps_package_name = True
                assert isinstance(item[1], str)
                assert item[1] != ''
        assert has_gps_package_name == context.gps_package_name_send
        assert has_number
        assert has_display_language
        assert request.query == {'consumer': 'bank-applications'}
        assert request.headers['Ya-Consumer-Client-Ip'] == common.SOME_IP
        assert request.headers['Ya-Client-User-Agent']
        assert (
            request.headers['Ya-Consumer-Client-Scheme']
            == common.PASSPORT_CLIENT_SCHEME
        )
        assert context.expect_user_tickets == (
            'X-Ya-User-Ticket' in request.headers
        )
        context.sms_remained = context.sms_remained - 1
        return mockserver.make_response(
            status=context.submit_status_code, json=context.submit_response,
        )

    @mockserver.json_handler(
        '/passport-internal/2/bundle/'
        'phone/bind_simple_or_confirm_bound/commit/',
    )
    def _commit_handler(request):
        data = [it.split('=') for it in request.get_data().decode().split('&')]
        has_code = False
        has_uid = False
        for item in data:
            if item[0] == 'code':
                has_code = True
                assert isinstance(item[1], str)
                assert item[1] != ''
            elif item[0] == 'uid':
                has_uid = True
                assert item[1] == common.DEFAULT_YANDEX_UID
            elif item[0] == 'track_id':
                assert item[1] == common.TRACK_ID
        assert has_code
        assert has_uid != context.expect_user_tickets
        assert context.expect_user_tickets == (
            'X-Ya-User-Ticket' in request.headers
        )
        assert request.query == {'consumer': 'bank-applications'}
        assert request.headers['Ya-Consumer-Client-Ip'] == common.SOME_IP
        assert request.headers['Ya-Client-User-Agent']
        assert (
            request.headers['Ya-Consumer-Client-Scheme']
            == common.PASSPORT_CLIENT_SCHEME
        )
        return mockserver.make_response(
            status=context.commit_status_code, json=context.commit_response,
        )

    @mockserver.json_handler(
        '/passport-internal/1/bundle/account/register/limits/',
    )
    def _limits_handler(request):
        assert request.query == {'consumer': 'bank-applications'}
        assert request.get_data().decode() == 'track_id=' + common.TRACK_ID
        assert request.headers['Ya-Consumer-Client-Ip'] == common.SOME_IP
        assert context.expect_user_tickets == (
            'X-Ya-User-Ticket' in request.headers
        )
        return {
            'status': 'ok',
            'sms_remained_count': context.sms_remained,
            'confirmation_remained_count': 3,
        }

    @mockserver.json_handler(
        r'/passport-internal/1/account/.*/alias/bank_phonenumber/', regex=True,
    )
    def _remove_passport_phone_handler(request):
        assert request.method == 'DELETE'
        assert 'Ya-Consumer-Client-Ip' in request.headers
        assert 'X-Ya-Service-Ticket' in request.headers
        json_data = json.loads(request.get_data())

        assert 'phone_number' in json_data, json_data
        phone_number = json_data['phone_number']
        unknown_phones = set(['+70987654321'])
        known_phones = set(['+71234567890', '+79999999999'])
        error_data = {'status': 'error', 'errors': ['alias.not_found']}

        ok_data = {'status': 'ok'}

        if phone_number in unknown_phones:
            return error_data
        assert phone_number in known_phones
        return ok_data

    @mockserver.json_handler(
        r'/passport-internal/1/account/(?P<yandex_uid>.*)/subscription/bank/',
        regex=True,
    )
    def _remove_sid_handler(request, yandex_uid):
        assert request.method == 'DELETE'
        assert 'X-Ya-Service-Ticket' in request.headers
        assert yandex_uid
        unknown_uids = set(['no_sid_phone_uid'])
        known_uids = set(['111111111'])
        error_data = {
            'status': 'error',
            'errors': [
                {
                    'field': None,
                    'message': (
                        'RemoveSidFromPassport error: '
                        'DELETE /1/account/yandex_uid/subscription/bank/, '
                        'status code 404'
                    ),
                    'code': 'nosubscription',
                },
            ],
        }
        ok_data = {'status': 'ok'}
        if yandex_uid in unknown_uids:
            return mockserver.make_response(status=404, json=error_data)
        assert yandex_uid in known_uids
        return ok_data

    context.submit_handler = _submit_handler
    context.commit_handler = _commit_handler
    context.limits_handler = _limits_handler
    context.remove_passport_phone_handler = _remove_passport_phone_handler
    context.remove_sid_handler = _remove_sid_handler

    return context


@pytest.fixture
def avatars_mds_mock(mockserver):
    def make_response(image_name, group_id):
        return {
            'imagename': image_name,
            'group-id': group_id,
            'meta': {'orig-format': 'JPEG'},
            'sizes': {
                'orig': {
                    'height': 640,
                    'path': (
                        common.get_image_url(
                            host='', group_id=group_id, image_name=image_name,
                        )
                        + 'orig'
                    ),
                    'width': 1024,
                },
                'sizename': {
                    'height': 200,
                    'path': (
                        common.get_image_url(
                            host='', group_id=group_id, image_name=image_name,
                        )
                        + 'sizename'
                    ),
                    'width': 200,
                },
            },
        }

    class Context:
        def __init__(self):
            self.group_id = None
            self.image_name = None

            self.put_unnamed_handler = None
            self.invalid_data_format = False
            self.bad_request = False

        def set_image_name(self, image_name):
            self.image_name = image_name

        def set_group_id(self, group_id):
            self.group_id = group_id

    context = Context()

    @mockserver.json_handler('/avatars-mds/put-fintech-passports', prefix=True)
    def _mock_put_unnamed_handler(request):
        if context.invalid_data_format:
            return mockserver.make_response(
                status=415,
                json={'status': '415', 'description': 'invalid data format'},
            )
        if context.bad_request:
            return mockserver.make_response(
                status=400,
                json={'status': '400', 'description': 'bad request'},
            )
        return make_response(context.image_name, context.group_id)

    context.put_unnamed_handler = _mock_put_unnamed_handler

    return context


@pytest.fixture
def ocr_recognize_mock(mockserver):
    def _parse_form(form):
        form = form.decode('utf-8')
        vals = form.split('\r\n\r\n')
        res = {}
        for i in range(len(vals) - 1):
            elem_with_name = vals[i].split()[-1]
            if elem_with_name.startswith('name'):
                res[elem_with_name[6:-1]] = vals[i + 1].split('\r\n')[0]
        return res

    def _make_fulltext(entity):
        return {
            'Confidence': entity['confidence'],
            'LineSizeCategory': 0,
            'Text': entity['text'],
            'Type': entity['type'],
        }

    def _make_block(entity):
        coefs = {
            'a0': 1,
            'a1': 0,
            'a2': 0,
            'a3': 0,
            'fromXtoY': True,
            'hh': 5.749999881,
        }
        color = {'Points': [], 'a': 0, 'b': 0, 'g': 0, 'r': 0, 'x': 0, 'y': 0}
        return {
            'angle': 0,
            'boxes': [
                {
                    'backgroundColor': color,
                    'confidence': entity['confidence'],
                    'h': 0,
                    'languages': [
                        {
                            'lang': 'en',
                            'texts': [
                                {
                                    'rank': entity['confidence'],
                                    'text': entity['text'],
                                    'words': [
                                        {
                                            'entity_idx': 0,
                                            'h': 0,
                                            'hyp': False,
                                            'meta': 'unk',
                                            'polyCoefs': coefs,
                                            'w': 0,
                                            'word': 'rus',
                                            'x': 0,
                                            'y': 0,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                    'lineSizeCategory': 0,
                    'polyCoefs': coefs,
                    'textColor': color,
                    'w': 0,
                    'x': 0,
                    'y': 0,
                },
            ],
            'h': 0,
            'lang': 'en',
            'rh': 5,
            'rw': 2,
            'rx': 0,
            'ry': 0,
            'type': 'main',
            'w': 0,
            'x': 0,
            'y': 0,
        }

    def _make_response(entities, status):
        return {
            'data': {
                'aggregated_stat': 967,
                'blocks': list(map(_make_block, entities)),
                'entities': entities,
                'fulltext': list(map(_make_fulltext, entities)),
                'imgsize': {'h': 2211, 'w': 1654},
                'istext': 0,
                'lang': 'en',
                'max_line_confidence': 1,
                'rotate': 0,
                'timeLimit': {'percent': 100, 'stopped_by_timeout': False},
            },
            'status': status,
        }

    def _make_entity(text, text_type, confidence):
        return {
            'confidence': confidence,
            'text': text,
            'text_clean': text,
            'type': text_type,
        }

    class Context:
        DEFAULT_ENTITIES = [_make_entity('-', 'expiration_date', 1.0)]

        def __init__(self):
            self.status = None
            self.entities = Context.DEFAULT_ENTITIES

            self.set_entities = None
            self.set_status = None
            self.set_bad_response = None

            self.make_entity = _make_entity

            self.make_response = _make_response
            self.ocr_recognize_handler = None

    context = Context()

    def _set_entities(entities):
        context.entities = Context.DEFAULT_ENTITIES + entities

    def _set_status(status):
        context.status = status

    def _set_bad_response(response_type):
        def _make_response(entities, status):
            return mockserver.make_response(
                status=int(response_type),
                json={'code': str(response_type), 'message': 'Failure'},
            )

        context.make_response = _make_response

    context.set_entities = _set_entities
    context.set_status = _set_status
    context.set_bad_response = _set_bad_response

    @mockserver.json_handler('/cv-ocr-translate/recognize')
    def _mock_ocr_recognize_handler(request):
        form_data = _parse_form(request.get_data())
        # apikey как в services.yaml ocr_apikey
        if (
                'apikey' not in form_data
                or form_data['apikey']
                != '99999999-9999-9999-9999-999999999999'
        ):
            return mockserver.make_response(
                status=400, json={'code': '400', 'message': 'Bad apikey'},
            )
        if 'langName' not in form_data:
            return mockserver.make_response(
                status=400, json={'code': '400', 'message': 'No lang'},
            )
        if 'rotate' in form_data and form_data['rotate'] not in {
                'balancer',
                '90',
                '180',
                '270',
                'off',
        }:
            return mockserver.make_response(
                status=400, json={'code': '400', 'message': 'invalid rotate'},
            )
        return context.make_response(context.entities, context.status)

    context.ocr_recognize_handler = _mock_ocr_recognize_handler

    return context


@pytest.fixture
def stq_agent(mockserver):
    class Context:
        def __init__(self):
            self.reschedule = None

    context = Context()

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    context.reschedule = _mock_stq_reschedule
    return context


@pytest.fixture
def bank_core_client_mock(mockserver):
    class Context:
        def __init__(self):
            self.client_info_handler = None
            self.client_request_check_handler = None
            self.client_ensure_handler = None
            self.http_status_code = 200
            self.auth_level = 'KYC'
            self.request_status = 'PENDING'
            self.errors = None
            self.ensure_pending = False
            self.ensure_failed = False
            self.ensure_success = False

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_auth_level(self, auth_level):
            self.auth_level = auth_level

        def set_request_status(self, status, errors=None):
            self.request_status = status
            self.errors = errors

    context = Context()

    @mockserver.json_handler('/bank-core-client/v1/client/info/get')
    def _client_info_handler(request):
        assert request.headers['X-Yandex-BUID']
        if context.http_status_code == 200:
            return {
                'auth_level': context.auth_level,
                'phone_number': common.DEFAULT_PHONE,
            }
        return mockserver.make_response(
            status=context.http_status_code,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    @mockserver.json_handler('/bank-core-client/v1/client/request/check')
    def _client_request_check_handler(request):
        assert request.json['request_id'] is not None
        if context.http_status_code == 200:
            return {
                'status': context.request_status,
                'request_id': request.json['request_id'],
                'errors': context.errors,
            }
        return mockserver.make_response(
            status=context.http_status_code,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    context = Context()

    @mockserver.json_handler(
        '/bank-core-client/v2/client/identification/ensure',
    )
    def _client_identification_ensure_handler(request):
        body = json.loads(request.get_data())
        for param in ['buid', 'context', 'data_revision', 'auth_level']:
            if param not in body:
                return mockserver.make_response(
                    status=400,
                    json={'code': '400', 'message': 'invalid params'},
                )
        assert body['context']['source_type'] == 'ESIA_VERIFIED'
        assert (
            body['context']['source_application_type']
            == 'SIMPLIFIED_IDENTIFICATION'
        )
        if context.ensure_pending:
            resp = {
                'data_revision': 0,
                'is_checks_in_progress': True,
                'auth_level': context.auth_level,
            }
            if context.request_status is not None:
                assert context.request_status in ['ALLOW', 'DENY', 'PENDING']
                resp['status'] = context.request_status
            return mockserver.make_response(status=200, json=resp)
        if context.ensure_failed:
            resp = {
                'data_revision': 1,
                'is_checks_in_progress': False,
                'auth_level': 'ANONYMOUS',
                'checks': [
                    {
                        'auth_level': 'IDENTIFIED',
                        'status': 'FAILED',
                        'errors': [
                            {'code': 'error_code', 'message': 'error_message'},
                        ],
                    },
                ],
            }
            if context.request_status is not None:
                assert context.request_status in ['ALLOW', 'DENY', 'PENDING']
                resp['status'] = context.request_status
            return mockserver.make_response(status=200, json=resp)
        if context.ensure_success:
            return mockserver.make_response(
                status=200,
                json={
                    'data_revision': 2,
                    'is_checks_in_progress': False,
                    'auth_level': context.auth_level,
                    'checks': [
                        {
                            'auth_level': context.auth_level,
                            'status': 'SUCCESS',
                        },
                    ],
                },
            )
        return mockserver.make_response(
            status=context.http_status_code,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    context.client_info_handler = _client_info_handler
    context.client_request_check_handler = _client_request_check_handler
    context.client_ensure_handler = _client_identification_ensure_handler
    return context


@pytest.fixture
def blackbox_mock(mockserver):
    class Context:
        def __init__(self):
            self.blackbox_handler = None
            self.uid = ''

        def set_uid(self, uid):
            self.uid = uid

    context = Context()

    def make_response_userinfo():
        result = {
            '111111111': {
                'users': [
                    {
                        'id': '111111111',
                        'attributes': {
                            '27': 'Пётр',
                            '28': 'Петров',
                            '30': '2000-07-02',
                        },
                    },
                ],
            },
            '111111112': {
                'users': [
                    {
                        'id': '111111112',
                        'attributes': {'27': 'Пётр', '28': 'Петров'},
                    },
                ],
            },
            '111111113': {'users': [{'111111113': '3'}]},
        }
        if context.uid not in result:
            return mockserver.make_response(status=500)
        return result[context.uid]

    @mockserver.json_handler('/blackbox/blackbox')
    def _mock_get_blackbox_info(request):
        assert request.query.get('method') == 'userinfo'
        assert request.query['uid']
        assert request.query['userip']
        if request.query.get('attributes') and '27' in request.query.get(
                'attributes',
        ):
            context.uid = request.query['uid']
            return make_response_userinfo()
        return mockserver.make_response(status=500)

    context.blackbox_handler = _mock_get_blackbox_info

    return context


@pytest.fixture
def access_control_mock(mockserver):
    class Context:
        def __init__(self):
            self.apply_policies_handler = None
            self.http_status_code = 200
            self.handler_path = None

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-access-control/access-control-internal/v1/apply-policies',
    )
    def _apply_policies_handler(request):
        assert request.method == 'POST'
        context.handler_path = request.json['resource_attributes'][
            'handler_path'
        ]
        is_allowed = request.json['subject_attributes']['jwt'] in [
            'allow',
            common.SUPPORT_TOKEN,
        ]
        response = {'decision': ('PERMIT' if is_allowed else 'DENY')}
        if is_allowed:
            response['user_login'] = common.SUPPORT_LOGIN
        return mockserver.make_response(
            status=context.http_status_code, json=response,
        )

    context.apply_policies_handler = _apply_policies_handler
    return context


@pytest.fixture
def nalog_ru_mock(mockserver):
    class Context:
        def __init__(self):
            self.get_request_id_handler = None
            self.get_req_status = 200
            self.get_req_response = None
            self.get_inn_handler = None
            self.get_inn_status = 200
            self.get_inn_resp = None
            self.request_data_mappings = {}

            self.get_inn_responses = None
            self.get_inn_index = -1

        def set_get_request_response(self, status, response):
            self.get_req_status = status
            self.get_req_response = response

        def set_get_inn_response(self, status, response):
            self.get_inn_status = status
            self.get_inn_resp = response

        def set_get_inn_responses(self, responses):
            self.get_inn_responses = responses
            self.get_inn_index = -1

    context = Context()

    def get_inn_response(last_name, middle_name):
        assert last_name is not None
        result = {
            ('Петров', 'Петрович'): {'state': 1.0, 'inn': '000000000000'},
            ('Петров', None): {'state': 1.0, 'inn': '000000000001'},
            ('Иванов', 'Петрович'): {'state': 0.0},
        }
        return result.get((last_name, middle_name))

    def set_mapping_request_inn(request_id, data):
        context.request_data_mappings[request_id] = data

    def get_data_by_request(request_id):
        return context.request_data_mappings[request_id]

    @mockserver.json_handler('/nalog-ru/inn-new-proc.do')
    def _mock_get_request_id(request):
        if context.get_req_response is not None:
            return mockserver.make_response(
                status=context.get_req_status, json=context.get_req_response,
            )
        request_id = randomword(10)
        data = {}
        request_data = {
            it.split('=')[0]: it.split('=')[1]
            for it in urllib.parse.unquote(
                request.get_data().decode('utf-8'),
            ).split('&')
        }
        if 'opt_otch' in request_data:
            data = get_inn_response(request_data['fam'], None)
            set_mapping_request_inn(request_id, data)
        else:
            assert 'otch' in request_data
            data = get_inn_response(request_data['fam'], request_data['otch'])
            set_mapping_request_inn(request_id, data)
        return mockserver.make_response(
            status=200,
            json={'requestId': request_id, 'captchaRequired': False},
        )

    context.get_request_id_handler = _mock_get_request_id

    @mockserver.json_handler('/nalog-ru/inn-new-proc.json')
    def _mock_get_inn(request):
        if context.get_inn_responses is not None:
            context.get_inn_index += 1
            return mockserver.make_response(
                status=context.get_inn_responses[context.get_inn_index][0],
                json=context.get_inn_responses[context.get_inn_index][1],
            )

        if context.get_inn_resp is not None:
            return mockserver.make_response(
                status=context.get_inn_status, json=context.get_inn_resp,
            )
        request_data = {
            it.split('=')[0]: it.split('=')[1]
            for it in urllib.parse.unquote(
                request.get_data().decode('utf-8'),
            ).split('&')
        }
        assert 'requestId' in request_data
        return mockserver.make_response(
            status=200, json=get_data_by_request(request_data['requestId']),
        )

    context.get_inn_handler = _mock_get_inn

    return context


@pytest.fixture
def core_esia_integration_mock(mockserver):
    class Context:
        def __init__(self):
            self.internal_error = False
            self.esia_url = 'https://url'
            self.esia_state = 'abc'
            self.esia_create_application_handler = None
            self.parse_esia_auth_response = None
            self.check_redirect_uri = None
            self.auth_code = None
            self.parse_error_reason = None

    context = Context()

    @mockserver.json_handler('/core-esia-integration/v1/esia/auth/url/get')
    def _esia_create_application_mock(request):

        if (
                'X-YaBank-ApplicationUUID' not in request.headers
                or context.internal_error
        ):
            return {'code': 500, 'message': 'Some error'}

        body = json.loads(request.get_data())
        state = body.get('state', context.esia_state)
        if context.check_redirect_uri is not None:
            assert 'redirect_url' in body
            assert body['redirect_url'] == context.check_redirect_uri

        return {'esia_url': context.esia_url, 'state': state}

    @mockserver.json_handler(
        '/core-esia-integration/v1/esia/auth/response/parse',
    )
    def _parse_esia_auth_response_mock(request):

        if context.internal_error:
            return mockserver.make_response(
                json={'code': 500, 'message': 'Some error'}, status=500,
            )

        body = json.loads(request.get_data())
        assert 'esia_raw_input' in body
        if body['esia_raw_input'] == common.INVALID_ESIA_RAW_RESPONSE:
            return mockserver.make_response(
                json={'parse_error_reason': context.parse_error_reason},
                status=400,
            )

        return {
            'auth_code': context.auth_code,
            'state': context.esia_state,
            'log_id': {'log_entry': ['123']},
        }

    context.esia_create_application_handler = _esia_create_application_mock
    context.parse_esia_auth_response = _parse_esia_auth_response_mock
    return context


@pytest.fixture
def core_current_account_mock(mockserver):
    class Context:
        def __init__(self):
            self.client_check_handler = None
            self.http_status_code = 200
            self.request_status = 'PENDING'
            self.errors = None

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response_errors(self, errors=None):
            self.errors = errors

        def set_request_status(self, status='PENDING'):
            self.request_status = status

    context = Context()

    @mockserver.json_handler('/core-current-account/v1/request/check')
    def _client_check_handler(request):
        if (
                not request.json['request_id']
                or not request.headers['X-Yandex-BUID']
                or not request.headers['X-YaBank-SessionUUID']
        ):
            mockserver.make_response(
                status=400, json={'code': '400', 'message': 'BadRequest'},
            )
        if context.http_status_code == 200:
            return {
                'status': context.request_status,
                'request_id': request.json['request_id'],
                'errors': context.errors,
            }
        return mockserver.make_response(
            status=context.http_status_code,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    context.client_check_handler = _client_check_handler
    return context


@pytest.fixture
def bank_notifications_mock(mockserver):
    class Context:
        def __init__(self):
            self.send_events_handler = None
            self.http_status_code = 200
            self.response = {
                'event_ids': ['e4cc96b1-5b29-4a35-ae37-67f7e03bbba6'],
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response(self, response):
            self.response = response

    context = Context()

    @mockserver.json_handler(
        '/bank-notifications/notifications-internal/v1/send_events',
    )
    def _send_events_mock(request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.json['consumer'] == 'BANK_APPLICATIONS'
        assert 'buid' in request.json or request.json['all']
        assert request.json['events'] != []
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.send_events_handler = _send_events_mock

    return context


@pytest.fixture
def bank_core_current_account_mock(mockserver):
    class Context:
        def __init__(self):
            self.request_check_handler = None
            self.http_status_code = 200
            self.response = {
                'status': common.STATUS_PENDING,
                'request_id': common.CORE_REQUEST_ID,
            }

    context = Context()

    @mockserver.json_handler('/bank-core-current-account/v1/request/check')
    def _request_check_mock(request):
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.request_check_handler = _request_check_mock

    return context
