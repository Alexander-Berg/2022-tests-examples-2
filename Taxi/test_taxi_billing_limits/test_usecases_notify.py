# pylint: disable=redefined-outer-name
import typing

import pytest

from taxi_billing_limits import tickets
from taxi_billing_limits.usecases import notify


@pytest.fixture
def ticket():
    return tickets.Ticket(
        queue='queue',
        summary='Заголок тикета',
        description='Text',
        link_to=[],
        notify=['me'],
        components=['test_component'],
    )


async def test_create_new_ticket(ticket):
    repo = TicketWindowRepositoryStub()
    tracker = TicketTrackerStub()
    usecase = notify.SendNotificationUseCase(repo=repo, tracker=tracker)
    await usecase(blank=ticket, window_pk=1)
    assert tracker.called == [{'blank': ticket, 'window_pk': 1}]
    assert repo.called == {
        'get': {'window_pk': 1},
        'attach': {'window_pk': 1, 'key': 'TICKET-NEW'},
    }


async def test_create_comment_if_ticket_exists(ticket):
    repo = TicketWindowRepositoryStub('TICKET-1')
    tracker = TicketTrackerStub()
    usecase = notify.SendNotificationUseCase(repo=repo, tracker=tracker)
    await usecase(blank=ticket, window_pk=1)
    assert tracker.called == [
        {
            'key': 'TICKET-1',
            'text': '\n\n'.join([ticket.summary, ticket.description]),
            'summonees': ticket.notify,
        },
    ]
    assert repo.called == {'get': {'window_pk': 1}, 'attach': None}


class TicketTrackerStub(notify.TicketTracker):
    def __init__(self):
        self.called = []

    async def create_ticket(
            self, *, ticket: tickets.Ticket, window_pk: int,
    ) -> str:
        self.called.append({'blank': ticket, 'window_pk': window_pk})
        return 'TICKET-NEW'

    async def create_comment(self, *, key: str, text: str, summonees: list):
        self.called.append({'key': key, 'text': text, 'summonees': summonees})


class TicketWindowRepositoryStub(notify.TicketWindowRepository):
    def __init__(self, ticket_key=None):
        self.key = ticket_key
        self.called = {'get': None, 'attach': None}

    async def get_attached_ticket(
            self, *, window_pk: int,
    ) -> typing.Optional[str]:
        self.called['get'] = {'window_pk': window_pk}
        return self.key

    async def attach_ticket(self, *, window_pk: int, key: str):
        self.called['attach'] = {'window_pk': window_pk, 'key': key}
