import datetime

import pytest

from atlas_backend.generated.cron import run_cron

NOW = datetime.datetime(2021, 1, 1, 0, 10, 0)


@pytest.mark.now(NOW.isoformat())
async def test_update_cities(web_app_client, patch, db):
    assert await db.atlas_cities.count() == 1
    await run_cron.main(['atlas_backend.crontasks.update_cities'])
    assert await db.atlas_cities.count() == 2
    moscow = await db.atlas_cities.find_one({'_id': 'Москва'})
    assert moscow == {
        '_id': 'Москва',
        'br': [5, 0],
        'class': ['courier'],
        'eng': 'moscow',
        'tl': [10, 5],
        'tz': 'Europe/Moscow',
        'main_class': 'econom',
        'geo_center': [7.5, 2.5],
        'geo_polygon': {
            'coordinates': [[[5, 10], [5, 5], [0, 5], [0, 10], [5, 10]]],
            'type': 'Polygon',
        },
        'utcoffset': 3.0,
        'zoom': 11,
        'updated': NOW,
    }
