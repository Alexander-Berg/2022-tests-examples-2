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


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        TVM_ENABLED=True,
        TVM_RULES=[{'src': 'test', 'dst': 'example_service'}],
        TVM_SERVICES={'example_service': 111, 'test': 222},
        TVM_API_URL='$mockserver/tvm',
    ),
    pytest.mark.usefixtures('mocked_tvm'),
]


async def test_with_ticket(web_app_client):
    resp = await web_app_client.get(
        '/tvm/testing', headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )
    assert resp.status == 200
    assert await resp.read() == b''


async def test_without_ticket(web_app_client):
    resp = await web_app_client.get('/tvm/testing')
    assert resp.status == 200
    assert await resp.read() == b''


async def test_bad_ticket(web_app_client):
    resp = await web_app_client.get(
        '/tvm/testing', headers={'X-Ya-Service-Ticket': '1111'},
    )
    assert resp.status == 401
    assert await resp.json() == {
        'code': 'tvm-auth-error',
        'message': 'TVM authentication error',
    }
