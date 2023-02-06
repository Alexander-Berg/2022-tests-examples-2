# coding: utf-8
import copy
import json
import datetime

from django.test import RequestFactory
import pytest

from django import http

from taxi.core import async
from taxi.util import dates
from taxicabinet.views import internal as internal_views


@pytest.mark.parametrize(
    'park_id,expected_csv_path,data',
    [
        (
            'park1', 'payments.csv', [
                {
                    'bank_order_created': 1467795600,
                    'bank_order_updated': 1467968400,
                    'commission_committed': 1467969120,
                    'credit': 1069465,
                    'csv_updated': 1467969120,
                    'alias_id': '21a3db8ec8724be5826147fdb7e6166e',
                    'paid_by': 'card',
                    'park_id': 'park1',
                    'payment_type': 'commission',
                    'db_id': 'db_id',
                    'umbrella_order_id': 'umbrella-alias',
                    'payload': {
                        'db': 'some_db_id_1'
                    },
                }
            ]
        ),
        (
            'park-kzt', 'payments-kzt.csv', [
                {
                    'bank_order_created': 1467968400,
                    'bank_order_updated': 1467968400,
                    'commission_committed': 1467969120,
                    'credit': 100000,
                    'currency': 'USD',
                    'local_currency': 'KZT',
                    'local_currency_rate': '0.002936',
                    'local_credit': 34059945,
                    'csv_updated': 1467969120,
                    'alias_id': 'order-kzt-alias',
                    'paid_by': 'card',
                    'park_id': 'park-kzt',
                    'payment_type': 'commission',
                }
            ]
        ),
    ]
)
@pytest.inline_callbacks
def test_payments_csv_view(patch, load, park_id, expected_csv_path, data):
    @patch('taxicabinet.views.internal.PaymentsCSVInternalView.find_payments')
    @pytest.inline_callbacks
    def find_payments(*args, **kwargs):
        yield
        async.return_value(data)

    request = http.HttpRequest()
    request.GET['clid'] = park_id
    request.GET['encoding'] = 'utf-8'
    request.GET['date'] = '2016-07-08'

    view = internal_views.PaymentsCSVInternalView()
    response = yield view.get(request)

    expected_csv = load(expected_csv_path)

    assert response.content == expected_csv


@pytest.mark.parametrize(
    'expected_csv_path,data',
    [
        (
            'payments_scout.csv', [
                {
                    'bank_order_created': 1467795600,
                    'bank_order_updated': 1467968400,
                    'commission_committed': 1467969120,
                    'credit': 1069465,
                    'csv_updated': 1467969120,
                    'alias_id': '21a3db8ec8724be5826147fdb7e6166e',
                    'paid_by': 'card',
                    'park_id': 'park1',
                    'payment_type': 'commission',
                    'db_id': 'db_id',
                    'umbrella_order_id': 'umbrella-alias',
                    'payload': '{"db":"some_db_id_1"}',
                }
            ]
        )
    ]
)
@pytest.inline_callbacks
def test_payments_csv_scout(patch, load, expected_csv_path, data):
    @patch('taxicabinet.views.internal.PaymentsCSVScoutView.find_payments')
    @pytest.inline_callbacks
    def find_payments(*args, **kwargs):
        yield
        async.return_value(data)

    request = http.HttpRequest()
    request.GET['start'] = '2017-01-02T00:00:00'
    request.GET['end'] = '2017-01-03T00:00:00'

    view = internal_views.PaymentsCSVScoutView()
    response = yield view.get(request)

    expected_csv = load(expected_csv_path)

    assert response.content == expected_csv


class DummyYtClient(object):
    config = {
        'prefix': '//home/taxi/production/'
    }

    def __init__(self, select_data=None):
        self.oplog = []
        self.select_data = select_data or []

    def select_rows(self, query):
        self.oplog.append(
            ('select_rows', copy.deepcopy(query))
        )
        return self.select_data


