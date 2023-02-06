ROUTE_RESULTS_BY_ID = '/exams/v2.0/courses'


def _compare(config, response_body):
    courses = [
        {'course': key, 'description': value['description']}
        for key, value in config.items()
    ]
    courses = sorted(courses, key=lambda x: x['course'])
    actual_courses = sorted(
        response_body['courses'], key=lambda x: x['course'],
    )
    assert courses == actual_courses


async def test_courses(request_exams_platform, taxi_config):
    response = await request_exams_platform(
        url=ROUTE_RESULTS_BY_ID, method='get', expected_response_code=200,
    )
    _compare(
        taxi_config.get_values()['EXAMS_PLATFORM_EXTRA_INFO'], response.json(),
    )
