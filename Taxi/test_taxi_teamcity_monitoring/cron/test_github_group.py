import functools
from typing import Dict
from typing import List
from typing import NamedTuple
from urllib import parse as urlparse

from aiohttp import web
import pytest

from taxi_teamcity_monitoring.crontasks.github_group import run_github_group
from taxi_teamcity_monitoring.generated.cron import run_cron


class Params(NamedTuple):
    staff: List[Dict]
    expected_github_calls: List[Dict]
    expected_staff_calls: List[Dict]
    has_exit_code: bool = False
    add_memberships_response: int = 0
    team_members: Dict = {
        '1234': [
            {'login': 'oyaso'},
            {'login': 'alberist'},
            {'login': 'aselutin'},
        ],
        '9876': [{'login': 'petya'}, {'login': 'kolya'}],
    }
    all_teams: List[Dict] = [
        {'id': 1234, 'slug': 'acc-automatization'},
        {'id': 537, 'slug': 'acc-efficiency'},
        {'id': 9876, 'slug': 'acc-develop-eats'},
    ]
    all_users: List[Dict] = [
        {'login': 'oyaso'},
        {'login': 'alberist'},
        {'login': 'aselutin'},
        {'login': 'vasya'},
        {'login': 'petya'},
        {'login': 'kolya'},
        {'login': 'ivan'},
    ]
    logger_error_list: List[str] = []


def staff_query(department: str, page: str = '') -> str:
    return (
        f'groupmembership?_query=group.url+%3D%3D+%22{department}%22+or+'
        f'group.ancestors.url+%3D%3D+%22{department}%22&_fields=id,'
        f'person.login,group.url{page}&_sort=id&group.type='
        'department&person.official.is_dismissed=false&person.'
        'official.is_robot=false'
    )


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                staff=[
                    {
                        'yandex_taxi_automatization_100500': {
                            'result': [
                                {'person': {'login': 'oyaso'}},
                                {'person': {'login': 'aselutin'}},
                            ],
                        },
                        'yandex_rkub_taxi_develop_6154': {
                            'result': [{'person': {'login': 'alberist'}}],
                        },
                        'yandex_chicken': {
                            'result': [{'person': {'login': 'petya'}}],
                        },
                        'yandex_kebab': {
                            'result': [{'person': {'login': 'kolya'}}],
                        },
                    },
                ],
                expected_github_calls=[
                    {'method': 'GET', 'url': 'users'},
                    {'method': 'GET', 'url': 'orgs/taxi/teams'},
                    {'method': 'GET', 'url': 'teams/1234/members?role=all'},
                    {'method': 'GET', 'url': 'orgs/eats/teams'},
                    {'method': 'GET', 'url': 'teams/9876/members?role=all'},
                ],
                expected_staff_calls=[
                    {
                        'method': 'GET',
                        'url': staff_query(
                            'yandex_taxi_automatization_100500',
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': staff_query('yandex_rkub_taxi_develop_6154'),
                    },
                    {'method': 'GET', 'url': staff_query('yandex_chicken')},
                    {'method': 'GET', 'url': staff_query('yandex_kebab')},
                ],
            ),
            id='nothing to add',
        ),
        pytest.param(
            Params(
                staff=[
                    {
                        'yandex_taxi_automatization_100500': {
                            'result': [
                                {'person': {'login': 'oyaso'}},
                                {'person': {'login': 'aselutin'}},
                            ],
                        },
                        'yandex_rkub_taxi_develop_6154': {
                            'result': [
                                {'person': {'login': 'alberist'}},
                                {'person': {'login': 'vasya'}},
                            ],
                        },
                        'yandex_chicken': {
                            'result': [{'person': {'login': 'petya'}}],
                        },
                        'yandex_kebab': {
                            'result': [
                                {'person': {'login': 'kolya'}},
                                {'person': {'login': 'ivan'}},
                                {'person': {'login': 'not_in_github'}},
                            ],
                        },
                    },
                ],
                expected_github_calls=[
                    {'method': 'GET', 'url': 'users'},
                    {'method': 'GET', 'url': 'orgs/taxi/teams'},
                    {'method': 'GET', 'url': 'teams/1234/members?role=all'},
                    {'method': 'PUT', 'url': 'teams/1234/memberships/vasya'},
                    {'method': 'GET', 'url': 'orgs/eats/teams'},
                    {'method': 'GET', 'url': 'teams/9876/members?role=all'},
                    {'method': 'PUT', 'url': 'teams/9876/memberships/ivan'},
                ],
                expected_staff_calls=[
                    {
                        'method': 'GET',
                        'url': staff_query(
                            'yandex_taxi_automatization_100500',
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': staff_query('yandex_rkub_taxi_develop_6154'),
                    },
                    {'method': 'GET', 'url': staff_query('yandex_chicken')},
                    {'method': 'GET', 'url': staff_query('yandex_kebab')},
                ],
            ),
            id='add to several groups',
        ),
        pytest.param(
            Params(
                staff=[
                    {
                        'yandex_taxi_automatization_100500': {
                            'result': [
                                {'person': {'login': 'oyaso'}},
                                {'person': {'login': 'aselutin'}},
                            ],
                            'page': 1,
                            'links': {
                                'last': (
                                    'https://staff-api.yandex-team.ru/v3/'
                                    + staff_query(
                                        'yandex_taxi_automatization_100500',
                                    )
                                    + '&_page=2'
                                ),
                                'next': (
                                    'https://staff-api.yandex-team.ru/v3/'
                                    + staff_query(
                                        'yandex_taxi_automatization_100500',
                                    )
                                    + '&_page=2'
                                ),
                            },
                        },
                        'yandex_rkub_taxi_develop_6154': {'result': []},
                        'yandex_chicken': {'result': []},
                        'yandex_kebab': {'result': []},
                    },
                    {
                        'yandex_taxi_automatization_100500': {
                            'result': [
                                {'person': {'login': 'alberist'}},
                                {'person': {'login': 'vasya'}},
                            ],
                            'page': 2,
                            'links': {
                                'last': (
                                    'https://staff-api.yandex-team.ru/v3/'
                                    + staff_query(
                                        'yandex_taxi_automatization_100500',
                                    )
                                    + '&_page=2'
                                ),
                                'next': '',
                            },
                        },
                        'yandex_rkub_taxi_develop_6154': {'result': []},
                        'yandex_chicken': {'result': []},
                        'yandex_kebab': {'result': []},
                    },
                ],
                expected_github_calls=[
                    {'method': 'GET', 'url': 'users'},
                    {'method': 'GET', 'url': 'orgs/taxi/teams'},
                    {'method': 'GET', 'url': 'teams/1234/members?role=all'},
                    {'method': 'PUT', 'url': 'teams/1234/memberships/vasya'},
                    {'method': 'GET', 'url': 'orgs/eats/teams'},
                    {'method': 'GET', 'url': 'teams/9876/members?role=all'},
                ],
                expected_staff_calls=[
                    {
                        'method': 'GET',
                        'url': staff_query(
                            'yandex_taxi_automatization_100500',
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': staff_query(
                            'yandex_taxi_automatization_100500', '&_page=2',
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': staff_query('yandex_rkub_taxi_develop_6154'),
                    },
                    {'method': 'GET', 'url': staff_query('yandex_chicken')},
                    {'method': 'GET', 'url': staff_query('yandex_kebab')},
                ],
            ),
            id='pagination',
        ),
        pytest.param(
            Params(
                staff=[
                    {
                        'yandex_taxi_automatization_100500': {
                            'result': [
                                {'person': {'login': 'oyaso'}},
                                {'person': {'login': 'aselutin'}},
                            ],
                        },
                        'yandex_rkub_taxi_develop_6154': {
                            'result': [
                                {'person': {'login': 'alberist'}},
                                {'person': {'login': 'vasya'}},
                            ],
                        },
                        'yandex_chicken': {
                            'result': [{'person': {'login': 'petya'}}],
                        },
                        'yandex_kebab': {
                            'result': [
                                {'person': {'login': 'kolya'}},
                                {'person': {'login': 'ivan'}},
                                {'person': {'login': 'not_in_github'}},
                            ],
                        },
                    },
                ],
                expected_github_calls=[
                    {'method': 'GET', 'url': 'users'},
                    {'method': 'GET', 'url': 'orgs/taxi/teams'},
                    {'method': 'GET', 'url': 'teams/1234/members?role=all'},
                    {'method': 'PUT', 'url': 'teams/1234/memberships/vasya'},
                    {'method': 'GET', 'url': 'orgs/eats/teams'},
                    {'method': 'GET', 'url': 'teams/9876/members?role=all'},
                    {'method': 'PUT', 'url': 'teams/9876/memberships/ivan'},
                ],
                expected_staff_calls=[
                    {
                        'method': 'GET',
                        'url': staff_query(
                            'yandex_taxi_automatization_100500',
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': staff_query('yandex_rkub_taxi_develop_6154'),
                    },
                    {'method': 'GET', 'url': staff_query('yandex_chicken')},
                    {'method': 'GET', 'url': staff_query('yandex_kebab')},
                ],
                add_memberships_response=403,
                has_exit_code=True,
                logger_error_list=[
                    'Cannot add membership `vasya` to the '
                    '`acc-automatization` group',
                    'Cannot add membership `ivan` to the '
                    '`acc-develop-eats` group',
                ],
            ),
            id='forbidden 403',
        ),
        pytest.param(
            Params(
                staff=[
                    {
                        'yandex_taxi_automatization_100500': {
                            'result': [
                                {'person': {'login': 'oyaso'}},
                                {'person': {'login': 'aselutin'}},
                            ],
                        },
                        'yandex_rkub_taxi_develop_6154': {
                            'result': [
                                {'person': {'login': 'alberist'}},
                                {'person': {'login': 'vasya'}},
                            ],
                        },
                        'yandex_chicken': {
                            'result': [{'person': {'login': 'petya'}}],
                        },
                        'yandex_kebab': {
                            'result': [
                                {'person': {'login': 'kolya'}},
                                {'person': {'login': 'ivan'}},
                                {'person': {'login': 'not_in_github'}},
                            ],
                        },
                    },
                ],
                expected_github_calls=[
                    {'method': 'GET', 'url': 'users'},
                    {'method': 'GET', 'url': 'orgs/taxi/teams'},
                    {'method': 'GET', 'url': 'teams/1234/members?role=all'},
                    {'method': 'PUT', 'url': 'teams/1234/memberships/vasya'},
                    {'method': 'GET', 'url': 'orgs/eats/teams'},
                    {'method': 'GET', 'url': 'teams/9876/members?role=all'},
                    {'method': 'PUT', 'url': 'teams/9876/memberships/ivan'},
                ],
                expected_staff_calls=[
                    {
                        'method': 'GET',
                        'url': staff_query(
                            'yandex_taxi_automatization_100500',
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': staff_query('yandex_rkub_taxi_develop_6154'),
                    },
                    {'method': 'GET', 'url': staff_query('yandex_chicken')},
                    {'method': 'GET', 'url': staff_query('yandex_kebab')},
                ],
                add_memberships_response=422,
                has_exit_code=True,
                logger_error_list=[
                    'Cannot add membership `vasya` to the '
                    '`acc-automatization` group',
                    'Cannot add membership `ivan` to the '
                    '`acc-develop-eats` group',
                ],
            ),
            id='forbidden 422',
        ),
    ],
)
@pytest.mark.config(
    TEAMCITY_MONITORING_GITHUB_GROUP_ENABLED=True,
    TEAMCITY_MONITORING_GITHUB_GROUP_MATCHES=[
        {
            'organization': 'taxi',
            'github': 'acc-automatization',
            'staff': [
                'yandex_taxi_automatization_100500',
                'yandex_rkub_taxi_develop_6154',
            ],
        },
        {
            'organization': 'eats',
            'github': 'acc-develop-eats',
            'staff': ['yandex_chicken', 'yandex_kebab'],
        },
    ],
)
def test_github_group(monkeypatch, mock_github, mock_staff, params):
    @mock_github('/api/v3', prefix=True)
    async def github_request(request):
        if request.path.endswith('/users'):
            return web.json_response(params.all_users)
        if request.path.endswith('/teams'):
            return web.json_response(params.all_teams)
        if request.path.endswith('/members'):
            for key in params.team_members.keys():
                if key in request.url:
                    return web.json_response(params.team_members[key])
        if request.method == 'PUT':
            if params.add_memberships_response != 0:
                return web.json_response(
                    status=params.add_memberships_response,
                    data={
                        'message': 'some message',
                        'documentation_url': 'some url',
                    },
                )
            return web.json_response(
                status=200,
                data={'url': 'some url', 'role': 'member', 'state': 'active'},
            )

    @mock_staff('/v3', prefix=True)
    async def staff_request(request):
        if request.path.endswith('/groupmembership'):
            query = urlparse.urlparse(request.url).query
            parsed_query = urlparse.parse_qs(query)
            if '_page' not in parsed_query:
                page_no = 0
            else:
                page_no = int(parsed_query['_page'][0]) - 1
            for key in params.staff[page_no].keys():
                if key in request.url:
                    return web.json_response(params.staff[page_no][key])

    _logger_error_messages = []
    original_logger_error = run_github_group.logger.error

    def _wrapper_logger_error(*args, **kwargs):
        log_str = args[0]
        output_string = log_str % args[1:]
        _logger_error_messages.append(output_string)
        return original_logger_error(*args, **kwargs)

    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.'
        'github_group.run_github_group.logger.error',
        _wrapper_logger_error,
    )

    run_cron_main = functools.partial(
        run_cron.main,
        [
            'taxi_teamcity_monitoring.crontasks.'
            'github_group.run_github_group',
            '-t',
            '0',
        ],
    )
    if params.has_exit_code:
        with pytest.raises(run_github_group.GithubGroupError):
            run_cron_main()
    else:
        run_cron_main()

    assert github_request.times_called == len(params.expected_github_calls)
    i = 0
    while github_request.has_calls:
        gh_req = github_request.next_call()['request']
        assert gh_req.method == params.expected_github_calls[i]['method']
        short_url = str(gh_req.url).split('/', maxsplit=6)[6]
        assert short_url == params.expected_github_calls[i]['url']
        i += 1

    assert staff_request.times_called == len(params.expected_staff_calls)
    i = 0
    while staff_request.has_calls:
        sf_req = staff_request.next_call()['request']
        assert sf_req.method == params.expected_staff_calls[i]['method']
        short_url = str(sf_req.url).split('/', maxsplit=5)[5]
        assert short_url == params.expected_staff_calls[i]['url']
        i += 1

    assert _logger_error_messages == params.logger_error_list
