import datetime

import pytest

# pylint: disable=W0621


async def test_groups_to_send_empty(web_app_client, campaign_exists):
    start_date = datetime.datetime(2019, 11, 20, 1, 0, 0)

    params = {'start_date': str(start_date)}
    response = await web_app_client.get(
        '/v1/campaigns/groups/sending_list', params=params,
    )
    assert response.status == 200
    response = await response.json()
    assert response['list'] == []


@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_groups_to_send(web_app_client, campaign_exists):
    start_date = datetime.datetime(2019, 11, 19, 1, 0, 0)

    params = {'start_date': str(start_date)}
    response = await web_app_client.get(
        '/v1/campaigns/groups/sending_list', params=params,
    )
    assert response.status == 200
    response = await response.json()
    assert response['list'] == [
        {'name': 'Кампания 8', 'path': 'segment6_yt_table'},
    ]
