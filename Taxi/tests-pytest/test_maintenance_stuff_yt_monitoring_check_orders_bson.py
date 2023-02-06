import datetime

import freezegun
import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.internal import dbh
from taxi.internal import event_monitor
from taxi_maintenance.stuff import yt_monitoring_check_orders_bson


NOW = datetime.datetime(2018, 1, 12, 5, 0)


class DummyYtClient(object):
    def __init__(self):
        self.active = False
        self.config = {'prefix': '//home/', 'proxy': {'url': 'hahn'}}

    def exists(self, table):
        self.active = True
        return True

    def row_count(self, table):
        self.active = True
        return 1

    def read_table(self, table):
        self.active = True
        yield {'id': 12}

    def remove(self, table, **kwargs):
        self.active = True

    def TablePath(self, path, *args, **kwargs):
        return path


BAD_COUNT = 100500
GOOD_COUNT = 19


def make_check_result(count, good_count=GOOD_COUNT):
    result = {
        key: (
            count
            if key in yt_monitoring_check_orders_bson.DOUBT_KEYS
            else good_count
        ) for key in yt_monitoring_check_orders_bson.AGG_KEYS
    }
    details = {key: [] for key in yt_monitoring_check_orders_bson.AGG_KEYS}
    result['details'] = details

    result[yt_monitoring_check_orders_bson.STAT_TMP_TABLES_KEY] = 1
    result['details'][yt_monitoring_check_orders_bson.STAT_TMP_TABLES_KEY] = [
        '//home/path/to/table',
    ]
    return result


bad_check_result = make_check_result(count=BAD_COUNT)
good_check_result = make_check_result(count=0)


