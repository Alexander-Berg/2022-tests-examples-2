# pylint: disable=too-many-lines
import pytest

from clownductor.internal.tasks import cubes
from clownductor.internal.tasks.cubes import cubes_approve
from clownductor.internal.utils import postgres
from clownductor.internal.utils.links import wiki as wiki_links


RELEASE_ID = 'release:456'
APPROVE_KEY_PHRASE = 'OK for {}'.format(RELEASE_ID)
CLOSE_TICKET_PHRASE = 'CLOSE TICKET for {}'.format(RELEASE_ID)
BORDER_COMMENT = 'some comment here'
ST_LOGIN = 'robot-taxi-clown'
VALID_MANAGERS = ['some-manager1', 'some-manager2']
VALID_DEVELOPERS = ['some-developer1', 'some-developer2']
INVALID_MANAGER = 'invalid-manager'
INVALID_DEVELOPER = 'invalid-developer'

OUTDATED_MANAGER_OK_FEEDBACK = (
    f'Manager approval is out of date for release {RELEASE_ID}. '
    'Should set ticket any status and return it '
    'to readyForRelease again.'
)

INVALID_MANAGER_OK_FEEDBACK = (
    f'кто:{INVALID_MANAGER} cannot approve release as manager. '
    'Right manager should set ticket any status and return it '
    'to readyForRelease.\n'
    'Ask one of the next people to approve: кто:some-manager1'
)
INVALID_DEVELOPER_OK_FEEDBACK = (
    f'кто:{INVALID_DEVELOPER} cannot approve release as developer.\n'
    'Ask one of the next people to approve: '
    'кто:d1mbas, кто:isharov, кто:oxcd8o, кто:some-developer1'
)

INVALID_USER_TICKET_CLOSE_FEEDBACK = (
    f'кто:{INVALID_DEVELOPER} cannot approve the closure of this ticket.\n'
    'It should be either the assignee кто:axolm or one of these people:\n'
    'кто:d1mbas, кто:effeman, кто:isharov, кто:oxcd8o, кто:some-developer1'
)

_NANNY_BASE_URL = 'https://nanny.yandex-team.ru/ui/#/services/catalog/'

_GRAFANA_URL = (
    'https://grafana.yandex-team.ru/'
    'd/someuuid/nanny_taxi_cool_service_stable'
)

_PRE_GRAFANA_URL = (
    'https://grafana.yandex-team.ru/'
    'd/someuuid/nanny_taxi_cool_service_stable?'
    'var-dorblu_group_cool_service='
    'dorblu_rtc_taxi_cool_service_pre_stable'
)

_GOLOVAN_BASE_URL = 'https://yasm.yandex-team.ru/panel/robot-taxi-clown.nanny_'

_KIBANA_URL = (
    (
        'https://kibana.taxi.yandex-team.ru/app/kibana#/discover?'
        '_g=(filters:!())&_a=(columns:!(_source),filters:!('
        '(\'$state\':(store:appState),'
        'meta:(alias:!n,disabled:!f,'
        'index:f8e70880-c75c-11e9-8a12-ddb2ef5a51ea,'
        'key:ngroups,negate:!f,'
        'params:!(taxi_cool_service_stable),type:phrases,'
        'value:\'taxi_cool_service_stable\'),'
        'query:(bool:(minimum_should_match:1,should:!(('
        'match_phrase:(ngroups:taxi_cool_service_stable)))))),'
        '(\'$state\':(store:appState),meta:(alias:!n,disabled:!f,'
        'index:f8e70880-c75c-11e9-8a12-ddb2ef5a51ea,key:level,negate:!f,'
        'params:!(ERROR,WARNING),type:phrases,value:\'ERROR,+WARNING\'),'
        'query:(bool:(minimum_should_match:1,should:!'
        '((match_phrase:(level:ERROR)),(match_phrase:(level:WARNING))))))),'
        'index:f8e70880-c75c-11e9-8a12-ddb2ef5a51ea,interval:auto,'
        'query:(language:kuery,query:\'\'),sort:!(\'@timestamp\',desc))'
    )
    .replace('(', '%28')
    .replace(')', '%29')
)
_KIBANA_SHORTCUT_URL_ID = '1c8ea15ae948b7936e3aa287f1739cd3'
_KIBANA_SHORTCUT_URL = (
    f'https://kibana.taxi.yandex-team.ru/goto/{_KIBANA_SHORTCUT_URL_ID}'
)

_RTC_HELP_LINK = wiki_links.RTC_HELP_LINK

STARTED_DEPLOY_MESSAGE_SIMPLE = (
    f"""
Deployment of the release with internal id {RELEASE_ID} started.
""".strip()
)
STARTED_DEPLOY_MESSAGE_VERBOSE = (
    f"""
Deployment of the release with internal id {RELEASE_ID} started.
To look for the release follow links:
* (({_NANNY_BASE_URL}taxi_cool_service_stable/ deploy status))
* (({_GRAFANA_URL} grafana graphics))
* (({_GOLOVAN_BASE_URL}taxi_cool_service_stable golovan graphics))
* (({_KIBANA_SHORTCUT_URL} short link logs))
* (({_KIBANA_URL} service logs))

Typical problems are described in (({_RTC_HELP_LINK} F.A.Q.))
""".strip()
)
STARTED_DEPLOY_MESSAGE_VERBOSE_NO_GRAFANA = (
    f"""
Deployment of the release with internal id {RELEASE_ID} started.
To look for the release follow links:
* (({_NANNY_BASE_URL}taxi_cool_service_stable/ deploy status))
* (({_GOLOVAN_BASE_URL}taxi_cool_service_stable golovan graphics))
* (({_KIBANA_URL} service logs))

Typical problems are described in (({_RTC_HELP_LINK} F.A.Q.))

""".strip()
)
PRE_STARTED_DEPLOY_MESSAGE_SIMPLE = (
    f"""
Deployment of the release in pre with internal id {RELEASE_ID} started.
""".strip()
)
PRE_STARTED_DEPLOY_MESSAGE_VERBOSE = (
    f"""
Deployment of the release in pre with internal id {RELEASE_ID} started.
To look for the release follow links:
* (({_NANNY_BASE_URL}taxi_cool_service_pre_stable/ deploy status))
* (({_PRE_GRAFANA_URL} grafana graphics))
* (({_GOLOVAN_BASE_URL}taxi_cool_service_stable golovan graphics))
* (({_KIBANA_SHORTCUT_URL} short link logs))
* (({
_KIBANA_URL.replace('taxi_cool_service_stable', 'taxi_cool_service_pre_stable')
} service logs))

Typical problems are described in (({_RTC_HELP_LINK} F.A.Q.))
""".strip()
)

