from aiohttp import web
import pytest

from testsuite.mockserver import classes as mock_types


REVIEW_REQUEST_SHORT_MOCK = {
    'id': 123456,
    'url': 'https://a.yandex-team.ru/review/123456',
}


@pytest.mark.parametrize(
    'responses_filename, expected_error, expected_data',
    [
        pytest.param(
            'arcanum_get_review_request_success_200.json',
            None,
            REVIEW_REQUEST_SHORT_MOCK,
            id='success',
        ),
    ],
)
async def test_get_review_request(
        library_context,
        mock_arcanum,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
        expected_data,
):
    number = 123456
    response = load_json(responses_filename)

    @mock_arcanum(f'/api/v1/review-requests/{number}')
    def _pull_requests_mock_handler(request: mock_types.MockserverRequest):
        return web.json_response(response['json'], status=response['status'])

    call = library_context.arcanum_api.get_review_request(number=number)
    review_request = await _try_call(call, expected_error)

    assert _pull_requests_mock_handler.times_called == 1
    assert review_request.serialize() == expected_data
