import json

import pytest


@pytest.mark.skip(reason='fix in TAXIFLAPTEST-4512')
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
    CORP_BILLING_FAILED_SYNC_INTERVAL=0,
)
async def test_save_failed_topics(
        taxi_corp_billing, load_json, mockserver, testpoint, cursor,
):
    self_billing_orders_response = load_json(
        'self_billing_orders_response.json',
    )
    self_billing_orders_request = load_json('self_billing_orders_request.json')
    topics_compact = load_json('topics_compact.json')
    billing_orders_requests = []

    journal_requests = set()

    @mockserver.json_handler('/corp-billing-events/v1/events/journal/topics')
    def events_topics_handler(request):  # pylint: disable=W0612
        req = request.json
        if req['consumer'] in journal_requests:
            journal_topics = {'changed_topics': [], 'cursor': req['cursor']}
        else:
            journal_topics = load_json('journal_topics.json')
            cursor = req.get('cursor', '0')
            journal_topics['cursor'] = str(int(cursor) + 1)
            journal_requests.add(req['consumer'])
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
        req = {order['external_ref'] for order in request.json['orders']}
        billing_orders_requests.append(req)
        if req == {'claim-external-ref-1/2'}:
            return load_json('billing_orders_response.json')
        return mockserver.make_response(status=400)

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

    # First run:
    # Drive and Eats orders failed for the first time,
    # we inserted them in table.
    # Cargo orders were processed as usual.
    # Cursor were updated for all topic types anyway.
    await taxi_corp_billing.enable_testpoints()
    await taxi_corp_billing.invalidate_caches()

    # number of processed/failed events does not reset to 0 after previous test
    async with taxi_corp_billing.spawn_task('distlock/drive-task'):
        metrics_data = (await drive_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'drive/order': {'events': 1},
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
                'eats/order': {'events': 1},
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
                'tanker/order': {'events': 1},
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
                'claim/order': {'events': 2},
            },
        }

    async with taxi_corp_billing.spawn_task('distlock/discounts-task'):
        metrics_data = (await discounts_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'discount/order': {'events': 1},
            },
            'processed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'discount/order': {'events': 1},
            },
        }

    cursor.execute('SELECT * from corp_billing.billing_events_journal_cursor')
    cursors = {key: int(value) for key, value in cursor}
    assert cursors[2] == 1
    assert cursors[3] == 1
    assert cursors[4] == 1
    assert cursors[5] == 1
    assert cursors[7] == 1

    topic_external_ref_idx, topic_status_idx = 4, 5
    cursor.execute('SELECT * FROM corp_billing.failed_topics')
    failed_topics = {
        row[topic_external_ref_idx]: row[topic_status_idx] for row in cursor
    }
    assert len(failed_topics) == 4
    assert failed_topics['eats-external-ref-1'] == 'unprocessed'
    assert failed_topics['drive-external-ref-1'] == 'unprocessed'
    assert failed_topics['discount-external-ref-1'] == 'unprocessed'
    assert failed_topics['tanker-external-ref-1'] == 'unprocessed'

    # Second run:
    # We fetch failed topics from table, but they fail still.
    # Check that metrics numbers and topic statuses do not change.

    async with taxi_corp_billing.spawn_task('distlock/drive-task'):
        metrics_data = (await drive_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'drive/order': {'events': 1},
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
                'eats/order': {'events': 1},
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
                'tanker/order': {'events': 1},
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
                'claim/order': {'events': 2},
            },
        }

    async with taxi_corp_billing.spawn_task('distlock/discounts-task'):
        metrics_data = (await discounts_worker_finished.wait_call())['data']
        assert metrics_data == {
            'failed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'discount/order': {'events': 1},
            },
            'processed_events': {
                '$meta': {'solomon_children_labels': 'topic_name'},
                'discount/order': {'events': 1},
            },
        }

    cursor.execute('SELECT * from corp_billing.billing_events_journal_cursor')
    cursors = {key: int(value) for key, value in cursor}
    assert cursors[2] == 1
    assert cursors[3] == 1
    assert cursors[4] == 1
    assert cursors[5] == 1
    assert cursors[7] == 1

    cursor.execute('SELECT * FROM corp_billing.failed_topics')
    failed_topics = {
        row[topic_external_ref_idx]: row[topic_status_idx] for row in cursor
    }
    assert len(failed_topics) == 4
    assert failed_topics['eats-external-ref-1'] == 'unprocessed'
    assert failed_topics['drive-external-ref-1'] == 'unprocessed'
    assert failed_topics['discount-external-ref-1'] == 'unprocessed'
    assert failed_topics['tanker-external-ref-1'] == 'unprocessed'
