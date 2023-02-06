# pylint: disable=protected-access
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    ('sender_id', 'attachment_id'),
    (
        ('5b4f5059779fb332fcc26152', 'attachment_id1'),
        ('5b4f5059779fb332fcc26153', 'attachment_id2'),
    ),
)
async def test_resize(
        stq3_context: stq_context.Context,
        patch_resizer,
        mds_s3_client,
        sender_id: str,
        attachment_id: str,
):
    gen_url, get_file = patch_resizer(
        sender_id=sender_id, attachment_id=attachment_id, file=b'tst_file',
    )
    await stq_task.generate_preview(stq3_context, sender_id, attachment_id)
    assert gen_url.has_calls
    assert get_file.calls

    mds_file_name = '{}_{}_preview'.format(sender_id, attachment_id)
    assert mds_file_name in mds_s3_client._storage
    assert mds_s3_client._storage[mds_file_name] == b'tst_file'
