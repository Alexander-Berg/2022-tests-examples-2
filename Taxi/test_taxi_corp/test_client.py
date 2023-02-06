# pylint: disable=too-many-lines, too-many-locals
import pytest


@pytest.mark.parametrize(
    ['client_id', 'expected_result'],
    [
        pytest.param(
            'ad3abf37ac93481087c5348d0184bf36',
            {
                '_id': 'ad3abf37ac93481087c5348d0184bf36',
                'contract_id': '28ea38e926c444a5a68c591b8dd6bf6d',
                'country': 'rus',
                'currency': 'RUB',
                'currency_rules': {
                    'code': 'RUB',
                    'template': '_1',
                    'text': '_2',
                },
                'currency_sign': '₽',
                'default_tariff_class': 'econom',
                'is_corp_agent': False,
                'yandex_login': 'yandex_search_team',
                'comment': '',
                'name': 'Yandex.Search team',
                'email': 'search@yandex.ru',
                'is_active': True,
                'cabinet_only_role_id': '8e69bef99be44b35b47ce1507b861d61',
                'billing_name': '',
                'cost_centers_file_name': 'cost_centers.xls',
                'features': None,
                'services': {
                    'taxi': {
                        'is_active': True,
                        'is_visible': True,
                        'contract_id': '28ea38e926c444a5a68c591b8dd6bf6d',
                    },
                },
            },
            id='common rus client',
        ),
        pytest.param(
            'trial',
            {
                '_id': 'trial',
                'contract_id': '28ea38e926c444a5a68c591b8dd6bf6d',
                'country': 'rus',
                'currency': 'RUB',
                'currency_rules': {
                    'code': 'RUB',
                    'template': '_1',
                    'text': '_2',
                },
                'currency_sign': '₽',
                'is_corp_agent': False,
                'yandex_login': 'engineer',
                'comment': '',
                'name': 'engineer',
                'email': 'engineer@yandex.ru',
                'is_active': True,
                'trial': {'request_status': 'absent'},
                'cabinet_only_role_id': '8e69bef99be44b35b47ce1507b861d61',
                'billing_name': '',
                'cost_centers_file_name': 'cost_centers.xls',
                'features': None,
                'services': {
                    'taxi': {
                        'is_active': True,
                        'is_visible': True,
                        'contract_id': '28ea38e926c444a5a68c591b8dd6bf6d',
                    },
                },
            },
            id='trial client',
        ),
        pytest.param(
            'trial_cr',
            {
                '_id': 'trial_cr',
                'contract_id': '28ea38e926c444a5a68c591b8dd6bf6e',
                'country': 'rus',
                'currency': 'RUB',
                'currency_rules': {
                    'code': 'RUB',
                    'template': '_1',
                    'text': '_2',
                },
                'currency_sign': '₽',
                'is_corp_agent': False,
                'yandex_login': 'engineer0',
                'comment': '',
                'name': 'engineer',
                'email': 'engineer@yandex.ru',
                'is_active': True,
                'trial': {'reason': 'duplicate', 'request_status': 'rejected'},
                'cabinet_only_role_id': '8e69bef99be44b35b47ce1507b861d62',
                'billing_name': '',
                'cost_centers_file_name': 'cost_centers.xls',
                'features': None,
                'services': {
                    'taxi': {
                        'is_active': True,
                        'is_visible': True,
                        'contract_id': '28ea38e926c444a5a68c591b8dd6bf6e',
                    },
                },
            },
            id='trial client with existing client request',
        ),
        pytest.param(
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                '_id': '7ff7900803534212a3a66f4d0e114fc2',
                'contract_id': '24b322b91bef4d4e80dfa6c44ca6df38',
                'country': 'rus',
                'currency': 'RUB',
                'currency_rules': {
                    'code': 'RUB',
                    'template': '_1',
                    'text': '_2',
                },
                'currency_sign': '₽',
                'is_corp_agent': False,
                'yandex_login': 'yandex_taxi_team',
                'comment': 'brilliant comment',
                'name': 'Yandex.Taxi team',
                'email': 'taxi@yandex.ru',
                'is_active': True,
                'cabinet_only_role_id': '8b0fd32438914c869566b1310b943cdf',
                'billing_name': 'Yandex.Taxi',
                'cost_centers_file_name': '',
                'features': None,
                'services': {
                    'drive': {
                        'contract_id': '123',
                        'is_visible': False,
                        'is_active': False,
                        'task_id': 'some_task_id',
                    },
                    'eats': {
                        'contract_id': '1234',
                        'is_visible': False,
                        'is_active': False,
                    },
                    'taxi': {
                        'is_active': True,
                        'is_visible': True,
                        'contract_id': '24b322b91bef4d4e80dfa6c44ca6df38',
                        'comment': 'brilliant comment',
                    },
                    'eats2': {
                        'contract_id': '1234',
                        'is_visible': False,
                        'is_active': False,
                    },
                    'cargo': {
                        'contract_id': 'cargo_contract_id',
                        'is_active': True,
                        'is_visible': True,
                    },
                    'tanker': {
                        'contract_id': 'tanker_contract_id',
                        'is_active': True,
                        'is_visible': False,
                    },
                },
            },
            id='many services',
        ),
        pytest.param(
            '66e18797de794a9b8bde685aa5628d50',
            {
                '_id': '66e18797de794a9b8bde685aa5628d50',
                'contract_id': 'NEW',
                'country': 'rus',
                'currency': 'RUB',
                'currency_rules': {
                    'code': 'RUB',
                    'template': '_1',
                    'text': '_2',
                },
                'currency_sign': '₽',
                'is_corp_agent': False,
                'yandex_login': 'client3',
                'name': 'Yandex.Uber team',
                'email': '',
                'comment': '',
                'is_active': True,
                'cabinet_only_role_id': '24354584482e495882d4b632ead0a980',
                'billing_name': None,
                'cost_centers_file_name': '',
                'features': ['departments', 'support_chat'],
                'services': {
                    'taxi': {
                        'is_active': True,
                        'is_visible': True,
                        'contract_id': 'NEW',
                        'comment': '',
                    },
                },
            },
            id='prepaid',
        ),
        pytest.param(
            'fa9705dd59b04ea182888d7343320572',
            {
                '_id': 'fa9705dd59b04ea182888d7343320572',
                'contract_id': 'min_balance',
                'country': 'kaz',
                'currency': 'RUB',
                'currency_rules': {
                    'code': 'RUB',
                    'template': '_1',
                    'text': '_2',
                },
                'cabinet_only_role_id': None,
                'currency_sign': None,
                'is_corp_agent': False,
                'yandex_login': 'min_balance',
                'name': 'min_balance',
                'email': '',
                'comment': '',
                'is_active': False,
                'billing_name': '',
                'cost_centers_file_name': '',
                'features': None,
                'services': {
                    'taxi': {
                        'is_active': False,
                        'is_visible': True,
                        'contract_id': 'min_balance',
                        'comment': '',
                    },
                },
            },
            id='inactive',
        ),
    ],
)
@pytest.mark.translations(
    tariff={
        'currency.rub': {'ru': '_2'},
        'currency_with_sign.default': {'ru': '_1'},
    },
)
@pytest.mark.config(ALLOW_CORP_BILLING_REQUESTS=True)
async def test_single_get(
        taxi_corp_auth_client,
        patch,
        client_id,
        expected_result,
        mock_corp_requests,
):
    @patch('taxi_corp.util.personal_data.find_pd_by_condition')
    async def _mock_find_pd(app, item, field, *args, **kwargs):
        return item[field]

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient.find_client')
    async def _find_client(*args, **kwargs):
        return {'services': [{'type': 'eats/rus', 'suspended': True}]}

    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}'.format(client_id),
    )

    assert response.status == 200
    assert await response.json() == expected_result

    assert len(_mock_find_pd.calls) == 2

    assert _find_client.calls


@pytest.mark.parametrize(
    ['client_id', 'response_code'],
    [('89f20862543f4e4495e55f7699d1f33c', 404)],
)
async def test_single_get_fail(
        taxi_corp_auth_client, client_id, response_code,
):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}'.format(client_id),
    )
    response_json = await response.json()
    assert response.status == response_code, response_json
