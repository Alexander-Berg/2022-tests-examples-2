# pylint: disable=C0103
import pytest


# Generated via `tvmknife unittest service -s 2001716 -d 2001716`
USERVER_SAMPLE_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggItJZ6ELSWeg'
    ':Ub6VhOZcj0V93-TSypyEqqwxTUs7uaaeb46PA'
    'HNiMnAuNrGXVbuR9wSfKvjTM_7defPpjqsiGf'
    'xeZLUdjcM8pVxLeXC-cE5O62YmXLyQawXU5IKB'
    'NFna0ZbvepJ69NeXag1hfSiqCXYi6Ih_v39fEjO8MWeSGGNsThNX9Ze9k1s'
)

# Generated via `tvmknife unittest service -s 111 -d 111`
MOCK_SERVICE_SELF_TICKET = (
    '3:serv:CBAQ__________9_IgQIbxBv:EHGF97'
    'ARomnpmVtlj8HsrGlGTToqEtIoeG1s2HsrEUF'
    'Q4WuSRjdhMlvXdUCi8xCdq_Fh4ddg4HA3jlyg3'
    'ObCBE-dS7k1jHo7VSWDLzhhwG1rSk55SMMiBB'
    'SGMY0UndgyFNncw3L2mhJ9m2HS4pavia01QoLOyTuWLP084xe0KAU'
)

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq'
    '_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXD'
    'iiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848PW-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkHR3s'
)

# Generated via:
# tvmknife unittest user -d 42 -e test_yateam --scopes test:scope1,test:scope2
USER_TICKET = (
    '3:user:CA4Q__________9_GigKAggqECoaC3'
    'Rlc3Q6c2NvcGUxGgt0ZXN0OnNjb3BlMiDShdjM'
    'BCgD:CfnUVumvRuqaW2blbN5v-njW73jd0G1c'
    '_vcNE-_8XQAadniAayTKrq6iLgE2weMgidW0oi'
    'eLdssjjyOIZDIqCy3gQyYslrYOiO17pIuvYXd'
    '0CTOdpJQdeFEBsnj8BqvhXWYJs7Y99gGYamKr8'
    '7hMeLUyippo4p_Ve3aJeuA1Syc'
)

# Generated via:
# tvmknife unittest user -d 42 -e test --scopes test:scope1,test:scope2
USER_TICKET_NON_YATEAM = (
    '3:user:CA0Q__________9_GigKAggqECoaC3Rlc3Q6c2NvcGUxGgt0ZXN0OnNjb3BlMiDSh'
    'djMBCgB:LD6XNU9mPRhWe5nRqftWN7xBXI8mACQN-i9CmwXJGdzsNfSmdiN1oA_Acqte8k3Z'
    '2acJk1gMTNoXqR4R-wd786Q_NJmk_Lf-2uZ0w5kz3WGYzfA_pvdG-T2ia1ElHQrXiQEicrd2'
    'IfFPvYWB_yIysbW3Kt9l6w9yU4KCJWmsq3g'
)


# Generated via:
# tvmknife unittest user -d 42 -e prod_yateam --scopes test:scope1,test:scope2
USER_TICKET_PROD_YATEAM = (
    '3:user:CAwQ__________9_GigKAggqECoaC3Rlc3Q6c2NvcGUxGgt0ZXN0'
    'OnNjb3BlMiDShdjMBCgC:Qu7VFDKGGPA_rYlODpyP4y2lmPQfj_9BulJJN2'
    '_2SqbMIMaVz9E2gmHQRuCXMXf4wp07eQuu9y0Hb8F3VkUEQaYo0NjR74fyE'
    'LcRlPOoMHpfkv76pMI9RNyf23n4gZYve16V4Taq9dnUhU0dGsRC5DjbkZcS'
    'vf-kN6PBbJfo4Dw'
)

# Generated via:
# tvmknife unittest user -d 42 -e prod --scopes test:scope1,test:scope2
USER_TICKET_PROD = (
    '3:user:CAsQ__________9_GigKAggqECoaC3Rlc3Q6c2NvcGUxGgt0ZXN0On'
    'Njb3BlMiDShdjMBCgA:IcTjUdPpuEwpTCjkiiFalm9dv1wx25_9BOKmSX8Ak6'
    'WQdVrhhAh819qG2Mkrn6OWfL-SG1ZFENgc8UdA3Q35nfEC2tZxTg9qpBDpJ7o'
    'Z4xlkhHOvw-ezfvGBHU52ZduLeb3lRLfps70fP8U6PsSBjZbTcP8OTIgcbFci'
    'Pvsc2sU'
)


@pytest.mark.config(TVM_ENABLED=True)
async def test_tvm2_no_service_ticket(taxi_userver_sample):
    response = await taxi_userver_sample.get('auth/tvm2')
    assert response.status_code == 401
    assert response.content == b'missing or empty X-Ya-Service-Ticket header'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(TVM_ENABLED=False)
