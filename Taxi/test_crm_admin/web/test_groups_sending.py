import pytest


@pytest.mark.pgsql('crm_admin', files=['groups.sql'])
async def test_group_not_found(web_context, web_app_client):
    response = await web_app_client.get(
        '/v1/campaigns/groups/sending', params={'group_id': -1},
    )

    assert response.status == 404


@pytest.mark.parametrize(
    'group_id, stat',
    [
        (
            3,
            {
                'not_sent': 833,
                'analyzed': 9000,
                'denied': 0,
                'failed': 633,
                'skipped': 200,
                'publication_cancelled': False,
            },
        ),
        (
            4,
            {
                'not_sent': 833,
                'analyzed': 9000,
                'denied': 0,
                'failed': 633,
                'skipped': 200,
                'publication_cancelled': False,
            },
        ),
        (
            5,
            {
                'not_sent': 833,
                'analyzed': 9000,
                'denied': 0,
                'failed': 633,
                'skipped': 200,
                'publication_cancelled': False,
            },
        ),
        (
            6,
            {
                'not_sent': 9833,
                'analyzed': 0,
                'denied': 9000,
                'failed': 633,
                'skipped': 200,
                'publication_cancelled': False,
            },
        ),
        (
            7,
            {
                'not_sent': 9826,
                'analyzed': 0,
                'denied': 8993,
                'failed': 633,
                'skipped': 200,
                'publication_cancelled': False,
            },
        ),
        (
            8,
            {
                'not_sent': 8221,
                'analyzed': 0,
                'denied': 7388,
                'failed': 633,
                'skipped': 200,
                'publication_cancelled': False,
            },
        ),
        (
            9,
            {
                'not_sent': 0,
                'analyzed': 0,
                'denied': 0,
                'failed': 0,
                'skipped': 0,
                'publication_cancelled': False,
            },
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['groups.sql'])
async def test_success(web_app_client, group_id, stat):
    response = await web_app_client.get(
        '/v1/campaigns/groups/sending', params={'group_id': group_id},
    )

    assert response.status == 200
    data = await response.json()
    assert data == stat
