import pytest

DEFAULT_UID = '4003514353'

NOTIFICATION_REQUEST = {
    'id': 'b300bda7d41b4bae8d58dfa93221ef16',
    'route': [[37.900188446044922, 55.416580200195312]],
    'revision_id': 24,
    'selected_class': 'econom',
    'tariffs': [],
    'payment_method': {'id': 'card-x7698', 'type': 'card'},
}

PROMO_REDIRECT = {
    'redirect': {
        'content': 'promo_redirect_content',
        'details': 'promo_redirect_details',
        'icon_image_tag': '<promo_redirect_icon_image_tag>',
        'show_limitations': [
            {'type': 'days_period', 'range_days': 15, 'limit': 5},
        ],
    },
    'class': 'business',
}

PROMO_REDIRECT_YA_PLUS = {
    'redirect': {
        'content': 'yaplus_content',
        'details': 'yaplus_details',
        'icon_image_tag': '<yaplus_icon_image_tag>',
        'show_limitations': [
            {'type': 'days_period', 'range_days': 15, 'limit': 5},
        ],
    },
    'class': 'business',
}


def discount_data(name, tariff='business', card_id='card-test-id'):
    return {'discount_name': name, 'tariff': tariff, 'card_id': card_id}


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_redirect_content': {'ru': '<promo_redirect_content>'},
        'promo_redirect_details': {'ru': '<promo_redirect_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize('remove_revision', [True, False])
@pytest.mark.parametrize('phone_payment_method', [True, False])
async def test_personalstate_notification_redirect(
        taxi_user_state,
        mongodb,
        remove_revision,
        phone_payment_method,
        mock_ride_discounts,
        mock_feeds,
        mock_cardstorage,
        mockserver,
):
    mock_feeds.add_payload('business_discount', PROMO_REDIRECT)
    mock_ride_discounts.set_discounts(
        [
            discount_data(
                'business_discount', tariff='business', card_id='card-x7698',
            ),
        ],
    )

    json = NOTIFICATION_REQUEST.copy()
    if remove_revision:
        json.pop('revision_id', None)

    if phone_payment_method:

        @mockserver.handler('/user-api/users/get')
        def _users_get(request):
            response = {
                'id': json['id'],
                'last_payment_method': json['payment_method'],
            }
            return mockserver.make_response(json.dumps(response), 200)

        json.pop('payment_method', None)

    response = await taxi_user_state.post(
        'personalstate',
        json=json,
        headers={
            'X-Yandex-UID': DEFAULT_UID,
            'X-YaTaxi-PhoneId': 'test_phone_id',
        },
    )

    assert response.status_code == 200

    action = response.json()['action']
    assert action['type'] == 'notification'
    assert 'notification' in action

    assert action['notification'] == {
        'event_info': {
            'event_name': 'DiscountSummaryPromo',
            'event_type': 'redirect_to_tariff',
            'tag': 'business_discount',
        },
        'content': '<promo_redirect_content>',
        'details': '<promo_redirect_details>',
        'icon_image_tag': '<promo_redirect_icon_image_tag>',
        'options': [
            {'on': 'tap', 'action': {'type': 'redirect', 'class': 'business'}},
        ],
        'show_limitations': [
            {'type': 'days_period', 'range_days': 15, 'limit': 5},
        ],
    }


@pytest.mark.experiments3(filename='exp3/fictitious_discounts.json')
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    TVM_ENABLED=False,
    INAPP_PROMOBLOCKS_CARD_PLUS_FEATURES=[
        {
            'feature_name': 'mastercard_plus',
            'conditions': {'bin_one_of': ['510126']},
        },
    ],
    PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''],
)
@pytest.mark.translations(
    client_messages={
        'promo_pme_info': {'ru': '<promo_pme_info>'},
        'promo_pme_info_instead_date': {'ru': '<promo_pme_info_instead_date>'},
        'promo_pme_message': {'ru': '<promo_pme_message>'},
        'promo_pme_content': {'ru': '<promo_pme_content>'},
        'promo_pme_details': {'ru': '<promo_pme_details>'},
        'promo_pme_details_redirect': {'ru': '<promo_pme_details_redirect>'},
        'promo_pme_details_redirect_button_title': {
            'ru': '<promo_pme_details_redirect_button_title>',
        },
    },
)
@pytest.mark.filldb(personal_state='one')
async def test_personalstate_exp_based_discounts(
        taxi_user_state, mock_feeds, mock_cardstorage,
):
    promo = PROMO_REDIRECT.copy()
    promo['payments_methods_extra'] = {
        'info': 'promo_pme_info',
        'info_instead_date': 'promo_pme_info_instead_date',
        'message': 'promo_pme_message',
        'info_screen': {
            'content': 'promo_pme_content',
            'details': 'promo_pme_details',
            'details_redirect': 'promo_pme_details_redirect',
            'details_redirect_button_title': (
                'promo_pme_details_redirect_button_title'
            ),
            'icon_image_tag': 'promo_pme_icon_image_tag',
        },
    }
    mock_feeds.add_payload('exp_discount_description', promo)

    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
    }
    response = await taxi_user_state.post(
        'personalstate',
        json=json,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )

    response_json = response.json()

    assert response_json == {
        'requirements': {'nosmoking': True, 'yellowcarnumber': True},
        'revision_id': 777,
        'selected_class': 'econom',
        'tariffs': [
            {
                'class': 'comfortplus',
                'payments_methods_extra': [
                    {
                        'event_info': {
                            'event_name': 'DiscountSummaryPromo',
                            'tag': 'exp_discount_description',
                        },
                        'id': 'card-x7698',
                        'info': '<promo_pme_info>',
                        'info_instead_date': '<promo_pme_info_instead_date>',
                        'info_screen': {
                            'content': '<promo_pme_content>',
                            'details': '<promo_pme_details>',
                            'details_redirect': 'promo_pme_details_redirect',
                            'details_redirect_button_title': (
                                '<promo_pme_details_redirect_button_title>'
                            ),
                            'icon_image_tag': 'promo_pme_icon_image_tag',
                        },
                        'message': '<promo_pme_message>',
                    },
                ],
                'requirements': {},
            },
            {
                'class': 'econom',
                'payments_methods_extra': [
                    {
                        'event_info': {
                            'event_name': 'DiscountSummaryPromo',
                            'tag': 'exp_discount_description',
                        },
                        'id': 'card-x7698',
                        'info': '<promo_pme_info>',
                        'info_instead_date': '<promo_pme_info_instead_date>',
                        'info_screen': {
                            'content': '<promo_pme_content>',
                            'details': '<promo_pme_details>',
                            'details_redirect': 'promo_pme_details_redirect',
                            'details_redirect_button_title': (
                                '<promo_pme_details_redirect_button_title>'
                            ),
                            'icon_image_tag': 'promo_pme_icon_image_tag',
                        },
                        'message': '<promo_pme_message>',
                    },
                ],
                'requirements': {'nosmoking': True, 'yellowcarnumber': True},
            },
        ],
    }


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_redirect_content': {'ru': '<promo_redirect_content>'},
        'promo_redirect_details': {'ru': '<promo_redirect_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personalstate_notification_redirect_wrong_class(
        taxi_user_state, mock_ride_discounts, mock_feeds,
):
    mock_ride_discounts.set_discounts(
        [discount_data('business_discount', tariff='business')],
    )

    payload = PROMO_REDIRECT.copy()
    payload['class'] = 'comfort'
    mock_feeds.add_payload('business_discount', payload)

    json = NOTIFICATION_REQUEST.copy()
    response = await taxi_user_state.post(
        'personalstate',
        json=json,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200
    assert 'action' not in response.json()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_redirect_content': {'ru': '<promo_redirect_content>'},
        'promo_redirect_details': {'ru': '<promo_redirect_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personalstate_notification_selected(
        taxi_user_state, mock_ride_discounts, mock_feeds,
):
    already_selected_promo = PROMO_REDIRECT.copy()
    already_selected_promo['already_selected'] = already_selected_promo.pop(
        'redirect',
    )
    mock_feeds.add_payload('business_discount', already_selected_promo)

    mock_ride_discounts.set_discounts(
        [
            discount_data(
                'business_discount', 'business', card_id='card-x7698',
            ),
            discount_data('business_discount', 'vip', card_id='card-x7698'),
            discount_data('business_discount2', 'vip', card_id='card-x7698'),
        ],
    )
    json = NOTIFICATION_REQUEST.copy()
    json['selected_class'] = 'business'
    response = await taxi_user_state.post(
        'personalstate',
        json=json,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    action = response.json()['action']
    assert action['type'] == 'notification'
    assert 'notification' in action

    assert action['notification'] == {
        'event_info': {
            'event_name': 'DiscountSummaryPromo',
            'event_type': 'discount_info',
            'tag': 'business_discount',
        },
        'content': '<promo_redirect_content>',
        'details': '<promo_redirect_details>',
        'icon_image_tag': '<promo_redirect_icon_image_tag>',
        'options': [],
        'show_limitations': [
            {'limit': 5.0, 'range_days': 15.0, 'type': 'days_period'},
        ],
    }


# TODO: rides_count: how to replace?
@pytest.mark.skip
@pytest.mark.translations(
    client_messages={
        'promo_redirect_content': {'ru': '<promo_redirect_content>'},
        'promo_redirect_details': {'ru': '<promo_redirect_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize('num_rides,apply_discount', [(1, True), (3, False)])
async def test_personalstate_notification_discount_stats_check_old(
        taxi_user_state,
        db,
        num_rides,
        apply_discount,
        mock_ride_discounts,
        mock_feeds,
):
    if apply_discount:
        mock_ride_discounts.set_discounts(
            [discount_data('rides_limited_discount')],
        )

        mock_feeds.add_payload('rides_limited_discount', PROMO_REDIRECT)

    user = db.users.find_one({'_id': NOTIFICATION_REQUEST['id']})
    phone_id = user['phone_id']
    result = db.discounts_usage_stats.update(
        {
            'phone_id': phone_id,
            'discount_id': 'a122c228ba2b4d3189971a430ca6d2d1',
        },
        {'$set': {'rides_count': num_rides}},
        upsert=True,
    )
    assert result['upserted']

    response = taxi_user_state.post(
        'personalstate',
        json=NOTIFICATION_REQUEST,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    if apply_discount:
        assert 'action' in response.json()
    else:
        assert 'action' not in response.json()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_redirect_content': {'ru': '<promo_redirect_content>'},
        'promo_redirect_details': {'ru': '<promo_redirect_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personalstate_notification_discount_stats_check(
        taxi_user_state, mock_ride_discounts, mock_feeds,
):
    mock_ride_discounts.set_discounts(
        [discount_data('rides_limited_discount', card_id='card-x7698')],
    )
    mock_feeds.add_payload('rides_limited_discount', PROMO_REDIRECT)
    response = await taxi_user_state.post(
        'personalstate',
        json=NOTIFICATION_REQUEST,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200
    assert mock_ride_discounts.calls == 1
    assert 'action' in response.json()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_redirect_content': {'ru': '<promo_redirect_content>'},
        'promo_redirect_details': {'ru': '<promo_redirect_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize('num_rides,apply_discount', [(1, True), (3, False)])
async def test_personalstate_notification_phone_stats_check_old(
        taxi_user_state,
        num_rides,
        apply_discount,
        mock_ride_discounts,
        mock_feeds,
        mockserver,
):
    if apply_discount:
        mock_ride_discounts.set_discounts(
            [discount_data('newbie_discount', card_id='card-x7698')],
        )

        mock_feeds.add_payload('newbie_discount', PROMO_REDIRECT)

    @mockserver.json_handler('/user-api/user_phones/get')
    def _phones_get(request):
        import json
        response = {
            'id': 'user_id',
            'personal_phone_id': request.json['id'],
            'stat': {
                'big_first_discounts': 1,
                'complete': num_rides,
                'complete_card': 1,
                'complete_apple': 1,
                'complete_google': 1,
                'total': 1,
                'fake': 1,
            },
            'type': 'yandex',
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
            'phone': '+70000000000',
            'last_payment_method': {'type': 'card', 'id': 'card-x7698'},
        }
        return mockserver.make_response(json.dumps(response), 200)

    response = await taxi_user_state.post(
        'personalstate',
        json=NOTIFICATION_REQUEST,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    if apply_discount:
        assert 'action' in response.json()
    else:
        assert 'action' not in response.json()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_redirect_content': {'ru': '<promo_redirect_content>'},
        'promo_redirect_details': {'ru': '<promo_redirect_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personalstate_notification_phone_stats_check(
        taxi_user_state, mock_ride_discounts, mock_feeds,
):
    mock_ride_discounts.set_discounts(
        [discount_data('newbie_discount', card_id='card-x7698')],
    )
    mock_feeds.add_payload('newbie_discount', PROMO_REDIRECT)

    response = await taxi_user_state.post(
        'personalstate',
        json=NOTIFICATION_REQUEST,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200
    assert 'action' in response.json()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'yaplus_content': {'ru': '<yaplus_content>'},
        'yaplus_details': {'ru': '<yaplus_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    ('user_has_ya_plus', 'price_modifier_class', 'apply_discount'),
    [
        pytest.param(
            False, 'business', False, id='no_discount_without_ya_plus',
        ),
        pytest.param(True, 'econom', False, id='no_discount_without_modifier'),
        pytest.param(True, 'business', True, id='ya_plus_discount'),
    ],
)
async def test_personalstate_notification_yaplus_discount_old(
        taxi_user_state,
        mongodb,
        user_has_ya_plus,
        price_modifier_class,
        apply_discount,
        mock_ride_discounts,
        mock_feeds,
        mockserver,
):
    if user_has_ya_plus:

        @mockserver.handler('/user-api/users/get')
        def _users_get(request):
            import json
            response = {'id': NOTIFICATION_REQUEST['id'], 'has_ya_plus': True}
            return mockserver.make_response(json.dumps(response), 200)

    if apply_discount:
        mock_ride_discounts.set_discounts(
            [discount_data('ya_plus_discount', card_id='card-x7698')],
        )

        mock_feeds.add_payload('ya_plus_discount', PROMO_REDIRECT_YA_PLUS)

    modifiers_result = mongodb.price_modifiers.update(
        {},
        {'$set': {'modifiers.0.tariff_categories': [price_modifier_class]}},
    )
    assert modifiers_result['nModified'] == 1

    response = await taxi_user_state.post(
        'personalstate',
        json=NOTIFICATION_REQUEST,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    if apply_discount:
        response_json = response.json()
        assert 'action' in response_json
        action = response_json['action']
        assert action['type'] == 'notification'
        assert 'notification' in action
        assert action['notification']['details'] == '<yaplus_details>'
    else:
        assert 'action' not in response.json()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'yaplus_content': {'ru': '<yaplus_content>'},
        'yaplus_details': {'ru': '<yaplus_details>'},
    },
)
@pytest.mark.parametrize(
    (
        'user_has_ya_plus',
        'price_modifier_class',
        'apply_discount',
        'peek_discount_response',
    ),
    [
        pytest.param(
            False, 'business', False, {}, id='no_discount_without_ya_plus',
        ),
        pytest.param(
            True, 'econom', False, {}, id='no_discount_without_modifier',
        ),
        pytest.param(
            True,
            'business',
            True,
            discount_data(
                'ya_plus_discount', tariff='business', card_id='card-x7698',
            ),
            id='ya_plus_discount',
        ),
    ],
)
async def test_personalstate_notification_yaplus_discount(
        taxi_user_state,
        mongodb,
        mockserver,
        mock_ride_discounts,
        mock_feeds,
        user_has_ya_plus,
        price_modifier_class,
        apply_discount,
        peek_discount_response,
):
    mock_ride_discounts.set_discounts([peek_discount_response])
    mock_feeds.add_payload('ya_plus_discount', PROMO_REDIRECT_YA_PLUS)

    if user_has_ya_plus:

        @mockserver.handler('/user-api/users/get')
        def _users_get(request):
            import json
            response = {'id': NOTIFICATION_REQUEST['id'], 'has_ya_plus': True}
            return mockserver.make_response(json.dumps(response), 200)

    modifiers_result = mongodb.price_modifiers.update(
        {},
        {'$set': {'modifiers.0.tariff_categories': [price_modifier_class]}},
    )
    assert modifiers_result['nModified'] == 1

    response = await taxi_user_state.post(
        'personalstate',
        json=NOTIFICATION_REQUEST,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    if apply_discount:
        response_json = response.json()
        assert 'action' in response_json
        action = response_json['action']
        assert action['type'] == 'notification'
        assert 'notification' in action
        assert action['notification']['details'] == '<yaplus_details>'
    else:
        assert 'action' not in response.json()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_cpm_content': {'ru': '<promo_cpm_content>'},
        'promo_cpm_details': {'ru': '<promo_cpm_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
async def test_personalstate_notification_cpm(
        taxi_user_state, mock_ride_discounts, mock_feeds,
):
    mock_ride_discounts.set_discounts(
        [discount_data('business_discount', card_id='card-x7698')],
    )
    mock_feeds.add_payload(
        'business_discount',
        {
            'change_payments_method': {
                'content': 'promo_cpm_content',
                'details': 'promo_cpm_details',
                'icon_image_tag': '<promo_cpm_icon_image_tag>',
                'show_limitations': [
                    {'type': 'days_period', 'range_days': 15, 'limit': 5},
                ],
            },
            'class': 'business',
        },
    )
    json = NOTIFICATION_REQUEST.copy()
    json['payment_method'] = {'type': 'cash'}
    response = await taxi_user_state.post(
        'personalstate',
        json=json,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    action = response.json()['action']
    assert action['type'] == 'notification'
    assert 'notification' in action

    assert action['notification'] == {
        'event_info': {
            'event_name': 'DiscountSummaryPromo',
            'event_type': 'change_payment_method',
            'tag': 'business_discount',
        },
        'content': '<promo_cpm_content>',
        'details': '<promo_cpm_details>',
        'icon_image_tag': '<promo_cpm_icon_image_tag>',
        'options': [
            {
                'on': 'tap',
                'action': {
                    'type': 'select_payment_then_redirect',
                    'class': 'business',
                },
            },
        ],
        'show_limitations': [
            {'type': 'days_period', 'range_days': 15, 'limit': 5},
        ],
    }


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_cpm_content': {'ru': '<promo_cpm_content>'},
        'promo_cpm_details': {'ru': '<promo_cpm_details>'},
        'promo_pme_message': {'ru': '<promo_pme_message>'},
        'promo_pme_info': {'ru': '<promo_pme_info>'},
        'promo_pme_info_instead_date': {'ru': '<promo_pme_info_instead_date>'},
        'promo_screen_content': {'ru': '<promo_screen_content>'},
        'promo_screen_details': {'ru': '<promo_screen_details>'},
        'promo_screen_button': {'ru': '<promo_screen_button>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    'tariff',
    ['business', 'minivan'],
    ids=['can_be_default', 'canNOT_be_default'],
)
async def test_personalstate_payments_methods_extra(
        taxi_user_state, mock_ride_discounts, mock_feeds, tariff,
):
    mock_ride_discounts.set_discounts(
        [
            discount_data(
                'business_discount', tariff=tariff, card_id='card-x7698',
            ),
        ],
    )
    mock_feeds.add_payload(
        'business_discount',
        {
            'change_payments_method': {
                'content': 'promo_cpm_content',
                'details': 'promo_cpm_details',
                'icon_image_tag': '<promo_cpm_icon_image_tag>',
                'show_limitations': [
                    {'type': 'days_period', 'range_days': 15, 'limit': 5},
                ],
            },
            'payments_methods_extra': {
                'message': 'promo_pme_message',
                'info': 'promo_pme_info',
                'info_instead_date': 'promo_pme_info_instead_date',
                'info_screen': {
                    'content': 'promo_screen_content',
                    'details': 'promo_screen_details',
                    'icon_image_tag': '<promo_pme_icon_image_tag>',
                    'details_redirect': '<promo_screen_redirect>',
                    'details_redirect_button_title': 'promo_screen_button',
                },
            },
            'class': tariff,
        },
    )
    json = NOTIFICATION_REQUEST.copy()
    json['payment_method'] = {'type': 'cash'}
    json['selected_class'] = tariff
    response = await taxi_user_state.post(
        'personalstate',
        json=json,
        headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200
    assert response.json()['tariffs'] == [
        {
            'class': tariff,
            'payments_methods_extra': [
                {
                    'event_info': {
                        'event_name': 'DiscountSummaryPromo',
                        'tag': 'business_discount',
                    },
                    'id': 'card-x7698',
                    'info': '<promo_pme_info>',
                    'info_instead_date': '<promo_pme_info_instead_date>',
                    'info_screen': {
                        'content': '<promo_screen_content>',
                        'details': '<promo_screen_details>',
                        'details_redirect': '<promo_screen_redirect>',
                        'details_redirect_button_title': (
                            '<promo_screen_button>'
                        ),
                        'icon_image_tag': '<promo_pme_icon_image_tag>',
                    },
                    'message': '<promo_pme_message>',
                },
            ],
            'requirements': {},
        },
    ]


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'promo_redirect_content': {'ru': '<promo_redirect_content>'},
        'promo_redirect_details': {'ru': '<promo_redirect_details>'},
    },
)
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    ('promo_exists', 'has_discount', 'feeds_failing', 'promo_shown'),
    [
        pytest.param(True, True, False, True, id='promo_exists'),
        pytest.param(
            True, False, False, False, id='promo_exists_without_discount',
        ),
        pytest.param(
            True,
            True,
            False,
            True,
            marks=pytest.mark.experiments3(
                filename='exp3/ride_discounts_call_call_both_use_both.json',
            ),
            id='ride_discounts_call_promo_exists',
        ),
        pytest.param(
            True,
            True,
            False,
            True,
            marks=pytest.mark.experiments3(
                filename=(
                    'exp3/ride_discounts_call_call_'
                    'both_use_old_discounts.json'
                ),
            ),
            id='ride_discounts_call_promo_exists',
        ),
        pytest.param(
            True,
            True,
            False,
            True,
            marks=pytest.mark.experiments3(
                filename='exp3/ride_discounts_call_disabled.json',
            ),
            id='ride_discounts_call_promo_exists',
        ),
        pytest.param(
            True,
            True,
            False,
            True,
            marks=pytest.mark.experiments3(
                filename=(
                    'exp3/ride_discounts_call_use_only_ride_discounts.json'
                ),
            ),
            id='ride_discounts_call_promo_exists',
        ),
        pytest.param(
            True,
            False,
            False,
            False,
            marks=pytest.mark.experiments3(
                filename='exp3/ride_discounts_call_disabled.json',
            ),
            id='ride_discounts_call_without_discount',
        ),
        pytest.param(False, True, False, False, id='promo_not_exist'),
        pytest.param(True, True, True, False, id='feeds_failing'),
    ],
)
async def test_personalstate_feeds_cache(
        taxi_user_state,
        mock_ride_discounts,
        mock_feeds,
        promo_exists,
        has_discount,
        feeds_failing,
        promo_shown,
):
    discounts = []
    if has_discount:
        discounts = [
            discount_data(
                'business_discount', tariff='business', card_id='card-x7698',
            ),
        ]
    mock_ride_discounts.set_discounts(discounts)
    if feeds_failing:
        mock_feeds.set_failing()

    if promo_exists:
        payload = PROMO_REDIRECT.copy()
        mock_feeds.add_payload('business_discount', payload)

    json = NOTIFICATION_REQUEST.copy()
    json.pop('revision_id', None)
    for _ in range(3):
        response = await taxi_user_state.post(
            'personalstate',
            json=json,
            headers={'Accept-Language': 'ru', 'X-Yandex-UID': DEFAULT_UID},
        )
        assert response.status_code == 200
        if promo_shown:
            assert 'action' in response.json()
        else:
            assert 'action' not in response.json()
    if has_discount:
        assert mock_feeds.times_called == 1
