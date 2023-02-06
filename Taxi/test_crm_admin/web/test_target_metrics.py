import pytest


@pytest.mark.config(
    CRM_ADMIN_RECOMMENDED_TARGET_METRICS=[
        {'selectors': {'entity': 'User'}, 'metrics': ['user_metric']},
        {'selectors': {'trend': 'eats_trend'}, 'metrics': ['eda_metric']},
        {
            'selectors': {'entity': 'Driver', 'trend': 'driver_trend'},
            'metrics': ['driver_metric'],
        },
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'campaign_id, recommended_metrics',
    [
        (1, ['user_metric']),
        (2, ['eda_metric']),
        (3, ['driver_metric']),
        (4, []),
        (5, None),
    ],
)
async def test_entity_selector(
        web_app_client, campaign_id, recommended_metrics,
):
    response = await web_app_client.get(
        f'/v1/campaigns/{campaign_id}/recommended_metrics',
    )
    if recommended_metrics is not None:
        assert response.status == 200
        assert await response.json() == recommended_metrics
    else:
        assert response.status == 400
