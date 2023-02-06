import pytest

from crm_admin import audience
import crm_admin.audience.settings as audience_settings


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_campaign_types(web_app_client):
    response = await web_app_client.get('/v1/dictionaries/campaign_types')
    assert response.status == 200
    response = await response.json()

    assert set(item['value'] for item in response) == {'regular', 'oneshot'}


@pytest.mark.parametrize(
    'audience_type',
    [
        item.value
        for item in audience_settings.AudienceType
        if item != audience_settings.AudienceType.ZUSER
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_get_channels(web_app_client, audience_type):

    audience_cmp = audience.get_audience_by_type(audience_type)
    expected_channels = [
        item['value'] for item in audience_cmp.channel.channel_cfg
    ]

    response = await web_app_client.get(
        '/v1/dictionaries/channels', params={'entity': audience_type},
    )
    assert response.status == 200

    answer = await response.json()
    actual = [item['value'] for item in answer]
    assert set(expected_channels) == set(actual)
