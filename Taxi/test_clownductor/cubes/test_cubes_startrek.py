import pytest

from taxi.clients import startrack

from clownductor.internal.tasks import cubes
from clownductor.internal.utils import postgres


def task_data(name='name'):
    return {
        'id': 123,
        'job_id': 456,
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


async def test_create_new_ticket(
        patch,
        web_context,
        add_project,
        add_service,
        login_mockserver,
        staff_mockserver,
):
    login_mockserver()
    staff_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(**kwargs):
        assert (
            kwargs['summary'] == 'some-summary'
            and kwargs['description'] == 'some-description'
        )
        return {'key': 'TAXIADMIN-1'}

    await add_project('taxi')
    service = await add_service('taxi', 'some-service')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['StartrekCubeCreateTicket'](
            web_context,
            task_data(),
            {
                'service_id': service['id'],
                'ticket_summary': 'some-summary',
                'ticket_description': 'some-description',
                'user': 'axolm',
            },
            [],
            conn,
        )
        await cube.update()
        assert cube.success
    assert len(create_ticket.calls) == 1


async def test_create_new_ticket_mds_queue(
        patch,
        web_context,
        add_project,
        add_service,
        login_mockserver,
        staff_mockserver,
):
    login_mockserver()
    staff_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(**kwargs):
        assert (
            kwargs['summary'] == 'some-summary'
            and kwargs['description'] == 'some-description'
        )
        return {'key': 'MDSSUPPORT-1'}

    await add_project('taxi')
    service = await add_service('taxi', 'some-service')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['StartrekCubeCreateTicket'](
            web_context,
            task_data(),
            {
                'service_id': service['id'],
                'ticket_summary': 'some-summary',
                'ticket_description': 'some-description',
                'user': 'axolm',
                'set_ticket_project': 'mdssupport',
            },
            [],
            conn,
        )
        await cube.update()
        assert cube.success
    assert len(create_ticket.calls) == 1


@pytest.mark.parametrize(
    'ticket, component_list, existing_component, success',
    [
        pytest.param(
            'TAXIREL-1',
            [100],
            False,
            True,
            id='adding component - okay',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_STARTREK_QUEUE_COMPONENTS={
                        'TAXIREL': [100],
                        'EDAREL': [200],
                        'TAXIDWHREL': [300],
                    },
                ),
            ],
        ),
        pytest.param(
            'TAXIREL-1',
            [200],
            True,
            True,
            id='adding component - partial',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_STARTREK_QUEUE_COMPONENTS={
                        'TAXIREL': [100, 200],
                        'EDAREL': [200],
                        'TAXIDWHREL': [300],
                    },
                ),
            ],
        ),
        pytest.param(
            'TAXIREL-1',
            [100],
            True,
            False,
            id='adding component - it already exists',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_STARTREK_QUEUE_COMPONENTS={
                        'TAXIREL': [100],
                        'EDAREL': [200],
                        'TAXIDWHREL': [300],
                    },
                ),
            ],
        ),
        pytest.param(
            'TAXIREL-1',
            None,
            False,
            False,
            id='feature is disabled',
            marks=[
                pytest.mark.features_off('startrek_clown_component'),
                pytest.mark.config(
                    CLOWNDUCTOR_STARTREK_QUEUE_COMPONENTS={
                        'TAXIREL': [100],
                        'EDAREL': [200],
                        'TAXIDWHREL': [300],
                    },
                ),
            ],
        ),
        pytest.param(
            'TAXIADMIN-1',
            None,
            False,
            False,
            id=(
                'correct ticket id but in a queue we '
                'don\'t have anything to do with'
            ),
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_STARTREK_QUEUE_COMPONENTS={
                        'TAXIREL': [100],
                        'EDAREL': [200],
                        'TAXIDWHREL': [300],
                    },
                ),
            ],
        ),
        pytest.param(
            'insane_ticket_value',
            None,
            False,
            False,
            id='garbage ticket id',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_STARTREK_QUEUE_COMPONENTS={
                        'TAXIREL': [100],
                        'EDAREL': [200],
                        'TAXIDWHREL': [300],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.features_on('startrek_clown_component')
async def test_update_ticket(
        patch,
        ticket: str,
        component_list,
        existing_component: bool,
        success: bool,
        web_context,
        login_mockserver,
        staff_mockserver,
):
    login_mockserver()
    staff_mockserver()
    returned_component_exists = (
        [
            {
                'self': 'https://st-api.yandex-team.ru/v2/components/100',
                'id': '100',
                'display': 'Чудесный компонент релизов такси',
            },
        ]
        if existing_component
        else []
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def update_ticket(ticket, **kwargs):
        pass

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        if ticket not in ('TAXIADMIN-1', 'TAXIREL-1'):
            return {
                'errors': {},
                'errorMessages': ['Задача не существует.'],
                'statusCode': 404,
            }
        return {
            'self': f'https://st-api.yandex-team.ru/v2/issues/{ticket}',
            'key': ticket,
            'components': returned_component_exists,
            'type': {
                'self': 'https://st-api.yandex-team.ru/v2/issuetypes/2',
                'id': '2',
                'key': 'task',
                'display': 'Задача',
            },
            'resolution': {
                'self': 'https://st-api.yandex-team.ru/v2/resolutions/1',
                'id': '1',
                'key': 'fixed',
                'display': 'Решен',
            },
        }

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['StartrekCubeTicketAddClownComponent'](
            web_context, task_data(), {'ticket_id': ticket}, [], conn,
        )
        await cube.update()
        assert cube.success
    call = update_ticket.call
    assert bool(call) is success
    if call:
        assert call['kwargs'] == {
            'components': {
                'add': [
                    i
                    for i in component_list
                    if (not returned_component_exists)
                    or str(i) != returned_component_exists[0]['id']
                ],
            },
        }
    assert not update_ticket.call


@pytest.mark.parametrize(
    'state, ticket, expected_action',
    [
        pytest.param(
            'open', 'TAXIREL-10000', 'closed', id='correct open ticket',
        ),
        pytest.param(
            'readyForRelease',
            'TAXIREL-10000',
            'close',
            id='correct ready ticket',
        ),
        pytest.param(
            'testing', 'TAXIREL-10000', 'closed', id='correct testing ticket',
        ),
        pytest.param(
            'weird_status',
            'TAXIREL-10000',
            'close',
            id='correct testing ticket with weird status',
        ),
        pytest.param(
            'open', 'OLOLOREL-10000', 'close', id='incorrect open ticket',
        ),
        pytest.param('closed', 'OLOLOREL-10000', None, id='closed ticket'),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_STARTREK_CLOSE_ACTIONS={
        'TAXIREL': {
            'open': 'closed',
            'readyForRelease': 'close',
            'testing': 'closed',
        },
    },
)
async def test_close_ticket(
        patch, web_context, state, ticket, expected_action,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(*args, **kwargs):
        return {'status': {'key': state}}

    @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
    async def _execute_transition(*args, **kwargs):
        return

    cube = cubes.CUBES['StartrekCubeCloseTicket'](
        web_context,
        task_data('StartrekCubeCloseTicket'),
        {'new_service_ticket': ticket},
        [],
        None,
    )

    await cube.update()
    assert cube.success

    get_ticket_call = _get_ticket.call
    assert get_ticket_call['args'][0] == ticket
    assert not _get_ticket.call

    transition_call = _execute_transition.call
    if expected_action:
        assert transition_call['args'][0] == ticket
        assert transition_call['args'][1] == expected_action
    else:
        assert not transition_call

    assert not _execute_transition.call


async def test_generate_service_ticket_params(
        patch,
        web_context,
        add_project,
        add_service,
        login_mockserver,
        staff_mockserver,
):
    login_mockserver()
    staff_mockserver()

    project = await add_project('taxi')
    service = await add_service('taxi', 'some-service')

    cube = cubes.CUBES['StartrekCubeGenerateServiceTicketParams'](
        web_context,
        task_data(),
        {
            'project_id': project['id'],
            'service_id': service['id'],
            'preset_name': 'x2nano',
            'needs_unstable': False,
            'needs_balancers': True,
            'user': 'nevladov',
        },
        [],
        None,
    )
    await cube.update()
    assert cube.success
    assert (
        cube.data['payload']['ticket_summary']
        == 'New RTC-service environment: taxi-some-service'
    )


@pytest.mark.parametrize('comment_exists', [True, False])
async def test_link_service_tickets(
        patch, web_context, login_mockserver, comment_exists,
):
    login_mockserver()

    @patch('clownductor.internal.utils.startrek.find_comment')
    async def find_comment(st_api, st_key, comment_text):
        assert st_key == 'TAXIADMIN-1'
        assert 'TAXIADMIN-2' in comment_text
        if comment_exists:
            return 'some'
        return None

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert 'TAXIADMIN-2' in text
        return

    cube = cubes.CUBES['StartrekCubeLinkServiceTickets'](
        web_context,
        task_data(),
        {
            'linked_service_ticket': 'TAXIADMIN-1',
            'new_service_ticket': 'TAXIADMIN-2',
        },
        [],
        None,
    )
    await cube.update()
    assert cube.success
    assert len(find_comment.calls) == 1
    assert len(create_comment.calls) == (0 if comment_exists else 1)


@pytest.mark.parametrize('comment_exists', [True, False])
@pytest.mark.parametrize('comment_props', [None, {}])
@pytest.mark.parametrize('ticket_allowed', [True, False])
@pytest.mark.parametrize('skip', [True, False])
async def test_add_comment(
        patch,
        web_context,
        comment_exists,
        comment_props,
        ticket_allowed,
        skip,
):
    @patch('clownductor.internal.utils.startrek.find_comment')
    async def find_comment(st_api, st_key, comment_text):
        assert st_key == 'TAXIADMIN-1'
        assert comment_text == 'some'
        if not ticket_allowed:
            raise startrack.PermissionsError()
        if comment_exists:
            return 'some'
        return None

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text, **kwargs):
        if comment_props is not None:
            assert kwargs == comment_props
        assert ticket == 'TAXIADMIN-1'
        assert text == 'some'
        return

    job_vars = {
        'st_task': 'TAXIADMIN-1',
        'text': 'some',
        'skip_add_comment': skip,
    }
    if comment_props is not None:
        job_vars['comment_props'] = comment_props

    cube = cubes.CUBES['StartrekCubeAddComment'](
        web_context, task_data(), job_vars, [], None,
    )

    await cube.update()
    if ticket_allowed or skip:
        assert cube.success
    else:
        assert cube.failed
    if not skip:
        assert len(find_comment.calls) == 1
        assert len(create_comment.calls) == (
            1 if not comment_exists and ticket_allowed else 0
        )
