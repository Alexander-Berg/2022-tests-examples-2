# pylint: disable=too-many-lines

import copy
import datetime
import re
from typing import Dict
from typing import Union

import dateutil.parser
import pytest

from tests_cardstorage import common

CARD_LPM_FALLBACK = 'card.list-payment-methods'

CARD_X234 = 'card-x2345b3e693972872b9b58946'
CARD_X717 = 'card-x717eb3e693972872b9b5a317'
CARD_X987 = 'card-x9876b3e693972872b9b50087'
CARD_X008 = 'card-x0000000000000008'
CARD_X009 = 'card-x0000000000000009'
CARD_X010 = 'card-x0000000000000010'

# pylint: disable=invalid-name
tvm_ticket = pytest.mark.tvm2_ticket(
    {234: 'ticket', 456: 'ticket', 777: 'stat_ticket'},
)


@pytest.fixture(name='trust_service')
def _trust_service(mockserver, load_json):
    class Context:
        def __init__(self):
            self.mock_settings: Dict[str, Union[str, float]] = {}

        def setup_mock_settings(
                self,
                response,
                uid='123',
                is_uber=False,
                check_ticket=False,
                timeout_once=False,
                response_code=200,
                login_id=None,
        ):
            if isinstance(response, str):
                response = load_json(response)
            self.mock_settings['response'] = response
            self.mock_settings['uid'] = uid
            self.mock_settings['is_uber'] = is_uber
            self.mock_settings['check_ticket'] = check_ticket
            self.mock_settings['timeout_once'] = timeout_once
            self.mock_settings['response_code'] = response_code
            self.mock_settings['login_id'] = login_id

    ctx = Context()

    def check_headers(request):
        token = (
            'ubertaxi_4ea0f5fc283dc942c27bc7ae022e8821'
            if ctx.mock_settings['is_uber']
            else 'taxifee_8c7078d6b3334e03c1b4005b02da30f4'
        )
        assert request.headers['X-Uid'] == ctx.mock_settings['uid']
        assert request.headers['X-Service-Token'] == token
        if ctx.mock_settings['check_ticket']:
            assert request.headers['X-Ya-Service-Ticket'] == 'ticket'
        if ctx.mock_settings['login_id'] is not None:
            assert (
                request.headers['X-Login-Id'] == ctx.mock_settings['login_id']
            )

    @mockserver.json_handler('/trust-atlas/bindings/')
    async def _bindings_handler(request):
        check_headers(request)
        if ctx.mock_settings['timeout_once']:
            ctx.mock_settings['timeout_once'] = False
            raise mockserver.TimeoutError
        if not ctx.mock_settings['response']:
            return {'bindings': []}
        return mockserver.make_response(
            json=ctx.mock_settings['response'],
            status=ctx.mock_settings['response_code'],
        )

    @mockserver.json_handler('/trust/' + CARD_X234 + '/labels')
    def _handle_x234_label(request):
        check_headers(request)
        return {'status': 'success'}

    @mockserver.json_handler('/trust/' + CARD_X717 + '/labels')
    def _handle_x717_label(request):
        check_headers(request)
        return {'status': 'success'}

    return ctx


@pytest.mark.config(
    TVM_ENABLED=True, CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0,
)
@tvm_ticket
@pytest.mark.parametrize('tvm, code', [(False, 401), (True, 200)])
async def test_access(tvm, code, taxi_cardstorage, trust_service, statistics):
    trust_service.setup_mock_settings(
        'trust_response_card-x717.json', check_ticket=True,
    )
    body = {'yandex_uid': '123'}
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET if tvm else ''}
    response = await taxi_cardstorage.post(
        'v1/payment_methods', json=body, headers=headers,
    )
    assert response.status_code == code


@pytest.mark.config(
    CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0,
    CARDSTORAGE_USE_YANDEX_CARDS_CACHE_PROBABILITY=1.0,
)
@pytest.mark.filldb(payment_methods='for_test_list_payment_methods')
@tvm_ticket
@pytest.mark.parametrize(
    'is_uber,requests', [(False, 1), (True, 1), (False, 5), (True, 5)],
)
async def test_list_payment_methods(
        taxi_cardstorage, mongodb, trust_service, load_json, is_uber, requests,
):
    trust_service.setup_mock_settings(
        'trust_response_card_and_yabank_wallet.json',
        uid='789',
        is_uber=is_uber,
    )

    def fetch_card_from_mongo():
        return mongodb.cards.find_one({'number': '400000****1139'}, {'_id': 0})

    assert fetch_card_from_mongo() is None

    body = {'yandex_uid': '789', 'yandex_login_id': 'some_login_id'}
    if is_uber:
        body['service_type'] = 'uber'

    for _ in range(requests):
        response = await taxi_cardstorage.post('v1/payment_methods', json=body)
        assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['available_cards']) == 1
    body = response_json['available_cards'][0]
    persistent_id = body.pop('persistent_id')
    # No persistent id in card labels, so service creates random one (uuid4)
    label = body.pop('service_labels')[0]
    uuid = 'uber:[0-9a-f]{32}' if is_uber else '[0-9a-f]{32}'
    assert re.match(uuid, persistent_id)
    assert re.match('taxi:persistent_id:' + uuid, label)

    assert body.pop('updated_at') is not None
    assert response_json == load_json(
        'expected_response_card_and_yabank_wallet.json',
    )

    stored = load_json('storage/card-x717.json')
    stored['service_labels'].append(label)
    stored['persistent_id'] = persistent_id
    stored['expiration_date'] = datetime.datetime(year=2022, month=5, day=1)

    record = mongodb.cards.find_one({'number': '400000****1139'}, {'_id': 0})
    assert record.pop('created') < datetime.datetime.utcnow()
    assert record.pop('updated') < datetime.datetime.utcnow()
    record.pop('verification_levels')
    assert record == stored
    _check_payment_methods(mongodb, load_json, is_uber)


