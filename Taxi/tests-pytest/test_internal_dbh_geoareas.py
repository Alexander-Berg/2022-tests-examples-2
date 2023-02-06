import datetime

from taxi.core import async
from taxi.internal import dbh

import pytest


_NOW = datetime.datetime(2016, 6, 30)


@pytest.mark.parametrize(
        'name,expected_active_id,expected_removed_ids', [
    # nothing is removed
    ('mytishchi', 'mytishchi_active_id',
     []),
    # one is removed
    ('moscow', 'moscow_active_id',
     ['moscow_inactive_1_id']),
    # several are removed
    ('podolsk', 'podolsk_active_id',
     ['podolsk_inactive_1_id', 'podolsk_inactive_2_id']),
    # several are removed: fixtures have `removed` field set
    ('ekb', 'ekb_active_id',
     ['ekb_inactive_1_id', 'ekb_inactive_2_id']),
])
@pytest.mark.filldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_remove_by_name_earlier(
        name, expected_active_id, expected_removed_ids):
    yield dbh.geoareas.Doc.remove_by_name_earlier(name, _NOW)
    all_active_geoareas = yield dbh.geoareas.Doc.find_active_by_names([name])
    # we can't have more than 1 active geoarea for a name
    assert len(all_active_geoareas) == 1
    active_geoarea = all_active_geoareas[0]
    assert active_geoarea.pk == expected_active_id
    yield assert_geoarea_has_removed_ids(name, expected_removed_ids)


@pytest.mark.parametrize('name,expected_removed_ids', [
    # unknown zone name: nothing is removed
    ('unknown_zone_name', []),
])
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_remove_by_name_earlier_unknown_zone(
        name, expected_removed_ids):
    yield dbh.geoareas.Doc.remove_by_name_earlier(name, _NOW)
    yield assert_geoarea_has_removed_ids(name, expected_removed_ids)


@pytest.mark.filldb(
    geoareas='for_is_known_test',
)
@pytest.mark.parametrize('name,expected_result', [
    ('moscow', True),
    ('unknown_geoarea_name', False),
])
@pytest.inline_callbacks
def test_is_known(name, expected_result):
    actual_result = yield dbh.geoareas.Doc.is_known(name)
    assert actual_result == expected_result


@async.inline_callbacks
def assert_geoarea_has_removed_ids(name, expected_removed_ids):
    query = {
        dbh.geoareas.Doc.name: name,
        dbh.geoareas.Doc.removed: True,
    }
    removed_geoareas = yield dbh.geoareas.Doc.find_many(query)
    removed_ids = [geoarea.pk for geoarea in removed_geoareas]
    assert set(removed_ids) == set(expected_removed_ids)
