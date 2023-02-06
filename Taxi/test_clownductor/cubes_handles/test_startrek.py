import pytest


@pytest.mark.parametrize(
    'cube_name',
    [
        'StartrekCubeCreateTicket',
        'StartrekCubeGenerateServiceTicketParams',
        'StartrekCubeGenerateDatabaseTicketParams',
        'StartrekCubeLinkServiceTickets',
        'StartrekCubeTerminalComment',
        'StartrekCubeCloseTicket',
        'StartrekCubeAddNewServiceTicketToDB',
        'StartrekCubeAddComment',
    ],
)
async def test_post_startrek_cube_handles(
        web_app_client,
        cube_name,
        load_json,
        add_service,
        patch,
        login_mockserver,
        staff_mockserver,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    # pylint: disable=W0612
    async def create_ticket(**kwargs):
        assert (
            kwargs['summary'] == 'some-summary'
            and kwargs['description'] == 'some-description'
        )
        return {'key': 'TAXIADMIN-1'}

    @patch('clownductor.internal.utils.startrek.find_comment')
    # pylint: disable=W0612
    async def find_comment(st_api, st_key, comment_text):
        assert st_key == 'TAXIADMIN-1'
        return 'some'

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    # pylint: disable=W0612
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert 'TAXIADMIN-2' in text
        return

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    # pylint: disable=W0612
    async def get_ticket(*args, **kwargs):
        assert args[0] == 'TAXIADMIN-1'
        return {'status': {'key': 'closed'}}

    @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
    # pylint: disable=W0612
    async def execute_transition(*args, **kwargs):
        assert args[0] == 'TAXIADMIN-1'
        return {}

    login_mockserver()
    staff_mockserver()
    await add_service(
        'taxi',
        'some-service',
        design_review_ticket='https://st.yandex-team.ru/TEST-1',
    )
    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']


@pytest.mark.parametrize(
    'job_vars, expected_payload',
    [
        pytest.param(
            {'ticket': 'COOLTASK-1'},
            {
                'tickets_info': {
                    'COOLTASK-1': {
                        'key': 'COOLTASK-1',
                        'status': {'id': '4', 'key': 'inProgress'},
                        'createdBy': {'id': 'd1mbas', 'is_robot': False},
                        'assignee': {'id': 'deoevgen', 'is_robot': True},
                        'followers': [
                            {
                                'id': 'oxcd8o',
                                'is_robot': False,
                                'chief': 'ilyasov',
                            },
                            {'id': 'eatroshkin', 'is_robot': False},
                            {'id': 'deoevgen', 'is_robot': True},
                        ],
                    },
                },
            },
            id='single_ticket_on_ticket',
        ),
        pytest.param(
            {'tickets': ['COOLTASK-1', 'COOLTASK-2']},
            {
                'tickets_info': {
                    'COOLTASK-1': {
                        'key': 'COOLTASK-1',
                        'status': {'id': '4', 'key': 'inProgress'},
                        'createdBy': {'id': 'd1mbas', 'is_robot': False},
                        'assignee': {'id': 'deoevgen', 'is_robot': True},
                        'followers': [
                            {
                                'id': 'oxcd8o',
                                'is_robot': False,
                                'chief': 'ilyasov',
                            },
                            {'id': 'eatroshkin', 'is_robot': False},
                            {'id': 'deoevgen', 'is_robot': True},
                        ],
                    },
                    'COOLTASK-2': {
                        'key': 'COOLTASK-2',
                        'status': {'id': '4', 'key': 'inProgress'},
                        'createdBy': {'id': 'd1mbas', 'is_robot': False},
                        'followers': [
                            {'id': 'spock', 'is_robot': False},
                            {'id': 'eatroshkin', 'is_robot': False},
                            {'id': 'deoevgen', 'is_robot': True},
                        ],
                    },
                },
            },
            id='tickets_list',
        ),
        pytest.param(
            {'tickets': ['COOLTASK-1'], 'ticket': 'COOLTASK-2'},
            {
                'tickets_info': {
                    'COOLTASK-1': {
                        'key': 'COOLTASK-1',
                        'status': {'id': '4', 'key': 'inProgress'},
                        'createdBy': {'id': 'd1mbas', 'is_robot': False},
                        'assignee': {'id': 'deoevgen', 'is_robot': True},
                        'followers': [
                            {
                                'id': 'oxcd8o',
                                'is_robot': False,
                                'chief': 'ilyasov',
                            },
                            {'id': 'eatroshkin', 'is_robot': False},
                            {'id': 'deoevgen', 'is_robot': True},
                        ],
                    },
                    'COOLTASK-2': {
                        'key': 'COOLTASK-2',
                        'status': {'id': '4', 'key': 'inProgress'},
                        'createdBy': {'id': 'd1mbas', 'is_robot': False},
                        'followers': [
                            {'id': 'spock', 'is_robot': False},
                            {'id': 'eatroshkin', 'is_robot': False},
                            {'id': 'deoevgen', 'is_robot': True},
                        ],
                    },
                },
            },
            id='tickets_list_and_ticket',
        ),
    ],
)
async def test_helper_cube(
        patch,
        load_json,
        staff_mockserver,
        job_vars,
        expected_payload,
        call_cube_handle,
):
    staff_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        mocked_file = '{}.json'.format(ticket.lower().replace('-', '_'))
        return load_json(mocked_file)

    data = {
        'content_expected': {'payload': expected_payload, 'status': 'success'},
        'data_request': {
            'input_data': job_vars,
            'job_id': 1,
            'retries': 0,
            'status': 'in_progress',
            'task_id': 1,
        },
    }
    await call_cube_handle('StartrekCubeGetTicketInfo', data)
