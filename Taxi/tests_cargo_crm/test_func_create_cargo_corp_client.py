import pytest

OWNER_YANDEX_UID = 'owner_yandex_uid'
OWNER_YANDEX_LOGIN = 'owner_yandex_login'
CORP_CLIENT_ID = 'corporate_client_identifier_test'
CORP_CLIENT_NAME = 'corporate_client_name'
MOCK_NOW = '2021-05-31T19:00:00+00:00'


@pytest.mark.parametrize('skip_optional', (True, False))
@pytest.mark.parametrize(
    'cargo_corp_code, expected_code', ((200, 200), (500, 500)),
)
async def test_func_create_cargo_corp(
        taxi_cargo_crm,
        mockserver,
        skip_optional,
        cargo_corp_code,
        expected_code,
):
    @mockserver.json_handler('cargo-corp/internal/cargo-corp/v1/client/create')
    def _handler(request):
        expected_headers = {
            'X-B2B-Client-Id': CORP_CLIENT_ID,
            'X-Yandex-UID': OWNER_YANDEX_UID,
            'X-Yandex-Login': OWNER_YANDEX_LOGIN,
        }
        expected_json = {
            'company': {
                'name': CORP_CLIENT_NAME,
                'tin': '1234567890',
                'url': 'gogl.ru',
                'phones': [{'number': '+7912345645'}],
                'emails': [{'text': 'admin@gogl.ru'}],
            },
        }
        if skip_optional:
            del expected_headers['X-Yandex-Login']
            for field in ('name', 'tin', 'url', 'phones', 'emails'):
                del expected_json['company'][field]

        assert all(
            request.headers[key] == value
            for key, value in expected_headers.items()
        )
        assert request.json == expected_json

        body = None
        if cargo_corp_code == 200:
            body = dict(
                expected_json,
                **{
                    'corp_client_id': CORP_CLIENT_ID,
                    'revision': 1,
                    'created_ts': MOCK_NOW,
                    'updated_ts': MOCK_NOW,
                },
            )
        return mockserver.make_response(status=cargo_corp_code, json=body)

    request = {
        'corp_client_id': CORP_CLIENT_ID,
        'yandex_login': OWNER_YANDEX_LOGIN,
        'company_name': CORP_CLIENT_NAME,
        'yandex_uid': OWNER_YANDEX_UID,
        'tin': '1234567890',
        'url': 'gogl.ru',
        'contact_phone': '+7912345645',
        'email': 'admin@gogl.ru',
    }
    if skip_optional:
        for field in ('tin', 'url', 'contact_phone', 'email', 'company_name'):
            del request[field]

    response = await taxi_cargo_crm.post(
        '/functions/create-cargo-corp-client', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {}
