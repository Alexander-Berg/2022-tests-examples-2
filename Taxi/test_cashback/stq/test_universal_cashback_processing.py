# pylint: disable=C0302
import datetime
from typing import List
from typing import NamedTuple
from typing import Optional

import aiohttp
from dateutil import tz
import pytest

from cashback import const
from cashback.generated.stq3 import stq_context
from cashback.modules.cashback_services import module as cashback_services

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CASHBACK_SERVICES={
            'lavka': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'eda',
                    'url': '$mockserver/cashback/get',
                    'url_v2': '$mockserver/v2/cashback/get',
                    'tvm_name': 'lavka',
                    'cashback_item_ids': ['food'],
                },
            },
            'lavka_isr': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'lavka_isr',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'lavka_isr',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                },
            },
            'yataxi': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'yataxi',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'taxi',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                    'cashback_item_ids': ['ride'],
                    'some_extra_field': True,
                },
            },
            'yataxi_v2': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'yataxi',
                    'url': '$mockserver/cashback/get',
                    'url_v2': '$mockserver/v2/cashback/get',
                    'tvm_name': 'taxi',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                    'cashback_item_ids': ['ride'],
                    'some_extra_field': True,
                },
            },
            'restaurants': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'eda',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'restaurants',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                },
            },
            'afisha': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'eda',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'afisha',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                    'cashback_item_ids': [],
                },
            },
        },
    ),
]

DEFAULT_PROC = {
    '_id': 'order_id',
    'status': 'finished',
    'order': {
        'user_uid': 'yandex_uid_66',
        'taxi_status': 'complete',
        'performer': {'tariff': {'class': 'econom'}},
        'nz': 'moscow',
        'cost': '300',
    },
    'extra_data': {'cashback': {'is_cashback': True}},
    'payment_tech': {'type': 'card'},
    'created': datetime.datetime(
        2020, 9, 10, 12, 52, 5, 701000, tzinfo=tz.UTC,
    ),
}

INVOICE_CREATED = datetime.datetime(
    2021, 9, 10, 12, 52, 5, 701000, tzinfo=tz.UTC,
)


