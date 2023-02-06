# pylint: disable=too-many-lines
import json

import pytest
from tests_processing.processing.bank import common

CARD_TYPE = 'DIGITAL'
PUBLIC_AGREEMENT_ID = 'test_public_agreement_id'
BUID = 'buid-1'
YUID = '8421'
BUID_STATUS = 'FINAL'
SESSION_UUID = 'fac13679-73f7-465f-b94e-f359525850ec'
AGREEMENT_VERSION = 1
DEVICE_ID = 'some_device_id'


class MockParams:
    def __init__(self):
        self.handler = None
        self.response_code = 200
        self.grants_problems = False
        self.first_fail = False
        self.first_timeout = False
        self.errors_list = False
        self.empty_errors_list = False
        self.status_failed = False
        self.exists = False
        self.not_available = False
        self.access_deny = False


@pytest.fixture(name='passport_mock')
async def _passport_mock(mockserver):
    def make_error_bind_phone(error_code):
        if error_code != 500:
            return mockserver.make_response(
                status=error_code,
                content_type='application/json',
                response='{"status": "error",'
                '"errors": ["problem in passport"]}',
            )
        return mockserver.make_response(status=error_code)

    def make_phone_exists():
        return mockserver.make_response(
            status=200,
            content_type='application/json',
            response='{"status": "error", "errors": ["alias.exists"]}',
        )

    def make_phone_not_available():
        return mockserver.make_response(
            status=200,
            content_type='application/json',
            response='{"status": "error", "errors": ["alias.notavailable"]}',
        )

    def make_error_subscribe_sid(error_code):
        if error_code != 500:
            return mockserver.make_response(
                status=error_code,
                content_type='application/json',
                response='{"status": "error",'
                '"errors": [{"code": 400, "message": "problem in passport"}]}',
            )
        return mockserver.make_response(status=error_code)

    def make_grants_error_phone():
        return mockserver.make_response(
            status=403,
            content_type='application/json',
            response="""{
                "status": "error",
                "errors": [
                    "access.denied"
                ],
                "error_message": "access.denied_em"
            }""",
        )

    def make_grants_error_sid():
        return mockserver.make_response(
            status=403,
            content_type='application/json',
            response="""{
                "status": "error",
                "errors": [
                    {
                        "code": 403,
                        "message": "access.denied"
                    }
                ],
                "error_message": "access.denied_em"
            }""",
        )

    def make_ok():
        return mockserver.make_response(
            status=200,
            content_type='application/json',
            response='{\n  "status": "ok"}',
        )

    class Context:
        PASSPORT_CONSUMER = 'processing_fintech'
        SERVICE_SLUG = 'bank'

        def __init__(self):
            self.bind_phone = MockParams()
            self.subscribe_sid = MockParams()

            self.ip_address = None
            self.yuid = ''
            self.phone_number = ''
            self.old_phone_number = ''

    context = Context()

    @mockserver.json_handler(
        r'/account/(?P<yuid>\d+)/subscription/bank/', regex=True,
    )
    def _mock_subscribe_sid(request, yuid):
        assert context.yuid == yuid
        if context.subscribe_sid.first_fail:
            context.subscribe_sid.first_fail = False
            return make_error_subscribe_sid(500)
        if context.subscribe_sid.first_timeout:
            context.subscribe_sid.first_timeout = False
            raise mockserver.TimeoutError()
        if context.subscribe_sid.grants_problems:
            return make_grants_error_sid()
        if context.subscribe_sid.response_code != 200:
            return make_error_subscribe_sid(
                context.subscribe_sid.response_code,
            )
        assert request.method == 'POST'
        assert request.query == {'consumer': Context.PASSPORT_CONSUMER}
        return make_ok()

    @mockserver.json_handler(
        r'/account/(?P<yuid>\d+)/alias/bank_phonenumber/', regex=True,
    )
    def _mock_bind_phone(request, yuid):
        assert context.yuid == yuid
        if context.bind_phone.first_fail:
            context.bind_phone.first_fail = False
            return make_error_bind_phone(500)
        if context.bind_phone.first_timeout:
            context.bind_phone.first_timeout = False
            raise mockserver.TimeoutError()
        if context.bind_phone.grants_problems:
            return make_grants_error_phone()
        if context.bind_phone.response_code != 200:
            return make_error_bind_phone(context.bind_phone.response_code)

        if context.bind_phone.exists:
            return make_phone_exists()
        if context.bind_phone.not_available:
            return make_phone_not_available()
        assert (
            request.headers['Content-Type']
            == 'application/x-www-form-urlencoded'
        )

        assert request.headers['Ya-Consumer-Client-Ip'] == context.ip_address
        assert request.method in ['POST', 'DELETE']

        if request.method == 'POST':
            assert (
                request.get_data().decode()
                == 'phone_number=%2B' + context.phone_number[1:]
            )

        if request.method == 'DELETE':
            assert (
                request.get_data().decode()
                == 'phone_number=%2B' + context.old_phone_number[1:]
            )
        return make_ok()

    context.bind_phone.handler = _mock_bind_phone
    context.subscribe_sid.handler = _mock_subscribe_sid

    return context


@pytest.fixture(name='processing_mock')
async def _processing_mock(mockserver):
    class Context:
        UPDATE = 'update'
        TYPES = [
            'poll_result',
            'poll_digital_card_result',
            'update_buid_result',
            'application_status_result',
            'simplified_identification_application_status_result',
        ]

        def __init__(self):
            self.create_event = MockParams()

            self.buid = None
            self.application_id = None
            self.core_banking_request_id = None
            self.last_request_data = None
            self.received_events = []

    context = Context()

    @mockserver.json_handler('/processing/v1/bank/applications/create-event')
    def _mock_send_event_to_processing(request):
        if context.create_event.first_fail:
            context.create_event.first_fail = False
            return mockserver.make_response(status=500)
        if context.create_event.first_timeout:
            context.create_event.first_timeout = False
            raise mockserver.TimeoutError()
        data = request.json
        context.received_events.append(data)
        assert request.headers['Content-Type'] == 'application/json'
        assert request.query['item_id'] == context.application_id
        assert data['buid'] == context.buid
        assert data['kind'] == Context.UPDATE
        assert (
            data['core_banking_request_id'] == context.core_banking_request_id
            or data['core_banking_request_id'] is None
        )
        assert data['type'] in Context.TYPES
        return {}

    context.create_event.handler = _mock_send_event_to_processing

    return context


