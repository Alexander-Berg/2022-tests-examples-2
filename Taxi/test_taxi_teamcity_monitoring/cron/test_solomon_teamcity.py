import re
from typing import Optional

from aiohttp import web
import pytest

from taxi_teamcity_monitoring.generated.cron import run_cron

COUNT_REGEX = re.compile(r'.*count:(\d+).*')
START_REGEX = re.compile(r'.*start:(\d+).*')


def _construct_github_call(
        owner, repo, api_method, *, pull_number: Optional[int] = None,
):
    url = 'https://github.yandex-team.ru/api/v3/repos/%s/%s/%s' % (
        owner,
        repo,
        api_method,
    )
    kwargs: dict = {
        'allow_redirects': True,
        'headers': None,
        'params': None,
        'timeout': 20,
        'json': None,
    }
    if pull_number:
        url += f'/{pull_number}'
        kwargs['headers'] = {'Authorization': 'Token None'}
    return {'method': 'get', 'url': url, 'kwargs': kwargs}


# pylint: disable=too-many-locals
@pytest.mark.now('2019-03-01T12:00:00+0300')
@pytest.mark.config(TEAMCITY_MONITORING_V2_BUILDS_TO_LOAD_PER_REQUEST=2)
async def test_solomon_teamcity(
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        load_json,
        patch,
        db,
        mock_conductor,
        mock_solomon,
        mock_teamcity,
        mock_arcanum,
):
    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_request(request):
        builds_json = load_json('teamcity_api_response.json')
        locator = request.args['locator']
        count_match = COUNT_REGEX.match(locator)
        count = len(builds_json)
        if count_match:
            count = int(count_match.group(1))
        start_match = START_REGEX.match(locator)
        start = 0
        if start_match:
            start = int(start_match.group(1))
        response_json = {'build': builds_json[start : start + count]}
        return web.json_response(response_json)

    @mock_arcanum('/api/v1/review-requests', prefix=True)
    def arcanum_request(request):
        builds_json = load_json('arcanum_api_response.json')
        return web.json_response(builds_json)

    @mock_conductor('/', prefix=True)
    def conductor_request(request):
        return web.json_response(load_json('conductor_response.json'))

    github_api_url = 'https://github.yandex-team.ru/api/v3/'

    @patch_aiohttp_session(github_api_url)
    def github_api_request(method, url, **kwargs):
        if 'backend-cpp' not in url:
            return response_mock(json=[])
        if 'pulls' in url:
            return response_mock(
                json=load_json('github_api_pulls_response.json'),
            )
        if 'events' in url:
            return response_mock(
                json=load_json('github_api_events_response.json'),
            )
        return response_mock(status=500)

    startrek_url = 'https://test-startrack-url/issues/TAXIREL-5115/remotelinks'

    @patch_aiohttp_session(startrek_url, 'GET')
    def startrek_remote_links_request(method, url, **kwargs):
        return response_mock(json=load_json('startrek_response.json'))

    test_solomon_teamcity.solomon_json = load_json('solomon_request.json')

    @mock_solomon('/api/v2/push')
    def handler(request):
        assert (
            request.json
            == test_solomon_teamcity.solomon_json[handler.times_called]
        )
        return {'sensorsProcessed': len(request.json['sensors'])}

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'solomon_teamcity.run_solomon',
            '-t',
            '0',
            '--debug',
        ],
    )

    prefix = (
        '/teamcity/app/rest/builds?locator=affectedProject'
        '(id:YandexTaxiProjects),branch:default:any,'
    )
    fields = (
        '&fields=build(id,status,agent:(name),resultingProperties(*),'
        'triggered(type,date,user),comment(text),buildType(id,projectName,'
        'parameters(property(name,value)),steps(step(id,name,disabled))),'
        'startDate,finishDate,queuedDate,statistics(property(name,value)))'
    )
    assert teamcity_request.next_call()['request'].path_qs == (
        prefix + 'count:2,lookupLimit:5000' + fields
    )
    assert teamcity_request.next_call()['request'].path_qs == (
        prefix + 'count:2,start:2,lookupLimit:5000' + fields
    )
    assert teamcity_request.next_call()['request'].path_qs == (
        prefix + 'count:2,start:4,lookupLimit:5000' + fields
    )
    assert teamcity_request.next_call()['request'].path_qs == (
        prefix + 'count:2,start:6,lookupLimit:5000' + fields
    )
    assert not teamcity_request.has_calls

    assert arcanum_request.next_call()['request'].path_qs == (
        '/arcanum/api/v1/review-requests/8800555/diff-sets?'
        'fields=id,description,status,patch_url,'
        'patch_stats(additions,deletions),created_at,published_at,'
        'discarded_at,arc_branch_heads(from_id,to_id,merge_id)'
    )
    assert not arcanum_request.has_calls

    assert handler.times_called == 5

    assert conductor_request.times_called == 1
    c_request_args = (await conductor_request.wait_call())['request']
    assert str(c_request_args.url).endswith(
        '/api/custom/project-logs?'
        'project=taxi&newer_than=2019-02-28T12:00:00%2B03:00',
    )

    assert startrek_remote_links_request.calls == [
        {
            'method': 'get',
            'url': (
                'https://test-startrack-url/issues/TAXIREL-5115/remotelinks'
            ),
            'kwargs': {
                'data': None,
                'headers': {
                    'Authorization': 'OAuth some_startrack_token',
                    'X-Org-Id': '0',
                },
                'json': None,
                'params': None,
                'timeout': 5,
            },
        },
    ]

    assert github_api_request.calls == [
        _construct_github_call(
            'taxi', 'backend-cpp', 'pulls', pull_number=123,
        ),
        _construct_github_call('nfilchenko', 'backend-cpp', 'events'),
    ]

    builds_data = (
        await db.teamcity_builds_data.find().sort('_id').to_list(None)
    )
    assert builds_data == load_json('raw_teamcity_builds_data.json')
