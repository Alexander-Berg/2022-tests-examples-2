# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import datetime

import pytest

import yt.yson
from taxi import config
import taxi.internal.yt_driver_stats.temp_order_stats as temp_order_stats
import taxi.internal.yt_driver_stats.update_driver_stats as update_driver_stats
import taxi.internal.yt_driver_stats.valid_badges as valid_badges
import taxi.internal.yt_driver_stats.cypress as cypress
from taxi.util import dates


def _datetime_ts(*args, **kwargs):
    return dates.timestamp_us(datetime.datetime(*args, **kwargs))


@pytest.mark.parametrize("input_row,expected_row", [
    # Map license id row
    (
        {
            "@table_index": 0, "license": "A", "id": 1,
            "updated": _datetime_ts(2017, 9, 1),
        },
        {
            "license": "A", "id": 1, "type": temp_order_stats.ID_ROW,
            "updated": _datetime_ts(2017, 9, 1),
        },
    ),
    # order is not suitable because it"s status is not finished
    (
        {
            "@table_index": 1,
            "status": "finished",
            "taxi_status": "complete1",
            "created": _datetime_ts(2017, 8, 31),
        },
        None,
    ),
    (
        {
            "@table_index": 1,
            "status": "finished1",
            "taxi_status": "complete",
            "created": _datetime_ts(2017, 8, 31),
        },
        None,
    ),
    # some required fields absent
    (
        {
            "@table_index": 1,
            "status": "finished",
            "taxi_status": "complete",
            "performer_driver_license": "A",
            "created": _datetime_ts(2017, 8, 31),
        },
        None,
    ),
    (
        {
            "@table_index": 1,
            "status": "finished",
            "taxi_status": "complete",
            "user_phone_id": "test",
            "created": _datetime_ts(2017, 8, 31),
        },
        None,
    ),
    # city is invalid
    (
        {
            "@table_index": 1,
            "status": "finished",
            "taxi_status": "complete",
            "user_phone_id": "test",
            "performer_driver_license": "A",
            "city": "Test City",
            "created": _datetime_ts(2017, 8, 31),
        },
        None,
    ),
    # order travel_time is too short
    (
        {
            "@table_index": 1,
            "performer_driver_license": "A",
            "id": 4,
            "city": b"Москва",
            "feedback": {
                "rating": 5,
                "created_time": _datetime_ts(2017, 9, 1, 10, 0),
            },
            "created": _datetime_ts(2017, 8, 31),
            "status": "finished",
            "taxi_status": "complete",
            "user_phone_id": "test",
            "statistics": {"travel_time": 179},
        },
        None,
    ),
    # no feedback - only return travel distance
    (
        {
            "@table_index": 1,
            "performer_driver_license": "A",
            "id": 3,
            "city": b"Москва",
            "created": _datetime_ts(2017, 8, 31),
            "status": "finished",
            "taxi_status": "complete",
            "user_phone_id": "test",
            "statistics": {
                "travel_distance": 123.25,
            },
        },
        {
            "rating_reason": None,
            "travel_distance": 123.25,
            "type": temp_order_stats.ORDER_ROW,
            "license": "A",
        },
    ),
    # have feedback but no choices: the same
    (
        {
            "@table_index": 1,
            "performer_driver_license": "A",
            "id": 3,
            "city": b"Москва",
            "created": _datetime_ts(2017, 8, 31),
            "status": "finished",
            "taxi_status": "complete",
            "user_phone_id": "test",
            "statistics": {
                "travel_distance": 123.25,
            },
            "feedback": {}
        },
        {
            "rating_reason": None,
            "travel_distance": 123.25,
            "type": temp_order_stats.ORDER_ROW,
            "license": "A",
        },
    ),
    # no travel distance - should be None
    (
        {
            "@table_index": 1,
            "performer_driver_license": "A",
            "id": 3,
            "city": b"Москва",
            "created": _datetime_ts(2017, 8, 31),
            "status": "finished",
            "taxi_status": "complete",
            "user_phone_id": "test",
            "statistics": {},
            "feedback": {}
        },
        {
            "rating_reason": None,
            "travel_distance": None,
            "type": temp_order_stats.ORDER_ROW,
            "license": "A",
        },
    ),
    # Normal case - everything is present
    (
        {
            "@table_index": 1,
            "performer_driver_license": "A",
            "id": 3,
            "city": b"Москва",
            "created": _datetime_ts(2017, 8, 31),
            "status": "finished",
            "taxi_status": "complete",
            "user_phone_id": "test",
            "statistics": {
                "travel_distance": 123.25,
            },
            "feedback": {
                "choices": {
                    "rating_reason": ["cute_driver"],
                }
            }
        },
        {
            "rating_reason": ["cute_driver"],
            "travel_distance": 123.25,
            "type": temp_order_stats.ORDER_ROW,
            "license": "A",
        },
    ),
    # real data example
    (
        {
            "status": "finished",
            "taxi_status": "complete",
            "city": b"Москва",
            "statistics": {
                "driver_arrived": True,
                "start_transporting_time": 1548942641.802,
                "complete_time": 1548942657.42,
                "driver_delay": 0,
                "corp_ride_report_sent": False,
                "setcared": 1548942628.253,
                "application": "android",
                "start_driving_time": 1548942628.253,
                "travel_time": 1200.618,
                "driver_way_time": 5.459,
                "start_waiting_time": 1548942633.712,
            },
            "feedback": {
                "rating": 5,
                "updated": 1548945130.586,
                "choices": {},
                "created_time": 1548945128.0,
                "is_after_complete": True,
                "call_requested": False,
                "app_comment": False,
            },
            "created": 1548942610.891,
            "@table_index": 1,
            "user_phone_id": "581aff3dc202a785651382cb",
            "id": "1c47f2c1dfbe6abe9ab3fa9b062299af",
            "performer_driver_license": "45A\xd0\xab545598",
        },
        {
            "rating_reason": None,
            "travel_distance": None,
            "type": temp_order_stats.ORDER_ROW,
            "license": "45A\xd0\xab545598",
        },
    ),
])
@pytest.inline_callbacks
@pytest.mark.config(YT_RATINGS_GOOD_ORDER_DURATION=180)
def test_prepare_orders_data_mapper(input_row, expected_row):
    cities = [{"_id": u"Москва"}, {"_id": u"Санкт-Петербург"}]
    end_time = _datetime_ts(2017, 9, 10)
    min_duration = yield config.YT_RATINGS_GOOD_ORDER_DURATION.get()
    mapper = temp_order_stats.PrepareOrdersDataMapper(
        cities, min_duration, end_time)
    yielded = list(mapper(input_row))
    if expected_row:
        assert len(yielded) == 1
        assert expected_row == yielded[0]
    else:
        assert len(yielded) == 0