@pytest.fixture(name='core_applications_common_part_mock')
async def _core_applications_common_part_mock(mockserver):
    def make_error(error_code):
        if error_code != 500:
            return mockserver.make_response(
                status=error_code,
                json={
                    'code': error_code,
                    'message': 'problem in client_management',
                },
            )
        return mockserver.make_response(status=error_code)

    def create_application_common_part(request, context):
        if context.request_create.first_fail:
            context.request_create.first_fail = False
            return make_error(500)
        if context.request_create.first_timeout:
            context.request_create.first_timeout = False
            raise mockserver.TimeoutError()
        if context.request_create.response_code != 200:
            return make_error(context.request_create.response_code)

        assert request.headers['X-Idempotency-Token'] == context.application_id
        if context.request_create.errors_list:
            return {
                'request_id': context.core_banking_request_id,
                'status': context.application_status,
                'errors': [
                    {'code': '0', 'message': 'no errors'},
                    {'code': '1', 'message': 'but in lines'},
                ],
            }
        if context.request_create.empty_errors_list:
            return {
                'request_id': context.core_banking_request_id,
                'status': context.application_status,
                'errors': [],
                'error': {'code': '0', 'message': 'no errors'},
            }
        return {
            'request_id': context.core_banking_request_id,
            'status': context.application_status,
            'error': {'code': '0', 'message': 'no errors'},
        }

    class CommonHandlers:
        def __init__(self):
            self.common_create = None

    handlers = CommonHandlers()
    handlers.common_create = create_application_common_part
    return handlers


