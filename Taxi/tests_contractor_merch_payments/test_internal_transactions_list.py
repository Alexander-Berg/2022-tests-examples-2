import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.pgsql(
    'contractor_merch_payments', files=['partial_transactions.sql'],
)
async def test_empty_transactions_list(taxi_contractor_merch_payments):
    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/transactions/list',
        params={'park_id': 'park_id-10', 'contractor_id': 'contractor_id-10'},
        json={'limit': 10, 'driver_application': 'Taximeter 9.90'},
        headers={'Accept-Language': 'en_GB'},
    )

    assert response.status == 200
    assert response.json() == {'transactions': []}


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.pgsql(
    'contractor_merch_payments', files=['partial_transactions.sql'],
)
async def test_empty_refunds_list(
        taxi_contractor_merch_payments, load_json, mock_merchant_profiles,
):
    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/transactions/list',
        params={'park_id': 'park_id-1', 'contractor_id': 'contractor_id-1'},
        json={'limit': 10, 'driver_application': 'Taximeter 9.90'},
        headers={'Accept-Language': 'en_GB'},
    )

    assert response.status == 200
    assert response.json() == load_json('empty_refunds_response.json')


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.pgsql(
    'contractor_merch_payments', files=['partial_transactions.sql'],
)
@pytest.mark.parametrize(
    ['park_id', 'contractor_id', 'expected_response'],
    [
        pytest.param(
            'park_id-1',
            'contractor_id-1',
            'partial_refunds_response.json',
            id='partial_refunds',
        ),
        pytest.param(
            'park_id-2',
            'contractor_id-2',
            'partial_payments_response.json',
            id='partial_payments',
        ),
    ],
)
async def test_partial_transactions_list(
        taxi_contractor_merch_payments,
        load_json,
        mock_merchant_profiles,
        park_id,
        contractor_id,
        expected_response,
):
    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/transactions/list',
        params={'park_id': park_id, 'contractor_id': contractor_id},
        json={'limit': 1, 'driver_application': 'Taximeter 9.90'},
        headers={'Accept-Language': 'en_GB'},
    )
    transactions = response.json()['transactions']

    cursor = transactions[-1]['cursor']

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/transactions/list',
        params={'park_id': park_id, 'contractor_id': contractor_id},
        json={
            'limit': 1,
            'driver_application': 'Taximeter 9.90',
            'after_cursor': cursor,
        },
        headers={'Accept-Language': 'en_GB'},
    )

    assert response.status == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.pgsql(
    'contractor_merch_payments', files=['partial_transactions.sql'],
)
async def test_empty_payments_list(
        taxi_contractor_merch_payments, load_json, mock_merchant_profiles,
):
    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/transactions/list',
        params={'park_id': 'park_id-2', 'contractor_id': 'contractor_id-2'},
        json={'limit': 2, 'driver_application': 'Taximeter 9.90'},
        headers={'Accept-Language': 'en_GB'},
    )

    assert response.status == 200
    assert response.json() == load_json('empty_payments_response.json')


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.pgsql(
    'contractor_merch_payments', files=['primitive_transactions.sql'],
)
async def test_primitive_transactions_list(
        taxi_contractor_merch_payments, load_json, mock_merchant_profiles,
):
    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/transactions/list',
        params={'park_id': 'park_id-1', 'contractor_id': 'contractor_id-1'},
        json={'limit': 10, 'driver_application': 'Taximeter 9.90'},
        headers={'Accept-Language': 'en_GB'},
    )

    assert response.status == 200
    assert response.json() == load_json('primitive_transactions_response.json')

    assert mock_merchant_profiles.merchants_bulk_retrieve.times_called == 2


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.pgsql(
    'contractor_merch_payments', files=['simultaneous_transactions.sql'],
)
async def test_transactions_order(
        taxi_contractor_merch_payments, load_json, mock_merchant_profiles,
):
    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/transactions/list',
        params={'park_id': 'park_id-1', 'contractor_id': 'contractor_id-1'},
        json={'limit': 10, 'driver_application': 'Taximeter 9.90'},
        headers={'Accept-Language': 'en_GB'},
    )

    assert response.status == 200
    assert response.json() == load_json(
        'simultaneous_transactions_response.json',
    )


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.pgsql(
    'contractor_merch_payments', files=['multipage_transactions.sql'],
)
async def test_multipage_transactions_list(
        taxi_contractor_merch_payments, load_json, mock_merchant_profiles,
):
    async def test_scrolling(step):
        cursor = None
        given = 0
        while True:
            response = await taxi_contractor_merch_payments.post(
                '/internal/contractor-merch-payments/v1/transactions/list',
                params={
                    'park_id': 'park_id-1',
                    'contractor_id': 'contractor_id-1',
                },
                json={
                    'limit': step,
                    'driver_application': 'Taximeter 9.90',
                    'after_cursor': cursor,
                },
                headers={'Accept-Language': 'en_GB'},
            )
            response_json = response.json()
            transactions = response_json['transactions']

            assert transactions == all_transactions[given : given + step]

            if not transactions:
                break

            cursor = transactions[-1]['cursor']
            given += step

        # убедимся, что после последнего запроса история пуста
        response = await taxi_contractor_merch_payments.post(
            '/internal/contractor-merch-payments/v1/transactions/list',
            params={
                'park_id': 'park_id-1',
                'contractor_id': 'contractor_id-1',
            },
            json={
                'limit': 100,
                'driver_application': 'Taximeter 9.90',
                'after_cursor': cursor,
            },
            headers={'Accept-Language': 'en_GB'},
        )

        assert response.status == 200
        assert response.json()['transactions'] == []

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/transactions/list',
        params={'park_id': 'park_id-1', 'contractor_id': 'contractor_id-1'},
        json={'limit': 30, 'driver_application': 'Taximeter 9.90'},
        headers={'Accept-Language': 'en_GB'},
    )
    all_transactions = response.json()['transactions']

    for step in range(1, 4):
        await test_scrolling(step)
