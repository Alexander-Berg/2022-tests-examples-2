import pytest


@pytest.mark.parametrize(
    ('work_status', 'should_block'),
    (
        ('working', False),
        ('not_working', True),
        ('fired', True),
        ('something_else', True),
    ),
)
async def test_filter_work_status(
        mongodb, taxi_candidates, driver_positions, work_status, should_block,
):
    mongodb.dbdrivers.update_one(
        {'_id': 'clid0_uuid0'}, {'$set': {'work_status': work_status}},
    )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/work_status'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'requirements': {},
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = json['drivers']
    if should_block:
        assert not drivers
    else:
        assert len(drivers) == 1
        assert drivers[0]['uuid'] == 'uuid0'
