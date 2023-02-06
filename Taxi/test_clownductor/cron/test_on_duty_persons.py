import datetime

import pytest

from clownductor.generated.cron import run_cron
from clownductor.internal.utils import postgres
from clownductor.internal.utils import startrek as startrek_utils

TRANSLATIONS = {
    'clownductor.duty.on_duty_person.comment.intro_long_running_jobs': {
        'ru': 'long_intro_long_running_jobs\n',
    },
    'clownductor.duty.on_duty_person.comment.service_long_running_jobs': {
        'ru': (
            '===== ((https://tariff-editor.taxi.yandex-team.ru/'
            'services/{project_id}/edit/{service_id}/jobs '
            '{service_name}/{project_name})) =====\n'
        ),
    },
    'clownductor.duty.on_duty_person.comment.job_link': {
        'ru': (
            '((https://tariff-editor.taxi.yandex-team.ru/'
            'services/{project_id}/edit/{service_id}/jobs?jobId={job_id} '
            '{job_name}:{job_id}))\n'
        ),
    },
    'clownductor.duty.on_duty_person.comment.service_info': {
        'ru': (
            '{spoiler_start} Служебная информация\n'
            'Problem slug: {problem_slug} {spoiler_end}\n'
        ),
    },
    'clownductor.duty.on_duty_person.comment.start_duty': {
        'ru': 'Обрати внимание, создан тикет для дежурства {login}@.',
    },
    'clownductor.duty.on_duty_person.comment.end_duty': {
        'ru': 'Дежурство закончено, тикет закрыт.',
    },
}

LONG_RUNNING_JOBS = (
    '===== ((https://tariff-editor.taxi.yandex-team.ru/'
    'services/1/edit/1/jobs lavka-service/lavka)) =====\n'
    '((https://tariff-editor.taxi.yandex-team.ru/services/1'
    '/edit/1/jobs?jobId=1 DeployNannyServiceNoApprove:1))\n'
    '((https://tariff-editor.taxi.yandex-team.ru/services/1'
    '/edit/1/jobs?jobId=2 DeployOneNannyService:2))\n'
    '===== ((https://tariff-editor.taxi.yandex-team.ru/'
    'services/2/edit/2/jobs eda-service/eda)) =====\n'
    '((https://tariff-editor.taxi.yandex-team.ru/services/2'
    '/edit/2/jobs?jobId=3 DeployNannyServiceNoApprove:3))\n'
    '((https://tariff-editor.taxi.yandex-team.ru/services/2'
    '/edit/2/jobs?jobId=4 DeployOneNannyService:4))\n'
    '<{ Служебная информация\n'
    'Problem slug: %s }>\n'
)

EXPECTED_COMMENTS = [
    'Обрати внимание, создан тикет для дежурства karachevda@.',
    'long_intro_long_running_jobs\n'
    + LONG_RUNNING_JOBS
    % startrek_utils.ProblemSlug.START_DUTY_LONG_RUNNING_JOBS.value,
    LONG_RUNNING_JOBS
    % startrek_utils.ProblemSlug.END_DUTY_LONG_RUNNING_JOBS.value,
    LONG_RUNNING_JOBS,
    'Дежурство закончено, тикет закрыт.',
]

CONFIG_MARK = pytest.mark.config(
    CLOWNDUCTOR_ON_DUTY_PERSONS={
        'enabled': True,
        'disabled_for': [],
        'workday_timespan_msk': {'start': '09:00:00', 'end': '21:00:00'},
        'ticket_queue': 'TPD',
        'responsible_for_task': 'karachevda',
        'duty_group_id': 'taxidutyrtcsupport',
    },
    CLOWNDUCTOR_MONRUN_LONG_RUNNING_JOBS_SETTINGS={
        'common': {'age_levels': {'crit': 1, 'warn': 1}},
        'jobs': [],
        'ignored_jobs': [],
    },
)


INIT_TIME = datetime.datetime(year=2022, month=1, day=10, hour=12, minute=5)
START_TIME_MARK = pytest.mark.now(str(INIT_TIME))
END_TIME_MARK = pytest.mark.now(str(INIT_TIME.replace(hour=20, minute=5)))


@pytest.fixture(name='get_duty_persons')
def _get_duty_persons(cron_context):
    async def _wrapper():
        async with postgres.get_connection(cron_context) as conn:
            records = await conn.fetch('select * from duty.persons_on_duty')
            return [dict(row) for row in records]

    return _wrapper


@pytest.fixture(name='mock_st_get_ticket_by_unique_id')
def _mock_st_get_ticket_by_unique_id(mockserver, response_mock):
    @mockserver.json_handler('/startrek/issues/_findByUnique')
    def _get_ticket_by_unique_id(request):
        return mockserver.make_response(status=404)

    return _get_ticket_by_unique_id