@pytest.fixture(name='core_client_mock')
async def _core_client_mock(mockserver, core_applications_common_part_mock):
    def make_error(error_code):
        if error_code != 500:
            message = 'problem in core_client'
            return mockserver.make_response(
                status=error_code,
                json={'code': error_code, 'message': message},
            )
        return mockserver.make_response(status=error_code)

    class Context:
        STATUS_PENDING = 'PENDING'

        def __init__(self):
            self.request_create = MockParams()
            self.request_upgrade = MockParams()
            self.kyc_request_upgrade = MockParams()
            self.agreement_get_by_request_id = MockParams()
            self.phone_update = MockParams()
            self.esia_put = MockParams()
            self.client_details_get = MockParams()

            self.phone_number = None
            self.core_banking_request_id = None
            self.application_id = None
            self.application_status = Context.STATUS_PENDING
            self.last_name = None
            self.first_name = None
            self.patronymic = None
            self.birth_date = None
            self.id_doc_number = None
            self.inn = None
            self.snils = None
            self.product = None
            self.is_error = None
            self.client_revision = None
            self.buid = None
            self.remote_ip = None
            self.session_uuid = None
            self.auth_level = None

            # kyc form fields
            self.sex = None
            self.birth_place_info = None
            self.id_doc_issued = None
            self.id_doc_issued_by = None
            self.id_doc_department_code = None
            self.address_registration = None
            self.address_actual = None

    context = Context()

    @mockserver.json_handler('/v1/client/phone/update')
    def _mock_phone_update(request):
        assert request.headers['X-Yandex-BUID'] == BUID
        assert request.headers['X-Idempotency-Token']
        assert request.json['phone_number'] == context.phone_number
        return mockserver.make_response(
            status=200,
            json={
                'status': context.application_status,
                'request_id': 'aa1234',
            },
        )

    @mockserver.json_handler('/v1/client/anonymous/create')
    def _mock_anonymous_create(request):
        assert request.headers['X-Remote-IP'] == common.IP
        assert request.headers['X-YaBank-SessionUUID'] == common.SESSION_UUID
        assert request.json['phone_number'] == context.phone_number
        if context.product is not None:
            assert request.json['product_code'] == context.product

        return core_applications_common_part_mock.common_create(
            request, context,
        )

    @mockserver.json_handler('/v1/agreement/get-by-request-id')
    def _mock_get_agreement_id_by_request_id(request):
        assert request.headers['X-Yandex-BUID'] == BUID
        assert request.query['request_id'] == context.core_banking_request_id
        return mockserver.make_response(
            status=context.agreement_get_by_request_id.response_code,
            json={'public_agreement_id': PUBLIC_AGREEMENT_ID},
        )

    @mockserver.json_handler('/v1/client/anonymous/upgrade')
    async def _mock_anonymous_upgrade(request):
        assert request.headers['X-Remote-IP'] == common.IP
        assert request.headers['X-YaBank-SessionUUID'] == common.SESSION_UUID
        if context.request_upgrade.response_code != 200:
            return make_error(context.request_upgrade.response_code)

        data = request.json
        assert data['last_name'] == context.last_name
        assert data['first_name'] == context.first_name
        assert data['patronymic'] == context.patronymic
        assert data['birth_date'] == context.birth_date
        assert data['id_doc_type'] == 'PASSPORT'
        assert data['id_doc_number'] == context.id_doc_number
        if context.inn is not None:
            assert data['inn'] == context.inn
        else:
            assert 'inn' not in data.keys()

        if context.snils is not None:
            assert data['snils'] == context.snils
        else:
            assert 'snils' not in data.keys()

        errors = list()
        errors.append({'code': '0', 'message': 'no errors'})
        if context.request_upgrade.errors_list:
            errors.append({'code': '1', 'message': 'but in lines'})

        if context.request_upgrade.first_fail:
            context.request_upgrade.first_fail = False
            return make_error(500)
        if context.request_upgrade.first_timeout:
            context.request_upgrade.first_timeout = False
            raise mockserver.TimeoutError()

        return {
            'request_id': context.core_banking_request_id,
            'status': context.application_status,
            'errors': errors,
        }

    @mockserver.json_handler('/v1/client/kyc/upgrade')
    async def _mock_kyc_upgrade(request):
        assert request.headers['X-Remote-IP'] == common.IP
        assert request.headers['X-YaBank-SessionUUID'] == common.SESSION_UUID
        if context.kyc_request_upgrade.response_code != 200:
            return make_error(context.kyc_request_upgrade.response_code)

        data = json.loads(request.get_data())
        assert data['last_name'] == context.last_name
        assert data['first_name'] == context.first_name
        assert data['sex'] == context.sex
        assert data['birth_date'] == context.birth_date
        assert data['birth_place_info'] == context.birth_place_info
        assert data['resident']
        assert data['id_doc_type'] == 'PASSPORT'
        assert data['id_doc_number'] == context.id_doc_number
        assert data['id_doc_issued'] == context.id_doc_issued
        assert data['id_doc_issued_by'] == context.id_doc_issued_by
        assert data['id_doc_department_code'] == context.id_doc_department_code
        assert data['address_registration'] == context.address_registration
        assert data['address_actual'] == context.address_actual
        assert data['inn'] == context.inn
        if context.snils is not None:
            assert data['snils'] == context.snils
        else:
            assert 'snils' not in data.keys()

        errors = list()
        errors.append({'code': '0', 'message': 'no errors'})
        if context.kyc_request_upgrade.errors_list:
            errors.append({'code': '1', 'message': 'but in lines'})

        if context.kyc_request_upgrade.first_fail:
            context.kyc_request_upgrade.first_fail = False
            return make_error(500)
        if context.kyc_request_upgrade.first_timeout:
            context.kyc_request_upgrade.first_timeout = False
            raise mockserver.TimeoutError()

        return {
            'request_id': context.core_banking_request_id,
            'status': context.application_status,
            'errors': errors,
        }

    @mockserver.json_handler('/v2/client/details/esia/put')
    async def _mock_esia_put(request):
        if context.esia_put.response_code != 200:
            return make_error(context.esia_put.response_code)

        data = json.loads(request.get_data())
        assert data['idempotency_token']
        assert data['buid']
        assert data['context']
        assert (
            data['context']['source_application_type']
            == 'SIMPLIFIED_IDENTIFICATION'
        )
        assert data['context']['source_type'] == 'ESIA_VERIFIED'
        assert data['auth_code']
        assert data['redirect_url']

        return {'data_revision': 1000_000_000_000}

    @mockserver.json_handler('/v2/client/details/get')
    async def _mock_client_details_get(request):
        if context.client_details_get.response_code != 200:
            return make_error(context.client_details_get.response_code)

        assert request.json['buid'] == context.buid
        assert request.json['context'] == {
            'ip_address': context.remote_ip,
            'session_id': context.session_uuid,
            'source_application_id': context.application_id,
            'source_application_type': 'PRODUCT',
        }

        return {
            'data_revision': context.client_revision,
            'details': {'auth_level': context.auth_level},
            'status': 'ACTIVE',
        }

    context.request_create.handler = _mock_anonymous_create
    context.request_upgrade.handler = _mock_anonymous_upgrade
    context.kyc_request_upgrade.handler = _mock_kyc_upgrade
    context.phone_update.handler = _mock_phone_update
    context.agreement_get_by_request_id.handler = (
        _mock_get_agreement_id_by_request_id
    )
    context.esia_put.handler = _mock_esia_put
    context.client_details_get.handler = _mock_client_details_get

    return context


@pytest.fixture(name='core_current_account_mock')
async def _core_current_account_mock(mockserver):
    class Context:
        def __init__(self):
            self.open_product = MockParams()
            self.request_upgrade = MockParams()
            self.agreement_get_by_request_id = MockParams()

            self.buid = None
            self.session_uuid = None
            self.remote_ip = None
            self.core_request_id = None
            self.product = None
            self.client_revision = None
            self.status = common.STATUS_PENDING

    context = Context()

    @mockserver.json_handler('/v1/current-account/open')
    def _mock_open_product(request):
        assert request.headers['X-Yandex-BUID'] == context.buid
        assert request.headers['X-YaBank-SessionUUID'] == context.session_uuid
        assert request.headers['X-Remote-IP'] == context.remote_ip
        assert request.headers['X-Idempotency-Token']
        assert request.json == {
            'auth_level': 'ANONYMOUS',
            'product_code': context.product,
            'client_revision': context.client_revision,
        }
        return mockserver.make_response(
            status=200,
            json={
                'status': context.status,
                'request_id': context.core_request_id,
            },
        )

    @mockserver.json_handler('/v1/current-account/upgrade')
    async def _mock_upgrade_esia(request):
        if context.request_upgrade.first_fail:
            context.request_upgrade.first_fail = False
            return mockserver.make_response(status=500)
        if context.request_upgrade.first_timeout:
            context.request_upgrade.first_timeout = False
            raise mockserver.TimeoutError()
        if context.request_upgrade.response_code != 200:
            return mockserver.make_response(
                status=context.request_upgrade.response_code,
                json={
                    'code': context.request_upgrade.response_code,
                    'message': 'problem in core-current-account',
                },
            )
        assert context.status in ['SUCCESS', 'FAILED', 'PENDING']
        assert request.headers['X-Idempotency-Token']
        assert request.headers['X-Yandex-BUID'] == common.BUID
        assert request.headers['X-Remote-IP'] == common.IP
        assert request.headers['X-YaBank-SessionUUID'] == common.SESSION_UUID

        data = request.json
        assert data['auth_level'] in [
            'ANONYMOUS',
            'IDENTIFIED',
            'KYC_EDS',
            'KYC',
        ]
        assert data['client_revision'] is not None
        return {
            'request_id': context.core_request_id,
            'status': context.status,
        }

    @mockserver.json_handler('/v1/agreement/get-by-request-id')
    def _mock_get_by_request_id(request):
        assert request.headers['X-Yandex-BUID'] == context.buid
        assert request.query == {'request_id': context.core_request_id}
        return mockserver.make_response(
            status=200, json={'public_agreement_id': PUBLIC_AGREEMENT_ID},
        )

    context.open_product.handler = _mock_open_product
    context.request_upgrade.handler = _mock_upgrade_esia
    context.agreement_get_by_request_id.handler = _mock_get_by_request_id

    return context


