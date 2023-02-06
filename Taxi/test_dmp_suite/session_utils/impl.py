# coding: utf-8
from pprint import pformat
import pytest

from nile.api.v1 import Record

from dmp_suite import yt
from dmp_suite.session_utils import HistorySessionIncrementLoader, DatetimeFormat
from dmp_suite.yt import etl
from dmp_suite.yt.operation import write_yt_table, get_temp_table, read_yt_table

from test_dmp_suite.yt.utils import random_yt_table


def session(effective_from, effective_to, lightbox_flg, sticker_flg):
    rec_dict = dict(
        car_number='A777UE',
        park='YANDEX',
        utc_effective_from_dt=effective_from,
        utc_effective_to_dt=effective_to,
        lightbox_flg=lightbox_flg,
        sticker_flg=sticker_flg
    )
    return Record(**rec_dict)


class _HistorySessionTestTable(yt.YTTable):
    user_key = yt.String()
    user_value = yt.String()

class DtHistorySessionTestTable(_HistorySessionTestTable):
    utc_effective_from_dt = yt.Date()
    utc_effective_to_dt = yt.Date()


class DttmHistorySessionTestTable(_HistorySessionTestTable):
    utc_effective_from_dttm = yt.Datetime()
    utc_effective_to_dttm = yt.Datetime()


def _test_history_session_loader(
    default_history_values,
    extend_history_flg,
    initial_data,
    increment_data,
    expected_data,
    start_datetime,
    end_datetime,
    datetime_format
):
    table_class = DtHistorySessionTestTable if datetime_format == DatetimeFormat.dt else DttmHistorySessionTestTable
    table = random_yt_table(table_class)
    history_session_meta = yt.YTMeta(table)

    etl.init_target_table(history_session_meta)
    write_yt_table(
        history_session_meta.target_path(),
        initial_data
    )

    with get_temp_table() as tmp_table:
        write_yt_table(
            tmp_table,
            increment_data
        )
        job = etl.cluster_job(history_session_meta)
        increment = job.table(tmp_table)

        HistorySessionIncrementLoader(
            job=job,
            table=table,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            increment=increment,
            history_key_fields=('user_key', ),
            history_value_fields=('user_value', ),
            datetime_format=datetime_format,
            default_history_values=default_history_values,
            extend_history_flg=extend_history_flg
        ).run()

    actual_data = sorted(
        read_yt_table(history_session_meta.target_path()),
        key=lambda x: (
            x.get('user_key'),
            x.get('utc_effective_from_{}'.format(datetime_format.value))
        )
    )

    assert expected_data == actual_data, \
        'Expected data is different from actual:\nexpected\n{},\nactual\n{}'.format(
            pformat(expected_data), pformat(actual_data)
        )
