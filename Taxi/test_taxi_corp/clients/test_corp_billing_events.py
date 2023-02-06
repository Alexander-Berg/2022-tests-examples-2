# pylint: disable=redefined-outer-name, protected-access
import pytest

from taxi import config
from taxi.clients import http_client
from taxi.clients import tvm

from taxi_corp.clients import corp_billing_events


@pytest.fixture
async def client(loop, db, simple_secdist):
    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield corp_billing_events.CorpBillingEventsClient(
            config=config_,
            session=session,
            tvm_client=tvm.TVMClient(
                service_name='corp-billing-events',
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


async def test_journal_topics(client, mockserver, response_mock):
    response_example = {
        'changed_topics': [
            {
                'namespace': 'corp',
                'topic': {
                    'external_ref': '14c4dc3890c44732a24f7546d45e6ae3',
                    'type': 'order',
                },
            },
        ],
    }

    @mockserver.json_handler('/corp-billing-events/v1/events/journal/topics')
    async def _journal_topics(request):
        return response_example

    response = await client.journal_topics('corp', 'cursor_1')
    assert response == response_example
    assert _journal_topics.times_called == 1