def _check_payment_methods(mongodb, load_json, is_uber):
    methods = list(
        mongodb.payment_methods.find(
            {
                'uid': '789',
                'login_id': 'some_login_id',
                'type': 'yabank_wallet',
            },
        ).sort([('payment_method_id', 1), ('service_type', 1)]),
    )
    if is_uber:
        assert len(methods) == 6
        _assert_same_payment_methods(
            methods[0],
            load_json('storage/yabank_wallet-some_yabank_wallet_id.json'),
        )
        _assert_same_payment_methods(
            methods[1],
            load_json('storage/yabank_wallet-some_uber_yabank_wallet_id.json'),
        )
        _assert_same_payment_methods(
            methods[2],
            load_json('storage/yabank_wallet-to_delete_yabank_wallet_id.json'),
        )
        _assert_same_payment_methods(
            methods[3],
            load_json(
                'storage/yabank_wallet-to_insert_uber_yabank_wallet_id.json',
            ),
        )
        _assert_same_payment_methods(
            methods[4],
            load_json(
                (
                    'storage/yabank_wallet-to_update'
                    '_unchanged_yabank_wallet_id.json'
                ),
            ),
        )
        _assert_same_payment_methods(
            methods[5],
            load_json(
                'storage/yabank_wallet-to_update_uber_yabank_wallet_id.json',
            ),
        )

    else:
        assert len(methods) == 3
        _assert_same_payment_methods(
            methods[0],
            load_json('storage/yabank_wallet-some_yabank_wallet_id.json'),
        )
        _assert_same_payment_methods(
            methods[1],
            load_json('storage/yabank_wallet-to_insert_yabank_wallet_id.json'),
        )
        _assert_same_payment_methods(
            methods[2],
            load_json('storage/yabank_wallet-to_update_yabank_wallet_id.json'),
        )


def _assert_same_payment_methods(actual, expected):
    assert _prepare_payment_method(actual) == _prepare_payment_method(expected)


def _prepare_payment_method(payment_method):
    result = copy.deepcopy(payment_method)
    result.pop('_id', None)
    result.pop('created_at', None)
    result.pop('updated_at', None)
    return result


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
@pytest.mark.parametrize('is_cached_on_error_allowed', [False, True])
async def test_on_error_returns_cached_if_allowed(
        taxi_cardstorage, trust_service, is_cached_on_error_allowed,
):
    trust_service.setup_mock_settings(
        'trust_response_with_verification_details.json',
        uid='789',
        response_code=200,
    )
    store_req_body = {'yandex_uid': '789', 'yandex_login_id': 'some_login_id'}
    store_req_response = await taxi_cardstorage.post(
        'v1/payment_methods', json=store_req_body,
    )

    trust_service.setup_mock_settings(
        response='expected_response_card_and_yabank_wallet.json',
        uid='789',
        response_code=502,
    )
    failed_get_req_body = {
        'yandex_uid': '789',
        'yandex_login_id': 'some_login_id',
        'always_return_cached_on_error': is_cached_on_error_allowed,
    }
    failed_get_req_response = await taxi_cardstorage.post(
        'v1/payment_methods', json=failed_get_req_body,
    )

    failed_get_req_json = failed_get_req_response.json()
    store_req_response_json = store_req_response.json()

    assert store_req_response.status_code == 200
    if is_cached_on_error_allowed:
        assert failed_get_req_response.status_code == 200
        assert failed_get_req_json['available_cards'][0]['from_db']
        assert (
            failed_get_req_json['available_cards'][0]['card_id']
            == store_req_response_json['available_cards'][0]['card_id']
        )
    else:
        assert failed_get_req_response.status_code != 200


@tvm_ticket
@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@pytest.mark.now('2019-08-26T14:11:22.123456Z')
async def test_list_payment_methods_stq_labels(
        taxi_cardstorage, mongodb, trust_service, load_json, mockserver, stq,
):
    @mockserver.json_handler('/trust/' + CARD_X717 + '/labels')
    def _handle_label(request):
        return {'status': 'success'}

    trust_service.setup_mock_settings(
        'trust_response_card-x717.json', uid='789',
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods', json={'yandex_uid': '789'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['available_cards']) == 1

    available_card = response_json['available_cards'][0]
    persistent_id = available_card.pop('persistent_id')
    # No persistent id in card labels, so service creates random one (uuid4)
    label = available_card.pop('service_labels')[0]
    assert re.match('[0-9a-f]{32}', persistent_id)
    assert re.match('taxi:persistent_id:[0-9a-f]{32}', label)

    assert available_card.pop('updated_at') is not None
    assert response_json == load_json('expected_response1.json')

    stored = load_json('storage/card-x717.json')
    stored['service_labels'].append(label)
    stored['persistent_id'] = persistent_id
    stored['expiration_date'] = datetime.datetime(year=2022, month=5, day=1)

    record = mongodb.cards.find_one({'number': '400000****1139'}, {'_id': 0})
    assert record.pop('created') < datetime.datetime.utcnow()
    assert record.pop('updated') < datetime.datetime.utcnow()
    assert record == stored

    assert _handle_label.times_called == 0
    assert stq.cardstorage_set_card_label.times_called == 1
    stq_call = stq.cardstorage_set_card_label.next_call()
    # link from handler, check for non-empty string
    link = stq_call['kwargs']['log_extra'].pop('_link')
    assert re.match('[0-9a-f]{32}', link)
    assert stq_call == {
        'queue': 'cardstorage_set_card_label',
        'id': '789:' + record['payment_id'] + ':' + label,
        'eta': datetime.datetime(2019, 8, 26, 14, 11, 22, 123456),
        'args': [],
        'kwargs': {
            'card_id': record['payment_id'],
            'owner_uid': '789',
            'service_type': 'card',
            'label': label,
            'log_extra': {},
        },
    }


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
async def test_cache_preferred(
        taxi_cardstorage, mongodb, trust_service, load_json,
):
    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={'yandex_uid': '123', 'cache_preferred': True},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response2.json')


@pytest.mark.config(CARDSTORAGE_DISABLE_TRUST_BINDINGS=True)
@pytest.mark.parametrize(
    'yandex_uid, expected_data_json',
    [
        ('123', 'expected_response2.json'),
        ('unknown_uid', 'empty_response.json'),
    ],
)
async def test_bindings_disabled(
        taxi_cardstorage, mongodb, load_json, yandex_uid, expected_data_json,
):
    response = await taxi_cardstorage.post(
        'v1/payment_methods', json={'yandex_uid': yandex_uid},
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_data_json)


@pytest.mark.config(CARDSTORAGE_DISABLE_TRUST_BINDINGS=True)
@pytest.mark.parametrize(
    'yandex_uid, expected_data_json, exp_value',
    [
        ('1337', 'expected_response5-experiment_enabled.json', True),
        ('1337', 'expected_response5-experiment_disabled.json', False),
    ],
)
async def test_full_card_id_experiment(
        taxi_cardstorage,
        experiments3,
        mongodb,
        load_json,
        yandex_uid,
        expected_data_json,
        exp_value,
):
    experiments3.add_experiment(
        name='enable_long_card_id',
        consumers=['cardstorage/paymentmethods'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': exp_value},
    )
    response = await taxi_cardstorage.post(
        'v1/payment_methods', json={'yandex_uid': yandex_uid},
    )
    assert response.status_code == 200
    expected_data = load_json(expected_data_json)
    assert response.json() == expected_data


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@pytest.mark.parametrize(
    'login_id,expected_data_json',
    [
        ('absent-login-id', 'no_details.json'),
        ('fresh-login-id', 'return_card_from_db.json'),
        ('old-login-id', 'return_card_from_trust.json'),
    ],
)
async def test_cached_verification_details(
        taxi_cardstorage,
        mongodb,
        trust_service,
        load_json,
        login_id,
        expected_data_json,
):
    yandex_uid = '12345'
    trust_service.setup_mock_settings(
        response='card_x0007_trust_response.json',
        uid=yandex_uid,
        login_id=login_id,
    )
    EXPECTED_CARD_ID = 'card-x0000000000000007'
    expected_data = load_json(expected_data_json)
    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': yandex_uid,
            'yandex_login_id': login_id,
            'cache_preferred': True,
            'renew_after': '2020-04-01T10:00:00.000000+00:00',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['available_cards']) == 1
    card = response_json['available_cards'][0]
    assert card['card_id'] == EXPECTED_CARD_ID
    actual_details = card.get('verification_details')
    assert actual_details == expected_data['details']
    assert card['from_db'] == expected_data['from_db']


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_compare_with_stored_card(
        taxi_cardstorage, mongodb, trust_service,
):
    trust_service.setup_mock_settings('trust_response_card-x717.json')

    mongodb.cards.delete_one({'owner_uid': '123'})
    response1 = await taxi_cardstorage.post(
        'v1/payment_methods', json={'yandex_uid': '123'},
    )
    assert response1.status_code == 200
    card1 = response1.json()['available_cards'][0]

    response2 = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={'yandex_uid': '123', 'cache_preferred': True},
    )
    assert response2.status_code == 200
    card2 = response2.json()['available_cards'][0]

    assert not card1.pop('from_db')
    assert card2.pop('from_db')
    assert card1.pop('regions_checked') == []
    assert card2.pop('regions_checked') == ['225']
    assert card1 == card2