class MyTestCase(NamedTuple):
    service: str
    invoice: dict
    calculated_cashback: str
    expected_calc_hold: str
    expected_calc_clear: str
    expected_register_clear: str
    expected_cashback: str
    expected_cashback_by_source: List[dict]
    expected_charge_queue: Optional[str] = 'cashback_charge_processing'
    expected_register_cashback: Optional[int] = None
    service_payload: Optional[dict] = None
    expected_cleared_items: Optional[list] = None
    expected_held_items: Optional[list] = None
    expected_payload: dict = {'has_plus': True}

    def _make_payment_items(self, section: str):
        return [
            {
                'payment_type': payment_type,
                'items': [
                    {'item_id': key, 'amount': value}
                    for key, value in items[section].items()
                ],
            }
            for payment_type, items in self.invoice.items()
        ]

    def make_invoice_update(self) -> dict:
        return {
            'payment_types': list(self.invoice),
            'cleared': self._make_payment_items('cleared'),
            'held': self._make_payment_items('held'),
            'user_ip': None,  # check that ucp does not fail with user_ip: None
            'created': INVOICE_CREATED.isoformat(),
        }


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'held': {'ride': '100'},
                        'cleared': {
                            'ride': '1000',
                            'cashback': '100',
                            'tips': '20',
                        },
                    },
                },
                calculated_cashback='100',
                expected_calc_hold='100',
                expected_calc_clear='1000',
                expected_register_clear='1100',
                expected_cashback='200',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '100'},
                    {'source': 'service', 'value': '100'},
                ],
            ),
            id='yataxi-both-cashbacks',
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'corp': {
                        'held': {'ride': '100'},
                        'cleared': {
                            'ride': '1000',
                            'cashback': '100',
                            'tips': '20',
                        },
                    },
                },
                calculated_cashback='100',
                expected_calc_hold='100',
                expected_calc_clear='1000',
                expected_register_clear='1100',
                expected_register_cashback=0,
                expected_charge_queue=None,
                expected_cashback='0',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '0'},
                    {'source': 'service', 'value': '0'},
                ],
            ),
            id='yataxi-blacklisted-payment-cashback',
        ),
        pytest.param(
            # Normally we don't offer cashback for rides with composite payment
            # but we must check it anyway
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {'held': {'ride': '800'}, 'cleared': {}},
                    'personal_wallet': {
                        'held': {},
                        'cleared': {'ride': '200'},
                    },
                },
                calculated_cashback='100',
                expected_calc_hold='800',
                expected_calc_clear='0',
                expected_register_clear='800',
                expected_cashback='100',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '0'},
                    {'source': 'service', 'value': '100'},
                ],
                expected_charge_queue=(
                    'cashback_charge_processing_non_critical'
                ),
            ),
            id='yataxi-composite-payment',
            marks=pytest.mark.config(
                CASHBACK_CHARGE_PROCESSING_NON_CRITICAL_ENABLED=True,
            ),
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={'card': {'held': {}, 'cleared': {'ride': '1000'}}},
                calculated_cashback='150',
                expected_calc_hold='0',
                expected_calc_clear='1000',
                expected_register_clear='1000',
                expected_cashback='150',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '0'},
                    {'source': 'service', 'value': '150'},
                ],
            ),
            id='yataxi-calc-cashback-only',
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={'card': {'held': {}, 'cleared': {'ride': '1000'}}},
                calculated_cashback='150',
                expected_calc_hold='0',
                expected_calc_clear='1000',
                expected_register_clear='1000',
                expected_cashback='150',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '0'},
                    {'source': 'service', 'value': '150'},
                ],
                expected_charge_queue=(
                    'cashback_charge_processing_non_critical'
                ),
            ),
            id='yataxi-calc-cashback-with-noncritical',
            marks=pytest.mark.config(
                CASHBACK_CHARGE_PROCESSING_NON_CRITICAL_ENABLED=True,
            ),
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'held': {},
                        'cleared': {'ride': '1000', 'cashback': '175'},
                    },
                },
                calculated_cashback='0',
                expected_calc_hold='0',
                expected_calc_clear='1000',
                expected_register_clear='1000',
                expected_cashback='175',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '175'},
                    {'source': 'service', 'value': '0'},
                ],
            ),
            id='yataxi-paid-cashback-only',
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'held': {'cashback': '150'},
                        'cleared': {'ride': '1000', 'cashback': '175'},
                    },
                },
                calculated_cashback='0',
                expected_calc_hold='0',
                expected_calc_clear='1000',
                expected_register_clear='1000',
                expected_cashback='325',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '325'},
                    {'source': 'service', 'value': '0'},
                ],
            ),
            id='yataxi-paid-cashback-instant-on',
            marks=[pytest.mark.config(INSTANT_CASHBACK_ENABLED=True)],
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'held': {'cashback': '150'},
                        'cleared': {'ride': '1000', 'cashback': '180'},
                    },
                },
                calculated_cashback='0',
                expected_calc_hold='0',
                expected_calc_clear='1000',
                expected_register_clear='1000',
                expected_cashback='180',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '180'},
                    {'source': 'service', 'value': '0'},
                ],
            ),
            id='yataxi-paid-cashback-instant-off',
            marks=[pytest.mark.config(INSTANT_CASHBACK_ENABLED=False)],
        ),
        pytest.param(
            MyTestCase(
                service='restaurants',
                invoice={
                    'card': {
                        'held': {'1': '100', '2': '200'},
                        'cleared': {'3': '1000'},
                    },
                },
                calculated_cashback='200',
                expected_calc_hold='300',
                expected_calc_clear='1000',
                expected_register_clear='1300',
                expected_cashback='200',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '0'},
                    {'source': 'service', 'value': '200'},
                ],
            ),
            id='restaurants',
        ),
        pytest.param(
            MyTestCase(
                service='afisha',
                invoice={
                    'card': {
                        'held': {'1': '100', '2': '200'},
                        'cleared': {'3': '1000'},
                    },
                },
                calculated_cashback='0',
                expected_calc_hold='0',
                expected_calc_clear='0',
                expected_register_clear='0',
                expected_cashback='0',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '0'},
                    {'source': 'service', 'value': '0'},
                ],
            ),
            id='service_without_cashback_items',
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'cleared': {
                            'ride': '90',
                            'cashback': '10',
                            'tips': '10',
                        },
                        'held': {},
                    },
                    'applepay': {
                        'cleared': {'ride': '280', 'cashback': '20'},
                        'held': {},
                    },
                },
                calculated_cashback='37',
                expected_calc_hold='0',
                expected_calc_clear='370',  # 90 + 280,
                expected_register_clear='370',
                expected_cashback='67',  # 37 + 10 + 20
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '30'},
                    {'source': 'service', 'value': '37'},
                ],
            ),
            id='switch-to-applepay',
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'held': {'ride': '100'},
                        'cleared': {
                            'ride': '1000',
                            'cashback': '100',
                            'tips': '20',
                        },
                    },
                },
                calculated_cashback='100',
                expected_calc_hold='100',
                expected_calc_clear='1000',
                expected_register_clear='1100',
                expected_cashback='200',
                expected_cashback_by_source=[
                    {
                        'source': 'user',
                        'value': '100',
                        'extra_payload': {'extra_payload_field': 'value'},
                    },
                    {
                        'source': 'service',
                        'value': '100',
                        'extra_payload': {'extra_payload_field': 'value'},
                    },
                ],
                service_payload={'extra_payload_field': 'value'},
            ),
            id='extra-payload-with-join',
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'held': {'ride': '100'},
                        'cleared': {
                            'ride': '1000',
                            'cashback': '100',
                            'tips': '20',
                        },
                    },
                },
                calculated_cashback='100',
                expected_calc_hold='100',
                expected_calc_clear='1000',
                expected_register_clear='1100',
                expected_cashback='200',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '100'},
                    {
                        'source': 'service',
                        'value': '100',
                        'extra_payload': {'extra_payload_field': 'value'},
                    },
                ],
                service_payload={'extra_payload_field': 'value'},
            ),
            marks=pytest.mark.config(CASHBACK_JOIN_PAYLOADS_ENABLED=False),
            id='extra-payload-without-join',
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'held': {'ride': '100'},
                        'cleared': {
                            'ride': '1000',
                            'cashback': '100',
                            'tips': '20',
                        },
                    },
                },
                calculated_cashback='100',
                expected_calc_hold='100',
                expected_calc_clear='1000',
                expected_register_clear='1100',
                expected_cashback='200',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '100'},
                    {
                        'source': 'service',
                        'value': '100',
                        'extra_payload': {
                            'base_amount': '100',
                            'extra_payload_field': 'value',
                            'cashback_service': 'yataxi',
                        },
                    },
                ],
                service_payload={
                    'base_amount': '100',
                    'cashback_service': 'yataxi',
                    'extra_payload_field': 'value',
                },
                expected_payload={
                    'cashback_service': 'yataxi',
                    'base_amount': '100',
                    'has_plus': True,
                },
            ),
            marks=pytest.mark.config(CASHBACK_JOIN_PAYLOADS_ENABLED=False),
            id='base-amount-in-payload',
        ),
        pytest.param(
            MyTestCase(
                service='yataxi',
                invoice={
                    'card': {
                        'held': {'ride': '100'},
                        'cleared': {
                            'ride': '1000',
                            'cashback': '100',
                            'tips': '20',
                        },
                    },
                },
                calculated_cashback='200',
                expected_calc_hold='100',
                expected_calc_clear='1000',
                expected_register_clear='1100',
                expected_cashback='300',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '100'},
                    {
                        'source': 'service',
                        'value': '100',
                        'extra_payload': {
                            'base_amount': '100',
                            'extra_payload_field': 'value',
                            'cashback_service': 'yataxi',
                        },
                    },
                    {
                        'source': 'possible_cashback_service',
                        'value': '100',
                        'extra_payload': {
                            'base_amount': '100',
                            'cashback_service': 'yataxi',
                        },
                    },
                ],
                service_payload={
                    'base_amount': '100',
                    'cashback_service': 'yataxi',
                    'extra_payload_field': 'value',
                },
                expected_payload={
                    'cashback_service': 'yataxi',
                    'base_amount': '100',
                    'has_plus': True,
                },
            ),
            marks=pytest.mark.config(CASHBACK_JOIN_PAYLOADS_ENABLED=False),
            id='possible-cashback',
        ),
        pytest.param(
            MyTestCase(
                service='lavka_isr',
                invoice={
                    'card': {
                        'held': {'1': '100', '2': '200'},
                        'cleared': {'3': '1000'},
                    },
                },
                calculated_cashback='200',
                expected_calc_hold='300',
                expected_calc_clear='1000',
                expected_register_clear='1300',
                expected_cashback='200',
                expected_cashback_by_source=[
                    {'source': 'user', 'value': '0'},
                    {'source': 'service', 'value': '200'},
                ],
            ),
            id='lavka_isr',
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'cashback', 'dst': 'archive-api'},
        {'src': 'cashback', 'dst': 'stq-agent'},
    ],
)
async def test_universal_cashback_processing(
        mock_cashback,
        mockserver,
        load_json,
        stq_runner,
        transactions_mock,
        stq,
        order_archive_mock,
        case: MyTestCase,
):
    @mock_cashback('/v2/internal/cashback/restore')
    async def _mock_restore_order(request, **kwargs):
        expected_order_created = INVOICE_CREATED
        request_order_created = datetime.datetime.fromisoformat(
            request.query['order_created_at'],
        )

        assert request_order_created == expected_order_created

        return {'order_id': 'order_id', 'service': case.service, 'version': 0}

    @mockserver.json_handler('/cashback/get')
    async def _mock_cashback_get(request, **kwargs):
        assert request.json == {
            'cleared': case.expected_calc_clear,
            'held': case.expected_calc_hold,
            'currency': 'RUB',
        }
        extra_payload = {}
        if case.service_payload is not None:
            extra_payload = {'payload': case.service_payload}

        possible_cashback = None
        marketing_cashback = case.calculated_cashback
        for cashback_by_source in case.expected_cashback_by_source:
            if cashback_by_source['source'] == 'possible_cashback_service':
                possible_cashback = {
                    'cashback': cashback_by_source['value'],
                    'payload': cashback_by_source['extra_payload'],
                }
                marketing_cashback = float(marketing_cashback) - float(
                    possible_cashback['cashback'],
                )
        return {
            'cashback': marketing_cashback,
            'currency': 'RUB',
            **extra_payload,
            'possible_cashback': possible_cashback,
        }

    @mock_cashback('/v2/internal/cashback/register')
    async def _mock_register_cashback(request, **kwargs):
        by_source = request.json['cashback_by_source']
        for source in by_source:
            assert source in case.expected_cashback_by_source
            case.expected_cashback_by_source.remove(source)
        assert not case.expected_cashback_by_source
        request.json.pop('cashback_by_source')
        assert request.json == {
            'cashback_sum': case.expected_cashback,
            'clear_sum': case.expected_register_clear,
            'currency': 'RUB',
            'payload': case.expected_payload,
            'version': 0,
            'yandex_uid': 'yandex_uid_1',
        }
        return {'status': const.REGISTER_STATUS_NEED_PROCESSING}

    @mockserver.json_handler('/blackbox', prefix=True)
    async def _mock_passport(request):
        assert request.query['attributes'] == '1015'
        assert request.query['uid'] == 'yandex_uid_1'
        return {
            'users': [
                {
                    'uid': {'value': 'yandex_uid_1'},
                    'login': 'yalogin',
                    'attributes': {'1015': 1},
                },
            ],
        }

    order_archive_mock.set_order_proc(DEFAULT_PROC)

    transactions_mock.invoice_retrieve_v2.update(**case.make_invoice_update())

    await stq_runner.universal_cashback_processing.call(
        task_id=f'order_id/{case.service}', args=('order_id', case.service),
    )

    if case.expected_register_cashback is not None:
        assert _mock_register_cashback.times_called == 0

    if case.expected_charge_queue is not None:
        assert stq[case.expected_charge_queue].times_called == 1


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                service='yataxi_v2',
                invoice={
                    'card': {
                        'held': {'ride': '100'},
                        'cleared': {
                            'ride': '1000',
                            'cashback': '100',
                            'tips': '20',
                        },
                    },
                    'yandex_card': {'held': {'ride': '100'}, 'cleared': {}},
                },
                expected_cleared_items=[
                    {
                        'payment_type': 'card',
                        'items': [
                            {'item_id': 'ride', 'amount': '1000'},
                            {'item_id': 'cashback', 'amount': '100'},
                            {'item_id': 'tips', 'amount': '20'},
                        ],
                    },
                    {'payment_type': 'yandex_card', 'items': []},
                ],
                expected_held_items=[
                    {
                        'payment_type': 'card',
                        'items': [{'item_id': 'ride', 'amount': '100'}],
                    },
                    {
                        'payment_type': 'yandex_card',
                        'items': [{'item_id': 'ride', 'amount': '100'}],
                    },
                ],
                calculated_cashback='600',
                expected_register_clear='1200',
                expected_cashback='600',
                expected_calc_hold='200',
                expected_calc_clear='1000',
                expected_cashback_by_source=[
                    {
                        'source': 'user',
                        'value': '100',
                        'extra_payload': {
                            'alias_id': 'alias_id',
                            'base_amount': '1000',
                            'cashback_service': 'yataxi',
                            'country': 'RU',
                            'oebs_mvp_id': 'MSKc',
                            'order_id': 'order_id',
                            'payment_type': 'card',
                            'tariff_class': 'econom',
                        },
                    },
                    {
                        'source': 'service',
                        'value': '200',
                        'extra_payload': {
                            'alias_id': 'alias_id',
                            'base_amount': '1000',
                            'cashback_service': 'yataxi',
                        },
                    },
                    {
                        'source': 'some_sponsor',
                        'value': '300',
                        'extra_payload': {
                            'country': 'RU',
                            'oebs_mvp_id': 'MSKc',
                            'order_id': 'order_id',
                            'payment_type': 'card',
                            'tariff_class': 'econom',
                        },
                    },
                ],
                expected_payload={'has_plus': True},
            ),
            id='yataxi-v2-url_v2',
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'cashback', 'dst': 'archive-api'},
        {'src': 'cashback', 'dst': 'stq-agent'},
    ],
)
async def test_configuration_with_url_v2(
        mock_cashback,
        mockserver,
        load_json,
        stq_runner,
        transactions_mock,
        stq,
        order_archive_mock,
        case: MyTestCase,
):
    @mock_cashback('/v2/internal/cashback/restore')
    async def _mock_restore_order(request, **kwargs):
        return {'order_id': 'order_id', 'service': case.service, 'version': 0}

    @mockserver.json_handler('/v2/cashback/get')
    async def _mock_cashback_get(request, **kwargs):
        assert request.json == {
            'order_id': 'order_id',
            'cleared': case.expected_cleared_items,
            'held': case.expected_held_items,
            'currency': 'RUB',
        }
        return {
            'cashback_by_sources': {
                'user': {
                    'amount': '100',
                    'payload': {
                        'alias_id': 'alias_id',
                        'base_amount': '1000',
                        'cashback_service': 'yataxi',
                        'country': 'RU',
                        'oebs_mvp_id': 'MSKc',
                        'order_id': 'order_id',
                        'payment_type': 'card',
                        'tariff_class': 'econom',
                    },
                },
                'service': {
                    'amount': '200',
                    'payload': {
                        'alias_id': 'alias_id',
                        'base_amount': '1000',
                        'cashback_service': 'yataxi',
                    },
                },
                'some_sponsor': {
                    'amount': '300',
                    'payload': {
                        'country': 'RU',
                        'oebs_mvp_id': 'MSKc',
                        'order_id': 'order_id',
                        'payment_type': 'card',
                        'tariff_class': 'econom',
                    },
                },
            },
        }

    @mock_cashback('/v2/internal/cashback/register')
    async def _mock_register_cashback(request, **kwargs):
        by_source = request.json['cashback_by_source']
        assert by_source == case.expected_cashback_by_source
        request.json.pop('cashback_by_source')
        assert request.json == {
            'cashback_sum': case.expected_cashback,
            'clear_sum': case.expected_register_clear,
            'currency': 'RUB',
            'payload': case.expected_payload,
            'version': 0,
            'yandex_uid': 'yandex_uid_1',
        }
        return {'status': const.REGISTER_STATUS_NEED_PROCESSING}

    @mockserver.json_handler('/blackbox', prefix=True)
    async def _mock_passport(request):
        assert request.query['attributes'] == '1015'
        assert request.query['uid'] == 'yandex_uid_1'
        return {
            'users': [
                {
                    'uid': {'value': 'yandex_uid_1'},
                    'login': 'yalogin',
                    'attributes': {'1015': 1},
                },
            ],
        }

    order_archive_mock.set_order_proc(DEFAULT_PROC)

    transactions_mock.invoice_retrieve_v2.update(**case.make_invoice_update())

    await stq_runner.universal_cashback_processing.call(
        task_id=f'order_id/{case.service}', args=('order_id', case.service),
    )

    assert _mock_register_cashback.times_called == 1
    assert stq[case.expected_charge_queue].times_called == 1