class FailYtClient(DummyYtClient):
    def select_rows(self, query):
        raise RuntimeError('Oops')


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    YT_REPLICATION_CLUSTERS=['fail', 'arnold'],
)
def test_find_payments_csv_view(patch):
    yt_client = DummyYtClient()

    @patch('taxi.internal.yt_replication.rules.ReplicationRule.get_yt_clients')
    @async.inline_callbacks
    def get_yt_clients(*args, **kwargs):
        yield
        async.return_value([FailYtClient(), yt_client])

    request = http.HttpRequest()
    request.GET['clid'] = 'park1'
    request.GET['date'] = '2017-09-01'
    view = internal_views.PaymentsCSVInternalView()
    view.find_payments(request)
    assert yt_client.oplog == [
        (
            'select_rows',
            'alias_id, payment_type, trust_payment_id, trust_refund_id, '
            'csv_updated, commission_committed, park_id, db_id, currency, '
            'paid_by, credit, debet, local_currency, local_currency_rate, '
            'local_credit, local_debet, bank_order_id, bank_order_created, '
            'bank_order_updated, status, description, pcv, park_multiplier, '
            'umbrella_order_id, payload '
            'FROM [//home/taxi/production/replica/external/pbl/indexes/clid] '
            'as index '
            'JOIN [//home/taxi/production/'
            'replica/external/pbl/park_balance_logs] '
            'ON (index.alias_id, index.payment_type, index.trust_payment_id, '
            'index.trust_refund_id) = '
            '(alias_id, payment_type, trust_payment_id, trust_refund_id) '
            'WHERE index.park_id="park1" '
            'AND index.csv_updated >= 1504213200 '
            'AND index.csv_updated < 1504299600 '
            'AND index.csv_updated = csv_updated'
        ),
    ]


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    YT_REPLICATION_CLUSTERS=['fail', 'arnold'],
)
def test_find_payments_csv_bulk_view(patch):
    yt_client = DummyYtClient()

    @patch('taxi.internal.yt_replication.rules.ReplicationRule.get_yt_clients')
    @async.inline_callbacks
    def get_yt_clients(*args, **kwargs):
        yield
        async.return_value([FailYtClient(), yt_client])

    request = http.HttpRequest()
    request.GET['db_id'] = '3a1bffe456d54dfd9eee962ade4e7df2'
    request.GET['start'] = '2017-09-01'
    request.GET['end'] = '2017-09-02'
    view = internal_views.PaymentsCSVBulkView()
    view.find_payments(request)
    assert yt_client.oplog == [
        (
            'select_rows',
            'alias_id, payment_type, trust_payment_id, trust_refund_id, '
            'csv_updated, commission_committed, park_id, db_id, currency, '
            'paid_by, credit, debet, local_currency, local_currency_rate, '
            'local_credit, local_debet, bank_order_id, bank_order_created, '
            'bank_order_updated, status, description, pcv, park_multiplier, '
            'umbrella_order_id, payload '
            'FROM [//home/taxi/production/replica/external/pbl/indexes/db] '
            'as index '
            'JOIN [//home/taxi/production/replica/external/pbl/park_balance_logs] '
            'ON (index.alias_id, index.payment_type, index.trust_payment_id, '
            'index.trust_refund_id) = '
            '(alias_id, payment_type, trust_payment_id, trust_refund_id) '
            'WHERE index.db_id="3a1bffe456d54dfd9eee962ade4e7df2" '
            'AND index.csv_updated >= 1504224000 '
            'AND index.csv_updated < 1504310400 '
            'AND index.csv_updated = csv_updated'
        ),
    ]


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    YT_REPLICATION_CLUSTERS=['fail', 'arnold'],
)
def test_find_payments_csv_by_order_view(patch):
    yt_client = DummyYtClient()

    @patch('taxi.internal.yt_replication.rules.ReplicationRule.get_yt_clients')
    @async.inline_callbacks
    def get_yt_clients(*args, **kwargs):
        yield
        async.return_value([FailYtClient(), yt_client])

    request = http.HttpRequest()
    request.GET['order'] = 'ebb00fa19fff4dfd8546f624ceaac99f'
    view = internal_views.PaymentsCSVByOrderView()
    view.find_payments(request)
    assert yt_client.oplog == [
        (
            'select_rows',
            '* FROM [//home/taxi/production/replica/external/pbl/park_balance_logs] '
            'WHERE alias_id="ebb00fa19fff4dfd8546f624ceaac99f"'
        ),
    ]


