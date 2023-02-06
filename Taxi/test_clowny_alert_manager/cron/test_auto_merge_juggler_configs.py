import collections

import pytest


@pytest.fixture(autouse=True)
def cache_mocks_fixture(mockserver, mock_clownductor):
    @mock_clownductor('/v1/branches/')
    def _branches_mock(_):
        return [
            {
                'id': 1,
                'service_id': 1,
                'direct_link': 'taxi-infra_clowny_balancer_stable',
                'env': 'stable',
                'name': 'stable',
            },
        ]

    @mock_clownductor('/v1/parameters/remote_values/')
    def _remote_values_mock(request):
        branch = request.query['branch_id']
        branch_to_group = {
            '18': 'duty_group_hejmdal',
            '1234': 'duty_group_not_found',
            '1337': 'duty_group_irresponsible',
            '1338': 'duty_group_days_only',
        }
        duty_group = branch_to_group.get(branch, 'duty_group_1')

        if duty_group == 'duty_group_not_found':
            return {'subsystems': []}

        return {
            'subsystems': [
                {
                    'subsystem_name': 'service_info',
                    'parameters': [
                        {'name': 'duty_group_id', 'value': duty_group},
                    ],
                },
            ],
        }

    @mock_clownductor('/v1/parameters/service_values/')
    def _service_values_mock(_):
        return {
            'subsystems': [
                {
                    'subsystem_name': 'abc',
                    'parameters': [{'name': 'maintainers', 'value': []}],
                },
            ],
        }

    @mockserver.json_handler('/duty-api/api/duty_group')
    def _duty_mock(request):
        duty_name = request.query['group_id']

        suggested_events = [{'user': 'd1mbas'}]
        if duty_name == 'duty_group_hejmdal':
            suggested_events = [{'user': 'oboroth'}]

        return {
            'result': {
                'data': {
                    'staffGroups': [],
                    'suggestedEvents': suggested_events,
                    'currentEvent': {'user': f'duty-user-{duty_name}'},
                },
                'ok': True,
            },
        }


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.translations(
        clownductor={
            'alert_manager.automerge.paths_out_of_infra_cfg_juggler': {
                'ru': 'ПР содержит правки вне `{repo_path}`',
            },
            'alert_manager.automerge.bad_change_type': {
                'ru': (
                    'ПР содержит не только добавление/удаление/'
                    'редактирование файлов'
                ),
            },
            'alert_manager.automerge.ship': {
                'ru': (
                    'ПР соответствует всем критериям для мержа, робот '
                    '`{arcanum_robot_login}` шипнул его. Можете мержить.'
                ),
            },
            'alert_manager.automerge.fix_me': {
                'ru': (
                    'ПР пока нельзя помержить автоматически, '
                    'но вы можете исправить проблему самостоятельно'
                ),
            },
            'alert_manager.automerge.call_admins': {
                'ru': (
                    'ПР нельзя помержить автоматически, обратитесь в '
                    '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx)'
                ),
            },
            'alert_manager.automerge.need_ship_any': {
                'ru': 'нужен шип от любого человека',
            },
            'alert_manager.automerge.need_ship_responsibles': {
                'ru': (
                    'нужен шип от кого-нибудь из ответственных: {responsibles}'
                ),
            },
            'alert_manager.automerge.responsibles_not_found': {
                'ru': 'не удалось определить ответственных',
            },
            'alert_manager.automerge.service_not_found': {
                'ru': (
                    'не удалось определить сервис '
                    'для direct_link={direct_link}'
                ),
            },
            'alert_manager.automerge.duty_group_not_found': {
                'ru': (
                    'не удалось определить дежурную группу для '
                    'direct_link={direct_link}'
                ),
            },
            'alert_manager.automerge.duty_group_is_not_dev': {
                'ru': (
                    'дежурная группа {duty_group_id} не '
                    'круглосуточная (в ночные часы [эскалации по телефону]'
                    '(https://nda.ya.ru/t/4Gr_0rgI5GGPTk) '
                    'получают не дежурные сервиса, а эксплуатация).\n'
                    '\n'
                    'Для того чтобы исправить это и '
                    'проходить ревью внутри команды, '
                    'добавьте в конфиг [CLOWNY_ALERT_MANAGER_DUTY_GROUPS]'
                    '(https://nda.ya.ru/t/i8CV3P8C5GGPkd) запись:\n'
                    '```\n'
                    '{{\n'
                    '\t"id": "{duty_group_id}",\n'
                    '\t"duty_mode": "full"\n'
                    '}}\n'
                    '```'
                ),
            },
            'alert_manager.automerge.not_managed_files': {
                'ru': (
                    'ПР содержит файлы, которые не могут быть обработаны '
                    'автоматически: `{path}`'
                ),
            },
        },
    ),
]


