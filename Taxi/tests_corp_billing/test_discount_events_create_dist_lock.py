import json

import pytest


@pytest.mark.config(
    CORP_BILLING_CREATE_DISCOUNT_EVENTS_SYNC_ENABLED=True,
    CORP_BILLING_CREATE_DISCOUNT_EVENTS_SYNC_INTERVAL_MS=1,
)
async def test_happy_path(
        taxi_corp_billing, load_json, mockserver, mocks, testpoint,
):

    topics_compact = load_json('topics_compact.json')
    create_events_requests = load_json('create_events_request.json')
    discounts_responses = load_json('discounts_response.json')

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

    @mockserver.json_handler('/corp-discounts/v1/discounts/apply')
    def discounts_apply_handler(request):  # pylint: disable=W0612
        order_id = request.json.get('order_id')
        return discounts_responses.get(order_id)

    @mockserver.json_handler('/corp-billing-events/v1/events')
    def events_create_handler(request):  # pylint: disable=W0612
        events = request.json.get('events')

        # although we expect single event
        for event in events:
            external_ref = event['topic']['external_ref']
            assert event in create_events_requests[external_ref]
            create_events_requests[external_ref].remove(event)

        return {}

    @testpoint('create-discount-events-pg-dist-lock-finished')
    def discounts_worker_finished(data):
        return data

    await taxi_corp_billing.enable_testpoints()
    await taxi_corp_billing.invalidate_caches()
    await discounts_worker_finished.wait_call()
    for val in create_events_requests.values():
        assert not val
