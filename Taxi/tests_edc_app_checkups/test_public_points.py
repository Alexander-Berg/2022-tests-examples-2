import pytest

PP_ID_2 = '11111111-1111-1111-1111-111111111112'
PP_ID_4 = '11111111-1111-1111-1111-111111111114'
PP_ID_6 = '11111111-1111-1111-1111-111111111116'
NOT_EXISTING_ID = '11111111-1111-1111-1111-111111111120'

NEW_SERVICE_POINT_1 = {
    'id': '21111111-1111-1111-1111-111111111124',
    'park_id': '31111111111111111111111111111116',
    'type': 'technician',
    'work_hours': '9:00-16:00',
    'is_active': True,
    'updated_ts': '2020-06-02 00:00:00',
}

NEW_SERVICE_POINT_1_2 = NEW_SERVICE_POINT_1.copy()
NEW_SERVICE_POINT_1_2['type'] = 'physician'

NEW_SERVICE_POINT_1_3 = NEW_SERVICE_POINT_1.copy()
NEW_SERVICE_POINT_1_3['id'] = '21111111-1111-1111-1111-111111111130'

NEW_SERVICE_POINT_2 = {
    'id': '21111111-1111-1111-1111-111111111125',
    'park_id': '31111111111111111111111111111116',
    'type': 'physician',
    'work_hours': '9:00-17:00',
    'is_active': False,
    'updated_ts': '2020-06-02 00:00:00',
}

NEW_SERVICE_POINT_3 = {
    'id': '21111111-1111-1111-1111-111111111126',
    'park_id': '31111111111111111111111111111116',
    'type': 'telemedicine',
    'work_hours': '9:00-18:00',
    'is_active': False,
    'updated_ts': '2020-06-02 00:00:00',
}

GOOD_NEW_PP_WITH_SPS_1 = {
    'id': '11111111-1111-1111-1111-111111111120',
    'contact': {'name': 'Михаил', 'phone': '+79503334444'},
    'location': {
        'address': 'ул. Серпуховска, 56',
        'latitude': 57.626579,
        'longitude': 39.893872,
    },
    'is_active': True,
    'updated_ts': '2020-06-02 00:00:00',
    'service_points': [],
}

GOOD_NEW_PP_WITH_SPS_2 = {
    'id': '11111111-1111-1111-1111-111111111120',
    'contact': {'name': 'Михаил', 'phone': '+79503334444'},
    'location': {
        'address': 'ул. Серпуховска, 56',
        'latitude': 57.626579,
        'longitude': 39.893872,
    },
    'updated_ts': '2020-06-02 00:00:00',
    'is_active': True,
    'owner_park_id': '31111111111111111111111111111121',
    'service_points': [
        NEW_SERVICE_POINT_1,
        NEW_SERVICE_POINT_2,
        NEW_SERVICE_POINT_3,
    ],
}

BAD_NEW_PUBLIC_POINT_1 = {
    'id': '11111111-1111-1111-1111-111111111113',
    'contact': {'name': 'Михаил', 'phone': '+79503334444'},
    'location': {
        'address': 'ул. Серпуховска, 56',
        'latitude': 57.626579,
        'longitude': 39.893872,
    },
    'is_active': False,
    'service_points': [],
}

BAD_NEW_PUBLIC_POINT_2 = GOOD_NEW_PP_WITH_SPS_1.copy()
BAD_NEW_PUBLIC_POINT_2['service_points'] = [
    NEW_SERVICE_POINT_1,
    NEW_SERVICE_POINT_1_2,
]

BAD_NEW_PUBLIC_POINT_3 = GOOD_NEW_PP_WITH_SPS_1.copy()
BAD_NEW_PUBLIC_POINT_3['service_points'] = [
    NEW_SERVICE_POINT_1,
    NEW_SERVICE_POINT_1_3,
]

