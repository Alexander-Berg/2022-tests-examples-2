from aiohttp import web
import pytest

from taxi_teamcity_monitoring.crontasks.arcadia_checks_watchdog import (
    run_arcadia_checks_watchdog,
)
from taxi_teamcity_monitoring.generated.cron import run_cron


ARCANUM_API_PREFIX = '/api/'
QUERY = {'_id': 'arcadia_checks_last_merged_time'}


@pytest.mark.config(
    TEAMCITY_MONITORING_ARCADIA_CHECKS_ENABLED=True,
    TEAMCITY_MONITORING_ARCADIA_CHECKS_PATHS=['/taxi/backend-py3'],
    TEAMCITY_MONITORING_ARCADIA_CHECKS_TICKET_TITLE_TPL='{review_id}',
    TEAMCITY_MONITORING_ARCADIA_CHECKS_TICKET_BODY_TPL=(
        '{review_id} {activities}'
    ),
    TEAMCITY_MONITORING_ARCADIA_CHECKS_COMMENT_BODY='text',
    TEAMCITY_MONITORING_ARCADIA_FORCEMERGE_TICKET_TITLE_TPL='{review_id}',
    TEAMCITY_MONITORING_ARCADIA_FORCEMERGE_TICKET_BODY_TPL='{review_id}',
    TEAMCITY_MONITORING_ARCADIA_FORCEMERGE_COMMENT_BODY='force-merge',
)
async def test_arcadia_checks_watchdog(
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        async_commands_mock,
        db,
        mock_arcanum,
):
    update = {'$set': {'value': '2021-06-16T14:45:34.419000Z'}}
    await db.teamcity_monitoring_settings.update_one(
        filter=QUERY, update=update, upsert=True,
    )

    @mock_arcanum(ARCANUM_API_PREFIX, prefix=True)
    async def arcanum_request(request):

        arcanum_api_suffix = request.path.split(ARCANUM_API_PREFIX)[1]
        if arcanum_api_suffix.startswith('v1/review-requests'):
            reviews_info = load_json('arcanum_reviews_info.json')
            return web.json_response(data=reviews_info)
        if arcanum_api_suffix.startswith('review/review-request'):
            review_id = arcanum_api_suffix.split('/')[2]
            reviews_activities = load_json(
                f'arcanum_activities_info_{review_id}.json',
            )
            return web.json_response(data=reviews_activities)

        assert False, (
            'this should not happened, command: %s' % arcanum_api_suffix
        )

    @patch_aiohttp_session('https://test-startrack-url/')
    def st_request(method, url, json, **kwargs):
        if method == 'post':
            return response_mock(json={'key': 'TAXIARCAUDIT-456'})
        ticket_id = url.split('/')[4]
        responses = {
            'TAXIARCAUDIT-268': {
                'key': 'TAXIARCAUDIT-268',
                'status': {'key': 'closed'},
                'resolution': {'key': 'fixed'},
                'assignee': {'id': 'example1'},
                'resolvedAt': '2010-01-01T00:00:00.0+0000',
            },
        }
        return response_mock(json=responses[ticket_id])

    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.TICKET_URL_TPL',
        'https://test-startrack-url/{ticket_id}',
    )

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'arcadia_checks_watchdog.run_arcadia_checks_watchdog',
            '-t',
            '0',
        ],
    )

    arcanum_calls = []

    while arcanum_request.has_calls:
        req = arcanum_request.next_call()['request']
        cut_url = req.url.split('/arcanum/api/')[-1]
        arcanum_calls.append({'method': req.method, 'url': cut_url})

    assert arcanum_calls == [
        {
            'method': 'GET',
            'url': (
                'v1/review-requests?'
                'limit=10000&'
                'query=not(open())%3Bpath(/taxi/backend-py3)&sort=-updated_at&'
                'fields=review_requests(id,author(name),full_status,'
                'updated_at,checks(system,type,required,status,data))'
            ),
        },
        {'method': 'GET', 'url': 'review/review-request/2039873/activity'},
        {'method': 'GET', 'url': 'review/review-request/2174821/activity'},
        {'method': 'GET', 'url': 'review/review-request/1830350/activity'},
        {'method': 'GET', 'url': 'review/review-request/1339132/activity'},
        {'method': 'GET', 'url': 'review/review-request/3427151/activity'},
    ]

    calls = st_request.calls
    for call in calls:
        call.pop('kwargs')
        if call['json'] is not None:
            if 'unique' in call['json']:
                call['json'].pop('unique')

    assert calls == [
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': '2039873',
                'queue': {'key': 'TAXIARCAUDIT'},
                'description': '2039873',
                'type': {'key': 'task'},
                'assignee': 'alberist',
            },
        },
        {
            'method': 'post',
            'url': (
                'https://test-startrack-url/issues/TAXIARCAUDIT-456/comments'
            ),
            'json': {'text': 'force-merge', 'summonees': ['alberist']},
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': '1830350',
                'queue': {'key': 'TAXIARCAUDIT'},
                'description': (
                    '1830350 Отключенная проверка: YandexTaxiProjects_'
                    'TaxiBackendPy3Arcadia_PullRequests_PullRequest\n'
                    'Пользователь, отключивший проверку: кто:rumkex\n'
                    'Причина отключения: changes are not used in tests\n'
                ),
                'type': {'key': 'task'},
                'assignee': 'rumkex',
            },
        },
        {
            'method': 'post',
            'url': (
                'https://test-startrack-url/issues/TAXIARCAUDIT-456/comments'
            ),
            'json': {'text': 'text', 'summonees': ['rumkex']},
        },
    ]

    teamcity_monitoring_settings = [
        doc
        async for doc in db.teamcity_monitoring_settings.find().sort('_id', 1)
    ]
    assert teamcity_monitoring_settings == [
        {
            '_id': 'arcadia_checks_last_merged_time',
            'value': '2021-12-08T17:51:09.529651Z',
        },
    ]


def test_check_filters():
    filter_list_checks = [
        '+:arcanum.',
        '+:ci.',
        '-:arcanum.published',
        '-:ci.test',
    ]
    checks_statuses = {
        'arcanum.approved': 'sample',
        'arcanum.published': 'sample',
        'ci.test': 'sample',
        'ci.build': 'sample',
        'taxi-teamcity.YandexTaxi': 'sample',
    }

    filtered_checks = run_arcadia_checks_watchdog.filter_check_statuses(
        checks_statuses, filter_list_checks,
    )
    assert filtered_checks == {
        'arcanum.approved': 'sample',
        'ci.build': 'sample',
    }
