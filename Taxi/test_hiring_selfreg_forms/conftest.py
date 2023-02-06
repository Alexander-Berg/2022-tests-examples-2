# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import functools
import json

import pytest

from taxi.pytest_plugins import core
import taxi.util.dates

import hiring_selfreg_forms.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from hiring_selfreg_forms.internal import tools

pytest_plugins = ['hiring_selfreg_forms.generated.service.pytest_plugins']

ResponseType = core.Response

ROUTE_EDA_EXPERIMENT_PRO_WEB = '/v1/eda/experiment/pro-web'
ROUTE_EDA_FORM_DATA = '/v1/eda/form/data'
ROUTE_EDA_FORM_SUBMIT = '/v1/eda/form/submit'
ROUTE_EDA_FORM_USE_KIOSK = '/v1/eda/form/use-kiosk'
ROUTE_EDA_VACANCY_CHOOSE = '/v1/eda/vacancy/choose'
ROUTE_INTERNAL_EDA_VACANCY_CHOOSE = '/internal/v1/eda/vacancy/choose'
ROUTE_PHONE_CHECK = '/v1/auth/phone/check'
ROUTE_PHONE_SUBMIT = '/v1/auth/phone/submit'

X_REAL_IP_KEY = 'X-Real-Ip'
X_REMOTE_IP_KEY = 'X-Remote-IP'
X_FORM_USER_IP_KEY = 'X-Form-User-IP'
X_USE_KIOSK_IP_KEY = 'X-Use-Kiosk-IP'
YA_CONSUMER_CLIENT_IP = 'Ya-Consumer-Client-Ip'
USER_IP = '127.0.0.1'
INVALID_PHONES = {'+78921000000'}
SMS_LIMIT_EXCEEDED = {'+78921000001'}

DEFAULT_PHONE_PHONE_ID_PAIR = (
    '+79210000000',
    'aaaaaaaabbbb4cccddddeeeeeeeeeeee',
)
DEFAULT_EXTERNAL_ID = '78fdabf83a0940d0b199768689b3ae44'
DEFAULT_FORM_COMPLETION_ID = '61fdabf83a0940d0b199768689b3ae32'
DEFAULT_TICKET_ID = 1
DEFAULT_LEAD_ID = '12'


def generate_code(phone):
    """Mock code generation -- last six symbols of phone"""
    return phone[-6:]


@pytest.fixture  # noqa: F405
def personal(mockserver):
    phones_storage = {
        'store': {
            DEFAULT_PHONE_PHONE_ID_PAIR[0]: DEFAULT_PHONE_PHONE_ID_PAIR[1],
        },
        'retrieve': {
            DEFAULT_PHONE_PHONE_ID_PAIR[1]: DEFAULT_PHONE_PHONE_ID_PAIR[0],
        },
    }

    def generate_id(string):
        if string in phones_storage['store']:
            return phones_storage['store'][string]
        id_ = tools.hex_uuid()
        phones_storage['store'][string] = id_
        phones_storage['retrieve'][id_] = string
        return generate_id(string)

    def _store(request):
        type_ = 'value'
        value = request.json[type_]
        id_ = generate_id(value)
        response = {'id': id_, type_: value}
        return response

    def _retrieve(request):
        id_ = request.json['id']
        type_ = 'value'
        try:
            value = phones_storage['retrieve'][id_]
        except KeyError:
            response = {'code': '404', 'message': 'Doc not found in mongo'}
        else:
            response = {'id': id_, type_: value}
        return response

    @mockserver.json_handler('/personal/v1/phones/store')
    def phones_store(request):  # pylint: disable=W0612
        return _store(request)

    @mockserver.json_handler('/personal/v1/emails/store')
    def emails_store(request):  # pylint: disable=W0612
        return _store(request)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def phones_retrieve(request):  # pylint: disable=W0612
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def emails_retrieve(request):  # pylint: disable=W0612
        return _retrieve(request)


