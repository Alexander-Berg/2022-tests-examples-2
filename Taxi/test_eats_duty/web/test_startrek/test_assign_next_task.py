import typing

import pytest

OptionalList = typing.Optional[typing.List[str]]


def parse_queue(issue: str) -> str:
    parts = issue.split('-', 2)
    if not parts[0]:
        raise Exception(f'Failed to parse queue from issue key {issue}')
    return parts[0]


@pytest.fixture(name='trigger_assing_next')
def assing_next_request(web_app_client):
    async def request(
            issue: str, json_filter: dict, order: OptionalList = None,
    ):
        payload = {'name': 'assign_next', 'filter': json_filter, 'debug': True}

        if order is not None:
            payload['order'] = order

        return await web_app_client.post(
            '/v1/startrek/issue-status-change',
            json={'issue_key': issue, 'task': payload},
        )

    return request


@pytest.mark.parametrize(
    'json_filter,issue_order',
    [
        pytest.param({}, None, id='empty'),
        pytest.param({'status': 'open'}, None, id='simple, no order'),
        pytest.param(
            {'status': 'closed'}, ['+priority'], id='simple, with order',
        ),
    ],
)
async def test_assign_next_issue(
        patch, trigger_assing_next, json_filter, issue_order,
):

    issue_key: str = 'EDANOTDUTY-100500'
    expected_assignee: str = 'test-user'

    expected_filter = json_filter.copy()
    expected_filter.update(
        {'queue': parse_queue(issue_key), 'assignee': 'empty()'},
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == issue_key
        return {
            'key': issue_key,
            'queue': {'key': parse_queue(issue_key)},
            'assignee': {'id': expected_assignee},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.search')
    async def _search(json_filter, order, **kwargs):
        assert json_filter == expected_filter
        assert order == issue_order

        return [{'key': issue_key}, {'key': 'EDANOTDUTY-100501'}]

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, assignee, **kwargs):
        assert ticket == 'EDANOTDUTY-100501'
        assert assignee == expected_assignee
        return {'key': ticket}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself():
        return {'login': 'test-bot'}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(ticket, **kwargs):
        assert ticket == issue_key
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text, summonees):
        assert ticket == issue_key

    response = await trigger_assing_next(issue_key, json_filter, issue_order)
    assert response.status == 200
    assert await response.json() == {
        'code': 'SUCCESS',
        'message': 'Task completed',
    }
