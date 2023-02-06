import pytest

CORP_CLIENT_ID = 'some_long_id_string_of_length_32'

INITIAL_DESCRIPTION = 'random random string string !@#$%^&'
INITIAL_FEATURES = ['feat1', 'feat2', 'feat3']

DELETED_DESCRIPTION = '[DELETED] ' + INITIAL_DESCRIPTION
DELETED_FEATURES = INITIAL_FEATURES + ['cargo-corp-autoremoved']


@pytest.mark.parametrize(
    (
        'corp_clients_get_response_code',
        'corp_clients_get_response_json',
        'expected_response_code',
    ),
    (
        (
            200,
            {
                'id': CORP_CLIENT_ID,
                'description': INITIAL_DESCRIPTION,
                'features': INITIAL_FEATURES,
            },
            200,
        ),
        (
            200,
            {
                'id': CORP_CLIENT_ID,
                'description': DELETED_DESCRIPTION,
                'features': DELETED_FEATURES,
            },
            200,
        ),
        (404, {'code': '404', 'message': ''}, 200),
        (500, {'code': '500', 'message': ''}, 500),
    ),
)
async def test_func_remove_taxi_corp(
        taxi_cargo_crm,
        mockserver,
        corp_clients_get_response_code,
        corp_clients_get_response_json,
        expected_response_code,
):
    @mockserver.json_handler('/corp-clients-uservices/v1/clients')
    def _handler(request):
        assert request.query['client_id'] == CORP_CLIENT_ID

        code = 200
        json = {}

        if request.method == 'GET':
            for param in ('description', 'features'):
                assert param in request.query['fields']
            code = corp_clients_get_response_code
            json = corp_clients_get_response_json
        else:
            assert request.json['description'] == DELETED_DESCRIPTION
            assert request.json['features'] == DELETED_FEATURES

        return mockserver.make_response(status=code, json=json)

    response = await taxi_cargo_crm.post(
        '/functions/remove-taxi-corp-client',
        json={'corp_client_id': CORP_CLIENT_ID},
    )

    assert response.status_code == expected_response_code
