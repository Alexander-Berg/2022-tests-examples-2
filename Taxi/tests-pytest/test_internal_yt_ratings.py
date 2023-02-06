# coding: utf-8
import copy
import datetime

from bson import json_util
import pytest


from taxi import config
import taxi.internal.yt_ratings.core as yt_ratings
from taxi.internal.yt_ratings import helpers
from taxi.util import dates


def _datetime_ts(*args, **kwargs):
    return dates.timestamp_us(datetime.datetime(*args, **kwargs))


@pytest.mark.parametrize('input_row,expected_row', [
    (
        {
            '@table_index': 0, 'license': 'A', 'id': 1,
            'updated': _datetime_ts(2017, 9, 1),
        },
        {
            'license': 'A', 'id': 1, 'type': yt_ratings.ID_ROW,
            'updated': _datetime_ts(2017, 9, 1),
        },
    ),
    (
        {
            '@table_index': 1,
            'profile_licence_serial': 'A',
            'city': 'Москва',
            'created': _datetime_ts(2017, 9, 1),
            'result': 5,
        },
        {
            'license': 'A',
            'city': 'Москва',
            'created': _datetime_ts(2017, 9, 1),
            'exam_score': '5',
            'type': yt_ratings.EXAM_ROW,
        },
    ),
    (
        {
            '@table_index': 1,
            'profile_licence_serial': 'A',
            'city': 'Москва',
            'created': _datetime_ts(2017, 9, 1),
            'result': 10,
        },
        None,
    ),
    (
        {
            '@table_index': 2,
            'driver_license': 'A',
            'state': 'active',
            'requirements': {'charge': True},
        },
        {
            'license': 'A',
            'has_charger': True,
            'type': yt_ratings.CHARGER_ROW,
        },
    ),
    (
        {
            '@table_index': 2,
            'driver_license': 'A',
            'state': 'active',
            'requirements': {},
        },
        None,
    ),
    (
        {
            '@table_index': 3,
            'performer_driver_license': 'A',
            'id': 1,
            'city': 'Москва',
            'feedback': {
                'rating': 4,
                'created_time': _datetime_ts(2017, 9, 1, 10, 0),
            },
            'created': _datetime_ts(2017, 8, 31),
            'status': 'finished',
            'taxi_status': 'complete',
            'user_phone_id': 'test',
            'statistics': {},
        },
        {
            'license': 'A',
            'order_id': 1,
            'city': 'Москва',
            'rating': 4,
            'type': yt_ratings.ORDER_ROW,
            'ts': _datetime_ts(2017, 9, 1, 10, 0),
        },
    ),
    (
        {
            '@table_index': 3,
            'performer_driver_license': 'A',
            'id': 2,
            'city': 'Москва',
            'feedback': {
                'rating': 4,
                'created_time': _datetime_ts(2017, 9, 10, 10, 0),
            },
            'created': _datetime_ts(2017, 8, 31),
            'status': 'finished',
            'taxi_status': 'complete',
            'user_phone_id': 'test',
            'statistics': {},
        },
        None,
    ),
    (
        {
            '@table_index': 3,
            'performer_driver_license': 'A',
            'id': 3,
            'city': 'Test City',
            'feedback': {
                'rating': 4,
                'created_time': _datetime_ts(2017, 9, 1, 10, 0),
            },
            'created': _datetime_ts(2017, 8, 31),
            'status': 'finished',
            'taxi_status': 'complete',
            'user_phone_id': 'test',
            'statistics': {},
        },
        None,
    ),
    (
        {
            '@table_index': 3,
            'performer_driver_license': 'A',
            'id': 4,
            'city': b'Москва',
            'feedback': {
                'rating': 5,
                'created_time': _datetime_ts(2017, 9, 1, 10, 0),
            },
            'created': _datetime_ts(2017, 8, 31),
            'status': 'finished',
            'taxi_status': 'complete',
            'user_phone_id': 'test',
            'statistics': {'travel_time': 120},
        },
        None,
    )
])
@pytest.inline_callbacks
@pytest.mark.config(YT_RATINGS_GOOD_ORDER_DURATION=180)
def test_prepare_orders_data_mapper(input_row, expected_row):
    cities = [{'_id': u'Москва'}, {'_id': u'Санкт-Петербург'}]
    end_time = _datetime_ts(2017, 9, 10)
    min_duration = yield config.YT_RATINGS_GOOD_ORDER_DURATION.get()
    mapper = yt_ratings.PrepareOrdersData(cities, min_duration, end_time)
    yielded = list(mapper(input_row))
    if expected_row:
        assert len(yielded) == 1
        assert expected_row == yielded[0]
    else:
        assert len(yielded) == 0