@pytest.mark.parametrize(
    'query,expected_status',
    [
        ({}, 406),
        (
            {'range': {}},
            406,
        ),
        (
            {
                'range': {
                    'limit': 'booyaka'
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': None
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {}
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {'newer_than': {}}
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': 'booyaka'
                        }
                    }
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-01T00:00:01.000000+00:00',
                            'payment_batch_id': 12345
                        }
                    }
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-01T00:00:01.000000+00:00',
                            'payment_batch_id': '12345'
                        }
                    }
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-01T00:00:01.000000+00:00',
                            'version': 1
                        }
                    }
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-01T00:00:01.000000+00:00',
                            'payment_batch_id': '12345',
                            'version': 'blah'
                        }
                    }
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than_but_not_too_much': {
                            'created': '2018-01-01T00:00:01.000000+00:00',
                            'payment_batch_id': '12345',
                            'version': 1
                        }
                    }
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-01T00:00:01.000000+00:00',
                            'payment_batch_id': '12345',
                            'version': 1
                        }
                    }
                }
            },
            200,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-01T00:00:01.000000+00:00'
                        }
                    }
                }
            },
            200,
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    YT_REPLICATION_CLUSTERS=['seneca-sas'],
)
@pytest.inline_callbacks
def test_driver_partner_payment_view_validation(patch, query, expected_status):
    yt_client = DummyYtClient()

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(environment):
        _clients = {'seneca-sas': yt_client}
        return _clients[environment]

    request = RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    view = internal_views.DriverPartnerPaymentView()
    response = yield view.post(request)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'query,data,expected_metadata',
    [
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-01T00:00:01.000000+00:00',
                        }
                    }
                }
            },
            [],
            {}
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-01T00:00:00.000000+00:00',
                        }
                    }
                }
            },
            [
                {
                    'created': 1514764801,
                    'payment_batch_id': '1234',
                    'version': 1,
                    'currency': 'RUB',
                    'delta': '1234.56',
                    'park_id': 'clid',
                    'payment_batch_description': 'description'
                }
            ],
            {
                'cursor': {
                    'item_id': {
                        'created': '2018-01-01T00:00:01.000000+00:00',
                        'payment_batch_id': '1234',
                        'version': 1,
                    }
                }
            }
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    YT_REPLICATION_CLUSTERS=['seneca-sas'],
)
@pytest.inline_callbacks
def test_driver_partner_payment_view_cursor(
        patch, query, data, expected_metadata):
    yt_client = DummyYtClient(select_data=data)

    @patch('taxi.external.yt_wrapper.get_client')
    @async.inline_callbacks
    def get_client(environment):
        yield None
        _clients = {'seneca-sas': yt_client}
        async.return_value(_clients[environment])

    request = RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    view = internal_views.DriverPartnerPaymentView()
    response = yield view.post(request)
    response_data = json.loads(response.content)
    assert response.status_code == 200
    assert response_data['metadata'] == expected_metadata


