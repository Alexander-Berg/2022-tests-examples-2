import datetime as dt
import json

import pytest

ENDPOINT = '/v1/payment/availability'

VERIFIED_CARD_USER = USER_WITH_CARDS = 'user_2'
VERIFIED_CARD_DEVICE = DEVICE_WITH_CARDS = 'device_2'
VERIFIED_CARD_ID = 'card_2'

USER_UID_WITH_VERIFIED_DEVICE = 'user_uid_1'
VERIFIED_DEVICE_ID = 'device_1'
USER_ID_WITH_VERIFIED_DEVICE = 'user_id_1'
YANDEX_LOGIN_ID = 'login_id'


@pytest.mark.parametrize(
    'request_params',
    [
        {
            'yandex_uid': USER_UID_WITH_VERIFIED_DEVICE,
            'device_id': VERIFIED_DEVICE_ID,
            'card_id': 'some_card_id',
        },
        {
            'yandex_uid': USER_UID_WITH_VERIFIED_DEVICE,
            'device_id': VERIFIED_DEVICE_ID,
        },
    ],
    ids=['with_card_id', 'without_card_id'],
)
async def test_device_verified(taxi_card_antifraud, request_params):
    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)

    assert response.status_code == 200

    response_body = response.json()
    assert response_body['all_payments_available'] is True
    assert response_body['available_cards'] == []


@pytest.mark.parametrize(
    'request_params, available_cards_expected',
    [
        (
            {
                'yandex_uid': VERIFIED_CARD_USER,
                'device_id': VERIFIED_CARD_DEVICE,
                'card_id': VERIFIED_CARD_ID,
            },
            [{'card_id': VERIFIED_CARD_ID}],
        ),
        (
            {
                'yandex_uid': VERIFIED_CARD_USER,
                'device_id': VERIFIED_CARD_DEVICE,
                'card_id': 'absent_card',
            },
            [],
        ),
        (
            {
                'yandex_uid': 'absent_user',
                'device_id': VERIFIED_CARD_DEVICE,
                'card_id': VERIFIED_CARD_ID,
            },
            [],
        ),
        (
            {
                'yandex_uid': VERIFIED_CARD_USER,
                'device_id': 'absent_device',
                'card_id': VERIFIED_CARD_ID,
            },
            [],
        ),
    ],
    ids=['ok', 'absent_card', 'absent_user', 'absent_device'],
)
async def test_card_id_in_request(
        taxi_card_antifraud, request_params, available_cards_expected,
):
    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)
    assert response.status_code == 200

    response_body = response.json()
    expected_response = {
        'all_payments_available': False,
        'available_cards': available_cards_expected,
    }
    assert response_body == expected_response


@pytest.mark.parametrize(
    'request_params, available_cards_ids_expected',
    [
        (
            {
                'yandex_uid': USER_WITH_CARDS,
                'device_id': DEVICE_WITH_CARDS,
                'yandex_login_id': YANDEX_LOGIN_ID,
            },
            ['card_2', 'card_3'],
        ),
        ({'yandex_uid': 'absent_user', 'device_id': DEVICE_WITH_CARDS}, []),
        ({'yandex_uid': USER_WITH_CARDS, 'device_id': 'absent_device'}, []),
    ],
    ids=['with_cards', 'absent_user', 'absent_device'],
)
async def test_card_id_not_in_request(
        taxi_card_antifraud, request_params, available_cards_ids_expected,
):
    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['all_payments_available'] is False

    card_ids = sorted(c['card_id'] for c in response_body['available_cards'])

    assert card_ids == sorted(available_cards_ids_expected)


async def test_request_neither_userid_deviceid(taxi_card_antifraud):
    response = await taxi_card_antifraud.get(
        ENDPOINT, params={'yandex_uid': 'doesntmatter'},
    )
    assert response.status_code == 400


async def test_request_either_userid_deviceid(taxi_card_antifraud, mockserver):
    @mockserver.handler('/user-api/users/get')
    def _users_get(request):
        assert False

    request_params = {
        'yandex_uid': USER_UID_WITH_VERIFIED_DEVICE,
        'device_id': VERIFIED_DEVICE_ID,
        'user_id': USER_ID_WITH_VERIFIED_DEVICE,
    }
    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)
    assert response.status_code == 200
    assert response.json() == {
        'all_payments_available': True,
        'available_cards': [],
    }


