import pytest

from tests_contractor_merch import util

TRANSLATIONS = util.STQ_TRANSLATIONS


async def test_empty_transactions_list(
        taxi_contractor_merch, mock_contractor_merch_payments,
):
    mock_contractor_merch_payments.set_response_list(all_transactions=[])

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 10},
        headers=util.get_headers('park_id-10', 'driver_id-10'),
    )

    assert response.status == 200
    assert response.json() == {'transactions': []}


@pytest.mark.pgsql('contractor_merch', files=['primitive_transactions.sql'])
async def test_primitive_transactions(
        taxi_contractor_merch, load_json, mock_contractor_merch_payments,
):
    limit = 20

    mock_contractor_merch_payments.set_response_list(limit=limit)

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': limit},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )
    response_json = response.json()

    assert response.status == 200
    assert response_json == load_json('primitive_transactions_response.json')

    cmp_transactions_list_request = (
        mock_contractor_merch_payments.transactions_list.next_call()['request']
    )
    assert cmp_transactions_list_request.query == {
        'park_id': 'park_id-1',
        'contractor_id': 'driver_id-1',
    }
    assert cmp_transactions_list_request.json == {
        'limit': limit,
        'driver_application': 'Taximeter 9.90',
    }

    headers = cmp_transactions_list_request.headers
    assert headers['Accept-Language'] == 'en_GB'


@pytest.mark.pgsql('contractor_merch', files=['primitive_transactions.sql'])
async def test_contractor_merch_cursor(
        taxi_contractor_merch, load_json, mock_contractor_merch_payments,
):
    mock_contractor_merch_payments.set_response_list(all_transactions=[])

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 5},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )

    assert response.status == 200
    assert response.json() == load_json(
        'contractor_merch_cursor_response.json',
    )


@pytest.mark.pgsql('contractor_merch', files=['primitive_transactions.sql'])
async def test_contractor_merch_payments_cursor(
        taxi_contractor_merch, load_json, mock_contractor_merch_payments,
):
    mock_contractor_merch_payments.set_response_list(limit=5)

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 5},
        headers=util.get_headers('park_id-10', 'driver_id-10'),
    )

    assert response.status == 200
    assert response.json() == load_json(
        'contractor_merch_payments_cursor_response.json',
    )


@pytest.mark.pgsql('contractor_merch', files=['simultaneous_transactions.sql'])
async def test_transactions_order(
        taxi_contractor_merch, load_json, mock_contractor_merch_payments,
):
    mock_contractor_merch_payments.response_json = (
        'simultaneous_list_response.json'
    )
    mock_contractor_merch_payments.set_response_list(limit=5)

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 5},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )

    assert response.status == 200
    assert response.json() == load_json(
        'simultaneous_transactions_response.json',
    )


@pytest.mark.pgsql('contractor_merch', files=['primitive_transactions.sql'])
async def test_no_transactions_left(
        taxi_contractor_merch, load_json, mock_contractor_merch_payments,
):
    mock_contractor_merch_payments.set_response_list(limit=20)

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 20},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )
    cursor = response.json()['cursor']

    mock_contractor_merch_payments.set_response_list(
        limit=20, after_cursor=cursor,
    )

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 20, 'after_cursor': cursor},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )

    assert response.status == 200
    assert response.json() == {'transactions': [], 'cursor': cursor}


@pytest.mark.pgsql('contractor_merch', files=['multipage_transactions.sql'])
@pytest.mark.parametrize('step', list(range(1, 5)))
async def test_multipage_transaction_history(
        taxi_contractor_merch, load_json, mock_contractor_merch_payments, step,
):
    mock_contractor_merch_payments.set_response_list(limit=100)

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 100},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )
    all_transactions = response.json()['transactions']

    cursor = None
    given = 0

    while True:
        mock_contractor_merch_payments.set_response_list(
            limit=step, after_cursor=cursor,
        )

        response = await taxi_contractor_merch.post(
            '/driver/v1/contractor-merch/v1/transactions/list',
            json={'limit': step, 'after_cursor': cursor},
            headers=util.get_headers('park_id-1', 'driver_id-1'),
        )

        response_json = response.json()
        transactions = response_json['transactions']

        assert transactions == all_transactions[given : given + step]

        if not transactions:
            break

        cursor = response_json['cursor']
        given += step

    # убедимся, что после последнего запроса история пуста
    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 100, 'after_cursor': cursor},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )

    assert response.status == 200
    assert response.json()['transactions'] == []


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.pgsql(
    'contractor_merch', files=['priority_promocode_purchase.sql'],
)
async def test_offer_with_priority_params(
        taxi_contractor_merch, load_json, mock_contractor_merch_payments,
):

    mock_contractor_merch_payments.set_response_list(all_transactions=[])

    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/transactions/list',
        json={'limit': 10},
        headers=util.get_headers('park_id', 'driver_id'),
    )

    assert response.status == 200
    assert len(response.json()['transactions']) == 1
    assert response.json()['transactions'] == [
        {
            'id': 'idemp2',
            'amount': {
                'value': '123',
                'currency': 'RUB',
                'formatted': '123 ₽',
            },
            'type': 'debit',
            'purchase': {
                'id': 'voucher_idemp2',
                'type': 'voucher',
                'description': 'Gift card (tire)',
                'merchant': {'merchant_name': 'Apple'},
            },
            'general_status': 'success',
            'created_at': '2021-07-02T14:00:00+00:00',
        },
    ]
