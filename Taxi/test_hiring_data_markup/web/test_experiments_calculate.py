import pytest

FILE_REQUESTS = 'requests.json'
FIELD_EXPERIMENTS = 'experiments'
FIELD_FLOW = 'flow'
FIELD_JSON = 'JSON'
FIELD_REQUEST = 'REQUEST'
FIELD_RESPONSE = 'RESPONSE'
FIELD_RESULT = 'result'
FIELD_STATUS = 'STATUS'
FIELD_TICKET_ID = 'ticket_id'


SIMPLE_FIELDS = (FIELD_FLOW, FIELD_TICKET_ID)


def _check_result(result: dict, expected_result: dict):
    for field in SIMPLE_FIELDS:
        assert result[field] == expected_result[field]
    assert sorted(result[FIELD_EXPERIMENTS]) == sorted(
        expected_result[FIELD_EXPERIMENTS],
    )


@pytest.mark.parametrize(
    'request_name', ['NO_FLOW', 'NO_EXPERIMENTS', 'SOURCE_AND_MEDIUM'],
)
async def test_calculate(
        load_json,
        mock_request_calculate,
        mock_personal_api,
        mock_data_markup_experiments3,
        request_name,
):
    requests = load_json(FILE_REQUESTS)[request_name]
    for request in requests:
        body = request[FIELD_REQUEST]
        response = request[FIELD_RESPONSE]
        status = response[FIELD_STATUS]
        expected_response = response[FIELD_JSON]
        response_body = await mock_request_calculate(body, status)
        if FIELD_RESULT not in response_body:
            assert response[FIELD_JSON].items() <= response_body.items()
        else:
            _check_result(
                response_body[FIELD_RESULT], expected_response[FIELD_RESULT],
            )
