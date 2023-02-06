# pylint: disable=redefined-outer-name, invalid-name
import pytest

from billing_bank_orders import models
from billing_bank_orders.crontasks import read_fresh_payments
from billing_bank_orders.generated.cron import cron_context


@pytest.fixture
def driver_partner_payment_reconciled():
    return models.PaymentHistory.from_yt(
        data={
            'BATCH_PAYMENTS': [
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261555]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11111']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1000.00']],
                    ['PAYMENT_BATCH_ID', [123123221]],
                ],
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261554]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11112']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['300.00']],
                    ['PAYMENT_BATCH_ID', [123123222]],
                ],
                [
                    ['BILLING_CLIENT_ID', [69113931]],
                    ['BILLING_CONTRACT_ID', [1261556]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11113']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['35.88']],
                    ['PAYMENT_BATCH_ID', [123123223]],
                ],
            ],
            'BILLING_CLIENT_IDS': [69113930, 69113931],
            'CONC_REQUEST_ID': 72476239,
            'CREATION_DATE': '2020-01-16T03:43:00Z',
            'CUSTOMER_TYPE': 'SELFEMPLOYED',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_0',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 0',
            'INVOICE_COUNT': 3,
            'LAST_UPDATE_DATE': '2020-01-17T11:22:01Z',
            'ORG_ID': 64552,
            'PAYEE_ALTERNATE_NAME': 'ФИО_0',
            'PAYEE_JGZZ_FISCAL_CODE': 'SOME_FISCAL_CODE_0',
            'PAYMENT_AMOUNT': '1335.88',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_GUID': '9C397769-7309-0A73-E055-000006C63108',
            'PAYMENT_ID': 69113930,
            'PAYMENT_ORDER_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ORDER_NUMBER': '250132',
            'PAYMENT_STATUS': 'RECONCILED',
            'PAYMENT_TARGET': (
                'Опл.по Дог.РАС-475556 245.00 руб,'
                ' Опл.по Дог.457077/20 1051.67 руб,'
                ' Опл.по Дог.ОФ-457077/20 39.21 руб'
            ),
            'PMT_HIST_DATE': '2020-01-17T11:22:01Z',
            'PMT_HIST_ID': 100774,
            'RECONCILATION_DATE': None,
            'VOIDED_BY': None,
            'VOID_DATE': None,
            'VOID_REASON': None,
        },
    )


@pytest.fixture
def driver_partner_payment_returned():
    return models.PaymentHistory.from_yt(
        data={
            'BATCH_PAYMENTS': [
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261555]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11111']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1101.00']],
                    ['PAYMENT_BATCH_ID', [123123221]],
                ],
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261554]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11112']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1102.00']],
                    ['PAYMENT_BATCH_ID', [123123222]],
                ],
            ],
            'BILLING_CLIENT_IDS': [69117930],
            'CONC_REQUEST_ID': 72476239,
            'CREATION_DATE': '2020-01-16T03:43:27Z',
            'CUSTOMER_TYPE': 'SELFEMPLOYED',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_2',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 2',
            'INVOICE_COUNT': 3,
            'LAST_UPDATE_DATE': '2020-01-17T11:22:06Z',
            'ORG_ID': 64552,
            'PAYEE_ALTERNATE_NAME': 'ФИО_2',
            'PAYEE_JGZZ_FISCAL_CODE': 'SOME_FISCAL_CODE_2',
            'PAYMENT_AMOUNT': '4489.28',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_GUID': '9C397769-C025-0A73-E055-000006C63108',
            'PAYMENT_ID': 69117930,
            'PAYMENT_ORDER_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ORDER_NUMBER': '250001',
            'PAYMENT_STATUS': 'RETURNED',
            'PAYMENT_TARGET': (
                'Опл.по Дог.ОФ-454553/20 614.84 руб,'
                ' Опл.по Дог.454553/20 3161.44 руб,'
                ' Опл.по Дог.РАС-469644 713.00 руб'
            ),
            'PMT_HIST_DATE': '2020-01-17T11:22:06Z',
            'PMT_HIST_ID': 100772,
            'RECONCILATION_DATE': None,
            'VOIDED_BY': 23841,
            'VOID_DATE': '2020-01-17T11:22:03Z',
            'VOID_REASON': None,
        },
    )


