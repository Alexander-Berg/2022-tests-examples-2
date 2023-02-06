import pytest

ROUTE_FAKE_UPLOAD = '/v1.1/upload'
ROUTE_REAL_UPLOAD = '/exams/v2.0/results/upload'
FILE_REQUESTS = 'requests.json'


@pytest.mark.parametrize(
    'route, content_type', [(ROUTE_FAKE_UPLOAD, 'image/*')],
)
async def test_fake_upload(request_exams_platform, route, content_type):
    headers = {'Content-Type': content_type}
    await request_exams_platform(url=route, method='post', headers=headers)


@pytest.mark.now('2022-04-07T12:00:00.345678+00:00')
@pytest.mark.parametrize('legacy_on', (True, False))
@pytest.mark.parametrize(
    'case',
    (
        'invalid.by_grade',
        'invalid.by_course',
        'invalid.by_personal',
        'invalid.by_license',
        'invalid.score_too_low',
        'invalid.new_exam_date_is_older',
        'invalid.legacy_not_found_in_unique_drivers',
        'invalid.legacy_score_too_low',
        'invalid.legacy_new_exam_date_is_older',
        'valid.new_grade_5',
        'valid.multiple_existing_exams',
        'valid.unique_request_id_violation',
        'valid.same_license_id_and_course_new_date',
        'valid.legacy_existing_grade_5',
        'valid.legacy_exam_exists_in_mongo',
    ),
)
async def test_real_upload(
        request_exams_platform, load_json, taxi_config, legacy_on, case,
):
    taxi_config.set_values({'EXAMS_PLATFORM_ENABLE_SAVE_TO_MONGO': legacy_on})
    _type, _name = case.split('.')
    data = load_json(FILE_REQUESTS)[_type][_name]
    if legacy_on is False and _name.startswith('legacy_'):
        data['response']['code'] = 200
        data['response']['body'] = {'id': 'uuid.UUID'}
    await request_exams_platform(
        url=ROUTE_REAL_UPLOAD,
        method='post',
        headers=data['request']['headers'],
        body=data['request']['body'],
        expected_response_code=data['response']['code'],
        expected_response_body=data['response']['body'],
    )