@pytest.mark.parametrize(
    'user_id,metrica_device_id,expected_response',
    [
        (
            USER_ID_WITH_VERIFIED_DEVICE,
            VERIFIED_DEVICE_ID,
            {'all_payments_available': True, 'available_cards': []},
        ),
        (
            USER_ID_WITH_VERIFIED_DEVICE,
            None,
            {'all_payments_available': False, 'available_cards': []},
        ),
        pytest.param(
            USER_ID_WITH_VERIFIED_DEVICE,
            None,
            {'all_payments_available': True, 'available_cards': []},
            marks=pytest.mark.experiments3(
                filename='experiments3_allow_payment_for_expired_users.json',
            ),
        ),
    ],
    ids=[
        'metrica_device_id_ok',
        'no_metrica_device_id_no_exp',
        'no_metrica_device_id_with_exp',
    ],
)
async def test_with_user_id(
        taxi_card_antifraud,
        mockserver,
        user_id,
        metrica_device_id,
        expected_response,
):
    @mockserver.handler('/user-api/users/get')
    def _users_get(request):
        assert request.json['id'] == user_id
        assert request.json['fields'] == ['metrica_device_id']
        response = {'id': user_id}
        if metrica_device_id is not None:
            response['metrica_device_id'] = metrica_device_id
        return mockserver.make_response(json.dumps(response), 200)

    request_params = {
        'yandex_uid': USER_UID_WITH_VERIFIED_DEVICE,
        'user_id': user_id,
    }

    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)

    assert response.status_code == 200
    assert response.json() == expected_response


async def test_user_api_unavailable(taxi_card_antifraud, mockserver):
    @mockserver.handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response('', 500)

    request_params = {'yandex_uid': 'doesntmatter', 'user_id': 'doesntmatter'}

    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)
    assert response.status_code == 500


@pytest.mark.config(CARD_ANTIFRAUD_SERVICE_ENABLED=False)
async def test_service_disabled(taxi_card_antifraud):
    request_params = {'yandex_uid': 'doesntmatter', 'user_id': 'doesntmatter'}
    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)
    assert response.status_code == 429


@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'lv'])
@pytest.mark.translations(
    client_messages={
        'common_errors.PAYMENT_TYPE_BLOCKED_BY_CARD_ANTIFRAUD': {
            'ru': 'русское сообщение',
            'en': 'английское сообщение',
        },
    },
)
@pytest.mark.parametrize(
    'request_params,with_field,locale_header,expected_text',
    [
        (
            {
                'yandex_uid': USER_UID_WITH_VERIFIED_DEVICE,
                'device_id': VERIFIED_DEVICE_ID,
            },
            False,
            None,
            None,
        ),
        (
            {
                'yandex_uid': 'uid_with_no_verified_devices',
                'device_id': 'doesntmatter',
            },
            True,
            'en-US',
            'английское сообщение',
        ),
        (
            {
                'yandex_uid': 'uid_with_no_verified_devices',
                'device_id': 'doesntmatter',
            },
            True,
            'lv',
            'английское сообщение',
        ),
        (
            {
                'yandex_uid': 'uid_with_no_verified_devices',
                'device_id': 'doesntmatter',
            },
            True,
            None,
            'русское сообщение',
        ),
    ],
    ids=[
        'without_field',
        'with_field_with_lang',
        'fallback_when_no_translation',
        'fallback_when_no_header',
    ],
)
async def test_localized_disabled_reason(
        taxi_card_antifraud,
        request_params,
        with_field,
        locale_header,
        expected_text,
):
    headers = {}
    if locale_header:
        headers.update({'Accept-Language': locale_header})

    response = await taxi_card_antifraud.get(
        ENDPOINT, params=request_params, headers=headers,
    )

    assert response.status_code == 200

    data = response.json()
    has_reason_field = 'disabled_reason_localized' in data
    assert has_reason_field == with_field

    if with_field:
        assert expected_text == data['disabled_reason_localized']