@pytest.mark.parametrize(
    'clusters,should_fail',
    [
        (['good'], False),
        (['fail_1', 'good'], False),
        (['fail_1'], True),
        (['fail_1', 'fail_2'], True),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_driver_partner_payment_view_failover(
        patch, clusters, should_fail):
    query = {
        'range': {
            'limit': 100,
            'item_id': {
                'newer_than': {
                    'created': '2018-01-01T00:00:00.000000+00:00',
                }
            }
        }
    }

    @patch('taxi.config.YT_REPLICATION_CLUSTERS.get')
    @async.inline_callbacks
    def get():
        yield
        async.return_value(clusters)

    @patch('taxi.external.yt_wrapper.get_client')
    @async.inline_callbacks
    def get_client(environment):
        yield None
        _clients = {
            'fail_1': FailYtClient(),
            'fail_2': FailYtClient(),
            'good': DummyYtClient()
        }
        async.return_value(_clients[environment])

    request = RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    view = internal_views.DriverPartnerPaymentView()
    if should_fail:
        with pytest.raises(internal_views.DriverPartnerPaymentViewReadError):
            yield view.post(request)
    else:
        response = yield view.post(request)
        assert response.status_code == 200


@pytest.mark.parametrize(
    'query,expected_code',
    [
        ({}, 406),
        (
            {
                'range': {
                    'item_id': 'abcd',
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {},
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': 'abcd',
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': 'foobar',
                        'item_id': 'abcd'
                    }
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': 'foobar',
                            'payment_id': 'abcd'
                        },
                    },
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 0,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-28T12:08:48.372567+00:00',
                            'payment_id': 'abcd',
                        },
                    },
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': -1,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-28T12:08:48.372567+00:00',
                            'payment_id': 'abcd',
                        },
                    },
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 99999999,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-28T12:08:48.372567+00:00',
                            'payment_id': 'abcd',
                        },
                    },
                }
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 'baz',
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-28T12:08:48.372567+00:00',
                            'payment_id': 'abcd',
                        },
                    },
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-28T12:08:48.372567+00:00',
                            'payment_id': 'abcd',
                        },
                    },
                },
            },
            406,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-28T12:08:48.372567+00:00',
                            'payment_id': 'abcd',
                        },
                    },
                },
            },
            200,
        ),
        (
            {
                'range': {
                    'limit': 100,
                    'item_id': {
                        'newer_than': {
                            'created': '2018-01-28T12:08:48.372567+00:00',
                        },
                    },
                },
            },
            200,
        ),
    ]
)
@pytest.inline_callbacks
def test_parse_query(query, expected_code):
    request = RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    view = internal_views.TaximeterBalanceChangesView()
    response = yield view.post(request)
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'query',
    [
        {
            'range': {
                'limit': 100,
                'item_id': {
                    'newer_than': {
                        'created': '2018-01-28T12:08:48.372567+00:00',
                        'payment_id': 'abcd'
                    }
                }
            }
        },
        {
            'range': {
                'limit': 100,
                'item_id': {
                    'newer_than': {
                        'created': '2018-01-28T12:08:48.372567+00:00',
                    }
                }
            }
        },
    ]
)
@pytest.inline_callbacks
def test_empty_response_cursor(query):
    request = RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    view = internal_views.TaximeterBalanceChangesView()
    response = yield view.post(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data['balance_changes']) == 0
    assert 'cursor' not in response_data['metadata']


@async.inline_callbacks
def _check_balance_changes_response_with_relative_time(
        expected_payment_ids, query_created_offset, limit,
        query_payment_id=None, expected_cursor_created_offset=None,
        expected_cursor_payment_id=None, reconcile=False):
    """
    Helper function to check if balance-changes returned correct payment IDs
    """
    query = _make_query(
        query_created_offset, limit, query_payment_id, reconcile)
    request = RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    view = internal_views.TaximeterBalanceChangesView()
    response = yield view.post(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data['balance_changes']) == len(expected_payment_ids)
    for payment_id, balance_change in zip(
            expected_payment_ids, response_data['balance_changes']):
        assert payment_id == balance_change['payment_id']
    if expected_cursor_payment_id is not None:
        cursor = response_data['metadata']['cursor']['item_id']
        assert cursor['payment_id'] == expected_cursor_payment_id
    if expected_cursor_created_offset is not None:
        cursor = response_data['metadata']['cursor']['item_id']
        expected_cursor_created = (
            datetime.datetime.utcnow() +
            datetime.timedelta(seconds=expected_cursor_created_offset)
        )
        cursor_created = dates.parse_timestring(cursor['created'])
        assert cursor_created == expected_cursor_created


def _make_query(created_offset, limit, payment_id=None, reconcile=False):
    item_id = {
        'created': dates.timestring(
            datetime.datetime.utcnow() +
            datetime.timedelta(seconds=created_offset)
        )
    }
    if payment_id:
        item_id['payment_id'] = payment_id
    query_range = {
        'limit': limit,
        'item_id': {'newer_than': item_id},
    }
    if reconcile:
        query_range['reconcile'] = reconcile
    return {'range': query_range}


