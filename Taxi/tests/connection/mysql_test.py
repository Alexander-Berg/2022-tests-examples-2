# coding: utf-8
import pytest
import mock
from connection.mysql import MySqlDataIncrement, MySqlDataIncrementById
import dmp_suite.datetime_utils as dtu
from dmp_suite.yt import NotLayeredYtTable, YTMeta, NotLayeredYtLayout


class MockMySqlConnection(object):
    def __init__(self, **kwargs):
        self._tables = kwargs

    def select_union(self, table, fields, start_value, end_value, order_by=None):
        if end_value is None:
            return
        for record in self._tables[table]:
            for field in fields:
                if (
                    record.get(field) is not None
                    and (start_value is None or start_value < record[field])
                    and record[field] <= end_value
                ):
                    yield record

    def get_max_value(self, table, columns):
        values = [
            record[column]
            for record in self._tables[table]
            for column in columns
            if record.get(column) is not None
        ]
        if not values:
            return None
        return max(values)


def patch_ctl(param_value):
    return mock.patch(
        "connection.mysql.get_ctl",
        mock.MagicMock(
            return_value=mock.MagicMock(
                yt=mock.MagicMock(get_param=mock.MagicMock(return_value=param_value))
            )
        ),
    )


class SomeTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout(folder='folder', name='some_table')


TABLE_W_DATES = [
    {"updated_at": dtu.msk("2018-08-01")},
    {"updated_at": dtu.msk("2018-08-02")},
    {"updated_at": dtu.msk("2018-08-03")},
    {"updated_at": dtu.msk("2018-08-04")},
]


def test_default_upper_bound_is_max_value():
    data = MySqlDataIncrement(
        MockMySqlConnection(some_table=TABLE_W_DATES),
        YTMeta(SomeTable),
        update_fields=["updated_at"],
        update_from=dtu.msk("2018-08-02"),
    )
    assert list(data) == [
        {"updated_at": dtu.msk("2018-08-03")},
        {"updated_at": dtu.msk("2018-08-04")},
    ]
    assert data.last_load_date == dtu.msk("2018-08-04")


@patch_ctl(dtu.msk("2018-08-02"))
def test_default_lower_bound_is_queried_from_ctl():
    data = MySqlDataIncrement(
        MockMySqlConnection(some_table=TABLE_W_DATES),
        YTMeta(SomeTable),
        update_fields=["updated_at"],
        update_to=dtu.msk("2018-08-03"),
    )
    assert list(data) == [{"updated_at": dtu.msk("2018-08-03")}]
    assert data.last_load_date == dtu.msk("2018-08-03")


def parametrize(*args):
    """A convenience wrapper for pytest.mark.parametrize."""
    argnames = list(args[1].keys())
    return pytest.mark.parametrize(
        argnames,
        [
            pytest.param(*[case_params[argname] for argname in argnames], id=case_name)
            for case_name, case_params in zip(args[::2], args[1::2])
        ],
    )


@parametrize(
    "when_source_has_new_records",
    dict(
        given_source_records=[{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}],
        given_ctl_value=2,
        expect_records=[{"id": 3}, {"id": 4}],
        expect_last_load_date=4,
    ),
    "when_source_has_single_new_record",
    dict(
        given_source_records=[{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}],
        given_ctl_value=3,
        expect_records=[{"id": 4}],
        expect_last_load_date=4,
    ),
    "when_source_has_no_new_records",
    dict(
        given_source_records=[{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}],
        given_ctl_value=4,
        expect_records=[],
        expect_last_load_date=None,
    ),
    "when_source_has_less_records_than_destination",
    dict(
        given_source_records=[{"id": 1}, {"id": 2}, {"id": 3}],
        given_ctl_value=4,
        expect_records=[],
        expect_last_load_date=None,
    ),
    "when_source_has_no_records",
    dict(
        given_source_records=[],
        given_ctl_value=4,
        expect_records=[],
        expect_last_load_date=None,
    ),
    "when_ctl_is_not_set",
    dict(
        given_source_records=[{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}],
        given_ctl_value=None,
        expect_records=[{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}],
        expect_last_load_date=4,
    ),
    "when_ctl_is_not_set_and_source_has_no_records",
    dict(
        given_source_records=[],
        given_ctl_value=None,
        expect_records=[],
        expect_last_load_date=None,
    ),
)
def test_increment_by_id(
    given_source_records, given_ctl_value, expect_records, expect_last_load_date
):
    with patch_ctl(given_ctl_value):
        data = MySqlDataIncrementById(
            MockMySqlConnection(some_table=given_source_records),
            YTMeta(SomeTable),
            update_field="id",
        )
        records = list(data)
    assert records == expect_records
    if expect_last_load_date is None:
        with pytest.raises(RuntimeError):
            data.last_load_date
    else:
        assert data.last_load_date == expect_last_load_date