async def test_not_cashback_order(
        mock_cashback,
        mockserver,
        load_json,
        stq_runner,
        transactions_mock,
        stq,
):
    @mock_cashback('/v2/internal/cashback/restore')
    async def _mock_restore_order(request, **kwargs):
        return {'order_id': 'order_id', 'service': 'restaurants', 'version': 0}

    @mockserver.json_handler('/cashback/get')
    async def _mock_cashback_get(request, **kwargs):
        return aiohttp.web.Response(status=409)

    await stq_runner.universal_cashback_processing.call(
        args=('order_id', 'restaurants'),
    )

    assert stq.cashback_charge_processing.times_called == 0


async def test_not_cashback_order_v2(
        mock_cashback,
        mockserver,
        load_json,
        stq_runner,
        transactions_mock,
        stq,
):
    @mock_cashback('/v2/internal/cashback/restore')
    async def _mock_restore_order(request, **kwargs):
        return {'order_id': 'order_id', 'service': 'yataxi_v2', 'version': 0}

    @mockserver.json_handler('/v2/cashback/get')
    async def _mock_cashback_get(request, **kwargs):
        return aiohttp.web.Response(status=409)

    await stq_runner.universal_cashback_processing.call(
        args=('order_id', 'yataxi_v2'),
    )

    assert stq.cashback_charge_processing.times_called == 0


