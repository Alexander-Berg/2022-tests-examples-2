import pytest

from taxi.pytest_plugins.blacksuite import service_client

ORDER_PROC = {
    '_id': 'order_id',
    'commit_state': 'done',
    'created': {'$date': '2020-02-05T10:05:50.508000Z'},
    'order': {
        'user_uid': 'yandex_uid_66',
        'nz': 'moscow',
        'performer': {
            'tariff': {'class': 'econom'},
            'taxi_alias': {'id': 'alias_id'},
        },
        'pricing_data': {
            'currency': {'name': 'RUB'},
            'user': {'data': {'country_code2': 'RU'}, 'meta': {}},
        },
    },
    'payment_tech': {'type': 'card'},
}

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CASHBACK_SERVICES={
            'yataxi': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'yataxi',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'taxi',
                    'cashback_item_ids': ['ride'],
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                },
            },
        },
    ),
]


async def test_get_payload(
        taxi_cashback_web: service_client.AiohttpClientTestsControl,
        order_archive_mock,
        transactions_mock,
        mock_taxi_agglomerations,
        mockserver,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

    order_archive_mock.set_order_proc(ORDER_PROC)
    transactions_mock.invoice_retrieve_v2.update(
        sum_to_pay=[
            {
                'payment_type': 'card',
                'items': [
                    {'item_id': 'ride', 'amount': '541'},
                    {'item_id': 'cashback', 'amount': '60'},
                ],
            },
        ],
        held=[{'payment_type': 'card', 'items': []}],
        cleared=[],
    )

    resp = await taxi_cashback_web.get(
        '/v1/cashback/payload', params={'order_id': 'order_id'},
    )

    resp.raise_for_status()

    assert await resp.json() == {
        'payload': {
            'order_id': 'order_id',
            'alias_id': 'alias_id',
            'oebs_mvp_id': 'MSKc',
            'tariff_class': 'econom',
            'currency': 'RUB',
            'country': 'RU',
            'base_amount': '541',
        },
    }
