import pytest

SPB = {
    'id': '61711eb7b7e4790047d4fe52',
    'tariff_zone': 'spb',
    'tariffs': ['econom'],
    'branding_types': ['unspecified'],
    'tags': ['super_tag'],
    'created_by': 'user_2',
    'created_at': '2021-10-21T08:03:03.546877+03:00',
    'status': 'FAILED',
    'subvention_start_date': '2021-11-01',
    'subvention_end_date': '2022-11-01',
}
STICKER = {
    'id': '61711eb7b7e4790047d4fe51',
    'tariff_zone': 'moscow',
    'tariffs': ['econom', 'comfort'],
    'branding_types': ['sticker'],
    'tags': [],
    'created_by': 'user_2',
    'created_at': '2021-10-21T09:03:03+03:00',
    'status': 'FINISHED',
    'subvention_start_date': '2021-12-01',
    'subvention_end_date': '2022-12-01',
}
MSK = {
    'id': '61711eb7b7e4790047d4fe50',
    'tariff_zone': 'moscow',
    'tariffs': ['econom'],
    'branding_types': ['unspecified'],
    'tags': [],
    'created_by': 'user',
    'created_at': '2021-10-21T08:03:03.546877+03:00',
    'status': 'CREATED',
    'subvention_start_date': '2021-11-01',
    'subvention_end_date': '2022-11-01',
}
DRAFT = {
    'branding_types': ['unspecified'],
    'created_at': '2022-04-11T12:29:12.277726+03:00',
    'created_by': 'dpano',
    'id': '62541f18637ede004af0cbdc',
    'status': 'DRAFT_CREATED',
    'subvention_end_date': '2022-04-26',
    'subvention_start_date': '2022-04-12',
    'tags': [],
    'tariff_zone': 'novosibirsk',
    'tariffs': ['selfdriving'],
    'draft_id': 777777,
    'ticket': 'RUPRICING-78',
}


@pytest.mark.parametrize(
    'params, expected_content',
    (
        pytest.param(
            {'limit': 4},
            {
                'offset': 0,
                'limit': 4,
                'total': 4,
                'items': [DRAFT, SPB, STICKER, MSK],
            },
        ),
        pytest.param(
            {'limit': 1},
            {'offset': 0, 'limit': 1, 'total': 4, 'items': [DRAFT]},
        ),
        pytest.param(
            {'limit': 10, 'branding_types': ['sticker']},
            {'offset': 0, 'limit': 10, 'total': 1, 'items': [STICKER]},
        ),
        pytest.param(
            {'limit': 10, 'tariff_zone': 'spb'},
            {'offset': 0, 'limit': 10, 'total': 1, 'items': [SPB]},
        ),
        pytest.param(
            {'limit': 10, 'tariffs': ['comfort']},
            {'offset': 0, 'limit': 10, 'total': 1, 'items': [STICKER]},
        ),
        pytest.param(
            {'limit': 10, 'statuses': ['FINISHED', 'FAILED']},
            {'offset': 0, 'limit': 10, 'total': 2, 'items': [SPB, STICKER]},
        ),
        pytest.param(
            {
                'limit': 10,
                'tariff_zone': 'spb',
                'tariffs': ['econom'],
                'branding_types': ['unspecified'],
                'statuses': ['FINISHED', 'FAILED'],
            },
            {'offset': 0, 'limit': 10, 'total': 1, 'items': [SPB]},
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations',
    files=[
        'pg_operations_params.sql',
        'pg_operations_status.sql',
        'pg_operations_result.sql',
    ],
)
async def test_v1_geosubventions_tasks_get(
        web_app_client, params, expected_content,
):
    response = await web_app_client.post(
        f'/v2/operations/filter/', json=params,
    )
    assert response.status == 200
    results = await response.json()
    assert results == expected_content