@pytest.fixture  # noqa: F405
def hiring_api(mockserver):
    storage = []

    class Context:
        @staticmethod
        @mockserver.json_handler(
            '/hiring-api/v1/tickets/create',
        )  # pylint: disable=W0612
        def create(request):
            return Context._build_response(request)

        @staticmethod
        @mockserver.json_handler(
            '/hiring-api/v1/tickets/update',
        )  # pylint: disable=W0612
        def update(request):
            return Context._build_response(request)

        @staticmethod
        def _build_response(request):
            request_data = request.json
            status = 200
            if request_data in storage:
                data = {
                    'code': 'DUPLICATED',
                    'message': 'Данные уже присутствуют в CRM',
                    'details': {
                        'occurred_at': str(taxi.util.dates.utcnow()),
                        'errors': [],
                    },
                }
                status = 409
            else:
                data = {
                    'code': 'SUCCESS',
                    'message': 'Данные приняты.',
                    'details': {'accepted_fields': ['phone', 'name']},
                }
            storage.append(request_data)
            response = mockserver.make_response(status=status, json=data)
            return response

    return Context()


@pytest.fixture  # noqa: F405
def hiring_api_create(mockserver):
    def create(response):
        @mockserver.json_handler('/hiring-api/v1/tickets/create')
        def _wrapper(request):
            return response

        return _wrapper

    return create


@pytest.fixture  # noqa: F405
def infranaim_api(mockserver):
    storage = []

    class Context:
        @staticmethod
        @mockserver.json_handler(
            '/infranaim-api/api/v1/submit/selfreg-forms',
        )  # pylint: disable=W0612
        def post_submit(request):
            return Context._build_response(request)

        @staticmethod
        @mockserver.json_handler(
            '/infranaim-api/api/v1/update/selfreg-forms',
        )  # pylint: disable=W0612
        def post_update(request):
            return Context._build_response(request)

        @staticmethod
        def _build_response(request):
            assert request.headers['token'] == 'TOKEN_HIRING_SELFREG_FORMS'
            request_data = request.json
            if request_data in storage:
                data = {
                    'code': 409,
                    'message': 'Conflict',
                    'details': 'Duplicated',
                }
            else:
                data = {
                    'code': 200,
                    'message': 'Success',
                    'details': 'Survey added',
                }
            storage.append(request_data)
            response = mockserver.make_response(status=data['code'], json=data)
            return response

    return Context()


@pytest.fixture  # noqa: F405
def hiring_trigger_zend(mockserver, load_json):
    @mockserver.json_handler(
        '/hiring-trigger-zend/v1/data/manage-supply',
    )  # pylint: disable=W0612
    def func(request):
        data = load_json('hiring-trigger-zend_response.json')
        return data


@pytest.fixture  # noqa: F405
def eda_core(mockserver, load_json):
    @mockserver.json_handler(
        '/eda_core/api/v1/general-information/regions',
    )  # pylint: disable=W0612
    def regions(_):
        data = load_json('eda_core_response.json')['regions']
        return data

    @mockserver.json_handler(
        '/eda_core/api/v1/general-information/countries',
    )  # pylint: disable=W0612
    def countries(_):
        data = load_json('eda_core_response.json')['countries']
        return data


@pytest.fixture  # noqa: F405
def passport_internal(mockserver):
    storage = {}

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )  # pylint: disable=W0612
    def submit(request):
        data = request.form
        headers = request.headers
        assert headers.get(YA_CONSUMER_CLIENT_IP) == USER_IP
        track_id = tools.hex_uuid()
        phone = data['number']
        if phone in INVALID_PHONES:
            return {'status': 'error', 'errors': ['number.invalid']}
        if phone in SMS_LIMIT_EXCEEDED:
            return {'status': 'error', 'errors': ['sms_limit.exceeded']}
        code = generate_code(phone)
        response = {'status': 'ok', 'track_id': track_id}
        storage[track_id] = {'phone': phone, 'code': code}
        return response

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )  # pylint: disable=W0612
    def commit(request):
        data = request.form
        headers = request.headers
        assert headers.get(YA_CONSUMER_CLIENT_IP) == USER_IP
        code = data['code']
        track_id = data['track_id']
        if track_id not in storage:
            response = {'status': 'error', 'errors': ['track.not_found']}
        elif storage[track_id]['code'] != code:
            response = {'status': 'error', 'errors': ['code.invalid']}
        else:
            response = {
                'status': 'ok',
                'number': {'original': storage[track_id]['phone']},
            }
        return response

    return submit, commit


