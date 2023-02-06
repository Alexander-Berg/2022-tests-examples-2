import pytest

from tests_cargo_sf import const

PREFIX = '/internal/cargo-sf/internal-requests'

REQUEST = {
    'company': 'Walhalalalala',
    'last_name': 'Asgardov 2022-01-26 01:51:11',
    'first_name': 'Loki',
    'middle_name': 'Hansson',
    'email': 'voytekh@ya.ru',
    'phone': '+79002222220',
    'title': 'Landser',
    'lead_source': 'Other',
    'contact_type': 'Accountant',
    'lead_owner': '00509000009P3YoAAK',
    'sales_group': 'Sales',
    'website': 'ya.ru',
    'industry': 'Аптеки и фармацевтические компании',
    'product': None,
    'tier': '1',
    'tin': '1111',
    'kpp': '11111',
    'potential': '9001',
    'city': 'Moskva',
    'state': 'Moscow',
    'country': 'Russia',
    'postal_code': '350000',
    'street': 'Novinskiy Bul\'var 8',
    'rating': 'Hot',
    'utm_campaign': None,
    'utm_content': 'utm_content_hello',
    'utm_medium': 'utm_medium_hello',
}


@pytest.mark.now(const.TOKEN_JUST_UPDATED_TIME)
@pytest.mark.parametrize(
    'sf_response_code, expected_code', ((201, 200), (200, 200), (400, 400)),
)
async def test_func_create_lead(
        taxi_cargo_sf,
        mockserver,
        mock_auth,
        sf_response_code,
        expected_code,
        load_json,
        create_auth_token_record,
):
    @mockserver.json_handler(
        '/salesforce-cargo/services/data/v53.0/sobjects/Lead/',
    )
    def _handler(request):
        assert (
            request.headers['Authorization'] == 'Bearer database_stored_token'
        )
        body = None
        if sf_response_code in (200, 201):
            body = {'id': '00Q1j000005ci7CEAQ', 'success': True, 'errors': []}
        if sf_response_code in (400,):
            body = [{'errorCode': 'ERROR', 'message': 'surrender'}]
        return mockserver.make_response(status=sf_response_code, json=body)

    response = await taxi_cargo_sf.post(f'{PREFIX}/create-lead', json=REQUEST)
    assert response.status_code == expected_code
    if expected_code in (200, 201):
        assert response.json() == {'id': '00Q1j000005ci7CEAQ'}
    elif expected_code == 400:
        assert response.json() == {
            'code': 'BAD_SALESFORCE_RESPONSE',
            'message': 'surrender',
        }


@pytest.mark.now(const.TOKEN_JUST_UPDATED_TIME)
async def test_func_create_lead_token_invalid(
        taxi_cargo_sf,
        mockserver,
        mock_auth,
        load_json,
        create_auth_token_record,
):
    @mockserver.json_handler(
        '/salesforce-cargo/services/data/v53.0/sobjects/Lead/',
    )
    def _handler(request):
        if request.headers['Authorization'] == 'Bearer database_stored_token':
            return mockserver.make_response(
                status=401,
                json=[{'errorCode': 'ERROR', 'message': 'surrender'}],
            )

        assert request.headers['Authorization'] == 'Bearer token_from_sf'
        return mockserver.make_response(
            status=200,
            json={'id': '00Q1j000005ci7CEAQ', 'success': True, 'errors': []},
        )

    response = await taxi_cargo_sf.post(f'{PREFIX}/create-lead', json=REQUEST)
    assert response.json() == {'id': '00Q1j000005ci7CEAQ'}


@pytest.mark.now(const.TOKEN_NEEDS_UPDATE_TIME)
async def test_func_create_lead_token_timed_out(
        taxi_cargo_sf,
        mockserver,
        mock_auth,
        load_json,
        create_auth_token_record,
):
    @mockserver.json_handler(
        '/salesforce-cargo/services/data/v53.0/sobjects/Lead/',
    )
    def _handler(request):
        assert request.headers['Authorization'] == 'Bearer token_from_sf'
        return mockserver.make_response(
            status=200,
            json={'id': '00Q1j000005ci7CEAQ', 'success': True, 'errors': []},
        )

    response = await taxi_cargo_sf.post(f'{PREFIX}/create-lead', json=REQUEST)
    assert response.json() == {'id': '00Q1j000005ci7CEAQ'}
