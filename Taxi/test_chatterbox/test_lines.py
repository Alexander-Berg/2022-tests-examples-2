# pylint: disable=protected-access

import http

import pytest

from taxi.clients import support_metrics

from chatterbox.internal.tasks_manager import _constants
from test_chatterbox import plugins as conftest


@pytest.mark.translations(
    chatterbox={
        'lines.corp': {'ru': 'Корп', 'en': 'Corp'},
        'lines.urgent': {'ru': 'Ургент', 'en': 'Urgent'},
    },
)
async def test_available_lines(cbox: conftest.CboxWrap):
    await cbox.post(
        '/v1/lines/available/', data={}, headers={'Accept-Language': 'en'},
    )
    available_lines = [
        {
            'line': 'urgent',
            'line_name': 'Ургент',
            'open_chats': 1,
            'types': ['client'],
            'mode': 'offline',
            'can_take': True,
            'can_search': True,
            'logbroker_telephony': False,
        },
        {
            'line': 'corp',
            'line_name': 'Corp',
            'open_chats': 1,
            'types': ['client'],
            'mode': 'online',
            'can_take': True,
            'can_search': True,
            'logbroker_telephony': False,
        },
        {
            'line': 'vip',
            'line_name': 'ВИП',
            'open_chats': 0,
            'types': ['client'],
            'mode': 'online',
            'can_take': True,
            'can_search': True,
            'logbroker_telephony': False,
        },
        {
            'line': 'first',
            'line_name': 'Первая линия',
            'open_chats': 2,
            'types': ['client'],
            'mode': 'offline',
            'can_take': True,
            'can_search': True,
            'logbroker_telephony': False,
        },
        {
            'line': 'driver_first',
            'line_name': 'Первая водительская линия',
            'open_chats': 0,
            'types': ['driver'],
            'mode': 'offline',
            'can_take': True,
            'can_search': True,
            'logbroker_telephony': False,
        },
    ]

    assert cbox.status == 200
    assert cbox.body_data == {'available_lines': available_lines}


@pytest.mark.config(
    CHATTERBOX_LINE_REQUIRED_FIELDS={
        '__default__': ['macros'],
        'custom_line': ['custom_field'],
    },
    CHATTERBOX_SETTINGS_SEND_EMAIL={
        'first': {
            'default_email_from': 'chatterbox@yandex.ru',
            'tracker_queue': 'CHATTERBOX',
        },
    },
)
@pytest.mark.parametrize(
    'line, expected_result',
    [
        (
            'first',
            {
                'macros': [
                    {
                        'id': '5a68200190e5d644b19b31c8',
                        'title': 'test1',
                        'comment': 'comment1',
                        'tags': ['1', '2'],
                    },
                    {
                        'id': '5a68200190e5d644b19b31c9',
                        'title': 'test2',
                        'comment': 'comment2',
                        'tags': ['3', '4'],
                    },
                ],
                'themes': [],
                'themes_style': 'tree',
                'themes_tree': [
                    {
                        'children': [],
                        'id': '5a68200190e5d644b19b31d0',
                        'title': 'Theme',
                        'tags': ['3', '4'],
                    },
                ],
                'required_answer_fields': ['macros'],
                'default_email_from': ['chatterbox@yandex.ru'],
            },
        ),
        (
            'urgent',
            {
                'macros': [
                    {
                        'id': '5a68200190e5d644b19b31c9',
                        'title': 'test2',
                        'comment': 'comment2',
                        'tags': ['3', '4'],
                    },
                ],
                'themes': [
                    {
                        'id': '5a68200190e5d644b19b31d0',
                        'title': 'Theme',
                        'tags': ['3', '4'],
                    },
                ],
                'themes_style': 'list',
                'required_answer_fields': ['macros'],
            },
        ),
        (
            'vip',
            {
                'macros': [
                    {
                        'id': '5a68200190e5d644b19b31c8',
                        'title': 'test1',
                        'comment': 'comment1',
                        'tags': ['1', '2'],
                    },
                ],
                'themes': [],
                'required_answer_fields': ['macros'],
                'themes_style': 'list',
            },
        ),
        (
            'unknown',
            {
                'macros': [],
                'themes': [],
                'required_answer_fields': ['macros'],
                'themes_style': 'tree',
                'themes_tree': [],
            },
        ),
        (
            'custom_line',
            {
                'macros': [],
                'themes': [],
                'required_answer_fields': ['custom_field'],
                'themes_style': 'tree',
                'themes_tree': [],
            },
        ),
    ],
)
async def test_line_options_list(cbox, line, expected_result):
    await cbox.query('/v1/lines/{}/options/'.format(line))
    assert cbox.status == http.HTTPStatus.OK, line
    assert cbox.body_data == expected_result


@pytest.mark.config(
    CHATTERBOX_LINE_REQUIRED_FIELDS={
        '__default__': ['macros'],
        'custom_line': ['custom_field'],
    },
    CHATTERBOX_LINES={
        'themes_line': {
            'name': 'Первая линия',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'autoreply': True,
            'themes_style': 'tree',
        },
    },
)
@pytest.mark.parametrize(
    'line, expected_result',
    [
        (
            'themes_line',
            {
                'macros': [
                    {
                        'id': '5a68200190e5d644b19b31c8',
                        'title': 'test1',
                        'comment': 'comment1',
                        'tags': ['1', '2'],
                    },
                    {
                        'id': '5a68200190e5d644b19b31c9',
                        'title': 'test2',
                        'comment': 'comment2',
                        'tags': ['3', '4'],
                    },
                ],
                'themes': [
                    {'id': '3', 'title': 'Theme::Subtheme 1', 'tags': []},
                    {'id': '4', 'title': 'Theme::Subtheme 2', 'tags': []},
                    {
                        'id': '5',
                        'title': 'Theme::Subtheme 1::Subsubtheme 1',
                        'tags': [],
                    },
                ],
                'themes_style': 'tree',
                'themes_tree': [
                    {
                        'id': '6',
                        'title': 'Theme 2',
                        'tags': [],
                        'children': [],
                    },
                    {
                        'id': '5a68200190e5d644b19b31d0',
                        'title': 'Theme',
                        'tags': ['3', '4'],
                        'children': [
                            {
                                'id': '4',
                                'title': 'Subtheme 2',
                                'tags': [],
                                'children': [],
                            },
                            {
                                'id': '3',
                                'title': 'Subtheme 1',
                                'tags': [],
                                'children': [
                                    {
                                        'id': '5',
                                        'title': 'Subsubtheme 1',
                                        'tags': [],
                                        'children': [],
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'required_answer_fields': ['macros'],
            },
        ),
    ],
)
async def test_line_options_tree(cbox, line, expected_result):
    await cbox.query('/v1/lines/{}/options/'.format(line))
    assert cbox.status == http.HTTPStatus.OK, line
    assert cbox.body_data == expected_result


@pytest.mark.parametrize(
    'line, chat_type, expected_result',
    [
        (
            'first',
            'driver',
            {
                'macros': [
                    {
                        'comment': 'comment1',
                        'id': '5a68200190e5d644b19b31c8',
                        'tags': ['1', '2'],
                        'title': 'test1',
                    },
                ],
                'themes': [],
                'themes_tree': [
                    {
                        'children': [],
                        'id': '5a68200190e5d644b19b31d0',
                        'title': 'Theme',
                        'tags': ['3', '4'],
                    },
                ],
                'themes_style': 'tree',
                'required_answer_fields': ['macros'],
            },
        ),
    ],
)
async def test_line_options_chat_type(cbox, line, chat_type, expected_result):
    await cbox.query(
        '/v1/lines/{}/options/?chat_type={}'.format(line, chat_type),
    )
    assert cbox.status == http.HTTPStatus.OK, line
    assert cbox.body_data == expected_result


@pytest.mark.parametrize(
    'task, line, expected_result',
    [
        # old-style conditions
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {'some': 'meta', 'another': 'data'},
            },
            {},
            False,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {'types': ['client'], 'tags': ['tags']},
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {'types': ['client'], 'tags': ['bad']},
            False,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'support',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {'types': ['client'], 'tags': ['good', 'tags']},
            False,
        ),
        (
            {
                '_id': 'some_task_id',
                'tags': ['some', 'tags'],
                'meta_info': {'some': 'meta'},
            },
            {'tags': ['tags'], 'fields': {'field': ['value']}},
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'tags': ['some', 'tags'],
                'meta_info': {'some': 'meta'},
            },
            {'tags': ['bad'], 'fields': {'field': ['value']}},
            False,
        ),
        (
            {
                '_id': 'some_task_id',
                'tags': ['some', 'tags'],
                'meta_info': {'some': 'meta'},
            },
            {'tags': ['bad'], 'fields': {'some': ['good', 'meta']}},
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'meta_info': {'some': 'meta', 'another': 'data'},
            },
            {
                'tags': ['bad'],
                'fields': {'some': ['good', 'meta'], 'another': ['bad']},
            },
            True,
        ),
        # new-style conditions
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {'conditions': {}},
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {'conditions': {'type': 'client', 'tags': 'tags'}},
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {'conditions': {'type': 'client', 'tags': 'bad'}},
            False,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'support',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {
                'conditions': {
                    'type': 'client',
                    'tags': {'#in': ['good', 'tags']},
                },
            },
            False,
        ),
        (
            {
                '_id': 'some_task_id',
                'tags': ['some', 'tags'],
                'meta_info': {'some': 'meta'},
            },
            {
                'conditions': {
                    '#or': [{'tags': 'tags'}, {'fields/field': 'value'}],
                },
            },
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'tags': ['some', 'tags'],
                'meta_info': {'some': 'meta'},
            },
            {
                'conditions': {
                    '#or': [{'tags': 'bad'}, {'fields/field': 'value'}],
                },
            },
            False,
        ),
        (
            {
                '_id': 'some_task_id',
                'tags': ['some', 'tags'],
                'meta_info': {'some': 'meta'},
            },
            {
                'conditions': {
                    '#or': [
                        {'tags': 'bad'},
                        {'fields/some': {'#in': ['good', 'meta']}},
                    ],
                },
            },
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'meta_info': {'some': 'meta', 'another': 'data'},
            },
            {
                'conditions': {
                    '#or': [
                        {'tags': 'bad'},
                        {'fields/some': {'#in': ['good', 'meta']}},
                        {'fields/another': 'bad'},
                    ],
                },
            },
            True,
        ),
        # mixed case, old-style ignored
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {
                'tags': ['tags'],
                'conditions': {'type': 'client', 'tags': 'bad'},
            },
            False,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
            },
            {
                'fields': {'some': ['bad', 'values']},
                'conditions': {'type': 'client', 'tags': 'tags'},
            },
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': [],
                'meta_info': {},
                'profile': 'taxi',
            },
            {'conditions': {'profile': 'taxi'}},
            True,
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': [],
                'meta_info': {},
                'profile': 'taxi',
            },
            {'conditions': {'profile': 'eats'}},
            False,
        ),
    ],
)
def test_line_conditions(cbox, task, line, expected_result):
    result = cbox.app.autoexporter._check_line_conditions(
        task, 'some_line', line, log_extra=None,
    )
    assert result == expected_result