@pytest.mark.parametrize('key,input_rows,expected_rows', [
    (
        {'license': 'A'},
        [
            {
                'id': 1, 'updated': _datetime_ts(2017, 9, 2),
                'type': yt_ratings.ID_ROW,
            },
            {
                'id': 2, 'updated': _datetime_ts(2017, 9, 3),
                'type': yt_ratings.ID_ROW,
            },
            {'type': yt_ratings.ORDER_ROW},
        ],
        [
            {
                'id': 2,
                'type': yt_ratings.ID_ROW,
            },
            {'type': yt_ratings.ORDER_ROW, 'id': 2},
        ],
    ),
    (
        {'license': 'B'},
        [
            {
                'id': 1, 'updated': _datetime_ts(2017, 9, 1),
                'type': yt_ratings.ID_ROW
            },
        ],
        [
            {'id': 1, 'type': yt_ratings.ID_ROW},
        ],
    )
])
def test_add_id_reducer(key, input_rows, expected_rows):
    reducer = yt_ratings.AddIdReducer()
    yielded = list(reducer(key, copy.deepcopy(input_rows)))
    assert yielded == expected_rows


@pytest.mark.parametrize('key,input_rows,expected_row', [
    # standard cases, all in one
    (
        {'id': 1},
        [
            {
                'exam_score': '5',
                'created': _datetime_ts(2017, 9, 1),
                'type': yt_ratings.EXAM_ROW,
            },
            {
                'exam_score': '1',
                'created': _datetime_ts(2017, 9, 2),
                'type': yt_ratings.EXAM_ROW,
            },
            {'has_charger': True, 'type': yt_ratings.CHARGER_ROW},
            {
                'order_id': 1,
                'rating': 2,
                'ts': _datetime_ts(2017, 9, 5),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'order_id': 2,
                'rating': 5,
                'ts': _datetime_ts(2017, 7, 1),
                'type': yt_ratings.ORDER_ROW,
            },
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(2.62),
            'exam': '1',
            'scores': {
                'rating_count': 1,
                'rating_avg': 2.0,
                'scores': [
                    {
                        'order': 1,
                        'rating': 2,
                        'ts': _datetime_ts(2017, 9, 5)
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_NOVICE,
                        'rating': 4.2,
                        'count': 1,
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_EXAM_BONUS,
                        'rating': 1,
                        'count': 5,
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_CHARGER_BONUS,
                        'rating': 5,
                        'count': 3,
                    }
                ]
            }
        }
    ),
    # rating override cases
    # case A. No orders, just Uber rating override
    (
        {'id': 1},
        [
            {
                'license': 'AB003',
                'created': _datetime_ts(2017, 9, 10, 10),
                'mark': 4.5,
                'type': yt_ratings.RATING_OVERRIDE_ROW,
            },
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(4.5),
            'exam': None,
            'scores': {
                'scores': [
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_OVERRIDE,
                        'rating': 4.5,
                        'count': 2,
                    },
                ]
            }
        }
    ),
    # rating override cases
    # case B. Multiple old orders (with low scores) does not affect Uber rating
    (
        {'id': 1},
        [
            {
                'order_id': 1,
                'rating': 3,
                'ts': _datetime_ts(2017, 9, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'order_id': 2,
                'rating': 3,
                'ts': _datetime_ts(2017, 9, 10, 3),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'order_id': 3,
                'rating': 3,
                'ts': _datetime_ts(2017, 2, 10, 3),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'license': 'AB003',
                'created': _datetime_ts(2017, 9, 10, 10),
                'mark': 4.5,
                'type': yt_ratings.RATING_OVERRIDE_ROW,
            },
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(4.5),
            'exam': None,
            'scores': {
                'rating_count': 2,
                'rating_avg': 3.0,
                'scores': [
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_OVERRIDE,
                        'rating': 4.5,
                        'count': 2,
                    },
                ]
            }
        }
    ),
    # rating override cases
    # case C. Old orders with score higher than Uber scores, still this scores
    (
        {'id': 1},
        [
            {
                'order_id': 1,
                'rating': 4.9,
                'ts': _datetime_ts(2017, 9, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'order_id': 2,
                'rating': 4.9,
                'ts': _datetime_ts(2017, 9, 10, 3),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'order_id': 3,
                'rating': 3,
                'ts': _datetime_ts(2017, 2, 10, 3),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'license': 'AB003',
                'created': _datetime_ts(2017, 9, 10, 10),
                'mark': 4.5,
                'type': yt_ratings.RATING_OVERRIDE_ROW,
            },
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(4.9),
            'exam': None,
            'scores': {
                'rating_count': 2,
                'rating_avg': 4.9,
                'scores': [
                    {
                        'order': 1,
                        'rating': 4.9,
                        'ts': _datetime_ts(2017, 9, 10, 2)
                    },
                    {
                        'order': 2,
                        'rating': 4.9,
                        'ts': _datetime_ts(2017, 9, 10, 3)
                    },
                ]
            }
        }
    ),
    # rating override cases
    # case D. One new order, and Uber override. Uber rating is blurred with it
    (
        {'id': 1},
        [
            {
                'order_id': 1,
                'rating': 3.5,
                'ts': _datetime_ts(2017, 10, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'license': 'AB003',
                'created': _datetime_ts(2017, 9, 10, 10),
                'mark': 4.5,
                'type': yt_ratings.RATING_OVERRIDE_ROW,
            },
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(4.0),
            'exam': None,
            'scores': {
                'rating_count': 1,
                'rating_avg': 3.5,
                'scores': [
                    {
                        'order': 1,
                        'rating': 3.5,
                        'ts': _datetime_ts(2017, 10, 10, 2)
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_OVERRIDE,
                        'rating': 4.5,
                        'count': 1,
                    },
                ]
            }
        }
    ),
    # rating override cases
    # case E. Two new orders, and Uber override. Fully blurred Uber rating
    (
        {'id': 1},
        [
            {
                'order_id': 1,
                'rating': 3.5,
                'ts': _datetime_ts(2017, 10, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'order_id': 2,
                'rating': 4.0,
                'ts': _datetime_ts(2017, 11, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'license': 'AB003',
                'created': _datetime_ts(2017, 9, 10, 10),
                'mark': 4.5,
                'type': yt_ratings.RATING_OVERRIDE_ROW,
            },
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(3.75),
            'exam': None,
            'scores': {
                'rating_count': 2,
                'rating_avg': 3.75,
                'scores': [
                    {
                        'order': 1,
                        'rating': 3.5,
                        'ts': _datetime_ts(2017, 10, 10, 2)
                    },
                    {
                        'order': 2,
                        'rating': 4.0,
                        'ts': _datetime_ts(2017, 11, 10, 2)
                    },
                ]
            }
        }
    ),
    # rating override cases
    # case F, everything in one. Like D but with exam and charger extra scores
    (
        {'id': 1},
        [
            {
                'order_id': 1,
                'rating': 3.5,
                'ts': _datetime_ts(2017, 10, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'license': 'AB003',
                'created': _datetime_ts(2017, 9, 10, 10),
                'mark': 4.5,
                'type': yt_ratings.RATING_OVERRIDE_ROW,
            },
            {
                'exam_score': '5',
                'created': _datetime_ts(2017, 9, 1),
                'type': yt_ratings.EXAM_ROW,
            },
            {
                'exam_score': '1',
                'created': _datetime_ts(2017, 9, 2),
                'type': yt_ratings.EXAM_ROW,
            },
            {'has_charger': True, 'type': yt_ratings.CHARGER_ROW},
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(2.8),
            'exam': '1',
            'scores': {
                'rating_count': 1,
                'rating_avg': 3.5,
                'scores': [
                    {
                        'order': 1,
                        'rating': 3.5,
                        'ts': _datetime_ts(2017, 10, 10, 2)
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_OVERRIDE,
                        'rating': 4.5,
                        'count': 1,
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_EXAM_BONUS,
                        'rating': 1,
                        'count': 5,
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_CHARGER_BONUS,
                        'rating': 5,
                        'count': 3,
                    }
                ]
            }
        }
    ),
    # rating override cases
    # case G, everything in one, plus Uber rating override fully blurred
    (
        {'id': 1},
        [
            {
                'order_id': 1,
                'rating': 3.5,
                'ts': _datetime_ts(2017, 10, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'order_id': 2,
                'rating': 3.5,
                'ts': _datetime_ts(2017, 11, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'license': 'AB003',
                'created': _datetime_ts(2017, 9, 10, 10),
                'mark': 4.5,
                'type': yt_ratings.RATING_OVERRIDE_ROW,
            },
            {
                'exam_score': '5',
                'created': _datetime_ts(2017, 9, 1),
                'type': yt_ratings.EXAM_ROW,
            },
            {
                'exam_score': '1',
                'created': _datetime_ts(2017, 9, 2),
                'type': yt_ratings.EXAM_ROW,
            },
            {'has_charger': True, 'type': yt_ratings.CHARGER_ROW},
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(2.7),
            'exam': '1',
            'scores': {
                'rating_count': 2,
                'rating_avg': 3.5,
                'scores': [
                    {
                        'order': 1,
                        'rating': 3.5,
                        'ts': _datetime_ts(2017, 10, 10, 2)
                    },
                    {
                        'order': 2,
                        'rating': 3.5,
                        'ts': _datetime_ts(2017, 11, 10, 2)
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_EXAM_BONUS,
                        'rating': 1,
                        'count': 5,
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_CHARGER_BONUS,
                        'rating': 5,
                        'count': 3,
                    }
                ]
            }
        }
    ),
    # Case H, one order with 5.0, novice, Uber 5.0:
    # Apply Uber override and don't add novice rating
    (
        {'id': 1},
        [
            {
                'order_id': 1,
                'rating': 5.0,
                'ts': _datetime_ts(2017, 10, 10, 2),
                'type': yt_ratings.ORDER_ROW,
            },
            {
                'license': 'AB003',
                'created': _datetime_ts(2017, 9, 10, 10),
                'mark': 5.0,
                'type': yt_ratings.RATING_OVERRIDE_ROW,
            },
        ],
        {
            '_id': 1,
            'rating': helpers.normalize_rating(5.0),
            'exam': None,
            'scores': {
                'rating_count': 1,
                'rating_avg': 5.0,
                'scores': [
                    {
                        'order': 1,
                        'rating': 5.0,
                        'ts': _datetime_ts(2017, 10, 10, 2)
                    },
                    {
                        'artificial': True,
                        'source': yt_ratings.RATING_SOURCE_OVERRIDE,
                        'rating': 5.0,
                        'count': 1,
                    },
                ]
            }
        }
    ),
])
@pytest.mark.now('2017-09-10 10:00:00')
def test_update_ratings_reducer(key, input_rows, expected_row):
    now = datetime.datetime.utcnow()
    config = {
         '_id': 'ratings_config',
         'default_settings': {
             'charger_bonus': {'count': 3, 'mark': 5},
             'exam_bonus_sep': {
                 '1': {'count': 5, 'mark': 1},
                 '2': {'count': 5, 'mark': 2},
                 '3': {'count': 5, 'mark': 4.7},
                 '4': {'count': 5, 'mark': 5},
                 '5': {'count': 5, 'mark': 5}
             },
             'expire_days': 60,
             'min_scores': 2,
             'novice_rating': 0.8,
         }
    }
    threshold = dates.timestamp_us(now - datetime.timedelta(
        days=config['default_settings']['expire_days']
    ))
    reducer = yt_ratings.UpdateRatings(config, threshold)
    yielded = list(reducer(key, input_rows))
    assert len(yielded) == 1
    result_row = yielded[0]
    result_row['scores'] = json_util.loads(result_row['scores'])
    assert result_row == expected_row