@pytest.fixture(name='userinfo_mock')
async def _userinfo_mock(mockserver):
    def make_error(error_code):
        if error_code != 500:
            message = 'problem in userinfo'
            if error_code == 409:
                message = 'phone already use'
            return mockserver.make_response(
                status=error_code,
                json={'code': error_code, 'message': message},
            )
        return mockserver.make_response(status=error_code)

    class Context:
        BUID_STATUS_FINAL = 'FINAL'

        def __init__(self):
            self.set_bank_phone = MockParams()
            self.get_buid_info = MockParams()
            self.get_info_by_phone = MockParams()
            self.update_buid_status = MockParams()
            self.get_phone_number = MockParams()
            self.get_phone_number_by_phone_id = MockParams()
            self.add_product = MockParams()
            self.get_antifraud_info = MockParams()
            self.get_latest_session = MockParams()

            self.buid = None
            self.yuid = None
            self.phone_number = None
            self.buid_status = Context.BUID_STATUS_FINAL
            self.product = None
            self.session_uuid = None

    context = Context()

    @mockserver.json_handler('/userinfo-internal/v1/get_info_by_phone')
    def _mock_get_info_by_phone(request):
        if context.get_info_by_phone.first_fail:
            context.get_info_by_phone.first_fail = False
            return make_error(500)
        if context.get_info_by_phone.first_timeout:
            context.get_info_by_phone.first_timeout = False
            raise mockserver.TimeoutError()
        if context.get_info_by_phone.response_code != 200:
            return make_error(context.get_info_by_phone.response_code)
        data = request.json

        if data['phone'] == '+71234567111':
            return mockserver.make_response(status=200, json={'uid': YUID})
        if data['phone'] == '+71234567112':
            return make_error(404)

        return make_error(505)

    @mockserver.json_handler('/userinfo-internal/v1/get_buid_info')
    def _mock_get_buid_info(request):
        if context.get_buid_info.first_fail:
            context.get_buid_info.first_fail = False
            return make_error(500)
        if context.get_buid_info.first_timeout:
            context.get_buid_info.first_timeout = False
            raise mockserver.TimeoutError()
        if context.get_buid_info.response_code != 200:
            return make_error(context.get_buid_info.response_code)
        data = request.json
        if data['buid'] == BUID:
            return mockserver.make_response(
                status=200,
                json={
                    'buid_info': {
                        'buid': context.buid,
                        'yandex_uid': context.yuid,
                        'phone_id': 'phone_id_sample',
                        'status': context.buid_status,
                    },
                },
            )
        return mockserver.make_response(
            status=404, json={'code': 'NotFound', 'message': 'buid not found'},
        )

    @mockserver.json_handler('/userinfo-internal/v1/get_phone_number')
    def _mock_get_phone_number(request):
        if context.get_phone_number.first_fail:
            context.get_phone_number.first_fail = False
            return make_error(500)
        if context.get_phone_number.first_timeout:
            context.get_phone_number.first_timeout = False
            raise mockserver.TimeoutError()
        if context.get_phone_number.response_code != 200:
            return make_error(context.get_phone_number.response_code)
        data = request.json
        if data['buid'] == BUID:
            return mockserver.make_response(
                status=200, json={'phone': '+71234567111'},
            )
        return mockserver.make_response(
            status=404, json={'code': 'NotFound', 'message': 'buid not found'},
        )

    @mockserver.json_handler('/userinfo-internal/v1/get_antifraud_info')
    def _mock_get_antifraud_info(request):
        if context.get_antifraud_info.first_fail:
            context.get_antifraud_info.first_fail = False
            return make_error(500)
        if context.get_antifraud_info.first_timeout:
            context.get_antifraud_info.first_timeout = False
            raise mockserver.TimeoutError()
        if context.get_antifraud_info.response_code != 200:
            return make_error(context.get_antifraud_info.response_code)
        data = request.json
        if data['session_uuid'] == context.session_uuid:
            return {
                'created_at': '',
                'updated_at': '',
                'antifraud_info': {'device_id': DEVICE_ID},
            }
        return mockserver.make_response(
            status=404,
            json={'code': 'NotFound', 'message': 'session_uuid not found'},
        )

    @mockserver.json_handler('/userinfo-internal/v1/get_latest_session')
    def _mock_get_latest_session(request):
        if context.get_latest_session.first_fail:
            context.get_latest_session.first_fail = False
            return make_error(500)
        if context.get_latest_session.first_timeout:
            context.get_latest_session.first_timeout = False
            raise mockserver.TimeoutError()
        if context.get_latest_session.response_code != 200:
            return make_error(context.get_latest_session.response_code)
        data = request.json
        if data['buid'] == context.buid:
            return {
                'session_uuid': '',
                'buid': '',
                'yandex_uid': YUID,
                'status': '',
                'created_at': '',
                'updated_at': '',
                'antifraud_info': {'device_id': DEVICE_ID},
            }
        return mockserver.make_response(
            status=404, json={'code': 'NotFound', 'message': 'buid not found'},
        )

    @mockserver.json_handler(
        '/userinfo-internal/v1/get_phone_number_by_phone_id',
    )
    def _mock_get_phone_number_by_phone_id(request):
        known_phone_id = {
            'phone_id_111': '+71234567111',
            'phone_id_112': '+71234567112',
            'BAD_PHONE_ID': 'BAD_NUMBER',
        }
        if context.get_phone_number_by_phone_id.first_fail:
            context.get_phone_number_by_phone_id.first_fail = False
            return make_error(500)
        if context.get_phone_number_by_phone_id.first_timeout:
            context.get_phone_number_by_phone_id.first_timeout = False
            raise mockserver.TimeoutError()
        if context.get_phone_number_by_phone_id.response_code != 200:
            return make_error(
                context.get_phone_number_by_phone_id.response_code,
            )
        data = request.json
        if data['phone_id'] in known_phone_id.keys():
            return mockserver.make_response(
                status=200,
                json={'phone': known_phone_id.get(data['phone_id'])},
            )
        return mockserver.make_response(
            status=404, json={'code': 'NotFound', 'message': 'buid not found'},
        )

    @mockserver.json_handler('/userinfo-internal/v1/set_bank_phone')
    def _mock_set_bank_phone(request):
        if context.set_bank_phone.first_fail:
            context.set_bank_phone.first_fail = False
            return make_error(500)
        if context.set_bank_phone.first_timeout:
            context.set_bank_phone.first_timeout = False
            raise mockserver.TimeoutError()
        if context.set_bank_phone.response_code != 200:
            return make_error(context.set_bank_phone.response_code)
        data = request.json
        assert data['buid'] == context.buid
        assert data['phone'] == context.phone_number
        return {}

    @mockserver.json_handler('/userinfo-internal/v1/update_buid_status')
    def _mock_update_buid_status(request):
        if context.update_buid_status.first_fail:
            context.update_buid_status.first_fail = False
            return make_error(500)
        if context.update_buid_status.first_timeout:
            context.update_buid_status.first_timeout = False
            raise mockserver.TimeoutError()
        if context.update_buid_status.response_code != 200:
            return make_error(context.update_buid_status.response_code)
        data = request.json
        assert data['buid'] == context.buid
        assert data['status'] == context.buid_status
        return {}

    @mockserver.json_handler('/userinfo-internal/v1/add_new_product')
    def _mock_add_product(request):
        if context.add_product.first_fail:
            context.add_product.first_fail = False
            return make_error(500)
        if context.add_product.first_timeout:
            context.add_product.first_timeout = False
            raise mockserver.TimeoutError()
        if context.add_product.response_code != 200:
            return make_error(context.add_product.response_code)
        assert request.json == {
            'buid': context.buid,
            'product': context.product,
            'agreement_id': PUBLIC_AGREEMENT_ID,
        }
        return {}

    context.get_phone_number_by_phone_id.handler = (
        _mock_get_phone_number_by_phone_id
    )
    context.get_phone_number.handler = _mock_get_phone_number
    context.get_info_by_phone.handler = _mock_get_info_by_phone
    context.get_buid_info.handler = _mock_get_buid_info
    context.set_bank_phone.handler = _mock_set_bank_phone
    context.update_buid_status.handler = _mock_update_buid_status
    context.add_product.handler = _mock_add_product
    context.get_antifraud_info.handler = _mock_get_antifraud_info
    context.get_latest_session.handler = _mock_get_latest_session

    return context


