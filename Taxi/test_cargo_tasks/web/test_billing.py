import pytest

from taxi.clients import billing_v2

CREATE_CLIENT = 'create_client'
CREATE_ASSOCIATION = 'create_user_client_association'
CREATE_PERSON = 'create_person'
CREATE_PERSON_SIMULATE = 'create_person_simulate'
CREATE_PERSON_SIMULATE_OK = 'create_person_simulate_ok'
CREATE_PERSON_SIMULATE_INTERNAL_OK = 'create_person_simulate_internal_ok'
CREATE_PERSON_SIMULATE_FAIL = 'create_person_simulate_fail'
CREATE_PERSON_SIMULATE_INTERNAL_FAIL = 'create_person_simulate_internal_fail'
CREATE_OFFER = 'create_offer'
GET_CONTRACTS = 'get_contracts'
FIND_CLIENT = 'find_client'
GET_CLIENT_PERSONS = 'get_client_persons'
CREATE_CONTRACT = 'create_contract'
GET_ORDERS_INFO = 'get_orders_info'
CREATE_PREPAY_INVOICE = 'create_prepay_invoice'

INVOICE_EXTERNAL_URL = 'https://invoice_external_url'


@pytest.fixture(name='requests')
def _load_requests(load_json):
    return load_json('requests.json')


@pytest.fixture(name='responses')
def _load_responses(load_json):
    return load_json('responses.json')


@pytest.fixture(name='expected_billing_requests')
def _load_billing_requests(load_json):
    loaded_data = load_json('expected_billing_requests.json')
    return {
        key: (
            tuple(value) if isinstance(value, list) else value
        )  # tuples are expected, not lists
        for key, value in loaded_data.items()
    }


async def test_upsert_billing_client(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[CREATE_CLIENT],
    )
    mocked_billing.set_response(responses[CREATE_CLIENT])

    response = await web_app_client.post(
        '/v1/billing/client/upsert', json=requests[CREATE_CLIENT],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {'client_id': responses[CREATE_CLIENT]}


async def test_create_association(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[CREATE_ASSOCIATION],
    )
    mocked_billing.set_response(responses[CREATE_ASSOCIATION])

    response = await web_app_client.post(
        '/v1/billing/association/create', json=requests[CREATE_ASSOCIATION],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'code': responses[CREATE_ASSOCIATION][0],
        'message': responses[CREATE_ASSOCIATION][1],
    }


async def test_create_person(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[CREATE_PERSON],
    )
    mocked_billing.set_response(responses[CREATE_PERSON])

    response = await web_app_client.post(
        '/v1/billing/person/upsert', json=requests[CREATE_PERSON],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {'person_id': responses[CREATE_PERSON]}


async def test_create_person_simulate_ok(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[CREATE_PERSON_SIMULATE],
    )
    mocked_billing.set_response(responses[CREATE_PERSON_SIMULATE_INTERNAL_OK])

    response = await web_app_client.post(
        '/v1/billing/person/upsert-simulate',
        json=requests[CREATE_PERSON_SIMULATE],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == responses[CREATE_PERSON_SIMULATE_OK]


async def test_create_person_simulate_fail(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[CREATE_PERSON_SIMULATE],
    )
    mocked_billing.set_response(
        responses[CREATE_PERSON_SIMULATE_INTERNAL_FAIL],
    )

    response = await web_app_client.post(
        '/v1/billing/person/upsert-simulate',
        json=requests[CREATE_PERSON_SIMULATE],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == responses[CREATE_PERSON_SIMULATE_FAIL]


async def test_create_offer(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[CREATE_OFFER],
    )
    mocked_billing.set_response(responses[CREATE_OFFER])

    response = await web_app_client.post(
        '/v1/billing/offer/create', json=requests[CREATE_OFFER],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        key.lower(): value for key, value in responses[CREATE_OFFER].items()
    }


async def test_get_contracts(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[GET_CONTRACTS],
    )
    mocked_billing.set_response(responses[GET_CONTRACTS])

    response = await web_app_client.get(
        '/v1/billing/offer/list', params=requests[GET_CONTRACTS],
    )

    assert response.status == 200
    response_json = await response.json()
    # field "IS_FAXED" should be excluded from balance response
    assert response_json == {
        'contracts': [
            {
                key.lower(): value
                for key, value in contract.items()
                if key != 'IS_FAXED'
            }
            for contract in responses[GET_CONTRACTS]
        ],
    }


@pytest.mark.parametrize(
    ('is_client_found', 'expected_code'),
    [
        pytest.param(True, 200, id='client_found'),
        pytest.param(False, 404, id='client_not_found'),
    ],
)
async def test_find_client(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
        is_client_found,
        expected_code,
):
    mocked_billing.set_expected_request(expected_billing_requests[FIND_CLIENT])
    if is_client_found:
        mocked_billing.set_response(responses[FIND_CLIENT])

    response = await web_app_client.get(
        '/v1/billing/client/find', params=requests[FIND_CLIENT],
    )

    assert response.status == expected_code
    if expected_code == 200:
        response_json = await response.json()
        assert response_json == {
            key.lower(): value for key, value in responses[FIND_CLIENT].items()
        }


async def test_get_client_persons(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[GET_CLIENT_PERSONS],
    )
    mocked_billing.set_response(responses[GET_CLIENT_PERSONS])

    response = await web_app_client.get(
        '/v1/billing/client/person/list', params=requests[GET_CLIENT_PERSONS],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'persons': [
            {key.lower(): value for key, value in contract.items()}
            for contract in responses[GET_CLIENT_PERSONS]
        ],
    }


async def test_create_contract(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[CREATE_CONTRACT],
    )
    mocked_billing.set_response(responses[CREATE_CONTRACT])

    response = await web_app_client.post(
        '/v1/billing/contract/create', json=requests[CREATE_CONTRACT],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        key.lower(): value for key, value in responses[CREATE_CONTRACT].items()
    }


async def test_create_prepay_invoice(
        web_app_client,
        mocked_billing,
        requests,
        responses,
        expected_billing_requests,
):
    mocked_billing.set_expected_request(
        expected_billing_requests[GET_ORDERS_INFO],
        handler_key=GET_ORDERS_INFO,
    )
    mocked_billing.set_expected_request(
        expected_billing_requests[CREATE_PREPAY_INVOICE],
        handler_key=CREATE_PREPAY_INVOICE,
    )

    mocked_billing.set_response(
        response=responses[GET_ORDERS_INFO], handler_key=GET_ORDERS_INFO,
    )
    mocked_billing.set_response(
        response=billing_v2.PrepayInvoice('', INVOICE_EXTERNAL_URL, ''),
        handler_key=CREATE_PREPAY_INVOICE,
    )

    response = await web_app_client.post(
        '/v1/billing/create-prepay-invoice',
        json=requests[CREATE_PREPAY_INVOICE],
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == responses[CREATE_PREPAY_INVOICE]
