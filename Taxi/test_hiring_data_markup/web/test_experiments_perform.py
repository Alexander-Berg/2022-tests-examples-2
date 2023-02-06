import pytest

FILE_REQUESTS = 'requests.json'
FIELD_EXPERIMENTS = 'experiments'
FIELD_FIELDS = 'fields'
FIELD_FLOW = 'flow'
FIELD_JSON = 'JSON'
FIELD_NAME = 'name'
FIELD_PHONE = 'phone'
FIELD_REQUEST = 'REQUEST'
FIELD_REQUESTED = 'requested'
FIELD_RESPONSE = 'RESPONSE'
FIELD_RESULT = 'result'
FIELD_STATUS = 'STATUS'
FIELD_TAGS_ADD = 'tags_add'
FIELD_TAGS_REMOVE = 'tags_remove'
FIELD_TICKET_ID = 'ticket_id'
FIELD_VALUE = 'value'


SIMPLE_FIELDS = (FIELD_FLOW, FIELD_TICKET_ID)
TAG_FIELDS = (FIELD_TAGS_ADD, FIELD_TAGS_REMOVE)
CHECK_FIELDS = (FIELD_FIELDS, FIELD_VALUE)
CHECK_EXPERIMENTS = (FIELD_EXPERIMENTS, FIELD_REQUESTED)


def _check_iterable_fields(result, expected, key):
    for field in expected:
        result_value = next(
            (
                item[key]
                for item in result
                if item[FIELD_NAME] == field[FIELD_NAME]
            ),
            None,
        )
        assert result_value is not None
        assert field[key] == result_value


def _check_result(result: dict, expected_result: dict):
    for field in SIMPLE_FIELDS:
        assert result[field] == expected_result[field]
    for field in TAG_FIELDS:
        assert sorted(result[field]) == sorted(expected_result[field])
    for check in [CHECK_FIELDS, CHECK_EXPERIMENTS]:
        _check_iterable_fields(
            result[check[0]], expected_result[check[0]], check[1],
        )


@pytest.fixture
def _ensure_history(
        mock_request_history_ticket_id, mock_request_history_phone,
):
    async def _wrapper(result):
        if result[FIELD_TICKET_ID]:
            history_body = {FIELD_TICKET_ID: result[FIELD_TICKET_ID]}
            await mock_request_history_ticket_id(history_body, 200)
        else:
            phone = next(
                (
                    item[FIELD_VALUE]
                    for item in result[FIELD_FIELDS]
                    if item[FIELD_NAME] == FIELD_PHONE
                ),
                None,
            )
            if phone:
                history_body = {FIELD_PHONE: phone}
                await mock_request_history_phone(history_body, 200)

    return _wrapper


@pytest.mark.parametrize(
    'request_name',
    [
        'NO_ID_FIELDS',
        'NO_FLOW',
        'NO_EXPERIMENTS',
        'SOURCE_AND_MEDIUM',
        'SOURCE_AND_STOP',
        'LOOPS',
        'LOOPS_WITH_SKIP_ALL',
    ],
)
async def test_perform(
        load_json,
        mock_request_perform,
        _ensure_history,
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
        response_body = await mock_request_perform(body, status)
        if FIELD_RESULT not in response_body:
            assert response[FIELD_JSON].items() <= response_body.items()
        else:
            _check_result(
                response_body[FIELD_RESULT], expected_response[FIELD_RESULT],
            )
            await _ensure_history(response_body[FIELD_RESULT])


async def test_perform_only_data(
        load_json,
        mock_request_perform,
        mock_personal_api,
        mock_data_markup_experiments3,
):
    request = load_json(FILE_REQUESTS)['SOURCE_AND_MEDIUM'][0]
    body = request[FIELD_REQUEST]
    status = request[FIELD_RESPONSE][FIELD_STATUS]
    response_body = await mock_request_perform(body, status, {'only_data': 1})
    assert FIELD_EXPERIMENTS not in response_body
