import pytest

GET_FEEDBACK_URL = '/v1/feedback/info'


@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'response_body'],
    (
        pytest.param(
            {'commutation_id': 'commutation_id_test_1'},
            200,
            {
                'feedbacks': [
                    {
                        'id': 'id1',
                        'type': 'ServerError',
                        'image_link': 'image/test_link',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                ],
            },
            id='simple_request',
        ),
        pytest.param(
            {'commutation_id': 'commutation_id_bad'},
            200,
            {'feedbacks': []},
            id='not_found',
        ),
        pytest.param(
            {'commutation_id': 'commutation_id_test_2'},
            200,
            {
                'feedbacks': [
                    {
                        'id': 'id2',
                        'type': 'ServerError',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                ],
            },
            id='bad_binary_1',
        ),
        pytest.param(
            {'commutation_id': 'commutation_id_test_3'},
            200,
            {
                'feedbacks': [
                    {
                        'id': 'id3',
                        'type': 'ServerError',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                ],
            },
            id='bad_binary_2',
        ),
        pytest.param(
            {'commutation_id': 'commutation_id_test_4'},
            200,
            {
                'feedbacks': [
                    {
                        'id': 'id4',
                        'type': 'ServerError',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                ],
            },
            id='bad_binary_3',
        ),
        pytest.param(
            {'commutation_id': 'commutation_id_test_5'},
            200,
            {
                'feedbacks': [
                    {
                        'id': 'id5',
                        'type': 'ServerError',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                ],
            },
            id='bad_binary_4',
        ),
        pytest.param(
            {'commutation_id': 'commutation_id_test_6'},
            200,
            {
                'feedbacks': [
                    {
                        'id': 'id6',
                        'type': 'ServerError',
                        'image_link': 'image/test_link',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                    {
                        'id': 'id7',
                        'type': 'ServerError2',
                        'image_link': 'image/test_link_2',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                ],
            },
            id='good_request_with_2_feedbacks',
        ),
        pytest.param(
            {'commutation_id': 'commutation_id_test_7'},
            200,
            {
                'feedbacks': [
                    {
                        'id': 'id8',
                        'type': 'ServerError2',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                    {
                        'id': 'id9',
                        'type': 'ServerError',
                        'image_link': 'image/test_link',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                ],
            },
            id='bad_binary_1_with_2_feedbacks',
        ),
        pytest.param(
            {'commutation_id': 'commutation_id_test_8'},
            200,
            {
                'feedbacks': [
                    {
                        'id': 'id10',
                        'type': 'ServerError2',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                    {
                        'id': 'id11',
                        'type': 'ServerError',
                        'created_at': '2020-07-19T08:13:16.425+0000',
                    },
                ],
            },
            id='bad_binary_2_with_2_feedbacks',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['insert_feedback.sql'])
async def test_base(
        taxi_callcenter_qa,
        request_body,
        expected_status,
        response_body,
        mockserver,
):
    @mockserver.handler('/mds-s3-internal', prefix=True)
    def _mock_s3(request):
        return mockserver.make_response('binary_image', 200)

    response = await taxi_callcenter_qa.post(GET_FEEDBACK_URL, request_body)
    assert response.status_code == expected_status
    assert response.json() == response_body
