from aiohttp import web

from atlas_backend.generated.cron import run_cron


async def test_update_tariffs_list(mock_individual_tariffs, db):
    @mock_individual_tariffs('/internal/v1/tariff-zones')
    def _mock_individual_tariffs(request):  # pylint: disable=unused-variable
        return web.json_response(
            {
                'tariffs': [
                    {
                        'categories': ['econom', 'start', 'vip', 'uberx'],
                        'home_zone': 'kazan',
                    },
                ],
            },
        )

    city = await db.atlas_cities.find_one({'_id': 'Казань'})
    assert city['class'] == ['business', 'econom']
    await run_cron.main(['atlas_backend.crontasks.update_tariffs'])
    city = await db.atlas_cities.find_one({'_id': 'Казань'})
    assert set(city['class']) == {
        'business',
        'econom',
        'start',
        'vip',
        'uberx',
    }
    assert _mock_individual_tariffs.has_calls
