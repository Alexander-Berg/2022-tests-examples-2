import pytest


@pytest.fixture(name='mock_catalog_storage')
def _mock_catalog_storage(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage/'
        'v1/places/retrieve-by-ids',
    )
    def _catalog_storage(request):
        request.json['projection'].sort()
        assert request.json == {
            'place_ids': [1],
            'projection': ['address', 'brand', 'name'],
        }
        return mockserver.make_response(
            status=200,
            json={
                'not_found_place_ids': [],
                'places': [
                    {
                        'name': 'Вкусная еда',
                        'address': {
                            'city': 'Санкт-Петербург',
                            'short': 'Улица и дом',
                        },
                        'id': 1,
                        'brand': {
                            'id': 2,
                            'slug': 'brand_slug',
                            'name': 'brand_name',
                            'picture_scale_type': 'aspect_fit',
                        },
                        'revision_id': 123,
                        'updated_at': '2022-03-01T00:00:00Z',
                    },
                ],
            },
        )

    return _catalog_storage


@pytest.fixture(name='mock_feedback')
def _mock_feedback(mockserver, request, mocked_time):
    @mockserver.json_handler('/eats-feedback/internal/eats-feedback/v1/answer')
    def _feedback(request):
        assert request.json['coupon']['coupon'] == 'COUPONTYPE'
        assert request.json['coupon']['currency_code'] == ''
        assert request.json['coupon']['percent'] == 10
        assert (
            request.json['comment']
            == 'спасибо за отзыв, &lt&gtмы исправимся, вот вам скидка на заказ'
        )
        assert request.json['feedback_id'] == 1
        return mockserver.make_response(status=204, json={})

    return _feedback


@pytest.fixture(name='mock_core_restapp')
def _mock_core_restapp(mockserver, request):
    @mockserver.json_handler('/eats-core-restapp/v1/places/paired-place')
    def _core_restapp(request):
        return mockserver.make_response(status=200, json={'paired_place': 2})

    return _core_restapp


@pytest.fixture(name='mock_eats_place_subscription')
def _mock_place_subscription(mockserver, request, mocked_time):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/eats-place-subscriptions/v1/'
        'feature/enabled-for-places',
    )
    def _place_subscription(request):
        return mockserver.make_response(
            status=200,
            json={
                'feature': request.json['feature'],
                'places': {
                    'with_enabled_feature': request.json['place_ids'],
                    'with_disabled_feature': [],
                },
            },
        )

    return _place_subscription


@pytest.fixture(name='mock_eats_place_subscription_no')
def _mock_eats_place_subscription_no(mockserver, request, mocked_time):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/eats-place-subscriptions/v1/'
        'feature/enabled-for-places',
    )
    def _eats_place_subscription_no(request):
        return mockserver.make_response(
            status=200,
            json={
                'feature': request.json['feature'],
                'places': {
                    'with_disabled_feature': request.json['place_ids'],
                    'with_enabled_feature': [],
                },
            },
        )

    return _eats_place_subscription_no


@pytest.fixture(name='mock_feedback_update')
def _mock_feedback_update(mockserver, request, mocked_time):
    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/answer/update',
    )
    def _feedback_update(request):
        return mockserver.make_response(status=204, json={})

    return _feedback_update


@pytest.fixture(name='mock_core_order')
def _mock_core_order(mockserver, request):
    @mockserver.json_handler(
        '/eats-core-orders/internal-api/v1/order/ORDER_3/metainfo',
    )
    def _core_order(request):
        return {
            'order_nr': 'ORDER_3',
            'location_latitude': 60.000,
            'location_longitude': 35.000,
            'is_asap': True,
            'place_id': '1',
            'region_id': '1',
            'taxi_user_id': 'taxi112',
            'order_user_information': {
                'eater_id': '112',
                'yandex_uid': 'passport-uid-112',
                'personal_email_id': '567',
            },
        }

    return _core_order


