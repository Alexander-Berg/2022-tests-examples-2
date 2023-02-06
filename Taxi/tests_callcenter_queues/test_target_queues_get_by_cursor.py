import pytest


@pytest.mark.config(CALLCENTER_QUEUES_USER_QUEUES_ROWS_LIMIT=2)
@pytest.mark.parametrize(
    ('cursor', 'limit', 'expected_response'),
    [
        (
            None,
            None,
            {
                'next_cursor': 3,
                'queues': [
                    {
                        'sip_username': 'sip_1',
                        'metaqueues': ['test'],
                        'update_seq': 1,
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                    {
                        'sip_username': 'sip_2',
                        'metaqueues': ['disp'],
                        'update_seq': 2,
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        ),
        (
            2,
            None,
            {
                'next_cursor': 4,
                'queues': [
                    {
                        'sip_username': 'sip_2',
                        'metaqueues': ['disp'],
                        'update_seq': 2,
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                    {
                        'sip_username': 'sip_3',
                        'metaqueues': ['help'],
                        'update_seq': 3,
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        ),
        (
            None,
            1,
            {
                'next_cursor': 2,
                'queues': [
                    {
                        'sip_username': 'sip_1',
                        'metaqueues': ['test'],
                        'update_seq': 1,
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        ),
        (100, None, {'next_cursor': 100, 'queues': []}),
    ],
)
@pytest.mark.pgsql('callcenter_queues', files=['target_queues.sql'])
async def test_target_queues_by_cursor(
        taxi_callcenter_queues, cursor, limit, expected_response,
):
    response = await taxi_callcenter_queues.post(
        '/v1/sip_user/queues/list', {'cursor': cursor, 'limit': limit},
    )
    # check ok scenario
    assert response.status_code == 200
    assert response.json() == expected_response