@pytest.mark.parametrize("key,input_rows,expected_rows", [
    (
        {"license": "A"},
        [
            {
                "id": 1,
                "updated": _datetime_ts(2017, 9, 2),
                "type": temp_order_stats.ID_ROW,
            },
            {
                "id": 2,
                "updated": _datetime_ts(2017, 9, 3),
                "type": temp_order_stats.ID_ROW,
            },
            {
                "order_id": 3,
                "rating_reason": ["cute_driver"],
                "travel_distance": 123.25,
                "type": temp_order_stats.ORDER_ROW,
            },
        ],
        [
            {
                "id": 2,
                "order_id": 3,
                "rating_reason": ["cute_driver"],
                "travel_distance": 123.25,
                "type": temp_order_stats.ORDER_ROW,
            },
        ],
    ),
])
def test_add_driver_id_reducer(key, input_rows, expected_rows):
    reducer = temp_order_stats.AddDriverIdReducer()
    yielded = list(reducer(key, copy.deepcopy(input_rows)))
    assert yielded == expected_rows


@pytest.mark.parametrize("key,input_rows,expected_row", [
    # standard cases, all in one
    (
        {"id": 1},
        [
            {
                "rating_reason": ["cute_driver_1"],
                "travel_distance": 5.1,
                "type": update_driver_stats.NEW_CALCULATED_STATS,
            },
            {
                "rating_reason": ["cute_driver_2"],
                "travel_distance": 10.5,
                "type": update_driver_stats.NEW_CALCULATED_STATS,
            },
            {
                "rating_reason": None,
                "travel_distance": None,
                "type": update_driver_stats.NEW_CALCULATED_STATS,
            },
            {
                "rating_reason": {"cute_driver_1": 10, "cute_driver_2": 5, "cute_driver_3": 100500},
                "travel_distance": 1000,
                "orders_count": 1000,
                "type": update_driver_stats.PREV_STATS_ROW,
            },
        ],
        {
            "_id": 1,
            "rating_reasons": {
                "cute_driver_1": 1 + 10,
                "cute_driver_2": 1 + 5,
                "cute_driver_3": 100500,
            },
            "total_travel_distance": 5.1 + 10.5 + 1000,
            "orders_count": 3 + 1000,
        }
    ),
])
def test_update_driver_stats_reducer(key, input_rows, expected_row):
    reducer = update_driver_stats.UpdateDriverStatsReducer()
    result_row = list(reducer(key, input_rows))
    assert result_row == [expected_row]


