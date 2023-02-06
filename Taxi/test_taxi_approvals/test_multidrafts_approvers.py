import pytest


@pytest.mark.parametrize(
    'query,response_case',
    [
        (
            {'id': 4},
            {
                'approvers_groups': [
                    {
                        'group_name': 'test_name',
                        'approvals_number': 1,
                        'logins': [
                            'papay',
                            'test_login',
                            'test_login_2',
                            'test_login_5',
                        ],
                    },
                ],
            },
        ),
        ({'id': 6}, {'approvers_groups': []}),
    ],
)
@pytest.mark.now('2019-05-14T00:05:00+0000')
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_multidrafts_approvers(
        query, response_case, taxi_approvals_client,
):
    response = await taxi_approvals_client.get(
        '/multidrafts/approvers/', params=query,
    )
    content = await response.json()
    assert response.status == 200
    for approvers_group in content['approvers_groups']:
        approvers_group['logins'].sort()
    assert content == response_case


@pytest.mark.now('2019-05-14T00:05:00+0000')
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_multidrafts_general_approvers(taxi_approvals_client):
    response = await taxi_approvals_client.post(
        '/multidrafts/general_approvers/', json={'drafts_ids': [5, 1]},
    )
    content = await response.json()
    assert response.status == 200
    content['approvers_groups'][0]['logins'].sort()
    assert content == {
        'approvers_groups': [
            {
                'group_name': 'test_name',
                'approvals_number': 1,
                'logins': [
                    'papay',
                    'test_login',
                    'test_login_2',
                    'test_login_5',
                ],
            },
        ],
    }