@pytest.mark.parametrize('key,rows,expected_result', [
    (
        {'id': 'test_order'},
        [
            {
                'updated': 1000,
                'created': 1000,
                'type': 'order_bson'
            }
        ],
        [
            {'@table_index': 2, 'id': 'test_order',
             'reasons': ['struct_missing']},
            {
                'id': 'test_order',
                'total': 1,
                'struct_missing': 1,
                '@table_index': 0,
            }
        ]
    ),
    (
        {'id': 'test_order_bson_missing'},
        [
            {
                'updated_order': 1499999000,
                'updated_proc': 1499999000,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1499999000,
                'created_proc': 1499999000,
            }
        ],
        [
            {'@table_index': 2, 'id': 'test_order_bson_missing',
             'reasons': ['order_bson_missing', 'proc_bson_missing']},
            {
                'id': 'test_order_bson_missing',
                'total': 1,
                'order_bson_missing': 1,
                'proc_bson_missing': 1,
                '@table_index': 0,
            },
        ]
    ),
    (
        {'id': 'test_order'},
        [
            {
                'updated': 1000,
                'created': 1000,
                'type': 'order_bson'
            },
            {
                'updated': 2000,
                'created': 2000,
                'type': 'proc_bson'
            },
            {
                'updated_order': 1000,
                'updated_proc': 2000,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1513700000,
                'created_proc': 1513700000,
            },
        ],
        [
            {
                'id': 'test_order',
                '@table_index': 0,
                'total': 1,
            }
        ]
    ),
    (
        {'id': 'test_inconsistent_doc'},
        [
            {
                'updated': 1510000000,
                'created': 1510000000,
                'type': 'order_bson'
            },
            {
                'updated': 1510000000,
                'created': 1510000000,
                'type': 'proc_bson'
            },
            {
                'updated_order': 1510000000,
                'updated_proc': None,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1510000000,
                'created_proc': 1510000000,
            },
        ],
        [
            {'@table_index': 2, 'id': 'test_inconsistent_doc',
             'reasons': ['inconsistent_doc']},
            {
                'id': 'test_inconsistent_doc',
                'inconsistent_doc': 1,
                '@table_index': 0,
                'total': 1,
            }
        ]
    ),
    (
        {'id': 'test_old_inconsistent_doc'},
        [
            {
                'updated': 1000,
                'created': 1000,
                'type': 'order_bson'
            },
            {
                'updated': 2000,
                'created': 2000,
                'type': 'proc_bson'
            },
            {
                'updated_order': 1000,
                'updated_proc': None,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1000,
                'created_proc': 1000,
            },
        ],
        [
            {
                'id': 'test_old_inconsistent_doc',
                'old_inconsistent_doc': 1,
                '@table_index': 0,
                'total': 1,
            }
        ]
    ),
    (
        {'id': 'test_order'},
        [
            {
                'created': 1000,
                'updated': 1000,
                'type': 'order_bson'
            },
            {
                'created': 2000,
                'updated': 2000,
                'type': 'proc_bson'
            },
            {
                'updated_order': 1001,
                'updated_proc': 2000,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1513700000,
                'created_proc': 1513700000,
            },
        ],
        [
            {'@table_index': 2, 'id': 'test_order',
             'reasons': ['order_timestamp_mismatch']},
            {
                'id': 'test_order',
                'total': 1,
                '@table_index': 0,
                'order_timestamp_mismatch': 1,
            }
        ]
    ),
    (
        {'id': 'test_order_proc_struct_missing'},
        [
            {
                'created': 1000,
                'updated': 1000,
                'type': 'order_bson'
            },
            {
                'created': 2000,
                'updated': 2000,
                'type': 'proc_bson'
            },
            {
                'updated_order': 1000,
                'updated_proc': None,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1513700000,
                'created_proc': None,
            },
        ],
        [
            {'@table_index': 2, 'id': 'test_order_proc_struct_missing',
             'reasons': ['proc_struct_missing_order_exists']},
            {
                'id': 'test_order_proc_struct_missing',
                'total': 1,
                '@table_index': 0,
                'proc_struct_missing_order_exists': 1,
            }
        ]
    ),
    (
        {'id': 'test_order_struct_missing'},
        [
            {
                'created': 1000,
                'updated': 1000,
                'type': 'order_bson'
            },
            {
                'created': 2000,
                'updated': 2000,
                'type': 'proc_bson'
            },
            {
                'updated_order': None,
                'updated_proc': 2000,
                'type': 'struct',
                'status': 'finished',
                'created_order': None,
                'created_proc': 2000,
            },
        ],
        [
            {'@table_index': 2, 'id': 'test_order_struct_missing',
             'reasons': ['order_struct_missing_proc_exists']},
            {
                'id': 'test_order_struct_missing',
                'total': 1,
                '@table_index': 0,
                'order_struct_missing_proc_exists': 1,
            }
        ]
    ),
    (
        {'id': 'test_order'},
        [
            {
                'created': 1000,
                'updated': 1000,
                'type': 'order_bson'
            },
            {
                'created': 2000,
                'updated': 2000,
                'type': 'proc_bson'
            },
            {
                'updated_order': 1000,
                'updated_proc': 2001,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1513700000,
                'created_proc': 1513700000,
            },
        ],
        [
            {'@table_index': 2, 'id': 'test_order',
             'reasons': ['proc_timestamp_old_mismatch']},
            {
                'id': 'test_order',
                'total': 1,
                '@table_index': 0,
                'proc_timestamp_old_mismatch': 1,
            }
        ]
    ),
    (
        {'id': 'test_fresh_update'},
        [
            {
                'updated_order': 1513700000,
                'updated_proc': 1513700000,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1513700000,
                'created_proc': 1513700000,
            }
        ],
        [
            {
                'id': 'test_fresh_update',
                'total': 1,
                '@table_index': 0,
                'order_fresh_update': 1,
                'proc_fresh_update': 1,
            }
        ]
    ),
    (
        {'id': 'test_fresh_update2'},
        [
            {
                'type': 'struct',
                'status': 'finished',
                'updated_order': 1513701000,
                'updated_proc': 1513701000,
                'created_order': 1513700000,
                'created_proc': 1513700000,
            },
            {
                'created': 1000001,
                'updated': 1000001,
                'type': 'order_bson'
            },
            {
                'created': 2000002,
                'updated': 2000002,
                'type': 'proc_bson'
            }
        ],
        [
            {
                'id': 'test_fresh_update2',
                'total': 1,
                '@table_index': 0,
                'order_fresh_update': 1,
                'proc_fresh_update': 1,
            }
        ]
    ),
    (
        {'id': 'test_order_no_proc'},
        [
            {
                'updated_order': 1499999000,
                'updated_proc': None,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1499999000,
                'created_proc': None,
            },
            {
                'type': 'order_bson',
                'updated': 1499999000,
                'created': 1499999000,
            }
        ],
        [
            {
                'id': 'test_order_no_proc',
                'total': 1,
                'proc_missing_order_exists': 1,
                '@table_index': 1,
            },
            {'@table_index': 2, 'id': 'test_order_no_proc',
             'reasons': ['proc_missing_order_exists']},
            {
                'id': 'test_order_no_proc',
                'total': 1,
                'proc_missing_order_exists': 1,
                '@table_index': 0,
            }
        ]
    ),
    (
        {'id': 'test_order_missing_but_proc'},
        [
            {
                'type': 'struct',
                'status': 'finished',
                'updated_order': None,
                'created_order': None,
                'updated_proc': 1490000001,
                'created_proc': 1490000001,
            },
            {
                'created': 1490000001,
                'updated': 1490000001,
                'type': 'proc_bson'
            }
        ],
        [
            {
                'id': 'test_order_missing_but_proc',
                'total': 1,
                '@table_index': 1,
                'order_missing_proc_exists': 1,
            },
            {'@table_index': 2, 'id': 'test_order_missing_but_proc',
             'reasons': ['order_missing_proc_exists']},
            {
                'id': 'test_order_missing_but_proc',
                '@table_index': 0,
                'total': 1,
                'order_missing_proc_exists': 1,
            }
        ]
    ),
    (
        {'id': 'test_proc_missing_but_order'},
        [
            {
                'updated_order': 1490000001,
                'updated_proc': None,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1490000000,
                'created_proc': None,
            },
            {
                'created': 1490000001,
                'updated': 1490000001,
                'type': 'order_bson',
            }
        ],
        [
            {
                'id': 'test_proc_missing_but_order',
                '@table_index': 1,
                'total': 1,
                'proc_missing_order_exists': 1,
            },
            {
                '@table_index': 2,
                'id': 'test_proc_missing_but_order',
                'reasons': ['proc_missing_order_exists'],
            },
            {
                'id': 'test_proc_missing_but_order',
                '@table_index': 0,
                'total': 1,
                'proc_missing_order_exists': 1,
            },
        ]
    ),
    (
        {'id': 'test_proc_missing_but_order_old'},
        [
            {
                'updated_order': 1400000001,
                'updated_proc': None,
                'type': 'struct',
                'status': 'finished',
                'created_order': 1400000000,
                'created_proc': None,
            },
            {
                'created': 1400000001,
                'updated': 1400000001,
                'type': 'order_bson',
            }
        ],
        [
            {
                'id': 'test_proc_missing_but_order_old',
                '@table_index': 0,
                'total': 1,
            }
        ]
    )
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_doc_reducer(key, rows, expected_result):
    reducer = yt_monitoring_check_orders_bson.DocReducer(
        fresh_timestamp=1500000000,
    )
    result = list(reducer(key, rows))
    assert result == expected_result


DESCRIPTION_TEMPLATE = (
    '<{total: %(good_count)s\n}>\n'
    '<{struct_missing: %(bad_count)s\n}>\n'
    '<{draft_spotted: %(good_count)s\n}>\n'
    '<{draft_invalid: %(bad_count)s\n}>\n'
    '<{inconsistent_doc: %(bad_count)s\n}>\n'
    '<{old_inconsistent_doc: %(good_count)s\n}>\n'
    '<{proc_bson_ancient_missing: %(good_count)s\n}>\n'
    '<{proc_timestamp_old_mismatch: %(bad_count)s\n}>\n'
    '<{order_bson_missing: %(bad_count)s\n}>\n'
    '<{proc_bson_missing: %(bad_count)s\n}>\n'
    '<{order_fresh_update: %(good_count)s\n}>\n'
    '<{proc_fresh_update: %(good_count)s\n}>\n'
    '<{order_timestamp_mismatch: %(bad_count)s\n}>\n'
    '<{proc_timestamp_mismatch: %(bad_count)s\n}>\n'
    '<{order_missing_proc_exists: %(bad_count)s\n}>\n'
    '<{proc_missing_order_exists: %(bad_count)s\n}>\n'
    '<{order_struct_missing_proc_exists: %(bad_count)s\n}>\n'
    '<{proc_struct_missing_order_exists: %(bad_count)s\n}>\n'
    '<{stat_tmp_tables_url: %(stat_tmp_tables_url)s\n}>'
)
FAILED_DESCRIPTION = DESCRIPTION_TEMPLATE % {
    'bad_count': BAD_COUNT,
    'good_count': GOOD_COUNT,
    'stat_tmp_tables_url': GOOD_COUNT,
}


@pytest.mark.parametrize(
    (
        'ticket_event,'
        'check_events,'
        'check_result,'
        'expected_create_comment_calls,'
        'expected_create_ticket_or_comment_calls,'
        'expected_ticket_event_count,'
        'is_special_fast_run'
    ),
    [
        (
            None,
            [],
            good_check_result,
            [],
            [],
            0,
            False,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket',
            },
            [],
            good_check_result,
            [],
            [],
            1,
            False,
        ),
        (
            None,
            [],
            bad_check_result,
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'queue',
                        'components': [100500],
                        'followers': ['test_user', 'test_user_2'],
                        'ticket': None,
                        'title': (
                            '[yt-replication-orders-bson-check] bson vs struct'
                            ' check failed: orders-hahn'
                        ),
                        'message': (
                            '!!(red)**bson vs struct** check failed for '
                            'orders-hahn!!\n{}\n'.format(FAILED_DESCRIPTION)
                        )
                    }
                }
            ],
            1,
            False,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket'
            },
            [],
            bad_check_result,
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'queue',
                        'components': [100500],
                        'followers': ['test_user', 'test_user_2'],
                        'ticket': 'previous_ticket',
                        'title': (
                            '[yt-replication-orders-bson-check] bson vs struct'
                            ' check failed: orders-hahn'
                        ),
                        'message': (
                            '!!(red)**bson vs struct** check failed for '
                            'orders-hahn!!\n{}\n'.format(FAILED_DESCRIPTION)
                        )
                    }
                }
            ],
            2,
            False,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket',
            },
            [{
                'check_name': 'orders-hahn',
                'status': True,
                'full_run': True,
            }],
            {},
            [],
            [],
            1,
            False,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket',
            },
            [
                {
                    'check_name': 'orders-hahn',
                    'status': False,
                    'full_run': True,
                },
                {
                    'check_name': 'orders-hahn',
                    'status': True,
                    'full_run': False,
                },
            ],
            {},
            [],
            [],
            1,
            False,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket',
            },
            [
                {
                    'check_name': 'orders-hahn',
                    'status': False,
                    'full_run': True,
                    'stats': bad_check_result,
                    # to ensure that we receive status ok
                    # after failed last full run
                    'created': NOW - datetime.timedelta(days=5),
                },
                {
                    'check_name': 'orders-hahn',
                    'status': True,
                    'full_run': False,
                },
            ],
            good_check_result,
            [{
                'args': (
                    'previous_ticket',
                    '!!(green)**bson vs struct** now OK for orders-hahn!!',
                ),
                'kwargs': {}
            }],
            [],
            2,
            False,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket',
            },
            [{
                'check_name': 'orders-hahn',
                'status': False,
                'full_run': True,
                'stats': bad_check_result,
            }],
            good_check_result,
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'queue',
                        'components': [100500],
                        'followers': ['test_user', 'test_user_2'],
                        'ticket': 'previous_ticket',
                        'title': (
                            '[yt-replication-orders-bson-check] bson vs struct'
                            ' check failed: orders-hahn'
                        ),
                        'message': (
                            '!!(blue)last **bson vs struct** check updated for'
                            ' orders-hahn!!\n<{total: %(good_count)s\n}>\n'
                            '<{draft_spotted: %(good_count)s\n}>\n'
                            '<{old_inconsistent_doc: %(good_count)s\n}>\n'
                            '<{proc_bson_ancient_missing: %(good_count)s\n}>\n'
                            '<{order_fresh_update: %(good_count)s\n}>\n'
                            '<{proc_fresh_update: %(good_count)s\n}>\n'
                            '<{stat_tmp_tables_url: 1\n'
                            '* https://yt.hahn.path=//home/path/to/table'
                            '\n}>\n\n'
                            '!!(green)**bson vs struct** '
                            'now OK for orders-hahn!!'
                        ) % {'good_count': GOOD_COUNT}
                    }
                }
            ],
            2,
            True,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket',
            },
            [{
                'check_name': 'orders-hahn',
                'status': False,
                'full_run': True,
                'stats': bad_check_result,
            }],
            make_check_result(100499, 13000),
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'queue',
                        'components': [100500],
                        'followers': ['test_user', 'test_user_2'],
                        'ticket': 'previous_ticket',
                        'title': (
                            '[yt-replication-orders-bson-check] bson vs struct'
                            ' check failed: orders-hahn'
                        ),
                        'message': (
                            '!!(blue)last **bson vs struct** check updated for'
                            ' orders-hahn!!\n{}\n'.format(
                                DESCRIPTION_TEMPLATE % {
                                    'bad_count': 100499,
                                    # good count will not overrides
                                    # by fast checks
                                    'good_count': GOOD_COUNT,
                                    'stat_tmp_tables_url': (
                                        '1\n* '
                                        'https://yt.hahn.path=//home/path/to/table'
                                    ),
                                },
                            )
                        )
                    }
                }
            ],
            2,
            True,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket',
            },
            [{
                'check_name': 'orders-hahn',
                'status': False,
                'full_run': True,
                'stats': bad_check_result,
            }],
            bad_check_result,  # the same result, no notifying
            [],
            [],
            1,
            True,
        ),
        (
            {
                'check_type': 'yt-replication-orders-bson-check',
                'ticket': 'previous_ticket',
            },
            [{
                'check_name': 'orders-hahn',
                'status': False,
                'full_run': True,
                'stats': bad_check_result,
            }],
            make_check_result(100499),
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'queue',
                        'components': [100500],
                        'followers': ['test_user', 'test_user_2'],
                        'ticket': 'previous_ticket',
                        'title': (
                            '[yt-replication-orders-bson-check] bson vs struct'
                            ' check failed: orders-hahn'
                        ),
                        'message': (
                            '!!(blue)last **bson vs struct** check updated for'
                            ' orders-hahn!!\n{}\n'.format(
                                DESCRIPTION_TEMPLATE % {
                                    'bad_count': 100499,
                                    'good_count': GOOD_COUNT,
                                    'stat_tmp_tables_url': (
                                        '1\n* '
                                        'https://yt.hahn.path=//home/path/to/table'
                                    ),
                                },
                            )
                        )
                    }
                }
            ],
            2,
            True,
        ),
    ]
)
@pytest.mark.config(MONITORINGS_SETTINGS={
    'startrack_queue': {
        'yt_replication': 'queue',
    },
    'startrack_kwargs': {
        'yt_replication': {
            'component': 100500,
            'department_id': 111111,
        },
    }
})
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_notifications(patch, monkeypatch, ticket_event, check_events,
                       replication_yt_target_info,
                       check_result,
                       expected_create_comment_calls,
                       expected_create_ticket_or_comment_calls,
                       expected_ticket_event_count, is_special_fast_run):
    if ticket_event is not None:
        yield event_monitor.yt_data_issue_event(
            **ticket_event
        )
    for num, check_event in enumerate(check_events):
        now_for_upload = (
            NOW - datetime.timedelta(minutes=60) +
            datetime.timedelta(minutes=num)
        )
        assert num < 50
        if 'created' in check_event:
            now_for_upload = check_event['created']
        with freezegun.freeze_time(now_for_upload, ignore=['']):
            yield event_monitor.yt_bson_check_event(
                **check_event
            )

    @patch('taxi.external.startrack.create_ticket_or_comment')
    @async.inline_callbacks
    def create_ticket_or_comment(queue, title, message, ticket=None, **kwargs):
        ticket = ticket or 'ticket'
        yield async.return_value(ticket)

    @patch('taxi.external.startrack.create_comment')
    @async.inline_callbacks
    def create_comment(ticket, body):
        yield

    @patch('taxi.external.staff.search_staff_by_department_id')
    @async.inline_callbacks
    def search_staff_by_department_id(department_id, fields=None,
                                      log_extra=None):
        assert department_id == 111111
        yield async.return_value(
            [{'login': 'test_user'}, {'login': 'test_user_2'}]
        )

    @patch(
        'taxi_maintenance.stuff.yt_monitoring_check_orders_bson.'
        '_do_map_reduce_on_cluster'
    )
    @async.inline_callbacks
    def _do_map_reduce_on_cluster(*args, **kwargs):
        yield async.return_value(check_result)

    @patch(
        'taxi_maintenance.stuff.yt_monitoring_check_orders_bson.'
        '_wait_for_flush'
    )
    def _wait_for_flush(*args, **kwargs):
        assert not is_special_fast_run

    @patch(
        'taxi_maintenance.stuff.yt_monitoring_check_orders_bson.'
        '_get_fresh_timestamp'
    )
    @async.inline_callbacks
    def _get_fresh_timestamp(*args, **kwargs):
        yield

    @patch(
        'taxi_maintenance.stuff.yt_monitoring_check_orders_bson.'
        '_lookup_and_write_rows'
    )
    def _lookup_and_write_rows(*args, **kwargs):
        pass

    yt_client = DummyYtClient()
    yt_clients = {'hahn': yt_client}

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(name, **kwargs):
        return yt_clients[name]

    monkeypatch.setattr(settings, 'YT_PATH_URL_TEMPLATE',
                        'https://yt.{}.path={}')

    @patch('taxi.internal.replication.get_actual_yt_client_names')
    @async.inline_callbacks
    def get_actual_yt_client_names(rule_name, **kwargs):
        assert rule_name == 'orders'
        yield async.return_value(['hahn'])

    monkeypatch.setattr(
        settings,
        'STARTRACK_API_TOKEN',
        'supersecret'
    )

    yield yt_monitoring_check_orders_bson.do_stuff()

    assert (create_ticket_or_comment.calls ==
            expected_create_ticket_or_comment_calls)
    assert create_comment.calls == expected_create_comment_calls
    ticket_events = yield dbh.event_monitor.Doc.find_many(
        {
            dbh.event_monitor.Doc.name: event_monitor.yt_data_issue_event.name
        },
        secondary=False
    )
    assert len(ticket_events) == expected_ticket_event_count

    if is_special_fast_run:
        assert not _wait_for_flush.calls
        assert len(_lookup_and_write_rows.calls) == 1
        assert yt_client.active
    else:
        assert not _lookup_and_write_rows.calls
        assert not yt_client.active