UPDATED_PUBLIC_POINT_1 = {
    'id': '11111111-1111-1111-1111-111111111111',
    'contact': {'name': 'Федор', 'phone': '+79503334440'},
    'location': {
        'address': 'ул. Моховая, 53/6',
        'latitude': 57.626567,
        'longitude': 39.893822,
    },
    'is_active': False,
    'owner_park_id': '31111111111111111111111111111121',
    'updated_ts': '2020-06-02 00:00:00',
}

PUBLIC_POINT_FIELDS = [
    'id',
    'address',
    'contact_name',
    'contact_phone',
    'latitude',
    'longitude',
    'is_active',
    'owner_park_id',
    'updated_ts',
]

SERVICE_POINT_FIELDS = [
    'id',
    'park_id',
    'type',
    'work_hours',
    'is_active',
    'updated_ts',
]


def _select_public_point(pgsql, public_point_id):
    cursor = pgsql['edc_app_checkups'].cursor()
    cursor.execute(
        f"""
    SELECT {", ".join(PUBLIC_POINT_FIELDS)}
    FROM  edc_app_checkups.public_points
    WHERE id = '{public_point_id}';
    """,
    )
    row = cursor.fetchone()
    result = {}
    if row:
        result['id'] = row[0]
        result['contact'] = {'name': row[2], 'phone': row[3]}
        result['location'] = {
            'address': row[1],
            'latitude': row[4],
            'longitude': row[5],
        }
        result['is_active'] = row[6]
        if row[7]:
            result['owner_park_id'] = row[7]
        result['updated_ts'] = str(row[8])
    return result


def _select_service_points(pgsql, public_point_id):
    cursor = pgsql['edc_app_checkups'].cursor()
    cursor.execute(
        f"""
    SELECT {", ".join(SERVICE_POINT_FIELDS)}
    FROM  edc_app_checkups.service_points
    WHERE public_point_id = '{public_point_id}';
    """,
    )

    result = []
    rows = cursor.fetchall()
    for row in rows:
        service_point = {}
        for i, field in enumerate(SERVICE_POINT_FIELDS):
            service_point[field] = row[i]
        service_point['updated_ts'] = str(service_point['updated_ts'])
        result.append(service_point)
    return result