@pytest.fixture
def driver_partner_payment_void():
    return models.PaymentHistory.from_yt(
        data={
            'BATCH_PAYMENTS': [
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261555]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11111']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1101.00']],
                    ['PAYMENT_BATCH_ID', [123123221]],
                ],
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261554]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11112']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1102.00']],
                    ['PAYMENT_BATCH_ID', [123123222]],
                ],
            ],
            'BILLING_CLIENT_IDS': [69117930],
            'CONC_REQUEST_ID': 72476239,
            'CREATION_DATE': '2020-01-16T03:43:27Z',
            'CUSTOMER_TYPE': 'SELFEMPLOYED',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_2',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 2',
            'INVOICE_COUNT': 3,
            'LAST_UPDATE_DATE': '2020-01-17T11:22:06Z',
            'ORG_ID': 64552,
            'PAYEE_ALTERNATE_NAME': 'ФИО_2',
            'PAYEE_JGZZ_FISCAL_CODE': 'SOME_FISCAL_CODE_2',
            'PAYMENT_AMOUNT': '4489.28',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_GUID': '9C397769-C025-0A73-E055-000006C63108',
            'PAYMENT_ID': 69117930,
            'PAYMENT_ORDER_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ORDER_NUMBER': '250001',
            'PAYMENT_STATUS': 'VOID',
            'PAYMENT_TARGET': (
                'Опл.по Дог.ОФ-454553/20 614.84 руб,'
                ' Опл.по Дог.454553/20 3161.44 руб,'
                ' Опл.по Дог.РАС-469644 713.00 руб'
            ),
            'PMT_HIST_DATE': '2020-01-17T11:22:06Z',
            'PMT_HIST_ID': 100772,
            'RECONCILATION_DATE': None,
            'VOIDED_BY': 23841,
            'VOID_DATE': '2020-01-17T11:22:03Z',
            'VOID_REASON': None,
        },
    )


@pytest.fixture
def driver_partner_payment_deferred():
    return models.PaymentHistory.from_yt(
        data={
            'BATCH_PAYMENTS': [
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261555]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11111']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1101.00']],
                    ['PAYMENT_BATCH_ID', [123123221]],
                ],
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261554]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11112']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1102.00']],
                    ['PAYMENT_BATCH_ID', [123123222]],
                ],
            ],
            'BILLING_CLIENT_IDS': [69117930],
            'CONC_REQUEST_ID': 72476239,
            'CREATION_DATE': '2020-01-16T03:43:27Z',
            'CUSTOMER_TYPE': 'SELFEMPLOYED',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_2',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 2',
            'INVOICE_COUNT': 3,
            'LAST_UPDATE_DATE': '2020-01-17T11:22:06Z',
            'ORG_ID': 64552,
            'PAYEE_ALTERNATE_NAME': 'ФИО_2',
            'PAYEE_JGZZ_FISCAL_CODE': 'SOME_FISCAL_CODE_2',
            'PAYMENT_AMOUNT': '4489.28',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_GUID': '9C397769-C025-0A73-E055-000006C63108',
            'PAYMENT_ID': 69117930,
            'PAYMENT_ORDER_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ORDER_NUMBER': '250001',
            'PAYMENT_STATUS': 'DEFERRED',
            'PAYMENT_TARGET': (
                'Опл.по Дог.ОФ-454553/20 614.84 руб,'
                ' Опл.по Дог.454553/20 3161.44 руб,'
                ' Опл.по Дог.РАС-469644 713.00 руб'
            ),
            'PMT_HIST_DATE': '2020-01-17T11:22:06Z',
            'PMT_HIST_ID': 100772,
            'RECONCILATION_DATE': None,
            'VOIDED_BY': 23841,
            'VOID_DATE': '2020-01-17T11:22:03Z',
            'VOID_REASON': None,
        },
    )


