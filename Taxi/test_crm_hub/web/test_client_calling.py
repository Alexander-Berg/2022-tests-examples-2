import hashlib

import pytest

from generated.clients import ucommunications

from crm_hub.logic import idempotency
from crm_hub.logic import retry


@pytest.mark.parametrize(
    'max_attempts, times_called, status',
    [(1, 1, 409), (2, 2, 409), (3, 3, 409), (4, 4, 409), (5, 1, 200)],
)
async def test_retries(
        web_context, mockserver, max_attempts, times_called, status,
):
    @mockserver.json_handler('/ucommunications/user/notification/bulk-push')
    async def _bulk_push(request):
        return mockserver.make_response(
            status=status, json={'code': 'code', 'message': 'message'},
        )

    client = web_context.clients.ucommunications

    retry_settings = dict(max_attempts=max_attempts, delay_ms=100)

    retry_exceptions = (
        ucommunications.UserNotificationBulkPushPost409,
        ucommunications.ClientResponse,
    )

    error_exceptions = (
        ucommunications.UserNotificationBulkPushPost400,
        ucommunications.UserNotificationBulkPushPost404,
        ucommunications.UserNotificationBulkPushPost500,
        ucommunications.UserNotificationBulkPushPost502,
    )

    if status != 200:
        with pytest.raises(retry.TooManyRetries):
            await retry.retry_client(
                client=client.user_notification_bulk_push_post,
                retry_settings=retry_settings,
                retry_exceptions=retry_exceptions,
                error_exceptions=error_exceptions,
                x_idempotency_token='idempotency_token',
                body=None,
            )
    else:
        await retry.retry_client(
            client=client.user_notification_bulk_push_post,
            retry_settings=retry_settings,
            retry_exceptions=retry_exceptions,
            error_exceptions=error_exceptions,
            x_idempotency_token='idempotency_token',
            body=None,
        )

    assert _bulk_push.times_called == times_called


@pytest.mark.parametrize(
    'campaign_id, group_id, users, columns, result',
    [
        (1, 1, [{'a': 'a1'}], ['a'], '11a1a1'),
        (2, 2, [{'a': 'a1'}, {'a': 'a2'}], ['a'], '22a1a2'),
        (3, 3, [{'b': 'b1'}, {'b': 'b2'}, {'b': 'b3'}], ['b'], '33b1b3'),
        (
            4,
            4,
            [{'a': 'a1', 'b': 'b1'}, {'a': 'a2', 'b': 'b2'}],
            ['a', 'b'],
            '44a1b1a2b2',
        ),
    ],
)
async def test_idempotency_token_creation(
        campaign_id, group_id, users, columns, result,
):
    token = idempotency.get_communication_token(
        campaign_id=campaign_id,
        group_id=group_id,
        entities=users,
        key_columns=columns,
    )

    assert token == hashlib.md5(result.encode()).hexdigest()