@pytest.fixture(name='applications_mock')
async def _applications_mock(mockserver):
    def make_error(error_code):
        if error_code != 500:
            return mockserver.make_response(
                status=error_code,
                json={
                    'code': error_code,
                    'message': 'problem in applications',
                },
            )
        return mockserver.make_response(status=error_code)

    class Context:
        STATUS_SUCCESS = 'SUCCESS'
        STATUS_FAILED = 'FAILED'
        buid_status = BUID_STATUS

        def __init__(self):
            self.create_plus_subscription = MockParams()
            self.set_status = MockParams()
            self.simpl_set_status = MockParams()
            self.kyc_set_status = MockParams()
            self.product_set_status = MockParams()
            self.get_application_data = MockParams()
            self.delete_personal_data = MockParams()
            self.simpl_get_application_data = MockParams()
            self.kyc_get_application_data = MockParams()
            self.set_core_request_id = MockParams()
            self.card_internal_create_app = MockParams()
            self.card_internal_submit = MockParams()
            self.simplified_internal_create_app = MockParams()
            self.reg_get_personal_data = MockParams()
            self.simplified_internal_submit_app = MockParams()
            self.simplified_esia_set_status = MockParams()

            self.buid = None
            self.yandex_uid = None
            self.application_id = None
            self.application_status = None
            self.phone_number = None
            self.old_phone_number = None
            self.core_banking_request_id = None
            self.received_events = []
            self.idempotency_token = None
            self.last_name = None
            self.first_name = None
            self.middle_name = None
            self.birthday = None
            self.passport_number = None
            self.inn = None
            self.snils = None
            self.remote_ip = None
            self.set_status_iterator = 0
            self.set_application_status = None
            self.session_uuid = None
            self.simpl_application_id = None
            self.product = None

            # kyc form fields
            self.sex = None
            self.birth_place_info = None
            self.id_doc_issued = None
            self.id_doc_issued_by = None
            self.id_doc_department_code = None
            self.address_registration = None
            self.address_actual = None

    context = Context()

    @mockserver.json_handler(
        '/applications-internal/v1/plus/create_application',
    )
    def _mock_plus_create_application(request):
        return {'application_id': 'plus_app_id'}

    @mockserver.json_handler(
        '/applications-internal/v1/'
        'simplified_identification/set_application_status',
    )
    def _mock_simpl_set_status(request):
        if context.simpl_set_status.first_fail:
            context.simpl_set_status.first_fail = False
            return make_error(500)
        if context.simpl_set_status.first_timeout:
            context.simpl_set_status.first_timeout = False
            raise mockserver.TimeoutError()
        if context.simpl_set_status.response_code != 200:
            return make_error(context.simpl_set_status.response_code)
        data = request.json
        context.received_events.append(data)
        assert data['application_id'] == context.application_id
        # pylint: disable=unsubscriptable-object
        assert (
            data['status']
            == context.set_application_status[context.set_status_iterator]
        )
        context.set_status_iterator += 1
        return {'result': 'ok'}

    @mockserver.json_handler(
        '/applications-internal/v1/'
        'simplified_identification/esia/set_application_status',
    )
    def _mock_simpl_esia_set_status(request):
        if context.simplified_esia_set_status.first_fail:
            context.simplified_esia_set_status.first_fail = False
            return make_error(500)
        if context.simplified_esia_set_status.first_timeout:
            context.simplified_esia_set_status.first_timeout = False
            raise mockserver.TimeoutError()
        if context.simplified_esia_set_status.response_code != 200:
            return make_error(context.simplified_esia_set_status.response_code)
        data = request.json
        context.received_events.append(data)
        assert data['yandex_buid'] == context.buid
        assert data['application_id'] == context.application_id
        # pylint: disable=unsubscriptable-object
        assert (
            data['status']
            == context.set_application_status[context.set_status_iterator]
        )
        context.set_status_iterator += 1
        return {'result': 'ok'}

    @mockserver.json_handler(
        '/applications-internal/v1/kyc/set_application_status',
    )
    def _mock_kyc_set_status(request):
        if context.kyc_set_status.first_fail:
            context.kyc_set_status.first_fail = False
            return make_error(500)
        if context.kyc_set_status.first_timeout:
            context.kyc_set_status.first_timeout = False
            raise mockserver.TimeoutError()
        if context.kyc_set_status.response_code != 200:
            return make_error(context.kyc_set_status.response_code)
        data = json.loads(request.get_data())
        context.received_events.append(data)
        assert data['application_id'] == context.application_id
        # pylint: disable=unsubscriptable-object
        assert (
            data['status']
            == context.set_application_status[context.set_status_iterator]
        )
        context.set_status_iterator += 1
        return {'result': 'ok'}

    @mockserver.json_handler(
        '/applications-internal/v1/set_application_status',
    )
    def _mock_set_status(request):
        if context.set_status.first_fail:
            context.set_status.first_fail = False
            return make_error(500)
        if context.set_status.first_timeout:
            context.set_status.first_timeout = False
            raise mockserver.TimeoutError()
        if context.set_status.response_code != 200:
            return make_error(context.set_status.response_code)
        data = request.json
        context.received_events.append(data)
        assert data['application_id'] == context.application_id
        return {'result': 'ok'}

    @mockserver.json_handler(
        '/applications-internal/v1/product/set_application_status',
    )
    def _mock_product_set_status(request):
        if context.set_status.first_fail:
            context.set_status.first_fail = False
            return make_error(500)
        if context.set_status.first_timeout:
            context.set_status.first_timeout = False
            raise mockserver.TimeoutError()
        if context.set_status.response_code != 200:
            return make_error(context.set_status.response_code)
        data = request.json
        context.received_events.append(data)
        assert data['application_id'] == context.application_id
        return {'result': 'ok'}

    @mockserver.json_handler('/applications-internal/v1/get_application_data')
    def _mock_get_application_data(request):
        if context.get_application_data.first_fail:
            context.get_application_data.first_fail = False
            return make_error(500)
        if context.get_application_data.first_timeout:
            context.get_application_data.first_timeout = False
            raise mockserver.TimeoutError()
        if context.get_application_data.response_code != 200:
            return make_error(context.get_application_data.response_code)
        data = request.json
        assert data['application_id'] == context.application_id
        body = {'form': {'phone': context.phone_number}}

        if context.last_name is not None:
            body['form']['last_name'] = context.last_name
        if context.first_name is not None:
            body['form']['first_name'] = context.first_name
        if context.middle_name is not None:
            body['form']['middle_name'] = context.middle_name
        if context.birthday is not None:
            body['form']['birthday'] = context.birthday
        if context.passport_number is not None:
            body['form']['passport_number'] = context.passport_number
        if context.inn is not None:
            body['form']['inn'] = context.inn
        if context.snils is not None:
            body['form']['snils'] = context.snils
        return body

    @mockserver.json_handler(
        '/applications-internal/v1/'
        'simplified_identification/get_application_data',
    )
    def _mock_simpl_get_application_data(request):
        if context.simpl_get_application_data.first_fail:
            context.simpl_get_application_data.first_fail = False
            return make_error(500)
        if context.simpl_get_application_data.first_timeout:
            context.simpl_get_application_data.first_timeout = False
            raise mockserver.TimeoutError()
        if context.simpl_get_application_data.response_code != 200:
            return make_error(context.simpl_get_application_data.response_code)
        data = request.json
        assert data['application_id'] == context.application_id
        body = {'form': {'phone': context.phone_number}}

        if context.last_name is not None:
            body['form']['last_name'] = context.last_name
        if context.first_name is not None:
            body['form']['first_name'] = context.first_name
        if context.middle_name is not None:
            body['form']['middle_name'] = context.middle_name
        if context.birthday is not None:
            body['form']['birthday'] = context.birthday
        if context.passport_number is not None:
            body['form']['passport_number'] = context.passport_number
        if context.inn is not None:
            body['form']['inn'] = context.inn
        if context.snils is not None:
            body['form']['snils'] = context.snils
        body['agreement_version'] = AGREEMENT_VERSION
        return body

    @mockserver.json_handler(
        '/applications-internal/v1/kyc/get_application_data',  # noqa
    )
    def _mock_kyc_get_application_data(request):
        if context.kyc_get_application_data.first_fail:
            context.kyc_get_application_data.first_fail = False
            return make_error(500)
        if context.kyc_get_application_data.first_timeout:
            context.kyc_get_application_data.first_timeout = False
            raise mockserver.TimeoutError()
        if context.kyc_get_application_data.response_code != 200:
            return make_error(context.kyc_get_application_data.response_code)
        data = json.loads(request.get_data())
        assert data['application_id'] == context.application_id
        body = {'form': {}}
        body['form']['last_name'] = context.last_name
        body['form']['first_name'] = context.first_name
        body['form']['patronymic'] = context.middle_name
        body['form']['sex'] = context.sex
        body['form']['birthday'] = context.birthday
        body['form']['birth_place_info'] = context.birth_place_info
        body['form']['id_doc_number'] = context.passport_number
        body['form']['id_doc_issued'] = context.id_doc_issued
        body['form']['id_doc_issued_by'] = context.id_doc_issued_by
        body['form']['id_doc_department_code'] = context.id_doc_department_code
        body['form']['address_registration'] = context.address_registration
        body['form']['address_actual'] = context.address_actual
        body['form']['inn'] = context.inn
        body['form']['snils'] = context.snils
        body['agreement_version'] = AGREEMENT_VERSION
        return body

    @mockserver.json_handler(
        '/applications-internal/v1/'
        r'(?P<application_type>(\w+\/)*)set_core_request_id',
        regex=True,
    )
    def _mock_set_core_request_id(request, application_type):
        if context.set_core_request_id.first_fail:
            context.set_core_request_id.first_fail = False
            return make_error(500)
        if context.set_core_request_id.first_timeout:
            context.set_core_request_id.first_timeout = False
            raise mockserver.TimeoutError()
        if context.set_core_request_id.response_code != 200:
            return make_error(context.set_core_request_id.response_code)
        data = request.json
        assert data['application_id'] == context.application_id
        assert data['core_request_id'] == context.core_banking_request_id
        return {}

    @mockserver.json_handler('/card-internal/v1/create_application')
    def _mock_card_internal_create_application(request):
        data = request.json
        assert data['buid'] == BUID
        assert request.headers['X-Idempotency-Token']
        context.idempotency_token = request.headers['X-Idempotency-Token']
        return mockserver.make_response(
            status=context.card_internal_create_app.response_code,
            json={'application_id': context.application_id},
        )

    @mockserver.json_handler('/card-internal/v1/submit')
    def _mock_card_internal_submit(request):
        data = request.json
        assert data['buid'] == BUID
        assert data['session_uuid'] == context.session_uuid
        assert data['yuid'] == context.yandex_uid
        if context.product is not None:
            assert data['product'] == context.product
        else:
            assert 'product' not in data
        assert request.headers['X-Idempotency-Token']
        if context.idempotency_token:
            # should be different from token in create_application to send
            # different events to procaas
            assert (
                context.idempotency_token
                != request.headers['X-Idempotency-Token']
            )
        return mockserver.make_response(
            status=context.card_internal_submit.response_code, json={},
        )

    @mockserver.json_handler(
        '/applications-internal/v1/'
        'simplified_identification/delete_personal_data',
    )
    def _mock_delete_personal_data(request):
        if context.delete_personal_data.first_fail:
            context.delete_personal_data.first_fail = False
            return make_error(500)
        if context.delete_personal_data.first_timeout:
            context.delete_personal_data.first_timeout = False
            raise mockserver.TimeoutError()
        if context.delete_personal_data.response_code != 200:
            return make_error(context.delete_personal_data.response_code)
        return mockserver.make_response(
            status=context.delete_personal_data.response_code, json={},
        )

    @mockserver.json_handler(
        '/applications-internal/v1/'
        'simplified_identification/create_application',
    )
    def _mock_simplified_internal_create_application(request):
        assert request.json == {
            'yandex_uid': YUID,
            'yandex_buid': BUID,
            'remote_ip': context.remote_ip,
            'locale': 'ru',
        }
        return mockserver.make_response(
            status=context.simplified_internal_create_app.response_code,
            json={'application_id': context.simpl_application_id},
        )

    @mockserver.json_handler(
        '/applications-internal/v1/simplified_identification/submit_form',
    )
    def _mock_simplified_internal_submit_form(request):
        assert request.json == {
            'application_id': context.simpl_application_id,
            'yandex_buid': BUID,
            'session_uuid': context.session_uuid,
            'remote_ip': context.remote_ip,
            'form': {
                'last_name': context.last_name,
                'first_name': context.first_name,
                'middle_name': context.middle_name,
                'passport_number': context.passport_number,
                'birthday': context.birthday,
                'inn_or_snils': context.inn,
            },
        }

        assert request.headers['X-Idempotency-Token']
        return mockserver.make_response(
            status=context.simplified_internal_submit_app.response_code,
            json={},
        )

    @mockserver.json_handler(
        '/applications-internal/v1/registration/get_personal_data',
    )
    def _mock_registration_internal_get_personal_data(request):
        assert request.json == {'yandex_uid': context.yandex_uid}

        return mockserver.make_response(
            status=context.reg_get_personal_data.response_code,
            json={
                'last_name': context.last_name,
                'first_name': context.first_name,
                'middle_name': context.middle_name,
                'passport_number': context.passport_number,
                'birthday': context.birthday,
                'inn_or_snils': context.inn,
            },
        )

    context.create_plus_subscription.handler = _mock_plus_create_application
    context.set_status.handler = _mock_set_status
    context.simpl_set_status.handler = _mock_simpl_set_status
    context.simplified_esia_set_status.handler = _mock_simpl_esia_set_status
    context.kyc_set_status.handler = _mock_kyc_set_status
    context.product_set_status.handler = _mock_product_set_status

    context.get_application_data.handler = _mock_get_application_data

    context.simpl_get_application_data.handler = (
        _mock_simpl_get_application_data
    )
    context.kyc_get_application_data.handler = _mock_kyc_get_application_data

    context.delete_personal_data.handler = _mock_delete_personal_data

    context.set_core_request_id.handler = _mock_set_core_request_id
    context.card_internal_create_app.handler = (
        _mock_card_internal_create_application
    )
    context.card_internal_submit.handler = _mock_card_internal_submit
    context.simplified_internal_create_app.handler = (
        _mock_simplified_internal_create_application
    )
    context.reg_get_personal_data.handler = (
        _mock_registration_internal_get_personal_data
    )
    context.simplified_internal_submit_app.handler = (
        _mock_simplified_internal_submit_form
    )

    return context


