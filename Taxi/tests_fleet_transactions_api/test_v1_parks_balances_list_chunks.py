import pytest

from tests_fleet_transactions_api import utils


ENDPOINT_URLS = [
    'v1/parks/balances/list',
    'v1/parks/driver-profiles/balances/list',
]


def _make_category(index):
    return f'category_{index}'


def _make_agreement_id(index):
    return f'taxi/{index}'


def _make_accrued_at(index):
    assert 0 <= index < 10
    return f'2022-01-22T1{index}:00:00+00:00'


def _make_groups_config():
    return [
        {
            'group_id': 'partner_other',
            'group_name_tanker_key': 'Ключ',
            'categories': [
                {
                    'category_id': _make_category(i),
                    'category_name_tanker_key': 'Ключ',
                    'is_affecting_driver_balance': True,
                    'accounts': [
                        {
                            'agreement_id': _make_agreement_id(i),
                            'sub_account': 'manual',
                        },
                    ],
                }
                for i in range(0, 8)
            ],
        },
    ]


def _make_restrictions_config(chunk_size, concurrency):
    return {
        'FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS': {
            'chunk_size': chunk_size,
            'concurrency': concurrency,
        },
    }


def _make_pairs(values1, values2):
    return [(v1, v2) for v1 in values1 for v2 in values2]


def _make_accounts(categories_size, accrued_ats_size):
    agreement_ids = [_make_agreement_id(i) for i in range(0, categories_size)]
    accrued_ats = [_make_accrued_at(i) for i in range(0, accrued_ats_size)]
    return _make_pairs(agreement_ids + ['taxi/driver_balance'], accrued_ats)


def _make_request(categories_size, accrued_ats_size):
    categories = [_make_category(i) for i in range(0, categories_size)]
    accrued_ats = [_make_accrued_at(i) for i in range(0, accrued_ats_size)]
    return utils.make_request(['9c5e35'], accrued_ats, None, categories)


@pytest.mark.config(FLEET_TRANSACTIONS_API_GROUPS=_make_groups_config())
@pytest.mark.parametrize('chunk_size', [0, 1, 5])
@pytest.mark.parametrize('concurrency', [1, 3])
@pytest.mark.parametrize('categories_size', [1, 3, 7])
@pytest.mark.parametrize('accrued_ats_size', [1, 3, 7])
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
async def test_chunks(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        driver_profiles,
        taxi_config,
        mockserver,
        chunk_size,
        concurrency,
        categories_size,
        accrued_ats_size,
        endpoint_url,
):
    taxi_config.set_values(_make_restrictions_config(chunk_size, concurrency))
    expected_accounts = _make_accounts(categories_size, accrued_ats_size)
    requested_accounts = []

    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _v1_balances_select(request):
        accrued_ats = request.json['accrued_at']
        agreements = [acc['agreement_id'] for acc in request.json['accounts']]
        request_accounts = _make_pairs(agreements, accrued_ats)
        assert chunk_size == 0 or len(request_accounts) <= chunk_size
        requested_accounts.extend(request_accounts)

        def _make_balance(accrued_at):
            return {
                'accrued_at': accrued_at,
                'balance': '1.0000',
                'last_created': '2022-01-22T19:00:00.000+00:00',
                'last_entry_id': 12345678,
            }

        balances = [_make_balance(accrued_at) for accrued_at in accrued_ats]

        def _make_account(agreement_id):
            return {
                'account_id': 777,
                'agreement_id': agreement_id,
                'currency': 'RUB',
                'entity_external_id': 'taximeter_park_id/7ad35b',
                'sub_account': 'manual',
            }

        def _make_entry(agreement_id):
            return {
                'account': _make_account(agreement_id),
                'balances': balances,
            }

        return {'entries': [_make_entry(a) for a in agreements]}

    response = await taxi_fleet_transactions_api.post(
        endpoint_url, json=_make_request(categories_size, accrued_ats_size),
    )

    assert response.status == 200, response.text
    assert chunk_size > 0 or _v1_balances_select.times_called == 1
    assert sorted(requested_accounts) == sorted(expected_accounts)
