from aiohttp import web
import pytest

from chatterbox import constants
from test_chatterbox import plugins


EATS_EATER_META_ADD_TAG_URL = '/v1/eaters/tags/add'
EATS_EATER_META_DEL_TAG_URL = '/v1/eaters/tags/delete'


@pytest.mark.parametrize(
    'comment, expected_comment, tag',
    [
        (
            'Hello! Ok, The courier will be wearing a foil cap '
            'all the time he is coming to you!'
            '{{eats_add_tag_eater:bizarre}}',
            'Hello! Ok, The courier will be wearing a foil cap '
            'all the time he is coming to you!',
            'bizarre',
        ),
        (
            'Hello! We are glad to welcome you to the club'
            '{{eats_add_tag_eater:top100}}',
            'Hello! We are glad to welcome you to the club',
            'top100',
        ),
    ],
)
async def test_add_eater_tag_green(
        cbox: plugins.CboxWrap,
        mock_eats_eater_meta,
        auth_data: dict,
        comment: str,
        expected_comment: str,
        tag: str,
):
    comment_processor = cbox.app.comment_processor
    task_data = {'task_id': '1', 'eater_id': '123'}

    @mock_eats_eater_meta(EATS_EATER_META_ADD_TAG_URL)
    def _mock_add_eater_tag(request):
        assert request.json['tag'] == tag
        return {'status': 'ok'}

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == {'add_eater_tag'}
    assert processing_info.operations_log == ['Eater tag was added']


@pytest.mark.parametrize(
    'comment, expected_comment, tag',
    [
        (
            'Ah, it was just a joke){{eats_del_tag_eater:bizarre}}',
            'Ah, it was just a joke)',
            'bizarre',
        ),
        (
            'Unfortunately, we have to exclude you'
            '{{eats_del_tag_eater:top100}}',
            'Unfortunately, we have to exclude you',
            'top100',
        ),
    ],
)
async def test_del_eater_tag_green(
        cbox: plugins.CboxWrap,
        mock_eats_eater_meta,
        auth_data: dict,
        comment: str,
        expected_comment: str,
        tag: str,
):
    comment_processor = cbox.app.comment_processor
    task_data = {'task_id': '1', 'eater_id': '123'}

    @mock_eats_eater_meta(EATS_EATER_META_DEL_TAG_URL)
    def _mock_del_eater_tag(request):
        assert request.json['tag'] == tag
        return {'status': 'ok'}

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == {'del_eater_tag'}
    assert processing_info.operations_log == ['Eater tag was deleted']


@pytest.mark.parametrize(
    'comment, eater_id, eats_eater_meta_response, error',
    [
        (
            'Hello! Bye bye! {{eats_add_tag_eater:some_tag}}',
            None,
            None,
            'No eater_id in task',
        ),
        (
            'Hello! Bye bye! {{eats_add_tag_eater:some_tag}}',
            '-1',
            {
                'status': 400,
                'response': {
                    'code': 'eater_not_found',
                    'message': 'Eater with id -1 not found',
                },
            },
            'Error while adding eater tag',
        ),
        (
            'Hello! {{eats_add_tag_eater:}}',
            None,
            None,
            'Cant apply macro: unknown templates',
        ),
        (
            'Hello! Bye bye! {{eats_add_tag_eater:100}}',
            None,
            None,
            'Cant apply macro: unknown templates',
        ),
    ],
)
async def test_add_eater_tag_red(
        cbox: plugins.CboxWrap,
        mock_eats_eater_meta,
        auth_data: dict,
        comment: str,
        eater_id: str,
        eats_eater_meta_response: dict,
        error: str,
):
    comment_processor = cbox.app.comment_processor
    task_data = {'task_id': '1', 'eater_id': eater_id}

    @mock_eats_eater_meta(EATS_EATER_META_ADD_TAG_URL)
    def _mock_add_eater_tag(request):
        return web.json_response(
            eats_eater_meta_response['response'],
            status=eats_eater_meta_response['status'],
        )

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == comment
    assert processing_info.error
    assert not processing_info.succeed_operations
    assert processing_info.operations_log == [error]


@pytest.mark.parametrize(
    'comment, eater_id, eats_eater_meta_response, error',
    [
        (
            'Hello! Bye bye! {{eats_del_tag_eater:some_tag}}',
            None,
            None,
            'No eater_id in task',
        ),
        (
            'Hello! Bye bye! {{eats_del_tag_eater:some_tag}}',
            '-1',
            {
                'status': 400,
                'response': {
                    'code': 'eater_not_found',
                    'message': 'Eater with id -1 not found',
                },
            },
            'Error while deleting eater tag',
        ),
        (
            'Hello! {{eats_del_tag_eater:}}',
            None,
            None,
            'Cant apply macro: unknown templates',
        ),
        (
            'Hello! Bye bye! {{eats_del_tag_eater:100}}',
            None,
            None,
            'Cant apply macro: unknown templates',
        ),
    ],
)
async def test_del_eater_tag_red(
        cbox: plugins.CboxWrap,
        mock_eats_eater_meta,
        auth_data: dict,
        comment: str,
        eater_id: str,
        eats_eater_meta_response: dict,
        error: str,
):
    comment_processor = cbox.app.comment_processor
    task_data = {'task_id': '1', 'eater_id': eater_id}

    @mock_eats_eater_meta(EATS_EATER_META_DEL_TAG_URL)
    def _mock_del_eater_tag(request):
        return web.json_response(
            eats_eater_meta_response['response'],
            status=eats_eater_meta_response['status'],
        )

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == comment
    assert processing_info.error
    assert not processing_info.succeed_operations
    assert processing_info.operations_log == [error]