@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'lv'])
@pytest.mark.translations(
    client_messages={
        'common_errors.PAYMENT_TYPE_BLOCKED_BY_CARD_ANTIFRAUD': {
            'ru': 'русское сообщение',
            'en': 'английское сообщение',
        },
    },
)
@pytest.mark.parametrize(
    'request_params,with_field,locale_header,expected_text',
    [
        (
            {
                'yandex_uid': USER_UID_WITH_VERIFIED_DEVICE,
                'device_id': VERIFIED_DEVICE_ID,
            },
            False,
            None,
            None,
        ),
        (
            {
                'yandex_uid': 'uid_with_no_verified_devices',
                'device_id': 'doesntmatter',
            },
            True,
            'en',
            'английское сообщение',
        ),
        (
            {
                'yandex_uid': 'uid_with_no_verified_devices',
                'device_id': 'doesntmatter',
            },
            True,
            'lv',
            'английское сообщение',
        ),
        (
            {
                'yandex_uid': 'uid_with_no_verified_devices',
                'device_id': 'doesntmatter',
            },
            True,
            'ru',
            'русское сообщение',
        ),
    ],
    ids=[
        'without_field',
        'with_field_with_lang',
        'fallback_when_no_translation',
        'fallback_when_no_header',
    ],
)
async def test_locale_from_pa_context(
        taxi_card_antifraud,
        request_params,
        with_field,
        locale_header,
        expected_text,
):
    headers = {'X-Yandex-UID': 'uid_with_no_verified_devices'}
    if locale_header:
        headers.update({'X-Request-Language': locale_header})

    response = await taxi_card_antifraud.get(
        ENDPOINT, params=request_params, headers=headers,
    )

    assert response.status_code == 200

    data = response.json()
    has_reason_field = 'disabled_reason_localized' in data
    assert has_reason_field == with_field

    if with_field:
        assert expected_text == data['disabled_reason_localized']


@pytest.mark.parametrize(
    'request_params, available_cards_expected, has_verification_details',
    [
        (
            {
                'yandex_uid': VERIFIED_CARD_USER,
                'device_id': VERIFIED_CARD_DEVICE,
                'card_id': VERIFIED_CARD_ID,
                'yandex_login_id': YANDEX_LOGIN_ID,
            },
            [{'card_id': VERIFIED_CARD_ID}],
            False,
        ),
        (
            {
                'yandex_uid': VERIFIED_CARD_USER,
                'device_id': VERIFIED_CARD_DEVICE,
                'card_id': 'absent_card',
                'yandex_login_id': YANDEX_LOGIN_ID,
            },
            [],
            False,
        ),
        (
            {
                'yandex_uid': VERIFIED_CARD_USER,
                'device_id': VERIFIED_CARD_DEVICE,
                'card_id': 'absent_card',
                'yandex_login_id': YANDEX_LOGIN_ID,
            },
            [{'card_id': 'absent_card'}],
            True,
        ),
    ],
    ids=[
        'verified_card_from_db',
        'no_verification_details',
        'verified_card_by_cardstorage',
    ],
)
async def test_cardstorage_call(
        taxi_card_antifraud,
        mock_cardstorage_card,
        request_params,
        available_cards_expected,
        has_verification_details,
):
    mock_card = mock_cardstorage_card(
        YANDEX_LOGIN_ID, has_verification_details,
    )

    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)
    assert response.status_code == 200
    assert mock_card.times_called == 1

    response_body = response.json()
    expected_response = {
        'all_payments_available': False,
        'available_cards': available_cards_expected,
    }
    assert response_body == expected_response


async def test_cardstorage_family_member_card(
        taxi_card_antifraud, mock_cardstorage_card,
):
    mock_card = mock_cardstorage_card(YANDEX_LOGIN_ID, is_family_member=True)

    response = await taxi_card_antifraud.get(
        ENDPOINT,
        params={
            'yandex_uid': VERIFIED_CARD_USER,
            'device_id': 'absent_device',
            'card_id': 'absent_family_card',
            'yandex_login_id': YANDEX_LOGIN_ID,
        },
    )
    assert response.status_code == 200
    assert mock_card.times_called == 1

    response_body = response.json()
    expected_response = {
        'all_payments_available': False,
        'available_cards': [{'card_id': 'absent_family_card'}],
    }
    assert response_body == expected_response


async def test_cardstorage_404(taxi_card_antifraud, mock_cardstorage_card):
    mock_card = mock_cardstorage_card(
        YANDEX_LOGIN_ID, has_verification_details=True, status=404,
    )
    params = {
        'yandex_uid': VERIFIED_CARD_USER,
        'device_id': VERIFIED_CARD_DEVICE,
        'card_id': VERIFIED_CARD_ID,
        'yandex_login_id': YANDEX_LOGIN_ID,
    }

    resp = await taxi_card_antifraud.get(ENDPOINT, params=params)

    assert resp.status_code == 200, resp.text
    # ignore yandex_login_id check and fallback to cards check
    assert resp.json() == {
        'all_payments_available': False,
        'available_cards': [{'card_id': VERIFIED_CARD_ID}],
    }
    assert mock_card.times_called == 1


