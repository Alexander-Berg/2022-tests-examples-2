# pylint: disable=no-self-use, too-many-arguments, redefined-outer-name
# pylint: disable=unused-variable
import bson
import pytest

from taxi.clients import tvm

from chatterbox.api import rights
from chatterbox.internal import tasks_manager
from test_chatterbox import plugins as conftest


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'chatterbox', 'dst': 'support_chat'},
        {'src': 'chatterbox', 'dst': 'messenger_chat_mirror'},
    ],
    TVM_ENABLED=True,
)
@pytest.mark.parametrize('handler', ['attachment', 'attachment_with_tvm'])
@pytest.mark.parametrize(
    'task_id, attachment_id, expected_url, expected_status',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            '8eaee405c384e7348366a27f3f60474370fba3a3',
            '/v1/chat/'
            'some_user_chat_message_id/attachment/'
            '8eaee405c384e7348366a27f3f60474370fba3a3?'
            'sender_id=superuser&sender_role=support',
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a6',
            '8eaee405c384e7348366a27f3f60474370fba3a3',
            '/api/chatterbox/download_attachment?chat_id=some_messenger_id&'
            'file_id=8eaee405c384e7348366a27f3f60474370fba3a3',
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a3',
            '8eaee405c384e7348366a27f3f60474370fba3a3',
            '/v1/chat/chat_id/attachment/'
            '8eaee405c384e7348366a27f3f60474370fba3a3?'
            'sender_id=superuser&sender_role=support',
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a4',
            '8eaee405c384e7348366a27f3f60474370fba3a3',
            '',
            404,
        ),
        (
            '5b2cae5cb2682a976914c2a5',
            '8eaee405c384e7348366a27f3f60474370fba3a3',
            '',
            400,
        ),
    ],
)
async def test_download_file(
        cbox,
        handler,
        task_id,
        attachment_id,
        expected_url,
        expected_status,
        patch,
):
    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return 'Ticket 123'

    @patch('taxi.clients.tvm.check_tvm')
    async def check_tvm(request, *args, **kwargs):
        assert request.headers['X-Ya-Service-Ticket'] == 'Ticket chatterbox'
        return tvm.CheckResult(src_service_name='developers')

    @patch('chatterbox.internal.tasks_manager.TasksManager.get_from_archive')
    async def get_from_archive(*args, **kwargs):
        if args[0] == bson.ObjectId('5b2cae5cb2682a976914c2a3'):
            return {
                '_id': bson.ObjectId('5b2cae5cb2682a976914c2a3'),
                'line': 'first',
                'type': 'chat',
                'external_id': 'chat_id',
            }
        raise tasks_manager.TaskNotFound()

    await cbox.query(
        '/v1/tasks/{}/{}/{}'.format(task_id, handler, attachment_id),
        headers={'X-Ya-Service-Ticket': 'Ticket chatterbox'},
    )
    assert cbox.status == expected_status
    if expected_status == 200:
        assert cbox.headers['X-Accel-Redirect'] == expected_url
        assert cbox.headers['X-Ya-Service-Ticket'] == 'Ticket 123'


@pytest.mark.config(
    CHATTERBOX_LINES_PERMISSIONS={
        'first': {
            'search': [{'permissions': [rights.CHATTERBOX_CLIENT_FIRST_LINE]}],
        },
    },
    TVM_ENABLED=True,
)
async def test_forbidden_without_line_permission(
        cbox: conftest.CboxWrap, patch_auth,
):
    groups = ['chatterbox_readonly']

    patch_auth(superuser=False, groups=groups)
    task_id = '5b2cae5cb2682a976914c2a1'
    attachment_id = '8eaee405c384e7348366a27f3f60474370fba3a3'

    await cbox.query(f'/v1/tasks/{task_id}/attachment/{attachment_id}')

    assert cbox.status == 403
