import pytest

FILE_REQUESTS = 'requests.json'
FIELD_CURSOR = 'cursor'
FIELD_JSON = 'JSON'
FIELD_REQUEST = 'REQUEST'
FIELD_RESPONSE = 'RESPONSE'
FIELD_RESULT = 'result'
FIELD_STATUS = 'STATUS'


@pytest.mark.pgsql('hiring_data_markup', files=['pg_hiring_data_markup.sql'])
@pytest.mark.parametrize('request_name', ['NO_HISTORY_PHONE', 'HISTORY_PHONE'])
async def test_history_via_phone(
        load_json, mock_request_history_phone, mock_personal_api, request_name,
):
    requests = load_json(FILE_REQUESTS)[request_name]
    for request in requests:
        body = request[FIELD_REQUEST]
        response = request[FIELD_RESPONSE]
        status = response[FIELD_STATUS]
        expected_response = response[FIELD_JSON]
        response_body = await mock_request_history_phone(body, status)
        assert response_body[FIELD_CURSOR] == expected_response[FIELD_CURSOR]
        result = response_body[FIELD_RESULT]
        expected_result = expected_response[FIELD_RESULT]
        if not expected_result:
            assert not result
        else:
            assert len(result) == len(expected_result)


@pytest.mark.pgsql('hiring_data_markup', files=['pg_hiring_data_markup.sql'])
@pytest.mark.parametrize(
    'request_name', ['NO_HISTORY_TICKET_ID', 'HISTORY_TICKET_ID'],
)
async def test_history_via_ticket_id(
        load_json, mock_request_history_ticket_id, request_name,
):
    requests = load_json(FILE_REQUESTS)[request_name]
    for request in requests:
        body = request[FIELD_REQUEST]
        response = request[FIELD_RESPONSE]
        status = response[FIELD_STATUS]
        expected_response = response[FIELD_JSON]
        response_body = await mock_request_history_ticket_id(body, status)
        assert response_body[FIELD_CURSOR] == expected_response[FIELD_CURSOR]
        result = response_body[FIELD_RESULT]
        expected_result = expected_response[FIELD_RESULT]
        if not expected_result:
            assert not result
        else:
            assert len(result) == len(expected_result)