@pytest.fixture
def driver_partner_payment_confirmed():
    return models.PaymentHistory.from_yt(
        data={
            'BATCH_PAYMENTS': [
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261555]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11111']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1101.00']],
                    ['PAYMENT_BATCH_ID', [123123221]],
                ],
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261554]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11112']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1102.00']],
                    ['PAYMENT_BATCH_ID', [123123222]],
                ],
            ],
            'BILLING_CLIENT_IDS': [69113930],
            'CONC_REQUEST_ID': 72476239,
            'CREATION_DATE': '2020-01-16T03:43:00Z',
            'CUSTOMER_TYPE': 'SELFEMPLOYED',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_0',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 0',
            'INVOICE_COUNT': 3,
            'LAST_UPDATE_DATE': '2020-01-17T11:22:01Z',
            'ORG_ID': 64552,
            'PAYEE_ALTERNATE_NAME': 'ФИО_0',
            'PAYEE_JGZZ_FISCAL_CODE': 'SOME_FISCAL_CODE_0',
            'PAYMENT_AMOUNT': '1335.88',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_GUID': '9C397769-7309-0A73-E055-000006C63108',
            'PAYMENT_ID': 69113930,
            'PAYMENT_ORDER_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ORDER_NUMBER': '250132',
            'PAYMENT_STATUS': 'CONFIRMED',
            'PAYMENT_TARGET': (
                'Опл.по Дог.РАС-475556 245.00 руб,'
                ' Опл.по Дог.457077/20 1051.67 руб,'
                ' Опл.по Дог.ОФ-457077/20 39.21 руб'
            ),
            'PMT_HIST_DATE': '2020-01-17T11:22:01Z',
            'PMT_HIST_ID': 100774,
            'RECONCILATION_DATE': None,
            'VOIDED_BY': None,
            'VOID_DATE': None,
            'VOID_REASON': None,
        },
    )


@pytest.fixture
def driver_partner_payment_transmitted():
    return models.PaymentHistory.from_yt(
        data={
            'BATCH_PAYMENTS': [
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261555]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11111']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1101.00']],
                    ['PAYMENT_BATCH_ID', [123123221]],
                ],
                [
                    ['BILLING_CLIENT_ID', [69113930]],
                    ['BILLING_CONTRACT_ID', [1261554]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11112']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1102.00']],
                    ['PAYMENT_BATCH_ID', [123123222]],
                ],
            ],
            'BILLING_CLIENT_IDS': [69113930],
            'CONC_REQUEST_ID': 72476239,
            'CREATION_DATE': '2020-01-16T03:43:00Z',
            'CUSTOMER_TYPE': 'SELFEMPLOYED',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_0',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 0',
            'INVOICE_COUNT': 3,
            'LAST_UPDATE_DATE': '2020-01-17T11:22:01Z',
            'ORG_ID': 64552,
            'PAYEE_ALTERNATE_NAME': 'ФИО_0',
            'PAYEE_JGZZ_FISCAL_CODE': 'SOME_FISCAL_CODE_0',
            'PAYMENT_AMOUNT': '1335.88',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_GUID': '9C397769-7309-0A73-E055-000006C63108',
            'PAYMENT_ID': 69113930,
            'PAYMENT_ORDER_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ORDER_NUMBER': '250132',
            'PAYMENT_STATUS': 'TRANSMITTED',
            'PAYMENT_TARGET': (
                'Опл.по Дог.РАС-475556 245.00 руб,'
                ' Опл.по Дог.457077/20 1051.67 руб,'
                ' Опл.по Дог.ОФ-457077/20 39.21 руб'
            ),
            'PMT_HIST_DATE': '2020-01-17T11:22:01Z',
            'PMT_HIST_ID': 100774,
            'RECONCILATION_DATE': None,
            'VOIDED_BY': None,
            'VOID_DATE': None,
            'VOID_REASON': None,
        },
    )


