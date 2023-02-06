import pytest

from tests_cardstorage import common

CARD_X234 = 'card-x2345b3e693972872b9b58946'
BILLING_X234 = 'x2345b3e693972872b9b58946'
ALIAS_X234 = 'card-x2345'
CARD_WITH_VERIFICATION_LEVELS = 'card-x000000000000000000000001'
CARD_WITH_TAGS = 'card-x000000000000000000000002'


@pytest.mark.config(TVM_ENABLED=True)
@common.tvm_ticket
@pytest.mark.parametrize('tvm, code', [(False, 401), (True, 200)])
async def test_get_card_access(tvm, code, taxi_cardstorage):
    body = {'yandex_uid': '123', 'card_id': CARD_X234}
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET if tvm else ''}
    response = await taxi_cardstorage.post(
        'v1/card', json=body, headers=headers,
    )
    assert response.status_code == code


@pytest.mark.parametrize(
    'body,code',
    [
        ({'yandex_uid': '123'}, 400),
        ({'yandex_uid': '123', 'card_id': 'wrong'}, 404),
        ({'yandex_uid': '123', 'card_id': CARD_X234}, 200),
        ({'yandex_uid': '123', 'card_id': ALIAS_X234}, 200),
    ],
)
async def test_get_card(taxi_cardstorage, mongodb, body, code):
    response = await taxi_cardstorage.post('v1/card', json=body)
    assert response.status_code == code
    if code == 200:
        card = response.json()
        assert card['owner'] == '123'
        assert card['card_id'] == CARD_X234
        assert card['billing_card_id'] == BILLING_X234
        assert card['from_db']


@pytest.mark.parametrize(
    'body,expected_card_id,exp_value,',
    [
        (
            {'yandex_uid': '123', 'card_id': 'card-x1337'},
            'card-x313373e693972872b9b58946',
            True,
        ),
        ({'yandex_uid': '123', 'card_id': 'card-x1337'}, 'card-x1337', False),
    ],
)
async def test_full_card_id_experiment(
        taxi_cardstorage,
        experiments3,
        mongodb,
        body,
        expected_card_id,
        exp_value,
):
    experiments3.add_experiment(
        name='enable_long_card_id',
        consumers=['cardstorage/paymentmethods'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': exp_value},
    )
    response = await taxi_cardstorage.post('v1/card', json=body)
    assert response.status_code == 200
    card = response.json()
    assert card['owner'] == '123'
    assert card['card_id'] == expected_card_id
    assert card['from_db']


@pytest.mark.parametrize(
    'card_id,login_id,expected_details_path',
    [
        # No verification levels in this card, expect no details in response
        (CARD_X234, 'login-id', None),
        # Card has verification levels but not for this login-id,
        # expect no details in response
        (CARD_WITH_VERIFICATION_LEVELS, 'absent-login-id', None),
        # Card has full details for this login, expect full details in response
        (
            CARD_WITH_VERIFICATION_LEVELS,
            'login-id-with-full-info',
            'login_id_with_full_info_details.json',
        ),
        # Card has partial details for this login, expect partial details
        # in response
        (
            CARD_WITH_VERIFICATION_LEVELS,
            'login-id-with-partial-info',
            'login_id_with_partial_info_details.json',
        ),
        # No login-id provided, expect no details in response
        (CARD_WITH_VERIFICATION_LEVELS, None, None),
    ],
)
async def test_verification_details(
        taxi_cardstorage,
        mongodb,
        load_json,
        card_id,
        login_id,
        expected_details_path,
):
    expected_details = None
    if expected_details_path is not None:
        expected_details = load_json(expected_details_path)
    yandex_uid = '123'
    body = {'yandex_uid': yandex_uid, 'card_id': card_id}
    if login_id is not None:
        body['yandex_login_id'] = login_id
    response = await taxi_cardstorage.post('v1/card', json=body)
    assert response.status_code == 200
    card = response.json()
    assert card['owner'] == yandex_uid
    assert card['card_id'] == card_id
    assert card['from_db']
    actual_details = card.get('verification_details')
    assert actual_details == expected_details


@pytest.mark.parametrize(
    'card_id,code,ebin_tags',
    [(CARD_X234, 200, []), (CARD_WITH_TAGS, 200, ['tag1', 'tag2'])],
)
async def test_get_ebin_tags(
        taxi_cardstorage, mongodb, card_id, code, ebin_tags,
):
    response = await taxi_cardstorage.post(
        'v1/card', json={'yandex_uid': '123', 'card_id': card_id},
    )
    assert response.status_code == code
    if code == 200:
        card = response.json()
        assert card['owner'] == '123'
        assert card['card_id'] == card_id
        assert card['from_db']
        assert card['ebin_tags'] == ebin_tags
