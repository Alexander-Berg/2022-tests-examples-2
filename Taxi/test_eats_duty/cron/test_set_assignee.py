import typing

import pytest

# pylint: disable=redefined-outer-name
from eats_duty.generated.cron import run_cron


@pytest.mark.config(
    EATS_DUTY_SET_ASSIGNEE_CRON={
        'enabled': True,
        'tickets_per_page': 1,
        'queues': [
            {'queue': 'EDANOTDUTY', 'filter': {'resolution': 'empty()'}},
        ],
    },
    EATS_DUTY_RESPONSIBLE={
        'test-component-1': {
            'user': 'user1',
            'status': {
                'needQa': {'user': 'user_qa'},
                'needDeveloper': {'user': 'user_developer'},
            },
        },
    },
)
async def test_set_assignee(patch):

    max_page: int = 0
    expected_pages: typing.List[int] = [3, 2, 1]
    expected_tickets: typing.Dict[str, str] = {
        'EDANOTDUTY-1': 'user_qa',
        'EDANOTDUTY-2': 'user_developer',
    }

    @patch('taxi.clients.startrack.StartrackAPIClient.search')
    async def _search(
            json_filter: typing.Optional[dict] = None,
            queue: typing.Optional[str] = None,
            page: typing.Optional[int] = None,
            page_size: typing.Optional[int] = None,
            fields: typing.Optional[typing.List[str]] = None,
    ):
        assert json_filter == {'queue': 'EDANOTDUTY', 'resolution': 'empty()'}
        assert page_size == 1, 'Unexpected page size'
        assert page is not None

        nonlocal max_page
        if page > max_page:
            max_page = page

        nonlocal expected_pages
        assert expected_pages.pop() == page

        if page == 1:
            return [{'key': 'EDANOTDUTY-1'}]

        if page == 2:
            return [{'key': 'EDANOTDUTY-2'}]

        if page == 3:
            return []

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        ticket_status = {
            'EDANOTDUTY-1': 'needQa',
            'EDANOTDUTY-2': 'needDeveloper',
        }
        assert ticket in ticket_status

        return {
            'key': ticket,
            'components': [{'display': 'test-component-1'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': ticket_status[ticket]},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        nonlocal expected_tickets
        assert kwargs['assignee'] == expected_tickets.pop(ticket, None)

        return {'key': ticket}

    await run_cron.main(['eats_duty.crontasks.set_assignee', '-t', '0'])
    assert expected_pages == []
    assert expected_tickets == {}
    assert max_page == 3
