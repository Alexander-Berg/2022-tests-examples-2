import pytest


@pytest.mark.config(CALLCENTER_REG_STATUS_ROWS_LIMIT=2)
@pytest.mark.parametrize(
    ('projects', 'cursor', 'limit', 'expected_response'),
    [
        (
            None,
            None,
            None,
            {
                'next_cursor': 3,
                'statuses': [
                    {
                        'sip_username': 'sip_1',
                        'user_status': {'status': 'connected'},
                        'update_seq': 1,
                        'project': 'disp',
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                    {
                        'sip_username': 'sip_2',
                        'user_status': {'status': 'connected'},
                        'update_seq': 2,
                        'project': 'disp',
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        ),
        (
            None,
            2,
            None,
            {
                'next_cursor': 4,
                'statuses': [
                    {
                        'sip_username': 'sip_2',
                        'user_status': {'status': 'connected'},
                        'update_seq': 2,
                        'project': 'disp',
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                    {
                        'sip_username': 'sip_3',
                        'user_status': {'status': 'connected'},
                        'update_seq': 3,
                        'project': 'test',
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        ),
        (
            None,
            None,
            1,
            {
                'next_cursor': 2,
                'statuses': [
                    {
                        'sip_username': 'sip_1',
                        'user_status': {'status': 'connected'},
                        'update_seq': 1,
                        'project': 'disp',
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        ),
        (
            ['test'],
            None,
            None,
            {
                'next_cursor': 5,
                'statuses': [
                    {
                        'sip_username': 'sip_3',
                        'user_status': {'status': 'connected'},
                        'update_seq': 3,
                        'project': 'test',
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                    {
                        'sip_username': 'sip_4',
                        'user_status': {'status': 'connected'},
                        'update_seq': 4,
                        'project': 'test',
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        ),
        (None, 100, None, {'next_cursor': 100, 'statuses': []}),
    ],
)
@pytest.mark.pgsql('callcenter_reg', files=['statuses.sql'])
async def test_sip_user_status_by_cursor(
        taxi_callcenter_reg, projects, cursor, limit, expected_response,
):
    response = await taxi_callcenter_reg.post(
        '/v1/sip_user/status/list',
        {'filter': {'projects': projects}, 'cursor': cursor, 'limit': limit},
    )
    # check ok scenario
    assert response.status_code == 200
    assert response.json() == expected_response
