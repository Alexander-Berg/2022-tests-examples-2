from taxi.core import db
from taxi.internal import dbh

import pytest


@pytest.mark.filldb(
    personal_subventions='for_test_on_union_unique_drivers',
    unique_drivers='for_test_on_union_unique_drivers'
)
@pytest.mark.parametrize('id_from,id_to,expected_unique_driver_ids', [
    (
        'some_unique_driver_id', 'another_unique_driver_id',
        ['another_unique_driver_id', 'third_unique_driver_id']
    )
])
@pytest.inline_callbacks
def test_on_union_unique_drivers(
    id_from, id_to, expected_unique_driver_ids):
    unique_driver_from = yield dbh.unique_drivers.Doc.find_one_by_id(id_from)
    unique_driver_to = yield dbh.unique_drivers.Doc.find_one_by_id(id_to)
    yield dbh.personal_subventions.Doc.on_union_unique_drivers(
        unique_driver_from,
        unique_driver_to,
    )
    actual_unique_driver_ids = yield db.personal_subventions.distinct(
        dbh.personal_subventions.Doc.unique_driver_id
    )
    assert sorted(actual_unique_driver_ids) == sorted(
        expected_unique_driver_ids)