@pytest.mark.pgsql('edc_app_checkups', files=['insert_pps_with_sps.sql'])
@pytest.mark.parametrize(
    'params, expected_status_code, names, expected_response_body',
    [
        (
            {'id': PP_ID_2},
            200,
            {'pp_name': 'PUBLIC_POINT_2', 'sp_names': ['SERVICE_POINT_3']},
            {},
        ),
        (
            {'id': PP_ID_4},
            200,
            {
                'pp_name': 'PUBLIC_POINT_4',
                'sp_names': ['SERVICE_POINT_5', 'SERVICE_POINT_6'],
            },
            {},
        ),
        (
            {'id': PP_ID_6},
            200,
            {'pp_name': 'PUBLIC_POINT_6', 'sp_names': []},
            {},
        ),
        (
            {'id': NOT_EXISTING_ID},
            404,
            None,
            {'code': 'not_found', 'message': 'Public point not found'},
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
        '/v1/public-points/item', params=params,
    )

    assert response.status_code == expected_status_code
    if response.status_code == 200:
        pps_with_sps = load_json('pps_with_sps.json')
        expected_response_body = pps_with_sps[names['pp_name']]
        expected_response_body['service_points'] = []
        for sp_name in names['sp_names']:
            expected_response_body['service_points'].append(
                pps_with_sps[sp_name],
            )
    assert response.json() == expected_response_body


@pytest.mark.now('2020-06-02T00:00:00+00:00')
@pytest.mark.pgsql('edc_app_checkups', files=['insert_pps_with_sps.sql'])
@pytest.mark.parametrize(
    'request_body, expected_status_code, expected_response_body',
    [
        (GOOD_NEW_PP_WITH_SPS_1, 200, {}),
        (GOOD_NEW_PP_WITH_SPS_2, 200, {}),
        (
            BAD_NEW_PUBLIC_POINT_1,
            400,
            {
                'code': 'could_not_insert',
                'message': (
                    'ERROR:  duplicate key value violates unique '
                    'constraint "public_points_pkey"\nDETAIL:  Key (id)='
                    '(11111111-1111-1111-1111-111111111113) already exists.\n'
                ),
            },
        ),
        (
            BAD_NEW_PUBLIC_POINT_2,
            400,
            {
                'code': 'could_not_insert',
                'message': (
                    'ERROR:  duplicate key value violates unique '
                    'constraint "service_points_pkey"\nDETAIL:  Key (id)='
                    '(21111111-1111-1111-1111-111111111124) already exists.\n'
                ),
            },
        ),
        (
            BAD_NEW_PUBLIC_POINT_3,
            400,
            {
                'code': 'could_not_insert',
                'message': (
                    'ERROR:  duplicate key value violates unique '
                    'constraint "service_point_pp_id_type_idx"\nDETAIL:  Key '
                    '(public_point_id, type)=(11111111-1111-1111-'
                    '1111-111111111120, technician) already exists.\n'
                ),
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
        '/v1/public-points', json=request_body,
    )

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        db_pp_with_sps = _select_public_point(pgsql, request_body['id'])
        db_pp_with_sps['service_points'] = _select_service_points(
            pgsql, request_body['id'],
        )
        assert db_pp_with_sps == request_body
    assert response.json() == expected_response_body


@pytest.mark.now('2020-06-02T00:00:00+00:00')
@pytest.mark.pgsql('edc_app_checkups', files=['insert_pps_with_sps.sql'])
@pytest.mark.parametrize(
    'params, request_body, expected_status_code, expected_response_body',
    [
        (
            {'id': UPDATED_PUBLIC_POINT_1['id']},
            UPDATED_PUBLIC_POINT_1,
            200,
            {},
        ),
        (
            {'id': GOOD_NEW_PP_WITH_SPS_2['id']},
            GOOD_NEW_PP_WITH_SPS_2,
            404,
            {
                'code': 'could_not_update',
                'message': (
                    'public point with '
                    'id=11111111-1111-1111-1111-111111111120 doesn\'t exist'
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
        '/v1/public-points/item', params=params, json=request_body,
    )

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        public_point = _select_public_point(pgsql, request_body['id'])
        assert public_point == request_body
    assert response.json() == expected_response_body


CURSOR_LIMIT_2_PAGE_1 = (
    'eyJhbnlfb3duZXJfcGFya19pZCI6dHJ1ZSwib3duZXJfcGFya19pZCI6bnVsbCwiaXNfYWN0a'
    'XZlIjpudWxsLCJvZmZzZXQiOjAsImxpbWl0IjoyfQ'
)
CURSOR_LIMIT_2_PAGE_2 = (
    'eyJhbnlfb3duZXJfcGFya19pZCI6dHJ1ZSwib3duZXJfcGFya19pZCI6bnVsbCwiaXNfYWN0a'
    'XZlIjpudWxsLCJvZmZzZXQiOjIsImxpbWl0IjoyfQ'
)
CURSOR_LIMIT_2_PAGE_3 = (
    'eyJhbnlfb3duZXJfcGFya19pZCI6dHJ1ZSwib3duZXJfcGFya19pZCI6bnVsbCwiaXNfYWN0a'
    'XZlIjpudWxsLCJvZmZzZXQiOjQsImxpbWl0IjoyfQ'
)

CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_1 = (
    'eyJhbnlfb3duZXJfcGFya19pZCI6ZmFsc2UsIm93bmVyX3BhcmtfaWQiOm51bGwsImlzX2Fjd'
    'Gl2ZSI6bnVsbCwib2Zmc2V0IjowLCJsaW1pdCI6Mn0'
)
CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_2 = (
    'eyJhbnlfb3duZXJfcGFya19pZCI6ZmFsc2UsIm93bmVyX3BhcmtfaWQiOm51bGwsImlzX2Fjd'
    'Gl2ZSI6bnVsbCwib2Zmc2V0IjoyLCJsaW1pdCI6Mn0'
)

CURSOR_LIMIT_2_PARK_ID_PAGE_1 = (
    'eyJhbnlfb3duZXJfcGFya19pZCI6ZmFsc2UsIm93bmVyX3BhcmtfaWQiOiIzMTExMTExMTExM'
    'TExMTExMTExMTExMTExMTExMTEyMSIsImlzX2FjdGl2ZSI6bnVsbCwib2Zmc2V0IjowLCJsaW'
    '1pdCI6Mn0'
)

CURSOR_LIMIT_3_IS_ACTIVE_PAGE_1 = (
    'eyJhbnlfb3duZXJfcGFya19pZCI6dHJ1ZSwib3duZXJfcGFya19pZCI6bnVsbCwiaXNfYWN0a'
    'XZlIjp0cnVlLCJvZmZzZXQiOjAsImxpbWl0IjozfQ'
)
CURSOR_LIMIT_3_IS_ACTIVE_PAGE_2 = (
    'eyJhbnlfb3duZXJfcGFya19pZCI6dHJ1ZSwib3duZXJfcGFya19pZCI6bnVsbCwiaXNfYWN0a'
    'XZlIjp0cnVlLCJvZmZzZXQiOjMsImxpbWl0IjozfQ'
)
BAD_CURSOR = 'eyZvZmZzZXZiZjIsImxpbWl0IjoyfQ'


@pytest.mark.parametrize(
    'request_body, expected_status_code, expected_response_body',
    [
        (
            {'limit': 2, 'query': {'owner': {'type': 'any'}}},
            200,
            {'cursor': CURSOR_LIMIT_2_PAGE_1},
        ),
        (
            {'limit': 2, 'query': {'owner': {'type': 'none'}}},
            200,
            {'cursor': CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_1},
        ),
        (
            {
                'limit': 2,
                'query': {
                    'owner': {
                        'type': 'park',
                        'park_id': '31111111111111111111111111111121',
                    },
                },
            },
            200,
            {'cursor': CURSOR_LIMIT_2_PARK_ID_PAGE_1},
        ),
        (
            {
                'limit': 3,
                'query': {'owner': {'type': 'any'}, 'is_active': True},
            },
            200,
            {'cursor': CURSOR_LIMIT_3_IS_ACTIVE_PAGE_1},
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
        '/v1/public-points/search', json=request_body,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_response_body


@pytest.mark.pgsql('edc_app_checkups', files=['insert_pps_with_sps.sql'])
@pytest.mark.parametrize(
    'params, expected_status_code, expected_response_body, names_list',
    [
        (
            {'cursor': CURSOR_LIMIT_2_PAGE_1},
            200,
            {
                'cursor': CURSOR_LIMIT_2_PAGE_1,
                'cursor_next': CURSOR_LIMIT_2_PAGE_2,
                'items': [],
            },
            [
                {'pp_name': 'PUBLIC_POINT_6', 'sp_names': []},
                {
                    'pp_name': 'PUBLIC_POINT_5',
                    'sp_names': ['SERVICE_POINT_7', 'SERVICE_POINT_8'],
                },
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_2_PAGE_2},
            200,
            {
                'cursor_prev': CURSOR_LIMIT_2_PAGE_1,
                'cursor': CURSOR_LIMIT_2_PAGE_2,
                'cursor_next': CURSOR_LIMIT_2_PAGE_3,
                'items': [],
            },
            [
                {
                    'pp_name': 'PUBLIC_POINT_4',
                    'sp_names': ['SERVICE_POINT_5', 'SERVICE_POINT_6'],
                },
                {'pp_name': 'PUBLIC_POINT_3', 'sp_names': ['SERVICE_POINT_4']},
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_2_PAGE_3},
            200,
            {
                'cursor_prev': CURSOR_LIMIT_2_PAGE_2,
                'cursor': CURSOR_LIMIT_2_PAGE_3,
                'items': [],
            },
            [
                {'pp_name': 'PUBLIC_POINT_2', 'sp_names': ['SERVICE_POINT_3']},
                {
                    'pp_name': 'PUBLIC_POINT_1',
                    'sp_names': ['SERVICE_POINT_1', 'SERVICE_POINT_2'],
                },
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_1},
            200,
            {
                'cursor_next': CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_2,
                'cursor': CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_1,
                'items': [],
            },
            [
                {
                    'pp_name': 'PUBLIC_POINT_5',
                    'sp_names': ['SERVICE_POINT_7', 'SERVICE_POINT_8'],
                },
                {'pp_name': 'PUBLIC_POINT_3', 'sp_names': ['SERVICE_POINT_4']},
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_2},
            200,
            {
                'cursor_prev': CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_1,
                'cursor': CURSOR_LIMIT_2_NULL_PARK_ID_PAGE_2,
                'items': [],
            },
            [
                {
                    'pp_name': 'PUBLIC_POINT_1',
                    'sp_names': ['SERVICE_POINT_1', 'SERVICE_POINT_2'],
                },
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_2_PARK_ID_PAGE_1},
            200,
            {'cursor': CURSOR_LIMIT_2_PARK_ID_PAGE_1, 'items': []},
            [
                {
                    'pp_name': 'PUBLIC_POINT_4',
                    'sp_names': ['SERVICE_POINT_5', 'SERVICE_POINT_6'],
                },
                {'pp_name': 'PUBLIC_POINT_2', 'sp_names': ['SERVICE_POINT_3']},
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_3_IS_ACTIVE_PAGE_1},
            200,
            {
                'cursor_next': CURSOR_LIMIT_3_IS_ACTIVE_PAGE_2,
                'cursor': CURSOR_LIMIT_3_IS_ACTIVE_PAGE_1,
                'items': [],
            },
            [
                {'pp_name': 'PUBLIC_POINT_6', 'sp_names': []},
                {
                    'pp_name': 'PUBLIC_POINT_5',
                    'sp_names': ['SERVICE_POINT_7', 'SERVICE_POINT_8'],
                },
                {
                    'pp_name': 'PUBLIC_POINT_4',
                    'sp_names': ['SERVICE_POINT_5', 'SERVICE_POINT_6'],
                },
            ],
        ),
        (
            {'cursor': CURSOR_LIMIT_3_IS_ACTIVE_PAGE_2},
            200,
            {
                'cursor_prev': CURSOR_LIMIT_3_IS_ACTIVE_PAGE_1,
                'cursor': CURSOR_LIMIT_3_IS_ACTIVE_PAGE_2,
                'items': [],
            },
            [
                {
                    'pp_name': 'PUBLIC_POINT_1',
                    'sp_names': ['SERVICE_POINT_1', 'SERVICE_POINT_2'],
                },
            ],
        ),
        (
            {'cursor': BAD_CURSOR},
            400,
            {'code': 'could_not_search', 'message': 'Couldn\'t search'},
            None,
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
        '/v1/public-points/search', params=params,
    )

    assert response.status_code == expected_status_code
    if response.status_code == 200:
        pps_with_sps = load_json('pps_with_sps.json')
        for names in names_list:
            pp_with_sps = pps_with_sps[names['pp_name']]
            pp_with_sps['service_points'] = []
            for sp_name in names['sp_names']:
                pp_with_sps['service_points'].append(pps_with_sps[sp_name])
            expected_response_body['items'].append(pp_with_sps)
    assert response.json() == expected_response_body