@pytest.fixture
def organization_payment():
    return models.PaymentHistory.from_yt(
        data={
            'BATCH_PAYMENTS': [
                [
                    ['BILLING_CLIENT_ID', [69115270]],
                    ['BILLING_CONTRACT_ID', [1261555]],
                    ['CONTRACT_ALIAS', ['CONTRACT-11111']],
                    ['CURRENCY_CODE', ['RUB']],
                    ['PAYMENT_AMOUNT', ['1101.00']],
                    ['PAYMENT_BATCH_ID', [123123221]],
                ],
            ],
            'BILLING_CLIENT_IDS': [69115270],
            'CONC_REQUEST_ID': 72476239,
            'CREATION_DATE': '2020-01-16T03:43:10Z',
            'CUSTOMER_TYPE': 'ORGANIZATION',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_1',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 1',
            'INVOICE_COUNT': 2,
            'LAST_UPDATE_DATE': '2020-01-17T11:22:03Z',
            'ORG_ID': 64552,
            'PAYEE_ALTERNATE_NAME': 'ФИО_1',
            'PAYEE_JGZZ_FISCAL_CODE': 'SOME_FISCAL_CODE_1',
            'PAYMENT_AMOUNT': '5465.45',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_GUID': '9C397769-8CF4-0A73-E055-000006C63108',
            'PAYMENT_ID': 69115270,
            'PAYMENT_ORDER_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ORDER_NUMBER': '247164',
            'PAYMENT_STATUS': 'RECONCILED',
            'PAYMENT_TARGET': (
                'Опл.по Дог.РАС-471400 974.00 руб,'
                ' Опл.по Дог.455688/20 4491.45 руб'
            ),
            'PMT_HIST_DATE': '2020-01-17T11:22:03Z',
            'PMT_HIST_ID': 100771,
            'RECONCILATION_DATE': None,
            'VOIDED_BY': None,
            'VOID_DATE': None,
            'VOID_REASON': None,
        },
    )


async def test_driver_partner_payment_selector(
        driver_partner_payment_reconciled,
        driver_partner_payment_returned,
        driver_partner_payment_confirmed,
        driver_partner_payment_transmitted,
        driver_partner_payment_deferred,
        organization_payment,
):
    result = read_fresh_payments.payment_for_driver_partner(
        driver_partner_payment_reconciled,
    )
    assert result is True
    result = read_fresh_payments.payment_for_driver_partner(
        driver_partner_payment_returned,
    )
    assert result is True
    result = read_fresh_payments.payment_for_driver_partner(
        driver_partner_payment_transmitted,
    )
    assert result is False
    result = read_fresh_payments.payment_for_driver_partner(
        driver_partner_payment_confirmed,
    )
    assert result is True
    result = read_fresh_payments.payment_for_driver_partner(
        driver_partner_payment_deferred,
    )
    assert result is False
    result = read_fresh_payments.payment_for_driver_partner(
        organization_payment,
    )
    assert result is True


async def test_new_processing_selector(driver_partner_payment_reconciled):
    clid_time_config_dict = {'__default__': '2020-01-01T00:00:00+00:00'}
    result = read_fresh_payments.new_processing_for_clid(
        '1001', driver_partner_payment_reconciled, clid_time_config_dict,
    )
    assert result is True
    clid_time_config_dict = {'__default__': '2025-01-01T00:00:00+00:00'}
    result = read_fresh_payments.new_processing_for_clid(
        '1001', driver_partner_payment_reconciled, clid_time_config_dict,
    )
    assert result is False
    clid_time_config_dict = {
        '__default__': '2025-01-01T00:00:00+00:00',
        '1001': '2020-01-01T00:00:00+00:00',
    }
    result = read_fresh_payments.new_processing_for_clid(
        '1001', driver_partner_payment_reconciled, clid_time_config_dict,
    )
    assert result is True

    clid_time_config_dict = {
        '__default__': '2025-01-01T00:00:00+00:00',
        '1001': '2020-02-01T00:00:00+00:00',
    }
    result = read_fresh_payments.new_processing_for_clid(
        '1001', driver_partner_payment_reconciled, clid_time_config_dict,
    )
    assert result is False