@pytest.fixture
def stq_mock(mockserver):
    @mockserver.json_handler(
        '/stq-agent/queues/api/add/hiring_selfreg_forms_publish',
    )
    async def _wrapper(*args, **kwargs):
        request = args[0].json
        info = _wrapper.calls_data
        info.append(request)
        return {}

    _wrapper.calls_data = []
    return _wrapper


@pytest.fixture  # noqa: F405
def perform_auth(make_request):
    async def func(phone='+79210000000', id_=None):
        id_ = id_ or tools.hex_uuid()
        data = {'form_completion_id': id_, 'phone': phone}
        await make_request(ROUTE_PHONE_SUBMIT, data=data)
        code = generate_code(phone)
        data = {'form_completion_id': id_, 'code': code}
        await make_request(ROUTE_PHONE_CHECK, data=data)
        return id_

    return func


@pytest.fixture  # noqa: F405
def make_request(taxi_hiring_selfreg_forms_web):
    async def func(
            route,
            *,
            method='post',
            data=None,
            params=None,
            status_code=200,
            headers=None,
            set_x_real_ip=True,
    ):
        response: ResponseType
        method = getattr(taxi_hiring_selfreg_forms_web, method)
        headers = headers or {}
        if set_x_real_ip:
            headers[X_REAL_IP_KEY] = USER_IP
        headers['User-Agent'] = 'user-agent'
        response = await method(
            route, json=data, params=params, headers=headers,
        )
        assert response.status == status_code
        return await response.json()

    return func


@pytest.fixture  # noqa: F405
def set_ticket_id(pgsql, load):
    db = pgsql['hiring_misc']
    query_template = load('set_ticket_id.sql')

    def _do_it(form_completion_id, ticket_id):
        cursor = db.cursor()
        query = query_template.format(
            form_completion_id=form_completion_id, ticket_id=str(ticket_id),
        )
        cursor.execute(query)
        row = cursor.fetchone()
        return row

    return _do_it


@pytest.fixture  # noqa: F405
def fill_form_data(pgsql, load):
    db = pgsql['hiring_misc']
    query_template = load('fill_form_data.sql')

    def _do_it(form_completion_id, form_data):
        cursor = db.cursor()
        query = query_template.format(
            form_completion_id=form_completion_id,
            form_data=json.dumps(form_data),
        )
        cursor.execute(query)
        row = cursor.fetchone()
        return row

    return _do_it


@pytest.fixture  # noqa: F405
async def insert_auth_zeros(perform_auth):
    id_ = '00000000000000000000000000000000'
    await perform_auth(id_=id_)


def main_configuration(func):
    @pytest.mark.config(  # noqa: F405
        TVM_RULES=[
            {'src': 'hiring-selfreg-forms', 'dst': 'personal'},
            {'src': 'hiring-selfreg-forms', 'dst': 'passport-internal'},
            {'src': 'hiring-selfreg-forms', 'dst': 'stq-agent'},
            {'src': 'hiring-selfreg-forms', 'dst': 'hiring-candidates'},
        ],
    )
    @pytest.mark.usefixtures(  # noqa: F405
        'eda_core',
        'personal',
        'passport_internal',
        'hiring_api',
        'infranaim_api',
        'hiring_trigger_zend',
        'insert_auth_zeros',
        'pgsql',
    )
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched
