import attr
import pytest
import pytz

from taxi_billing_subventions import config
from taxi_billing_subventions.common import converters
from taxi_billing_subventions.common import models
from taxi_billing_subventions.process_doc import _antifraud_common
from test_taxi_billing_subventions.test_process_doc import AccountsClient
from test_taxi_billing_subventions.test_process_doc import AntifraudClient


@pytest.mark.now('2018-5-10T19:31:35')
@pytest.mark.parametrize(
    'doc_json,'
    'antifraud_response_json,'
    'expected_docs_json,'
    'expected_accounts_json,',
    [
        (
            'antifraud_check_driver_fix_b2b.json',
            'antifraud_response_pay.json',
            'expected_docs_driver_fix_b2b_to_pay.json',
            'expected_accounts_driver_fix_b2b_to_pay.json',
        ),
        (
            'antifraud_check_driver_fix_b2b.json',
            'antifraud_response_block.json',
            'expected_docs_driver_fix_b2b_in_case_of_fraud.json',
            'expected_accounts_driver_fix_b2b_in_case_of_fraud.json',
        ),
    ],
)
async def test_process_antifraud_check(
        db,
        load_json,
        load_py_json,
        doc_json,
        antifraud_response_json,
        expected_docs_json,
        expected_accounts_json,
):
    # pylint: disable=protected-access
    doc_dict = load_py_json(doc_json)
    doc = converters.convert_to_subvention_antifraud_check_v2(doc_dict['data'])
    antifraud_response = load_py_json(antifraud_response_json)
    expected_docs = load_py_json(expected_docs_json)
    expected_accounts = load_json(expected_accounts_json)
    context = ContextData(db)
    future_docs = await _antifraud_common.get_v2_future_documents(
        context=context,
        doc=doc,
        doc_kind='subvention_antifraud_check',
        doc_external_obj_id='antifraud_check/alias_id/some_alias_id',
        doc_id=12345678,
        response=antifraud_response,
        log_extra=None,
    )
    assert len(future_docs) == len(expected_docs)
    for actual, expected in zip(future_docs, expected_docs):
        assert attr.asdict(actual) == attr.asdict(expected)
    assert context.accounts_client.created_accounts == expected_accounts


class ContextData:
    def __init__(self, db):
        self.zones_cache = ZonesCache()
        self.config = config.Config()
        self.config.BILLING_SEND_DRIVER_FIX_PARK_COMMISSION = True
        self.config.SUBVENTION_ANTIFRAUD_NEEDED_STARTUP_WINDOW = 0
        self.config.NEW_BILLING_MIGRATION = {}
        self.config.BILLING_SUBVENTIONS_ANTIFRAUD_PREFIX = 'test_new_billing_'
        self.config.BILLING_SUBVENTIONS_WRITE_DRIVER_FIX_INCOME_MINUTES = True
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
