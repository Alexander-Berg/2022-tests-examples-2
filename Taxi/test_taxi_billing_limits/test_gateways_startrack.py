# pylint: disable=redefined-outer-name
import pytest

from taxi.clients import startrack as client

from taxi_billing_limits import tickets
from taxi_billing_limits.startrack import gateway as startrack


@pytest.fixture
def ticket():
    return tickets.Ticket(
        queue='QUEUE',
        summary='SUMMARY',
        description='TEXT',
        link_to=[],
        notify=[],
        components=[],
    )


async def test_ticket_already_created(patch, web_context, ticket):
    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _request(url, *_args, **kwargs):
        if url == 'issues':
            raise client.ConflictError('OOPS')
        elif url == 'issues/_findByUnique':
            return {'key': 'TESTKEY-1'}
        raise NotImplementedError('Unexpected request')

    repo = startrack.Gateway(context=web_context)
    key = await repo.create_ticket(ticket=ticket, window_pk=1)
    assert key == 'TESTKEY-1'
