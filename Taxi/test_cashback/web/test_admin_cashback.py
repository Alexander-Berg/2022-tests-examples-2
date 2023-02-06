import copy
import dataclasses
import enum
import random
from typing import Dict
from typing import List

import pytest


class ExceptionCases(enum.Enum):
    NOT_CASHBACK_ORDER = 'NotCashbackOrder'
    NOT_CASHBACK_BY_SPONSOR = 'NotCashbackBySponsorInOrderProcException'
    NOT_CURRENT_PRICES = 'NotCurrentPricesInOrderProcException'

    NOT_CASHBACK_IN_INVOICE = 'NotCashbackInInvoiceException'
    INVOICE_NOT_FOUND = 'InvoiceNotFound'

    NOT_PLUS_CASHBACK = 'NotPlusCashback'


@dataclasses.dataclass
class CaseData:
    source: str
    calc: str
    paid: str


def _fill_test_data_class(
        raw_data: Dict[str, Dict[str, str]],
) -> List[CaseData]:
    result = []

    for source, values in raw_data.items():
        result.append(
            CaseData(source=source, calc=values['calc'], paid=values['paid']),
        )

    return result


def _generate_test_data(sponsors: List[str]) -> Dict[str, Dict[str, str]]:
    result = {}

    for sponsor in sponsors:
        rand_val = random.uniform(10.0, 250.0)
        round_val = str(round(rand_val, 2))

        result.update({sponsor: {'calc': round_val, 'paid': round_val}})

    return result


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(TVM_RULES=[{'src': 'cashback', 'dst': 'archive-api'}]),
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

DEFAULT_PROC = {
    '_id': 'order_id',
    'commit_state': 'done',
    'status': 'finished',
    'order': {
        'user_uid': 'yandex_uid_66',
        'taxi_status': 'complete',
        'performer': {
            'tariff': {'class': 'comfortplus'},
            'taxi_alias': {'id': 'alias_id'},
        },
        'nz': 'moscow',
        'cost': '300',
        'pricing_data': {
            'currency': {'name': 'RUB'},
            'user': {'data': {'country_code2': 'RU'}, 'meta': {}},
        },
        'current_prices': {
            # fill it in test
            'cashback_by_sponsor': {},
        },
    },
    'extra_data': {'cashback': {'is_cashback': True}},
    'payment_tech': {'type': 'card'},
}

DEFAULT_TRANSACTIONS = {
    'cashback': {
        'version': 1,
        'transactions': [],
        'operations': [],
        'commit_version': 1,
        'status': 'success',
        'rewarded': [
            # fill in test
        ],
    },
    'held': [{'payment_type': 'card', 'items': []}],
    'sum_to_pay': [],
    'cleared': [],
}


@pytest.mark.parametrize(
    'test_data, exceptions',
    [
        (_generate_test_data(['agent', 'fintech', 'mastercard']), []),
        (
            _generate_test_data(['agent', 'fintech']),
            [ExceptionCases.NOT_CURRENT_PRICES],
        ),
        (
            _generate_test_data(['agent', 'fintech']),
            [ExceptionCases.NOT_CASHBACK_BY_SPONSOR],
        ),
        (
            _generate_test_data(['agent', 'fintech']),
            [ExceptionCases.NOT_CASHBACK_IN_INVOICE],
        ),
        (
            _generate_test_data(['agent', 'fintech']),
            [ExceptionCases.INVOICE_NOT_FOUND],
        ),
        (
            _generate_test_data(['agent', 'fintech']),
            [ExceptionCases.NOT_CASHBACK_ORDER],
        ),
        (
            _generate_test_data(['agent', 'fintech']),
            [
                ExceptionCases.NOT_CURRENT_PRICES,
                ExceptionCases.INVOICE_NOT_FOUND,
            ],
        ),
        (
            _generate_test_data(['agent', 'fintech']),
            [
                ExceptionCases.NOT_CASHBACK_BY_SPONSOR,
                ExceptionCases.NOT_CASHBACK_IN_INVOICE,
            ],
        ),
        (
            _generate_test_data(['agent', 'fintech']),
            [
                ExceptionCases.NOT_CASHBACK_ORDER,
                ExceptionCases.INVOICE_NOT_FOUND,
            ],
        ),
        (
            _generate_test_data(['agent', 'fintech']),
            [ExceptionCases.NOT_PLUS_CASHBACK],
        ),
    ],
)
async def test_admin_cashback_info(
        taxi_cashback_web,
        order_archive_mock,
        transactions_mock,
        test_data,
        exceptions,
):
    data = _fill_test_data_class(test_data)

    any_calc_exc = any(
        exc in exceptions
        for exc in [
            ExceptionCases.NOT_CASHBACK_ORDER,
            ExceptionCases.NOT_CASHBACK_BY_SPONSOR,
            ExceptionCases.NOT_CURRENT_PRICES,
            ExceptionCases.NOT_PLUS_CASHBACK,
        ]
    )

    any_paid_exc = any(
        exc in exceptions
        for exc in [
            ExceptionCases.INVOICE_NOT_FOUND,
            ExceptionCases.NOT_CASHBACK_IN_INVOICE,
        ]
    )

    proc = copy.deepcopy(DEFAULT_PROC)
    for item in data:
        if any_calc_exc:
            if ExceptionCases.NOT_CASHBACK_BY_SPONSOR in exceptions:
                proc['order']['current_prices'].pop('cashback_by_sponsor')
            if (
                    ExceptionCases.NOT_CURRENT_PRICES in exceptions
                    or ExceptionCases.NOT_CASHBACK_ORDER in exceptions
            ):
                proc['order'].pop('current_prices')
            break
        proc['order']['current_prices']['cashback_by_sponsor'].update(
            {item.source: item.calc},
        )
        if item.source == 'agent':
            if ExceptionCases.NOT_PLUS_CASHBACK not in exceptions:
                proc['order']['current_prices']['cashback_price'] = item.calc

    order_archive_mock.set_order_proc(proc)

    transactions = copy.deepcopy(DEFAULT_TRANSACTIONS)
    for item in data:
        if any_paid_exc:
            if ExceptionCases.NOT_CASHBACK_IN_INVOICE in exceptions:
                transactions.pop('cashback')
            if ExceptionCases.INVOICE_NOT_FOUND in exceptions:
                transactions_mock.invoice_retrieve_v2.set_http_status(404)
                transactions['cashback'] = {}
                transactions['sum_to_pay'] = {}
                transactions['code'] = '404'
                transactions['message'] = 'Invoice not found'
            break
        transactions['cashback']['rewarded'].append(
            {
                'amount': item.paid,
                'source': item.source if item.source != 'agent' else 'user',
            },
        )
    transactions_mock.invoice_retrieve_v2.update(**transactions)

    resp = await taxi_cashback_web.get(
        '/admin/cashback', params={'order_id': 'order_id'},
    )

    assert resp.status == 200

    content = await resp.json()
    assert content

    cashbacks = content['cashbacks']
    assert cashbacks

    cashback_dict = {
        cashback_item['source_name']: CaseData(
            source=cashback_item['source_name'],
            calc=cashback_item['calculated'],
            paid=cashback_item['paid'],
        )
        for cashback_item in cashbacks
    }
    if any_calc_exc and any_paid_exc:
        assert cashback_dict == {'total': CaseData('total', '0', '0')}
        return

    for item in data:
        content_item = cashback_dict.get(item.source, None)

        assert content_item

        if any_calc_exc:
            assert content_item.calc == '0'
        else:
            assert item.calc == content_item.calc
        if any_paid_exc:
            assert content_item.paid == '0'
        else:
            assert item.paid == content_item.paid
