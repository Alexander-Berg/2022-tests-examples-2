# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from corp_billing_events_plugins import *  # noqa: F403 F401 I100 I202


@pytest.fixture
def push_events(taxi_corp_billing_events):
    async def _wrapper(events):
        body = {'events': events}
        response = await taxi_corp_billing_events.post('/v1/events', json=body)
        return response

    return _wrapper


@pytest.fixture
def read_journal_full(taxi_corp_billing_events):
    async def _wrapper(namespace, cursor=None, consumer=None):
        url = '/v1/events/journal/full'
        body = _build_journal_request_body(namespace, cursor, consumer)
        response = await taxi_corp_billing_events.post(url, json=body)
        return response

    return _wrapper


@pytest.fixture
def read_journal_topics(taxi_corp_billing_events):
    async def _wrapper(namespace, cursor=None):
        url = '/v1/events/journal/topics'
        body = _build_journal_request_body(namespace, cursor)
        response = await taxi_corp_billing_events.post(url, json=body)
        return response

    return _wrapper


@pytest.fixture
def get_topics(taxi_corp_billing_events):
    async def _wrapper(topics, compact=False):
        if compact:
            url = '/v1/topics/compact'
        else:
            url = '/v1/topics/full'
        body = {'topics': topics}
        response = await taxi_corp_billing_events.post(url, json=body)
        return response

    return _wrapper


def _build_journal_request_body(namespace, cursor=None, consumer=None):
    body = {'namespace': namespace}
    if cursor is not None:
        body['cursor'] = cursor

    if consumer is not None:
        body['consumer'] = consumer

    return body