async def test_tvm2_no_service_ticket_disabled(taxi_userver_sample):
    response = await taxi_userver_sample.get('auth/tvm2')
    assert response.status_code == 200
    assert response.content == b''
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(TVM_ENABLED=False, TVM_FORBIDDEN=True)
async def test_tvm2_no_service_ticket_forbidden(taxi_userver_sample):
    response = await taxi_userver_sample.get('auth/tvm2')
    assert response.status_code == 403
    assert response.content == b''
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(TVM_ENABLED=True)
async def test_tvm2_invalid_service_ticket(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': 'incorrect-ticket'}
    response = await taxi_userver_sample.get('auth/tvm2', headers=headers_set)
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 service ticket'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_SELF_TICKET},
)
async def test_tvm2_service_ticket_for_other_dest(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': MOCK_SERVICE_SELF_TICKET}
    response = await taxi_userver_sample.get('auth/tvm2', headers=headers_set)
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 service ticket'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'userver-sample', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_ticket_but_no_rule(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_userver_sample.get('auth/tvm2', headers=headers_set)
    assert response.status_code == 403
    assert response.content == b'No rule found for source from tvm2 ticket'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'userver-sample', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: 'ANOTHERTICKET'},
)
async def test_tvm2_valid_service_ticket1(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': USERVER_SAMPLE_SERVICE_TICKET}
    response = await taxi_userver_sample.get('auth/tvm2', headers=headers_set)
    assert response.status_code == 200


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_ticket2(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_userver_sample.get('auth/tvm2', headers=headers_set)
    assert response.status_code == 200


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_ticket_invalid_user_ticket(
        taxi_userver_sample,
):
    headers_set = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': 'I am bad',
    }
    response = await taxi_userver_sample.get('auth/tvm2', headers=headers_set)
    assert response.status_code == 200


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=False,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_ticket_but_no_yandex_uid(
        taxi_userver_sample,
):
    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket', headers=headers,
    )
    assert response.status_code == 403
    assert response.content == b'missing or empty X-Yandex-UID header'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_ticket_but_user_ticket_required(
        taxi_userver_sample,
):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Yandex-UID': '999',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket', headers=headers,
    )
    assert response.status_code == 401
    assert response.content == b'missing or empty X-Ya-User-Ticket header'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_ticket_but_bad_user_ticket(
        taxi_userver_sample,
):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': 'I am bad',
        'X-Yandex-UID': '999',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket', headers=headers,
    )
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 user ticket'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_and_user_tickets_but_wrong_uid(
        taxi_userver_sample,
):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
        'X-Yandex-UID': '999',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-and-scope2', headers=headers,
    )
    assert response.status_code == 403
    assert response.content == (
        b'UID 999 from X-Yandex-UID header mismatch '
        b'UID 42 from tvm user ticket'
    )
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_and_user_tickets_but_no_scope(
        taxi_userver_sample,
):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-and-scope2', headers=headers,
    )
    assert response.status_code == 403
    assert response.content == (
        b'no scope \'test:scope_that_is_missing_in_'
        b'user_ticket\' in user ticket'
    )
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_and_user_tickets_wrong_env(
        taxi_userver_sample,
):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-and-scope-stress', headers=headers,
    )
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 user ticket'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_and_user_tickets(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-and-scope', headers=headers,
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_and_user_tickets_no_uid(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-and-scope', headers=headers,
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_valid_service_and_user_tickets_no_scopes_required(
        taxi_userver_sample,
):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket', headers=headers,
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_echo_to_mock_with_user_tickets(
        taxi_userver_sample, mockserver,
):
    @mockserver.json_handler('/tvm2-echo')
    def _tvm2_echo(request):
        assert request.headers['X-Ya-User-Ticket'] == USER_TICKET
        assert request.headers['X-Yandex-UID'] == '42'
        assert request.headers['X-Ya-Service-Ticket'] == MOCK_SERVICE_TICKET
        return {'status': 'OK'}

    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/user-external-echo', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'response': {'status': 'OK'}}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_env_adjuster_no_header(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-env-adjuster-and-scope', headers=headers,
    )
    assert response.status_code == 401
    assert response.content == (
        b'missing or empty X-Ya-User-Ticket-Provider header'
    )
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_env_adjuster_bad_header(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,
        'X-Ya-User-Ticket-Provider': 'bad_value',
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-env-adjuster-and-scope', headers=headers,
    )
    assert response.status_code == 401
    assert response.content == (
        b'\'X-Ya-User-Ticket-Provider\' header has unsupported '
        b'value \'bad_value\''
    )
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_env_adjuster_dont_adjust1(taxi_userver_sample):
    # Make sure 'TestYateam' env is not affected by X-Ya-User-Ticket-Provider
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET,  # Requires 'TestYateam'
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-env-adjuster-and-scope', headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_env_adjuster_dont_adjust2(taxi_userver_sample):
    # Make sure 'Test' env is not affected by X-Ya-User-Ticket-Provider
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET_NON_YATEAM,  # Requires 'Test'
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-env-adjuster-and-scope', headers=headers,
    )
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 user ticket'
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_env_adjuster_adjust_correct(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET_PROD_YATEAM,
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-prod-env-adjuster-and-scope',
        headers=headers,
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_env_adjuster_adjust_to_the_same(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET_PROD,
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-with-user-ticket-prod-env-adjuster-and-scope',
        headers=headers,
    )
    assert response.status_code == 200
    assert response.content == b''
