import pytest


@pytest.mark.parametrize(
    'campaign_id, group_id, start_id, result',
    [
        # Have tables, but there are no successful sending
        (101, 102, 103, False),
        (101, 103, 104, True),  # Have tables, hve successful sending
        (102, 103, -1, False),  # no tables for this start_id
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init.sql'])
async def test_bulk_result(
        web_app_client, web_context, campaign_id, group_id, start_id, result,
):
    response = await web_app_client.get(
        '/v1/communication/bulk/sent',
        params={
            'campaign_id': campaign_id,
            'group_id': group_id,
            'start_id': start_id,
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data['data'] == result
