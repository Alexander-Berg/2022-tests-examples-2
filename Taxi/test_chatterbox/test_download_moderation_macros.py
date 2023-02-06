# pylint: disable=invalid-name, unused-variable
import uuid

import pytest

from chatterbox.crontasks import download_macros_from_moderation


def _dummy_uuid4():
    return uuid.UUID(int=0, version=4)


def dummy_secret(*args, **kwargs):
    return '00000000000040008000000000000000'


@pytest.mark.parametrize(
    'data',
    [
        ([]),
        (
            [
                {
                    'project_id_id': 1,
                    'id': 5948,
                    'title': 'Платная отмена ₽',
                    'text': 'Текст ₽',
                    'status': 'solved',
                    'tags': [
                        'test_tag',
                        'закрыто_на_модерации',
                        'после_модерации',
                    ],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5949,
                    'title': 'Платная отмена ₽',
                    'text': 'Текст ₽',
                    'status': 'solved',
                    'tags': [
                        'test_tag',
                        'закрыто_на_модерации',
                        'после_модерации',
                    ],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
            ]
        ),
    ],
)
async def test_download_moderation_macros_too_less(
        cbox_context,
        loop,
        patch_aiohttp_session,
        monkeypatch,
        response_mock,
        data,
):
    @patch_aiohttp_session('http://support-api.taxi.tst.yandex.net', 'GET')
    def patched_request(method, url, **kwargs):
        assert method == 'get'
        assert 'api/macros' in url
        assert kwargs['headers'] == {'Authorization': 'Token test_token'}
        assert kwargs['params'] == {'project_id': '1', 'type_macros': 'dm'}
        return response_mock(json=data)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    with pytest.raises(download_macros_from_moderation.TooLessRecordsError):
        await download_macros_from_moderation.do_stuff(cbox_context, loop)


@pytest.mark.parametrize(
    'data',
    [
        (
            [
                {
                    'project_id_id': 1,
                    'id': 5948,
                    'title': 'Платная отмена ₽',
                    'text': 'Текст ₽ {{ticket.ticket_field_123}}',
                    'status': 'solved',
                    'tags': [
                        'test_tag',
                        'закрыто_на_модерации',
                        'после_модерации',
                    ],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
            ]
        ),
    ],
)
async def test_download_moderation_unknown_field(
        cbox_context,
        loop,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        data,
):
    @patch_aiohttp_session('http://support-api.taxi.tst.yandex.net', 'GET')
    def patched_request(method, url, **kwargs):
        assert method == 'get'
        assert 'api/macros' in url
        assert kwargs['headers'] == {'Authorization': 'Token test_token'}
        assert kwargs['params'] == {'project_id': '1', 'type_macros': 'dm'}
        return response_mock(json=data)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    with pytest.raises(download_macros_from_moderation.UnknownTicketField):
        await download_macros_from_moderation.do_stuff(cbox_context, loop)


@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            [
                {
                    'project_id_id': 1,
                    'id': 5948,
                    'title': 'Платная отмена ₽',
                    'text': 'Текст ₽',
                    'status': 'solved',
                    'tags': [
                        'Te,st_t\ta g a\rb\nc',
                        'закрыто_на_модерации',
                        'после_модерации',
                    ],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5949,
                    'title': 'Бесплатная отмена',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1', 'Кириллица'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5950,
                    'title': 'Бесплатная отмена',
                    'text': (
                        'Текст {{promo}} ₽' ' {{ticket.ticket_field_35941509}}'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1', 'test_tag2'],
                    'sms_flag': False,
                    'visible': True,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5951,
                    'title': 'Бесплатная отмена',
                    'text': 'Текст {{promo}} {{ticket.ticket_field_35941509}}',
                    'status': 'solved',
                    'tags': ['test_tag1', 'test_tag2'],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'visible': False,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
            ],
            [
                {
                    '_id': 5948,
                    'title': 'Платная отмена ₽',
                    'comment': 'Текст ₽',
                    'tags': ['te_st_t_a_g_abc'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'macro',
                    'moderation_type': 'dm',
                },
                {
                    '_id': 5949,
                    'title': 'Бесплатная отмена',
                    'comment': (
                        'Текст {{promo:100}} {{meta:user_email}} '
                        '{{currency}}'
                    ),
                    'tags': ['test_tag1', 'кириллица'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'macro',
                    'moderation_type': 'dm',
                },
                {
                    '_id': 5950,
                    'title': 'Бесплатная отмена',
                    'comment': 'Текст {{promo}} ₽ {{meta:payment_type}}',
                    'tags': ['test_tag1', 'test_tag2'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'macro',
                    'moderation_type': 'dm',
                },
            ],
        ),
    ],
)
async def test_download_moderation_macros(
        cbox_context,
        loop,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        data,
        expected_result,
):
    @patch_aiohttp_session('http://support-api.taxi.tst.yandex.net', 'GET')
    def patched_request(method, url, **kwargs):
        assert method == 'get'
        assert 'api/macros' in url
        assert kwargs['headers'] == {'Authorization': 'Token test_token'}
        assert kwargs['params'] == {'project_id': '1', 'type_macros': 'dm'}
        return response_mock(json=data)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    await download_macros_from_moderation.do_stuff(cbox_context, loop)

    macros = await cbox_context.data.db.support_macros.find().to_list(None)
    assert sorted(macros, key=lambda item: item['_id']) == expected_result


@pytest.mark.config(
    SUPPORT_MODERATION_PARAMS=[
        {
            'project_id': '1',
            'type': 'dm',
            'lines': ['first', 'vip', 'urgent'],
            'output_type': 'macro',
        },
        {'project_id': '2', 'type': 'sms', 'output_type': 'macro'},
    ],
)
@pytest.mark.parametrize(
    'data_1, data_2, expected_result',
    [
        (
            [
                {
                    'project_id_id': 1,
                    'id': 5948,
                    'title': 'Платная отмена ₽',
                    'text': 'Текст ₽',
                    'status': 'solved',
                    'tags': [
                        'test_tag',
                        'закрыто_на_модерации',
                        'после_модерации',
                    ],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5949,
                    'title': 'Бесплатная отмена',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
            ],
            [
                {
                    'project_id_id': 2,
                    'id': 5950,
                    'title': 'Бесплатная отмена',
                    'text': (
                        'Текст {{promo}} ₽' ' {{ticket.ticket_field_35941509}}'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1', 'test_tag2'],
                    'sms_flag': False,
                    'visible': True,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'sms',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 2,
                    'id': 5951,
                    'title': 'Бесплатная отмена',
                    'text': 'Текст {{promo}} {{ticket.ticket_field_35941509}}',
                    'status': 'solved',
                    'tags': ['test_tag1', 'test_tag2'],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'visible': False,
                    'type_macros': 'sms',
                    'hide_macros': True,
                    'send_sms': False,
                },
            ],
            [
                {
                    '_id': 5948,
                    'title': 'Платная отмена ₽',
                    'comment': 'Текст ₽',
                    'tags': ['test_tag'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'macro',
                    'moderation_type': 'dm',
                },
                {
                    '_id': 5949,
                    'title': 'Бесплатная отмена',
                    'comment': (
                        'Текст {{promo:100}} {{meta:user_email}} '
                        '{{currency}}'
                    ),
                    'tags': ['test_tag1'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'macro',
                    'moderation_type': 'dm',
                },
                {
                    '_id': 5950,
                    'title': 'Бесплатная отмена',
                    'comment': 'Текст {{promo}} ₽ {{meta:payment_type}}',
                    'tags': ['test_tag1', 'test_tag2'],
                    'lines': [],
                    'type': 'macro',
                    'moderation_type': 'sms',
                },
            ],
        ),
    ],
)
async def test_download_moderation_many_params(
        cbox_context,
        loop,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        data_1,
        data_2,
        expected_result,
):
    @patch_aiohttp_session('http://support-api.taxi.tst.yandex.net', 'GET')
    def patched_request(method, url, **kwargs):
        assert method == 'get'
        assert 'api/macros' in url
        assert kwargs['headers'] == {'Authorization': 'Token test_token'}
        assert kwargs['params'] in [
            {'project_id': '1', 'type_macros': 'dm'},
            {'project_id': '2', 'type_macros': 'sms'},
        ]
        if kwargs['params']['type_macros'] == 'dm':
            return response_mock(json=data_1)
        return response_mock(json=data_2)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    await download_macros_from_moderation.do_stuff(cbox_context, loop)

    macros = await cbox_context.data.db.support_macros.find().to_list(None)
    assert sorted(macros, key=lambda item: item['_id']) == expected_result


@pytest.mark.config(
    SUPPORT_MODERATION_PARAMS=[
        {
            'project_id': '1',
            'type': 'dm',
            'lines': ['first', 'vip', 'urgent'],
            'output_type': 'theme',
        },
    ],
)
@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            [
                {
                    'project_id_id': 1,
                    'id': 5951,
                    'title': 'Тема 1',
                    'text': 'Текст ₽',
                    'status': 'solved',
                    'tags': [
                        'test_tag',
                        'закрыто_на_модерации',
                        'после_модерации',
                    ],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5952,
                    'title': 'Тема 1::Подтема 1',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5958,
                    'title': 'Тема 1::Подтема 1::Подподтема 1',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                    'visible': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5953,
                    'title': 'Тема 1::Подтема 2',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5954,
                    'title': 'Тема 1::Подтема 3',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5955,
                    'title': 'Тема 1::Подтема 1::Подподтема 1',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5956,
                    'title': 'Тема 1::Подтема 1::Подподтема 2',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5957,
                    'title': 'Тема 2',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
            ],
            [
                {
                    '_id': 5951,
                    'title': 'Тема 1',
                    'root': True,
                    'node_name': 'Тема 1',
                    'tags': ['test_tag'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'theme',
                    'moderation_type': 'dm',
                    'child_themes': [5952, 5953, 5954],
                },
                {
                    '_id': 5952,
                    'title': 'Тема 1::Подтема 1',
                    'root': False,
                    'node_name': 'Подтема 1',
                    'tags': ['test_tag1'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'theme',
                    'moderation_type': 'dm',
                    'child_themes': [5955, 5956],
                },
                {
                    '_id': 5953,
                    'title': 'Тема 1::Подтема 2',
                    'root': False,
                    'node_name': 'Подтема 2',
                    'tags': ['test_tag1'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'theme',
                    'moderation_type': 'dm',
                    'child_themes': [],
                },
                {
                    '_id': 5954,
                    'title': 'Тема 1::Подтема 3',
                    'root': False,
                    'node_name': 'Подтема 3',
                    'tags': ['test_tag1'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'theme',
                    'moderation_type': 'dm',
                    'child_themes': [],
                },
                {
                    '_id': 5955,
                    'title': 'Тема 1::Подтема 1::Подподтема 1',
                    'root': False,
                    'node_name': 'Подподтема 1',
                    'tags': ['test_tag1'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'theme',
                    'moderation_type': 'dm',
                    'child_themes': [],
                },
                {
                    '_id': 5956,
                    'title': 'Тема 1::Подтема 1::Подподтема 2',
                    'root': False,
                    'node_name': 'Подподтема 2',
                    'tags': ['test_tag1'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'theme',
                    'moderation_type': 'dm',
                    'child_themes': [],
                },
                {
                    '_id': 5957,
                    'title': 'Тема 2',
                    'root': True,
                    'node_name': 'Тема 2',
                    'tags': ['test_tag1'],
                    'lines': ['first', 'vip', 'urgent'],
                    'type': 'theme',
                    'moderation_type': 'dm',
                    'child_themes': [],
                },
            ],
        ),
    ],
)
async def test_download_moderation_themes(
        cbox_context,
        loop,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        data,
        expected_result,
):
    @patch_aiohttp_session('http://support-api.taxi.tst.yandex.net', 'GET')
    def patched_request(method, url, **kwargs):
        assert method == 'get'
        assert 'api/macros' in url
        assert kwargs['headers'] == {'Authorization': 'Token test_token'}
        assert kwargs['params'] == {'project_id': '1', 'type_macros': 'dm'}
        return response_mock(json=data)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    await download_macros_from_moderation.do_stuff(cbox_context, loop)

    macros = await cbox_context.data.db.support_macros.find().to_list(None)
    assert sorted(macros, key=lambda item: item['_id']) == expected_result
    for item in macros:
        for child in item['child_themes']:
            for item_child in macros:
                if item_child['_id'] == child:
                    assert item_child.get('visible', True) is True
                    break


@pytest.mark.config(
    SUPPORT_MODERATION_PARAMS=[
        {
            'project_id': '1',
            'type': 'dm',
            'lines': ['first', 'vip', 'urgent'],
            'output_type': 'theme',
        },
    ],
)
@pytest.mark.parametrize(
    'data, count',
    [
        (
            [
                {
                    'project_id_id': 1,
                    'id': 5954,
                    'title': 'Тема 1::Подтема 3',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5951,
                    'title': 'Тема 2',
                    'text': 'Текст ₽',
                    'status': 'solved',
                    'tags': [
                        'test_tag',
                        'закрыто_на_модерации',
                        'после_модерации',
                    ],
                    'sms_flag': False,
                    'promocode': 0,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5952,
                    'title': 'Тема 3',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
                {
                    'project_id_id': 1,
                    'id': 5953,
                    'title': 'Тема 4',
                    'text': (
                        'Текст {{promo}} {{ticket.ticket_field_45557125}}' ' ₽'
                    ),
                    'status': 'solved',
                    'tags': ['test_tag1'],
                    'sms_flag': False,
                    'promocode': 100,
                    'clicks': 114,
                    'type_macros': 'dm',
                    'hide_macros': True,
                    'send_sms': False,
                },
            ],
            3,
        ),
        (
            [
                {
                    'project_id_id': 1,
                    'id': 5951,
                    'title': 'Тема 1::Подтема 1::Подподтема 1',
                    'text': 'test',
                    'tags': ['test_tag1'],
                },
                {
                    'project_id_id': 1,
                    'id': 5952,
                    'title': 'Тема 1::Подтема 1',
                    'text': 'test',
                    'tags': ['test_tag1'],
                },
                {
                    'project_id_id': 1,
                    'id': 5953,
                    'title': 'Тема 3',
                    'text': 'test',
                    'tags': ['test_tag1'],
                },
                {
                    'project_id_id': 1,
                    'id': 5954,
                    'title': 'Тема 4',
                    'text': 'test',
                    'tags': ['test_tag1'],
                },
                {
                    'project_id_id': 1,
                    'id': 5955,
                    'title': 'Тема 5',
                    'text': 'test',
                    'tags': ['test_tag1'],
                },
            ],
            3,
        ),
    ],
)
async def test_download_moderation_macros_parent(
        cbox_context,
        loop,
        patch_aiohttp_session,
        monkeypatch,
        response_mock,
        data,
        count,
):
    @patch_aiohttp_session('http://support-api.taxi.tst.yandex.net', 'GET')
    def patched_request(method, url, **kwargs):
        assert method == 'get'
        assert 'api/macros' in url
        assert kwargs['headers'] == {'Authorization': 'Token test_token'}
        assert kwargs['params'] == {'project_id': '1', 'type_macros': 'dm'}
        return response_mock(json=data)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
    monkeypatch.setattr(
        'taxi.opentracing.tracer.generate_span_id', dummy_secret,
    )

    with pytest.raises(download_macros_from_moderation.UnknownThemeParent):
        await download_macros_from_moderation.do_stuff(cbox_context, loop)
    assert await cbox_context.data.db.support_macros.find().count() == count