@pytest.fixture(name='mock_st_create_ticket')
def _mock_st_create_ticket(mockserver):
    @mockserver.json_handler('/startrek/issues')
    def _create_ticket(request):
        return {'key': f'{request.json["queue"]["key"]}-1'}

    return _create_ticket


@pytest.fixture(name='duty_service_mock')
def _duty_service_mock(mockserver):
    @mockserver.json_handler('/duty-api/api/duty_group')
    def _duty_group_handler(request):
        return {
            'result': {
                'data': {
                    'currentEvent': {'user': 'karachevda'},
                    'suggestedEvents': [{'user': 'test_user'}],
                    'staffGroups': ['test_group'],
                },
                'ok': True,
            },
        }

    return _duty_group_handler


@pytest.fixture(name='mock_st_myself', autouse=True)
def _mock_st_myself(mockserver):
    @mockserver.json_handler('/startrek/myself')
    def _myself(request):
        return {}

    return _myself


@pytest.fixture(name='mock_st_comments')
def _mock_st_comments(mockserver):
    @mockserver.json_handler('/startrek/issues/TPD-1/comments')
    def _comments(request):
        if request.method == 'POST':
            assert request.json.get('text') in EXPECTED_COMMENTS
        return {}

    return _comments


@pytest.fixture(name='mock_st_get_ticket', autouse=True)
def _mock_st_get_ticket(mockserver):
    @mockserver.json_handler('/startrek/issues/TPD-1')
    def _get_ticket(request):
        return {}

    return _get_ticket


@pytest.fixture(name='mock_close_ticket', autouse=True)
def _mock_close_ticket(mockserver):
    @mockserver.json_handler(
        '/startrek/issues/TPD-1/transitions/close/_execute',
    )
    def _close_ticket(request):
        return {}

    return _close_ticket


@START_TIME_MARK
@CONFIG_MARK
@pytest.mark.pgsql('clownductor', files=[])
@pytest.mark.translations(clownductor=TRANSLATIONS)
async def test_on_duty_persons(
        get_duty_persons,
        mockserver,
        duty_service_mock,
        mock_st_get_ticket_by_unique_id,
        mock_st_create_ticket,
        mock_st_comments,
):
    start_persons = await get_duty_persons()
    assert start_persons == []
    await run_cron.main(
        ['clownductor.crontasks.on_duty_persons_ticket_process', '-t', '0'],
    )
    assert duty_service_mock.times_called == 1
    assert mock_st_get_ticket_by_unique_id.times_called == 1
    assert mock_st_create_ticket.times_called == 1
    assert mock_st_comments.times_called == 2
    end_persons = await get_duty_persons()
    assert len(end_persons) == 1
    person = end_persons[0]
    assert person.pop('id')
    assert person == {
        'duty_day': datetime.date(2022, 1, 10),
        'duty_status': 'in_progress',
        'login': 'karachevda',
        'ticket': 'TPD-1',
    }


@START_TIME_MARK
@CONFIG_MARK
@pytest.mark.pgsql('clownductor', files=['long_running_jobs.sql'])
@pytest.mark.translations(clownductor=TRANSLATIONS)
@pytest.mark.features_on('enable_long_running_jobs_comment')
async def test_starting_duty_comments(
        get_duty_persons,
        mockserver,
        duty_service_mock,
        mock_st_get_ticket_by_unique_id,
        mock_st_create_ticket,
        mock_st_comments,
):
    start_persons = await get_duty_persons()
    assert start_persons == []
    await run_cron.main(
        ['clownductor.crontasks.on_duty_persons_ticket_process', '-t', '0'],
    )
    assert mock_st_comments.times_called == 4


@END_TIME_MARK
@CONFIG_MARK
@pytest.mark.pgsql(
    'clownductor', files=['has_in_progress.sql', 'long_running_jobs.sql'],
)
@pytest.mark.translations(clownductor=TRANSLATIONS)
@pytest.mark.features_on('enable_long_running_jobs_comment')
async def test_end_duty_comments(
        get_duty_persons,
        mockserver,
        duty_service_mock,
        mock_st_get_ticket_by_unique_id,
        mock_st_create_ticket,
        mock_st_comments,
):
    await run_cron.main(
        ['clownductor.crontasks.on_duty_persons_ticket_process', '-t', '0'],
    )
    assert mock_st_comments.times_called == 2


@START_TIME_MARK
@CONFIG_MARK
@pytest.mark.pgsql('clownductor', files=['has_in_progress.sql'])
@pytest.mark.translations(clownductor=TRANSLATIONS)
async def test_has_in_progress(get_duty_persons, mockserver, mock_st_comments):
    start_persons = await get_duty_persons()
    assert len(start_persons) == 3
    await run_cron.main(
        ['clownductor.crontasks.on_duty_persons_ticket_process', '-t', '0'],
    )
    assert mock_st_comments.times_called == 2
    end_persons = await get_duty_persons()
    assert end_persons == start_persons
