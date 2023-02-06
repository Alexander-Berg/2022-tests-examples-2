import pytest

from order_notify.stq import suggest_userplace

TRANSLATIONS = {
    'order_notify.suggest_userplace.title': {'ru': 'suggest userplace title'},
    'order_notify.suggest_userplace.text': {'ru': 'suggest userplace text'},
}


@pytest.mark.config(DEEPLINK_PREFIX={'brand': 'brand_prefix'})
@pytest.mark.translations(notify=TRANSLATIONS)
async def test_send_notification(stq3_context, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        expected_request = {
            'intent': 'taxi_suggest_userplace',
            'user': 'user_1',
            'locale': '',  # not sent for push notifications
            'meta': {'order_id': 'order_1'},
            'data': {
                'payload': {
                    'deeplink': (
                        'brand_prefix://savetofavorites?lat=56.4545&'
                        'lon=37.234&full_text=full%20text&short_text='
                        'short%20text&available_types=work&'
                        'available_types=other'
                    ),
                    'text': 'suggest userplace text',
                    'title': 'suggest userplace title',
                    'extra': {
                        'id': '00000000000040008000000000000000',
                        'order_id': 'order_1',
                    },
                },
            },
        }
        assert request.json == expected_request
        return {}

    await suggest_userplace.task(
        context=stq3_context,
        order_id='order_1',
        user_id='user_1',
        locale='ru',
        completion_point=[37.234, 56.4545],
        full_text='full text',
        short_text='short text',
        available_types=['work', 'other'],
        brand='brand',
    )
    assert _ucommunications_handler.times_called == 1


@pytest.mark.config(DEEPLINK_PREFIX={'yataxi': 'yataxi_prefix'})
@pytest.mark.translations(notify=TRANSLATIONS)
async def test_ucommunications_error(stq3_context, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        return mockserver.make_response(
            status=500, json={'code': 'SOME_ERROR', 'message': 'some error'},
        )

    await suggest_userplace.task(
        context=stq3_context,
        order_id='order_1',
        user_id='user_1',
        locale='ru',
        completion_point=[37.234, 56.4545],
        full_text='full_text',
        short_text='short_text',
        available_types=['work', 'other'],
        brand='yataxi',
    )
    assert _ucommunications_handler.times_called == 3  # retries


@pytest.mark.translations(notify=TRANSLATIONS)
async def test_bad_completion_point(stq3_context, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        pass

    try:
        await suggest_userplace.task(
            context=stq3_context,
            order_id='order_1',
            user_id='user_1',
            locale='ru',
            completion_point=[37.234, 56.4545, 12.234],
            full_text='full_text',
            short_text='short_text',
            available_types=['work', 'other'],
            brand='yataxi',
        )
    except suggest_userplace.BadCompletionPoint:
        pass
    assert _ucommunications_handler.times_called == 0


@pytest.mark.translations(notify=TRANSLATIONS)
async def test_brand_with_no_deeplink_prefix(stq3_context, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        pass

    try:
        await suggest_userplace.task(
            context=stq3_context,
            order_id='order_1',
            user_id='user_1',
            locale='ru',
            completion_point=[37.234, 56.4545, 12.234],
            full_text='full_text',
            short_text='short_text',
            available_types=['work', 'other'],
            brand='some_brand',
        )
    except suggest_userplace.NoDeeplinkPrefix:
        pass
    assert _ucommunications_handler.times_called == 0
