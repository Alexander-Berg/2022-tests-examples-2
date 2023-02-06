import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.internal import dbh
from taxi_maintenance.stuff import billing_scripts_monitoring


NOW = datetime.datetime(2018, 1, 12, 5, 0)
TWO_HOURS = datetime.timedelta(hours=2)


@async.inline_callbacks
def make_event(event_type, record, now):
    record['name'] = event_type.name
    if 'created' not in record:
        record['created'] = now
    yield dbh.event_monitor.Doc.register_event(record)


@pytest.inline_callbacks
def check_event_count(event_type, expected_event_count):
    events = yield dbh.event_monitor.Doc.find_many(
        {dbh.event_monitor.Doc.name: event_type.name},
        secondary=False
    )
    assert len(events) == expected_event_count


@pytest.mark.parametrize(
    (
        'last_state_event,'
        'ticket_event,'
        'errors,'
        'previous_ticket_is_open,'
        'expected_state_event_count,'
        'expected_ticket_event_count,'
        'expected_create_ticket_calls,'
        'expected_create_comment_calls,'
    ),
    [
        (
            {'status': True, 'errors': []},
            None,
            [],
            False,
            # no state events created
            1,
            # no ticket events created
            0,
            [],
            [],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # old previous ticket
            {'ticket': 'previous_ticket', 'created': NOW - TWO_HOURS},
            # no current errors
            [],
            # previous ticket is not open
            False,
            # no state events created
            1,
            # no ticket events created
            1,
            [],
            [],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # new previous ticket
            {'ticket': 'previous_ticket', 'created': NOW},
            # no current errors
            [],
            # previous ticket is not open
            False,
            # no state events created
            1,
            # no ticket events created
            1,
            [],
            [],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # old previous ticket
            {'ticket': 'previous_ticket', 'created': NOW - TWO_HOURS},
            # no current errors
            [],
            # previous ticket is open
            True,
            # no state events created
            1,
            # no ticket events created
            1,
            [],
            [],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # new previous ticket
            {'ticket': 'previous_ticket', 'created': NOW},
            # no current errors
            [],
            # previous ticket is open
            True,
            # no state events created
            1,
            # no ticket events created
            1,
            [],
            [],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # no previous ticket
            None,
            # has current errors
            ['error'],
            # previous ticket is not open
            False,
            # 1 state event created
            2,
            # 1 ticket event created
            1,
            # should create a new ticket
            [
                {
                    'args': (
                        {
                            'components': [100500],
                            'description': 'Problems:\n* error',
                            'queue': 'queue',
                            'summary': '[billing-check-failure] error'
                        },
                    ),
                    'kwargs': {'profile': None}
                }
            ],
            [],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # old previous ticket
            {'ticket': 'previous_ticket', 'created': NOW - TWO_HOURS},
            # has current errors
            ['error'],
            # previous ticket is not open
            False,
            # 1 state event created
            2,
            # 1 ticket event created
            2,
            # should create a new ticket
            [
                {
                    'args': (
                        {
                            'components': [100500],
                            'description': 'Problems:\n* error',
                            'queue': 'queue',
                            'summary': '[billing-check-failure] error'
                        },
                    ),
                    'kwargs': {'profile': None}
                }
            ],
            [],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # new previous ticket
            {'ticket': 'previous_ticket', 'created': NOW},
            # has current errors
            ['error'],
            # previous ticket is not open
            False,
            # 1 state event created
            2,
            # 1 ticket event created
            2,
            # should create a new ticket
            [
                {
                    'args': (
                        {
                            'components': [100500],
                            'description': 'Problems:\n* error',
                            'queue': 'queue',
                            'summary': '[billing-check-failure] error'
                        },
                    ),
                    'kwargs': {'profile': None}
                }
            ],
            [],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # old previous ticket
            {'ticket': 'previous_ticket', 'created': NOW - TWO_HOURS},
            # has current errors
            ['error'],
            # previous ticket is open
            True,
            # 1 state event created
            2,
            # 1 ticket event created
            2,
            [],
            # should write a comment
            [
                {
                    'args': ('previous_ticket', 'Problems:\n* error'),
                    'kwargs': {'profile': None}
                }
            ],
        ),
        (
            # no previous errors
            {'status': True, 'errors': []},
            # new previous ticket
            {'ticket': 'previous_ticket', 'created': NOW},
            # has current errors
            ['error'],
            # previous ticket is open
            True,
            # 1 state event created
            2,
            # 1 ticket event created
            2,
            [],
            # should write a comment
            [
                {
                    'args': ('previous_ticket', 'Problems:\n* error'),
                    'kwargs': {'profile': None}
                }
            ],
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # no previous ticket
            None,
            # no current errors
            [],
            # previous ticket is not open
            False,
            # 1 state event created
            2,
            # no ticket events created
            0,
            [],
            [],
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # old previous ticket
            {'ticket': 'previous_ticket', 'created': NOW - TWO_HOURS},
            # no current errors
            [],
            # previous ticket is not open
            False,
            # 1 state event created
            2,
            # 1 ticket event created
            2,
            [],
            # should write a comment
            [
                {
                    'args': (u'previous_ticket', 'Now OK'),
                    'kwargs': {}
                }
            ]
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # new previous ticket
            {'ticket': 'previous_ticket', 'created': NOW},
            # no current errors
            [],
            # previous ticket is not open
            False,
            # 1 state event created
            2,
            # 1 ticket event created
            2,
            [],
            # should write a comment
            [
                {
                    'args': (u'previous_ticket', 'Now OK'),
                    'kwargs': {}
                }
            ]
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # old previous ticket
            {'ticket': 'previous_ticket', 'created': NOW - TWO_HOURS},
            # no current errors
            [],
            # previous ticket is open
            True,
            # 1 state event created
            2,
            # 1 ticket event created
            2,
            [],
            # should write a comment
            [
                {
                    'args': (u'previous_ticket', 'Now OK'),
                    'kwargs': {}
                }
            ]
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # new previous ticket
            {'ticket': 'previous_ticket', 'created': NOW},
            # no current errors
            [],
            # previous ticket is open
            True,
            # 1 state event created
            2,
            # 1 ticket event created
            2,
            [],
            # should write a comment
            [
                {
                    'args': (u'previous_ticket', 'Now OK'),
                    'kwargs': {}
                }
            ]
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # no previous ticket
            None,
            # has current errors
            ['error'],
            # previous ticket is not open
            False,
            # no state events created
            1,
            # 1 ticket event created
            1,
            # should create a new ticket
            [
                {
                    'args': (
                        {
                            'components': [100500],
                            'description': 'Problems:\n* error',
                            'queue': 'queue',
                            'summary': '[billing-check-failure] error'
                        },
                    ),
                    'kwargs': {'profile': None}
                }
            ],
            []
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # old previous ticket
            {'ticket': 'previous_ticket', 'created': NOW - TWO_HOURS},
            # has current errors
            ['error'],
            # previous ticket is not open
            False,
            # no state events created
            1,
            # 1 ticket event created
            2,
            # should create a new ticket
            [
                {
                    'args': (
                        {
                            'components': [100500],
                            'description': 'Problems:\n* error',
                            'queue': 'queue',
                            'summary': '[billing-check-failure] error'
                        },
                    ),
                    'kwargs': {'profile': None}
                }
            ],
            []
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # new previous ticket
            {'ticket': 'previous_ticket', 'created': NOW},
            # has current errors
            ['error'],
            # previous ticket is not open
            False,
            # no state events created
            1,
            # no ticket events created
            1,
            [],
            []
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # old previous ticket
            {'ticket': 'previous_ticket', 'created': NOW - TWO_HOURS},
            # has current errors
            ['error'],
            # previous ticket is open
            True,
            # no state events created
            1,
            # 1 ticket event created
            2,
            [],
            # should write a comment
            [
                {
                    'args': ('previous_ticket', 'Problems:\n* error'),
                    'kwargs': {'profile': None}
                }
            ]
        ),
        (
            # has previous errors
            {'status': True, 'errors': ['error']},
            # new previous ticket
            {'ticket': 'previous_ticket', 'created': NOW},
            # has current errors
            ['error'],
            # previous ticket is open
            True,
            # no state events created
            1,
            # no ticket events created
            1,
            [],
            []
        ),
    ]
)
@pytest.mark.config(
    BILLING_MONITOR_ST_REPORT_PERIOD=(60 * 60),  # 1 hour
    BILLING_MONITOR_ST_QUEUE='queue',
    BILLING_MONITOR_ST_COMPONENT=100500
)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_notifications(patch, monkeypatch, last_state_event, ticket_event,
                       errors, previous_ticket_is_open,
                       expected_state_event_count, expected_ticket_event_count,
                       expected_create_ticket_calls,
                       expected_create_comment_calls):
    if last_state_event is not None:
        yield make_event(
            billing_scripts_monitoring.check_state_changed_event,
            last_state_event,
            now=NOW
        )
    if ticket_event is not None:
        yield make_event(
            billing_scripts_monitoring.error_report_sent_event,
            ticket_event,
            now=NOW
        )

    @patch('taxi.external.startrack.create_ticket')
    @async.inline_callbacks
    def create_ticket(data, profile=None):
        yield async.return_value({
            'key': 'new_ticket'
        })

    @patch('taxi.external.startrack.get_ticket_info')
    @async.inline_callbacks
    def get_ticket_info(ticket, profile=None):
        info = {
            'status': {
                'key': 'closed'
            }
        }
        if previous_ticket_is_open:
            info['status']['key'] = 'open'
        yield async.return_value(info)

    @patch('taxi.external.startrack.create_comment')
    @async.inline_callbacks
    def create_comment(ticket, body, profile=None):
        yield async.return_value()

    monkeypatch.setattr(settings, 'STARTRACK_API_TOKEN', 'supersecret')

    yield billing_scripts_monitoring.handle_new_state(errors)
    assert create_ticket.calls == expected_create_ticket_calls
    assert create_comment.calls == expected_create_comment_calls
    yield check_event_count(
        billing_scripts_monitoring.check_state_changed_event,
        expected_state_event_count
    )
    yield check_event_count(
        billing_scripts_monitoring.error_report_sent_event,
        expected_ticket_event_count
    )
