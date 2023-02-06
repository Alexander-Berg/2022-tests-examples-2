import pytest

from tests_fleet_synchronizer import common


async def test_parks_full(taxi_fleet_synchronizer, mongodb):
    fleet_type = common.FLEET_TYPE_VEZET
    assert not list(mongodb.dbparks.find({'fleet_type': fleet_type}))

    # has no effect - must show explicitly
    mongodb.dbparks.update_many(
        {'_id': {'$in': ['ParkOne', 'ParkTwo', 'ParkFour']}},
        {
            '$currentDate': {
                'modified_date': {'$type': 'date'},
                'updated_ts': {'$type': 'timestamp'},
            },
        },
    )

    await taxi_fleet_synchronizer.invalidate_caches()
    await taxi_fleet_synchronizer.run_periodic_task('parks_full_update')

    docs = list(mongodb.dbparks.find({'fleet_type': fleet_type}))
    common.check_parks(docs, ['One', 'Three'])


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    queries=[
        f"""
        INSERT INTO fleet_sync.parks_mappings
          (park_id, mapped_park_id, app_family)
        VALUES
          ('ParkOne', 'ParkOneVezet', '{common.FLEET_TYPE_VEZET}')
        ON CONFLICT DO NOTHING;""",
    ],
)
@pytest.mark.config(
    PARKS_SYNCHRONIZER_INCREMENTAL_SETTINGS={
        'vezet': {'cities': [], 'enabled': True, 'park_ids': ['ParkOne']},
    },
)
async def test_mapped_not_active(
        taxi_fleet_synchronizer, mongodb, pgsql, mock_fleet_parks_list,
):
    fleet_type = common.FLEET_TYPE_VEZET
    assert not list(mongodb.dbparks.find({'fleet_type': fleet_type}))

    mongodb.dbparks.insert_one(
        {
            '_id': 'ParkOneVezet',
            'city': 'CityOne',
            'login': 'loginOne - Таксометр X',
            'name': 'ParkNameOne - Таксометр X',
            'fleet_type': fleet_type,
            'is_active': False,
        },
    )

    await taxi_fleet_synchronizer.invalidate_caches()
    await taxi_fleet_synchronizer.run_periodic_task('parks_full_update')

    docs = list(mongodb.dbparks.find({'fleet_type': fleet_type}))
    common.check_parks(docs, ['One'])

    assert docs[0]['_id'] == 'ParkOneVezet'
    assert docs[0]['is_active']
