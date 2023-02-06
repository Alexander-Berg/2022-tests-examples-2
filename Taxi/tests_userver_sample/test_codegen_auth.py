import json

import pytest


# Generated via `tvmknife unittest service -s 2001716 -d 2001716`
USERVER_SAMPLE_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggItJZ6E'
    'LSWeg:FeioYuB3kuByOMR5TC3Fz2aswcgUsBcYGFtjC'
    '-HolyAAcTL4_fRg-G7PhL-2rezhvamBQ'
    'kzTtouKN9F8PMGRyu-NtZGHLCoKn-pl12FbaAgiYhwz'
    'TTL-9f-N78hXBoAoBN9rHj-euFaQiAYi'
    '-E3hCspYEYvt4FisZnXUirWF0ak'
)

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:F'
    'ZL4lLvnBYAXMBlHXC8_vYrZUEtjEKj1xctj1hIz'
    'hkZtefwJqns1G0JkUC99mrWgjRQi4IPp2XEQ'
    'bJy2MBzNV0MFu582x3aj2pENfuRBGuCKpXNcnhy'
    'cwuiy4FGmq09xVhNEsLcbxGIOm1sET7tDmAp'
    '4XkK0RB91-wxH0vSS46g'
)

# Generated via:
# tvmknife unittest user -d 42 -e test_yateam --scopes read
USER_TICKET_READ = (
    '3:user:CA4Q__________9_GhQKAggqECoaBH'
    'JlYWQg0oXYzAQoAw:GP7exvbGHYkvuYTETXRiZ'
    'IFecUhiVKtip-L3yASSiDw_NONbwYDoZ760o1'
    'WPxQxT_xKoIRfdZGvzW4Jop2aa15SazwLfLPZR'
    's5dOlXvn3auJYc5L6t_2ffm9m43fr5RcqAi9_'
    'ovYzwOqxVZYNP57daC6BRgwMYju7DrOhHhuFo0'
)

# Generated via:
# tvmknife unittest user -d 42 -e test_yateam --scopes read,write
USER_TICKET_RW = (
    '3:user:CA4Q__________9_GhsKAggqECoaBH'
    'JlYWQaBXdyaXRlINKF2MwEKAM:FmLcx6glId9f'
    'VYjhFTD69vUVDyMcawZ0z7En9Q0g6fsioFNEq'
    'dMhvEyx4bl25SFWFjjVnGBs-pPOpPWsqC4JmHV'
    'STH8lFgoAqeOb5B3D5g1t20V0NwxuAU9EIzkQ'
    'eE8a6cMbi4r6-lvAkUZZmefXbMvQddk_r1pHBg'
    'S--V-qAU4'
)

# Generated via:
# tvmknife unittest user -d 123321 -e prod --scopes read,write
USER_TICKET_PROD = (
    '3:user:CAsQ__________9_Gh8KBAi5wwcQucMHGgRyZWFkGgV3cml0ZSDShdjMBCgA:JoJm'
    'raRBV54urv_iDRIkCSZsQJbSKiWpUokDvjfMd4i9D9yry6ldCv-g25SrAjpr7T4LQcXtbpb5'
    '8zSQ1ynf81uhWUp9qkBd7mj34dllkh6TtUE4huvVS95E4E5vP_bz2xchqQAEOkwg4et_mTMJ'
    'rDj8kiEylKyFcCiH60XIYJQ'
)

# Generated via:
# tvmknife unittest user -d 123321 -e prod_yateam --scopes read,write
USER_TICKET_PROD_YATEAM = (
    '3:user:CAwQ__________9_Gh8KBAi5wwcQucMHGgRyZWFkGgV3cml0ZSDShdjMBCgC:Kzcw'
    'wx9Cypl0w1RJKMm7Fa2z48LtBwg1UcDhbG6c5ET_hQ5m7Z89Y9GGB3Gmzu6sDGF_yV802bBM'
    '-feekrGsXVijYLbH291k2RK2TIGzioweiGF92vVHV1MTWWitJxHFvDB2UnYwP823YhjeyQ7_'
    '-xqjupaRyiO7jdT0slLBFPY'
)

# Generated via:
# tvmknife unittest user -d 42 -e test_yateam --scopes bb:sessionid
USER_TICKET_NON_YATEAM_SESSIONID = (
    '3:user:CA4Q__________9_GhwKAggqECoaDGJiOnNlc3Npb25pZCDShdjMBCgD:GSkVDci9'
    '09'
    'g4EiazWRtmSXyZj9Mcds1kUBVK6jGBaRm6Z4v2j9lpjRXOIl_lXDVmv8qbwPO3OgN1tnwyGt'
    'R1Tn3R7D73e12G1mG7Gs7ZHcCiQYhKRl6OVugtidaYS9oUTPQzqqo5hin1__VeNB6b18RhL3'
    'oIG_m9gsod8dMfADc'
)

DEFAULT_ERROR_CONTENT_TYPE = 'application/json; charset=utf-8'