@pytest.mark.config(CHATTERBOX_GET_LINES_BACKLOG_FROM_SUPPORT_METRICS=True)
async def test_support_metrics_error(cbox: conftest.CboxWrap, patch):
    @patch(
        'taxi.clients.support_metrics.'
        'SupportMetricsClient.fetch_raw_aggregated_stats',
    )
    async def _dummy_fetch_raw_aggregated_stats(*args, **kwargs):
        raise support_metrics.RequestRetriesExceeded

    await cbox.post(
        '/v1/lines/available/', data={}, headers={'Accept-Language': 'en'},
    )

    assert cbox.status == 200
    for line in cbox.body_data['available_lines']:
        assert 'open_chats' not in line


@pytest.mark.now('2019-11-27T12:15:10+0000')
@pytest.mark.config(CHATTERBOX_GET_LINES_BACKLOG_FROM_SUPPORT_METRICS=True)
async def test_get_from_support_metrics(
        cbox: conftest.CboxWrap,
        patch_aiohttp_session,
        patch_raw_stat_lines_backlog,
):
    stat_lines_backlog = [
        {
            'line': 'urgent',
            'average_counts': {
                'new': 1.0,
                'reopened': 0.0,
                'forwarded': 0.0,
                'closed': 1000.0,
            },
        },
        {
            'line': 'corp',
            'average_counts': {
                'new': 0.0,
                'reopened': 1.0,
                'forwarded': 0.0,
                'closed': 1000.0,
            },
        },
        {
            'line': 'vip',
            'average_counts': {
                'new': 0.0,
                'reopened': 0.0,
                'forwarded': 0.0,
                'closed': 1000.0,
            },
        },
        {
            'line': 'first',
            'average_counts': {
                'new': 1.0,
                'reopened': 1.0,
                'forwarded': 0.0,
                'closed': 1000.0,
            },
        },
        {
            'line': 'driver_first',
            'average_counts': {
                'new': 0.0,
                'reopened': 0.0,
                'forwarded': 0.0,
                'closed': 1000.0,
            },
        },
    ]
    expected_lines_count = {
        'urgent': 1,
        'corp': 1,
        'vip': 0,
        'first': 2,
        'driver_first': 0,
    }

    patch_raw_stat_lines_backlog(result=stat_lines_backlog)

    await cbox.post(
        '/v1/lines/available/', data={}, headers={'Accept-Language': 'en'},
    )

    assert cbox.status == 200
    for line in cbox.body_data['available_lines']:
        assert line['open_chats'] == expected_lines_count[line['line']]


