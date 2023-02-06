import pytest


REQUEST_FILE = 'embarks_create.json'
ROUTE_CREATE = '/admin/v1/embark/create'
ROUTE_VALIDATE = '/admin/v1/embark/validate'

QUERY = 'SELECT id FROM hiring_partners_app.embarks;'


@pytest.mark.parametrize(
    'request_type, case',
    [
        ('valid', 'default'),
        ('invalid', 'empty_field'),
        ('invalid', 'end_before_start'),
        ('invalid', 'start_in_past'),
    ],
)
async def test_v1_admin_embarks_create(
        taxi_hiring_partners_app_web, load_json, request_type, case,
):
    data = load_json(REQUEST_FILE)[request_type][case]
    for task in data:
        response = await taxi_hiring_partners_app_web.post(
            path=ROUTE_CREATE, json=task['request'], headers=task['headers'],
        )
        assert response.status == task['response']['status_code']
        body = await response.json()
        assert body == task['response']['body']


@pytest.mark.parametrize(
    'request_type, case',
    [
        ('valid', 'validation_ok'),
        ('invalid', 'start_in_past'),
        ('invalid', 'end_before_start'),
    ],
)
async def test_v1_admin_embarks_validate(
        taxi_hiring_partners_app_web, load_json, request_type, case,
):
    data = load_json(REQUEST_FILE)[request_type][case]
    for task in data:
        response = await taxi_hiring_partners_app_web.post(
            path=ROUTE_VALIDATE, json=task['request'], headers=task['headers'],
        )
        assert response.status == task['response']['status_code']
        body = await response.json()
        assert body == task['response']['body']


@pytest.mark.parametrize(
    'request_type, case',
    [
        ('valid', 'no_intersection_city'),
        ('valid', 'no_intersection_date'),
        ('invalid', 'intersection1'),
        ('invalid', 'intersection2'),
        ('invalid', 'intersection3'),
    ],
)
async def test_embarks_intersection(
        taxi_hiring_partners_app_web, load_json, pgsql, request_type, case,
):
    first_embark = load_json(REQUEST_FILE)['valid']['default'][0]
    await taxi_hiring_partners_app_web.post(
        path=ROUTE_CREATE,
        json=first_embark['request'],
        headers=first_embark['headers'],
    )
    second_embark = load_json(REQUEST_FILE)[request_type][case][0]
    response = await taxi_hiring_partners_app_web.post(
        path=ROUTE_CREATE,
        json=second_embark['request'],
        headers=second_embark['headers'],
    )
    assert response.status == second_embark['response']['status_code']
    body = await response.json()
    assert body == second_embark['response']['body']

    if request_type == 'invalid':
        cursor = pgsql['hiring_partners_app'].cursor()
        cursor.execute(QUERY)
        ids = [row for row in cursor]
        assert ids == [(1,)]