@pytest.fixture(name='mock_get_feedbacks')
def _mock_get_feedbacks(mockserver, request):
    @mockserver.json_handler(
        '/eats-feedback/internal/eats-feedback/v1/feedbacks',
    )
    def _get_feedbacks(request):
        return {
            'count': 1,
            'feedbacks': [
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:23:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_1',
                    'predefined_comments': [
                        {'id': 15, 'title': 'Горячая еда!'},
                    ],
                    'rating': 4,
                    'eater_id': '111',
                    'feedback_answers': [
                        {
                            'answer': 'comment',
                            'answer_moderation_status': 'approved',
                            'coupon': {
                                'coupon': 'COUPON',
                                'currency_code': 'RUB',
                                'expire_at': '2022-03-08T20:59:00+00:00',
                                'limit': '1999.99',
                                'percent': 10,
                            },
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
                {
                    'actual': True,
                    'comment_status': 'raw',
                    'feedback_filled_at': '2021-02-10T09:27:00+00:00',
                    'id': 1,
                    'order_nr': 'ORDER_3',
                    'predefined_comments': [
                        {'id': 20, 'title': 'Еда была холодной'},
                    ],
                    'rating': 3,
                    'eater_id': '112',
                    'feedback_answers': [
                        {
                            'answer': 'comment2',
                            'answer_moderation_status': 'approved',
                        },
                    ],
                    'order_delivered_at': '2021-02-10T09:23:00+00:00',
                },
            ],
        }

    return _get_feedbacks


@pytest.fixture(name='mock_post_notification')
def _mock_post_notification(mockserver, request):
    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _post_notification(request):
        return mockserver.make_response(status=204, json={})

    return _post_notification


@pytest.fixture(name='mock_coupons')
def _mock_coupons(mockserver, request):
    @mockserver.json_handler('/eats-coupons/internal/generate')
    def _coupons(request):
        json = request.json
        assert json.pop('expire_at', 0) != 0
        text = json['reason']['tanker_args'][2].pop('value', '')
        assert text in (
            'спасибо за отзыв, мы исправимся, вот вам скидка на заказ',
            '',
        )
        assert json == {
            'brand_name': 'eats',
            'conditions': {'refund_type': 'percent', 'percent': 10},
            'promocode_type': 'COUPONTYPE',
            'yandex_uid': 'passport-uid-112',
            'reason': {
                'default_value': 'Промокод от ресторана',
                'tanker_args': [
                    {'key': 'name_place', 'value': 'Вкусная еда'},
                    {'key': 'address_place', 'value': 'Улица и дом'},
                    {'key': 'feedback_answer'},
                ],
                'tanker_key': 'place.feedback_answer',
            },
            'promocode_meta': {'places-ids': [1, 2]},
            'token': '1',
        }
        return mockserver.make_response(
            status=200,
            json={
                'promocode': 'PROMOCODE',
                'promocode_params': {
                    'value': 10,
                    'percent': 10,
                    'limit': 1000.00,
                    'expire_at': '2022-05-01T00:00:00Z',
                    'currency_code': 'RUB',
                },
            },
        )

    return _coupons


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_feedback_answer_happy_path(
        taxi_eats_place_rating,
        stq,
        mock_authorizer_allowed,
        mock_catalog_storage,
        mock_feedback,
        mock_eats_place_subscription,
        get_answer_log,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/answer-feedback?place_id=1',
        headers={'X-YaEda-PartnerId': '1'},
        json={
            'response': {
                'id': 1,
                'text': (
                    'спасибо за отзыв, <>мы испр'
                    'авимся, вот вам скидка на заказ'
                ),
                'coupon': {
                    'value': 10,
                    'reason': 'мы заботимся о клиентах',
                    'type': 'COUPONTYPE',
                },
            },
        },
    )

    assert response.status_code == 201
    assert stq.eats_place_rating_feedback_answer.times_called == 0

    result = get_answer_log()
    assert len(result) == 1
    assert result[0]['id'] == 1
    assert result[0]['feedback_id'] == 1
    assert result[0]['place_id'] == 1
    assert result[0]['partner_id'] == 1


@pytest.mark.experiments3(filename='exp3_eats_place_rating_false.json')
async def test_feedback_answer_no_sub(
        taxi_eats_place_rating,
        stq,
        mock_authorizer_allowed,
        mock_eats_place_subscription_no,
        get_answer_log,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/answer-feedback?place_id=1',
        headers={'X-YaEda-PartnerId': '1'},
        json={
            'response': {
                'id': 1,
                'text': (
                    'спасибо за отзыв, мы исправимся, вот вам скидка на заказ'
                ),
                'coupon': {
                    'value': 10,
                    'reason': 'мы заботимся о клиентах',
                    'type': 'COUPONTYPE',
                },
            },
        },
    )

    assert response.status_code == 400
    assert stq.eats_place_rating_feedback_answer.times_called == 0
    result = get_answer_log()
    assert not result


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_feedback_answer_stq(
        stq_runner,
        mock_catalog_storage,
        mock_feedback_update,
        mock_core_order,
        mock_coupons,
        mock_post_notification,
        mock_core_restapp,
):
    await stq_runner.eats_place_rating_feedback_answer.call(
        task_id='fake_task',
        kwargs={
            'answer': {
                'coupon': {
                    'reason': 'мы заботимся о клиентах',
                    'type': 'COUPONTYPE',
                    'value': 10,
                    'is_percent': True,
                },
                'feedback_id': 1,
                'answer_id': 1,
                'text': (
                    'спасибо за отзыв, мы исправимся, вот вам скидка на заказ'
                ),
            },
            'place_id': 1,
            'partner_id': 1,
            'eater_id': '112',
            'order_nr': 'ORDER_3',
        },
    )

    assert mock_catalog_storage.times_called == 1
    assert mock_feedback_update.times_called == 1
    request = mock_feedback_update.next_call()['request'].json
    request.pop('answer_status_code', 0)
    assert request == {
        'answer_id': 1,
        'coupon': {
            'coupon': 'PROMOCODE',
            'currency_code': 'RUB',
            'expire_at': '2022-05-01T00:00:00+00:00',
            'limit': '1000',
            'percent': 10,
        },
    }
    assert mock_coupons.times_called == 1
    assert mock_core_order.times_called == 1
    assert mock_post_notification.times_called == 2
    assert mock_post_notification.next_call()['request'].json == {
        'application': 'eda_native',
        'locale': 'ru',
        'notification_key': 'coupon_push_izvinyashki',
        'options_values': {
            'place_name': 'Вкусная еда',
            'place_address': 'Улица и дом',
        },
        'project': 'eda',
        'user_id': '112',
        'user_type': 'eater_id',
    }
    assert mock_post_notification.next_call()['request'].json == {
        'application': 'go',
        'locale': 'ru',
        'notification_key': 'coupon_push_izvinyashki',
        'options_values': {
            'place_name': 'Вкусная еда',
            'place_address': 'Улица и дом',
        },
        'project': 'eda',
        'user_id': 'taxi112',
        'user_type': 'taxi_user_id',
    }

    await stq_runner.eats_place_rating_feedback_answer.call(
        task_id='fake_task_2',
        kwargs={
            'answer': {
                'coupon': {
                    'reason': 'мы заботимся о клиентах',
                    'type': 'COUPONTYPE',
                    'value': 10,
                    'is_percent': True,
                },
                'feedback_id': 1,
                'answer_id': 1,
                'text': (
                    'спасибо за отзыв, мы исправимся, вот вам скидка на заказ'
                ),
            },
            'place_id': 1,
            'partner_id': 1,
            'eater_id': '112',
            'order_nr': 'ORDER_3',
        },
    )

    assert mock_catalog_storage.times_called == 1
    assert mock_feedback_update.times_called == 0
    assert mock_coupons.times_called == 1
    assert mock_core_order.times_called == 1
    assert mock_post_notification.times_called == 0


@pytest.mark.parametrize(
    (
        'stq_answer',
        'feedback_answer',
        'email_data',
        'mock_count',
        'update_request',
        'sticker_send_times',
    ),
    [
        pytest.param(
            {
                'coupon': {
                    'reason': 'мы заботимся о клиентах',
                    'type': 'COUPONTYPE',
                    'value': 10,
                },
                'feedback_id': 1,
                'answer_id': 1,
            },
            {
                'coupon': {
                    'coupon': 'PROMOCODE',
                    'currency_code': 'RUB',
                    'expire_at': '2022-05-01T00:00:00+00:00',
                    'value': 10,
                    'limit': '1000',
                    'percent': 10,
                },
                'feedback_id': 1,
            },
            {},
            1,
            {
                'answer_id': 1,
                'coupon': {
                    'coupon': 'PROMOCODE',
                    'currency_code': 'RUB',
                    'expire_at': '2022-05-01T00:00:00+00:00',
                    'limit': '1000',
                    'percent': 10,
                },
            },
            0,
            id='without text',
        ),
        pytest.param(
            {
                'coupon': {
                    'reason': 'мы заботимся о клиентах',
                    'type': 'COUPONTYPE',
                    'value': 10,
                },
                'feedback_id': 1,
                'answer_id': 1,
                'text': (
                    'спасибо за отзыв, мы исправимся, вот вам скидка на заказ'
                ),
            },
            {
                'coupon': {
                    'coupon': 'PROMOCODE',
                    'currency_code': 'RUB',
                    'expire_at': '2022-05-01T00:00:00+00:00',
                    'value': 10,
                    'limit': '1000',
                    'percent': 10,
                },
                'comment': (
                    'спасибо за отзыв, мы исправимся, вот вам скидка на заказ'
                ),
                'feedback_id': 1,
            },
            {
                'body': (
                    '<?xml version="1.0" encoding="UTF-8"?><mails><mail><from>'
                    'no-reply@eda.yandex.ru</from><subject>Promocode: '
                    'PROMOCODE</subject><body>Your спасибо за отзыв, мы '
                    'исправимся, вот вам скидка на заказ, Do not reply, '
                    'Вкусная еда, Улица и дом</body></mail></mails>'
                ),
                'send_to': ['567'],
                'idempotence_token': 'idemp_1',
            },
            1,
            {
                'answer_id': 1,
                'coupon': {
                    'coupon': 'PROMOCODE',
                    'currency_code': 'RUB',
                    'expire_at': '2022-05-01T00:00:00+00:00',
                    'limit': '1000',
                    'percent': 10,
                },
            },
            1,
            id='with promocode',
        ),
        pytest.param(
            {
                'feedback_id': 1,
                'answer_id': 1,
                'text': 'спасибо за отзыв, мы исправимся и все',
            },
            {
                'comment': 'спасибо за отзыв, мы исправимся и все',
                'feedback_id': 1,
            },
            {
                'body': (
                    '<?xml version="1.0" encoding="UTF-8"?><mails><mail><from>'
                    'no-reply@eda.yandex.ru</from><subject>Just text, no '
                    'promocode</subject><body>Your спасибо за отзыв, мы '
                    'исправимся и все, Do not reply, Вкусная еда, Улица '
                    'и дом</body></mail></mails>'
                ),
                'send_to': ['567'],
                'idempotence_token': 'idemp_1',
            },
            0,
            {'answer_id': 1},
            1,
            id='without promocode',
        ),
        pytest.param(
            {
                'feedback_id': 1,
                'answer_id': 1,
                'text': 'спасибо за отзыв <HTML> &\'", мы исправимся и все',
            },
            {
                'comment': 'спасибо за отзыв <HTML> &\'", мы исправимся и все',
                'feedback_id': 1,
            },
            {
                'body': (
                    '<?xml version="1.0" encoding="UTF-8"?><mails><mail><from>'
                    'no-reply@eda.yandex.ru</from><subject>Just text, no '
                    'promocode</subject><body>Your спасибо за отзыв &amp;lt;'
                    'HTML&amp;gt; &amp;amp;&amp;apos;&amp;quot;, мы '
                    'исправимся и все, Do not reply, Вкусная еда, Улица и '
                    'дом</body></mail></mails>'
                ),
                'send_to': ['567'],
                'idempotence_token': 'idemp_1',
            },
            0,
            {'answer_id': 1},
            1,
            id='without promocode (html)',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
@pytest.mark.experiments3(filename='exp3_eats_place_rating_email.json')
async def test_feedback_answer_stq_email(
        stq_runner,
        mock_catalog_storage,
        mock_get_feedbacks,
        mock_core_order,
        mock_coupons,
        mockserver,
        feedback_answer,
        stq_answer,
        email_data,
        mock_count,
        update_request,
        mock_post_notification,
        mock_feedback_update,
        sticker_send_times,
        mock_core_restapp,
):
    @mockserver.json_handler('/sticker/send/')
    def mock_sticker_send(request):
        assert request.json == email_data
        return mockserver.make_response(status=200, json={})

    await stq_runner.eats_place_rating_feedback_answer.call(
        task_id='fake_task',
        kwargs={
            'answer': stq_answer,
            'place_id': 1,
            'partner_id': 1,
            'eater_id': '112',
            'order_nr': 'ORDER_3',
        },
    )

    assert mock_catalog_storage.times_called == 1
    assert mock_coupons.times_called == mock_count
    assert mock_core_order.times_called == 1
    assert mock_sticker_send.times_called == sticker_send_times
    assert mock_post_notification.times_called == mock_count * 2
    assert mock_feedback_update.times_called == 1
    request = mock_feedback_update.next_call()['request'].json
    del request['answer_status_code']
    assert request == update_request
