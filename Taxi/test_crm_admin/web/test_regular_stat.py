import pytest


@pytest.mark.parametrize(
    'campaign_id, stat',
    [
        (
            1,
            [
                {
                    'planned': 300,
                    'sent': 100,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 200,
                    'status': 'SUCCESS',
                    'scheduled': '2021-01-21T16:00:00+03:00',
                },
                {
                    'planned': 700,
                    'sent': 700,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'SUCCESS',
                    'scheduled': '2021-01-21T15:00:00+03:00',
                },
            ],
        ),
        (
            2,
            [
                {
                    'planned': 0,
                    'sent': 0,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'SEGMENT_EMPTY',
                    'scheduled': '2021-01-22T16:00:00+03:00',
                },
                {
                    'planned': 100,
                    'sent': 100,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'SUCCESS',
                    'scheduled': '2021-01-22T15:00:00+03:00',
                },
            ],
        ),
        (
            3,
            [
                {
                    'planned': 0,
                    'sent': 0,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'SEGMENT_ERROR',
                    'scheduled': '2021-01-23T16:00:00+03:00',
                },
                {
                    'planned': 400,
                    'sent': 300,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'SUCCESS',
                    'scheduled': '2021-01-23T15:00:00+03:00',
                },
            ],
        ),
        (
            4,
            [
                {
                    'planned': 200,
                    'sent': 200,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'SUCCESS',
                    'scheduled': '2021-01-24T16:00:00+03:00',
                },
                {
                    'planned': 0,
                    'sent': 0,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'GROUPS_ERROR',
                    'scheduled': '2021-01-24T15:00:00+03:00',
                },
            ],
        ),
        (
            5,
            [
                {
                    'planned': 0,
                    'sent': 0,
                    'denied': 0,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'GROUPS_ERROR',
                    'scheduled': '2021-01-25T15:00:00+03:00',
                },
            ],
        ),
        (
            6,
            [
                {
                    'planned': 200,
                    'sent': 100,
                    'denied': 100,
                    'skipped': 0,
                    'failed': 0,
                    'status': 'SUCCESS',
                    'scheduled': '2021-01-24T16:00:00+03:00',
                },
            ],
        ),
        (
            7,
            [
                {
                    'planned': 200,
                    'sent': 100,
                    'denied': 0,
                    'skipped': 100,
                    'failed': 0,
                    'status': 'SUCCESS',
                    'scheduled': '2021-01-24T16:00:00+03:00',
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['schedule.sql'])
async def test_regular_stat(web_app_client, campaign_id, stat):
    response = await web_app_client.get(
        '/v1/regular-campaigns/stat', params={'campaign_id': campaign_id},
    )

    assert response.status == 200
    data = await response.json()
    assert data == stat