@pytest.mark.config(
    CHATTERBOX_LINES={
        'default_taxi': {
            'name': 'Первая линия Такси',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
        },
        'second_taxi': {
            'name': 'Вторая линия Такси',
            'types': ['client'],
            'tags': ['test_tag'],
            'fields': {},
            'priority': 3,
            'sort_order': 1,
        },
        'default_zen': {
            'name': 'Первая линия Дзена',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'profile': 'support-zen',
        },
        'line_zen': {
            'name': 'Вторая линия Дзена',
            'types': ['client'],
            'tags': ['some', 'tags'],
            'fields': {},
            'priority': 3,
            'sort_order': 1,
            'autoreply': True,
            'profile': 'support-zen',
        },
    },
)
@pytest.mark.parametrize(
    'task, expected_line',
    [
        # new-style conditions
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
                'line': 'default_taxi',
                'status': _constants.STATUS_PREDISPATCH,
            },
            'Первая линия Такси',
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['test_tag'],
                'meta_info': {},
                'line': 'second_taxi',
                'status': _constants.STATUS_PREDISPATCH,
            },
            'Вторая линия Такси',
        ),
        (
            {
                '_id': 'some_task_id',
                'chat_type': 'client',
                'tags': ['some', 'tags'],
                'meta_info': {},
                'line': 'default_zen',
                'profile': 'support-zen',
                'status': _constants.STATUS_PREDISPATCH,
            },
            'Вторая линия Дзена',
        ),
    ],
)
async def test_line_auto_switch(cbox: conftest.CboxWrap, task, expected_line):
    _, selected_line, _ = await cbox.app.autoexporter.check_line(
        task, lazy_status_change=True,
    )
    assert selected_line['name'] == expected_line


@pytest.mark.config(
    CHATTERBOX_LINES={
        'default_taxi': {
            'name': 'Первая линия Такси',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'categories': ['taxi', 'category,with,commas'],
        },
        'single_category': {
            'name': 'Первая линия Такси',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'categories': ['single'],
        },
    },
)
@pytest.mark.usefixtures('mock_collections')
@pytest.mark.parametrize(
    'line, expected_collections',
    [
        ('default_taxi', 'collections_1.json'),
        ('single_category', 'collections_2.json'),
        ('not exists line', {'collections': []}),
    ],
)
async def test_collections_by_line(
        cbox: conftest.CboxWrap, load_json, line, expected_collections,
):
    if isinstance(expected_collections, str):
        collections = load_json(expected_collections)
    else:
        collections = expected_collections
    await cbox.query(f'/v1/lines/{line}/collections/')

    assert cbox.status == 200
    assert cbox.body_data == collections


