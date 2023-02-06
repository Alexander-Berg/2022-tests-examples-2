import pytest

from tests_fleet_synchronizer import common

FLEET_TYPE = common.FLEET_TYPE_VEZET


@pytest.mark.parametrize(
    'parks_for_pg_mappings,expected_docs',
    [
        (['One'], 1),
        (['One', 'Two'], 2),
        (['One', 'Two', 'Three'], 2),
        (['One', 'Two', 'Three', 'Four'], 3),
        (['One', 'Two', 'Three', 'Four', 'Five'], 3),
    ],
)
@pytest.mark.parametrize('disable_park_one', [False, True])
@pytest.mark.config(
    FLEET_SYNCHRONIZER_DKK_PERIOD={'__default__': 10, FLEET_TYPE: 20},
)
async def test_parks_incremental(
        taxi_fleet_synchronizer,
        mongodb,
        pgsql,
        taxi_config,
        parks_for_pg_mappings,
        expected_docs,
        disable_park_one,
):
    assert not list(mongodb.dbparks.find({'fleet_type': FLEET_TYPE}))

    recent_parks = ['One', 'Two', 'Four']
    mongodb.dbparks.update_many(
        {'_id': {'$in': [f'Park{park}' for park in recent_parks]}},
        {
            '$currentDate': {
                'modified_date': {'$type': 'date'},
                'updated_ts': {'$type': 'timestamp'},
            },
        },
    )

    if disable_park_one:
        mongodb.dbparks.update_one(
            {'_id': 'ParkOneMapped'},
            {
                '$setOnInsert': {
                    'is_active': False,
                    'fleet_type': 'uberdriver',
                    'city': 'CityOne',
                    'login': 'loginOne - Таксометр X',
                    'name': 'ParkNameOne - Таксометр X',
                },
                '$currentDate': {
                    'modified_date': {'$type': 'date'},
                    'updated_ts': {'$type': 'timestamp'},
                },
            },
            upsert=True,
        )

    common.clear_parks_mappings(pgsql, FLEET_TYPE)
    common.add_parks_mappings(
        pgsql, [f'Park{park}' for park in parks_for_pg_mappings], FLEET_TYPE,
    )

    await taxi_fleet_synchronizer.invalidate_caches()
    await taxi_fleet_synchronizer.run_periodic_task('parks_incremental')

    docs = list(mongodb.dbparks.find({'fleet_type': FLEET_TYPE}))
    assert len(docs) == expected_docs - int(disable_park_one)
    for doc in docs:
        assert doc['dkk_period'] == 20

    parks_list: list = [
        park for park in recent_parks if park in parks_for_pg_mappings
    ]

    if disable_park_one:
        parks_list.remove('One')
    common.check_parks(docs, parks_list)
