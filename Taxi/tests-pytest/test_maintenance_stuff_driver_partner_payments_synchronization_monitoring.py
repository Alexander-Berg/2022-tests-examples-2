import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import yt_wrapper
from taxi.internal import daily_mapreduce_monitoring
from taxi.internal import dbh
from taxi_maintenance.stuff import driver_partner_payments_synchronization_monitoring  # noqa


NOW = datetime.datetime(2018, 1, 12, 5, 0)
YESTERDAY_MIDNIGHT_TIMESTAMP = 1515618000


@async.inline_callbacks
def _make_event(name, record):
    record.update({
        'name': name,
        'created': NOW,
    })
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
        'expected_send_taxi_cluster_metric_calls,'
        'expected_ticket_calls,'
        'expected_comment_calls'
    ),
    [
        (
            0,
            None,
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': YESTERDAY_MIDNIGHT_TIMESTAMP,
                        'metric': (
                            'driver_partner_payments.'
                            'payments_missing_from_taximeter.hahn'
                        ),
                        'value': 0
                    }
                },
            ],
            [],
            [],
        ),
        (
            0,
            {'ticket': 'previous_ticket'},
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': YESTERDAY_MIDNIGHT_TIMESTAMP,
                        'metric': (
                            'driver_partner_payments.'
                            'payments_missing_from_taximeter.hahn'
                        ),
                        'value': 0
                    }
                },
            ],
            [],
            []
        ),
        (
            1,
            None,
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': YESTERDAY_MIDNIGHT_TIMESTAMP,
                        'metric': (
                            'driver_partner_payments.'
                            'payments_missing_from_taximeter.hahn'
                        ),
                        'value': 1
                    }
                },
            ],
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'TAXI_BACKEND',
                        'links': [{
                            'issue': 'TAXIPROJECTS-1337',
                            'relationship': 'has epic'
                        }],
                        'message': (
                            'hahn: 1 missing payments '
                            'in table [output_table_path]'
                        ),
                        'ticket': None,
                        'title': (
                            '[driver-partner-payments-synchronization] '
                            'found 1 missing payments'
                        )
                    }
                }
            ],
            [],
        ),
        (
            1,
            {'ticket': 'previous_ticket'},
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': YESTERDAY_MIDNIGHT_TIMESTAMP,
                        'metric': (
                            'driver_partner_payments.'
                            'payments_missing_from_taximeter.hahn'
                        ),
                        'value': 1
                    }
                },
            ],
            [
                {
                    'args': (),
                    'kwargs': {
                        'queue': 'TAXI_BACKEND',
                        'links': [{
                            'issue': 'TAXIPROJECTS-1337',
                            'relationship': 'has epic'
                        }],
                        'message': (
                            'hahn: 1 missing payments '
                            'in table [output_table_path]'
                        ),
                        'ticket': 'previous_ticket',
                        'title': (
                            '[driver-partner-payments-synchronization] '
                            'found 1 missing payments'
                        )
                    }
                }
            ],
            [],
        ),
    ]
)
@pytest.mark.config(
    MONITORINGS_SETTINGS={
        'startrack_queue': {
            'driver_partner_payments': 'TAXI_BACKEND'
        }
    },
    DRIVER_PARTNER_PAYMENTS_MONITORING_EPIC='TAXIPROJECTS-1337',
)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_monitoring_job(patch, monkeypatch, number_of_missing_payments,
                        ticket_event,
                        expected_send_taxi_cluster_metric_calls,
                        expected_ticket_calls, expected_comment_calls):
    monkeypatch.setattr(
        settings,
        'STARTRACK_API_TOKEN',
        'supersecret'
    )
    clients = [DummyYtClient(name='hahn')]
    if ticket_event:
        yield _make_event(
            'driver_partner_payments_synchronization_notification_sent',
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
                error_count=number_of_missing_payments,
                output_table='output_table_path',
            )
        )

    monkeypatch.setattr(
        driver_partner_payments_synchronization_monitoring.DriverPartnerPaymentsDeliveryMonitor,  # noqa
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

    yield driver_partner_payments_synchronization_monitoring.do_stuff()

    assert (send_taxi_cluster_metric.calls ==
            expected_send_taxi_cluster_metric_calls)
    assert create_ticket_or_comment.calls == expected_ticket_calls
    assert create_comment.calls == expected_comment_calls
