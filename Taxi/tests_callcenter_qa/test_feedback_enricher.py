import pytest

SAVE_FEEDBACK_URL = '/cc/v1/callcenter-qa/v1/feedback/save'


@pytest.mark.config(
    CALLCENTER_QA_FEEDBACK_SETTINGS={
        'children': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'feedback_enricher',
                    'settings': {'enable_call_info_upload': True},
                },
            ],
        },
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'test_city',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
)
@pytest.mark.parametrize(
    ['request_body', 'expected_db_body'],
    (
        pytest.param(
            'request_1.json',
            (
                'id1',
                {
                    'call_info': {
                        'city': 'test_city',
                        'queue': 'disp_on_1',
                        'fcalled': '+79999999999',
                        'metaqueue': 'disp',
                        'application': 'test_call_center',
                        'personal_phone_id': 'phone_pd_id',
                    },
                    'feedback_info': {'project': 'test_project'},
                },
            ),
            id='successful_creation',
        ),
    ),
)
async def test_create_ticket(
        taxi_callcenter_qa,
        request_body,
        expected_db_body,
        load_json,
        mockserver,
        pgsql,
        mock_callcenter_operators_list_full,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return {'id': 'phone_pd_id', 'value': '+71234567890'}

    @mockserver.json_handler('/callcenter-queues/v1/call_info')
    async def _mock_call_info(request):
        return {
            'personal_phone_id': 'phone_pd_id',
            'called_number': '+79999999999',
            'metaqueue': 'disp',
            'subcluster': '1',
        }

    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': 'test_uid'},
    )
    assert response.status_code == 200

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute('SELECT id, external_info FROM callcenter_qa.feedbacks')
    assert cursor.fetchall()[0] == expected_db_body
    cursor.close()
