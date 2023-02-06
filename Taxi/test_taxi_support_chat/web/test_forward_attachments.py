# pylint: disable=protected-access
import bson
import pytest

from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    (
        'chat_id',
        'messages_id',
        'old_owner_id',
        'attachments_id',
        'expected_attachments_id',
    ),
    (
        (
            bson.ObjectId('5b436ca8779fb3302cc784ba'),
            ['message_11'],
            'some_user_id',
            ['attachment_id'],
            [
                '5b4f5059779fb332fcc26152_attachment_id',
                '5b4f5059779fb332fcc26152_attachment_id_preview',
            ],
        ),
        (
            bson.ObjectId('5b436ece779fb3302cc784bb'),
            ['message_21', 'message_23'],
            '12345',
            ['attachment_id_1', 'attachment_id_2', 'attachment_id_3'],
            [
                '5b4f5092779fb332fcc26153_attachment_id_1',
                '5b4f5092779fb332fcc26153_attachment_id_1_preview',
                '5b4f5092779fb332fcc26153_attachment_id_2',
                '5b4f5092779fb332fcc26153_attachment_id_2_preview',
                '5b4f5092779fb332fcc26153_attachment_id_3',
                '5b4f5092779fb332fcc26153_attachment_id_3_preview',
            ],
        ),
    ),
)
async def test_forward_attachments(
        web_context,
        mds_s3_client,
        chat_id,
        messages_id,
        old_owner_id,
        attachments_id,
        expected_attachments_id,
):
    for attachment_id in attachments_id:
        key = '%s_%s' % (old_owner_id, attachment_id)
        preview_key = '%s_%s_preview' % (old_owner_id, attachment_id)
        mds_s3_client._storage[key] = b'test'
        mds_s3_client._storage[preview_key] = b'test'

    await stq_task.forward_attachments(
        web_context, old_owner_id, chat_id, messages_id,
    )
    for attachment_id in expected_attachments_id:
        assert attachment_id in mds_s3_client._storage
