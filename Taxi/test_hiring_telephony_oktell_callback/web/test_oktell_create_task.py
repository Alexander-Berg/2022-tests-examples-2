import pytest

ROUTE = '/v1/tasks/oktell/create-task'


@pytest.fixture  # noqa: F405
async def make_request(taxi_hiring_telephony_oktell_callback_web):
    async def func(body, code):
        response = await taxi_hiring_telephony_oktell_callback_web.post(
            ROUTE, json=body,
        )
        assert response.status == code
        return response

    return func


@pytest.fixture
async def salesforce(mockserver):
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    def auth(_):  # pylint: disable=W0612
        data = {
            'access_token': 'test_access_token',
            'instance_url': 'test_instance_url',
            'id': 'test_id',
            'token_type': 'test_token_type',
            'issued_at': 'test_issued_at',
            'signature': 'test_signature',
        }
        return data

    @mockserver.json_handler('/salesforce/services/data/v46.0/sobjects/Task/')
    def create(_):  # pylint: disable=W0612
        data = {'id': '00T0E00000FYSG4UAP', 'success': True, 'errors': []}
        return data


@pytest.mark.parametrize('request_name', ['default'])
@pytest.mark.usefixtures('salesforce')
async def test_oktell_create_task(  # pylint: disable=W0621
        make_request, load_json, request_name,
):
    data = load_json('requests.json')[request_name]
    response = await make_request(**data)
    body = await response.json()
    assert body


@pytest.mark.parametrize('request_name', ['sf_fail'])
@pytest.mark.usefixtures('salesforce')
async def test_oktell_create_task_sf_fail(  # pylint: disable=W0621
        mockserver, make_request, load_json, request_name,
):
    @mockserver.json_handler('/salesforce/services/data/v46.0/sobjects/Task/')
    def handler(_):  # pylint: disable=W0612
        doc = {}
        return mockserver.make_response(json=doc, status=400)

    data = load_json('requests.json')[request_name]
    response = await make_request(**data)
    body = await response.json()
    assert body
    assert body['code'] == 'salesforce_unexpected_response'
    assert 'message' in body
