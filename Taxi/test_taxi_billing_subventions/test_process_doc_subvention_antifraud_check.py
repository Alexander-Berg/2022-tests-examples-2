import itertools

import attr
import pytest
import pytz

from taxi_billing_subventions import config
from taxi_billing_subventions.common import models
from taxi_billing_subventions.process_doc import _antifraud_common
from test_taxi_billing_subventions.test_process_doc import AccountsClient
from test_taxi_billing_subventions.test_process_doc import AntifraudClient


_NEW_BILLING_MIGRATION = {
    'subventions': {
        'enabled': {'narofominsk': [{'first_date': '0001-01-01'}]},
    },
}


@pytest.mark.now('2018-11-30T19:31:35')
@pytest.mark.parametrize(
    'doc_json, antifraud_response_json, new_billing_migration, '
    'stop_write_to_py2_collections_config, '
    'expected_docs_json, expected_accounts_json',
    [
        # Zone without hold - PAY
        (
            'no_hold_doc.json',
            'antifraud_response_pay.json',
            {},
            None,
            'no_hold_pay_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone without hold with notifications - PAY
        (
            'no_hold_with_notifications_doc.json',
            'antifraud_response_pay.json',
            {},
            None,
            'no_hold_with_notifications_pay_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone without hold - DELAY
        (
            'no_hold_eye_forward_doc.json',
            'antifraud_response_delay.json',
            {},
            None,
            'no_hold_delay_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone without hold - BLOCK
        (
            'no_hold_doc.json',
            'antifraud_response_block.json',
            {},
            None,
            'no_hold_block_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone without hold - BLOCK
        (
            'no_hold_with_notifications_doc.json',
            'antifraud_response_block.json',
            {},
            None,
            'no_hold_with_notifications_block_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone with hold - initial PAY
        (
            'hold_initial_doc.json',
            'antifraud_response_pay.json',
            {},
            None,
            'hold_initial_pay_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone with hold - second PAY
        (
            'hold_second_doc.json',
            'antifraud_response_pay.json',
            {},
            None,
            'hold_second_pay_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone with hold - second PAY new_billing
        (
            'hold_second_doc.json',
            'antifraud_response_pay.json',
            _NEW_BILLING_MIGRATION,
            None,
            'hold_second_pay_new_billing_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone with hold - initial DELAY
        (
            'hold_initial_doc.json',
            'antifraud_response_delay.json',
            {},
            None,
            'hold_initial_delay_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone with hold - second DELAY
        (
            'hold_second_doc.json',
            'antifraud_response_delay.json',
            {},
            None,
            'hold_second_delay_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone with hold - initial BLOCK
        (
            'hold_initial_doc.json',
            'antifraud_response_block.json',
            {},
            None,
            'hold_initial_block_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone with hold - second BLOCK
        (
            'hold_second_doc.json',
            'antifraud_response_block.json',
            {},
            None,
            'hold_second_block_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone without hold - pay subvention
        (
            'doc_with_subvention_payment.json',
            'antifraud_response_pay.json',
            {},
            None,
            'doc_with_subvention_payment_expected_docs.json',
            'doc_with_subvention_payment_expected_accounts.json',
        ),
        (
            'doc_with_commission_payment.json',
            'antifraud_response_pay.json',
            {},
            None,
            'doc_with_commission_payments_expected_docs.json',
            'doc_with_commission_payments_expected_accounts.json',
        ),
        (
            'doc_with_subvention_payment.json',
            'antifraud_response_block.json',
            {},
            None,
            'doc_with_subvention_payment_if_fraud_expected_docs.json',
            'doc_with_subvention_payment_if_fraud_expected_accounts.json',
        ),
        # Zone with hold - second PAY, stop write to py2 collections
        (
            'hold_second_doc.json',
            'antifraud_response_pay.json',
            {},
            {'__default__': '2019-04-01T00:00:00.000000+00:00'},
            'hold_second_pay_stop_write_to_py2_col_expected_docs.json',
            'empty_accounts.json',
        ),
        # Zone with hold - second BLOCK, stop write to py2 collections
        (
            'hold_second_doc.json',
            'antifraud_response_block.json',
            {},
            {'__default__': '2019-04-01T00:00:00.000000+00:00'},
            'hold_second_block_stop_write_to_py2_col_expected_docs.json',
            'empty_accounts.json',
        ),
    ],
)
async def test_get_docs_on_antifraud(
        db,
        load_json,
        load_py_json,
        doc_json,
        antifraud_response_json,
        new_billing_migration,
        stop_write_to_py2_collections_config,
        expected_docs_json,
        expected_accounts_json,
):
    # pylint: disable=protected-access
    doc = load_py_json(doc_json)
    antifraud_response = load_py_json(antifraud_response_json)
    expected_docs = load_py_json(expected_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    context = ContextData(
        db=db,
        new_billing_migration=new_billing_migration,
        stop_write_to_py2_collections=stop_write_to_py2_collections_config,
    )
    future_docs = await _antifraud_common.get_v2_future_documents(
        context=context,
        doc=doc,
        doc_kind='subvention_antifraud_check',
        doc_external_obj_id='antifraud_check/alias_id/some_alias_id',
        doc_id=12345678,
        response=antifraud_response,
        log_extra=None,
    )
    for actual, expected in itertools.zip_longest(future_docs, expected_docs):
        assert attr.asdict(actual) == attr.asdict(expected)
    assert context.accounts_client.created_accounts == expected_accounts


class ContextData:
    def __init__(
            self,
            db,
            new_billing_migration,
            stop_write_to_py2_collections=None,
    ):
        self.zones_cache = ZonesCache()
        self.config = config.Config()
        self.config.BILLING_SEND_DRIVER_FIX_PARK_COMMISSION = True
        self.config.SUBVENTION_ANTIFRAUD_NEEDED_STARTUP_WINDOW = 0
        self.config.NEW_BILLING_MIGRATION = new_billing_migration
        self.config.BILLING_SUBVENTIONS_ANTIFRAUD_PREFIX = 'test_new_billing_'
        self.config.BILLING_SUBVENTIONS_WRITE_DRIVER_FIX_INCOME_MINUTES = True
        if stop_write_to_py2_collections is not None:
            self.config.BILLING_SUBVENTIONS_STOP_WRITE_TO_PY2_COLLECTIONS = (
                stop_write_to_py2_collections
            )
        self.db = db
        self.antifraud_client = AntifraudClient()
        self.accounts_client = AccountsClient(
            balances={}, journal_entries=[], existing_accounts=[],
        )


class ZonesCache:
    @staticmethod
    def get_zone(name) -> models.Zone:
        return models.Zone(
            name=name,
            city_id='Москва',
            tzinfo=pytz.timezone('Europe/Moscow'),
            currency='RUB',
            locale='ru',
            vat=models.Vat.make_naive(12000),
            country='rus',
        )
