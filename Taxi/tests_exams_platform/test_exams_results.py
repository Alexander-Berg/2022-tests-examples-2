import pytest

ROUTE_RESULTS_BY_ID = '/exams/v2.0/results/by-id'
ROUTE_RESULTS_BY_IDENTIFIER = '/exams/v2.0/results/by-identifier'
FILE_REQUESTS_BY_ID = 'requests_by_id.json'
FILE_REQUESTS_BY_IDENTIFIER = 'requests_by_identifier.json'


@pytest.mark.now('2022-04-07T12:00:00.345678+00:00')
@pytest.mark.parametrize(
    'route, file, case',
    (
        (
            ROUTE_RESULTS_BY_ID,
            FILE_REQUESTS_BY_ID,
            'valid.existing_default_provider',
        ),
        (
            ROUTE_RESULTS_BY_ID,
            FILE_REQUESTS_BY_ID,
            'valid.existing_with_provider',
        ),
        (
            ROUTE_RESULTS_BY_ID,
            FILE_REQUESTS_BY_ID,
            'valid.existing_with_wrong_provider',
        ),
        (ROUTE_RESULTS_BY_ID, FILE_REQUESTS_BY_ID, 'valid.non_existent'),
        (
            ROUTE_RESULTS_BY_IDENTIFIER,
            FILE_REQUESTS_BY_IDENTIFIER,
            'valid.existing_one',
        ),
        (
            ROUTE_RESULTS_BY_IDENTIFIER,
            FILE_REQUESTS_BY_IDENTIFIER,
            'valid.existing_ensure_order',
        ),
        (
            ROUTE_RESULTS_BY_IDENTIFIER,
            FILE_REQUESTS_BY_IDENTIFIER,
            'valid.existing_with_limit',
        ),
        (
            ROUTE_RESULTS_BY_IDENTIFIER,
            FILE_REQUESTS_BY_IDENTIFIER,
            'valid.existing_with_older_than',
        ),
        (
            ROUTE_RESULTS_BY_IDENTIFIER,
            FILE_REQUESTS_BY_IDENTIFIER,
            'valid.existing_with_older_than_and_limit',
        ),
        (
            ROUTE_RESULTS_BY_IDENTIFIER,
            FILE_REQUESTS_BY_IDENTIFIER,
            'valid.existing_with_different_course',
        ),
        (
            ROUTE_RESULTS_BY_IDENTIFIER,
            FILE_REQUESTS_BY_IDENTIFIER,
            'valid.existing_with_different_id_type',
        ),
        (
            ROUTE_RESULTS_BY_IDENTIFIER,
            FILE_REQUESTS_BY_IDENTIFIER,
            'valid.non_existent',
        ),
    ),
)
async def test_find(request_exams_platform, load_json, route, file, case):
    _type, _name = case.split('.')
    data = load_json(file)[_type][_name]
    await request_exams_platform(
        url=route,
        method='get',
        headers=data['request']['headers'],
        params=data['request']['params'],
        expected_response_code=data['response']['code'],
        expected_response_body=data['response']['body'],
    )