@pytest.mark.config(TVM_ENABLED=True)
async def test_autogen_service_tvm_disabled(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/tvm-service')
    assert response.status_code == 200
    assert response.content == b'{}'


@pytest.mark.config(TVM_ENABLED=True)
async def test_autogen_service_tvm_enabled(taxi_userver_sample):
    response = await taxi_userver_sample.post('autogen/tvm-service')
    assert response.status_code == 401
    assert response.json() == {
        'code': '401',
        'message': 'missing or empty X-Ya-Service-Ticket header',
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_valid_service_tickets(taxi_userver_sample):
    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_userver_sample.post(
        'autogen/tvm-service', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'test_message': 'mock'}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_valid_service_tickets_no_rule(taxi_userver_sample):
    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_userver_sample.post(
        'autogen/tvm-service', headers=headers,
    )
    assert response.status_code == 403
    assert response.json()['code'] == '403'


@pytest.mark.config(TVM_ENABLED=True)
async def test_tvm2_testing_autogen_no_service_tickets(taxi_userver_sample):
    response = await taxi_userver_sample.put(
        'autogen/tvm-service', data=json.dumps({}),
    )
    assert response.status_code == 200
    assert response.json() == {'test_message': ''}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_testing_autogen_valid_service_ticket(taxi_userver_sample):
    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_userver_sample.put(
        'autogen/tvm-service', headers=headers, data=json.dumps({}),
    )
    assert response.status_code == 200
    assert response.json() == {'test_message': 'mock'}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_testing_autogen_invalid_service_ticket(
        taxi_userver_sample,
):
    headers = {'X-Ya-Service-Ticket': 'invalid_ticket'}
    response = await taxi_userver_sample.put(
        'autogen/tvm-service', headers=headers, data=json.dumps({}),
    )
    assert response.json() == {
        'code': '401',
        'message': 'Bad tvm2 service ticket',
    }


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_valid_service_tickets_no_apikey(
        taxi_userver_sample,
):
    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_userver_sample.delete(
        'autogen/tvm-service', headers=headers, params={'data': 'some data'},
    )
    assert response.status_code == 200
    assert response.json() == {'test_message': 'some data', 'tvm': True}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_apikey_no_service_ticket(taxi_userver_sample):
    headers = {'X-YaTaxi-API-Key': 'sample-key-123'}
    response = await taxi_userver_sample.delete(
        'autogen/tvm-service', headers=headers, params={'data': 'some_data'},
    )
    assert response.status_code == 200
    assert response.json() == {'test_message': 'some_data', 'tvm': False}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_apikey_and_service_ticket(taxi_userver_sample):
    headers = {
        'X-YaTaxi-API-Key': 'sample-key-123',
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    }
    response = await taxi_userver_sample.delete(
        'autogen/tvm-service', headers=headers, params={'data': 'some_data'},
    )
    assert response.status_code == 200
    assert response.json() == {'test_message': 'some_data', 'tvm': True}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_no_apikey_no_service_ticket(taxi_userver_sample):
    headers = {}
    response = await taxi_userver_sample.delete(
        'autogen/tvm-service', headers=headers, params={'data': 'some_data'},
    )
    assert response.status_code == 401
    assert response.json() == {
        'code': '401',
        'message': 'missing or empty X-Ya-Service-Ticket header',
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_valid_service_and_user_tickets_but_no_scope(
        taxi_userver_sample,
):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET_READ,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'autogen/tvm-with-user-ticket-and-scopes', headers=headers,
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'no scope \'write\' in user ticket',
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


@pytest.mark.parametrize(
    'ticket', [USER_TICKET_RW, USER_TICKET_NON_YATEAM_SESSIONID],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_valid_service_and_user_tickets(
        taxi_userver_sample, ticket,
):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': ticket,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'autogen/tvm-with-user-ticket-and-scopes', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'test_value': '42'}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_env_adjuster_adjust_to_wrong1(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET_PROD_YATEAM,
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'autogen/tvm-with-user-ticket-env-adjuster', headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {
        'code': '401',
        'message': 'Bad tvm2 user ticket',
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_env_adjuster_adjust_to_wrong2(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET_PROD,
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '123321',
    }
    response = await taxi_userver_sample.get(
        'autogen/tvm-with-user-ticket-env-adjuster', headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {
        'code': '401',
        'message': 'Bad tvm2 user ticket',
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_env_adjust_to_the_same(
        taxi_userver_sample, mockserver,
):
    @mockserver.json_handler(
        '/userver-sample/autogen/tvm-with-user-ticket-env-adjuster',
    )
    def _handler(client_request):
        assert client_request.headers['X-Yandex-UID'] == '192'
        assert client_request.headers['X-Ya-User-Ticket'] == 'foo'
        assert client_request.headers['X-Ya-User-Ticket-Provider'] == 'yandex'
        return mockserver.make_response(json={'user_id': '', 'user_env': ''})

    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET_PROD,
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '123321',
    }
    response = await taxi_userver_sample.get(
        'autogen/tvm-with-user-ticket-env-adjuster', headers=headers,
    )
    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'user_id': '123321', 'user_env': 'Prod'}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_autogen_env_adjuster_adjust_correct(
        taxi_userver_sample, mockserver,
):
    @mockserver.json_handler(
        '/userver-sample/autogen/tvm-with-user-ticket-env-adjuster',
    )
    def _handler(client_request):
        assert client_request.headers['X-Yandex-UID'] == '192'
        assert client_request.headers['X-Ya-User-Ticket'] == 'foo'
        assert client_request.headers['X-Ya-User-Ticket-Provider'] == 'yandex'
        return mockserver.make_response(json={'user_id': '', 'user_env': ''})

    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET_PROD_YATEAM,
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '123321',
    }
    response = await taxi_userver_sample.get(
        'autogen/tvm-with-user-ticket-env-adjuster', headers=headers,
    )
    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'user_id': '123321', 'user_env': 'ProdYateam'}