async def test_prepare_partner_payment_raw(
        driver_partner_payment_returned,
        driver_partner_payment_reconciled,
        driver_partner_payment_confirmed,
        driver_partner_payment_deferred,
        driver_partner_payment_void,
):
    clid = 'some_clid'

    expected_prepared = {
        'kind': 'driver_partner_raw',
        'topic': 'taxi/driver_partner/69113930/clid/some_clid/raw',
        'external_ref': '100774',
        'event_at': '2020-01-17T14:22:01+03:00',
        'data': {
            'schema_version': 'v1',
            'topic_begin_at': '2020-01-16T00:00:00+03:00',
            'event_version': 100774,
            'driver_partner_topic': 'taxi/driver_partner/69113930',
            'billing_client_id_clids': [clid],
            'driver_income': {
                'clid': 'some_clid',
                'components': [
                    {
                        'kind': 'driver_partner',
                        'currency': 'RUB',
                        'amount': '-1335.88',
                        'component_payload': {
                            'payment': {
                                'order_number': '250132',
                                'payment_date': (
                                    '2020-01-15T21:00:00.000000+00:00'
                                ),
                                'account_number': 'SOME_BANK_ACCOUNT_0',
                                'bank_name': 'ПАО СУПЕР-БАНК 0',
                                'payee_name': 'ФИО_0',
                                'payment_id': '69113930',
                            },
                        },
                    },
                ],
            },
        },
    }
    for payment in (
            driver_partner_payment_reconciled,
            driver_partner_payment_confirmed,
    ):
        result = read_fresh_payments.prepare_driver_payment_raw(
            payment=payment,
            clid=clid,
            billing_client_id='69113930',
            clids=[clid],
            use_bclid=False,
        )
        assert result.serialize() == expected_prepared

    expected_prepared = {
        'data': {
            'driver_income': {'components': [], 'clid': 'some_clid'},
            'event_version': 100772,
            'schema_version': 'v1',
            'topic_begin_at': '2020-01-16T00:00:00+03:00',
            'driver_partner_topic': 'taxi/driver_partner/69117930',
            'billing_client_id_clids': [clid],
        },
        'event_at': '2020-01-17T14:22:06+03:00',
        'external_ref': '100772',
        'kind': 'driver_partner_raw',
        'topic': 'taxi/driver_partner/69117930/clid/some_clid/raw',
    }
    for payment in (
            driver_partner_payment_deferred,
            driver_partner_payment_void,
            driver_partner_payment_returned,
    ):
        result = read_fresh_payments.prepare_driver_payment_raw(
            payment=payment,
            clid=clid,
            billing_client_id='69113930',
            clids=[clid],
            use_bclid=False,
        )
        assert result.serialize() == expected_prepared


@pytest.mark.parametrize(
    'expected_order_path, clid',
    [
        ('order_with_total_amount.json', '1001'),
        ('order_with_bclid_amount.json', '1002'),
        ('order_v2.json', '1003'),
    ],
    ids=[
        'driver_partner_without_billing_client_id',
        'driver_partner_with_billing_client_id',
        'driver_partner_v2',
    ],
)
@pytest.mark.config(
    BILLING_DRIVER_PARTNER_PAYMENTS_ENABLED=True,
    BILLING_DRIVER_PARTNER_PAYMENTS_CLID_SELECTOR={
        '__default__': '2025-01-01T00:00:00+00:00',
        '1001': '2020-01-01T00:00:00+00:00',
        '1002': '2020-01-01T00:00:00+00:00',
        '1003': '2020-01-01T00:00:00+00:00',
    },
    BILLING_DRIVER_PARTNER_PAYMENTS_AMOUNT_BY_BCLID_SINCE={
        '__default__': '2099-01-01T00:00:00+00:00',
        '1002': '2020-01-01T00:00:00+00:00',
    },
    BILLING_DRIVER_PARTNER_PAYMENTS_V2_SINCE={
        '__default__': '2099-01-01T00:00:00+00:00',
        '1003': '2020-01-01T00:00:00+00:00',
    },
)
@pytest.mark.now('2020-03-27T00:00:00')
async def test_select_and_send_driver_partner_payments_raw(
        mockserver,
        monkeypatch,
        driver_partner_payment_reconciled,
        load_json,
        expected_order_path,
        clid,
):
    # pylint: disable=unused-variable
    context = cron_context.Context()
    await context.on_startup()

    expected_order = load_json(expected_order_path)
    actual_order = {}

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def post_v2_process_async(request):
        assert len(request.json['orders']) == 1
        actual_order.update(request.json['orders'][0])
        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'topic': 'taxi/driver_partner/clid/1001/69113930',
                        'external_ref': '100774',
                        'doc_id': 4774540016,
                    },
                ],
            },
        )

    await read_fresh_payments.send_driver_partner_payments(
        context, clid, '69113930', [clid], driver_partner_payment_reconciled,
    )
    assert actual_order == expected_order
