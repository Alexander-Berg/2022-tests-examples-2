import pytest

from tests_cargo_crm import const


PREFIX = '/internal/cargo-crm/flow/phoenixpipe/ticket'


@pytest.mark.parametrize(
    'pipedrive_code, expected_code', ((201, 200), (500, 500)),
)
async def test_func_create_pipedrive_account(
        taxi_cargo_crm, mockserver, pipedrive_code, expected_code, load_json,
):
    @mockserver.json_handler('pipedrive-api/v1/organizations')
    def _handler_o(request):
        body = None
        if pipedrive_code == 201:
            body = load_json('org.json')
        return mockserver.make_response(status=pipedrive_code, json=body)

    @mockserver.json_handler('pipedrive-api/v1/deals')
    def _handler_d(request):
        body = None
        if pipedrive_code == 201:
            body = load_json('deal.json')
        return mockserver.make_response(status=pipedrive_code, json=body)

    @mockserver.json_handler('pipedrive-api/v1/persons')
    def _handler_p(request):
        body = None
        if pipedrive_code == 201:
            body = load_json('person.json')
        return mockserver.make_response(status=pipedrive_code, json=body)

    @mockserver.json_handler('pipedrive-api/v1/notes')
    def _handler_n(request):
        body = None
        if pipedrive_code == 201:
            body = load_json('note.json')
        return mockserver.make_response(status=pipedrive_code, json=body)

    response = await taxi_cargo_crm.post(
        '{}/create-pipedrive-account'.format(PREFIX),
        params={'ticket_id': const.TICKET_ID},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {
            'pipedrive_account': {'deal_id': 1, 'org_id': 2, 'person_id': 3},
        }
