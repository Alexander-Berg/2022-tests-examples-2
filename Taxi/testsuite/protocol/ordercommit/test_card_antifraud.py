import json

import pytest

from protocol.ordercommit import order_commit_common


@pytest.mark.parametrize(
    'ca_code,all_payments_available,available_cards,code',
    [
        (200, True, [], 200),
        (200, False, [], 406),
        (200, False, [{'card_id': 'card-x5619'}], 200),
        (500, False, [], 200),
    ],
    ids=[
        'device_verified',
        'empty_verified_cards',
        'card_in_verified_cards',
        'card_antifraud_not_available',
    ],
)
@pytest.mark.experiments3(filename='use_card_antifraud.json')
def test_card_antifraud(
        taxi_protocol,
        db,
        load_json,
        mockserver,
        ca_code,
        all_payments_available,
        available_cards,
        code,
        pricing_data_preparer,
):
    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def _mock_ca_payment_availability(request):
        assert request.args.to_dict() == {
            'user_id': 'user_id_1',
            'card_id': 'card-x5619',
            'yandex_uid': '4003514353',
        }
        response = {
            'all_payments_available': all_payments_available,
            'available_cards': available_cards,
        }
        return mockserver.make_response(json.dumps(response), ca_code)

    request = load_json('card_request.json')
    order_id = order_commit_common.create_draft(taxi_protocol, request)
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    assert commit_resp.status_code == code
    if code == 406:
        assert commit_resp.json() == {'error': {'code': 'NEED_CARD_ANTIFRAUD'}}


@pytest.mark.experiments3(filename='use_card_antifraud.json')
def test_user_not_portal(taxi_protocol, db, load_json, pricing_data_preparer):

    db.users.update(
        {'_id': 'user_id_1'}, {'$set': {'yandex_uid_type': 'phonish'}},
    )

    request = load_json('card_request.json')
    order_id = order_commit_common.create_draft(taxi_protocol, request)
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    assert commit_resp.status_code == 200


@pytest.mark.experiments3(filename='use_card_antifraud.json')
def test_payment_method_not_card(
        taxi_protocol, load_json, pricing_data_preparer,
):

    request = load_json('card_request.json')
    request['payment'] = {'type': 'cash'}

    order_id = order_commit_common.create_draft(taxi_protocol, request)
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    assert commit_resp.status_code == 200


@pytest.mark.parametrize(
    'user_agent,code',
    [
        (
            'ru.yandex.taxi.inhouse/3.0.0 '
            '(iPhone; iPhone7,1; iOS 10.1.1; Darwin)',
            406,
        ),
        ('yandex-taxi/3.0.0 Android/7.0 (android test client)', 406),
        (
            'ru.yandex.taxi.inhouse/35.0.0 '
            '(iPhone; iPhone7,1; iOS 10.1.1; Darwin)',
            200,
        ),
        ('yandex-taxi/35.0.0 Android/7.0 (android test client)', 200),
    ],
    ids=[
        'iphone_match',
        'android_match',
        'iphone_mismatch',
        'android_mismatch',
    ],
)
@pytest.mark.experiments3(filename='use_card_antifraud.json')
def test_app_version_experiment(
        taxi_protocol,
        load_json,
        db,
        mockserver,
        user_agent,
        code,
        pricing_data_preparer,
):
    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def _mock_ca_payment_availability(request):
        assert request.args.to_dict() == {
            'user_id': 'user_id_1',
            'card_id': 'card-x5619',
            'yandex_uid': '4003514353',
        }
        response = {'all_payments_available': False, 'available_cards': []}
        return mockserver.make_response(json.dumps(response), 200)

    headers = {'User-Agent': user_agent}
    request = load_json('card_request.json')
    order_id = order_commit_common.create_draft(
        taxi_protocol, request, headers=headers,
    )
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    assert commit_resp.status_code == code


@pytest.mark.experiments3(filename='use_card_antifraud.json')
@pytest.mark.translations(
    client_messages={
        'common_errors.NEED_CARD_ANTIFRAUD': {
            'ru': 'Требуется верификация карты',
        },
    },
)
def test_error_text_translation(taxi_protocol, load_json, mockserver):
    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def _mock_ca_payment_availability(request):
        assert request.args.to_dict() == {
            'user_id': 'user_id_1',
            'card_id': 'card-x5619',
            'yandex_uid': '4003514353',
        }
        response = {'all_payments_available': False, 'available_cards': []}
        return mockserver.make_response(json.dumps(response), 200)

    request = load_json('card_request.json')

    order_id = order_commit_common.create_draft(taxi_protocol, request)
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    assert commit_resp.status_code == 406
    assert commit_resp.json() == {
        'error': {
            'code': 'NEED_CARD_ANTIFRAUD',
            'text': 'Требуется верификация карты',
        },
    }


@pytest.mark.experiments3(filename='use_card_antifraud.json')
def test_login_id(
        taxi_protocol, db, load_json, mockserver, pricing_data_preparer,
):
    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def mock_ca_payment_availability(request):
        assert request.args.to_dict() == {
            'user_id': 'user_id_1',
            'card_id': 'card-x5619',
            'yandex_uid': '4003514353',
            'yandex_login_id': 't:1234',
        }
        response = {'all_payments_available': True, 'available_cards': []}
        return response

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert 'get_login_id=yes' in query
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'login_id': 't:1234',
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    request = load_json('card_request.json')
    order_id = order_commit_common.create_draft(
        taxi_protocol, request, bearer='test_token', x_real_ip='my-ip-address',
    )
    commit_resp = order_commit_common.commit_order(
        taxi_protocol,
        order_id,
        request,
        bearer='test_token',
        x_real_ip='my-ip-address',
    )
    assert commit_resp.status_code == 200
    assert mock_ca_payment_availability.has_calls is True
    assert mock_blackbox.has_calls is True