@pytest.mark.parametrize(
    'request_params, available_cards_ids_expected',
    [
        (
            {
                'yandex_uid': USER_WITH_CARDS,
                'device_id': DEVICE_WITH_CARDS,
                'yandex_login_id': YANDEX_LOGIN_ID,
                'prefer_master': True,
            },
            ['card_2', 'card_3'],
        ),
    ],
)
async def test_prefer_master(
        taxi_card_antifraud, request_params, available_cards_ids_expected,
):
    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['all_payments_available'] is False

    card_ids = sorted(c['card_id'] for c in response_body['available_cards'])

    assert card_ids == sorted(available_cards_ids_expected)


# todo(sapunovnik): remove this test if experiment with simple cleanup succeed
@pytest.mark.skip(reason='maybe legacy')
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.parametrize(
    'yandex_uid,device_id,user_id,task_called',
    [
        (VERIFIED_CARD_USER, VERIFIED_CARD_DEVICE, None, 1),
        (VERIFIED_CARD_USER, None, 'user_id_without_devices', 0),
    ],
)
async def test_schedule_verifications_update(
        taxi_card_antifraud,
        stq,
        mockserver,
        yandex_uid,
        device_id,
        user_id,
        task_called,
):
    @mockserver.handler('/user-api/users/get')
    def _users_get(request):
        assert request.json['id'] == user_id
        return mockserver.make_response(json.dumps({'id': user_id}), 200)

    params = {'yandex_uid': yandex_uid}
    if device_id is not None:
        params['device_id'] = device_id
    if user_id is not None:
        params['user_id'] = user_id

    # testing delay from config
    expected_start = dt.datetime(2020, 1, 1) + dt.timedelta(minutes=60)

    response = await taxi_card_antifraud.get(ENDPOINT, params=params)

    assert response.status_code == 200

    assert stq.card_antifraud_verifications_update.times_called == task_called
    if task_called > 0:
        next_call = stq.card_antifraud_verifications_update.next_call()
        assert next_call['id'] == '{}:{}'.format(yandex_uid, device_id)
        assert next_call['eta'] == expected_start
        assert next_call['args'] == [yandex_uid, device_id]


