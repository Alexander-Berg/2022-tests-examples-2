import typing

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from plus_transactions_plugins import *  # noqa: F403 F401


@pytest.fixture
def transactions_ng_fixt(mockserver, load_json):
    class Context:
        invoice_id: str = 'ext_ref_id_1'
        id_namespace: str = 'cashback_levels'
        billing_service: str = 'card'
        invoice_yandex_uid: str = 'yandex_uid_1'
        invoice_currency: str = 'RUB'

        has_invoice: bool = True
        create_invoice_resp_code: int = 200
        has_cashback_in_invoice: bool = True
        cashback_status: str = 'init'
        cashback_rewarded: typing.List = []
        cashback_version: int = 1

        update_cashback_amount: str = '100'
        update_cashback_source: str = 'taxi'
        update_cashback_wallet: str = 'wallet_id_1'
        update_fiscal_nds: typing.Optional[str] = None
        update_fiscal_title: typing.Optional[str] = None
        update_cashback_resp_code: int = 200

        @staticmethod
        def make_error_response(code):
            return mockserver.make_response(
                status=code, json={'code': str(code), 'message': ''},
            )

    context = Context()

    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def _mock_retrieve_invoice(request):
        assert request.json['id'] == context.invoice_id
        assert request.json['id_namespace'] == context.id_namespace

        if context.has_invoice:
            invoice = load_json('default_invoice.json')
            invoice['id'] = context.invoice_id
            if context.has_cashback_in_invoice:
                invoice['cashback']['status'] = context.cashback_status
                invoice['cashback']['version'] = context.cashback_version
                invoice['cashback']['rewarded'] = context.cashback_rewarded
            else:
                invoice['cashback'] = None
            return invoice
        return context.make_error_response(404)

    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    def _mock_create_invoice(request):
        assert request.json['id'] == context.invoice_id
        assert request.json['id_namespace'] == context.id_namespace
        assert request.json['yandex_uid'] == context.invoice_yandex_uid
        assert request.json['currency'] == context.invoice_currency

        if context.create_invoice_resp_code != 200:
            return context.make_error_response(
                context.create_invoice_resp_code,
            )
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/transactions-ng/v2/cashback/update')
    def _mock_update_cashback(request):
        assert request.json['invoice_id'] == context.invoice_id
        assert request.json['id_namespace'] == context.id_namespace
        assert request.json['billing_service'] == context.billing_service

        assert request.json['operation_id'] == context.invoice_id + '_' + str(
            context.cashback_version,
        )
        assert request.json['reward'] == [
            {
                'amount': context.update_cashback_amount,
                'source': context.update_cashback_source,
            },
        ]
        assert request.json['wallet_account'] == context.update_cashback_wallet
        assert request.json['yandex_uid'] == context.invoice_yandex_uid

        if context.update_cashback_resp_code != 200:
            return context.make_error_response(
                context.update_cashback_resp_code,
            )
        return mockserver.make_response(status=200, json={})

    # pylint: disable=attribute-defined-outside-init
    context.mock_retrieve_invoice = _mock_retrieve_invoice
    context.mock_create_invoice = _mock_create_invoice
    context.mock_update_cashback = _mock_update_cashback
    # pylint: enable=attribute-defined-outside-init

    return context
