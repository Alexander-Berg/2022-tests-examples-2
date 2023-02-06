import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import yt_wrapper
from taxi.internal import daily_mapreduce_monitoring
from taxi.internal import dbh
from taxi_maintenance.stuff import check_taximeter_balance_changes_correctness  # noqa


NOW = datetime.datetime(2018, 1, 12, 5, 0)
YESTERDAY_MIDNIGHT_TIMESTAMP = 1515618000


@async.inline_callbacks
def _make_event(event_type, record):
    record['name'] = event_type
    if 'created' not in record:
        record['created'] = NOW
    yield dbh.event_monitor.Doc.register_event(record)


class DummyYtClient(object):
    def __init__(self, name):
        self.config = {
            'prefix': '//home/taxi/production/',
            'proxy': {
                'url': '{0}.yt.yandex.net'.format(name)
            }
        }


@pytest.mark.parametrize(
    (
        'number_of_errors,'
        'ticket_event,'
        'expected_ticket_calls,'
        'expected_comment_calls,'
        'expected_send_taxi_cluster_metric_calls'
    ),
    [
        (
            0,
            None,
            [],
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': YESTERDAY_MIDNIGHT_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.'
                            'num_incorrect_changes.hahn'
                        ),
                        'value': 0
                    }
                },
            ],
        ),
        (
            0,
            {'ticket': 'previous_ticket'},
            [],
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': YESTERDAY_MIDNIGHT_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.'
                            'num_incorrect_changes.hahn'
                        ),
                        'value': 0
                    }
                },
            ],
        ),
        (
            1,
            None,
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'TAXIBACKEND',
                        'links': [{
                            'issue': 'TAXIPROJECTS-100500',
                            'relationship': 'has epic'
                        }],
                        'message': (
                            'hahn: 1 errors in table [output_table_path]'
                        ),
                        'ticket': None,
                        'title': (
                            '[check-taximeter-balance-changes-correctness] '
                            'found 1 errors'
                        )
                    }
                }
            ],
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': YESTERDAY_MIDNIGHT_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.'
                            'num_incorrect_changes.hahn'
                        ),
                        'value': 1
                    }
                },
            ],
        ),
        (
            1,
            {'ticket': 'previous_ticket'},
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'TAXIBACKEND',
                        'links': [{
                            'issue': 'TAXIPROJECTS-100500',
                            'relationship': 'has epic'
                        }],
                        'message': (
                            'hahn: 1 errors in table [output_table_path]'
                        ),
                        'ticket': 'previous_ticket',
                        'title': (
                            '[check-taximeter-balance-changes-correctness] '
                            'found 1 errors'
                        )
                    }
                }
            ],
            [],
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': YESTERDAY_MIDNIGHT_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.'
                            'num_incorrect_changes.hahn'
                        ),
                        'value': 1
                    }
                },
            ],
        ),
    ]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    MONITORINGS_SETTINGS={
        'startrack_queue': {
            'taximeter_balance_changes': 'TAXIBACKEND'
        }
    },
    TAXIMETER_BALANCE_CHANGES_EPIC='TAXIPROJECTS-100500',
)
@pytest.inline_callbacks
def test_monitoring_job(patch, monkeypatch, number_of_errors, ticket_event,
                        expected_ticket_calls, expected_comment_calls,
                        expected_send_taxi_cluster_metric_calls):
    monkeypatch.setattr(
        settings,
        'STARTRACK_API_TOKEN',
        'supersecret'
    )
    clients = [DummyYtClient(name='hahn')]
    if ticket_event:
        yield _make_event(
            'taximeter_balance_changes_inaccuracy_notification_sent',
            ticket_event
        )

    @patch('taxi.external.yt_wrapper.get_yt_mapreduce_clients')
    @async.inline_callbacks
    def get_yt_mapreduce_clients(*args, **kwargs):
        yield
        async.return_value(clients)

    def calculate_error_info(self, client, interval):
        return (
            daily_mapreduce_monitoring.ErrorInfo(
                cluster_name=yt_wrapper.get_cluster_name(client),
                error_count=number_of_errors,
                output_table='output_table_path',
            )
        )

    monkeypatch.setattr(
        check_taximeter_balance_changes_correctness.TaximeterBalanceChangesInaccuracyMonitor,  # noqa
        'calculate_error_info',
        calculate_error_info
    )

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    @async.inline_callbacks
    def send_taxi_cluster_metric(*args, **kwargs):
        yield async.return_value()

    @patch('taxi.external.startrack.create_ticket_or_comment')
    @async.inline_callbacks
    def create_ticket_or_comment(queue, title, message, ticket=None, **kwargs):
        ticket = ticket or 'ticket'
        yield async.return_value(ticket)

    @patch('taxi.external.startrack.create_comment')
    @async.inline_callbacks
    def create_comment(ticket, body):
        yield async.return_value()

    yield check_taximeter_balance_changes_correctness.do_stuff()

    assert create_ticket_or_comment.calls == expected_ticket_calls
    assert create_comment.calls == expected_comment_calls
    assert (send_taxi_cluster_metric.calls ==
            expected_send_taxi_cluster_metric_calls)
