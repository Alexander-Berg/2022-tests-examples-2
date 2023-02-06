# pylint: disable=redefined-outer-name, invalid-name
import pytest

from billing_bank_orders import models
from billing_bank_orders.crontasks import read_fresh_additional_data
from billing_bank_orders.generated.cron import cron_context


@pytest.fixture
def driver_partner_payment_reconciled():
    return models.PaymentAdditionalData.from_yt(
        data={
            'BILLING_CLIENT_ID': 69113930,
            'BILLING_PAYSYS_TYPE': 'il_tax_withhold',
            'CREATION_DATE': '2020-01-16T03:43:00Z',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_0',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 0',
            'LAST_UPDATE_DATE': '2020-01-17T11:22:01Z',
            'PAYEE_ALTERNATE_NAME': 'ФИО_0',
            'PAYMENT_AMOUNT': '-1335.88',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ID': 69113930,
            'PAYMENT_ORDER_NUMBER': '250132',
            'PAYMENT_STATUS': 'RECONCILED',
            'PMT_HIST_ID': 100774,
        },
    )


@pytest.fixture
def driver_partner_payment_returned():
    return models.PaymentAdditionalData.from_yt(
        data={
            'BILLING_CLIENT_ID': 69117930,
            'BILLING_PAYSYS_TYPE': 'il_tax_withhold',
            'CREATION_DATE': '2020-01-16T03:43:27Z',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_2',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 2',
            'LAST_UPDATE_DATE': '2020-01-17T11:22:06Z',
            'PAYEE_ALTERNATE_NAME': 'ФИО_2',
            'PAYMENT_AMOUNT': '-4489.28',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ID': 69117930,
            'PAYMENT_ORDER_NUMBER': '250001',
            'PAYMENT_STATUS': 'RETURNED',
            'PMT_HIST_ID': 100772,
        },
    )


@pytest.fixture
def driver_partner_payment_void():
    return models.PaymentAdditionalData.from_yt(
        data={
            'BILLING_CLIENT_ID': 69117930,
            'BILLING_PAYSYS_TYPE': 'il_tax_withhold',
            'CREATION_DATE': '2020-01-16T03:43:27Z',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_2',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 2',
            'LAST_UPDATE_DATE': '2020-01-17T11:22:06Z',
            'PAYEE_ALTERNATE_NAME': 'ФИО_2',
            'PAYMENT_AMOUNT': '-4489.28',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ID': 69117930,
            'PAYMENT_ORDER_NUMBER': '250001',
            'PAYMENT_STATUS': 'VOID',
            'PMT_HIST_ID': 100772,
        },
    )


@pytest.fixture
def driver_partner_payment_deferred():
    return models.PaymentAdditionalData.from_yt(
        data={
            'BILLING_CLIENT_ID': 69117930,
            'BILLING_PAYSYS_TYPE': 'il_tax_withhold',
            'CREATION_DATE': '2020-01-16T03:43:27Z',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_2',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 2',
            'LAST_UPDATE_DATE': '2020-01-17T11:22:06Z',
            'PAYEE_ALTERNATE_NAME': 'ФИО_2',
            'PAYMENT_AMOUNT': '-4489.28',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ID': 69117930,
            'PAYMENT_ORDER_NUMBER': '250001',
            'PAYMENT_STATUS': 'DEFERRED',
            'PMT_HIST_ID': 100772,
        },
    )


@pytest.fixture
def driver_partner_payment_confirmed():
    return models.PaymentAdditionalData.from_yt(
        data={
            'BILLING_CLIENT_ID': 69113930,
            'BILLING_PAYSYS_TYPE': 'il_tax_withhold',
            'CREATION_DATE': '2020-01-16T03:43:00Z',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_0',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 0',
            'LAST_UPDATE_DATE': '2020-01-17T11:22:01Z',
            'PAYEE_ALTERNATE_NAME': 'ФИО_0',
            'PAYMENT_AMOUNT': '-1335.88',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ID': 69113930,
            'PAYMENT_ORDER_NUMBER': '250132',
            'PAYMENT_STATUS': 'CONFIRMED',
            'PMT_HIST_ID': 100774,
        },
    )


@pytest.fixture
def driver_partner_payment_transmitted():
    return models.PaymentAdditionalData.from_yt(
        data={
            'BILLING_CLIENT_ID': 69113930,
            'BILLING_PAYSYS_TYPE': 'il_tax_withhold',
            'CREATION_DATE': '2020-01-16T03:43:00Z',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_0',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 0',
            'LAST_UPDATE_DATE': '2020-01-17T11:22:01Z',
            'PAYEE_ALTERNATE_NAME': 'ФИО_0',
            'PAYMENT_AMOUNT': '-1335.88',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ID': 69113930,
            'PAYMENT_ORDER_NUMBER': '250132',
            'PAYMENT_STATUS': 'TRANSMITTED',
            'PMT_HIST_ID': 100774,
        },
    )


