import pytest


@pytest.mark.now('2020-01-01T12:00:00+03:00')
async def test_ready(contractors_payouts_preview, mock_api, stock, mockserver):
    @mockserver.json_handler('/fleet-antifraud/v1/park-check/blocked-balance')
    def _fleet_antifraud_handler(request):
        return {'blocked_balance': '10.0000'}

    response = await contractors_payouts_preview()

    assert response.status_code == 200, response.text
    assert response.json() == {
        'status': 'ready',
        'amount_minimum': '10',
        'amount_maximum': '36',
        'fee_percent': '10',
        'fee_minimum': '1',
        'cards': [
            {
                'id': '00000000-0001-0001-0000-000000000000',
                'is_last_used': True,
                'issuer': 'visa',
                'masked_pan': '4276********1234',
            },
            {
                'id': '00000000-0002-0002-0000-000000000000',
                'is_last_used': False,
                'issuer': 'maestro',
                'masked_pan': '5000********1234',
            },
            {
                'id': '00000000-0003-0003-0000-000000000000',
                'is_last_used': False,
                'issuer': 'mastercard',
                'masked_pan': '5100********1234',
            },
            {
                'id': '00000000-0004-0004-0000-000000000000',
                'is_last_used': False,
                'issuer': 'mir',
                'masked_pan': '2000********1234',
            },
            {
                'id': '00000000-0005-0005-0000-000000000000',
                'is_last_used': False,
                'issuer': 'unknown',
                'masked_pan': '1000********1234',
            },
        ],
        'last_payout_method': 'sbp',
        'last_phone_pd_id': 'pd_id1',
        'sbp_banks': [
            {
                'id': '101',
                'name_en': 'Bank1',
                'name_ru': 'Банк1',
                'is_last_used': True,
                'how_to_link': 'http://bank1/sbp/how_to',
            },
            {
                'id': '102',
                'name_en': 'Bank2',
                'name_ru': 'Банк2',
                'is_last_used': False,
            },
        ],
    }


async def test_amount(contractors_payouts_preview, mock_api, stock):
    response = await contractors_payouts_preview(withdrawal_amount='40')

    assert response.status_code == 200, response.text
    assert response.json() == {
        'status': 'ready',
        'amount_minimum': '10',
        'amount_maximum': '45',
        'fee_percent': '10',
        'fee_minimum': '1',
        'withdrawal_amount': '40',
        'debit_amount': '40',
        'debit_fee': '4',
        'transfer_amount': '40',
        'cards': [
            {
                'id': '00000000-0001-0001-0000-000000000000',
                'is_last_used': True,
                'issuer': 'visa',
                'masked_pan': '4276********1234',
            },
            {
                'id': '00000000-0002-0002-0000-000000000000',
                'is_last_used': False,
                'issuer': 'maestro',
                'masked_pan': '5000********1234',
            },
            {
                'id': '00000000-0003-0003-0000-000000000000',
                'is_last_used': False,
                'issuer': 'mastercard',
                'masked_pan': '5100********1234',
            },
            {
                'id': '00000000-0004-0004-0000-000000000000',
                'is_last_used': False,
                'issuer': 'mir',
                'masked_pan': '2000********1234',
            },
            {
                'id': '00000000-0005-0005-0000-000000000000',
                'is_last_used': False,
                'issuer': 'unknown',
                'masked_pan': '1000********1234',
            },
        ],
        'hash': '9fadd7582392bc84e95e3cfe40b6bec62cc5951f',
        'last_payout_method': 'sbp',
        'last_phone_pd_id': 'pd_id1',
        'sbp_banks': [
            {
                'id': '101',
                'name_en': 'Bank1',
                'name_ru': 'Банк1',
                'is_last_used': True,
                'how_to_link': 'http://bank1/sbp/how_to',
            },
            {
                'id': '102',
                'is_last_used': False,
                'name_en': 'Bank2',
                'name_ru': 'Банк2',
            },
        ],
    }


@pytest.mark.parametrize('amount', ['1', '1000'])
async def test_wrong_amount(contractors_payouts_preview, stock, amount):
    response = await contractors_payouts_preview(withdrawal_amount=amount)

    assert response.status_code == 200, response.text
    assert response.json() == {'status': 'wrong_amount'}


async def test_not_available(contractors_payouts_preview, stock):
    response = await contractors_payouts_preview(
        contractor_id='48b7b5d81559460fb176693800000004',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'status': 'not_available'}


async def test_already_in_progress(contractors_payouts_preview, stock):
    response = await contractors_payouts_preview(
        contractor_id='48b7b5d81559460fb176693800000002',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'status': 'already_in_progress'}


@pytest.mark.now('2020-01-01T12:00:00+03:00')
async def test_timeout(contractors_payouts_preview, stock):
    response = await contractors_payouts_preview(
        contractor_id='48b7b5d81559460fb176693800000005',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'status': 'already_in_progress'}


@pytest.mark.now('2020-01-01T18:00:00+03:00')
async def test_daily_limit_exceeded(contractors_payouts_preview, stock):
    response = await contractors_payouts_preview(
        contractor_id='48b7b5d81559460fb176693800000003',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'status': 'daily_limit_exceeded'}


TEST_SBP_BANKS_PARAMS = [
    (
        '48b7b5d81559460fb1766938f94009c2',
        None,
        {'CONTRACTOR_INSTANT_PAYOUTS_SBP_ACCOUNT_KINDS': []},
    ),
    (
        '48b7b5d81559460fb1766938f94009c2',
        [
            {
                'id': '100000000008',
                'is_last_used': False,
                'name_en': 'Alfa Bank',
                'name_ru': 'Альфа Банк',
                'how_to_link': 'http://alfa/sbp/how_to',
            },
            {
                'id': '200000000008',
                'is_last_used': False,
                'name_en': 'Tinkoff Bank',
                'name_ru': 'Тинькофф Банк',
            },
        ],
        {},
    ),
    ('76b7b5d81559460fb1766938f94009c2', None, {}),
]


@pytest.mark.now('2020-01-01T12:00:00+03:00')
@pytest.mark.parametrize(
    ('park_id', 'expected_sbp_banks', 'config'), TEST_SBP_BANKS_PARAMS,
)
async def test_sbp_banks(
        taxi_config,
        contractors_payouts_preview,
        mock_api,
        stock,
        park_id,
        expected_sbp_banks,
        config,
):
    taxi_config.set_values(config)

    response = await contractors_payouts_preview(park_id=park_id)

    assert response.status_code == 200, response.text
    if expected_sbp_banks:
        assert response.json()['sbp_banks'] == expected_sbp_banks
