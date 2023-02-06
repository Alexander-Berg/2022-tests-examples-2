import pytest

from clownductor.generated.cron import run_cron


@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
async def test_create_remote_jobs(patch):
    @patch('clownductor.internal.utils.startrek.find_comment')
    async def find_comment(st_api, st_key, comment_text):
        assert st_api is not None
        assert st_key == 'ticket_name'
        return None

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return {'assignee': {'id': 'robot-taxi-clown'}}

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert 'robot-taxi-clown' not in kwargs['summonees']
        return {}

    @patch('staff_api.components.StaffClient.get_persons')
    async def get_persons(logins, fields):
        assert len(fields) == 2
        robot_names = ['robot-taxi-clown']
        result = []
        for login in logins:
            result.append(
                {
                    'login': login,
                    'robot_owners': [
                        ['elrusso'] if login in robot_names else [],
                    ],
                },
            )
        return result

    await run_cron.main(['clownductor.crontasks.check_long_jobs', '-t', '0'])

    assert len(find_comment.calls) == 2
    assert len(create_comment.calls) == 2
    assert len(get_ticket.calls) == 2
    assert len(get_persons.calls) == 2
