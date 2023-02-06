import pytest


@pytest.mark.config(TVM_ENABLED=True)
async def test_no_apikey_no_ticket(taxi_userver_sample):
    response = await taxi_userver_sample.get('auth/apikey-or-tvm2')
    assert response.status_code == 400
    assert response.content == b''


@pytest.mark.config(TVM_ENABLED=True)
async def test_no_apikey_invalid_ticket(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': 'incorrect-ticket'}
    response = await taxi_userver_sample.get(
        'auth/apikey-or-tvm2', headers=headers_set,
    )
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 service ticket'


@pytest.mark.config(TVM_ENABLED=True)
async def test_invalid_key_no_ticket(taxi_userver_sample):
    headers_set = {'X-YaTaxi-API-Key': 'incorrect-apikey'}
    response = await taxi_userver_sample.get(
        'auth/apikey-or-tvm2', headers=headers_set,
    )
    assert response.status_code == 403
    assert response.content == b''


@pytest.mark.config(TVM_ENABLED=True)
async def test_invalid_key_invalid_ticket(taxi_userver_sample):
    headers_set = {
        'X-YaTaxi-API-Key': 'incorrect-apikey',
        'X-Ya-Service-Ticket': 'incorrect-ticket',
    }
    response = await taxi_userver_sample.get(
        'auth/apikey-or-tvm2', headers=headers_set,
    )
    assert response.status_code == 403
    assert response.content == b''


@pytest.mark.config(TVM_ENABLED=True)
async def test_good_key_no_ticket(taxi_userver_sample):
    headers_set = {'X-YaTaxi-API-Key': 'sample-key-123'}
    response = await taxi_userver_sample.get(
        'auth/apikey-or-tvm2', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.config(TVM_ENABLED=True)
async def test_good_key_invalid_ticket(taxi_userver_sample):
    headers_set = {
        'X-YaTaxi-API-Key': 'sample-key-123',
        'X-Ya-Service-Ticket': 'incorrect-ticket',
    }
    response = await taxi_userver_sample.get(
        'auth/apikey-or-tvm2', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.config(TVM_ENABLED=True)
async def test_no_ticket_no_apikey(taxi_userver_sample):
    response = await taxi_userver_sample.get('auth/tvm2-or-apikey')
    assert response.status_code == 401
    assert response.content == b'missing or empty X-Ya-Service-Ticket header'


@pytest.mark.config(TVM_ENABLED=True)
async def test_no_ticket_invalid_key(taxi_userver_sample):
    headers_set = {'X-YaTaxi-API-Key': 'incorrect-apikey'}
    response = await taxi_userver_sample.get(
        'auth/tvm2-or-apikey', headers=headers_set,
    )
    assert response.status_code == 403
    assert response.content == b''


@pytest.mark.config(TVM_ENABLED=True)
async def test_no_ticket_good_key(taxi_userver_sample):
    headers_set = {'X-YaTaxi-API-Key': 'sample-key-123'}
    response = await taxi_userver_sample.get(
        'auth/tvm2-or-apikey', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.config(TVM_ENABLED=True)
async def test_invalid_ticket_no_apikey(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': 'incorrect-ticket'}
    response = await taxi_userver_sample.get(
        'auth/tvm2-or-apikey', headers=headers_set,
    )
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 service ticket'


@pytest.mark.config(TVM_ENABLED=True)
async def test_invalid_ticket_invalid_key(taxi_userver_sample):
    headers_set = {
        'X-YaTaxi-API-Key': 'incorrect-apikey',
        'X-Ya-Service-Ticket': 'incorrect-ticket',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-or-apikey', headers=headers_set,
    )
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 service ticket'


@pytest.mark.config(TVM_ENABLED=True)
async def test_invalid_ticket_good_key(taxi_userver_sample):
    headers_set = {
        'X-YaTaxi-API-Key': 'sample-key-123',
        'X-Ya-Service-Ticket': 'incorrect-ticket',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-or-apikey', headers=headers_set,
    )
    assert response.status_code == 401
    assert response.content == b'Bad tvm2 service ticket'


# pylint: disable=C0103
@pytest.mark.config(TVM_ENABLED=False)
async def test_invalid_ticket_invalid_key_tvm_disabled(taxi_userver_sample):
    headers_set = {
        'X-YaTaxi-API-Key': 'incorrect-apikey',
        'X-Ya-Service-Ticket': 'incorrect-ticket',
    }
    response = await taxi_userver_sample.get(
        'auth/tvm2-or-apikey', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.content == b''
