# pylint: disable=unused-variable
import pytest

from taxi.util import client_session

from taxi_strongbox.components.sessions import clownductor_session as cs


async def test_get_groups_by_host(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(cs.ClownductorSession.base_url, 'GET')
    def request(method, url, *args, **kwargs):
        assert kwargs.get('params', {}).get('fqdn', '') == 'test_host'
        return response_mock(
            json=[
                {
                    'id': 123,
                    'branch_id': 1,
                    'name': 'test_host',
                    'datacenter': 'man',
                    'dom0_name': None,
                    'dom0_updated_at': 0,
                    'branch_name': 'unstable',
                    'service_name': 'some-service',
                    'service_id': 8,
                    'project_name': 'taxi',
                    'project_id': 11,
                },
            ],
        )

    clownductor_session = cs.ClownductorSession(
        session=client_session.get_client_session(), log_extra=None,
    )
    groups = await clownductor_session.get_groups_by_host('test_host')
    assert groups == ['taxi:some-service:unstable']


@pytest.mark.parametrize(
    ['projects_response', 'services_response', 'branches_response', 'result'],
    [
        (
            # Missing project
            [],
            [],
            [],
            False,
        ),
        (
            # Missing service
            [{'id': 1, 'name': 'taxi'}],
            [],
            [],
            False,
        ),
        (
            # Missing branch
            [{'id': 1, 'name': 'taxi'}],
            [{'id': 11, 'name': 'some-service'}],
            [],
            False,
        ),
        (
            # All good
            [{'id': 1, 'name': 'taxi'}],
            [{'id': 11, 'name': 'some-service'}],
            [{'name': 'stable'}, {'name': 'unstable'}],
            True,
        ),
    ],
)
async def test_check_if_group_exists(
        patch_aiohttp_session,
        response_mock,
        projects_response,
        services_response,
        branches_response,
        result,
):
    @patch_aiohttp_session(cs.ClownductorSession.base_url, 'GET')
    def request(method, url, *args, **kwargs):
        if '/api/projects' in url:
            return response_mock(json=projects_response)
        if '/api/services' in url:
            return response_mock(json=services_response)
        if '/api/branches' in url:
            return response_mock(json=branches_response)
        return None

    clownductor_session = cs.ClownductorSession(
        session=client_session.get_client_session(), log_extra=None,
    )
    exists = await clownductor_session.check_if_group_exists(
        'taxi:some-service:unstable',
    )
    assert exists == result
