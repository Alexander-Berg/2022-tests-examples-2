# pylint: disable=redefined-outer-name
import pytest

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.fixture
def mock_generate_key_data(mockserver):
    @mockserver.json_handler(
        '/eats-restapp-support-chat/internal/support_chat/'
        'v1/generate_key_data',
    )
    def _dummy_restapp(request):
        if request.query['partner_id'] == '000':
            return mockserver.make_response('bad request', status=400)
        return {'data': '123456'}

    return _dummy_restapp


@pytest.mark.parametrize(
    (
        'task_data',
        'comment',
        'expected_comment',
        'expected_succeed_operations',
        'expected_operations_log',
    ),
    [
        (
            {
                'task_id': '1',
                'restapp_author': '123',
                'restapp_place_id': '456',
            },
            'Hello! http://restapp/?token={{restapp_token}}',
            'Hello! http://restapp/?token=123456',
            {'restapp_token'},
            ['Restap token obtained'],
        ),
        (
            {
                'task_id': '1',
                'restapp_author': '000',
                'restapp_place_id': '456',
            },
            'Hello! http://restapp/?token={{restapp_token}}',
            'Hello! http://restapp/?token={{restapp_token}}',
            set(),
            [
                'Cannot fetch restapp token: eats-restapp-support-chat '
                'responded with code 400',
            ],
        ),
    ],
)
async def test_restapp(
        cbox: conftest.CboxWrap,
        mock_generate_key_data,
        auth_data,
        task_data,
        comment,
        expected_comment,
        expected_succeed_operations,
        expected_operations_log,
):
    comment_processor = cbox.app.comment_processor

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == expected_succeed_operations
    assert processing_info.operations_log == expected_operations_log
    restapp_call = mock_generate_key_data.next_call()
    assert dict(restapp_call['request'].query) == {
        'partner_id': task_data['restapp_author'],
        'place_id': task_data['restapp_place_id'],
    }
