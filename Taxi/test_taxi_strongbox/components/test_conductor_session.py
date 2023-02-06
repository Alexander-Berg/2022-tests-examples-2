# pylint: disable=unused-variable
from taxi.util import client_session

from taxi_strongbox.components.sessions import conductor_session as cs


async def test_conductor_session(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(cs.ConductorSession.base_url, 'GET')
    def request(method, url, *args, **kwargs):
        assert 'test_host' in url
        return response_mock('test_group_1\ntest_group_2')

    conductor_session = cs.ConductorSession(
        session=client_session.get_client_session(), log_extra=None,
    )
    groups = await conductor_session.get_groups_by_host('test_host')
    assert groups == ['test_group_1', 'test_group_2']
