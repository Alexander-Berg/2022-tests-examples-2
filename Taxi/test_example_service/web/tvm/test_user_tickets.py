import pytest


# Generated via `tvmknife unittest service -s 222 -d 111`
TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:'
    'KNEeJLUl2isKldQlwD15xTEN0oTC3Po5Yj'
    '-P6iTCPIjUC2IbfwEfU2_LHTMqh4qFmP9d'
    'NJ-mzLs9xYen8wh6_3XPlZV4ejioJ6y19M'
    'CqgwGjM5QPv4GYMhb_kxw2C9OumWxCB6Vt'
    'dHUCnuqt7VaNNxTk_UPU_OijlAX0B1pEkGg'
)

# Generated via:
# tvmknife unittest user -d 42
# -u 1,2,3,42 -e test --scopes test:read,test:write
USER_TICKET = (
    '3:user:CA0Q__________9_GjEKAggBCgII'
    'AgoCCAMKAggqECoaCXRlc3Q6cmVhZBoKdGV'
    'zdDp3cml0ZSDShdjMBCgB:JtO2tr4ZxaaqU'
    'OyADJLnArR1-zMD1olxZiuk5SRU7kw8dpaa'
    'nq8jimH34-xOvnETOjv5I7It7AIf_Zt1kI9'
    '8GtdM-6r759L-waOWw5u37UEpxx8uJFZumg'
    'R9m5fsaVtgxcElOHoHIpVaiq6xSuaIz_D28'
    'CYfWGGrlJ_hRuI8hFo'
)

# Generated via:
# tvmknife unittest user -d 123
# -u 1,2,3,123 -e test --scopes test:read,test:write
USER_TEAM_TICKET = (
    '3:user:CA4Q__________9_GjEKAggBCgIIA'
    'goCCAMKAgh7EHsaCXRlc3Q6cmVhZBoKdGVzd'
    'Dp3cml0ZSDShdjMBCgD:EmD2WL1eR67dqGXq'
    'Y0eUBRfsnemKDHzxOLTowYNbODZ5wBuqmbY8'
    'Bof7woMYa8JfeVzlZ2CHbgboE7bLiSjNcGyG'
    'MIjPdfjc7w5j8JWj1xhL49Pau1GctHlyXsJ0'
    'YJrROvyuzN7PFMA2tpy1F-dAxSdZVNLjKh8r'
    'KV2kgDzXVMA'
)

# Generated via `tvmknife unittest user -d 42 -e test`
NO_SCOPES_USER_TICKET = (
    '3:user:CA0Q__________9_Gg4KAggqECog0'
    'oXYzAQoAQ:IcTRZuIFcOuYrJ5LxWa_v4_0LB'
    'QRfcCDKUt8GgO0a8ApnVgmIcWXP2nIL-Xs_U'
    'P0Hv4tB7cb18-Go8pWnBjxTMZEUu-4swn_S1'
    'K6CheC7I7vBzAT2LYnJFnpppla0e8HfmjQYY'
    'odBvQT8XcO3jlITY3Vpp9peqIaZbdH0QtAmIw'
)

# Generated via `tvmknife unittest service -s 111 -d 333`
TO_YAS_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxDNAg:W_'
    '0N-v0kZUclPuKDisinQ28pDD4vgQHoT5HYAq'
    'ct7OVvafCBvyeOlBpKWMjpFZuMqKTJvKHAIk'
    '-wqQ-evtjrp0L5xXUGLjGgMlBegJDa1jUph9'
    'QjLpuRg1zzOmTGhXcljefa7QJElCYG6wmLxs'
    'I5uuR-vmtSu_u5jUegBOiPtKE'
)


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        TVM_ENABLED=True,
        TVM_USER_TICKETS_ENABLED=True,
        TVM_RULES=[
            {'src': 'test', 'dst': 'example_service'},
            {'src': 'example_service', 'dst': 'yet_another_service'},
        ],
        TVM_SERVICES={
            'example_service': 111,
            'test': 222,
            'yet_another_service': 333,
        },
        TVM_API_URL='$mockserver/tvm',
    ),
    pytest.mark.usefixtures('mocked_tvm'),
]


async def test_server_happy_path(web_app_client):
    resp = await web_app_client.get(
        '/tvm/user-ticket-scopes',
        headers={
            'X-Yandex-UID': '42',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': USER_TICKET,
        },
    )
    assert resp.status == 200
    assert await resp.json() == {
        'default_uid': 42,
        'uids': [1, 2, 3, 42],
        'scopes': ['test:read', 'test:write'],
    }


