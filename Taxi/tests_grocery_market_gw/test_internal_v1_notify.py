import pytest

NOTIFICATION_SUBTYPE = 'PUSH_STORE_LAVKA'


@pytest.mark.parametrize('push_title', ['Push title', None])
async def test_basic(taxi_grocery_market_gw, mock_market_utils, push_title):
    push_title_check_field = {}
    push_title_request_field = {}
    yandex_uid = '123456'
    idempotency_token = 'user_token'
    translated_push_message = 'Push Message'
    push_deeplink = 'yamarket://lavka/deeplink'

    if push_title is not None:
        push_title_check_field = {'push_template_param_title': push_title}
        push_title_request_field = {'translated_push_title': push_title}

    mock_market_utils.check_api_add_request(
        check_request_body={
            'data': {
                'push_data_store_push_deeplink_v1': push_deeplink,
                'push_template_param_message': translated_push_message,
                **push_title_check_field,
            },
            'notificationSubtype': 'PUSH_STORE_LAVKA',
            'uid': int(yandex_uid),
        },
        response_code=201,
    )

    response = await taxi_grocery_market_gw.post(
        '/internal/market-gw/v1/notify',
        json={
            'yandex_uid': yandex_uid,
            'idempotency_token': idempotency_token,
            **push_title_request_field,
            'translated_push_message': translated_push_message,
            'push_deeplink': push_deeplink,
        },
    )

    assert response.status == 200
    assert mock_market_utils.api_event_add_called == 1


async def test_406_on_400_from_market(
        taxi_grocery_market_gw, mock_market_utils,
):
    yandex_uid = '123456'
    idempotency_token = 'user_token'
    translated_push_title = 'Push title'
    translated_push_message = 'Push Message'
    push_deeplink = 'yamarket://lavka/deeplink'

    mock_market_utils.check_api_add_request(
        check_request_body={
            'data': {
                'push_data_store_push_deeplink_v1': push_deeplink,
                'push_template_param_message': translated_push_message,
                'push_template_param_title': translated_push_title,
            },
            'notificationSubtype': 'PUSH_STORE_LAVKA',
            'uid': int(yandex_uid),
        },
        response_code=400,
    )

    response = await taxi_grocery_market_gw.post(
        '/internal/market-gw/v1/notify',
        json={
            'yandex_uid': yandex_uid,
            'idempotency_token': idempotency_token,
            'translated_push_title': translated_push_title,
            'translated_push_message': translated_push_message,
            'push_deeplink': push_deeplink,
        },
    )

    assert response.status == 406
    assert mock_market_utils.api_event_add_called == 1
