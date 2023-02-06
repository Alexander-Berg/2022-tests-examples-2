import pytest

from tests_cargo_crm import const


EMPLOYEE_YANDEX_UID = 'owner_yandex_uid'
CARD_ID = 'some_card_id'
ADD_WATCH_QUERY_CARD_BOUND = (
    'INSERT INTO cargo_crm.ntfn_watchlist ('
    'ticket_id,ntfn_kind,corp_client_id) VALUES ('
    f'\'{const.TICKET_ID}\',\'card_bound\', \'{const.CORP_CLIENT_ID}\')'
)
ADD_WATCH_QUERY_CONTRACT_ACCEPTED = (
    'INSERT INTO cargo_crm.ntfn_watchlist ('
    'ticket_id,ntfn_kind,corp_client_id) VALUES ('
    f'\'{const.TICKET_ID}\',\'contract_accepted\', \'{const.CORP_CLIENT_ID}\')'
)


@pytest.mark.parametrize(
    'expected_code',
    (
        pytest.param(
            200,
            marks=pytest.mark.pgsql(
                'cargo_crm', queries=[ADD_WATCH_QUERY_CARD_BOUND],
            ),
            id='ok',
        ),
        pytest.param(404, id='not found'),
    ),
)
async def test_notification_card_bound(
        taxi_cargo_crm, mockserver, expected_code,
):
    @mockserver.json_handler(
        'cargo-crm/internal/cargo-crm/flow/phoenix/ticket/card-bound',
    )
    def ticket_handler(request):
        expected_json = {
            'corp_client_id': const.CORP_CLIENT_ID,
            'yandex_uid': EMPLOYEE_YANDEX_UID,
            'card_id': CARD_ID,
        }

        assert request.query['ticket_id'] == const.TICKET_ID
        assert request.json == expected_json

        return mockserver.make_response(status=200, json={})

    request = {
        'corp_client_id': const.CORP_CLIENT_ID,
        'yandex_uid': EMPLOYEE_YANDEX_UID,
        'card_id': CARD_ID,
    }
    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/notification/card-bound', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert ticket_handler.times_called == 1
        assert response.json() == {}


@pytest.mark.parametrize(
    'expected_code',
    (
        pytest.param(
            200,
            marks=pytest.mark.pgsql(
                'cargo_crm', queries=[ADD_WATCH_QUERY_CONTRACT_ACCEPTED],
            ),
            id='ok',
        ),
        pytest.param(404, id='not found'),
    ),
)
async def test_notification_contract_accepted(
        taxi_cargo_crm, mockserver, expected_code,
):
    @mockserver.json_handler(
        'cargo-crm/internal/cargo-crm/flow/manager/ticket/contract-accepted',
    )
    def ticket_handler(request):
        expected_json = {'corp_client_id': const.CORP_CLIENT_ID}

        assert request.query['ticket_id'] == const.TICKET_ID
        assert request.json == expected_json

        return mockserver.make_response(status=200, json={})

    request = {'corp_client_id': const.CORP_CLIENT_ID}

    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/notification/contract-accepted', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert ticket_handler.times_called == 1
        assert response.json() == {}


async def test_notifications_subscribe(taxi_cargo_crm):
    request = {
        'ticket_id': const.TICKET_ID,
        'ntfn_kind': 'card_bound',
        'corp_client_id': const.CORP_CLIENT_ID,
    }

    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/notifications/subscribe', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.pgsql('cargo_crm', queries=[ADD_WATCH_QUERY_CARD_BOUND])
@pytest.mark.parametrize(
    'ntfn_kind',
    (
        pytest.param(None, id='ok without ntfn_kind'),
        pytest.param('card_bound', id='ok with ntfn_kind'),
    ),
)
async def test_notifications_unsubscribe(taxi_cargo_crm, ntfn_kind, pgsql):
    request = {'ticket_id': const.TICKET_ID}
    if ntfn_kind:
        request['ntfn_kind'] = ntfn_kind

    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/notifications/unsubscribe', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {}

    cursor = pgsql['cargo_crm'].cursor()
    cursor.execute(
        'SELECT * FROM cargo_crm.ntfn_watchlist WHERE NOT is_removed',
    )
    assert list(cursor) == []