@pytest.fixture(name='core_card_mock')
async def _core_card_mock(mockserver, core_applications_common_part_mock):
    class Context:
        STATUS_PENDING = 'PENDING'

        def __init__(self):
            self.request_create = MockParams()

            self.core_banking_request_id = None
            self.application_id = None
            self.public_agreement_id = None
            self.application_status = Context.STATUS_PENDING

    context = Context()

    @mockserver.json_handler('/v1/card/issue')
    async def _mock_core_card_virtual_issue(request):
        data = request.json
        assert data['public_agreement_id'] == context.public_agreement_id
        assert data['card_type'] == CARD_TYPE
        return core_applications_common_part_mock.common_create(
            request, context,
        )

    context.request_create.handler = _mock_core_card_virtual_issue

    return context


@pytest.fixture(name='notifications_mock')
async def _notifications_mock(mockserver):
    class Context:
        def __init__(self):
            self.send_notification = MockParams()
            self.buid = None
            self.events = None
            self.consumer = None
            self.processing_notification_events = None
            self.defaults_groups = None
            self.defaults_groups_iterator = 0

    context = Context()

    @mockserver.json_handler('/notifications-internal/v1/send_events')
    def _mock_send_notification(request):

        if context.send_notification.first_fail:
            context.send_notification.first_fail = False
            return mockserver.make_response(status=500)
        if context.send_notification.first_timeout:
            context.send_notification.first_timeout = False
            raise mockserver.TimeoutError()
        assert request.headers['X-Idempotency-Token']

        data = request.json
        assert data['consumer'] == context.consumer
        assert data['buid'] == context.buid
        events = data['events']
        assert len(events) == 1
        assert (
            events[0]['defaults_group']
            == context.defaults_groups[  # pylint: disable=unsubscriptable-object # noqa: E501
                context.defaults_groups_iterator
            ]
        )
        context.defaults_groups_iterator += 1
        return {}

    context.send_notification.handler = _mock_send_notification

    return context