@pytest.mark.config(TVM_RULES=[{'src': 'cashback', 'dst': 'archive-api'}])
@pytest.mark.parametrize(
    'order_proc_update',
    [
        pytest.param(
            {'extra_data': {'cashback': {'is_cashback': False}}},
            id='not-cashback',
        ),
        pytest.param({'takeout': {'status': 'anonymized'}}, id='anonymized'),
    ],
)
async def test_cashback_check(
        order_archive_mock, stq, stq_runner, order_proc_update,
):
    order_proc = {
        '_id': 'order_id',
        'commit_state': 'done',
        'order': {'user_uid': '123456'},
        'created': datetime.datetime(2020, 9, 12, 12, 1, 1, tzinfo=tz.UTC),
        **order_proc_update,
    }
    order_archive_mock.set_order_proc(order_proc)
    await stq_runner.universal_cashback_processing.call(
        args=('order_id', 'yataxi'),
    )

    assert stq.cashback_charge_processing.times_called == 0


@pytest.mark.parametrize(
    'response_attributes,expected_payload',
    [
        pytest.param({}, {'has_plus': False}, id='no-attr'),
        pytest.param({'1015': 0}, {'has_plus': False}, id='attr-zero'),
        pytest.param({'543': 1}, {'has_plus': False}, id='other-attr'),
        pytest.param({'1015': 1}, {'has_plus': True}, id='attr-one'),
    ],
)
async def test_common_payload(
        stq3_context: stq_context.Context,
        mockserver,
        response_attributes,
        expected_payload,
):
    @mockserver.json_handler('/blackbox', prefix=True)
    def _mock_user_info(*args, **kwargs):
        return {
            'users': [
                {
                    'uid': {'value': 'yandex_uid'},
                    'login': 'yandex_login',
                    'attributes': response_attributes,
                },
            ],
        }

    payload = await cashback_services.get_common_payload(
        stq3_context, yandex_uid='yandex_uid',
    )

    assert payload == expected_payload


@pytest.mark.parametrize(
    'expected_payload',
    [
        pytest.param(
            {'campaign_name': 'mastercard'},
            marks=pytest.mark.config(
                CASHBACK_COMMON_PAYLOAD_KEYS=['campaign_name'],
            ),
        ),
        pytest.param(
            {'campaign_name': 'mastercard', 'base_amount': '1337'},
            marks=pytest.mark.config(
                CASHBACK_COMMON_PAYLOAD_KEYS=['campaign_name', 'base_amount'],
            ),
        ),
        pytest.param(
            {}, marks=pytest.mark.config(CASHBACK_COMMON_PAYLOAD_KEYS=[]),
        ),
    ],
)
async def test_extra_payload(
        stq3_context: stq_context.Context, expected_payload,
):
    service_payload = {
        'campaign_name': 'mastercard',
        'base_amount': '1337',
        'issuer': 'master',
    }
    extra_payload = cashback_services.get_extra_payload(
        stq3_context.config, service_payload,
    )
    assert extra_payload == expected_payload
