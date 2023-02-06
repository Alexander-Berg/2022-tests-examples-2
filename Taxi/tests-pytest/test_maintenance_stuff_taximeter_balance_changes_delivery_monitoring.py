import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import yt_wrapper
from taxi.internal import daily_mapreduce_monitoring
from taxi.internal import dbh
from taxi_maintenance.stuff import taximeter_balance_changes_delivery_monitoring  # noqa


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
        'number_of_missing_payments,'
        'ticket_event,'
        'expected_ticket_calls,'
        'expected_comment_calls,'
        'expected_send_taxi_cluster_metric_calls,'
        'expected_missing_changes_calls'
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
                            'taximeter_balance_changes.undelivered_changes.hahn'
                        ),
                        'value': 0
                    }
                },
            ],
            [
                {
                    'args': ('hahn', 'output_table_path'),
                    'kwargs': {
                        'lower_key': '2018-01-11',
                        'upper_key': '2018-01-12',
                    },
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
                            'taximeter_balance_changes.undelivered_changes.hahn'
                        ),
                        'value': 0
                    }
                },
            ],
            [
                {
                    'args': ('hahn', 'output_table_path'),
                    'kwargs': {
                        'lower_key': '2018-01-11',
                        'upper_key': '2018-01-12',
                    },
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
                        'queue': 'queue',
                        'links': [{
                            'issue': 'TAXIPROJECTS-100500',
                            'relationship': 'has epic'
                        }],
                        'message': (
                            '* hahn: 1 missing payments '
                            'in table [output_table_path]\n'
                        ),
                        'ticket': None,
                        'title': (
                            '[taximeter-balance-changes-delivery] '
                            'found 1 missing payments'
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
                            'taximeter_balance_changes.undelivered_changes.hahn'
                        ),
                        'value': 1
                    }
                },
            ],
            [
                {
                    'args': ('hahn', 'output_table_path'),
                    'kwargs': {
                        'lower_key': '2018-01-11',
                        'upper_key': '2018-01-12',
                    },
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
                        'queue': 'queue',
                        'links': [{
                            'issue': 'TAXIPROJECTS-100500',
                            'relationship': 'has epic'
                        }],
                        'message': (
                            '* hahn: 1 missing payments '
                            'in table [output_table_path]\n'
                        ),
                        'ticket': 'previous_ticket',
                        'title': (
                            '[taximeter-balance-changes-delivery] '
                            'found 1 missing payments'
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
                            'taximeter_balance_changes.undelivered_changes.hahn'
                        ),
                        'value': 1
                    }
                },
            ],
            [
                {
                    'args': ('hahn', 'output_table_path'),
                    'kwargs': {
                        'lower_key': '2018-01-11',
                        'upper_key': '2018-01-12',
                    },
                },
            ],
        ),
    ]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    MONITORINGS_SETTINGS={
        'startrack_queue': {
            'taximeter_balance_changes': 'queue'
        }
    },
    TAXIMETER_BALANCE_CHANGES_EPIC='TAXIPROJECTS-100500',
)
@pytest.inline_callbacks
def test_monitoring_job(patch, monkeypatch, number_of_missing_payments,
                        ticket_event, expected_ticket_calls,
                        expected_comment_calls,
                        expected_send_taxi_cluster_metric_calls,
                        expected_missing_changes_calls):
    monkeypatch.setattr(
        settings,
        'STARTRACK_API_TOKEN',
        'supersecret'
    )
    clients = [DummyYtClient(name='hahn')]
    if ticket_event:
        yield _make_event(
            'undelivered_taximeter_balance_changes_notification_sent',
            ticket_event
        )

    @patch('taxi.external.yt_wrapper.get_yt_mapreduce_clients')
    @async.inline_callbacks
    def get_yt_mapreduce_clients(*args, **kwargs):
        yield
        async.return_value(clients)

    @patch(
        'taxi.internal.taximeter_balance_changes.update_missing_changes.run'
    )
    @async.inline_callbacks
    def run(cluster_name, table_path, lower_key, upper_key, log_extra=None):
        yield async.return_value()

    def calculate_error_info(self, client, interval):
        return (
            daily_mapreduce_monitoring.ErrorInfo(
                cluster_name=yt_wrapper.get_cluster_name(client),
                error_count=number_of_missing_payments,
                output_table='output_table_path',
            )
        )

    monkeypatch.setattr(
        taximeter_balance_changes_delivery_monitoring.TaximeterBalanceChangesDeliveryMonitor,  # noqa
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

    yield taximeter_balance_changes_delivery_monitoring.do_stuff()

    assert create_ticket_or_comment.calls == expected_ticket_calls
    assert create_comment.calls == expected_comment_calls
    assert (send_taxi_cluster_metric.calls ==
            expected_send_taxi_cluster_metric_calls)
    assert run.calls == expected_missing_changes_calls