DEPLOY_INSTRUCTION_LINK_FALLBACK = (
    'https://wiki.yandex-team.ru/taxi/backend/basichowto/deploy/'
)
DEPLOY_INSTRUCTION_LINK_TEST_PROJ = (
    'https://wiki.yandex-team.ru/deploy-instruction-test'
)

DEPLOY_INSTRUCTION_LINKS_MOCK = {
    '__default__': {'link': DEPLOY_INSTRUCTION_LINK_FALLBACK},
    'test_project': {'link': DEPLOY_INSTRUCTION_LINK_TEST_PROJ},
}

OUTDATED_CLOSURE_APPROVAL_FEEDBACK = (
    f'Closure approval is out of date for release {RELEASE_ID}.\n'
    'Approver should set ticket to any status and return it to released again.'
)

INVALID_CLOSURE_APPROVAL_FEEDBACK = (
    f'кто:{INVALID_MANAGER} cannot approve the closure of this ticket.\n'
    'It should be either the assignee кто:axolm or one of these people:\n'
    'кто:d1mbas, кто:effeman, кто:isharov, кто:oxcd8o, кто:some-manager1'
)

DEPLOYED_MSG = 'OLOLO DEPLOYED'


def _clowny_roles_usage_switcher(feature: str):
    return pytest.mark.parametrize(
        '',
        [
            pytest.param(
                id=f'use clowny-roles for feature {feature}',
                marks=[pytest.mark.roles_features_on(feature)],
            ),
            pytest.param(
                id=f'do not use clowny-roles for feature {feature}',
                marks=[pytest.mark.roles_features_off(feature)],
            ),
        ],
    )


APPROVE_CHECK_SWITCHER = _clowny_roles_usage_switcher('approve_check')


