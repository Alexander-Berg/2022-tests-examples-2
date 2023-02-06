import collections
import datetime

import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi_maintenance.stuff import update_holded_driver_balances as uhdb


_NOW = datetime.datetime(2018, 1, 1)


_ExpectedData = collections.namedtuple(
    '_ExpectedData', [
        'holded_balance',
        'num_in_progress_subventions',
        'num_latest_subventions',
    ]
)

_SubventionInfo = collections.namedtuple(
    '_SubventionInfo', [
        'alias_id',
        'version',
        'clear_time',
    ]
)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('expected_by_clid_uuid', [
    {
        'clid_new':
            _ExpectedData({'RUB': 110000}, 0, 1),

        'clid_existing':
            _ExpectedData({'RUB': 230000}, 0, 1),

        'clid_already-added':
            _ExpectedData({'AMD': 380000}, 0, 1),

        'clid_new-v2':
            _ExpectedData({'AMD': 450000}, 0, 1),

        'clid_different-currencies':
            _ExpectedData({'AMD': 100000, 'RUB': 200000}, 0, 1),
    }
])
@pytest.mark.filldb(
    holded_driver_balances='for_test_update_holded_driver_balances',
    holded_subventions='for_test_update_holded_driver_balances',
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    SUBVENTIONS_USE_HOLDED_TAXIMETER_DRIVER_BALANCES=False,
)
@pytest.inline_callbacks
def test_update_holded_driver_balances(expected_by_clid_uuid):
    yield uhdb._update_holded_driver_balances(limit=1000)
    actual_by_clid_uuid = yield _get_actual_by_clid_uuid()
    assert actual_by_clid_uuid == expected_by_clid_uuid


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('expected_by_db_id_uuid', [
    {
        ('db_id', 'new'):
            _ExpectedData({'RUB': 110000}, 0, 1),

        ('db_id', 'existing'):
            _ExpectedData({'RUB': 230000}, 0, 1),

        ('db_id', 'already-added'):
            _ExpectedData({'AMD': 380000}, 0, 1),

        ('db_id', 'new-v2'):
            _ExpectedData({'AMD': 450000}, 0, 1),

        ('db_id', 'different-currencies'):
            _ExpectedData({'AMD': 100000, 'RUB': 200000}, 0, 1),
    }
])
@pytest.mark.filldb(
    holded_taximeter_driver_balances='for_test_update_holded_taximeter_driver_balances',
    holded_subventions='for_test_update_holded_driver_balances',
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    SUBVENTIONS_USE_HOLDED_TAXIMETER_DRIVER_BALANCES=True,
)
@pytest.inline_callbacks
def test_update_holded_taximeter_driver_balances(expected_by_db_id_uuid):
    yield uhdb._update_holded_driver_balances(limit=1000)
    actual_by_db_id_uuid = yield _get_actual_by_db_id_uuid()
    assert actual_by_db_id_uuid == expected_by_db_id_uuid


@async.inline_callbacks
def _get_actual_by_clid_uuid():
    all_driver_balances = yield dbh.holded_driver_balances.Doc.find_many()
    result = {
        driver_balance.pk: _make_expected_data(driver_balance)
        for driver_balance in all_driver_balances
    }
    async.return_value(result)


@async.inline_callbacks
def _get_actual_by_db_id_uuid():
    all_driver_balances = yield dbh.holded_taximeter_driver_balances.Doc.find_many()
    result = {
        (driver_balance.db_id, driver_balance.uuid): _make_expected_data(driver_balance)
        for driver_balance in all_driver_balances
    }
    async.return_value(result)


