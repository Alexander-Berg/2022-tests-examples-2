import json

import pytest


@pytest.mark.skip(reason='fix in TAXIFLAPTEST-1394')
@pytest.mark.config(
    CORP_BILLING_DRIVE_SYNC_ENABLED=True,
    CORP_BILLING_DRIVE_SYNC_INTERVAL_MS=1,
    CORP_BILLING_DISCOUNTS_SYNC_ENABLED=True,
    CORP_BILLING_DISCOUNTS_SYNC_INTERVAL_MS=1,
    CORP_BILLING_EATS_SYNC_ENABLED=True,
    CORP_BILLING_EATS_SYNC_INTERVAL_MS=1,
    CORP_BILLING_TANKER_SYNC_ENABLED=True,
    CORP_BILLING_TANKER_SYNC_INTERVAL_MS=1,
    CORP_BILLING_CARGO_SYNC_ENABLED=True,
    CORP_BILLING_CARGO_SYNC_INTERVAL_MS=1,
    CORP_BILLING_PROCESSES_ASYNC_COUNT={'__default__': 1},
    CORP_BILLING_SKIP_TOPICS=['eats-external-ref-2', 'eats-external-ref-3'],
    CORP_BILLING_FAILED_SYNC_INTERVAL=300,
)
async def test_happy_path(
        taxi_corp_billing, load_json, mockserver, testpoint, cursor,
):
    self_billing_orders_response = load_json(
        'self_billing_orders_response.json',
    )
    self_billing_orders_request = load_json('self_billing_orders_request.json')
    topics_compact = load_json('topics_compact.json')
    billing_orders_requests = []

    @mockserver.json_handler('/corp-billing-events/v1/events/journal/topics')
    def events_topics_handler(request):  # pylint: disable=W0612
        journal_topics = load_json('journal_topics.json')
        cursor = request.json.get('cursor', '0')
        journal_topics['cursor'] = str(int(cursor) + 1)
        return mockserver.make_response(
            json.dumps(journal_topics),
            200,
            headers={'X-Polling-Delay-Ms': '1'},
        )

    @mockserver.json_handler('/corp-billing-events/v1/topics/compact')
    def events_push_handler(request):  # pylint: disable=W0612
        return {
            'topics': [
                topics_compact[topic['topic']['external_ref']]
                for topic in request.json['topics']
            ],
        }

    @mockserver.json_handler('/corp-billing/v1/billing-orders')
    def self_request_handler(request):  # pylint: disable=W0612
        topic_type = request.json['topic']['type']
        assert request.json == self_billing_orders_request[topic_type]
        return self_billing_orders_response[topic_type]

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def billing_orders_handler(request):  # pylint: disable=W0612
        assert len(request.json['orders']) <= 1
        billing_orders_requests.append(
            {order['external_ref'] for order in request.json['orders']},
        )
        return load_json('billing_orders_response.json')

    @testpoint('billing-drive-sync-pg-dist-lock-finished')
    def drive_worker_finished(data):
        return data

    @testpoint('billing-eats-sync-pg-dist-lock-finished')
    def eats_worker_finished(data):
        return data

    @testpoint('billing-tanker-sync-pg-dist-lock-finished')
    def tanker_worker_finished(data):
        return data

    @testpoint('billing-cargo-sync-pg-dist-lock-finished')
    def cargo_worker_finished(data):
        return data

    @testpoint('billing-discounts-sync-pg-dist-lock-finished')
    def discounts_worker_finished(data):
        return data

    await taxi_corp_billing.enable_testpoints()
    await taxi_corp_billing.invalidate_caches()

    async with taxi_corp_billing.spawn_task('distlock/drive-task'):
        metrics_data = (await drive_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'drive/order': {'events': 0},
            },
            'processed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'drive/order': {'events': 1},
            },
        }

    async with taxi_corp_billing.spawn_task('distlock/eats-task'):
        metrics_data = (await eats_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'eats/order': {'events': 0},
            },
            'processed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'eats/order': {'events': 1},
            },
        }

    async with taxi_corp_billing.spawn_task('distlock/tanker-task'):
        metrics_data = (await tanker_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'tanker/order': {'events': 0},
            },
            'processed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'tanker/order': {'events': 1},
            },
        }

    async with taxi_corp_billing.spawn_task('distlock/cargo-task'):
        metrics_data = (await cargo_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'claim/order': {'events': 0},
            },
            'processed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'claim/order': {'events': 1},
            },
        }

    async with taxi_corp_billing.spawn_task('distlock/discounts-task'):
        metrics_data = (await discounts_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'discount/order': {'events': 0},
            },
            'processed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'discount/order': {'events': 1},
            },
        }

    billing_orders_requests.remove({'drive-external-ref-1/2'})
    billing_orders_requests.remove({'eats-external-ref-1/2'})
    billing_orders_requests.remove({'tanker-external-ref-1/2'})
    billing_orders_requests.remove({'claim-external-ref-1/2'})
    billing_orders_requests.remove({'discount-external-ref-1/2'})
    assert not billing_orders_requests

    cursor.execute('SELECT * from corp_billing.billing_events_journal_cursor')
    cursors = {key: int(value) for key, value in cursor}
    assert cursors[2] == 1
    assert cursors[3] == 1
    assert cursors[4] == 1
    assert cursors[5] == 1
    assert cursors[7] == 1

    cursor.execute('SELECT * FROM corp_billing.failed_topics')
    failed_topics = [key for key in cursor]
    assert not failed_topics
