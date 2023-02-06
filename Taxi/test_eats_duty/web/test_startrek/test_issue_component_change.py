import logging

import pytest

import taxi.clients.tvm as tvm

from eats_duty.generated.service.settings import plugin as settings
from eats_duty.internal.tasks import set_assignee_task
from eats_duty.internal.utils import links


logger = logging.getLogger('duty')


# 7 tests - 3 data sets with 2 source variants (abc and duty2.0) each
# plus test to check if service uses abc first rather than duty2.0
@pytest.mark.parametrize(
    'abc_times_called, assignee, expected_response, what_source',
    [
        param
        for param_list in [
            [
                pytest.param(
                    1,
                    'nk2ge5k',
                    {'code': 'SUCCESS', 'message': 'Task completed'},
                    src,
                    marks=(
                        pytest.mark.config(
                            EATS_DUTY_RESPONSIBLE={
                                'test-component': {
                                    'abc_service_id': 1234,
                                    'user': 'fallback',
                                },
                            },
                        )
                    ),
                    id='from abc ' + src,
                ),
                pytest.param(
                    1,
                    'test_user_1',
                    {'code': 'SUCCESS', 'message': 'Task completed'},
                    src,
                    marks=(
                        pytest.mark.config(
                            EATS_DUTY_RESPONSIBLE={
                                'test-component': {
                                    'abc_service_id': 1234,
                                    'role_id': 2,
                                },
                            },
                        )
                    ),
                    id='from abc by role ' + src,
                ),
                pytest.param(
                    0,
                    'fallback',
                    {'code': 'SUCCESS', 'message': 'Task completed'},
                    src,
                    marks=(
                        pytest.mark.config(
                            EATS_DUTY_RESPONSIBLE={
                                'test-component': {'user': 'fallback'},
                            },
                        )
                    ),
                    id='from config ' + src,
                ),
            ]
            for src in ['abc', 'duty2']
        ]
        for param in param_list
    ]
    + [
        pytest.param(
            1,
            'p34k1n',
            {'code': 'SUCCESS', 'message': 'Task completed'},
            'both',
            marks=(
                pytest.mark.config(
                    EATS_DUTY_RESPONSIBLE={
                        'test-component': {
                            'abc_service_id': 1234,
                            'role_id': 4,
                        },
                    },
                )
            ),
            id='prefer abc',
        ),
    ],
)
async def test_happy_path(
        patch,
        web_app_client,
        mockserver,
        abc_times_called,
        assignee,
        expected_response,
        what_source,
):
    ticket_text_placeholder = 'ticket_text_placeholder'

    @mockserver.json_handler('/client-abc/v4/duty/on_duty/')
    def on_duty(request):
        assert request.headers['Authorization'] == 'OAuth abc_oauth'
        assert request.query['service'] == '1234'
        assert request.query['fields'] == 'shift,person.login'

        if what_source == 'duty2':
            return []
        return [
            {'person': {'login': 'nk2ge5k'}, 'schedule': {'id': 1}},
            {'person': {'login': 'test_user_1'}, 'schedule': {'id': 2}},
            {'person': {'login': 'test_user_2'}, 'schedule': {'id': 3}},
            {'person': {'login': 'p34k1n'}, 'schedule': {'id': 4}},
        ]

    @mockserver.json_handler('/client-duty2/watcher/v1/shift/for_abc')
    def for_abc(request):
        assert (
            request.headers[tvm.TVM_TICKET_HEADER] == ticket_text_placeholder
        )
        assert request.query['filter'] == 'schedule.service_id=1234'
        assert request.query['current']

        if what_source == 'abc':
            shifts = []
        else:
            shifts = [
                {'staff': {'login': 'nk2ge5k'}, 'schedule': {'id': 1}},
                {'staff': {'login': 'test_user_1'}, 'schedule': {'id': 2}},
                {'staff': {'login': 'test_user_2'}, 'schedule': {'id': 3}},
                {
                    'staff': {'login': 'definetely_not_p34k1n'},
                    'schedule': {'id': 4},
                },
            ]

        return {'result': shifts, 'next': None, 'prev': None}

    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers(dst_service_name, **kwargs):
        assert (
            dst_service_name
            == settings.read_settings('taxi-eats-duty-web').service_settings[
                'duty2_tvm_name'
            ]
        )

        return {tvm.TVM_TICKET_HEADER: ticket_text_placeholder}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [{'display': 'test-component'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': 'open'},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'
        assert kwargs['assignee'] == assignee

        return {'key': 'EDANOTDUTY-100'}

    response = await web_app_client.post(
        '/v1/startrek/issue-component-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == expected_response

    assert on_duty.times_called == abc_times_called
    assert for_abc.times_called == (
        abc_times_called if what_source == 'duty2' else 0
    )


@pytest.mark.config(
    EATS_DUTY_COMPONENT_CHANGE={'notify_on_missing_assignee': True},
)
async def test_no_duty(patch, web_app_client):
    """
    Проверяет, что в случае если для задачи не было найдено ни одного
    дежурного, то мы автоматически добавляем комментарий с призывом
    автора тикета или тех саппорта, для того чтобы тикет был исправлен,
    но делаем это только один раз
    """

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [{'display': 'test-component'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': 'open'},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself():
        return {'login': 'test-bot'}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(ticket, short_id, per_page, log_extra=None):
        assert ticket == 'EDANOTDUTY-100'
        assert short_id is None
        assert per_page is None
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text, summonees):
        assert ticket == 'EDANOTDUTY-100'
        assert summonees == ['test-user']
        assert text == set_assignee_task.NO_DUTY.render(
            config_link=links.CONFIG_DUTY_MAP,
        )

    response = await web_app_client.post(
        '/v1/startrek/issue-component-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    content = await response.json()

    assert response.status == 500
    assert content == {
        'code': 'CANCELED',
        'message': 'No viable candidates found for ticket EDANOTDUTY-100',
    }


@pytest.mark.config(
    EATS_DUTY_COMPONENT_CHANGE={'notify_on_missing_assignee': True},
)
async def test_no_duty_existing_comment(patch, web_app_client):
    """
    Тест проверяет, что в случае если для задачи не нашлось дежурных и
    в конфиге сказано оставлять об этом комментарий, то комментарий не
    будет оставлен дважды
    """

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [{'display': 'test-component'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': 'open'},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself():
        return {'login': 'test-bot'}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(ticket, short_id, per_page, log_extra=None):
        assert ticket == 'EDANOTDUTY-100'
        assert per_page is None

        if short_id == '1':
            return []

        assert short_id is None

        return [
            {
                'id': '1',
                'createdBy': {'id': 'test-bot'},
                'text': set_assignee_task.NO_DUTY.render(
                    config_link=links.CONFIG_DUTY_MAP,
                ),
            },
        ]

    response = await web_app_client.post(
        '/v1/startrek/issue-component-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    content = await response.json()

    assert response.status == 500
    assert content == {
        'code': 'CANCELED',
        'message': 'No viable candidates found for ticket EDANOTDUTY-100',
    }


@pytest.mark.config(
    EATS_DUTY_COMPONENT_CHANGE={'notify_on_multiple_assignee': True},
    EATS_DUTY_RESPONSIBLE={
        'test-component-1': {'user': 'user1'},
        'test-component-2': {'user': 'user2'},
    },
)
async def test_multiple_candidates(patch, web_app_client):
    """
    Тест проверят, что в случае, если для задачи удалось найти нескольких
    исполнителей, то будет оставлен комментарий с возможных исполнителей
    """

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [
                {'display': 'test-component-1'},
                {'display': 'test-component-2'},
            ],
            'createdBy': {'id': 'test-user'},
            'status': {'key': 'open'},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself():
        return {'login': 'test-bot'}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(ticket, short_id, per_page, log_extra=None):
        assert ticket == 'EDANOTDUTY-100'
        assert short_id is None
        assert per_page is None
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text, summonees):
        assert ticket == 'EDANOTDUTY-100'
        assert set(summonees) == set(['user1', 'user2'])
        assert text == set_assignee_task.MULTIPLE_CANDIDATES

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'
        assert kwargs['assignee'] == 'user2'

        return {'key': 'EDANOTDUTY-100'}

    response = await web_app_client.post(
        '/v1/startrek/issue-component-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    content = await response.json()

    assert response.status == 200
    assert content == {'code': 'SUCCESS', 'message': 'Task completed'}


@pytest.mark.parametrize(
    'components',
    [
        pytest.param(
            ['test-component-1', 'test-component-2'],
            marks=(
                pytest.mark.config(
                    EATS_DUTY_COMPONENT_CHANGE={},
                    EATS_DUTY_RESPONSIBLE={
                        'test-component-1': {'user': 'user1'},
                        'test-component-2': {'user': 'user2'},
                    },
                )
            ),
            id='notify_on_multiple_assignee is missing',
        ),
    ],
)
async def test_invalid_config(patch, web_app_client, components):
    """
    Тест проверяет, что в случае невалидного конфига сервис отработает
    без ошибок
    """

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'
        components_json = []
        for component in components:
            components_json.append({'display': component})

        return {
            'key': 'EDANOTDUTY-100',
            'components': components_json,
            'createdBy': {'id': 'test-user'},
            'status': {'key': 'open'},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself():
        return {'login': 'test-bot'}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(ticket, short_id, per_page, log_extra=None):
        assert ticket == 'EDANOTDUTY-100'
        assert short_id is None
        assert per_page is None
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'
        assert kwargs['assignee'] == 'user2'

        return {'key': 'EDANOTDUTY-100'}

    response = await web_app_client.post(
        '/v1/startrek/issue-component-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    content = await response.json()

    assert response.status == 200
    assert content == {'code': 'SUCCESS', 'message': 'Task completed'}


@pytest.mark.config(
    EATS_DUTY_COMPONENT_CHANGE={'notify_on_multiple_assignee': True},
    EATS_DUTY_RESPONSIBLE={'test-component-1': {'user': 'user1'}},
)
async def test_no_update(patch, web_app_client):
    """
    Тест проверят, что для задач, у которых в исполнителях уже стоит
    правильный пользовтель изменений не происходит
    """

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [
                {'display': 'test-component-1'},
                {'display': 'test-component-2'},
            ],
            'createdBy': {'id': 'test-user'},
            'assignee': {'id': 'user1'},
            'status': {'key': 'open'},
        }

    response = await web_app_client.post(
        '/v1/startrek/issue-component-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    content = await response.json()

    assert response.status == 200
    assert content == {'code': 'SUCCESS', 'message': 'Task completed'}


@pytest.mark.config(
    EATS_DUTY_COMPONENT_CHANGE={'notify_on_multiple_assignee': True},
    EATS_DUTY_RESPONSIBLE={
        'test-component-1': {
            'user': 'user1',
            'status': {
                'needQa': {'user': 'user_qa'},
                'needDeveloper': {'user': 'user_developer'},
            },
        },
    },
)
@pytest.mark.parametrize(
    'assignee, status',
    [
        pytest.param('user_qa', 'needQa'),
        pytest.param('user_developer', 'needDeveloper'),
        pytest.param('user1', 'unknown'),
    ],
)
async def test_status_aware_udpate(patch, web_app_client, assignee, status):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'

        return {
            'key': 'EDANOTDUTY-100',
            'components': [{'display': 'test-component-1'}],
            'createdBy': {'id': 'test-user'},
            'status': {'key': status},
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.update_ticket')
    async def _update_ticket(ticket, **kwargs):
        assert ticket == 'EDANOTDUTY-100'
        assert kwargs['assignee'] == assignee

        return {'key': 'EDANOTDUTY-100'}

    response = await web_app_client.post(
        '/v1/startrek/issue-component-change',
        json={'issue_key': 'EDANOTDUTY-100'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {'code': 'SUCCESS', 'message': 'Task completed'}