@pytest.mark.parametrize('last_result,new_partial_result,expected', [
    (
        bad_check_result,
        good_check_result,
        good_check_result,
    ),
    (
        bad_check_result,
        bad_check_result,
        bad_check_result,
    ),
    (
        make_check_result(30),
        make_check_result(20),
        make_check_result(20),
    ),
])
@pytest.mark.filldb(_fill=False)
def test_get_updated_last_result(last_result, new_partial_result, expected):
    assert yt_monitoring_check_orders_bson._get_updated_last_result(
        last_result, new_partial_result
    ) == expected


@pytest.mark.parametrize('tables,expected', [
    (
        ['a'],
        {
            yt_monitoring_check_orders_bson.STAT_TMP_TABLES_KEY: 1,
            yt_monitoring_check_orders_bson.STAT_TMP_TABLES_URL_KEY: 1,
            'details': {
                yt_monitoring_check_orders_bson.STAT_TMP_TABLES_KEY:
                    ['a'],
                yt_monitoring_check_orders_bson.STAT_TMP_TABLES_URL_KEY:
                    ['https://yt.path=a'],
            },
        }
    ),
    (
        ['a', 'b'],
        {
            yt_monitoring_check_orders_bson.STAT_TMP_TABLES_KEY: 2,
            yt_monitoring_check_orders_bson.STAT_TMP_TABLES_URL_KEY: 2,
            'details': {
                yt_monitoring_check_orders_bson.STAT_TMP_TABLES_KEY:
                    ['a', 'b'],
                yt_monitoring_check_orders_bson.STAT_TMP_TABLES_URL_KEY:
                    ['https://yt.path=a', 'https://yt.path=b'],
            },
        }
    ),
])
@pytest.mark.filldb(_fill=False)
def test_update_result_with_tables(patch, tables, expected):
    @patch('taxi.external.yt_wrapper.get_path_url')
    def get_path_url(yt_client, path):
        return 'https://yt.path=%s' % path

    stats = {'details': {}}
    yt_monitoring_check_orders_bson._update_result_with_tables(
        stats, None, tables
    )
    assert stats == expected

    yt_monitoring_check_orders_bson._update_result_with_tables(
        stats, None, tables
    )
    assert stats == expected, 'second failed'


