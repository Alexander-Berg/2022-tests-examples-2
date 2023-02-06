import pytest

NOT_EXISTING_ID = '21111111111111111111111111111120'
SERVICE_POINT_ID_1 = '21111111111111111111111111111111'
SERVICE_POINT_ID_2 = '21111111111111111111111111111112'

GOOD_NEW_SERVICE_POINT_1 = {
    'id': '21111111-1111-1111-1111-111111111124',
    'public_point_id': '11111111-1111-1111-1111-111111111112',
    'park_id': '31111111111111111111111111111116',
    'type': 'technician',
    'work_hours': '9:00-16:00',
    'is_active': True,
    'updated_ts': '2020-06-02 00:00:00',
}

GOOD_NEW_SERVICE_POINT_2 = {
    'id': '21111111-1111-1111-1111-111111111125',
    'public_point_id': '11111111-1111-1111-1111-111111111113',
    'park_id': '31111111111111111111111111111116',
    'type': 'physician',
    'work_hours': '9:00-16:00',
    'is_active': False,
    'updated_ts': '2020-06-02 00:00:00',
}

BAD_NEW_SERVICE_POINT_1 = {
    'id': '21111111-1111-1111-1111-111111111111',
    'public_point_id': '11111111-1111-1111-1111-111111111113',
    'park_id': '31111111111111111111111111111116',
    'type': 'physician',
    'work_hours': '9:00-16:00',
    'is_active': False,
    'updated_ts': '2020-06-02 00:00:00',
}

BAD_NEW_SERVICE_POINT_2 = {
    'id': '21111111-1111-1111-1111-111111111129',
    'public_point_id': '11111111-1111-1111-1111-111111111112',
    'park_id': '31111111111111111111111111111116',
    'type': 'physician',
    'work_hours': '9:00-16:00',
    'is_active': False,
    'updated_ts': '2020-06-02 00:00:00',
}

BAD_NEW_SERVICE_POINT_3 = {
    'id': '21111111-1111-1111-1111-111111111124',
    'public_point_id': '11111111-1111-1111-1111-111111111133',
    'park_id': '31111111111111111111111111111116',
    'type': 'technician',
    'work_hours': '9:00-16:00',
    'is_active': False,
    'updated_ts': '2020-06-02 00:00:00',
}

MOCK_NOW = '2020-06-02T00:00:00+00:00'

SERVICE_POINT_FIELDS = [
    'id',
    'public_point_id',
    'park_id',
    'type',
    'work_hours',
    'is_active',
    'updated_ts',
]


def _select_service_point(pgsql, service_point_id):
    cursor = pgsql['edc_app_checkups'].cursor()
    cursor.execute(
        f"""
    SELECT {", ".join(SERVICE_POINT_FIELDS)}
    FROM  edc_app_checkups.service_points
    WHERE id = '{service_point_id}';
    """,
    )
    row = cursor.fetchone()
    result = {}
    if row:
        for i, field in enumerate(SERVICE_POINT_FIELDS):
            result[field] = row[i]
        result['updated_ts'] = str(result['updated_ts'])
    return result


@pytest.mark.pgsql('edc_app_checkups', files=['insert_pps_with_sps.sql'])
@pytest.mark.parametrize(
    'params, expected_status_code, names, expected_response_body',
    [
        (
            {'id': SERVICE_POINT_ID_1},
            200,
            ('SERVICE_POINT_1', 'PUBLIC_POINT_1'),
            {},
        ),
        (
            {'id': SERVICE_POINT_ID_2},
            200,
            ('SERVICE_POINT_2', 'PUBLIC_POINT_1'),
            {},
        ),
        (
            {'id': NOT_EXISTING_ID},
            404,
            None,
            {'code': 'not_found', 'message': 'Service point not found'},
        ),
    ],
)
async def test_get(
        taxi_edc_app_checkups,
        load_json,
        params,
        expected_status_code,
        names,
        expected_response_body,
):
    response = await taxi_edc_app_checkups.get(
        '/v1/service-points/item', params=params,
    )

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        service_points = load_json('pps_with_sps.json')
        expected_response_body = service_points[names[0]]
        expected_response_body['public_point'] = service_points[names[1]]
    assert response.json() == expected_response_body


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('edc_app_checkups', files=['insert_pps_with_sps.sql'])
@pytest.mark.parametrize(
    'request_body, expected_status_code, expected_response_body',
    [
        (GOOD_NEW_SERVICE_POINT_1, 200, {}),
        (GOOD_NEW_SERVICE_POINT_2, 200, {}),
        (
            BAD_NEW_SERVICE_POINT_1,
            400,
            {
                'code': 'could_not_insert',
                'message': (
                    'id (21111111-1111-1111-1111-111111111111) '
                    'violates unique constraint'
                ),
            },
        ),
        (
            BAD_NEW_SERVICE_POINT_2,
            400,
            {
                'code': 'service_type_exist',
                'message': 'Public point has service such type',
            },
        ),
        (
            BAD_NEW_SERVICE_POINT_3,
            400,
            {
                'code': 'public_point_not_exist',
                'message': 'Public point doesn\'t exist',
            },
        ),
    ],
)
async def test_post(
        taxi_edc_app_checkups,
        pgsql,
        request_body,
        expected_status_code,
        expected_response_body,
):
    response = await taxi_edc_app_checkups.post(
        '/v1/service-points', json=request_body,
    )

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        db_service_point = _select_service_point(pgsql, request_body['id'])
        assert db_service_point == request_body
    assert response.json() == expected_response_body


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('edc_app_checkups', files=['insert_pps_with_sps.sql'])
@pytest.mark.parametrize(
    'params, request_body, expected_status_code, expected_response_body',
    [
        (
            {'id': SERVICE_POINT_ID_1},
            {'work_hours': '10:00-15:00', 'is_active': False},
            200,
            {},
        ),
        (
            {'id': NOT_EXISTING_ID},
            {'work_hours': '10:00-15:00', 'is_active': False},
            404,
            {
                'code': 'could_not_update',
                'message': (
                    'service point with id='
                    '21111111-1111-1111-1111-111111111120 doesn\'t exist'
                ),
            },
        ),
    ],
)
async def test_put(
        taxi_edc_app_checkups,
        pgsql,
        params,
        request_body,
        expected_status_code,
        expected_response_body,
):
    response = await taxi_edc_app_checkups.put(
        '/v1/service-points/item', params=params, json=request_body,
    )

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        db_service_point = _select_service_point(pgsql, params['id'])
        assert db_service_point['work_hours'] == request_body['work_hours']
        assert db_service_point['is_active'] == request_body['is_active']
        assert db_service_point['updated_ts'] == '2020-06-02 00:00:00'
    assert response.json() == expected_response_body


