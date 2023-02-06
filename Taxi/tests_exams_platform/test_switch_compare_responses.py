import pytest

ROUTE_COMPARE = '/switch/v1.0/compare-responses'
FILE_REQUESTS = 'requests.json'


@pytest.mark.now('2022-04-07T12:00:00.345678+00:00')
@pytest.mark.parametrize(
    'case',
    (
        'valid.with_warnings',
        'valid.without_warnings',
        'invalid.warnings_mismatch',
        'invalid.ids_error',
    ),
)
async def test_compare(request_exams_platform, load_json, case):
    _type, _name = case.split('.')
    data = load_json(FILE_REQUESTS)[_type][_name]
    await request_exams_platform(
        url=ROUTE_COMPARE,
        method='post',
        body=data['request'],
        expected_response_code=data['response']['code'],
        expected_response_body=data['response']['body'],
    )