@pytest.mark.parametrize(
    'trust_response_json,uid,card_id,field,old_value,new_value',
    [
        (
            'trust_response_card-x008.json',
            '123008',
            CARD_X008,
            'ebin_tags',
            [],
            ['tag1', 'tag2'],
        ),
        (
            'trust_response_card-x009.json',
            '123009',
            CARD_X009,
            'currency',
            'RUB',
            'USD',
        ),
    ],
)
@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_field_updated(
        taxi_cardstorage,
        mongodb,
        trust_service,
        trust_response_json,
        uid,
        card_id,
        field,
        old_value,
        new_value,
):
    trust_service.setup_mock_settings(trust_response_json, uid=uid)
    # Get card from cache, expect old value
    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={'yandex_uid': uid, 'cache_preferred': True},
    )
    _check_field(
        response, card_id=card_id, from_db=True, field=field, value=old_value,
    )
    # Get card from Trust, expect new value
    response = await taxi_cardstorage.post(
        'v1/payment_methods', json={'yandex_uid': uid},
    )
    _check_field(
        response, card_id=card_id, from_db=False, field=field, value=new_value,
    )
    # Get card from cache again, expect new value to persist
    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={'yandex_uid': uid, 'cache_preferred': True},
    )
    _check_field(
        response, card_id=card_id, from_db=True, field=field, value=new_value,
    )


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
@pytest.mark.parametrize('is_uber', [False, True])
async def test_uncommitted_label(
        taxi_cardstorage, mongodb, trust_service, load_json, is_uber,
):
    trust_service.setup_mock_settings(
        'trust_response_card-x234.json', '456', is_uber,
    )

    body = {'yandex_uid': '456'}
    if is_uber:
        body['service_type'] = 'uber'
        pid = 'uncommitted:persistent_id:uber:ce6431855e0df6e183f1cad57fc19999'
        update = {'$set': {'persistent_id': pid}}
        mongodb.cards.update_one({'owner_uid': '456'}, update)

    response = await taxi_cardstorage.post('v1/payment_methods', json=body)
    assert response.status_code == 200

    response_body = response.json()
    response_body['available_cards'][0].pop('updated_at')
    if is_uber:
        assert response_body == load_json('expected_response3_uber.json')
    else:
        assert response_body == load_json('expected_response3.json')

    record = mongodb.cards.find_one(
        {'owner_uid': '456'},
        {'_id': 0, 'created': 0, 'updated': 0, 'expiration_date': 0},
    )
    if is_uber:
        stored = load_json('storage/card-x234_uber.json')
    else:
        stored = load_json('storage/card-x234.json')
    assert record == stored


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_wrong_label(
        taxi_cardstorage, mongodb, trust_service, load_json,
):
    trust_service.setup_mock_settings('trust_response_card-x234_labeled.json')

    response = await taxi_cardstorage.post(
        'v1/payment_methods', json={'yandex_uid': '123'},
    )
    assert response.status_code == 200

    response_body = response.json()
    response_body['available_cards'][0].pop('updated_at')
    assert response_body == load_json('expected_response4.json')

    record = mongodb.cards.find_one(
        {'owner_uid': '123'},
        {'_id': 0, 'created': 0, 'updated': 0, 'expiration_date': 0},
    )
    stored = load_json('storage/card-x234_changed_id.json')
    assert record == stored


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
@pytest.mark.tvm2_ticket({234: 'ticket', 456: 'ticket'})
async def test_unbound_cards(
        taxi_cardstorage, mongodb, trust_service, load_json,
):
    for trust_response, is_bound, show_unbound in [
            (None, False, True),
            ('trust_response_card-x234.json', True, True),
            (None, False, False),
            ('trust_response_card-x234.json', True, False),
    ]:
        trust_service.setup_mock_settings(response=trust_response)
        response = await taxi_cardstorage.post(
            'v1/payment_methods',
            json={'yandex_uid': '123', 'show_unbound': show_unbound},
        )

        assert response.status_code == 200
        cards = response.json()['available_cards']

        if not is_bound and not show_unbound:
            assert not cards
        else:
            assert len(cards) == 1
            card = cards[0]
            assert card['card_id'] == CARD_X234
            assert card['owner'] == '123'
            if is_bound:
                assert card['bound']
            else:
                assert not card['bound']

        record = mongodb.cards.find_one({'owner_uid': '123'})
        assert record['payment_id'] == CARD_X234
        if is_bound:
            assert 'unbound' not in record
        else:
            assert record.pop('unbound')


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_mark_unavailable_bindings_true(taxi_cardstorage, trust_service):
    trust_service.setup_mock_settings(
        'trust_response_mark_unavailable_bindings_mir_hidden.json',
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'mark_unavailable_bindings': True,
            'currency': 'NOSUCHCURRENCY',
        },
    )

    assert response.status_code == 200
    cards = response.json()['available_cards']
    assert len(cards) == 1
    assert cards[0]['is_hidden']


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_show_psp_payment_method_ids(taxi_cardstorage, trust_service):
    trust_service.setup_mock_settings(
        'trust_response_show_psp_payment_method_ids.json',
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={'yandex_uid': '123', 'show_psp_payment_method_ids': True},
    )

    assert response.status_code == 200
    cards = response.json()['available_cards']
    assert len(cards) == 1
    assert cards[0]['psp_payment_method_id'] == 'some_psp_payment_method_id'


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_mark_unavailable_bindings_false(
        taxi_cardstorage, trust_service,
):
    trust_service.setup_mock_settings(
        'trust_response_mark_unavailable_bindings_mir_not_hidden.json',
    )
    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'mark_unavailable_bindings': True,
            'currency': 'RUB',
        },
    )

    assert response.status_code == 200
    cards = response.json()['available_cards']
    assert len(cards) == 1
    assert not cards[0]['is_hidden']


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_mark_unavailable_bindings_empty_props_false(
        taxi_cardstorage, trust_service,
):
    trust_service.setup_mock_settings(
        'trust_response_mark_unavailable_empty_properties_response.json',
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'mark_unavailable_bindings': True,
            'currency': 'RUB',
        },
    )
    assert response.status_code == 200
    cards = response.json()['available_cards']
    assert len(cards) == 1
    assert not cards[0]['is_hidden']


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_mark_unavailable_bindings_hide_yabank_true(
        taxi_cardstorage, trust_service,
):
    trust_service.setup_mock_settings(
        'trust_response_mark_unavailable_hide_yabank_wallet.json',
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'mark_unavailable_bindings': True,
            'currency': 'NOSUCHCURRENCY',
        },
    )
    assert response.status_code == 200
    cards = response.json()['yandex_cards']['available_cards']
    assert len(cards) == 1
    assert cards[0]['is_hidden']


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_mark_unavailable_bindings_true_cache_preffered_do_not_hide(
        taxi_cardstorage, trust_service,
):
    trust_service.setup_mock_settings(
        'trust_response_mark_unavailable_bindings_mir_hidden.json',
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'mark_unavailable_bindings': True,
            'currency': 'NOSUCHCURRENCY',
        },
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'mark_unavailable_bindings': True,
            'currency': 'NOSUCHCURRENCY',
            'cache_preferred': True,
        },
    )

    assert response.status_code == 200
    cards = response.json()['available_cards']
    assert len(cards) == 1
    assert 'is_hidden' not in cards[0]


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_mark_unavailable_bindings_true_trust_error_do_not_hide(
        taxi_cardstorage, trust_service,
):
    trust_service.setup_mock_settings(
        'trust_response_mark_unavailable_bindings_mir_hidden.json',
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'mark_unavailable_bindings': True,
            'currency': 'NOSUCHCURRENCY',
        },
    )

    trust_service.setup_mock_settings(
        response='trust_response_mark_unavailable_bindings_mir_hidden.json',
        response_code=502,
    )

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'mark_unavailable_bindings': True,
            'currency': 'NOSUCHCURRENCY',
            'always_return_cached_on_error': True,
        },
    )

    assert response.status_code == 200
    cards = response.json()['available_cards']
    assert len(cards) == 1
    assert 'is_hidden' not in cards[0]


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_unverified_cards(
        taxi_cardstorage, mongodb, trust_service, load_json,
):
    trust_service.setup_mock_settings('trust_response_with_unverified.json')

    statuses = {CARD_X234: False, CARD_X987: True}

    def check_unverified_status(cards):
        card_statuses = statuses.copy()
        for card in cards:
            card_id = card['card_id']
            assert card['unverified'] == card_statuses[card_id]
            card_statuses.pop(card_id)
        assert not card_statuses

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={'yandex_uid': '123', 'show_unverified': True},
    )
    assert response.status_code == 200
    check_unverified_status(response.json()['available_cards'])

    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={
            'yandex_uid': '123',
            'show_unverified': True,
            'cache_preferred': True,
        },
    )
    assert response.status_code == 200
    check_unverified_status(response.json()['available_cards'])

    record_statuses = statuses.copy()
    for record in mongodb.cards.find({'owner_uid': '123'}):
        card_id = record['payment_id']
        if record_statuses[card_id]:
            assert record['unverified']
        else:
            assert 'unverified' not in record
        record_statuses.pop(card_id)
    assert not record_statuses

    trust_service.setup_mock_settings('trust_response_card-x234.json')
    response = await taxi_cardstorage.post(
        'v1/payment_methods',
        json={'yandex_uid': '123', 'show_unverified': False},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['available_cards']) == 1
    card = response_json['available_cards'][0]
    assert card['card_id'] == CARD_X234
    assert not card['unverified']

    # Make sure that unverified card was not marked as unbound
    record = mongodb.cards.find_one(
        {'owner_uid': '123', 'payment_id': CARD_X987},
    )
    assert record['unverified']
    assert 'unbound' not in record


