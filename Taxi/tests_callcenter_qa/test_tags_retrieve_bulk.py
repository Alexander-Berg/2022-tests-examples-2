import pytest

GET_TAGS_URL = '/cc/v1/callcenter-qa/v1/tags/retrieve_bulk'
ABONENT_PHONE = '+79161234567'


@pytest.mark.now('2020-07-19T11:14:00.00Z')
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_response'],
    (
        pytest.param(
            {},
            200,
            {
                'tags': [
                    {
                        'abonent_phone': 'phone_pd_test_3',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:14:50+0000',
                        'commutation_ids': ['commutation_id_test_7'],
                        'created_at': '2020-07-15T11:15:40+0000',
                        'metaqueue': 'test_disp_queue_2',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid5',
                    },
                    {
                        'abonent_phone': '+79161234567_id',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_1',
                            'commutation_id_test_2',
                            'commutation_id_test_3',
                        ],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid1',
                    },
                    {
                        'abonent_phone': 'phone_pd_test_2',
                        'application': 'test_app_2',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': ['commutation_id_test_6'],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid3',
                    },
                    {
                        'abonent_phone': 'phone_pd_test_2',
                        'application': 'test_app_2',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_6',
                            'commutation_id_test_7',
                        ],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'project': 'help',
                        'reason': 'aggressive_driver',
                        'tag_uuid': 'uuid4',
                    },
                    {
                        'abonent_phone': 'phone_pd_test_3',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid6',
                    },
                    {
                        'abonent_phone': '+79161234567_id',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:13:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_4',
                            'commutation_id_test_5',
                        ],
                        'created_at': '2020-07-15T11:13:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid2',
                    },
                ],
            },
            id='all_tags',
        ),
        pytest.param(
            {'abonent_phone': ABONENT_PHONE},
            200,
            {
                'tags': [
                    {
                        'abonent_phone': '+79161234567_id',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_1',
                            'commutation_id_test_2',
                            'commutation_id_test_3',
                        ],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid1',
                    },
                    {
                        'abonent_phone': '+79161234567_id',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:13:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_4',
                            'commutation_id_test_5',
                        ],
                        'created_at': '2020-07-15T11:13:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid2',
                    },
                ],
            },
            id='filter_phone',
        ),
        pytest.param(
            {'project': 'help'},
            200,
            {
                'tags': [
                    {
                        'abonent_phone': 'phone_pd_test_2',
                        'application': 'test_app_2',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_6',
                            'commutation_id_test_7',
                        ],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'project': 'help',
                        'reason': 'aggressive_driver',
                        'tag_uuid': 'uuid4',
                    },
                ],
            },
            id='project_filter',
        ),
        pytest.param(
            {'application': 'test_app_2'},
            200,
            {
                'tags': [
                    {
                        'abonent_phone': 'phone_pd_test_2',
                        'application': 'test_app_2',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': ['commutation_id_test_6'],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid3',
                    },
                    {
                        'abonent_phone': 'phone_pd_test_2',
                        'application': 'test_app_2',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_6',
                            'commutation_id_test_7',
                        ],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'project': 'help',
                        'reason': 'aggressive_driver',
                        'tag_uuid': 'uuid4',
                    },
                ],
            },
            id='application_filter',
        ),
        pytest.param(
            {'metaqueue': 'test_disp_queue_2'},
            200,
            {
                'tags': [
                    {
                        'abonent_phone': 'phone_pd_test_3',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:14:50+0000',
                        'commutation_ids': ['commutation_id_test_7'],
                        'created_at': '2020-07-15T11:15:40+0000',
                        'metaqueue': 'test_disp_queue_2',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid5',
                    },
                ],
            },
            id='metaqueue_filter',
        ),
        pytest.param(
            {
                'created_from': '2020-07-15T11:14:00.00+0000',
                'created_to': '2020-07-15T11:15:00.00+0000',
            },
            200,
            {
                'tags': [
                    {
                        'abonent_phone': '+79161234567_id',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_1',
                            'commutation_id_test_2',
                            'commutation_id_test_3',
                        ],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid1',
                    },
                    {
                        'abonent_phone': 'phone_pd_test_2',
                        'application': 'test_app_2',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': ['commutation_id_test_6'],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid3',
                    },
                    {
                        'abonent_phone': 'phone_pd_test_2',
                        'application': 'test_app_2',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_6',
                            'commutation_id_test_7',
                        ],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'project': 'help',
                        'reason': 'aggressive_driver',
                        'tag_uuid': 'uuid4',
                    },
                    {
                        'abonent_phone': 'phone_pd_test_3',
                        'application': 'test_app_1',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                        'tag_uuid': 'uuid6',
                    },
                ],
            },
            id='created_filters',
        ),
        pytest.param(
            {'abonent_phone': 'bad_phone_number'},
            200,
            {'tags': []},
            id='no_tags_for_selected_phone',
        ),
        pytest.param(
            {'reason': 'aggressive_driver'},
            200,
            {
                'tags': [
                    {
                        'abonent_phone': 'phone_pd_test_2',
                        'application': 'test_app_2',
                        'blocked_until': '2020-07-19T11:14:40+0000',
                        'commutation_ids': [
                            'commutation_id_test_6',
                            'commutation_id_test_7',
                        ],
                        'created_at': '2020-07-15T11:14:40+0000',
                        'project': 'help',
                        'reason': 'aggressive_driver',
                        'tag_uuid': 'uuid4',
                    },
                ],
            },
            id='filter_reason',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['prepare_tags.sql'])
async def test_base(
        taxi_callcenter_qa,
        request_body,
        expected_status,
        expected_response,
        mock_personal,
        mockserver,
):
    response = await taxi_callcenter_qa.post(GET_TAGS_URL, json=request_body)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.now('2020-07-19T11:14:00.00Z')
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_response'],
    (
        pytest.param(
            {'abonent_phone': ABONENT_PHONE},
            500,
            {
                'code': 'personal_client_error',
                'message': 'Can\'t get personal_phone_id',
            },
            id='error_in_personal_store',
        ),
        pytest.param(
            {},
            500,
            {'code': 'personal_client_error', 'message': 'Can\'t get phones'},
            id='error_in_personal_retrieve_bulk',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['prepare_tags.sql'])
async def test_personal_error(
        taxi_callcenter_qa,
        request_body,
        expected_status,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/store', prefix=True)
    async def _mock_personal_store(request):
        return mockserver.make_response('', status=500)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve', prefix=True)
    async def _mock_personal_retrieve(request):
        return mockserver.make_response('', status=500)

    response = await taxi_callcenter_qa.post(GET_TAGS_URL, json=request_body)
    assert response.status_code == expected_status
    assert response.json() == expected_response