def task_data(name, job_id=456):
    return {
        'id': 123,
        'job_id': job_id,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


def fake_st_response_issue(assignee):
    return {'assignee': {'id': assignee}}


def fake_st_response_comments(data):
    return [
        {
            'id': id(entry),
            'text': entry['text'],
            'createdBy': {'id': entry['login']},
            'createdAt': entry['time'],
        }
        for entry in data
    ]


def fake_st_response_history(data):
    return [
        {
            'fields': [{'to': {'key': entry['to']}}],
            'updatedBy': {'id': entry['login']},
            'updatedAt': entry['time'],
        }
        for entry in data
    ]


@pytest.mark.parametrize(
    'template, service_name, env, nda_status, expected',
    [
        pytest.param(
            cubes_approve.PRESTARTED_DEPLOY_TPL,
            'taxi_cool_service_pre_stable',
            'prestable',
            200,
            PRE_STARTED_DEPLOY_MESSAGE_VERBOSE,
            id='render_for_prestable-verbose_enabled',
            marks=pytest.mark.config(
                CLOWNDUCTOR_RELEASE_ST_COMMENT_SETTINGS={
                    'verbose_enabled': True,
                },
                CLOWNDUCTOR_FEATURES={'kibana_shortcut': True},
            ),
        ),
        pytest.param(
            cubes_approve.PRESTARTED_DEPLOY_TPL,
            'taxi_cool_service_pre_stable',
            'prestable',
            200,
            PRE_STARTED_DEPLOY_MESSAGE_SIMPLE,
            id='render_for_prestable-verbose_disabled',
            marks=pytest.mark.config(
                CLOWNDUCTOR_RELEASE_ST_COMMENT_SETTINGS={
                    'verbose_enabled': False,
                },
                CLOWNDUCTOR_FEATURES={'kibana_shortcut': True},
            ),
        ),
        pytest.param(
            cubes_approve.STARTED_DEPLOY_TPL,
            'taxi_cool_service_stable',
            'stable',
            200,
            STARTED_DEPLOY_MESSAGE_VERBOSE,
            id='render_for_stable-verbose_enabled',
            marks=pytest.mark.config(
                CLOWNDUCTOR_RELEASE_ST_COMMENT_SETTINGS={
                    'verbose_enabled': True,
                },
                CLOWNDUCTOR_FEATURES={'kibana_shortcut': True},
            ),
        ),
        pytest.param(
            cubes_approve.STARTED_DEPLOY_TPL,
            'taxi_cool_service_stable',
            'stable',
            400,
            STARTED_DEPLOY_MESSAGE_SIMPLE,
            id='render_for_stable-verbose_disabled',
            marks=pytest.mark.config(
                CLOWNDUCTOR_RELEASE_ST_COMMENT_SETTINGS={
                    'verbose_enabled': False,
                },
                CLOWNDUCTOR_FEATURES={'kibana_shortcut': False},
            ),
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
async def test_start_message_render(
        web_context,
        mockserver,
        template,
        service_name,
        nda_status,
        expected,
        env,
):
    @mockserver.handler('kibana/api/shorten_url', prefix=True)
    # pylint: disable=unused-variable
    async def get_short_link(request):
        return mockserver.make_response(
            json={'urlId': _KIBANA_SHORTCUT_URL_ID}, status=nda_status,
        )

    async with postgres.get_connection(web_context) as conn:
        result = await cubes_approve.render_started_deploy_msg(
            context=web_context,
            template=template,
            release_id=RELEASE_ID,
            service_name=service_name,
            env=env,
            conn=conn,
        )
    assert expected == result


@APPROVE_CHECK_SWITCHER
@pytest.mark.parametrize(
    'single_approve, service_id',
    [
        pytest.param(
            False,
            1,
            id='single approve feature globally disabled, '
            'service has it locally enabled',
            marks=[
                pytest.mark.features_off('startrek_release_single_approve'),
            ],
        ),
        pytest.param(
            True,
            1,
            id='single approve feature globally enabled, '
            'service has it locally enabled',
            marks=[pytest.mark.features_on('startrek_release_single_approve')],
        ),
        pytest.param(
            False,
            2,
            id='single approve feature globally disabled, '
            'service has it locally disabled',
            marks=[
                pytest.mark.features_off('startrek_release_single_approve'),
            ],
        ),
        pytest.param(
            False,
            2,
            id='single approve feature globally enabled, '
            'service has it locally disabled',
            marks=[pytest.mark.features_on('startrek_release_single_approve')],
        ),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_RELEASE_ST_COMMENT_SETTINGS={'verbose_enabled': True},
    CLOWNDUCTOR_FEATURES={'kibana_shortcut': True},
)
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
async def test_lite_generate_approve_id(
        single_approve, service_id, web_context, mockserver,
):
    @mockserver.handler('kibana/api/shorten_url', prefix=True)
    # pylint: disable=unused-variable
    async def get_short_link(request):
        return mockserver.make_response(
            json={'urlId': _KIBANA_SHORTCUT_URL_ID}, status=200,
        )

    cube = cubes.CUBES['ApproveCubeLiteGenerateApproveId'](
        web_context,
        task_data('ApproveCubeLiteGenerateApproveId'),
        {'name': 'taxi_cool_service_stable', 'service_id': service_id},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload'].get('release_id') == RELEASE_ID
    assert RELEASE_ID in cube.data['payload'].get('release_key_phrase')
    assert RELEASE_ID in cube.data['payload'].get('border_comment')
    assert (
        cube.data['payload']['started_deploy_msg']
        == STARTED_DEPLOY_MESSAGE_VERBOSE
    )
    assert cube.data['payload']['single_approve'] is single_approve


@pytest.mark.parametrize(
    'service_id, border_comment, summon_managers',
    [
        pytest.param(
            1,
            'Responsible managers: кто:azhuchkov, кто:vokhcuhza',
            True,
            id='summon managers',
            marks=[pytest.mark.features_on('startrek_release_single_approve')],
        ),
        pytest.param(
            1,
            'Responsible managers: кто:azhuchkov, кто:vokhcuhza',
            False,
            id='do not summon managers',
            marks=[
                pytest.mark.features_off('startrek_release_single_approve'),
            ],
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
async def test_disable_summon_managers(
        service_id, border_comment, summon_managers, web_context, mockserver,
):
    cube = cubes.CUBES['ApproveCubeLiteGenerateApproveId'](
        web_context,
        task_data('ApproveCubeLiteGenerateApproveId'),
        {
            'name': 'taxi_cool_service_stable',
            'service_id': service_id,
            'responsible_managers': ['azhuchkov', 'vokhcuhza'],
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    if summon_managers:
        assert border_comment in cube.data['payload']['border_comment']
    else:
        assert border_comment not in cube.data['payload']['border_comment']


@pytest.mark.parametrize(
    'ticket, ticket_data, expected_summoned_assignee',
    [
        pytest.param(
            'TAXIADMIN-1000',
            {'assignee': {'id': 'skolibaba'}},
            'skolibaba',
            id='success',
        ),
        pytest.param(None, None, None, id='optional_ticket_param'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
async def test_lite_generate_preapprove_id_receives_ticket_assignee(
        web_context, patch, ticket, ticket_data, expected_summoned_assignee,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return ticket_data

    cube = cubes.CUBES['ApproveCubeLiteGeneratePreApproveId'](
        web_context,
        task_data('ApproveCubeLiteGeneratePreApproveId'),
        {
            'name': 'taxi_cool_service_stable',
            'prestable_name': 'super_prestable',
            'ticket': ticket,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert (
        cube.data['payload']['summoned_assignee'] == expected_summoned_assignee
    )
    assert len(get_ticket.calls) == (1 if ticket else 0)


@pytest.mark.parametrize(
    'cube_name',
    [
        'ApproveCubeLiteGenerateApproveId',
        'ApproveCubeLiteGeneratePreApproveId',
    ],
)
@pytest.mark.parametrize(
    'expected_link',
    [
        pytest.param(
            DEPLOY_INSTRUCTION_LINK_TEST_PROJ,
            id='link-for-project-exists',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_DEPLOY_INSTRUCTION_LINKS=(
                        DEPLOY_INSTRUCTION_LINKS_MOCK
                    ),
                ),
            ],
        ),
        pytest.param(DEPLOY_INSTRUCTION_LINK_FALLBACK, id='fallback-link'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
async def test_get_deploy_instruction_link_in_border_comment(
        web_context, cube_name, expected_link,
):
    cube = cubes.CUBES[cube_name](
        web_context,
        task_data(cube_name),
        {
            'name': 'taxi_cool_service_stable',
            'prestable_name': 'super_prestable',
            'service_id': 1,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert expected_link in cube.data['payload']['border_comment']


@pytest.mark.parametrize(
    'expected_link',
    [
        pytest.param(
            DEPLOY_INSTRUCTION_LINK_TEST_PROJ,
            id='link-for-project-exists',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_DEPLOY_INSTRUCTION_LINKS=(
                        DEPLOY_INSTRUCTION_LINKS_MOCK
                    ),
                ),
            ],
        ),
        pytest.param(DEPLOY_INSTRUCTION_LINK_FALLBACK, id='fallback-link'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
async def test_get_deploy_instruction_link_in_managers_ok_received_msg(
        web_context, expected_link,
):
    cube = cubes.CUBES['ApproveCubeLiteGenerateApproveId'](
        web_context,
        task_data('ApproveCubeLiteGenerateApproveId'),
        {'name': 'taxi_cool_service_stable', 'service_id': 1},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert expected_link in cube.data['payload']['managers_ok_received_msg']


@pytest.mark.parametrize(
    'comments, should_create_comment',
    [
        ([], True),  # No comments - create ticket
        (  # Right comment, wrong author - create ticket
            [
                {
                    'login': 'oxcd8o',
                    'time': '2100-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
            ],
            True,
        ),
        (  # Right comment, right author - don't create ticket
            [
                {
                    'login': ST_LOGIN,
                    'time': '2100-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
            ],
            False,
        ),
    ],
)
async def test_lite_ensure_comment(
        web_context, patch, comments, should_create_comment,
):  # pylint: disable=W0612
    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def get_myself(*args, **kwargs):
        return {'login': ST_LOGIN}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return fake_st_response_comments(comments)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        pass

    cube = cubes.CUBES['ApproveCubeLiteEnsureComment'](
        web_context,
        task_data('ApproveCubeLiteEnsureComment'),
        {'st_key': 'TAXIADMIN-10000', 'comment': BORDER_COMMENT},
        [],
        None,
    )

    await cube.update()

    assert bool(create_comment.call) is should_create_comment
    assert not create_comment.call

    assert cube.success


@pytest.mark.parametrize(
    'cube_name',
    ['ApproveCubeLiteEnsureComment', 'ApproveCubeOptionalLiteEnsureComment'],
)
@pytest.mark.parametrize(
    'summonees, summoned_assignee, expected_summonees',
    [
        pytest.param(None, None, None, id='summones_none_and_assignee_none'),
        pytest.param([], None, None, id='summones_empty_and_assignee_none'),
        pytest.param(None, '', None, id='summones_none_and_assignee_empty'),
        pytest.param([], '', None, id='summones_empty_and_assignee_empty'),
        pytest.param(
            ['skolibaba'],
            None,
            ['skolibaba'],
            id='summonees_exists_and_assignee_none',
        ),
        pytest.param(
            None,
            'skolibaba',
            ['skolibaba'],
            id='summonees_none_and_assignee_exists',
        ),
        pytest.param(
            ['skolibaba'],
            'skolibaba',
            ['skolibaba'],
            id='summonees_and_assignee_duplicates',
        ),
        pytest.param(
            ['skolibaba'],
            'spolischouck',
            ['skolibaba', 'spolischouck'],
            id='summonees_and_assignee_no_duplicates',
        ),
    ],
)
async def test_lite_ensure_comment_with_summonees(
        web_context,
        patch,
        cube_name,
        summonees,
        summoned_assignee,
        expected_summonees,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def get_myself(*args, **kwargs):
        return {'login': ST_LOGIN}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        comments = []
        return fake_st_response_comments(comments)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert expected_summonees == kwargs.pop('summonees')

    cube = cubes.CUBES[cube_name](
        web_context,
        task_data(cube_name),
        {
            'st_key': 'TAXIADMIN-10000',
            'comment': BORDER_COMMENT,
            'skip': False,
            'summonees': summonees,
            'summoned_assignee': summoned_assignee,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert len(get_myself.calls) == 1
    assert len(get_comments.calls) == 1

    comment_call = create_comment.call
    assert comment_call['kwargs']['summonees'] == expected_summonees
    assert not create_comment.call


@APPROVE_CHECK_SWITCHER
@pytest.mark.parametrize(
    'assignee, comments, history, feedback_text, success',
    [
        pytest.param(
            'axolm',
            [],
            [],
            '',
            False,
            id='No comments, no history - no success',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2000-06-28T15:27:25.361+0000',
                    'to': 'readyForRelease',
                },
            ],
            OUTDATED_MANAGER_OK_FEEDBACK,
            False,
            id='Too old manager ok',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': ST_LOGIN,
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': OUTDATED_MANAGER_OK_FEEDBACK,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2000-06-28T15:27:25.361+0000',
                    'to': 'readyForRelease',
                },
            ],
            '',
            False,
            id='Too old manager but comment was created earlier',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
            ],
            [
                {
                    'login': 'invalid-manager',
                    'time': '2001-06-28T15:27:25.361+0000',
                    'to': 'readyForRelease',
                },
            ],
            INVALID_MANAGER_OK_FEEDBACK,
            False,
            id='OK not from manager',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': ST_LOGIN,
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': INVALID_MANAGER_OK_FEEDBACK,
                },
            ],
            [
                {
                    'login': 'invalid-manager',
                    'time': '2001-06-28T15:27:25.361+0000',
                    'to': 'readyForRelease',
                },
            ],
            '',
            False,
            id='OK not from manager but comment was created earlier',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2001-06-28T15:27:25.361+0000',
                    'to': 'open',
                },
            ],
            '',
            False,
            id='Not readyForRelease',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2001-06-28T15:27:25.361+0000',
                    'to': 'readyForRelease',
                },
            ],
            '',
            True,
            id='Good one',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2000-06-28T15:27:25.361+0000',
                    'to': 'readyForRelease',
                },
                {
                    'login': INVALID_MANAGER,
                    'time': '2003-06-28T15:27:25.361+0000',
                    'to': 'readyForRelease',
                },
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2005-06-28T15:27:25.361+0000',
                    'to': 'readyForRelease',
                },
            ],
            '',
            True,
            id='Good one with resolved problems',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_approve.sql'])
async def test_lite_wait_for_managers_approve(
        web_context,
        patch,
        add_grant,
        clowny_roles_grants,
        assignee,
        comments,
        history,
        feedback_text,
        success,
):  # pylint: disable=W0612
    await add_grant('some-manager1', 'deploy_approve_manager', project_id=1)
    clowny_roles_grants.add_manager_approver(
        'some-manager1', {'id': 'test_project', 'type': 'project'},
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def get_myself(*args, **kwargs):
        return {'login': ST_LOGIN}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return fake_st_response_comments(comments)

    @patch('taxi.clients.startrack.StartrackAPIClient.get_field_history')
    async def get_field_history(*args, **kwargs):
        return fake_st_response_history(history)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(st_key, text):
        assert feedback_text in text

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['ApproveCubeLiteWaitForManagersApprove'](
            web_context,
            task_data('ApproveCubeLiteWaitForManagersApprove'),
            {
                'st_key': 'TAXIADMIN-10000',
                'release_id': RELEASE_ID,
                'managers': VALID_MANAGERS,
                'border_comment': BORDER_COMMENT,
            },
            [],
            conn,
        )

        await cube.update()

    assert cube.success == success

    comment_call = create_comment.call
    if comment_call:
        assert comment_call['text'] == feedback_text
    assert not create_comment.call

    if cube.success:
        assert cube.data['payload'].get('approved', '') == RELEASE_ID


def case(
        login,
        comments,
        feedback_text,
        success,
        service_id=1,
        extra_developers=None,
        missing_grants=False,
        *,
        id: str,  # pylint: disable=invalid-name, redefined-builtin
        marks=None,
):
    return pytest.param(
        login,
        comments,
        feedback_text,
        success,
        service_id,
        extra_developers or [],
        missing_grants,
        id=id,
        marks=marks or [],
    )


@APPROVE_CHECK_SWITCHER
@pytest.mark.parametrize(
    (
        'assignee,'
        'comments,'
        'feedback_text,'
        'success,'
        'service_id,'
        'extra_developers,'
        'missing_grants'
    ),
    [
        case(
            'axolm', [], '', False, id='No comments, no history - no success',
        ),
        case(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            INVALID_DEVELOPER_OK_FEEDBACK,
            False,
            id='OK not from developer',
        ),
        case(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
                {
                    'login': ST_LOGIN,
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': INVALID_DEVELOPER_OK_FEEDBACK,
                },
            ],
            '',
            False,
            id='OK not from developer but comment was created earlier',
        ),
        case(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': VALID_DEVELOPERS[0],
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            '',
            True,
            id='Good one',
        ),
        case(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
                {
                    'login': VALID_DEVELOPERS[0],
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                f'кто:{INVALID_DEVELOPER} cannot approve '
                'release as developer.\n'
                'Ask one of the next people to approve: '
                'кто:d1mbas, кто:isharov, кто:oxcd8o, кто:some-developer1'
            ),
            True,
            id='Good one with resolved problems',
        ),
        case(
            'd1mbas',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            '',
            True,
            id='Authorized role via idm check',
        ),
        case(
            'd1mbas',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                'кто:d1mbas cannot approve release as developer.\n'
                'Ask one of the next people to approve: '
                'кто:isharov, кто:oxcd8o, кто:some-developer1\n'
                'This service has no own approvers. '
                'It may cause some unexpected consequences.\n'
                'Please, request role in IDM\n'
                'Clownductor -> project TAXI -> service role -> '
                'second_service_exist -> deploy approve by developer'
            ),
            False,
            2,
            id='Non authorized by idm check (feature forced off)',
            marks=[pytest.mark.roles_features_off('approve_check')],
        ),
        case(
            'nevladov',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'nevladov',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            '',
            True,
            3,
            id='Authorized by super role',
            marks=[pytest.mark.roles_features_off('approve_check')],
        ),
        case(
            'd1mbas',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                'кто:d1mbas cannot approve release as developer.\n'
                'Service has no approvers at all\n'
                'No one can approve its release.\n'
                'Please, request role in IDM\n'
                'Clownductor -> project TAXI -> service role -> '
                'second_service_exist -> deploy approve by developer'
            ),
            False,
            2,
            missing_grants=True,
            id='with empty roles list (feature forced off)',
            marks=[
                pytest.mark.pgsql(
                    'clownductor', files=['remove_all_roles.sql'],
                ),
                pytest.mark.roles_features_off('approve_check'),
            ],
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
async def test_lite_wait_for_developers_approve(
        web_context,
        patch,
        add_grant,
        clowny_roles_grants,
        assignee,
        comments,
        feedback_text,
        success,
        service_id,
        extra_developers,
        missing_grants,
):  # pylint: disable=W0612
    if not missing_grants:
        await add_grant(
            'some-developer1', 'deploy_approve_programmer', project_id=1,
        )
        clowny_roles_grants.add_manager_approver(
            'effeman', {'id': 'abc_service_exist', 'type': 'service'},
        )
        clowny_roles_grants.add_dev_approver(
            'd1mbas', {'id': 'abc_service_exist', 'type': 'service'},
        )
        clowny_roles_grants.add_dev_approver(
            'isharov', {'id': 'taxi', 'type': 'project'},
        )
        clowny_roles_grants.add_dev_approver(
            'oxcd8o', {'id': 'taxi', 'type': 'project'},
        )
        clowny_roles_grants.add_dev_approver(
            'some-developer1', {'id': 'taxi', 'type': 'project'},
        )

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def get_myself(*args, **kwargs):
        return {'login': ST_LOGIN}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return fake_st_response_comments(comments)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(st_key, text):
        assert feedback_text in text

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['ApproveCubeLiteWaitForDevelopersApprove'](
            web_context,
            task_data('ApproveCubeLiteWaitForDevelopersApprove'),
            {
                'st_key': 'TAXIADMIN-10000',
                'release_id': RELEASE_ID,
                'developers': VALID_DEVELOPERS + extra_developers,
                'release_key_phrase': APPROVE_KEY_PHRASE,
                'skip': False,
                'service_id': service_id,
            },
            [],
            conn,
        )

        await cube.update()

    assert cube.success == success

    comment_call = create_comment.call
    if comment_call:
        assert comment_call['text'] == feedback_text
    assert not create_comment.call

    if cube.success:
        assert cube.data['payload'].get('approved', '') == RELEASE_ID


@pytest.mark.parametrize(
    'service_id, expected_approving_managers, expected_summonees',
    [
        pytest.param(1, ['some-manager'], []),
        pytest.param(2, ['regular-manager'], ['regular-manager']),
        pytest.param(
            2,
            ['regular-manager'],
            [],
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'disable_ticket_summon_managers': True},
            ),
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
async def test_get_approvers(
        web_context,
        patch,
        service_id,
        expected_approving_managers,
        expected_summonees,
):
    @patch(
        'clownductor.generated.service.conductor_api.'
        'plugin.ConductorClient.get_approvers',
    )
    async def get_approvers(*args, **kwargs):  # pylint: disable=W0612
        if service_id == 2:
            return ['regular-manager']
        return ['some-manager']

    cube = cubes.CUBES['ApproveCubeGetApprovers'](
        web_context,
        task_data('ApproveCubeGetApprovers'),
        {'service_id': service_id},
        [],
        None,
    )

    await cube.update()

    assert cube.success

    assert (
        cube.data['payload'].get('approving_managers', '')
        == expected_approving_managers
    )
    assert cube.data['payload'].get('summonees', '') == expected_summonees


@pytest.mark.features_on('render_instruction')
@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
async def test_generate_instructions(web_context, patch):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        assert args[0]
        return {'assignee': {'id': 'skolibaba'}}

    cube = cubes.CUBES['ApproveGenerateInstruction'](
        web_context,
        task_data('ApproveCubeGetApprovers', 1),
        {
            'service_id': 1,
            'name': 'taxi_service_exist_pre_stable',
            'ticket': 'test_ticket',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success

    info = cube.data['payload'].get('instruction_after_deploy', '')
    info = info.split('\n')[1]

    assert info == (
        '1. ((https://grafana.yandex-team.ru/d/someuuid/'
        'nanny_taxi_service_exist_stable?'
        'var-dorblu_group_service_exist='
        'dorblu_rtc_taxi_service_exist_pre_stable Grafana graphics))'
    )
    assert len(get_ticket.calls) == 1


@APPROVE_CHECK_SWITCHER
@pytest.mark.parametrize(
    'assignee, ticket_status, comments, feedback_text, success, service_id',
    [
        pytest.param(
            'axolm',
            'open',
            [],
            '',
            False,
            1,
            id='No comments, no history - no success',
            marks=[],
        ),
        pytest.param(
            'axolm',
            'open',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
            ],
            INVALID_USER_TICKET_CLOSE_FEEDBACK,
            False,
            1,
            id='TICKET CLOSE approved by a random',
            marks=[],
        ),
        pytest.param(
            'axolm',
            'open',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
                {
                    'login': ST_LOGIN,
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': INVALID_DEVELOPER_OK_FEEDBACK,
                },
            ],
            '',
            False,
            1,
            id=(
                'TICKET CLOSE approved by a random '
                'and we have already answered'
            ),
            marks=[],
        ),
        pytest.param(
            'axolm',
            'open',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': VALID_DEVELOPERS[0],
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
            ],
            '',
            True,
            1,
            id='Correct CLOSE TICKET approve',
            marks=[],
        ),
        pytest.param(
            'axolm',
            'open',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
                {
                    'login': VALID_DEVELOPERS[0],
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
            ],
            INVALID_USER_TICKET_CLOSE_FEEDBACK,
            True,
            1,
            id='Good one with resolved problems',
            marks=[],
        ),
        pytest.param(
            'd1mbas',
            'open',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
            ],
            '',
            True,
            1,
            id='Authorized role via idm check',
        ),
        pytest.param(
            'd1mbas',
            'open',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
            ],
            '',
            True,
            2,
            id='Assignee closes own ticket',
        ),
        pytest.param(
            'axolm',
            'open',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
            ],
            (
                'кто:d1mbas cannot approve the closure of this ticket.\n'
                'It should be either the assignee '
                'кто:axolm or one of these people:\n'
                'кто:isharov, кто:oxcd8o, кто:some-developer1\n'
                'This service has no own approvers. '
                'It may cause some unexpected consequences.\n'
                'Please, request role in IDM\n'
                'Clownductor -> project TAXI -> service role '
                '-> second_service_exist -> deploy approve by developer'
            ),
            False,
            2,
            id='Non authorized by idm check (feature forced off)',
            marks=[pytest.mark.roles_features_off('approve_check')],
        ),
        pytest.param(
            'nevladov',
            'open',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'nevladov',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': CLOSE_TICKET_PHRASE,
                },
            ],
            '',
            True,
            3,
            id='Authorized by super role',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
@pytest.mark.features_on('startrek_close_approval')
async def test_expect_ticket_close_approve(
        web_context,
        patch,
        add_grant,
        clowny_roles_grants,
        assignee,
        ticket_status,
        comments,
        feedback_text,
        success,
        service_id,
):
    clowny_roles_grants.add_manager_approver(
        'effeman', {'id': 'abc_service_exist', 'type': 'service'},
    )
    clowny_roles_grants.add_dev_approver(
        'd1mbas', {'id': 'abc_service_exist', 'type': 'service'},
    )
    clowny_roles_grants.add_dev_approver(
        'isharov', {'id': 'taxi', 'type': 'project'},
    )
    clowny_roles_grants.add_dev_approver(
        'oxcd8o', {'id': 'taxi', 'type': 'project'},
    )
    await add_grant(
        'some-developer1', 'deploy_approve_programmer', project_id=1,
    )
    clowny_roles_grants.add_dev_approver(
        'some-developer1', {'id': 'taxi', 'type': 'project'},
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return fake_st_response_comments(comments)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(st_key, text):
        assert feedback_text in text

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself(*args, **kwargs):
        return {'login': ST_LOGIN}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(*args, **kwargs):
        return {'status': {'key': ticket_status}}

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['ApproveCubeWaitForClosureApproval'](
            web_context,
            task_data('ApproveCubeWaitForClosureApproval'),
            {
                'st_key': 'TAXIADMIN-10000',
                'release_id': RELEASE_ID,
                'managers': VALID_MANAGERS,
                'developers': VALID_DEVELOPERS,
                'summoned_assignee': assignee,
                'close_ticket_phrase': CLOSE_TICKET_PHRASE,
                'finished_deploy_msg': BORDER_COMMENT,
                'service_id': service_id,
            },
            [],
            conn,
        )

        await cube.update()
    create_comment_call = create_comment.call
    if feedback_text:
        assert create_comment_call['text'] == feedback_text
    else:
        assert not create_comment_call
    assert not create_comment.call

    assert cube.success == success

    if cube.success:
        assert cube.data['payload'] == {'skip': False}


@APPROVE_CHECK_SWITCHER
@pytest.mark.parametrize(
    'assignee, comments, history, feedback_text, success, ticket_status',
    [
        pytest.param(
            'axolm',
            [],
            [],
            '',
            False,
            'released',
            id='No comments, no history - no success',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': DEPLOYED_MSG,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2000-06-28T15:27:25.361+0000',
                    'to': 'released',
                },
            ],
            OUTDATED_CLOSURE_APPROVAL_FEEDBACK,
            False,
            'released',
            id='Too old manager ok',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': DEPLOYED_MSG,
                },
                {
                    'login': ST_LOGIN,
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': OUTDATED_CLOSURE_APPROVAL_FEEDBACK,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2000-06-28T15:27:25.361+0000',
                    'to': 'released',
                },
            ],
            '',
            False,
            'released',
            id='Too old manager but comment was created earlier',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': DEPLOYED_MSG,
                },
            ],
            [
                {
                    'login': 'invalid-manager',
                    'time': '2001-06-28T15:27:25.361+0000',
                    'to': 'released',
                },
            ],
            INVALID_CLOSURE_APPROVAL_FEEDBACK,
            False,
            'released',
            id='OK not from manager',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': DEPLOYED_MSG,
                },
                {
                    'login': ST_LOGIN,
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': INVALID_CLOSURE_APPROVAL_FEEDBACK,
                },
            ],
            [
                {
                    'login': 'invalid-manager',
                    'time': '2001-06-28T15:27:25.361+0000',
                    'to': 'released',
                },
            ],
            '',
            False,
            'released',
            id='OK not from manager but comment was created earlier',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': DEPLOYED_MSG,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2001-06-28T15:27:25.361+0000',
                    'to': 'open',
                },
            ],
            '',
            False,
            'open',
            id='Not readyForRelease',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': DEPLOYED_MSG,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2001-06-28T15:27:25.361+0000',
                    'to': 'released',
                },
            ],
            '',
            True,
            'released',
            id='Good one',
        ),
        pytest.param(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': DEPLOYED_MSG,
                },
            ],
            [
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2000-06-28T15:27:25.361+0000',
                    'to': 'released',
                },
                {
                    'login': INVALID_MANAGER,
                    'time': '2003-06-28T15:27:25.361+0000',
                    'to': 'released',
                },
                {
                    'login': VALID_MANAGERS[0],
                    'time': '2005-06-28T15:27:25.361+0000',
                    'to': 'released',
                },
            ],
            '',
            True,
            'released',
            id='Good one with resolved problems',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
@pytest.mark.features_on('startrek_close_by_status')
@pytest.mark.features_off('startrek_close_approval')
@pytest.mark.config(
    CLOWNDUCTOR_RELEASE_TICKET_PROPERTIES={'TAXIADMIN': 'released'},
)
async def test_lite_wait_for_closure_status(
        web_context,
        patch,
        add_grant,
        clowny_roles_grants,
        assignee,
        comments,
        history,
        feedback_text,
        success,
        ticket_status,
):  # pylint: disable=W0612
    clowny_roles_grants.add_manager_approver(
        'effeman', {'id': 'abc_service_exist', 'type': 'service'},
    )
    clowny_roles_grants.add_dev_approver(
        'd1mbas', {'id': 'abc_service_exist', 'type': 'service'},
    )
    clowny_roles_grants.add_dev_approver(
        'isharov', {'id': 'taxi', 'type': 'project'},
    )
    clowny_roles_grants.add_dev_approver(
        'oxcd8o', {'id': 'taxi', 'type': 'project'},
    )
    await add_grant('some-manager1', 'deploy_approve_manager', project_id=1)
    clowny_roles_grants.add_manager_approver(
        'some-manager1', {'id': 'taxi', 'type': 'project'},
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.get_field_history')
    async def get_field_history(*args, **kwargs):
        return fake_st_response_history(history)

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return fake_st_response_comments(comments)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text, summonees=None):
        pass

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself(*args, **kwargs):
        return {'login': ST_LOGIN}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(*args, **kwargs):
        return {'status': {'key': ticket_status}}

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['ApproveCubeWaitForClosureStatus'](
            web_context,
            task_data('ApproveCubeWaitForClosureStatus'),
            {
                'st_key': 'TAXIADMIN-10000',
                'release_id': RELEASE_ID,
                'service_id': 1,
                'summoned_assignee': assignee,
                'managers': VALID_MANAGERS,
                'developers': VALID_DEVELOPERS,
                'finished_deploy_msg': DEPLOYED_MSG,
                'is_rollback': False,
            },
            [],
            conn,
        )

        await cube.update()

    comment_call = create_comment.call
    if feedback_text:
        assert comment_call.get('text') == feedback_text
    else:
        assert not comment_call
    assert not create_comment.call

    if success:
        assert cube.data['payload'].get('skip') is False
    else:
        assert not cube.finished
    assert cube.success == success


# test_single_approve
@APPROVE_CHECK_SWITCHER
@pytest.mark.parametrize(
    (
        'assignee,'
        'comments,'
        'feedback_text,'
        'success,'
        'service_id,'
        'extra_developers,'
        'missing_grants'
    ),
    [
        case(
            'isharov',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'isharov',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                'кто:isharov cannot approve this release '
                'because they are the assignee.\n'
                'Ask one of the next people to approve: '
                'кто:effeman, кто:d1mbas, кто:some-developer1, кто:oxcd8o'
            ),
            False,
            service_id=1,
            id='Authorized by valid developer - but self-ok is forbidden',
        ),
        case(
            'axolm', [], '', False, id='No comments, no history - no success',
        ),
        case(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                f'кто:{INVALID_DEVELOPER} cannot approve this release.\n'
                'Ask one of the next people to approve: '
                'кто:effeman, кто:d1mbas, кто:some-developer1, '
                'кто:isharov, кто:oxcd8o'
            ),
            False,
            id='OK not from developer',
        ),
        case(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
                {
                    'login': ST_LOGIN,
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': INVALID_DEVELOPER_OK_FEEDBACK,
                },
            ],
            '',
            False,
            id='OK not from developer but comment was created earlier',
        ),
        case(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': VALID_DEVELOPERS[0],
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            '',
            True,
            id='Good one',
        ),
        case(
            'axolm',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': INVALID_DEVELOPER,
                    'time': '2001-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
                {
                    'login': VALID_DEVELOPERS[0],
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                f'кто:{INVALID_DEVELOPER} cannot approve this release.\n'
                'Ask one of the next people to approve: '
                'кто:effeman, кто:d1mbas, кто:some-developer1, '
                'кто:isharov, кто:oxcd8o'
            ),
            True,
            id='Good one with resolved problems',
        ),
        case(
            'nevladov',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            '',
            True,
            id='Authorized role via idm check',
        ),
        case(
            'isharov',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                'кто:d1mbas cannot approve this release.\n'
                'Ask one of the next people to approve: '
                'кто:isharov, кто:oxcd8o\n'
                'This service has no own approvers. '
                'It may cause some unexpected consequences.\n'
                'Please, request role in IDM\n'
                'Clownductor -> project TAXI -> service role '
                '-> second_service_exist -> deploy approve by developer'
            ),
            False,
            2,
            id='Non authorized by idm check (feature forced off)',
            marks=[pytest.mark.roles_features_off('approve_check')],
        ),
        case(
            'nevladov',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'nevladov',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                'кто:nevladov cannot approve this release '
                'because they are the assignee.\n'
                'Ask one of the next people to approve: '
                'кто:isharov, кто:oxcd8o\n'
                'This service has no own approvers. '
                'It may cause some unexpected consequences.\n'
                'Please, request role in IDM\n'
                'Clownductor -> project TAXI -> service role '
                '-> one_more_service -> deploy approve by developer'
            ),
            False,
            3,
            id=(
                'Authorized by super role - but self-ok is forbidden '
                '(feature forced off)'
            ),
            marks=[pytest.mark.roles_features_off('approve_check')],
        ),
        case(
            'd1mbas',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'nevladov',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            '',
            True,
            3,
            id='Authorized by super role',
            marks=[pytest.mark.roles_features_off('approve_check')],
        ),
        case(
            'd1mbas',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'nevladov',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                'кто:nevladov cannot approve this release.\n'
                'Service has no approvers at all\n'
                'No one can approve its release.\n'
                'Please, request role in IDM\n'
                'Clownductor -> project TAXI -> service role '
                '-> second_service_exist -> deploy approve by manager\n'
                'Clownductor -> project TAXI -> service role '
                '-> second_service_exist -> deploy approve by developer'
            ),
            False,
            2,
            id='with empty roles list (feature forced off)',
            marks=[
                pytest.mark.pgsql(
                    'clownductor', files=['remove_all_roles.sql'],
                ),
                pytest.mark.roles_features_off('approve_check'),
            ],
        ),
        case(
            'd1mbas',
            [
                {
                    'login': ST_LOGIN,
                    'time': '2000-06-28T15:27:25.361+0000',
                    'text': BORDER_COMMENT,
                },
                {
                    'login': 'd1mbas',
                    'time': '2002-06-28T15:27:25.361+0000',
                    'text': APPROVE_KEY_PHRASE,
                },
            ],
            (
                'кто:d1mbas cannot approve this release '
                'because they are the assignee.\n'
                'Ask one of the next people to approve: '
                'кто:isharov, кто:oxcd8o\n'
                'This service has no own approvers. '
                'It may cause some unexpected consequences.\n'
                'Please, request role in IDM\n'
                'Clownductor -> project TAXI -> service role -> '
                'second_service_exist -> deploy approve by developer'
            ),
            False,
            service_id=2,
            extra_developers=['d1mbas'],
            id='no self approve (feature forced off)',
            marks=[pytest.mark.roles_features_off('approve_check')],
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_data.sql'])
@pytest.mark.features_on('startrek_release_single_approve')
async def test_lite_wait_for_single_approve(
        web_context,
        patch,
        add_grant,
        clowny_roles_grants,
        assignee,
        comments,
        feedback_text,
        success,
        service_id,
        extra_developers,
        missing_grants,
):
    clowny_roles_grants.add_manager_approver(
        'effeman', {'id': 'abc_service_exist', 'type': 'service'},
    )
    clowny_roles_grants.add_dev_approver(
        'd1mbas', {'id': 'abc_service_exist', 'type': 'service'},
    )
    clowny_roles_grants.add_dev_approver(
        'isharov', {'id': 'taxi', 'type': 'project'},
    )
    clowny_roles_grants.add_dev_approver(
        'oxcd8o', {'id': 'taxi', 'type': 'project'},
    )
    await add_grant(
        'some-developer1', 'deploy_approve_programmer', service_id=1,
    )
    clowny_roles_grants.add_dev_approver(
        'some-developer1', {'id': 'abc_service_exist', 'type': 'service'},
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself(*args, **kwargs):
        return {'login': ST_LOGIN}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(*args, **kwargs):
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return fake_st_response_comments(comments)

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(st_key, text):
        pass

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['ApproveCubeLiteWaitForSingleApprove'](
            web_context,
            task_data('ApproveCubeLiteWaitForSingleApprove'),
            {
                'st_key': 'TAXIADMIN-10000',
                'release_id': RELEASE_ID,
                'summoned_assignee': assignee,
                'managers': VALID_MANAGERS,
                'developers': VALID_DEVELOPERS + extra_developers,
                'release_key_phrase': APPROVE_KEY_PHRASE,
                'skip': False,
                'single_approve': True,
                'service_id': service_id,
            },
            [],
            conn,
        )

        await cube.update()

    comment_call = create_comment.call
    if feedback_text or comment_call:
        assert comment_call['text'] == feedback_text
        assert not create_comment.call

    assert cube.success == success

    if cube.success:
        assert cube.data['payload'].get('approved', '') == RELEASE_ID