_CARD_LPM = 'card.list-payment-methods.%s'


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
@pytest.mark.parametrize(
    'trust_response, fallbacks, response_code, from_db, yandex_cards, '
    'new_stat',
    [
        ('ok', [], 200, False, [], {_CARD_LPM % 'success': 1}),
        ('timeout_once', [], 200, False, [], {_CARD_LPM % 'success': 1}),
        ('error', [], 502, None, [], {_CARD_LPM % 'error': 1}),
        (
            'error',
            ['uber.list-payment-methods'],
            502,
            None,
            [],
            {_CARD_LPM % 'error': 1},
        ),
        (
            'ok',
            [CARD_LPM_FALLBACK],
            200,
            False,
            [],
            {_CARD_LPM % 'success': 1},
        ),
        (
            'timeout_once',
            [CARD_LPM_FALLBACK],
            200,
            True,
            [],
            {_CARD_LPM % 'error': 1},
        ),
        pytest.param(
            'timeout_once',
            [CARD_LPM_FALLBACK],
            200,
            True,
            [{'id': 'yabank_wallet-some_yabank_wallet_id', 'currency': 'RUB'}],
            {_CARD_LPM % 'error': 1},
            marks=[
                pytest.mark.config(
                    CARDSTORAGE_USE_YANDEX_CARDS_CACHE_PROBABILITY=1.0,
                ),
            ],
        ),
    ],
)
async def test_fallback_statistics_service(
        taxi_cardstorage,
        trust_service,
        statistics,
        trust_response,
        fallbacks,
        response_code,
        from_db,
        yandex_cards,
        new_stat,
):
    trust_response_code = 500 if trust_response == 'error' else 200
    trust_timeout_once = trust_response == 'timeout_once'
    trust_service.setup_mock_settings(
        'trust_response_card-x234.json',
        timeout_once=trust_timeout_once,
        response_code=trust_response_code,
    )
    statistics.fallbacks = fallbacks

    async with statistics.capture(taxi_cardstorage) as capture:
        response = await taxi_cardstorage.post(
            'v1/payment_methods',
            json={'yandex_uid': '123', 'yandex_login_id': 'some_login_id'},
        )
    assert response.status_code == response_code
    if from_db is not None:
        for card in response.json()['available_cards']:
            assert card['from_db'] is from_db
    if yandex_cards:
        assert (
            response.json()['yandex_cards']['available_cards'] == yandex_cards
        )
    else:
        if response.status_code == 200:
            assert 'yandex_cards' not in response.json()
    for metric, value in new_stat.items():
        assert capture.statistics[metric] == value


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
async def test_legacy_format(
        taxi_cardstorage, mongodb, trust_service, load_json,
):
    trust_service.setup_mock_settings('trust_response_with_unverified.json')
    body = {'yandex_uid': '123', 'format': 'legacy'}
    response = await taxi_cardstorage.post('v1/payment_methods', json=body)

    assert response.status_code == 200
    assert response.json() == load_json('expected_response_legacy_format.json')


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
@pytest.mark.parametrize(
    'override_fallbacks, fallbacks_to_override,'
    ' service_fallbacks, fallback_mode,',
    [
        (True, [], [CARD_LPM_FALLBACK], False),
        (False, [], [CARD_LPM_FALLBACK], True),
        (True, [CARD_LPM_FALLBACK], [], True),
        (True, [], [CARD_LPM_FALLBACK], False),
        (True, ['uber.list-payment-methods'], [CARD_LPM_FALLBACK], False),
    ],
)
async def test_fallbacks_override(
        taxi_cardstorage,
        trust_service,
        statistics,
        override_fallbacks,
        fallbacks_to_override,
        service_fallbacks,
        fallback_mode,
        taxi_config,
):
    trust_service.setup_mock_settings(
        'trust_response_card-x234.json', response_code=503,
    )
    statistics.fallbacks = service_fallbacks
    taxi_config.set(
        STATISTICS_FALLBACK_OVERRIDES=[
            {
                'service': 'cardstorage',
                'enabled': override_fallbacks,
                'fallbacks': fallbacks_to_override,
            },
        ],
    )
    body = {'yandex_uid': '123'}
    response = await taxi_cardstorage.post('v1/payment_methods', json=body)
    if fallback_mode:
        assert response.status_code == 200
        cards = response.json()['available_cards']
        assert len(cards) > 0  # pylint: disable=len-as-condition
        for card in cards:
            assert card['from_db'] is True, cards
    else:
        assert response.status_code == 502


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@pytest.mark.parametrize('send_statistics', [True, False])
async def test_fallbacks_disable_send(
        taxi_cardstorage,
        statistics,
        taxi_config,
        send_statistics,
        trust_service,
):
    taxi_config.set(STATISTICS_ENABLE_SEND=send_statistics)
    trust_service.setup_mock_settings('trust_response_card-x234.json')
    body = {'yandex_uid': '123'}
    async with statistics.capture(taxi_cardstorage) as capture:
        response = await taxi_cardstorage.post('v1/payment_methods', json=body)
        assert response.status_code == 200
    if send_statistics:
        assert capture.statistics
    else:
        assert not capture.statistics


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@pytest.mark.parametrize('login_id', ['some-login-id', None])
async def test_login_id_is_passed(taxi_cardstorage, trust_service, login_id):
    trust_service.setup_mock_settings(
        response='trust_response_with_verification_details.json',
        login_id=login_id,
    )
    body = {'yandex_uid': '123'}
    if login_id is not None:
        body['yandex_login_id'] = login_id
    response = await taxi_cardstorage.post('v1/payment_methods', json=body)
    assert response.status_code == 200


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
async def test_empty_login_id(taxi_cardstorage, trust_service):
    login_id = ''
    trust_service.setup_mock_settings(
        response='trust_response_card-x234.json', login_id=login_id,
    )
    body = {'yandex_uid': '123', 'yandex_login_id': login_id}
    response = await taxi_cardstorage.post('v1/payment_methods', json=body)
    assert response.status_code == 400


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
@pytest.mark.parametrize('is_legacy', [False, True])
@pytest.mark.parametrize('is_insert', [False, True])
@pytest.mark.parametrize(
    'trust_response,yandex_uid,is_cache_preferred,'
    'is_family,is_invalid,is_unverified',
    [
        pytest.param(
            'trust_response_card_with_family_info.json',
            '123450',  # member
            False,  # is_cache_preferred
            True,  # is_family
            False,  # is_invalid
            False,  # is_unverified
            id='member_uid',
        ),
        pytest.param(
            'trust_response_card_with_family_info.json',
            '123450',  # member
            True,  # is_cache_preferred
            True,  # is_family
            False,  # is_invalid
            False,  # is_unverified
            id='member_uid_cached',
        ),
        pytest.param(
            'trust_response_card_wo_family_info_owner.json',
            '567890',  # owner
            False,  # is_cache_preferred
            True,  # is_family
            False,  # is_invalid
            False,  # is_unverified
            id='owner_uid',
        ),
        pytest.param(
            'trust_response_card_wo_family_info_owner.json',
            '567890',  # owner
            True,  # is_cache_preferred
            True,  # is_family
            False,  # is_invalid
            False,  # is_unverified
            id='owner_uid_cached',
        ),
        # no payer_info from trust -> no family info, no payer_info in db
        pytest.param(
            'trust_response_card_no_payer_info.json',
            '567890',  # owner
            False,  # is_cache_preferred
            False,  # is_family
            False,  # is_invalid
            False,  # is_unverified
            id='owner_no_payer_info',
        ),
        # incomplete payer_info from trust -> same as previous
        pytest.param(
            'trust_response_card_with_family_info_empty.json',
            '567890',  # owner
            False,  # is_cache_preferred
            False,  # is_family
            False,  # is_invalid
            False,  # is_unverified
            id='owner_empty_payer_info',
        ),
        # cached && valid: false && owner  -> seen as unverified
        pytest.param(
            'trust_response_card_wo_family_info_owner.json',
            '567890',  # owner
            True,  # is_cache_preferred
            True,  # is_family
            True,  # is_invalid
            False,  # is_unverified
            id='owner_uid_cached_invalid',
        ),
        # unverified by trust && owner -> seen as unverified
        pytest.param(
            'trust_response_card_wo_family_info_owner.json',
            '567890',  # owner
            False,  # is_cache_preferred
            True,  # is_family
            False,  # is_invalid
            True,  # is_unverified
            id='owner_uid_unverified',
        ),
        # unverified by trust && member -> not seen
        pytest.param(
            'trust_response_card_with_family_info.json',
            '123450',  # member
            False,  # is_cache_preferred
            True,  # is_family
            False,  # is_invalid
            True,  # is_unverified
            id='member_uid_unverified',
        ),
    ],
)
async def test_payer_info(
        taxi_cardstorage,
        mongodb,
        is_legacy,
        is_insert,
        trust_service,
        is_cache_preferred,
        load_json,
        trust_response,
        yandex_uid,
        is_family,
        is_invalid,
        is_unverified,
):
    is_owner = yandex_uid == '567890'
    trust_response = load_json(trust_response)
    if is_unverified:
        for binding in trust_response['bindings']:
            binding['unverified'] = True
    trust_service.setup_mock_settings(trust_response, uid=yandex_uid)

    MONGO_QUERY = {'payment_id': CARD_X717, 'owner_uid': yandex_uid}

    def fetch_card_from_mongo():
        return mongodb.cards.find_one(MONGO_QUERY, {'_id': 0})

    if is_insert:
        assert mongodb.cards.delete_one(MONGO_QUERY).deleted_count == 1
        assert fetch_card_from_mongo() is None
    else:
        assert fetch_card_from_mongo() is not None
        if is_invalid:
            mongodb.cards.update_one(MONGO_QUERY, {'$set': {'valid': False}})

    body = {'yandex_uid': yandex_uid}
    if is_cache_preferred:
        body['cache_preferred'] = True
    if is_legacy:
        body['format'] = 'legacy'
    if is_unverified:
        body['show_unverified'] = True

    response = await taxi_cardstorage.post('v1/payment_methods', json=body)
    assert response.status_code == 200
    response_json = response.json()

    field = None
    if is_insert and is_cache_preferred:
        assert response_json == {'available_cards': []}
        return

    if is_legacy:
        # unverified or invalid not shown for member (for legacy)
        # (by default shown in available_cards with unverified: true)
        if not is_owner and (is_invalid or is_unverified):
            assert response_json == {'available_cards': []}
            return
        field = 'unverified_cards' if is_unverified else 'available_cards'
    else:
        field = 'available_cards'

    # payer_info -> family in response
    assert len(response_json[field]) == 1
    response_card = response_json[field][0]
    if is_family:
        if not is_owner:
            assert response_card['family'] == {
                'is_owner': False,
                'owner_uid': '567890',
                'expenses': 32000,
                'frame': 'month',
                'limit': 123400,
                'currency': 'RUB',
            }
        else:
            assert response_card['family'] == {'is_owner': True}
    else:
        assert 'family' not in response_card

    trust_payer_info = trust_response['bindings'][0].get('payer_info')
    # payer_info in db stored as-is
    stored_card = fetch_card_from_mongo()
    if trust_payer_info:
        assert stored_card['payer_info'] == trust_payer_info
    else:
        assert 'payer_info' not in stored_card


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
@pytest.mark.parametrize('is_legacy', [False, True])
@pytest.mark.parametrize('is_cache_preferred', [False, True])
@pytest.mark.parametrize('is_insert', [False, True])
@pytest.mark.parametrize(
    'trust_response_json',
    [
        pytest.param(
            # Matches card in cache
            'trust_response_card_with_partner_info.json',
            id='with_yandex_card_info',
        ),
        pytest.param(
            # Differs from card in cache
            'trust_response_card_wo_partner_info.json',
            id='wo_yandex_card_info',
        ),
    ],
)
async def test_partner_info(
        taxi_cardstorage,
        mongodb,
        trust_service,
        load_json,
        is_legacy,
        is_cache_preferred,
        is_insert,
        trust_response_json,
):
    YANDEX_UID = '000010'
    CARD = CARD_X010
    MONGO_QUERY = {'payment_id': CARD, 'owner_uid': YANDEX_UID}

    def fetch_card_from_mongo():
        return mongodb.cards.find_one(MONGO_QUERY, {'_id': 0})

    def prepare_mongo():
        if is_insert:
            assert mongodb.cards.delete_one(MONGO_QUERY).deleted_count == 1
            assert fetch_card_from_mongo() is None
        else:
            assert fetch_card_from_mongo() is not None

    def cardstorage_yandex_card_metadata(source):
        """
        Converts cache doc or trust response to cardstorage yandex_card flags
        """
        card_partner_info = source.get('partner_info')
        if card_partner_info is None:
            return None
        if not card_partner_info['is_yabank_card']:
            return None
        result = {}
        if 'is_fake_yabank_card' in card_partner_info:
            result['is_fake'] = card_partner_info['is_fake_yabank_card']
        if 'is_yabank_card_owner' in card_partner_info:
            result['is_owner'] = card_partner_info['is_yabank_card_owner']
        return result

    async def make_request(is_cache_preferred, is_legacy):
        body = {'yandex_uid': YANDEX_UID}
        if is_cache_preferred:
            body['cache_preferred'] = True
        if is_legacy:
            body['format'] = 'legacy'
        response = await taxi_cardstorage.post('v1/payment_methods', json=body)
        assert response.status_code == 200
        return response.json()

    def check_updated_cache(expected_response_metadata):
        updated_cache_card = fetch_card_from_mongo()
        assert updated_cache_card is not None
        cache_metadata = cardstorage_yandex_card_metadata(updated_cache_card)
        assert expected_response_metadata == cache_metadata

    trust_response = load_json(trust_response_json)
    trust_service.setup_mock_settings(trust_response, uid=YANDEX_UID)
    prepare_mongo()

    expected_metadata_source = (
        fetch_card_from_mongo()
        if is_cache_preferred and not is_insert
        else trust_response['bindings'][0]
    )
    assert expected_metadata_source is not None
    expected_metadata = cardstorage_yandex_card_metadata(
        expected_metadata_source,
    )

    response = await make_request(
        is_cache_preferred=is_cache_preferred, is_legacy=is_legacy,
    )

    if is_insert and is_cache_preferred:
        assert response == {'available_cards': []}
        return

    cardstorage_card = response['available_cards'][0]
    assert expected_metadata == cardstorage_card.get('yandex_card')

    if not is_cache_preferred:
        check_updated_cache(expected_response_metadata=expected_metadata)