@pytest.mark.now(datetime.datetime.utcnow().isoformat())
@pytest.mark.filldb(
    taximeter_balance_changes='test_taximeter_balance_changes_payment_types',
)
@pytest.inline_callbacks
def test_taximeter_balance_changes_payment_types():
    payment_id_to_expected_payment_type = dict([
        ('resize_negative_ride_ride', 'resize_ride'),
        ('resize_negative_tips_tips', 'resize_tips'),
        ('resize_positive_ride_ride', 'resize_ride'),
        ('resize_positive_tips_tips', 'resize_tips'),
        ('compensation_positive_ride_ride', 'compensation'),
        ('compensation_positive_tips_tips', 'compensation'),
        ('refund_negative_ride_ride', 'refund'),
        ('refund_negative_tips_tips', 'refund_tips'),
        ('compensation_refund_negative_ride_ride', 'refund_compensation'),
        ('compensation_refund_negative_tips_tips', 'refund_compensation'),
        ('card_positive_ride_ride', 'card'),
        ('card_negative_ride_ride', 'refund'),
        ('card_positive_tips_tips', 'tips'),
        ('card_negative_tips_tips', 'refund_tips'),
        ('applepay_positive_ride_ride', 'card'),
        ('applepay_negative_ride_ride', 'refund'),
        ('applepay_positive_tips_tips', 'tips'),
        ('applepay_negative_tips_tips', 'refund_tips'),
        ('googlepay_positive_ride_ride', 'card'),
        ('googlepay_negative_ride_ride', 'refund'),
        ('googlepay_positive_tips_tips', 'tips'),
        ('googlepay_negative_tips_tips', 'refund_tips'),
        ('corp_positive_ride_ride', 'corporate'),
        ('corp_negative_ride_ride', 'refund'),
        ('corp_positive_tips_tips', 'tips'),
        ('corp_negative_tips_tips', 'refund_tips'),
    ])
    encountered_payment_ids = set()
    expected_count = len(payment_id_to_expected_payment_type)
    request = RequestFactory().post(
        path='',
        data=json.dumps(_make_query(created_offset=-1, limit=10000)),
        content_type='application/json'
    )
    view = internal_views.TaximeterBalanceChangesView()
    response = yield view.post(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data['balance_changes']) == expected_count
    for balance_change in response_data['balance_changes']:
        payment_id = balance_change['payment_id']
        assert payment_id in payment_id_to_expected_payment_type
        expected_payment_type = payment_id_to_expected_payment_type[payment_id]
        assert balance_change['payment_type'] == expected_payment_type
        encountered_payment_ids.add(payment_id)
    assert len(encountered_payment_ids) == expected_count


@pytest.mark.now(datetime.datetime.utcnow().isoformat())
@pytest.mark.filldb(
    taximeter_balance_changes=(
        'test_taximeter_balance_change_can_generate_multiple_payments',
    )
)
@pytest.inline_callbacks
def test_taximeter_balance_change_can_generate_multiple_payments():
    yield _check_balance_changes_response_with_relative_time(
        expected_payment_ids=['resize_ride', 'resize_tips'],
        query_created_offset=-1,
        query_payment_id=None,
        limit=10000,
    )