CURSOR_LIMIT_2_TYPE_PH_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJwYXJrX2lkI'
    'jpudWxsLCJ0eXBlIjoicGh5c2ljaWFuIn0'
)
CURSOR_LIMIT_2_TYPE_PH_PAGE_2 = (
    'eyJvZmZzZXQiOjIsImxpbWl0IjoyLCJwYXJrX2l'
    'kIjpudWxsLCJ0eXBlIjoicGh5c2ljaWFuIn0'
)
CURSOR_LIMIT_2_TYPE_TEL_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjoyLCJwYXJrX2l'
    'kIjpudWxsLCJ0eXBlIjoidGVsZW1lZGljaW5lIn0'
)
CURSOR_LIMIT_3_PARK_PAGE_1 = (
    'eyJvZmZzZXQiOjAsImxpbWl0IjozLCJwYXJrX2lkIjoiMz'
    'ExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTEiLCJ0eXBlIjpudWxsfQ'
)
CURSOR_LIMIT_3_PARK_PAGE_2 = (
    'eyJvZmZzZXQiOjMsImxpbWl0IjozLCJwYXJrX2lkIjoiMz'
    'ExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTEiLCJ0eXBlIjpudWxsfQ'
)


@pytest.mark.parametrize(
    'request_body, expected_status_code, expected_response_body',
    [
        (
            {'limit': 2, 'query': {'type': 'physician'}},
            200,
            {'cursor': CURSOR_LIMIT_2_TYPE_PH_PAGE_1},
        ),
        (
            {'limit': 2, 'query': {'type': 'telemedicine'}},
            200,
            {'cursor': CURSOR_LIMIT_2_TYPE_TEL_PAGE_1},
        ),
        (
            {
                'limit': 3,
                'query': {'park_id': '31111111111111111111111111111111'},
            },
            200,
            {'cursor': CURSOR_LIMIT_3_PARK_PAGE_1},
        ),
    ],
)
async def test_search_post(
        taxi_edc_app_checkups,
        request_body,
        expected_status_code,
        expected_response_body,
):
    response = await taxi_edc_app_checkups.post(
        '/v1/service-points/search', json=request_body,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_response_body


@pytest.mark.pgsql('edc_app_checkups', files=['insert_pps_with_sps.sql'])
@pytest.mark.parametrize(
    'params, expected_status_code, expected_response_body, names_list',
    [
        (
            {'cursor': CURSOR_LIMIT_2_TYPE_PH_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_TYPE_PH_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_TYPE_PH_PAGE_2,
            },
            [
                ('SERVICE_POINT_7', 'PUBLIC_POINT_5'),
                ('SERVICE_POINT_3', 'PUBLIC_POINT_2'),
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_2_TYPE_PH_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_2_TYPE_PH_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_2_TYPE_PH_PAGE_1,
            },
            [('SERVICE_POINT_1', 'PUBLIC_POINT_1')],
        ),
        (
            {'cursor': CURSOR_LIMIT_2_TYPE_TEL_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_TYPE_TEL_PAGE_1},
            [
                ('SERVICE_POINT_8', 'PUBLIC_POINT_5'),
                ('SERVICE_POINT_5', 'PUBLIC_POINT_4'),
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_3_PARK_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_3_PARK_PAGE_1,
                'cursor_next': CURSOR_LIMIT_3_PARK_PAGE_2,
            },
            [
                ('SERVICE_POINT_8', 'PUBLIC_POINT_5'),
                ('SERVICE_POINT_6', 'PUBLIC_POINT_4'),
                ('SERVICE_POINT_3', 'PUBLIC_POINT_2'),
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_3_PARK_PAGE_2},
            200,
            {
                'cursor': CURSOR_LIMIT_3_PARK_PAGE_2,
                'cursor_prev': CURSOR_LIMIT_3_PARK_PAGE_1,
            },
            [('SERVICE_POINT_1', 'PUBLIC_POINT_1')],
        ),
    ],
)
async def test_search_get(
        taxi_edc_app_checkups,
        load_json,
        params,
        expected_status_code,
        expected_response_body,
        names_list,
):
    response = await taxi_edc_app_checkups.get(
        '/v1/service-points/search', params=params,
    )

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        service_points = load_json('pps_with_sps.json')
        expected_response_body['items'] = []
        for names in names_list:
            if names[0] and names[1]:
                item = service_points[names[0]]
                item['public_point'] = service_points[names[1]]
                expected_response_body['items'].append(item)
    assert response.json() == expected_response_body