@pytest.mark.tvm2_ticket({333: TO_YAS_TICKET})
async def test_client_happy_path(web_app_client, mock_yet_another_service):
    @mock_yet_another_service('/tvm/user-ticket-scopes')
    async def handler(request):
        assert request.headers['X-Yandex-UID'] == '42'
        assert request.headers['X-Ya-User-Ticket'] == USER_TICKET
        assert request.headers['X-Ya-Service-Ticket'] == TO_YAS_TICKET
        return {
            'default_uid': 42,
            'uids': [1, 2, 3, 42],
            'scopes': ['test:read', 'test:write'],
        }

    resp = await web_app_client.get(
        '/tvm/user-ticket-proxy',
        headers={
            'X-Yandex-UID': '42',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': USER_TICKET,
        },
    )

    assert resp.status == 200
    assert await resp.json() == {
        'default_uid': 42,
        'uids': [1, 2, 3, 42],
        'scopes': ['test:read', 'test:write'],
    }

    assert handler.times_called == 1


async def test_server_wrong_uid(web_app_client):
    resp = await web_app_client.get(
        '/tvm/user-ticket-scopes',
        headers={
            'X-Yandex-UID': '44',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': USER_TICKET,
        },
    )
    assert resp.status == 401
    assert await resp.json() == {
        'code': 'tvm-user-ticket-error',
        'message': (
            'UID 44 from X-Yandex-UID mismatch UID 42 from tvm user ticket'
        ),
    }


async def test_server_no_uid(web_app_client):
    resp = await web_app_client.get(
        '/tvm/user-ticket-scopes',
        headers={
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': USER_TICKET,
        },
    )
    assert resp.status == 401
    assert await resp.json() == {
        'code': 'tvm-user-ticket-error',
        'message': 'Header X-Yandex-UID is missing',
    }


async def test_server_not_passing_required_scope(web_app_client):
    resp = await web_app_client.get(
        '/tvm/user-ticket-scopes',
        headers={
            'X-Yandex-UID': '42',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': NO_SCOPES_USER_TICKET,
        },
    )
    assert resp.status == 401
    assert await resp.json() == {
        'code': 'tvm-user-ticket-error',
        'message': 'TVM user ticket does not have required scope: test:read',
    }


async def test_server_user_ticket_no_scopes_required(web_app_client):
    resp = await web_app_client.get(
        '/tvm/user-ticket-no-scopes',
        headers={
            'X-Yandex-UID': '42',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': NO_SCOPES_USER_TICKET,
        },
    )
    assert resp.status == 200
    assert await resp.json() == {'default_uid': 42, 'scopes': [], 'uids': [42]}


async def test_server_user_ticket_no_scopes_required_no_ticket_provided(
        web_app_client,
):
    resp = await web_app_client.get(
        '/tvm/user-ticket-no-scopes',
        headers={
            'X-Yandex-UID': '42',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
        },
    )
    assert resp.status == 401
    assert await resp.json() == {
        'code': 'tvm-user-ticket-error',
        'message': 'TVM user ticket header missing',
    }


async def test_server_no_service_ticket(web_app_client):
    resp = await web_app_client.get(
        '/tvm/user-ticket-scopes',
        headers={
            'X-Yandex-UID': '42',
            'X-Ya-User-Ticket': NO_SCOPES_USER_TICKET,
        },
    )
    assert resp.status == 401
    assert await resp.json() == {
        'code': 'tvm-auth-error',
        'message': 'TVM header missing',
    }


async def test_server_adjust_env(web_app_client):
    resp = await web_app_client.get(
        '/tvm/user-ticket-scopes',
        headers={
            'X-Yandex-UID': '123',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': USER_TEAM_TICKET,
            'X-Ya-User-Ticket-Provider': 'yandex_team',
        },
    )
    assert resp.status == 200
    assert await resp.json() == {
        'default_uid': 123,
        'uids': [1, 2, 3, 123],
        'scopes': ['test:read', 'test:write'],
        'provider': 'yandex_team',
    }


@pytest.mark.tvm2_ticket({333: TO_YAS_TICKET})
async def test_client_adjust_env(web_app_client, mock_yet_another_service):
    @mock_yet_another_service('/tvm/user-ticket-scopes')
    async def handler(request):
        assert request.headers['X-Yandex-UID'] == '123'
        assert request.headers['X-Ya-User-Ticket'] == USER_TEAM_TICKET
        assert request.headers['X-Ya-Service-Ticket'] == TO_YAS_TICKET
        assert request.headers['X-Ya-User-Ticket-Provider'] == 'yandex_team'
        return {
            'default_uid': 123,
            'uids': [1, 2, 3, 123],
            'scopes': ['test:read', 'test:write'],
            'provider': 'yandex_team',
        }

    resp = await web_app_client.get(
        '/tvm/user-ticket-proxy',
        headers={
            'X-Yandex-UID': '123',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': USER_TEAM_TICKET,
            'X-Ya-User-Ticket-Provider': 'yandex_team',
        },
    )

    assert resp.status == 200
    assert await resp.json() == {
        'default_uid': 123,
        'uids': [1, 2, 3, 123],
        'scopes': ['test:read', 'test:write'],
        'provider': 'yandex_team',
    }

    assert handler.times_called == 1