@pytest.mark.config(CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0)
@tvm_ticket
@pytest.mark.parametrize('is_legacy', [False, True])
@pytest.mark.parametrize(
    'trust_response,exp_value,expected_wallet_ids',
    [
        pytest.param(
            'trust_response_for_yandex_card_wallet_substitution_1.json',
            {'enabled': False, 'replace_yandex_cards': False},
            [
                'yabank_wallet-some_yabank_wallet_id',
                'yabank_wallet-to_update_yabank_wallet_id',
                'yabank_wallet-to_insert_yabank_wallet_id',
            ],
            id='exp_disabled',
        ),
        pytest.param(
            'trust_response_for_yandex_card_wallet_substitution_1.json',
            {'enabled': True, 'replace_yandex_cards': False},
            [
                'yabank_wallet-some_yabank_wallet_id',
                'yabank_wallet-to_update_yabank_wallet_id',
                'yabank_wallet-to_insert_yabank_wallet_id',
                'card-x000000000000000000000123',
            ],
            id='exp_add',
        ),
        pytest.param(
            'trust_response_for_yandex_card_wallet_substitution_1.json',
            {'enabled': True, 'replace_yandex_cards': True},
            ['card-x000000000000000000000123'],
            id='exp_replace',
        ),
        pytest.param(
            'trust_response_for_yandex_card_wallet_substitution_1.json',
            {
                'enabled': True,
                'replace_yandex_cards': False,
                'hide_virtual_cards': True,
            },
            [
                'yabank_wallet-some_yabank_wallet_id',
                'yabank_wallet-to_update_yabank_wallet_id',
                'yabank_wallet-to_insert_yabank_wallet_id',
            ],
            id='exp_hide',
        ),
        pytest.param(
            'trust_response_for_yandex_card_wallet_substitution_2.json',
            {'enabled': True, 'replace_yandex_cards': False},
            ['card-x000000000000000000000123'],
            id='exp_add_no_wallet',
        ),
    ],
)
async def test_yandex_card_wallet_substitution(
        taxi_cardstorage,
        trust_service,
        experiments3,
        trust_response,
        is_legacy,
        exp_value,
        expected_wallet_ids,
):
    YANDEX_UID = '123'
    YANDEX_LOGIN_ID = 'some_login_id'
    CARD_WITH_YANDEX_CARD_FLAG_ID = 'card-x000000000000000000000123'
    STANDARD_CARD_ID = 'card-x717eb3e693972872b9b5a317'

    trust_service.setup_mock_settings(trust_response, uid=YANDEX_UID)

    experiments3.add_experiment(
        name='yandex_card_wallet_substitution',
        consumers=['cardstorage/card'],
        match={'enabled': True, 'predicate': {'type': 'true', 'init': {}}},
        clauses=[],
        default_value=exp_value,
    )
    exp_enabled = exp_value['enabled']
    should_hide_card = exp_value.get('hide_virtual_cards', False)

    async def make_request():
        body = {
            'yandex_uid': YANDEX_UID,
            'yandex_login_id': YANDEX_LOGIN_ID,
            'cache_preferred': False,
        }
        if is_legacy:
            body['format'] = 'legacy'
        response = await taxi_cardstorage.post('v1/payment_methods', json=body)
        assert response.status_code == 200
        return response.json()

    def card_ids(cards):
        if is_legacy:
            return [i['id'] for i in cards]
        return [i['card_id'] for i in cards]

    def wallet_ids(wallets):
        return [i['id'] for i in wallets]

    def check_cards(response):
        cards = response['available_cards']
        if exp_enabled or should_hide_card:
            assert CARD_WITH_YANDEX_CARD_FLAG_ID not in card_ids(cards)
            assert STANDARD_CARD_ID in card_ids(cards)
            return

        assert CARD_WITH_YANDEX_CARD_FLAG_ID in card_ids(cards)
        assert STANDARD_CARD_ID in card_ids(cards)

    def check_wallets(response):
        wallets = []
        if 'yandex_cards' in response:
            wallets = response['yandex_cards']['available_cards']
        assert wallet_ids(wallets) == expected_wallet_ids

    response = await make_request()
    check_cards(response)
    check_wallets(response)

    await taxi_cardstorage.invalidate_caches()


