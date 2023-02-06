import pytest

from hiring_selfreg_forms.internal import constants
from hiring_selfreg_forms.internal import tools
from test_hiring_selfreg_forms import conftest


@pytest.mark.config(
    HIRING_SELFREG_FORMS_ALLOWED_FIELDS=[
        {
            'fields': ['user_login_creator', 'utm_campaign'],
            'uri': '/v1/auth/phone/check',
        },
    ],
)
@pytest.mark.parametrize(
    'with_zendesk_ticket_id, ticket_exists',
    [(True, True), (True, False), (False, True), (False, False)],
)
@conftest.main_configuration
async def test_auth_phone(
        make_request, stq_mock, with_zendesk_ticket_id, ticket_exists,
):
    phone = '+79210000000'
    not_valid_code = '111111'
    valid_code = conftest.generate_code(phone)
    id_ = tools.hex_uuid()
    data = {'form_completion_id': id_, 'phone': phone}
    await make_request(conftest.ROUTE_PHONE_SUBMIT, data=data, status_code=200)

    # Check idempotency
    await make_request(conftest.ROUTE_PHONE_SUBMIT, data=data, status_code=200)

    data = {'form_completion_id': id_, 'code': not_valid_code}
    await make_request(conftest.ROUTE_PHONE_CHECK, data=data, status_code=401)
    assert not stq_mock.calls_data

    data = {
        'form_completion_id': id_,
        'code': valid_code,
        'data': [
            {'id': 'user_login_creator', 'value': 'test1'},
            {'id': 'utm_campaign', 'value': 'test2'},
        ],
    }
    if with_zendesk_ticket_id:
        if ticket_exists:
            data['zendesk_ticket_id'] = 100000
        else:
            data['zendesk_ticket_id'] = 100001

    await make_request(conftest.ROUTE_PHONE_CHECK, data=data, status_code=200)
    assert len(stq_mock.calls_data) == 1

    if with_zendesk_ticket_id and ticket_exists:
        assert not stq_mock.calls_data[0]['kwargs']['create']
    else:
        assert stq_mock.calls_data[0]['kwargs']['create']
    ticket_data = stq_mock.calls_data[0]['kwargs']['ticket_data']
    assert constants.FIELD_EXTERNAL_ID in ticket_data
    assert ticket_data[constants.FIELD_PHONE] == '+79210000000'
    assert ticket_data['user_login_creator'] == 'test1'
    assert ticket_data['utm_campaign'] == 'test2'


@conftest.main_configuration
async def test_auth_phone_missed_form(make_request):
    phone = '+79210000000'
    id_ = tools.hex_uuid()
    data = {'form_completion_id': id_, 'code': conftest.generate_code(phone)}
    await make_request(conftest.ROUTE_PHONE_CHECK, data=data, status_code=401)


@conftest.main_configuration
@pytest.mark.parametrize(
    'phone, error, status',
    [
        ('+78921000000', constants.CODE_INVALID_PHONE, 400),
        ('+78921000001', constants.CODE_SMS_LIMIT_EXCEEDED, 429),
    ],
)
async def test_auth_phone_errors(make_request, phone, error, status):
    id_ = tools.hex_uuid()
    data = {'form_completion_id': id_, 'phone': phone}
    data = await make_request(
        conftest.ROUTE_PHONE_SUBMIT, data=data, status_code=status,
    )
    assert data['code'] == error


@pytest.mark.parametrize('x_form_user_ip', [True, False])
@conftest.main_configuration
async def test_user_ip_source(taxi_hiring_selfreg_forms_web, x_form_user_ip):
    phone = '+79210000000'
    if x_form_user_ip:
        headers = {
            'X-Real-Ip': '127.0.0.2',
            'X-Form-User-IP': conftest.USER_IP,
        }
    else:
        headers = {'X-Real-Ip': conftest.USER_IP}
    id_ = tools.hex_uuid()
    data = {'form_completion_id': id_, 'phone': phone}
    response = await taxi_hiring_selfreg_forms_web.post(
        conftest.ROUTE_PHONE_SUBMIT, json=data, headers=headers,
    )
    assert response.status == 200


@pytest.mark.config(
    HIRING_SELFREG_FORMS_USE_RETENTION=True,
    TVM_RULES=[
        {'src': 'hiring-selfreg-forms', 'dst': 'personal'},
        {'src': 'hiring-selfreg-forms', 'dst': 'passport-internal'},
        {'src': 'hiring-selfreg-forms', 'dst': 'stq-agent'},
    ],
)
@pytest.mark.usefixtures('personal', 'passport_internal')
@pytest.mark.parametrize(
    ('phone', 'expected_status', 'expected_response'),
    [
        ('+79210000000', 200, {'message': 'OK', 'success': True}),
        (
            '+79210000001',
            403,
            {'message': 'retention failed', 'success': False},
        ),
    ],
)
async def test_auth_phone_retention_failed(
        mockserver,
        make_request,
        stq_mock,
        phone,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/hiring-candidates-py3/v1/eda/selfreg-retention')
    def selfreg_retention(request):  # pylint: disable=W0612
        if phone == '+79210000000':
            return {
                'ticket_data': {},
                'retention_success': True,
                'retention_message': '',
            }
        return {
            'ticket_data': {},
            'retention_success': False,
            'retention_message': 'retention failed',
        }

    id_ = tools.hex_uuid()
    data = {'form_completion_id': id_, 'phone': phone}
    await make_request(conftest.ROUTE_PHONE_SUBMIT, data=data, status_code=200)
    data = {'form_completion_id': id_, 'code': conftest.generate_code(phone)}
    response = await make_request(
        conftest.ROUTE_PHONE_CHECK, data=data, status_code=expected_status,
    )
    assert response == expected_response, response
    assert len(stq_mock.calls_data) == (1 if expected_status == 200 else 0)


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'hiring-selfreg-forms', 'dst': 'personal'},
        {'src': 'hiring-selfreg-forms', 'dst': 'passport-internal'},
        {'src': 'hiring-selfreg-forms', 'dst': 'stq-agent'},
    ],
    HIRING_SELFREG_FORMS_SOURCE_ROUTE_MAPPING={
        '__default__': 'eda',
        'test_source': 'taxi',
    },
)
@pytest.mark.usefixtures('personal')
@pytest.mark.parametrize(
    ('source', 'expected_route'),
    [('test_source', 'taxi'), ('other_source', 'eda')],
)
async def test_auth_phone_route(
        make_request, passport_internal, source, expected_route,
):
    id_ = tools.hex_uuid()
    phone = '+79210000000'
    submit, _ = passport_internal
    data = {
        'form_completion_id': id_,
        'phone': phone,
        'data': [{'id': 'source', 'value': source}],
    }
    await make_request(conftest.ROUTE_PHONE_SUBMIT, data=data, status_code=200)
    assert submit.has_calls
    submit_call = submit.next_call()
    submit_request = submit_call['request']
    submit_data = submit_request.get_data().decode()
    assert f'route={expected_route}' in submit_data