@pytest.fixture(name='agreements_mock')
async def _agreements_mock(mockserver):
    class Context:
        def __init__(self):
            self.accept_agreement = MockParams()

            self.agreement_title = None
            self.agreement_version = None
            self.buid = None
            self.yandex_uid = None

    context = Context()

    @mockserver.json_handler('/agreements-internal/v1/accept_agreement')
    def _mock_accept_agreement(request):
        if context.accept_agreement.first_fail:
            context.accept_agreement.first_fail = False
            return mockserver.make_response(
                status=500,
                content_type='application/json',
                response='{"status": "error",'
                '"code": 500, "message": "problem"}',
            )
        if context.accept_agreement.first_timeout:
            context.accept_agreement.first_timeout = False
            raise mockserver.TimeoutError()
        response_code = context.accept_agreement.response_code
        if response_code != 200:
            return mockserver.make_response(
                status=response_code,
                content_type='application/json',
                response='{"status": "error",'
                '"code": %s, "message": "problem"}' % response_code,
            )
        data = request.json
        if 'yandex_uid' in data:
            assert data['yandex_uid'] == context.yandex_uid
        assert data['buid'] == context.buid
        assert data['title'] == context.agreement_title
        assert data['version'] == context.agreement_version
        return {}

    context.accept_agreement.handler = _mock_accept_agreement

    return context


