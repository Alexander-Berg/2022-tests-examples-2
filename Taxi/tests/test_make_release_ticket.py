from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import pytest

import make_release_ticket


class Params(NamedTuple):
    project: str
    version: str
    assignee: str
    st_component_opened: Dict[int, List[Dict[str, str]]] = {}
    st_create_calls: List[Dict[str, Any]] = []
    st_update_calls: List[Dict[str, Any]] = []
    st_create_component_calls: List[Dict[str, Any]] = []
    st_get_opened_releases_calls: List[Dict[str, Any]] = []
    tc_set_parameter_calls: List[Dict[str, Any]] = [
        {
            'name': 'env.RELEASE_TICKET',
            'value': 'https://st.yandex-team.ru/TAXIREL-222',
        },
    ]
    tc_report_build_problems_calls: List[Dict[str, Any]] = []
    tc_report_build_number_calls: List[Dict[str, Any]] = [
        {'build_number': '1.1.1'},
    ]
    description: Optional[str] = None
    related_tickets: Optional[List] = None
    followers: Optional[List[str]] = None
    queue: Optional[str] = None
    prev_release_ticket: Optional[str] = None
    allow_attaching: bool = False
    tool_debug: bool = False


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                project='protocol',
                version='1.1.1',
                assignee='dteterin',
                st_create_calls=[
                    {
                        'json': {
                            'assignee': 'dteterin',
                            'components': [75],
                            'description': '',
                            'followers': [],
                            'queue': 'TAXIREL',
                            'summary': 'Release protocol 1.1.1',
                        },
                    },
                ],
                st_get_opened_releases_calls=[{'component': 75}],
                st_component_opened={75: []},
            ),
            id='simple_case',
        ),
        pytest.param(
            Params(
                project='taxi-graph',
                version='12345',
                assignee='dteterin',
                followers=['dteterin'],
                description='Arcadia some release',
                tc_report_build_number_calls=[{'build_number': '12345'}],
                st_create_calls=[
                    {
                        'json': {
                            'assignee': 'dteterin',
                            'components': [94],
                            'description': 'Arcadia some release',
                            'followers': ['dteterin'],
                            'queue': 'TAXIREL',
                            'summary': 'Release taxi-graph 12345',
                        },
                    },
                ],
                st_component_opened={94: []},
                st_get_opened_releases_calls=[{'component': 94}],
                allow_attaching=True,
            ),
            id='with_allow_attaching',
        ),
        pytest.param(
            Params(
                project='taxi-graph',
                version='12345',
                assignee='dteterin',
                followers=['dteterin'],
                related_tickets=['TAXITOOLS-321', 'TAXITOOLS-123'],
                tc_report_build_number_calls=[{'build_number': '12345'}],
                st_create_calls=[],
                tc_set_parameter_calls=[
                    {
                        'name': 'env.BUILD_PROBLEM',
                        'value': 'Attach to release is disabled',
                    },
                ],
                tc_report_build_problems_calls=[
                    {
                        'description': 'Attach to release is disabled',
                        'identity': None,
                    },
                ],
                prev_release_ticket='TAXIREL-11585',
            ),
            id='without_allow_attaching',
        ),
        pytest.param(
            Params(
                project='protocol',
                version='1.1.2',
                assignee='dteterin',
                description='Arcadia attach',
                st_update_calls=[
                    {
                        'json': {
                            'assignee': 'dteterin',
                            'description': (
                                'some\ntext\n'
                                'Revision: 1.1.2\nArcadia attach'
                            ),
                            'followers': {'add': []},
                            'summary': 'summary, 1.1.2',
                        },
                        'ticket': 'TAXIREL-11585',
                    },
                ],
                tc_set_parameter_calls=[
                    {
                        'name': 'env.RELEASE_TICKET',
                        'value': 'https://st.yandex-team.ru/TAXIREL-11585',
                    },
                ],
                tc_report_build_number_calls=[{'build_number': '1.1.2'}],
                prev_release_ticket='TAXIREL-11585',
                allow_attaching=True,
            ),
            id='with_attach_to_release',
        ),
        pytest.param(
            Params(
                project='taxi-graph',
                version='12345',
                assignee='dteterin',
                followers=['dteterin', 'alberist'],
                description='Arcadia some release',
                related_tickets=['TAXITOOLS-321', 'TAXITOOLS-123'],
                tc_report_build_number_calls=[{'build_number': '12345'}],
                st_create_calls=[
                    {
                        'json': {
                            'assignee': 'dteterin',
                            'components': [94],
                            'description': (
                                'Arcadia some release\n'
                                'TAXITOOLS-123\nTAXITOOLS-321'
                            ),
                            'followers': ['alberist', 'dteterin'],
                            'queue': 'TAXIREL',
                            'summary': 'Release taxi-graph 12345',
                        },
                    },
                ],
                st_get_opened_releases_calls=[{'component': 94}],
                st_component_opened={94: []},
            ),
            id='with_description_and_tickets',
        ),
        pytest.param(
            Params(
                project='protocol',
                version='1.1.1',
                assignee='dteterin',
                st_get_opened_releases_calls=[{'component': 75}],
                st_component_opened={75: [{'key': 'TAXIREL-9001'}]},
                tc_set_parameter_calls=[
                    {
                        'name': 'env.BUILD_PROBLEM',
                        'value': (
                            'Old release tickets are opened: '
                            '[https://st.yandex-team.ru/TAXIREL-9001]. '
                            'More information about new releases and '
                            'attachment to releases: '
                            'https://wiki.yandex-team.ru/taxi/backend'
                            '/basichowto/deploy/'
                        ),
                    },
                ],
                tc_report_build_problems_calls=[
                    {
                        'description': (
                            'Old release tickets are opened: '
                            '[https://st.yandex-team.ru/TAXIREL-9001]. '
                            'More information about new releases and '
                            'attachment to releases: '
                            'https://wiki.yandex-team.ru/taxi/backend'
                            '/basichowto/deploy/'
                        ),
                        'identity': None,
                    },
                ],
            ),
            id='old_ticket_opened',
        ),
        pytest.param(
            Params(
                project='yandex-taxi-cool-project',
                version='vers1',
                assignee='dteterin',
                followers=['dteterin'],
                tc_report_build_number_calls=[{'build_number': 'vers1'}],
                st_create_calls=[
                    {
                        'json': {
                            'assignee': 'dteterin',
                            'components': [100],
                            'description': '',
                            'followers': ['dteterin'],
                            'queue': 'TAXIREL',
                            'summary': (
                                'Release yandex-taxi-cool-project vers1'
                            ),
                        },
                    },
                ],
                st_create_component_calls=[
                    {
                        'json': {
                            'name': 'yandex-taxi-cool-project',
                            'queue': 'TAXIREL',
                        },
                    },
                ],
                st_component_opened={100: []},
            ),
            id='new_component',
        ),
        pytest.param(
            Params(
                project='protocol',
                version='1.1.1',
                assignee='dteterin',
                tool_debug=True,
            ),
            id='TOOL_DEBUG',
        ),
    ],
)
def test_create_ticket(
        params,
        monkeypatch,
        startrek,
        teamcity_report_problems,
        teamcity_report_build_number,
        teamcity_set_parameters,
):
    startrek.component_opened = params.st_component_opened

    if params.tool_debug:
        monkeypatch.setattr('make_release_ticket.DEBUG', '1')
    if params.prev_release_ticket:
        monkeypatch.setenv('RELEASE_TICKET', params.prev_release_ticket)

    argv = [
        '--project',
        params.project,
        '--version',
        params.version,
        '--assignee',
        params.assignee,
    ]
    if params.followers:
        argv += ['--followers', *params.followers]
    if params.queue:
        argv += ['--queue', params.queue]
    if params.description:
        argv += ['--description', params.description]
    if params.related_tickets:
        argv += ['--related-tickets', *params.related_tickets]
    if params.allow_attaching:
        argv.append('--allow-attaching')
    make_release_ticket.main(argv)

    assert startrek.create_ticket.calls == params.st_create_calls
    assert startrek.update_ticket.calls == params.st_update_calls
    assert startrek.create_component.calls == params.st_create_component_calls
    assert (
        startrek.get_opened_releases.calls
        == params.st_get_opened_releases_calls
    )
    assert teamcity_set_parameters.calls == params.tc_set_parameter_calls
    assert (
        teamcity_report_problems.calls == params.tc_report_build_problems_calls
    )
    assert (
        teamcity_report_build_number.calls
        == params.tc_report_build_number_calls
    )