def _make_expected_data(driver_balance):
    return _ExpectedData(
        holded_balance=driver_balance.holded_balance,
        num_in_progress_subventions=len(
            driver_balance.in_progress_subventions
        ),
        num_latest_subventions=len(driver_balance.latest_subventions),
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('clid_uuid,expected', [
    ('all-fresh-subventions-clid_uuid', [
        _SubventionInfo(
            alias_id='all_fresh_alias_id',
            version=1,
            clear_time=datetime.datetime(2018, 1, 1),
        )
    ]),
    ('two-old-subvention-clid_uuid', [
        _SubventionInfo(
            alias_id='two_old_alias_id',
            version=3,
            clear_time=datetime.datetime(2017, 12, 25),
        )
    ]),
    ('respect-status-clid_uuid', [
        _SubventionInfo(
            alias_id='respect_status_alias_id',
            version=1,
            clear_time=datetime.datetime(2017, 11, 26),
        ),
        _SubventionInfo(
            alias_id='respect_status_alias_id',
            version=2,
            clear_time=datetime.datetime(2017, 11, 26),
        )
    ]),
    ('respect-version-clid_uuid', [
        _SubventionInfo(
            alias_id='respect_version_alias_id',
            version=1,
            clear_time=datetime.datetime(2018, 11, 26),
        ),
        _SubventionInfo(
            alias_id='respect_version_alias_id',
            version=2,
            clear_time=datetime.datetime(2017, 11, 26),
        )
    ]),
])
@pytest.mark.filldb(
    holded_driver_balances='for_test_compact_driver_balances',
)
@pytest.inline_callbacks
def test_compact_driver_balances(clid_uuid, expected):
    yield uhdb._compact_driver_balances(dbh.holded_driver_balances.Doc, [clid_uuid])
    actual = yield _get_actual_subvention_infos(clid_uuid)
    assert sorted(actual) == sorted(expected)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('db_id,uuid,expected', [
    ('all-fresh-subventions-db-id', 'uuid', [
        _SubventionInfo(
            alias_id='all_fresh_alias_id',
            version=1,
            clear_time=datetime.datetime(2018, 1, 1),
        )
    ]),
    ('two-old-subvention-db-id', 'uuid', [
        _SubventionInfo(
            alias_id='two_old_alias_id',
            version=3,
            clear_time=datetime.datetime(2017, 12, 25),
        )
    ]),
    ('respect-status-db-id', 'uuid', [
        _SubventionInfo(
            alias_id='respect_status_alias_id',
            version=1,
            clear_time=datetime.datetime(2017, 11, 26),
        ),
        _SubventionInfo(
            alias_id='respect_status_alias_id',
            version=2,
            clear_time=datetime.datetime(2017, 11, 26),
        )
    ]),
    ('respect-version-db-id', 'uuid', [
        _SubventionInfo(
            alias_id='respect_version_alias_id',
            version=1,
            clear_time=datetime.datetime(2018, 11, 26),
        ),
        _SubventionInfo(
            alias_id='respect_version_alias_id',
            version=2,
            clear_time=datetime.datetime(2017, 11, 26),
        )
    ]),
])
@pytest.mark.filldb(
    holded_taximeter_driver_balances='for_test_compact_taximeter_driver_balances',
)
@pytest.inline_callbacks
def test_compact_taximeter_driver_balances(db_id, uuid, expected):
    yield uhdb._compact_driver_balances(dbh.holded_taximeter_driver_balances.Doc, [(db_id, uuid)])
    actual = yield _get_actual_taximeter_subvention_infos(db_id, uuid)
    assert sorted(actual) == sorted(expected)


@async.inline_callbacks
def _get_actual_subvention_infos(clid_uuid):
    balance = yield dbh.holded_driver_balances.Doc.find_one_by_id(clid_uuid)
    result = []
    for subvention in balance.latest_subventions:
        info = _SubventionInfo(
            alias_id=subvention.alias_id,
            version=subvention.version,
            clear_time=subvention.clear_time,
        )
        result.append(info)
    async.return_value(result)


@async.inline_callbacks
def _get_actual_taximeter_subvention_infos(db_id, uuid):
    query = {
        dbh.holded_taximeter_driver_balances.Doc.db_id: db_id,
        dbh.holded_taximeter_driver_balances.Doc.uuid: uuid,
    }
    balance = yield dbh.holded_taximeter_driver_balances.Doc.find_one_or_not_found(query)
    result = []
    for subvention in balance.latest_subventions:
        info = _SubventionInfo(
            alias_id=subvention.alias_id,
            version=subvention.version,
            clear_time=subvention.clear_time,
        )
        result.append(info)
    async.return_value(result)