@pytest.mark.parametrize("key,input_rows,expected_row", [
    # standard cases, all in one
    (
        {"_id": 1},
        [
            {
                "rating_reasons": {"badge_1": 1, "badge_2": 2},
                "total_travel_distance": 123.456,
                "orders_count": 101,
                "type": valid_badges.OLD_ROW,
            },
            {
                "rating_reasons": {"badge_1": 10, "badge_2": 20, "badge_3": 2},
                "total_travel_distance": 456.789,
                "orders_count": 202,
                "type": valid_badges.NEW_ROW,
            },
        ],
        {
            "_id": 1,
            "rating_reasons": {"badge_1": 9, "badge_2": 18, "badge_3": 2},
            "total_travel_distance": 456.789,
            "orders_count": 202,
        }
    ),
    # one badge is missing somehow from the new row
    (
        {"_id": 2},
        [
            {
                "rating_reasons": {"badge_1": 1, "badge_2": 2},
                "total_travel_distance": 123.456,
                "orders_count": 101,
                "type": valid_badges.OLD_ROW,
            },
            {
                "rating_reasons": {"badge_2": 20, "badge_3": 2},
                "total_travel_distance": 456.789,
                "orders_count": 202,
                "type": valid_badges.NEW_ROW,
            },
        ],
        {
            "_id": 2,
            "rating_reasons": {"badge_2": 18, "badge_3": 2},
            "total_travel_distance": 456.789,
            "orders_count": 202,
        }
    ),
    # new row is missing somehow
    (
        {"_id": 3},
        [
            {
                "rating_reasons": {"badge_1": 10, "badge_2": 20, "badge_3": 2},
                "total_travel_distance": 456.789,
                "orders_count": 202,
                "type": valid_badges.OLD_ROW,
            },
        ],
        None
    ),
    # old row is missing
    (
        {"_id": 4},
        [
            {
                "rating_reasons": {"badge_1": 1, "badge_2": 2},
                "total_travel_distance": 123.456,
                "orders_count": 101,
                "type": valid_badges.NEW_ROW,
            },
        ],
        {
            "_id": 4,
            "rating_reasons": {"badge_1": 1, "badge_2": 2},
            "total_travel_distance": 123.456,
            "orders_count": 101,
        }
    ),
])
def test_calculate_valid_badges_reducer(key, input_rows, expected_row):
    reducer = valid_badges.CalculateValidBadgesReducer()
    result_row = list(reducer(key, input_rows))
    if expected_row:
        assert result_row == [expected_row]
    else:
        assert result_row == []


@pytest.mark.now("2019-01-01 10:00:00")
@pytest.mark.parametrize("upper_bound_ts,cypress_tables_with_attrs,expected_output", [
    # only one table
    (
        datetime.datetime(2018, 1, 1, 0, 0, 0),
        [
            ("driver_stats_2019-02-04_12:27",
             datetime.datetime(2019, 1, 1, 0, 0, 0)),
        ],
        (
            "features/driver_stats/output/driver_stats_2019-02-04_12:27",
            None,
            datetime.datetime(2019, 1, 1, 0, 0, 0),
        )
    ),
    (
        datetime.datetime(2018, 6, 1, 0, 0, 1),
        [
            ("table_1", datetime.datetime(2019, 1, 1, 0, 0, 0)),
            ("table_2", datetime.datetime(2018, 1, 1, 0, 0, 0)),
            ("table_3", datetime.datetime(2018, 6, 1, 0, 0, 0)),
            ("table_4", datetime.datetime(2018, 7, 1, 0, 0, 0)),
            ("table_5", datetime.datetime(2018, 8, 1, 0, 0, 0)),
        ],
        (
            "features/driver_stats/output/table_1",
            "features/driver_stats/output/table_3",
            datetime.datetime(2019, 1, 1, 0, 0, 0),
        )
    ),
    (
        datetime.datetime(2018, 5, 31, 23, 59, 0),
        [
            ("table_2", datetime.datetime(2018, 1, 1, 0, 0, 0)),
            ("table_3", datetime.datetime(2018, 6, 1, 0, 0, 0)),
            ("table_4", datetime.datetime(2018, 7, 1, 0, 0, 0)),
            ("table_1", datetime.datetime(2019, 1, 1, 0, 0, 0)),
            ("table_5", datetime.datetime(2018, 8, 1, 0, 0, 0)),
        ],
        (
            "features/driver_stats/output/table_1",
            "features/driver_stats/output/table_2",
            datetime.datetime(2019, 1, 1, 0, 0, 0),
        )
    ),
])
def test_getting_ts_and_tables_from_cypress(upper_bound_ts,
                                            cypress_tables_with_attrs,
                                            expected_output):
    list_of_yson_strings = yt.yson.YsonList()
    for tup in cypress_tables_with_attrs:
        table_string = yt.yson.YsonString(tup[0])
        table_string.attributes["last_run_timestamp"] = dates.timestamp_us(
            tup[1])
        list_of_yson_strings.append(table_string)
    input_list = list_of_yson_strings
    result = cypress._extract_data_from_cypress_tables(
        input_list,
        upper_bound_ts)
    assert result == expected_output
