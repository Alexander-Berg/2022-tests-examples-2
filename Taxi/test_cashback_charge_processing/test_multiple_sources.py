import aiohttp
import pytest

from cashback.generated.stq3 import pytest_plugin as stq_plugin

BASE_EVENT = {
    'currency': 'RUB',
    'value': '100',
    'type': 'invoice',
    'yandex_uid': 'yandex_uid_1',
    'service': 'yataxi',
}


ENABLE_SOURCE_SETTINGS = pytest.mark.config(
    CASHBACK_CHARGE_PROCESSING_SOURCE_SETTINGS_ENABLED=True,
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CASHBACK_SERVICES={
            'yataxi': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'yataxi',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'taxi',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                    'billing_service': 'card',
                    'billing_parameters_by_source': {
                        'service': {
                            'cashback_type': 'agent',
                            'product_id': 'some_product_id_service',
                        },
                        'possible_cashback_service': {
                            'cashback_type': 'agent',
                            'product_id': 'some_product_id_possible_cashback',
                        },
                    },
                },
            },
        },
    ),
]


@pytest.mark.parametrize(
    'events, expected_sources, expected_reward',
    [
        pytest.param(
            [
                {
                    'event_id': 'event2',
                    'external_ref': 'order_id',
                    'source': 'user',
                    'payload': {'s': 's', 'a': 'a'},
                    **BASE_EVENT,
                },
                {
                    'event_id': 'event3',
                    'external_ref': 'order_id',
                    'source': 'service',
                    'payload': {'s': 'a', 'a': 's'},
                    **BASE_EVENT,
                },
                {
                    'event_id': 'event4',
                    'external_ref': 'order_id',
                    'source': 'possible_cashback_service',
                    'payload': {'f': 'f'},
                    **BASE_EVENT,
                },
            ],
            {},
            [
                {'amount': '100', 'source': 'user'},
                {'amount': '100', 'source': 'service'},
                {'amount': '100', 'source': 'possible_cashback_service'},
            ],
            id='source-settings-disabled',
        ),
        pytest.param(
            [
                {
                    'event_id': 'event2',
                    'external_ref': 'order_id',
                    'source': 'user',
                    'payload': {'s': 's', 'a': 'a'},
                    **BASE_EVENT,
                },
                {
                    'event_id': 'event3',
                    'external_ref': 'order_id',
                    'source': 'service',
                    'payload': {'s': 'a', 'a': 's'},
                    **BASE_EVENT,
                },
                {
                    'event_id': 'event4',
                    'external_ref': 'order_id',
                    'source': 'possible_cashback_service',
                    'payload': {'f': 'f'},
                    **BASE_EVENT,
                },
            ],
            {
                'user': {'extra_payload': {'s': 's', 'a': 'a'}},
                'service': {
                    'extra_payload': {'s': 'a', 'a': 's'},
                    'product_id': 'some_product_id_service',
                    'cashback_type': 'agent',
                },
                'possible_cashback_service': {
                    'extra_payload': {'f': 'f'},
                    'product_id': 'some_product_id_possible_cashback',
                    'cashback_type': 'agent',
                },
            },
            [
                {'amount': '100', 'source': 'user'},
                {'amount': '100', 'source': 'service'},
                {'amount': '100', 'source': 'possible_cashback_service'},
            ],
            id='source-settings-enabled',
            marks=[ENABLE_SOURCE_SETTINGS],
        ),
    ],
)
@pytest.mark.parametrize(
    'queue',
    ['cashback_charge_processing', 'cashback_charge_processing_non_critical'],
)
async def test_charge_processing_possible_cashback(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        transactions_mock,
        mock_cashback,
        mock_billing_wallet,
        mock_plus_balances,
        queue,
        events,
        expected_sources,
        expected_reward,
):
    transactions_mock.invoice_retrieve_v2.update(
        **{
            'cashback': {
                'commit_version': 12,
                'status': 'init',
                'version': 2,
                'rewarded': [],
                'transactions': [],
                'operations': [],
            },
            'external_user_info': {'user_id': 'user_id_1', 'origin': 'taxi'},
        },
    )

    @mockserver.json_handler('/transactions/v2/cashback/update')
    async def _mock_cashback_update(request):
        if 'sources' not in request.json:
            assert not expected_sources
            return aiohttp.web.json_response(status=200, data={})

        assert 'sources' in request.json
        sources = request.json['sources']
        for expected_source, source_setting in expected_sources.items():
            assert expected_source in sources
            assert source_setting == sources[expected_source]
        return aiohttp.web.json_response(status=200, data={})

    @mock_cashback('/internal/events')
    async def _mock_events(request, **kwargs):
        return {'events': events}

    await getattr(stq_runner, queue).call(
        task_id='order_id', args=('order_id',), kwargs=dict(service='yataxi'),
    )

    assert _mock_cashback_update.has_calls