@pytest.fixture(name='risk_mock')
async def _risk_mock(mockserver):
    class Context:
        def __init__(self):
            self.phone_check = MockParams()
            self.phone_number = None
            self.application_id = None

    context = Context()

    @mockserver.json_handler('/risk/calculation/registration')
    def _mock_phone_check(request):
        assert request.json == {
            'idempotent_token': context.application_id,
            'user_features': [
                {
                    'class_name': 'phone',
                    'phone': {'number': context.phone_number},
                },
            ],
        }
        if context.phone_check.first_fail:
            context.phone_check.first_fail = False
            return mockserver.make_response(
                status=500,
                content_type='application/json',
                response='{"status": "error",'
                '"code": 500, "message": "problem"}',
            )
        if context.phone_check.first_timeout:
            context.phone_check.first_timeout = False
            raise mockserver.TimeoutError()
        response_code = context.phone_check.response_code
        if response_code != 200:
            return mockserver.make_response(
                status=response_code,
                content_type='application/json',
                response='{"status": "error",'
                '"code": %s, "message": "problem"}' % response_code,
            )
        if context.phone_check.access_deny:
            return {
                'resolution': 'DENY',
                'reason': [
                    'Phone analyzer: Failed Russian phone number verification',
                ],
                'reason_code': ['10.00.99'],
            }
        return {'resolution': 'ALLOW', 'reason': [], 'reason_code': []}

    context.phone_check.handler = _mock_phone_check

    return context
