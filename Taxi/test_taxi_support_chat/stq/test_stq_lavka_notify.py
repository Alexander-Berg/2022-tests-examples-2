# pylint: disable=redefined-outer-name,unused-variable
import bson
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    ('chat_id', 'expected_store_id', 'count_change'),
    [
        (bson.ObjectId('5a436ca8779fb3302cc784ea'), 'lavka_store_id', 2),
        (bson.ObjectId('5a436ca8779fb3302cc222ea'), 'lavka_store_id_2', -5),
    ],
)
async def test_task(
        mockserver,
        stq3_context: stq_context.Context,
        chat_id,
        expected_store_id,
        count_change,
):
    token = 'idempotency_token'

    @mockserver.json_handler(
        '/grocery-wms/api/external/stores/v1/set_messages_count',
    )
    def _mock_lavka_wms(request):
        data = request.json
        assert data['store_id'] == expected_store_id
        assert data['count_change'] == count_change
        assert data['token'] == token
        return mockserver.make_response(
            status=200, json={'code': 'OK', 'message': ''},
        )

    await stq_task.lavka_wms_notify_task(
        stq3_context, chat_id, messages_count=count_change, token=token,
    )

    assert _mock_lavka_wms.has_calls