@pytest.fixture
def organization_payment():
    return models.PaymentAdditionalData.from_yt(
        data={
            'BILLING_CLIENT_ID': 69115270,
            'BILLING_PAYSYS_TYPE': 'il_tax_withhold',
            'CREATION_DATE': '2020-01-16T03:43:10Z',
            'EXT_BANK_ACCOUNT_NUM': 'SOME_BANK_ACCOUNT_1',
            'EXT_BANK_NAME': 'ПАО СУПЕР-БАНК 1',
            'LAST_UPDATE_DATE': '2020-01-17T11:22:03Z',
            'PAYEE_ALTERNATE_NAME': 'ФИО_1',
            'PAYMENT_AMOUNT': '-5465.45',
            'PAYMENT_CURRENCY_CODE': 'RUB',
            'PAYMENT_DATE': '2020-01-15T21:00:00Z',
            'PAYMENT_ID': 69115270,
            'PAYMENT_ORDER_NUMBER': '247164',
            'PAYMENT_STATUS': 'RECONCILED',
            'PMT_HIST_ID': 100771,
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
    result = read_fresh_additional_data.payment_for_driver_partner(
        driver_partner_payment_reconciled,
    )
    assert result is True
    result = read_fresh_additional_data.payment_for_driver_partner(
        driver_partner_payment_returned,
    )
    assert result is True
    result = read_fresh_additional_data.payment_for_driver_partner(
        driver_partner_payment_transmitted,
    )
    assert result is False
    result = read_fresh_additional_data.payment_for_driver_partner(
        driver_partner_payment_confirmed,
    )
    assert result is True
    result = read_fresh_additional_data.payment_for_driver_partner(
        driver_partner_payment_deferred,
    )
    assert result is False
    result = read_fresh_additional_data.payment_for_driver_partner(
        organization_payment,
    )
    assert result is True


async def test_new_processing_selector(driver_partner_payment_reconciled):
    bclid_time_config_dict = {'__default__': '2020-01-01T00:00:00+00:00'}
    result = read_fresh_additional_data.new_processing_for_bclid(
        driver_partner_payment_reconciled, bclid_time_config_dict,
    )
    assert result is True
    bclid_time_config_dict = {'__default__': '2025-01-01T00:00:00+00:00'}
    result = read_fresh_additional_data.new_processing_for_bclid(
        driver_partner_payment_reconciled, bclid_time_config_dict,
    )
    assert result is False
    bclid_time_config_dict = {
        '__default__': '2025-01-01T00:00:00+00:00',
        '69113930': '2020-01-01T00:00:00+00:00',
    }
    result = read_fresh_additional_data.new_processing_for_bclid(
        driver_partner_payment_reconciled, bclid_time_config_dict,
    )
    assert result is True

    bclid_time_config_dict = {
        '__default__': '2025-01-01T00:00:00+00:00',
        '69113930': '2020-02-01T00:00:00+00:00',
    }
    result = read_fresh_additional_data.new_processing_for_bclid(
        driver_partner_payment_reconciled, bclid_time_config_dict,
    )
    assert result is False


async def test_prepare_partner_payment_raw(
        driver_partner_payment_returned,
        driver_partner_payment_reconciled,
        driver_partner_payment_confirmed,
        driver_partner_payment_deferred,
        driver_partner_payment_void,
):
    expected_prepared = {
        'kind': 'driver_partner_raw',
        'topic': 'taxi/il_tax/69113930/bclid/69113930/raw',
        'external_ref': '100774',
        'event_at': '2020-01-17T14:22:01+03:00',
        'data': {
            'schema_version': 'v2',
            'topic_begin_at': '2020-01-16T00:00:00+03:00',
            'event_version': 100774,
            'driver_partner_topic': 'taxi/il_tax/69113930/bclid/69113930',
            'driver_income': {
                'billing_client_id': '69113930',
                'components': [
                    {
                        'kind': 'il_tax_withhold',
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
                                'billing_client_id': '69113930',
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
        result = read_fresh_additional_data.prepare_driver_payment_raw(
            payment=payment,
        )
        assert result.serialize() == expected_prepared

    expected_prepared = {
        'data': {
            'driver_income': {
                'components': [],
                'billing_client_id': '69117930',
            },
            'event_version': 100772,
            'schema_version': 'v2',
            'topic_begin_at': '2020-01-16T00:00:00+03:00',
            'driver_partner_topic': 'taxi/il_tax/69117930/bclid/69117930',
        },
        'event_at': '2020-01-17T14:22:06+03:00',
        'external_ref': '100772',
        'kind': 'driver_partner_raw',
        'topic': 'taxi/il_tax/69117930/bclid/69117930/raw',
    }
    for payment in (
            driver_partner_payment_deferred,
            driver_partner_payment_void,
            driver_partner_payment_returned,
    ):
        result = read_fresh_additional_data.prepare_driver_payment_raw(
            payment=payment,
        )
        assert result.serialize() == expected_prepared


@pytest.mark.config(
    BILLING_DRIVER_PARTNER_TAXES_BCLID_SELECTOR={
        '__default__': '2025-01-01T00:00:00+00:00',
        '1001': '2020-01-01T00:00:00+00:00',
    },
)
@pytest.mark.now('2020-03-27T00:00:00')
async def test_select_and_send_driver_partner_payments_raw(
        mockserver, monkeypatch, driver_partner_payment_reconciled,
):
    # pylint: disable=unused-variable
    context = cron_context.Context()
    await context.on_startup()

    expected_order = {
        'kind': 'driver_partner_raw',
        'topic': 'taxi/il_tax/69113930/bclid/69113930/raw',
        'external_ref': '100774',
        'event_at': '2020-01-17T14:22:01+03:00',
        'data': {
            'schema_version': 'v2',
            'topic_begin_at': '2020-01-16T00:00:00+03:00',
            'event_version': 100774,
            'driver_partner_topic': 'taxi/il_tax/69113930/bclid/69113930',
            'driver_income': {
                'billing_client_id': '69113930',
                'components': [
                    {
                        'kind': 'il_tax_withhold',
                        'currency': 'RUB',
                        'amount': '-1335.88',
                        'component_payload': {
                            'payment': {
                                'billing_client_id': '69113930',
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

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def post_v2_process_async(request):
        assert len(request.json['orders']) == 1
        assert request.json['orders'][0] == expected_order
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

    await read_fresh_additional_data.send_driver_partner_payments(
        context, driver_partner_payment_reconciled,
    )