@pytest.mark.parametrize('stats,expected_stats', [
    (
        {'x': 2, 'y': 1, 'details': {'x': [2, '2', 1], 'y': ['a', 'b']}},
        {'x': 2, 'y': 1, 'details': {'x': ['1', '2', '2'], 'y': ['a', 'b']}},
    ),
    (
        {'x': 2, 'details': {'x': ['foo', 'bar']}},
        {'x': 2, 'details': {'x': ['bar', 'foo']}},
    ),
    (
        {'details': {}},
        {'details': {}},
    ),
])
@pytest.mark.filldb(_fill=False)
def test_normalize_stat(stats, expected_stats):
    normalized = yt_monitoring_check_orders_bson._normalize_stat(
        stats
    )
    assert normalized == expected_stats
    assert normalized == (
        yt_monitoring_check_orders_bson._normalize_stat(normalized)
    )
    assert normalized == (
        yt_monitoring_check_orders_bson._normalize_stat(expected_stats)
    )


_OVERRIDES = {
    'struct_missing': 20,
    'draft_invalid': 30,
}


@pytest.mark.config(YT_MONITORING_CHECK_ORDERS_BSON={
    'thresholds_overrides': _OVERRIDES
})
@pytest.inline_callbacks
def test_get_check_thresholds():
    base_thresholds = yt_monitoring_check_orders_bson.CHECK_THRESHOLDS
    thresholds = yield yt_monitoring_check_orders_bson._get_check_thresholds()
    assert len(base_thresholds) == len(thresholds)
    for (base_key, base_value), (key, value) in zip(
            base_thresholds, thresholds
    ):
        assert base_key == key
        if base_key in _OVERRIDES:
            expected_value = _OVERRIDES[base_key]
        else:
            expected_value = base_value
        assert value == expected_value