@pytest.mark.now(datetime.datetime.utcnow().isoformat())
@pytest.mark.parametrize(
    (
        'created_offset,'
        'payment_id,'
        'limit,'
        'expected_payment_ids,'
        'expected_cursor_created_offset,'
        'expected_cursor_payment_id'
    ),
    [
        (-2001, None, 1, ['resize_2_ride'], -2000, 'resize_2'),
        (-2001, None, 2, ['resize_2_ride', 'resize_3_ride'], -2000, 'resize_3'),
        (-2000, 'resize_2', 1, ['resize_3_ride'], -2000, 'resize_3'),
        (
            -2000,
            'resize_2',
            2,
            ['resize_3_ride', 'resize_1_ride'],
            -1940,
            'resize_1'
        ),
        (
            -1881,
            None,
            3,
            ['resize_4_ride', 'resize_5_ride', 'resize_6_ride'],
            -1700,
            'resize_6',
        ),
        (
            -1881,
            None,
            4,
            ['resize_4_ride', 'resize_5_ride', 'resize_6_ride'],
            -1700,
            'resize_6',
        ),
        (-1100, None, 1, ['resize_20_ride'], -800, 'resize_20'),
        (-1100, 'resize_10', 1, ['resize_20_ride'], -800, 'resize_20'),
    ]
)
@pytest.mark.filldb(
    taximeter_balance_changes='test_query_correctness',
)
@pytest.inline_callbacks
def test_query_correctness(created_offset, payment_id, limit,
                           expected_payment_ids, expected_cursor_created_offset,
                           expected_cursor_payment_id):
    yield _check_balance_changes_response_with_relative_time(
        expected_payment_ids,
        created_offset,
        query_payment_id=payment_id,
        limit=limit,
        expected_cursor_created_offset=expected_cursor_created_offset,
        expected_cursor_payment_id=expected_cursor_payment_id,
    )


@pytest.mark.now(datetime.datetime.utcnow().isoformat())
@pytest.mark.parametrize(
    (
        'created_offset,'
        'payment_id,'
        'limit,'
        'expected_payment_ids,'
        'expected_cursor_created_offset,'
        'expected_cursor_payment_id'
    ),
    [
        (-200, None, 2, ['resize_30_ride'], -100, 'resize_30'),
        (-100, 'resize_30', 2, [], None, None),
    ]
)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_MIN_PAYMENT_AGE_TO_HIDE=70000
)
@pytest.mark.filldb(
    taximeter_balance_changes='test_query_correctness',
)
@pytest.inline_callbacks
def test_min_payment_age(created_offset, payment_id, limit,
                         expected_payment_ids, expected_cursor_created_offset,
                         expected_cursor_payment_id):
    yield _check_balance_changes_response_with_relative_time(
        expected_payment_ids,
        created_offset,
        query_payment_id=payment_id,
        limit=limit,
        expected_cursor_created_offset=expected_cursor_created_offset,
        expected_cursor_payment_id=expected_cursor_payment_id,
    )


@pytest.mark.parametrize(
    'query,expected_umbrella_ids',
    [
        (
            {
                'range': {
                    'limit': 3,
                    'item_id': {
                        'newer_than': {
                            'created': '2017-12-31T12:59:59.0+00:00',
                        },
                    },
                },
            },
            [
                None,
                'umbrella_id',
                None
            ],
        ),
    ]
)
@pytest.mark.filldb(
    taximeter_balance_changes='test_umbrella_order_ids',
)
@pytest.inline_callbacks
def test_umbrella_order_ids(query, expected_umbrella_ids):
    request = RequestFactory().post(
        path='',
        data=json.dumps(query),
        content_type='application/json'
    )
    view = internal_views.TaximeterBalanceChangesView()
    response = yield view.post(request)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data['balance_changes']) == len(expected_umbrella_ids)
    for umbrella_id, balance_change in zip(
            expected_umbrella_ids, response_data['balance_changes']):
        assert umbrella_id == balance_change['umbrella_order_id']


@pytest.mark.now(datetime.datetime.utcnow().isoformat())
@pytest.mark.parametrize(
    'created_offset,payment_id,limit,expected_payment_ids',
    [
        (10000, None, 1, []),
        (-4000, None, 1, ['resize_1_ride']),
        (-2000, 'resize_1', 1, ['resize_2_ride']),
    ]
)
@pytest.mark.filldb(
    missing_taximeter_balance_changes='test_missing_changes',
)
@pytest.inline_callbacks
def test_missing_changes(
        created_offset, payment_id, limit, expected_payment_ids):
    yield _check_balance_changes_response_with_relative_time(
        expected_payment_ids,
        created_offset,
        query_payment_id=payment_id,
        limit=limit,
        reconcile=True,
    )
