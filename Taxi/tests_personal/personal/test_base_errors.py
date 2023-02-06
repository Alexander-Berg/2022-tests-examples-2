import pytest


REQUEST_URLS = [
    'driver_licenses/find',
    'driver_licenses/retrieve',
    'driver_licenses/store',
    'emails/find',
    'emails/retrieve',
    'emails/store',
    'identifications/find',
    'identifications/retrieve',
    'identifications/store',
    'phones/find',
    'phones/retrieve',
    'phones/store',
    'telegram_logins/find',
    'telegram_logins/retrieve',
    'telegram_logins/store',
    'tins/find',
    'tins/retrieve',
    'tins/store',
    'yandex_logins/find',
    'yandex_logins/retrieve',
    'yandex_logins/store',
]

BULK_REQUEST_URLS = [
    'driver_licenses/bulk_retrieve',
    'driver_licenses/bulk_store',
    'emails/bulk_retrieve',
    'emails/bulk_store',
    'identifications/bulk_retrieve',
    'identifications/bulk_store',
    'phones/bulk_retrieve',
    'phones/bulk_store',
    'telegram_logins/bulk_retrieve',
    'telegram_logins/bulk_store',
    'tins/bulk_retrieve',
    'tins/bulk_store',
    'yandex_logins/bulk_retrieve',
    'yandex_logins/bulk_store',
]

TVM_TICKET = (
    '3:serv:CBAQ__________9_IgYIexC5wwc:Op8olaHfv3Bni0Y8DYHN9v'
    'UsoYBZtUHbAXLHVbZAtwcPTzAxKEU9m6S70zKakvlNTF8bX45Ngt6QY3p'
    'JV8MMgJMluZOfgehzQte8IeGkGPic1yQnaeV_y-4nOQksZLASY7KT8eMx'
    't-qzbHTY-r0OdjBt3L-5Xtx4fghYnE1bls8'
)


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_no_token_no_ticket(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url, params={'source': 'testsuite'}, json={'key': 'value'},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_wrong_token_no_ticket(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url,
        headers={'X-YaTaxi-Api-Key': 'wrong_apikey'},
        params={'source': 'testsuite'},
        json={'key': 'value'},
    )
    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Forbidden'}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_no_token_wrong_ticket(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url,
        headers={'X-Ya-Service-Ticket': 'wrong_ticket'},
        params={'source': 'testsuite'},
        json={'key': 'value'},
    )
    assert response.status_code == 401
    assert response.json() == {
        'code': '401',
        'message': 'Bad tvm2 service ticket',
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_good_token_no_ticket(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url, headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid request param \'source\': empty or not exists',
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_good_token_wrong_ticket(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url,
        headers={
            'X-YaTaxi-Api-Key': 'personal_apikey',
            'X-Ya-Service-Ticket': 'wrong_ticket',
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid request param \'source\': empty or not exists',
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_no_token_good_ticket(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url, headers={'X-Ya-Service-Ticket': TVM_TICKET},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid request param \'source\': empty or not exists',
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_wrong_token_good_ticket(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url,
        headers={
            'X-YaTaxi-Api-Key': 'wrong_apikey',
            'X-Ya-Service-Ticket': TVM_TICKET,
        },
    )
    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Forbidden'}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_no_source(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url, headers={'X-YaTaxi-Api-Key': 'personal_apikey'}, json={},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid request param \'source\': empty or not exists',
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', REQUEST_URLS + BULK_REQUEST_URLS)
async def test_empty_source(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url,
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': ''},
        json={},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid request param \'source\': empty or not exists',
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize('request_url', BULK_REQUEST_URLS)
async def test_too_many_docs(taxi_personal, request_url):
    response = await taxi_personal.post(
        request_url,
        headers={'X-YaTaxi-Api-Key': 'personal_apikey'},
        params={'source': 'testsuite'},
        json={'items': [{'value': str(i)} for i in range(1500)]},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Cannot perform bulk request with more than 1000 docs',
    }