@pytest.mark.parametrize(
    'service_payload,user_payload,has_sources',
    [
        pytest.param(None, None, False),
        pytest.param(None, None, True, marks=ENABLE_SOURCE_SETTINGS),
        pytest.param(None, {'a': 1}, False),
        pytest.param(None, {'a': 1}, True, marks=ENABLE_SOURCE_SETTINGS),
        pytest.param({'a': 1}, {'a': 1}, False),
        pytest.param({'a': 1}, {'a': 1}, True, marks=ENABLE_SOURCE_SETTINGS),
        pytest.param({'a': 1}, None, False),
        pytest.param({'a': 1}, None, True, marks=ENABLE_SOURCE_SETTINGS),
    ],
)
@pytest.mark.parametrize(
    'queue',
    ['cashback_charge_processing', 'cashback_charge_processing_non_critical'],
)
async def test_charge_processing_pass_sources(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        transactions_mock,
        mock_cashback,
        mock_billing_wallet,
        mock_plus_balances,
        queue,
        service_payload,
        user_payload,
        has_sources,
):
    transactions_mock.invoice_retrieve_v2.update(
        **{
            'cashback': {
                'commit_version': 12,
                'status': 'init',
                'version': 2,
                'rewarded': [],
                'transactions': [],
                'operations': [],
            },
            'external_user_info': {'user_id': 'user_id_1', 'origin': 'taxi'},
        },
    )

    @mockserver.json_handler('/transactions/v2/cashback/update')
    async def _mock_cashback_update(request):
        if not has_sources:
            assert 'sources' not in request.json
            return aiohttp.web.json_response(status=200, data={})

        assert 'sources' in request.json
        sources = request.json['sources']
        for source, payload in (
                ('user', user_payload),
                ('service', service_payload),
        ):
            assert source in sources
            if payload is not None:
                assert sources[source]['extra_payload'] == payload
            else:
                assert 'extra_payload' not in sources[source]
        return aiohttp.web.json_response(status=200, data={})

    @mock_cashback('/internal/events')
    async def _mock_events(request, **kwargs):
        base_event = {
            'currency': 'RUB',
            'value': '100',
            'type': 'invoice',
            'yandex_uid': 'yandex_uid_1',
            'service': 'yataxi',
        }
        return {
            'events': [
                {
                    'event_id': 'event2',
                    'external_ref': 'order_id',
                    'source': 'user',
                    **base_event,
                    **(
                        {'payload': user_payload}
                        if user_payload is not None
                        else {}
                    ),
                },
                {
                    'event_id': 'event3',
                    'external_ref': 'order_id',
                    'source': 'service',
                    **base_event,
                    **(
                        {'payload': service_payload}
                        if service_payload is not None
                        else {}
                    ),
                },
            ],
        }

    await getattr(stq_runner, queue).call(
        task_id='order_id', args=('order_id',), kwargs=dict(service='yataxi'),
    )

    assert _mock_cashback_update.has_calls
