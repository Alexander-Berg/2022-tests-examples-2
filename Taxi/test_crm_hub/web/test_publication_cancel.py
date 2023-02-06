import pytest


@pytest.mark.parametrize(
    'campaign_id, group_id, channel, unpublished_times, '
    'target_result, unpublish_result',
    [
        (1, 1, 'promo', 1, 200, 200),
        (2, 2, 'feeds', 1, 200, 200),
        (2, 2, 'feeds', 1, 500, 400),
        (2, 2, 'feeds', 4, 500, 500),
        (1, 3, None, 0, 200, None),
        (9, 3, None, 0, 404, None),
        (1, 9, None, 0, 404, None),
        (3, 4, 'promo', 1, 200, 200),
        (3, 5, 'promo', 2, 200, 200),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init.sql'])
@pytest.mark.config(
    DRIVER_WALL_CLIENT_QOS={
        '/internal/driver-wall/v1/remove': {'attempts': 4, 'timeout-ms': 250},
    },
)
async def test_cancel(
        mockserver,
        web_app_client,
        campaign_id,
        group_id,
        channel,
        unpublished_times,
        target_result,
        unpublish_result,
):
    is_feeds = is_promo = False

    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/remove')
    async def _unpublish_feeds(request):
        nonlocal is_feeds
        is_feeds = True
        return mockserver.make_response(status=unpublish_result, json={})

    @mockserver.json_handler(
        'communications-audience/communications-audience/v1/unpublish',
    )
    async def _unpublish_promo(request):
        nonlocal is_promo
        is_promo = True
        return mockserver.make_response(status=unpublish_result, json={})

    response = await web_app_client.post(
        '/v1/publication/cancel',
        params={'campaign_id': campaign_id, 'group_id': group_id},
    )

    assert response.status == target_result

    assert (
        unpublished_times
        == _unpublish_promo.times_called + _unpublish_feeds.times_called
    )

    if channel == 'promo':
        assert is_promo and not is_feeds
    if channel == 'feeds':
        assert is_feeds and not is_promo