@pytest.mark.features_on(
    'get_duty_group_from_clown', 'enable_clownductor_cache',
)
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_DUTY_GROUPS=[
        {'id': 'duty_group_1', 'duty_mode': 'full'},
        {'id': 'duty_group_hejmdal', 'duty_mode': 'full'},
        {'id': 'duty_group_irresponsible', 'duty_mode': 'IRRESPONSIBLE'},
        {
            'id': 'duty_group_days_only',
            'dev_duty_end': 24,
            'dev_duty_start': 0,
            'duty_mode': 'days_only',
        },
    ],
)
@pytest.mark.parametrize(
    [
        'review_requests',
        'expected_diff_entries_tc',
        'expected_comments_tc',
        'expected_comment',
        'expected_shipped',
    ],
    [
        pytest.param(
            'review_requests_responsible_shipped.json',
            1,
            {'GET': 1, 'POST': 1},
            '666: ПР соответствует всем критериям для мержа, робот '
            '`robot-taxi-tst-31127` шипнул его. Можете мержить.',
            True,
            id='shipped by responsible',
        ),
        pytest.param(
            'review_requests_call_responsible.json',
            1,
            {'GET': 1, 'POST': 1},
            '666: ПР пока нельзя помержить автоматически, но вы можете '
            'исправить проблему самостоятельно: нужен шип от кого-нибудь из '
            'ответственных: @d1mbas, @duty-user-duty_group_1',
            False,
            id='need ship from responsible',
        ),
        pytest.param(
            'review_requests_comment_exists.json',
            1,
            {'GET': 1},
            None,
            True,
            id='ship comment is already posted',
        ),
        pytest.param(
            'review_requests_solomon_only_shipped.json',
            1,
            {'GET': 1, 'POST': 1},
            '123: ПР соответствует всем критериям для мержа, робот '
            '`robot-taxi-tst-31127` шипнул его. Можете мержить.',
            True,
            id='solomon_only + 1 ship by noname',
        ),
        pytest.param(
            'review_requests_solomon_only_not_shipped.json',
            1,
            {'GET': 1, 'POST': 1},
            '123: ПР пока нельзя помержить автоматически, но вы можете '
            'исправить проблему самостоятельно: нужен шип от любого человека',
            False,
            id='solomon_only, but no ships',
        ),
        pytest.param(
            'review_requests_author_responsible_shipped.json',
            1,
            {'GET': 1, 'POST': 1},
            '666: ПР соответствует всем критериям для мержа, робот '
            '`robot-taxi-tst-31127` шипнул его. Можете мержить.',
            True,
            id='author is among responsibles + 1 ship by noname',
        ),
        pytest.param(
            'review_requests_author_responsible_not_shipped.json',
            1,
            {'GET': 1, 'POST': 1},
            '666: ПР пока нельзя помержить автоматически, но вы можете '
            'исправить проблему самостоятельно: нужен шип от любого человека',
            False,
            id='author is among responsibles, but no ships',
        ),
        pytest.param(
            'review_requests_responsibles_empty.json',
            1,
            {'GET': 1, 'POST': 1},
            '555: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'не удалось определить ответственных',
            False,
            id='responsibles intersection for branches is empty',
        ),
        pytest.param(
            'review_requests_branch_not_found.json',
            1,
            {'GET': 1, 'POST': 1},
            '822: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'не удалось определить сервис для '
            'direct_link=taxi_nonexistent_stable',
            False,
            id='branch not found in clownductor',
        ),
        pytest.param(
            'review_requests_duty_group_not_found.json',
            1,
            {'GET': 1, 'POST': 1},
            '321: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'не удалось определить дежурную группу для '
            'direct_link=test_service_stable',
            False,
            id='duty_group not found',
        ),
        pytest.param(
            'review_requests_duty_group_irresponsible.json',
            1,
            {'GET': 1, 'POST': 1},
            '1337: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'дежурная группа duty_group_irresponsible не '
            'круглосуточная (в ночные часы '
            '[эскалации по телефону](https://nda.ya.ru/t/4Gr_0rgI5GGPTk) '
            'получают не дежурные сервиса, а эксплуатация).\n'
            '\n'
            'Для того чтобы исправить это и проходить ревью внутри команды, '
            'добавьте в конфиг [CLOWNY_ALERT_MANAGER_DUTY_GROUPS]'
            '(https://nda.ya.ru/t/i8CV3P8C5GGPkd) запись:\n'
            '```\n'
            '{\n'
            '\t"id": "duty_group_irresponsible",\n'
            '\t"duty_mode": "full"\n'
            '}\n'
            '```',
            False,
            id='duty_group is irresponsible',
        ),
        pytest.param(
            'review_requests_duty_group_days_only.json',
            1,
            {'GET': 1, 'POST': 1},
            '1338: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'дежурная группа duty_group_days_only не '
            'круглосуточная (в ночные часы '
            '[эскалации по телефону](https://nda.ya.ru/t/4Gr_0rgI5GGPTk) '
            'получают не дежурные сервиса, а эксплуатация).\n'
            '\n'
            'Для того чтобы исправить это и проходить ревью внутри команды, '
            'добавьте в конфиг [CLOWNY_ALERT_MANAGER_DUTY_GROUPS]'
            '(https://nda.ya.ru/t/i8CV3P8C5GGPkd) запись:\n'
            '```\n'
            '{\n'
            '\t"id": "duty_group_days_only",\n'
            '\t"duty_mode": "full"\n'
            '}\n'
            '```',
            False,
            id='duty_group is days_only',
        ),
        pytest.param(
            'review_requests_out_of_repo.json',
            1,
            {'GET': 1, 'POST': 1},
            '567: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'ПР содержит правки вне `/taxi/infra/testing/infra-cfg-juggler/`',
            False,
            id='diff_set has out of repo modifications',
        ),
        pytest.param(
            'review_requests_bad_change_type.json',
            1,
            {'GET': 1, 'POST': 1},
            '765: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'ПР содержит не только добавление/удаление/редактирование файлов',
            False,
            id='diff_set has change_type=move file, which is not allowed',
        ),
        pytest.param(
            'review_requests_not_managed_files.json',
            1,
            {'GET': 1, 'POST': 1},
            '345: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'ПР содержит файлы, которые не могут быть обработаны '
            'автоматически: `checks/privet`',
            False,
            id='diff_set has files not managed by this cron',
        ),
        pytest.param(
            'review_requests_already_shipped.json',
            0,
            {},
            None,
            False,
            id='review request is already shipped by robot',
        ),
        pytest.param(
            'review_request_path_order_change_type.json',
            1,
            {'GET': 1, 'POST': 1},
            '11: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'ПР содержит не только добавление/удаление/редактирование файлов',
            False,
        ),
        pytest.param(
            'review_request_path_order_out_of_repo.json',
            1,
            {'GET': 1, 'POST': 1},
            '12: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'ПР содержит правки вне `/taxi/infra/testing/infra-cfg-juggler/`',
            False,
        ),
        pytest.param(
            'review_requests_direct_links_order.json',
            1,
            {'GET': 1, 'POST': 1},
            '2: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'не удалось определить сервис для '
            'direct_link=taxi_unknown1_stable',
            False,
        ),
        pytest.param(
            'review_requests_non_solomon_order.json',
            1,
            {'GET': 1, 'POST': 1},
            '3: ПР нельзя помержить автоматически, обратитесь в '
            '[чат поддержки](https://nda.ya.ru/t/ePhVLReX4jWesx): '
            'ПР содержит файлы, которые не могут быть обработаны '
            'автоматически: `checks/unknown_taxi_unknown1_stable`',
            False,
        ),
    ],
)
async def test_simple(
        cron_runner,
        mockserver,
        mock_arcanum,
        load_json,
        review_requests,
        expected_diff_entries_tc,
        expected_comments_tc,
        expected_comment,
        expected_shipped,
):
    @mock_arcanum('/api/v1/review-requests')
    def _mock_get_review_requests(request):
        return load_json(review_requests)

    @mock_arcanum(
        r'/api/v1/review-requests/(?P<review_request_id>\d+)/diff-sets/'
        r'(?P<diff_set_id>\d+)/diff-entries',
        regex=True,
    )
    def _mock_get_diff_entries(request, review_request_id, diff_set_id):
        diff_entries = load_json('diff_entries.json')

        return diff_entries[review_request_id][diff_set_id]

    @mock_arcanum(
        r'/api/v1/review-requests/(?P<review_request_id>\d+)/diff-sets/'
        r'(?P<diff_set_id>\d+)/ship',
        regex=True,
    )
    def _mock_ship(request, review_request_id, diff_set_id):
        return mockserver.make_response(status=204)

    @mock_arcanum(
        r'/api/v1/review-requests/(?P<review_request_id>\d+)/comments',
        regex=True,
    )
    def _mock_comments(request, review_request_id):
        if request.method == 'GET':
            comments = load_json('comments.json')

            return comments[review_request_id]

        assert request.json['content'] == expected_comment

        return {}

    await cron_runner.auto_merge_juggler_configs()

    assert _mock_ship.times_called == int(expected_shipped)
    assert _mock_get_review_requests.times_called == 1
    assert _mock_get_diff_entries.times_called == expected_diff_entries_tc

    comments_calls = []
    while _mock_comments.has_calls:
        comments_calls.append(_mock_comments.next_call()['request'].method)
    assert collections.Counter(comments_calls) == expected_comments_tc
