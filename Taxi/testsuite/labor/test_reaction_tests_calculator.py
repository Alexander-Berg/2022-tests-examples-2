import datetime

import pytest


@pytest.mark.config(
    REACTION_TESTS_ENABLED=True,
    REACTION_TESTS_WRITE_TO_DB_ENABLED=True,
    REACTION_TESTS_ENABLED_BY_CITY={'__default__': True},
)
@pytest.mark.now('2018-01-21T23:35:00Z')
@pytest.mark.driver_experiments('reaction_test_gopher')
def test_driver_weariness_calculation(taxi_labor, db, now):
    taxi_labor.run_workers(['reaction-tests-calculator'])
    obj = db.reaction_tests.find_one(
        {'unique_driver_id': '111111111111111111111111'},
    )
    obj.pop('_id')
    assert obj == {
        'created': datetime.datetime(2018, 1, 21, 23, 35),
        'updated': datetime.datetime(2018, 1, 21, 23, 35),
        'type': 'gopher',
        'unique_driver_id': '111111111111111111111111',
    }
    obj = db.reaction_tests.find_one(
        {'unique_driver_id': '111111111111111111111112'},
    )
    assert obj is None
    objs = db.reaction_tests.find(
        {'unique_driver_id': '111111111111111111111113'},
    )
    assert len(list(objs)) == 2
    objs = db.reaction_tests.find(
        {'unique_driver_id': '111111111111111111111114'},
    )
    assert len(list(objs)) == 2
    obj = db.reaction_tests.find_one(
        {'unique_driver_id': '111111111111111111111115'},
    )
    assert obj is None
    objs = db.reaction_tests.find(
        {'unique_driver_id': '111111111111111111111116'},
    )
    assert len(list(objs)) == 2
    objs = db.reaction_tests.find(
        {'unique_driver_id': '111111111111111111111117'},
    )
    assert len(list(objs)) == 1
    obj = db.reaction_tests.find_one(
        {'unique_driver_id': '111111111111111111111118'},
    )
    assert obj is None
