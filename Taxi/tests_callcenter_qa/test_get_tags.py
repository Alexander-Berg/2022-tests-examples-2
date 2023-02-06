import pytest

GET_TAGS_URL = '/v1/tags/info'


@pytest.mark.now('2020-07-19T11:14:00.00Z')
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_response'],
    (
        pytest.param(
            {'personal_phone_id': 'phone_pd_test'},
            200,
            {
                'tags': [
                    {
                        'application': 'test_app_1',
                        'metaqueue': 'test_disp_queue_2',
                        'project': 'disp',
                        'reason': 'children',
                    },
                    {
                        'application': 'test_app_2',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                    },
                    {
                        'application': 'test_app_2',
                        'project': 'help',
                        'reason': 'children',
                    },
                    {
                        'application': 'test_app_1',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                    },
                ],
            },
            id='simple_request',
        ),
        pytest.param(
            {'personal_phone_id': 'phone_pd_test', 'project': 'disp'},
            200,
            {
                'tags': [
                    {
                        'application': 'test_app_1',
                        'metaqueue': 'test_disp_queue_2',
                        'project': 'disp',
                        'reason': 'children',
                    },
                    {
                        'application': 'test_app_2',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                    },
                    {
                        'application': 'test_app_1',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                    },
                ],
            },
            id='project_filter',
        ),
        pytest.param(
            {
                'personal_phone_id': 'phone_pd_test',
                'project': 'disp',
                'application': 'test_app_1',
            },
            200,
            {
                'tags': [
                    {
                        'application': 'test_app_1',
                        'metaqueue': 'test_disp_queue_2',
                        'project': 'disp',
                        'reason': 'children',
                    },
                    {
                        'application': 'test_app_1',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                    },
                ],
            },
            id='application_filter',
        ),
        pytest.param(
            {
                'personal_phone_id': 'phone_pd_test',
                'project': 'disp',
                'metaqueue': 'test_disp_queue_1',
            },
            200,
            {
                'tags': [
                    {
                        'application': 'test_app_2',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                    },
                    {
                        'application': 'test_app_1',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                    },
                ],
            },
            id='metaqueue_filter',
        ),
        pytest.param(
            {
                'personal_phone_id': 'phone_pd_test',
                'project': 'disp',
                'application': 'test_app_1',
                'metaqueue': 'test_disp_queue_1',
            },
            200,
            {
                'tags': [
                    {
                        'application': 'test_app_1',
                        'metaqueue': 'test_disp_queue_1',
                        'project': 'disp',
                        'reason': 'children',
                    },
                ],
            },
            id='all_filters',
        ),
        pytest.param(
            {'personal_phone_id': 'phone_pd_not_found'},
            200,
            {'tags': []},
            id='no_tags_for_selected_pd_phone_id',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['prepare_tags.sql'])
async def test_base(
        taxi_callcenter_qa,
        request_body,
        expected_status,
        expected_response,
        mockserver,
):
    response = await taxi_callcenter_qa.post(GET_TAGS_URL, json=request_body)
    assert response.status_code == expected_status
    assert response.json() == expected_response
