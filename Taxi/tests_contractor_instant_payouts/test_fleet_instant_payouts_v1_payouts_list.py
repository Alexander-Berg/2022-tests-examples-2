import pytest

from tests_contractor_instant_payouts import utils

ENDPOINT = '/fleet/instant-payouts/v1/payouts/list'
MOCK_URL = '/parks/driver-profiles/list'


CURSOR = (
    'eyJpZCI6IjAwMDAwMDAwLTAwMDEtMDAwMS0wMDAxLTAwMDAwMDAwMD'
    'AwMCIsInRpbWUiOiIyMDIwLTAxLTAxVDEyOjAwOjAwKzAwOjAwIn0='
)

WITHDRAWAL_CURSOR = (
    'eyJ0aW1lIjoiMjAyMC0wMi0wMlQxMjowMDowMCswMDowMCIsImlkIj'
    'oiMDAwMDAwMDAtMDAwMS0wMDAxLTAwMDItMDAwMDAwMDAwMDAwIiwi'
    'd2l0aGRyYXdhbF9hbW91bnQiOiIyMDAuMDIwMiJ9'
)


def build_params(
        limit=None,
        cursor=None,
        search=None,
        status=None,
        date_from=None,
        date_to=None,
        sort_by=None,
        sort_order=None,
):
    params = {}
    if limit is not None:
        params['limit'] = limit
    if cursor is not None:
        params['cursor'] = cursor
    if search is not None:
        params['search'] = search
    if status is not None:
        params['status'] = status
    if date_from is not None:
        params['date_from'] = date_from
    if date_to is not None:
        params['date_to'] = date_to
    if sort_by is not None:
        params['sort_by'] = sort_by
    if sort_order is not None:
        params['sort_order'] = sort_order

    return params


OK_PARAMS = [
    (
        'park1',
        build_params(),
        {
            'payouts': [
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
                {
                    'amount': '100.01',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3810',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'debit_amount': '101.02',
                    'id': '00000000-0001-0001-0001-000000000000',
                    'status': 'succeeded',
                    'transfer_amount': '100.02',
                    'withdrawal_amount': '100.01',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(limit=1),
        {
            'next_cursor': CURSOR,
            'payouts': [
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(cursor=CURSOR),
        {
            'payouts': [
                {
                    'amount': '100.01',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3810',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'debit_amount': '101.02',
                    'id': '00000000-0001-0001-0001-000000000000',
                    'status': 'succeeded',
                    'transfer_amount': '100.02',
                    'withdrawal_amount': '100.01',
                },
            ],
        },
    ),
    ('park2', build_params(), {'payouts': []}),
    (
        'park1',
        build_params(search='cont'),
        {
            'payouts': [
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
                {
                    'amount': '100.01',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3810',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'debit_amount': '101.02',
                    'id': '00000000-0001-0001-0001-000000000000',
                    'status': 'succeeded',
                    'transfer_amount': '100.02',
                    'withdrawal_amount': '100.01',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(status='succeeded'),
        {
            'payouts': [
                {
                    'amount': '100.01',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3810',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'debit_amount': '101.02',
                    'id': '00000000-0001-0001-0001-000000000000',
                    'status': 'succeeded',
                    'transfer_amount': '100.02',
                    'withdrawal_amount': '100.01',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(status='failed'),
        {
            'payouts': [
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
            ],
        },
    ),
    ('park1', build_params(status='in_progress'), {'payouts': []}),
    (
        'park1',
        build_params(date_from='2020-02-02T14:00:00+03:00'),
        {
            'payouts': [
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(date_to='2020-02-02T12:00:00+12:00'),
        {
            'payouts': [
                {
                    'amount': '100.01',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3810',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'debit_amount': '101.02',
                    'id': '00000000-0001-0001-0001-000000000000',
                    'status': 'succeeded',
                    'transfer_amount': '100.02',
                    'withdrawal_amount': '100.01',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(sort_by='withdrawal_amount'),
        {
            'payouts': [
                {
                    'amount': '100.01',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3810',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'debit_amount': '101.02',
                    'id': '00000000-0001-0001-0001-000000000000',
                    'status': 'succeeded',
                    'transfer_amount': '100.02',
                    'withdrawal_amount': '100.01',
                },
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(sort_by='withdrawal_amount', sort_order='asc'),
        {
            'payouts': [
                {
                    'amount': '100.01',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3810',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'debit_amount': '101.02',
                    'id': '00000000-0001-0001-0001-000000000000',
                    'status': 'succeeded',
                    'transfer_amount': '100.02',
                    'withdrawal_amount': '100.01',
                },
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(sort_by='withdrawal_amount', sort_order='desc'),
        {
            'payouts': [
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
                {
                    'amount': '100.01',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3810',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'debit_amount': '101.02',
                    'id': '00000000-0001-0001-0001-000000000000',
                    'status': 'succeeded',
                    'transfer_amount': '100.02',
                    'withdrawal_amount': '100.01',
                },
            ],
        },
    ),
    (
        'park1',
        build_params(sort_by='withdrawal_amount', cursor=WITHDRAWAL_CURSOR),
        {
            'payouts': [
                {
                    'amount': '200.02',
                    'bank_payout_id': '3c178bd1-f720-4daf-99b8-b8ab253f3811',
                    'bank_provider': 'modulbank',
                    'card_last4': '************1234',
                    'contractor_id': 'contractor1',
                    'contractor_name': {
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                    },
                    'created_at': '2020-02-02T12:00:00+00:00',
                    'debit_amount': '202.04',
                    'error_code': 'account_insufficient_funds',
                    'id': '00000000-0001-0001-0002-000000000000',
                    'status': 'failed',
                    'withdrawal_amount': '200.02',
                },
            ],
        },
    ),
]


@pytest.mark.parametrize('park_id, params, expected_response', OK_PARAMS)
async def test_ok(
        taxi_contractor_instant_payouts,
        mock_driver_profiles,
        mockserver,
        park_id,
        params,
        expected_response,
):
    @mockserver.json_handler(MOCK_URL)
    def _mock_parks(request):
        return {
            'offset': 0,
            'total': 1,
            'parks': [],
            'driver_profiles': [{'driver_profile': {'id': 'contractor1'}}],
        }

    response = await taxi_contractor_instant_payouts.get(
        ENDPOINT, headers=utils.build_headers(park_id=park_id), params=params,
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_bad_cursor(taxi_contractor_instant_payouts):
    response = await taxi_contractor_instant_payouts.get(
        ENDPOINT,
        headers=utils.build_headers(park_id='park1'),
        params=build_params(cursor='bad_cursor'),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_argument',
        'message': 'Invalid cursor string.',
    }
