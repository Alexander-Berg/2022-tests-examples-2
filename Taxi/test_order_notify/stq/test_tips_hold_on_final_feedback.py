import pytest

from order_notify.stq import tips_hold_on_final_feedback


TRANSLATIONS_NOTIFY = {
    'order_notify.tips_hold_on_final_feedback.title': {
        'ru': 'tips hold title',
    },
    'order_notify.tips_hold_on_final_feedback.text': {'ru': 'tips hold text'},
}


@pytest.mark.translations(notify=TRANSLATIONS_NOTIFY)
async def test_send_notification(stq3_context, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        expected_request = {
            'intent': 'taxi_tips_hold_on_final_feedback',
            'user': 'user_1',
            'locale': '',  # not sent for push notifications
            'meta': {'order_id': 'order_1'},
            'data': {
                'payload': {
                    'title': 'tips hold title',
                    'text': 'tips hold text',
                    'extra': {
                        'id': '00000000000040008000000000000000',
                        'order_id': 'order_1',
                    },
                },
            },
        }
        assert request.json == expected_request
        return {}

    await tips_hold_on_final_feedback.task(
        context=stq3_context,
        order_id='order_1',
        user_id='user_1',
        locale='ru',
    )
    assert _ucommunications_handler.times_called == 1


@pytest.mark.translations(notify=TRANSLATIONS_NOTIFY)
async def test_ucommunications_error(stq3_context, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        return mockserver.make_response(
            status=500, json={'code': 'SOME_ERROR', 'message': 'some error'},
        )

    await tips_hold_on_final_feedback.task(
        context=stq3_context,
        order_id='order_1',
        user_id='user_1',
        locale='ru',
    )
    assert _ucommunications_handler.times_called == 3  # retries
