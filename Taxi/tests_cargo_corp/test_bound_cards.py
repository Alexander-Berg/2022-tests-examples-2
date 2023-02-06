import pytest

from tests_cargo_corp import utils


MOCK_NOW = '2021-05-31T19:00:00+00:00'
CARD_ID = 'card-007'
CARD_PAYMENT_METHOD = {
    'card_id': '1',
    'billing_card_id': '1',
    'permanent_card_id': '1',
    'currency': 'RUB',
    'expiration_month': 12,
    'expiration_year': 2020,
    'owner': 'Mr',
    'possible_moneyless': False,
    'region_id': 'RU',
    'regions_checked': ['RU'],
    'system': '1',
    'valid': True,
    'bound': True,
    'unverified': False,
    'busy': False,
    'busy_with': [],
    'from_db': True,
    'number': '5100222233334444',
    'bin': '510022',
}
CARD_ID_2 = 'card-008'
LOCAL_YANDEX_UID = 'yandex_uid2'


@pytest.fixture(name='assert_other_cards_unbound')
def _assert_cards(pgsql):
    def wrapper(excluded_card_id, corp_client_id=utils.CORP_CLIENT_ID):
        cursor = pgsql['cargo_corp'].conn.cursor()

        cursor.execute(
            """
            SELECT
                count(*)
            FROM corp_clients.bound_cards
            WHERE
                corp_client_id = '{}'
                AND
                NOT (card_id = '{}')
                AND
                is_bound
        """.format(
                corp_client_id, excluded_card_id,
            ),
        )
        row = cursor.fetchone()
        cursor.close()

        assert not row[0]

    return wrapper


def get_headers(corp_client_id, yandex_uid, request_mode=None):
    headers = {'X-B2B-Client-Id': corp_client_id}
    if yandex_uid:
        headers['X-Yandex-Uid'] = yandex_uid
    if request_mode:
        headers['X-Request-Mode'] = request_mode
    return headers


# TODO (dipterix): add test for filter_by_uid
@pytest.mark.parametrize(
    'requester_uid, request_mode, cards_expected',
    [
        (utils.YANDEX_UID, 'b2b', True),
        ('other_uid', 'b2b', True),
        ('other_uid', 'admin', True),
    ],
)
@pytest.mark.parametrize(
    'corp_client_id, expected_code',
    (
        pytest.param(utils.CORP_CLIENT_ID, 200, id='ok'),
        pytest.param('not_exist_corp_client_identifier', 404, id='not found'),
    ),
)
async def test_corp_client_cards(
        taxi_cargo_corp,
        user_has_rights,
        register_default_user,
        register_default_card,
        corp_client_id,
        requester_uid,
        request_mode,
        expected_code,
        cards_expected,
):
    response = await taxi_cargo_corp.post(
        'internal/cargo-corp/v1/client/card/list',
        headers=get_headers(corp_client_id, requester_uid, request_mode),
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        if not cards_expected:
            assert response.json()['bound_cards'] == []
        else:
            assert response.json()['bound_cards'] == [
                {'card_id': 'card_1', 'yandex_uid': 'yandex_uid1'},
            ]


def _mock_handler_v1_card(
        mockserver, request, yandex_uid=utils.YANDEX_UID, v1_card_code=200,
):
    assert request.json['yandex_uid'] == yandex_uid
    assert request.json['card_id'] == CARD_ID

    body = {'message': 'error', 'code': 'ERROR'}
    if v1_card_code == 200:
        body = {
            'card_id': CARD_ID,
            'billing_card_id': '1',
            'permanent_card_id': '1',
            'currency': 'RUB',
            'expiration_month': 12,
            'expiration_year': 2020,
            'owner': 'Mr',
            'possible_moneyless': False,
            'region_id': 'RU',
            'regions_checked': ['RU'],
            'system': '1',
            'valid': True,
            'bound': True,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': True,
            'number': '5100222233334444',
            'bin': '510022',
        }
    return mockserver.make_response(status=v1_card_code, json=body)


@pytest.mark.parametrize(
    'corp_client_id, yandex_uid, expected_code',
    (
        pytest.param(utils.CORP_CLIENT_ID, utils.YANDEX_UID, 200, id='ok'),
        pytest.param(
            utils.CORP_CLIENT_ID, 'other_uid', 404, id='employee not found',
        ),
        pytest.param(
            'not_exist_corp_client_identifier',
            utils.YANDEX_UID,
            404,
            id='corp not found',
        ),
    ),
)
@pytest.mark.now(MOCK_NOW)
async def test_bound_card(
        taxi_cargo_corp,
        user_has_rights,
        mockserver,
        stq,
        pgsql,
        assert_other_cards_unbound,
        corp_client_id,
        yandex_uid,
        expected_code,
):
    @mockserver.json_handler('cardstorage/v1/card')
    def mock_handler_v1_card(request):
        return _mock_handler_v1_card(mockserver, request, yandex_uid)

    utils.create_employee(pgsql, yandex_uid=LOCAL_YANDEX_UID)
    utils.add_card(pgsql, yandex_uid=LOCAL_YANDEX_UID, card_id=CARD_ID_2)

    response = await taxi_cargo_corp.post(
        '/v1/client/employee/card/bound',
        headers=get_headers(corp_client_id, yandex_uid),
        json={'card': {'id': CARD_ID}},
    )
    assert response.status_code == expected_code

    assert mock_handler_v1_card.times_called

    if expected_code == 200:
        assert response.json() == {}
        assert_other_cards_unbound(CARD_ID)

    assert stq.cargo_corp_bound_card_notifier.times_called == 1
    stq_params = stq.cargo_corp_bound_card_notifier.next_call()
    assert stq_params['id'] == f'{corp_client_id}:{yandex_uid}:{CARD_ID}'
    assert stq_params['kwargs']['corp_client_id'] == corp_client_id
    assert stq_params['kwargs']['yandex_uid'] == yandex_uid
    assert stq_params['kwargs']['card_id'] == CARD_ID
    assert stq_params['kwargs']['started_at'] == MOCK_NOW


@pytest.mark.parametrize(
    'cardstorage_code, expected_code',
    (
        pytest.param(400, 500, id='bad request'),
        pytest.param(404, 404, id='not found'),
        pytest.param(500, 500, id='internal error'),
    ),
)
async def test_bound_card_bad_cardstorage(
        taxi_cargo_corp, mockserver, stq, cardstorage_code, expected_code,
):
    @mockserver.json_handler('cardstorage/v1/card')
    def mock_handler_v1_card(request):
        return _mock_handler_v1_card(
            mockserver, request, v1_card_code=cardstorage_code,
        )

    response = await taxi_cargo_corp.post(
        '/v1/client/employee/card/bound',
        headers=get_headers(utils.CORP_CLIENT_ID, utils.YANDEX_UID),
        json={'card': {'id': CARD_ID}},
    )
    assert response.status_code == expected_code
    assert mock_handler_v1_card.times_called
    assert stq.cargo_corp_bound_card_notifier.times_called == 0
