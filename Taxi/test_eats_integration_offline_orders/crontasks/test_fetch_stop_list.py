import pytest

from eats_integration_offline_orders.generated.cron import run_cron


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'restaurants_options.sql', 'menu.sql'],
)
async def test_fetch_stop_list(
        cron_context, mockserver, load_json, place_id, restaurant_slug,
):
    @mockserver.handler(
        f'/rkeeper-cloud/api/menu/{restaurant_slug}/availability',
    )
    def _get_menu(request):
        return mockserver.make_response(
            json=load_json('rkeeper_response_data.json'),
        )

    await run_cron.main(
        [
            'eats_integration_offline_orders.crontasks.fetch_stop_list',
            '-t',
            '0',
        ],
    )

    saved_menu = await cron_context.queries.menu.get_by_place_id(place_id)
    assert saved_menu
    assert saved_menu.place_id == place_id
    assert saved_menu.stop_list == {
        'menu_item_id__1': True,
        'menu_item_id__2': False,
    }
