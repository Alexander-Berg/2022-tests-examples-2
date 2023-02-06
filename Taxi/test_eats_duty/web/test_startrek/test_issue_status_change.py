import pytest


@pytest.mark.config(
    EATS_DUTY_COMPONENT_CHANGE={'notify_on_multiple_assignee': True},
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
@pytest.mark.parametrize(
    'assignee, status',
    [
        pytest.param('user_qa', 'needQa'),
        pytest.param('user_developer', 'needDeveloper'),
        pytest.param('user1', 'unknown'),
    ],
)
async def test_status_aware_udpate(patch, web_app_client, assignee, status):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [{'display': 'test-component-1'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': status},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'
        assert kwargs['assignee'] == assignee

        return {'key': 'EDANOTDUTY-100'}

    response = await web_app_client.post(
        '/v1/startrek/issue-status-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {'code': 'SUCCESS', 'message': 'Task completed'}


@pytest.mark.config(
    EATS_DUTY_COMPONENT_CHANGE={'notify_on_multiple_assignee': True},
    EATS_DUTY_RESPONSIBLE={'test-component-1': {'user': 'user1'}},
)
async def test_status_aware_udpate_no_settings(patch, web_app_client):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [{'display': 'test-component-1'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': 'open'},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'
        assert kwargs['assignee'] == 'user1'

        return {'key': 'EDANOTDUTY-100'}

    response = await web_app_client.post(
        '/v1/startrek/issue-status-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {'code': 'SUCCESS', 'message': 'Task completed'}


@pytest.mark.config(
    EATS_DUTY_COMPONENT_CHANGE={'notify_on_multiple_assignee': True},
    EATS_DUTY_RESPONSIBLE={
        'test-component-1': {
            'user': 'user1',
            'status': {'open': {'user': 'user2'}},
        },
    },
)
async def test_status_aware_udpate_status_unknown(patch, web_app_client):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [{'display': 'test-component-1'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': 'unknown'},
            'assignee': {'id': 'user21'},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        assert False, 'unexpected call to update_ticket'

    response = await web_app_client.post(
        '/v1/startrek/issue-status-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {'code': 'SUCCESS', 'message': 'Task completed'}


@pytest.mark.config(
    EATS_DUTY_RESPONSIBLE={
        'test-component-1': {'status': {'open': {'user': 'user2'}}},
    },
)
async def test_status_aware_udpate_no_base(patch, web_app_client):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [{'display': 'test-component-1'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': 'open'},
            'assignee': {'id': 'user21'},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'
        assert kwargs['assignee'] == 'user2'

        return {'key': 'EDANOTDUTY-100'}

    response = await web_app_client.post(
        '/v1/startrek/issue-status-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {'code': 'SUCCESS', 'message': 'Task completed'}
