import datetime

import pytest

MERGED_ZONES_UPDATE_TIME = '2019-01-27T16:00:00+02:00'

MERGED_ZONES_LIST_RESPONSE = {
    'zone_info': [
        {
            'merged_zones': {
                'active_zones': [
                    {
                        'extern_contour': {
                            'coords': [
                                {'lat': 0.1, 'lon': 0.2},
                                {'lat': 0.2, 'lon': 0.299998},
                                {'lat': 0.1, 'lon': 0.299998},
                                {'lat': 0.033334666666666665, 'lon': 0.2},
                                {'lat': 0.0, 'lon': 0.2},
                                {'lat': 0.0, 'lon': 0.14999800000000002},
                                {'lat': 0.0, 'lon': 0.1},
                                {'lat': 0.1, 'lon': 0.1},
                            ],
                        },
                        'inners': [
                            {
                                'coords': [
                                    {'lat': 0.1, 'lon': 0.2},
                                    {'lat': 0.06666933333333333, 'lon': 0.2},
                                    {'lat': 0.1, 'lon': 0.224998},
                                ],
                            },
                        ],
                    },
                ],
                'soon_zones': [
                    {
                        'extern_contour': {
                            'coords': [
                                {'lat': 0.1, 'lon': 0.2},
                                {'lat': 0.2, 'lon': 0.299998},
                                {'lat': 0.1, 'lon': 0.299998},
                                {'lat': 0.033334666666666665, 'lon': 0.2},
                                {'lat': 0.0, 'lon': 0.2},
                                {'lat': 0.0, 'lon': 0.14999800000000002},
                                {'lat': 0.0, 'lon': 0.1},
                                {'lat': 0.1, 'lon': 0.1},
                            ],
                        },
                        'inners': [
                            {
                                'coords': [
                                    {'lat': 0.1, 'lon': 0.2},
                                    {'lat': 0.06666933333333333, 'lon': 0.2},
                                    {'lat': 0.1, 'lon': 0.224998},
                                ],
                            },
                        ],
                    },
                ],
            },
            'region_id': 213,
            'updated_at': MERGED_ZONES_UPDATE_TIME,
        },
    ],
}


@pytest.mark.pgsql('grocery_depots', files=['msk.sql'])
@pytest.mark.config(GROCERY_DEPOTS_ZONES_MERGE_SYNC_FLAG=True)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_merged_zones_sync(taxi_grocery_depots, mockserver, pgsql):
    @mockserver.json_handler(
        '/grocery-depots-user-view-calc/'
        'internal/v1/depots/v1/merged-zones/list',
    )
    def mock_zone_list_response(request):
        return MERGED_ZONES_LIST_RESPONSE

    response = await taxi_grocery_depots.post(
        '/lavka/v1/depots/v1/merged-zones',
        json={'user_location': {'lat': 55.584227, 'lon': 37.385534}},
    )

    assert response.status_code == 404

    await taxi_grocery_depots.invalidate_caches()
    await taxi_grocery_depots.run_periodic_task(
        'zone-merge-depot-sync-periodic-periodic',
    )

    await taxi_grocery_depots.invalidate_caches()
    response = await taxi_grocery_depots.post(
        '/lavka/v1/depots/v1/merged-zones',
        json={'user_location': {'lat': 55.584227, 'lon': 37.385534}},
    )

    assert mock_zone_list_response.times_called == 1
    assert response.status_code == 200

    merged_zones = response.json()['merged_zones']
    active_zones = merged_zones['active_zones']
    soon_zones = merged_zones['soon_zones']

    assert len(active_zones) == 1
    assert len(active_zones[0]['extern_contour']['coords']) == 8
    assert len(active_zones[0]['inners']) == 1
    assert len(active_zones[0]['inners'][0]['coords']) == 3

    assert len(soon_zones) == 1
    assert len(soon_zones[0]['extern_contour']['coords']) == 8
    assert len(soon_zones[0]['inners']) == 1
    assert len(soon_zones[0]['inners'][0]['coords']) == 3

    update_time = datetime.datetime.fromisoformat(MERGED_ZONES_UPDATE_TIME)

    cursor = pgsql['grocery_depots'].cursor()
    cursor.execute('SELECT updated from depots_wms.merged_zones')
    result = list(row[0] for row in cursor)
    assert result[0] == update_time


async def test_merged_zones_on_wrong_geo(taxi_grocery_depots):
    # 400 on incorrect geo_point
    response = await taxi_grocery_depots.post(
        '/lavka/v1/depots/v1/merged-zones',
        json={'user_location': {'lat': 1000.0, 'lon': 0.0}},
    )

    assert response.status_code == 400

    response = await taxi_grocery_depots.post(
        '/lavka/v1/depots/v1/merged-zones',
        json={'user_location': {'lat': -1000.0, 'lon': -0.0}},
    )

    assert response.status_code == 400

    # 404, no entry in DB
    response = await taxi_grocery_depots.post(
        '/lavka/v1/depots/v1/merged-zones',
        json={'user_location': {'lat': 55.584227, 'lon': 37.385534}},
    )

    assert response.status_code == 404