@pytest.mark.config(
    CARDSTORAGE_MAX_CACHED_VERIFICATION_LEVELS=4,
    CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-04-01T00:00:00.000000Z')
@pytest.mark.parametrize(
    'trust_response_json,expected_code,expected_verification_levels_json',
    [
        # No verification details - this is a Trust error, return 502
        ('no_verification_details.json', 502, None),
        # Empty verification details - this is a Trust error, return 502
        ('empty_verification_details.json', 502, None),
        # Malformed verification details - this is a Trust error, return 502
        ('null_verification_details.json', 502, None),
        # Malformed verification details - this is a Trust error, return 502
        ('string_verification_details.json', 502, None),
        # Malformed verification details - this is a Trust error, return 502
        ('array_verification_details.json', 502, None),
        # Unknown verification details, store them to db
        ('unknown_verification_details.json', 200, 'fresh_unknown_level.json'),
        # 3ds verification details, store them to db
        ('3ds_verification_details.json', 200, 'fresh_3ds_level.json'),
        # Unknown verification level but it's already stored, expect no changes
        (
            'still_unknown_verification_details.json',
            200,
            'still_unknown_level.json',
        ),
        # Verification details with changed service_id, store them to db
        (
            'changed_service_id_verification_details.json',
            200,
            'changed_service_id_level.json',
        ),
        # Verification details with changed verified_at, store them to db
        (
            'changed_verified_at_verification_details.json',
            200,
            'changed_verified_at_id_level.json',
        ),
        # New verification level for login id, expect no changes to other
        # levels
        ('new_level_verification_details.json', 200, 'new_level.json'),
        # Levels are at max capacity and some login is updated, expect this
        # login's level to update
        (
            'update_level_at_max_capacity_verification_details.json',
            200,
            'update_level_at_max_capacity.json',
        ),
        # Levels are at max capacity and nothing is updated
        (
            'no_update_at_max_capacity_verification_details.json',
            200,
            'no_update_at_max_capacity.json',
        ),
        # Levels are at max capacity and a new level is added. Expect the
        # oldest level to be evicted
        (
            'new_level_at_max_capacity_verification_details.json',
            200,
            'new_level_at_max_capacity.json',
        ),
        # Levels are at 2x max capacity and nothing is changed. Expect
        # max_capacity oldest levels to be evicted
        (
            'no_new_level_at_2x_max_capacity_verification_details.json',
            200,
            'no_new_level_at_2x_max_capacity.json',
        ),
        # Insert new card with unknown level
        (
            'new_unknown_verification_details.json',
            200,
            'fresh_unknown_level.json',
        ),
        # Insert new card with 3ds level
        ('new_3ds_verification_details.json', 200, 'fresh_3ds_level.json'),
    ],
)
async def test_verification_levels_are_stored(
        taxi_cardstorage,
        trust_service,
        mongodb,
        trust_response_json,
        expected_code,
        expected_verification_levels_json,
        load_json,
):
    await _check_verification_levels(
        taxi_cardstorage=taxi_cardstorage,
        trust_service=trust_service,
        mongodb=mongodb,
        load_json=load_json,
        yandex_uid='1234',
        login_id='some-login-id',
        expected_code=expected_code,
        trust_response_json=trust_response_json,
        expected_verification_levels_json=expected_verification_levels_json,
        expected_updated=None,
    )


@pytest.mark.config(
    CARDSTORAGE_MAX_CACHED_VERIFICATION_LEVELS=4,
    CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-04-01T00:00:00.000000Z')
async def test_verification_levels_are_not_stored(
        taxi_cardstorage, trust_service, mongodb, load_json,
):
    """
    Test that verification levels are not stored if there are no changes
    """
    dir_path = 'test_verification_levels_are_stored'
    trust_response_json = f'{dir_path}/still_unknown_verification_details.json'
    expected_verification_levels_json = f'{dir_path}/still_unknown_level.json'
    await _check_verification_levels(
        taxi_cardstorage=taxi_cardstorage,
        trust_service=trust_service,
        mongodb=mongodb,
        load_json=load_json,
        yandex_uid='1234',
        login_id='some-login-id',
        expected_code=200,
        trust_response_json=trust_response_json,
        expected_verification_levels_json=expected_verification_levels_json,
        expected_updated=datetime.datetime(2016, 12, 14, 10, 25, 5, 312000),
    )


@pytest.mark.config(
    CARDSTORAGE_MAX_CACHED_VERIFICATION_LEVELS=1,
    CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-04-01T00:00:00.000000Z')
async def test_max_cached_levels_config(
        taxi_cardstorage, trust_service, mongodb, load_json,
):
    dir_path = 'test_verification_levels_are_stored'
    trust_response_json = (
        f'{dir_path}/no_update_at_max_capacity_verification_details.json'
    )
    expected_verification_levels_json = f'{dir_path}/cvn_level.json'
    await _check_verification_levels(
        taxi_cardstorage=taxi_cardstorage,
        trust_service=trust_service,
        mongodb=mongodb,
        load_json=load_json,
        yandex_uid='1234',
        login_id='some-login-id',
        expected_code=200,
        trust_response_json=trust_response_json,
        expected_verification_levels_json=expected_verification_levels_json,
        expected_updated=None,
    )


async def _check_verification_levels(
        taxi_cardstorage,
        trust_service,
        mongodb,
        load_json,
        yandex_uid,
        login_id,
        expected_code,
        trust_response_json,
        expected_verification_levels_json,
        expected_updated,
):
    trust_service.setup_mock_settings(
        response=trust_response_json, uid=yandex_uid, login_id=login_id,
    )
    body = {'yandex_uid': yandex_uid, 'yandex_login_id': login_id}
    response = await taxi_cardstorage.post('v1/payment_methods', json=body)
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        assert len(response_json['available_cards']) == 1
        card = response_json['available_cards'][0]
        record = mongodb.cards.find_one(
            {'owner_uid': yandex_uid, 'payment_id': card['card_id']},
        )
        expected_verification_levels = _sorted_levels(
            load_json(expected_verification_levels_json),
        )
        actual_verification_levels = _sorted_levels(
            record['verification_levels'],
        )
        assert actual_verification_levels == expected_verification_levels
        _check_response_verification_details(
            card, actual_verification_levels, login_id,
        )
        if expected_updated is not None:
            assert record['updated'] == expected_updated


def _check_response_verification_details(
        card_json, verification_levels, login_id,
):
    actual_details = card_json.get('verification_details')
    levels_for_login = [
        level for level in verification_levels if level['login_id'] == login_id
    ]
    if actual_details is None:
        assert not levels_for_login
        return
    assert len(levels_for_login) == 1
    level = levels_for_login[0]
    del level['updated']
    assert level.pop('login_id') == login_id
    expected_response = {
        'level': level.pop('level'),
        'service_id': level.pop('service_id', None),
        'verified_at': level.pop('verified_at', None),
    }
    assert not level
    actual_response = {
        'level': actual_details.pop('level'),
        'service_id': actual_details.pop('service_id', None),
        'verified_at': actual_details.pop('verified_at', None),
    }
    if actual_response['verified_at'] is not None:
        actual_response['verified_at'] = _normalize_datetime(
            dateutil.parser.isoparse(actual_response['verified_at']),
        )
    assert not actual_details
    assert expected_response == actual_response


def _normalize_datetime(time):
    return time.replace(tzinfo=None).replace(
        microsecond=(time.microsecond // 1000) * 1000,
    )


def _sorted_levels(db_verification_levels):
    return sorted(db_verification_levels, key=lambda level: level['login_id'])


def _check_field(response, card_id, from_db, field, value):
    assert response.status_code == 200
    cards = response.json()['available_cards']
    assert len(cards) == 1
    assert cards[0]['card_id'] == card_id
    assert cards[0]['from_db'] == from_db
    assert cards[0][field] == value
