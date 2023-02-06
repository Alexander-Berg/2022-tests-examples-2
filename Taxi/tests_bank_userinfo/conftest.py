import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401
from bank_userinfo_plugins import *  # noqa: F403 F401
from bank_testing.pg_state import (
    PgState,
    Arbitrary,
    DateTimeAsStr,
    JsonbAsDict,
)


try:
    import library.python.resource  # noqa: F401

    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False

if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_userinfo):
        levels = {
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
        }

        # Each log record is captured as a dictionary,
        # so we need to turn it back into a string
        def serialize_tskv(row):
            # these two will only lead to data duplication
            skip = {'timestamp', 'level'}

            # reorder keys so that 'text' is always in front
            keys = list(row.keys())
            keys.remove('text')
            keys.insert(0, 'text')

            return '\t'.join([f'{k}={row[k]}' for k in keys if k not in skip])

        async with taxi_bank_userinfo.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_userinfo._client._state_manager._state = (
                dataclasses.replace(
                    # pylint: disable=protected-access
                    taxi_bank_userinfo._client._state_manager._state,
                    caches_invalidated=False,
                )
            )

            @capture.subscribe()
            # pylint: disable=unused-variable
            def log(**row):
                logging.log(
                    levels.get(row['level'], logging.DEBUG),
                    serialize_tskv(row),
                )

            yield capture


@pytest.fixture
def bank_applications(mockserver):
    class Context:
        def __init__(self):
            self.get_processing_apps_handle = None
            self.get_applications_handle = None
            self.delete_application_handle = None
            self.delete_passport_bank_phone = None
            self.http_status_code = 200
            self.response = {'applications': []}

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_applications(self, applications):
            self.response = {'applications': applications}

    context = Context()

    @mockserver.json_handler(
        '/bank-applications'
        '/applications-internal/v1/get_processing_applications',
    )
    def _get_processing_applications(request):
        assert request.method == 'POST'
        if context.http_status_code == 200:
            uid = request.json.get('uid')
            buid = request.json.get('buid')
            assert uid or buid
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    @mockserver.json_handler(
        '/bank-applications/applications-internal/v1/get_applications',
    )
    def _get_applications(request):
        assert request.method == 'POST'
        return {
            'applications': [
                {
                    'application_id': '681e86ff-b9c2-4494-a403-e82147529979',
                    'type': 'REGISTRATION',
                    'status': 'SUCCESS',
                    'operation_type': 'UPDATE',
                    'operation_at': '2021-10-31T00:01:00.0+00:00',
                },
            ],
        }

    @mockserver.json_handler(
        '/bank-applications/applications-internal/v1/delete_application',
    )
    def _delete_application(request):
        assert request.method == 'POST'
        return {}

    @mockserver.json_handler(
        '/bank-applications'
        '/applications-internal/v1/delete_passport_bank_phone',
    )
    def _delete_passport_bank_phone(request):
        assert request.method == 'POST'
        assert request.headers['X-Remote-IP'] != ''
        return {'status': 'SUCCESS'}

    context.get_processing_apps_handle = _get_processing_applications
    context.get_applications_handle = _get_applications
    context.delete_application_handle = _delete_application
    context.delete_passport_bank_phone = _delete_passport_bank_phone
    return context


@pytest.fixture(autouse=True)
def bank_risk(mockserver):
    class Context:
        def __init__(self):
            self.risk_calculation_handler = None
            self.http_status_code = 200
            self.response = {
                'resolution': 'ALLOW',
                'action': [],
                'af_decision_id': 'af_decision_id',
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response(self, resolution, actions):
            self.response = {
                'resolution': resolution,
                'action': actions,
                'af_decision_id': 'af_decision_id',
            }

    context = Context()

    @mockserver.json_handler('/bank-risk/risk/calculation/start_session')
    def _risk_calculation_handler(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.risk_calculation_handler = _risk_calculation_handler

    return context


@pytest.fixture(autouse=True)
def bank_core_client(mockserver):
    class Context:
        def __init__(self):
            self.client_deactivate_handler = None
            self.request_check_handler = None

    context = Context()

    @mockserver.json_handler('/bank-core-client/v1/client/deactivate')
    def _client_deactivate(request):
        assert request.method == 'POST'
        return {
            'status': 'PENDING',
            'request_id': '1ab7f45d-492f-41cd-bfe8-3611eb65ef80',
        }

    @mockserver.json_handler('/bank-core-client/v1/client/request/check')
    def _request_check(request):
        assert request.method == 'POST'
        return {
            'status': 'SUCCESS',
            'request_id': '1ab7f45d-492f-41cd-bfe8-3611eb65ef80',
        }

    context.client_deactivate_handler = _client_deactivate
    context.request_check_handler = _request_check

    return context


@pytest.fixture()
def bank_authorization(mockserver, mocked_time):
    class Context:
        def __init__(self):
            self.create_track_handler = None
            self.http_status_code = 200
            self.response_create_track = {'track_id': 'default_track_id'}

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response_create_track(self, new_response):
            self.response_create_track = new_response

    context = Context()

    @mockserver.json_handler(
        '/bank-authorization/authorization-internal/v1/create_track',
    )
    def _create_track_handler(request):
        assert request.method == 'POST'
        assert request.json.get('antifraud_context_id')
        return mockserver.make_response(
            status=context.http_status_code,
            json=context.response_create_track,
        )

    context.create_track_handler = _create_track_handler

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
        decision = (
            'PERMIT'
            if request.json['subject_attributes']['jwt'] == 'allow'
            else 'DENY'
        )
        user_login = (
            'support_login'
            if request.json['subject_attributes']['jwt'] == 'allow'
            else None
        )
        return mockserver.make_response(
            status=context.http_status_code,
            json={'decision': decision, 'user_login': user_login},
        )

    context.apply_policies_handler = _apply_policies_handler
    return context


@pytest.fixture
def bank_userinfo(mockserver):
    class Context:
        def __init__(self):
            self.delete_user_handler = None

    context = Context()

    @mockserver.json_handler('/bank-userinfo/userinfo-internal/v1/delete_user')
    def _delete_user_handler(request):
        assert request.method == 'POST'
        return {}

    context.delete_user_handler = _delete_user_handler
    return context


@pytest.fixture
def db(pgsql):
    db = PgState(pgsql, 'bank_userinfo')
    return db


@pytest.fixture
def db_sessions(db):
    db.add_table(
        'bank_userinfo.sessions',
        'id',
        [
            'id',
            'yandex_uid',
            'phone_id',
            'bank_uid',
            'antifraud_info',
            'status',
            'old_session_id',
            'created_at',
            'updated_at',
            'authorization_track_id',
            'app_vars',
            'locale',
            'pin_token_id',
            'deleted_at',
            'cursor_key',
        ],
        alias='sessions',
        defaults={'cursor_key': Arbitrary()},
        converters={
            'antifraud_info': JsonbAsDict(),
            'created_at': DateTimeAsStr(),
            'updated_at': DateTimeAsStr(),
            'deleted_at': DateTimeAsStr(),
        },
    )