# todo(sapunovnik): remove this test if experiment with simple cleanup succeed
@pytest.mark.skip(reason='maybe legacy')
async def test_verifications_update_stq(stq_runner, fetch_from):
    yandex_uid = 'user_3'
    device_id = 'device_for_user_3'

    devices_before = fetch_from(
        'verified_devices',
        ['id', 'updated_at'],
        variables={'yandex_uid': yandex_uid, 'device_id': device_id},
        order_by='id',
    )

    cards_before = fetch_from(
        'verified_cards',
        ['id', 'updated_at'],
        variables={'yandex_uid': yandex_uid, 'device_id': device_id},
        order_by='id',
    )

    assert len(devices_before) == 1
    assert len(cards_before) == 1

    await stq_runner.card_antifraud_verifications_update.call(
        task_id='{}:{}'.format(yandex_uid, device_id),
        args=[yandex_uid, device_id],
    )

    devices_after = fetch_from(
        'verified_devices',
        ['id', 'updated_at'],
        variables={'yandex_uid': yandex_uid, 'device_id': device_id},
        order_by='id',
    )

    cards_after = fetch_from(
        'verified_cards',
        ['id', 'updated_at'],
        variables={'yandex_uid': yandex_uid, 'device_id': device_id},
        order_by='id',
    )

    assert len(devices_after) == 1
    assert len(cards_after) == 1

    for i, device_after in enumerate(devices_after):
        assert device_after['updated_at'] > devices_before[i]['updated_at']

    for i, card_after in enumerate(cards_after):
        assert card_after['updated_at'] > cards_before[i]['updated_at']


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.parametrize('update_enabled', [True, False])
async def test_verifications_update(
        taxi_card_antifraud, fetch_from, taxi_config, update_enabled,
):
    # 1. Before
    yandex_uid = 'user_3'
    device_id = 'device_for_user_3'
    expected_now = dt.datetime(2020, 1, 1)

    taxi_config.set_values({'CARD_ANTIFRAUD_CLEANUP_ENABLED': update_enabled})
    await taxi_card_antifraud.invalidate_caches()

    devices_before = fetch_from(
        'verified_devices',
        ['id', 'updated_at'],
        variables={'yandex_uid': yandex_uid, 'device_id': device_id},
        order_by='id',
    )

    cards_before = fetch_from(
        'verified_cards',
        ['id', 'updated_at'],
        variables={'yandex_uid': yandex_uid, 'device_id': device_id},
        order_by='id',
    )

    assert len(devices_before) == 1
    assert len(cards_before) == 1

    assert all(card['updated_at'] != expected_now for card in cards_before)
    assert all(
        device['updated_at'] != expected_now for device in devices_before
    )

    # 2. Call
    response = await taxi_card_antifraud.get(
        ENDPOINT, params={'yandex_uid': yandex_uid, 'device_id': device_id},
    )
    assert response.status_code == 200

    # 3. After
    devices_after = fetch_from(
        'verified_devices',
        ['id', 'updated_at'],
        variables={'yandex_uid': yandex_uid, 'device_id': device_id},
        order_by='id',
    )

    cards_after = fetch_from(
        'verified_cards',
        ['id', 'updated_at'],
        variables={'yandex_uid': yandex_uid, 'device_id': device_id},
        order_by='id',
    )

    assert len(devices_after) == 1
    assert len(cards_after) == 1

    cards_updated = all(
        after['updated_at'] > before['updated_at']
        for (before, after) in zip(cards_before, cards_after)
    )

    devices_updated = all(
        after['updated_at'] > before['updated_at']
        for (before, after) in zip(devices_before, devices_after)
    )

    assert cards_updated == update_enabled
    assert devices_updated == update_enabled


@pytest.mark.config(
    CARD_ANTIFRAUD_VERIFICATION_LEVELS_BLACKLIST=['standard2_3ds'],
)
async def test_blocked_by_verification_level(
        taxi_card_antifraud, mock_cardstorage_card,
):
    request_params = {
        'yandex_uid': VERIFIED_CARD_USER,
        'device_id': VERIFIED_CARD_DEVICE,
        'card_id': 'absent_card',
        'yandex_login_id': YANDEX_LOGIN_ID,
    }
    has_verification_details = True
    mock_card = mock_cardstorage_card(
        YANDEX_LOGIN_ID, has_verification_details,
    )

    response = await taxi_card_antifraud.get(ENDPOINT, params=request_params)
    assert response.status_code == 200
    assert mock_card.times_called == 1

    response_body = response.json()

    expected_response = {
        'all_payments_available': False,
        'available_cards': [],
    }
    assert response_body == expected_response


async def test_allowed_for_phonish(taxi_card_antifraud):
    request_params = {
        'yandex_uid': 'uid_with_no_verified_devices',
        'device_id': VERIFIED_CARD_DEVICE,
    }
    request_headers = {
        'X-YaTaxi-Pass-Flags': 'phonish',
        'X-Yandex-UID': 'uid_with_no_verified_devices',
    }

    response = await taxi_card_antifraud.get(
        ENDPOINT, params=request_params, headers=request_headers,
    )
    assert response.status_code == 200
    response_body = response.json()

    expected_response = {'all_payments_available': True, 'available_cards': []}
    assert response_body == expected_response


@pytest.mark.parametrize(
    'flags,are_all_payments_available',
    [('neophonish', True), ('neophonish,portal', False)],
)
async def test_allowed_for_non_portal_neophonish(
        taxi_card_antifraud, flags, are_all_payments_available,
):
    request_params = {
        'yandex_uid': 'uid_with_no_verified_devices',
        'device_id': VERIFIED_CARD_DEVICE,
    }
    request_headers = {
        'X-YaTaxi-Pass-Flags': flags,
        'X-Yandex-UID': 'uid_with_no_verified_devices',
    }

    response = await taxi_card_antifraud.get(
        ENDPOINT, params=request_params, headers=request_headers,
    )
    assert response.status_code == 200
    response_body = response.json()

    expected_response = {
        'all_payments_available': are_all_payments_available,
        'available_cards': [],
    }
    assert response_body == expected_response
