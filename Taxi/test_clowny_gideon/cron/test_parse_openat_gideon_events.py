import datetime

import pytest

from testsuite.utils import matching

from clowny_gideon.crontasks import parse_openat_gideon_events
from clowny_gideon.generated.cron import run_cron


@pytest.fixture(name='clown_namespaces')
def _clown_namespaces():
    return [{'id': 1, 'name': 'taxi'}]


@pytest.fixture(name='clown_projects')
def _clown_projects():
    return [{'id': 1, 'name': 'taxi', 'namespace_id': 1}]


@pytest.fixture(name='clown_branches')
def _clown_branches():
    return [
        {
            'service_id': 1,
            'direct_link': 'taxi_clowny-gideon_stable',
            'name': 'stable',
            'env': 'stable',
            'id': 1,
        },
    ]


@pytest.fixture(name='clown_services')
def _clown_services():
    return [
        {
            'id': 1,
            'name': 'clowny-gideon',
            'cluster_type': 'nanny',
            'abc_slug': 'taxiclownygideon',
            'project_id': 1,
        },
    ]


def _assert_only_call(handler_mock, expected_request):
    call = handler_mock.next_call()
    assert call['request'].json == expected_request
    assert not handler_mock.has_calls


DEADLINE = (datetime.date.today() + datetime.timedelta(days=10)).strftime(
    '%Y-%m-%d',
)


@pytest.mark.parametrize('use_blacksuite', [True, False])
@pytest.mark.translations(
    clownductor={
        'gideon.openat_events.st.service.summary': {
            'ru': (
                '[gideon-audit] Changed files detected on {project}:{service}'
            ),
        },
        'gideon.openat_events.st.podset.summary': {
            'ru': '[gideon-audit] Changed files detected on {podset_id}',
        },
        'gideon.openat_events.st.common.footer': {
            'ru': (
                'Тикет должен быть решён в течение {deadline_period} дней, '
                'поэтому дедлайн установлен в {deadline_date},\n'
                'Через {deadline_escalation_starts_in} дней будет запущена '
                'эскалация этой проблемы средствами Стартрека.\n'
                '(({wiki_url} {wiki_title}))\n'
            ),
        },
        'gideon.openat_events.st.common.wiki_title': {'ru': 'Регламент'},
        'gideon.openat_events.st.common.event': {
            'ru': (
                'File: {file_path}\nHost: {host}\n'
                'PortoSessionId: {proto_session_id}\n'
                'User: @{user}'
            ),
        },
    },
)
@pytest.mark.usefixtures('clown_cache_mocks')
async def test_task(
        mockserver, load, load_json, mock_gideon, cron_runner, use_blacksuite,
):
    @mock_gideon('/api/query')
    def _gideon_query_handler(request):
        kind_filter = None
        for filter_ in request.json['filter']:
            if filter_['key'] == 'kind':
                if kind_filter is None:
                    assert (
                        len(filter_['values']) == 1
                    ), 'its strange to search by several kinds'
                    kind_filter = filter_['values'][0]
                else:
                    assert (
                        False
                    ), 'its strange to have several separate kind filters'

        assert kind_filter is not None, 'kind filter is required'
        if kind_filter == 'OpenAt':
            return load_json('gideon_open_at_response.json')
        if kind_filter == 'NewSession':
            return load_json('gideon_new_session_response.json')
        raise RuntimeError(f'unknown kind filter {kind_filter!r}')

    @mockserver.json_handler('/startrek/issues/_search')
    def _search_handler(request):
        summary_for_service = (
            '[gideon-audit] Changed files detected on taxi:clowny-gideon'
        )
        if request.json['filter']['summary'] == summary_for_service:
            return [{'key': 'TAXIADMIN-1'}]
        return []

    @mockserver.json_handler('/startrek/issues/TAXIADMIN-1/comments')
    def _create_comment_handler(request):
        return {}

    @mockserver.json_handler('/startrek/issues')
    def _create_ticket_handler(request):
        return {'key': 'TAXIADMIN-2'}

    if use_blacksuite:
        await cron_runner.parse_openat_gideon_events()
    else:
        await run_cron.main(
            ['clowny_gideon.crontasks.parse_openat_gideon_events', '-t', '0'],
        )

    _assert_only_call(
        _create_comment_handler,
        {'text': load('service_comment_text.txt').format(deadline=DEADLINE)},
    )
    _assert_only_call(
        _create_ticket_handler,
        {
            'components': ['duty', 'package-audit'],
            'description': load('podset_new_ticket_text.txt').format(
                deadline=DEADLINE,
            ),
            'queue': {'key': 'TAXIADMIN'},
            'summary': (
                '[gideon-audit] Changed files detected on '
                'taxi-clowny-gideon-testing'
            ),
            'type': {'key': 'task'},
            'unique': matching.any_string,
            'tags': ['auto-robot', 'audit'],
        },
    )


@pytest.mark.usefixtures('clown_cache_mocks')
async def test_events_filter(load_json, mock_gideon, cron_context):
    @mock_gideon('/api/query')
    def _handler(_):
        return load_json('gideon_open_at_response.json')

    project = parse_openat_gideon_events.Project.from_config(
        {
            'name': 'test',
            'period': '',
            'pod_set_id_pattern': '',
            'white_list': ['.*'],
            'black_list': [
                '/root/.bash_history',
                '/dev/tty',
                r'.*\.swp',
                r'.*\.swx',
                r'/root/\.viminfo',
            ],
        },
    )
    events = await cron_context.gideon_client.get_open_at_events(
        project.pod_set_id_pattern, project.period,
    )
    assert [str(x.filename) for x in events] == [
        '.aa.tmp.swp',
        '.aa.tmp.swx',
        '.aa.tmp.swp',
        'aa.tmp',
        '/root/.viminfo.tmp',
        '/dev/tty',
        '/root/.bash_history',
        '/dev/tty',
    ]
    events = parse_openat_gideon_events.filter_events(project, events)
    assert [str(x.filename) for x in events] == ['aa.tmp']