@pytest.mark.config(
    CHATTERBOX_LINES={
        'line_0': {'name': 'line_0', 'priority': 20, 'sort_order': 1},
        'line_1': {'name': 'line_1', 'priority': 19, 'sort_order': 1},
        'line_2': {'name': 'line_2', 'priority': 18, 'sort_order': 1},
        'line_3': {'name': 'line_3', 'priority': 17, 'sort_order': 1},
        'line_4': {'name': 'line_4', 'priority': 16, 'sort_order': 1},
    },
    CHATTERBOX_LINES_PERMISSIONS={
        'line_0': {'take': [{'permissions': ['permission_0']}]},
        'line_1': {'take': [{'permissions': ['permission_1']}]},
        'line_2': {
            'take': [{'permissions': ['permission_1', 'permission_2']}],
        },
        'line_3': {
            'take': [{'permissions': ['permission_1', 'permission_2']}],
        },
        'line_4': {'take': [{'permissions': ['permission_2']}]},
    },
)
@pytest.mark.parametrize(
    'data, expected_answer',
    [
        ({'logins': []}, []),
        ({'logins': ['not_existing_login']}, []),
        ({'logins': ['login_without_groups']}, []),
        ({'logins': ['login_without_permissions']}, []),
        ({'logins': ['login_without_lines_for_permissions']}, []),
        (
            {'logins': ['login_0', 'login_0']},
            [{'login': 'login_0', 'lines': ['line_0']}],
        ),
        (
            {'logins': ['login_1', 'login_2']},
            [
                {'login': 'login_2', 'lines': ['line_2', 'line_3', 'line_4']},
                {'login': 'login_1', 'lines': ['line_1', 'line_2', 'line_3']},
            ],
        ),
        (
            {
                'logins': [
                    'not_existing_login',
                    'login_without_groups',
                    'login_without_lines_for_permissions',
                    'login_0',
                    'login_1',
                    'login_2',
                ],
            },
            [
                {'login': 'login_2', 'lines': ['line_2', 'line_3', 'line_4']},
                {'login': 'login_1', 'lines': ['line_1', 'line_2', 'line_3']},
                {'login': 'login_0', 'lines': ['line_0']},
            ],
        ),
        (
            {'logins': ['login_3']},
            [
                {
                    'login': 'login_3',
                    'lines': ['line_1', 'line_2', 'line_3', 'line_4'],
                },
            ],
        ),
    ],
)
async def test_available_by_logins(
        cbox: conftest.CboxWrap, data, expected_answer,
):

    await cbox.post('/v1/lines/available_by_logins/', data=data)
    assert cbox.status == 200
    assert cbox.body_data == expected_answer


@pytest.mark.config(
    CHATTERBOX_LINES={
        'line_0': {
            'name': 'line_0',
            'mode': 'online',
            'title_tanker': 'line_0_tanker_key',
        },
        'line_1': {'name': 'line_1', 'mode': 'online'},
        'line_2': {
            'name': 'line_2',
            'mode': 'offline',
            'title_tanker': 'line_2_tanker_key',
        },
        'line_3': {'name': 'line_3', 'mode': 'offline'},
        'line_4': {'name': 'line_4'},
    },
)
@pytest.mark.parametrize(
    'data, expected_answer',
    [
        ({'lines': []}, []),
        (
            {'lines': ['line_0', 'line_1', 'line_2', 'line_3', 'line_4']},
            [
                {
                    'line': 'line_0',
                    'line_tanker_key': 'line_0_tanker_key',
                    'mode': 'online',
                    'open_chats': 10,
                },
                {
                    'line': 'line_1',
                    'line_tanker_key': 'line_1',
                    'mode': 'online',
                    'open_chats': 0,
                },
                {
                    'line': 'line_2',
                    'line_tanker_key': 'line_2_tanker_key',
                    'mode': 'offline',
                    'open_chats': 0,
                },
                {
                    'line': 'line_3',
                    'line_tanker_key': 'line_3',
                    'mode': 'offline',
                    'open_chats': 18,
                },
                {
                    'line': 'line_4',
                    'line_tanker_key': 'line_4',
                    'mode': 'offline',
                    'open_chats': 0,
                },
            ],
        ),
    ],
)
async def test_lines_info(
        cbox: conftest.CboxWrap,
        data,
        expected_answer,
        patch_raw_stat_lines_backlog,
):
    stat_lines_backlog = [
        {
            'line': 'line_0',
            'average_counts': {
                'new': 10.0,
                'reopened': 0.0,
                'forwarded': 0.0,
                'closed': 1000.0,
            },
        },
        {
            'line': 'line_3',
            'average_counts': {
                'new': 10.0,
                'reopened': 5.0,
                'forwarded': 3.0,
                'closed': 1000.0,
            },
        },
    ]
    patch_raw_stat_lines_backlog(result=stat_lines_backlog)

    await cbox.post('/v1/lines/info/', data=data)
    assert cbox.status == 200
    assert cbox.body_data == expected_answer
