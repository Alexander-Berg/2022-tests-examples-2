import datetime

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
UTCNOW = datetime.datetime(2020, 5, 15)


@pytest.mark.now(UTCNOW.isoformat())
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'test', 'dst': 'example_service'}],
    TVM_SERVICES={'example_service': 111, 'test': 222},
    TVM_API_URL='$mockserver/tvm',
)
async def test_tvm_caches(taxi_example_service_web, taxi_config, mocked_tvm):
    response = await taxi_example_service_web.get(
        '/tvm/testing', headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )
    assert response.status == 200
    assert await response.read() == b''
    taxi_config.set_values({'TVM_RULES': []})
    await taxi_example_service_web.invalidate_caches()

    response = await taxi_example_service_web.get(
        '/tvm/testing', headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )
    assert response.status == 401
    err = b'{"message": "TVM authentication error", "code": "tvm-auth-error"}'
    assert await response.read() == err
