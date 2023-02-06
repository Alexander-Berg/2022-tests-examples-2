import pytest
from tests_processing.processing.bank import common
from tests_processing.processing.bank.product import helper


@pytest.mark.parametrize(
    'product', [common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
async def test_ok(
        processing,
        stq,
        core_client_mock,
        applications_mock,
        userinfo_mock,
        core_current_account_mock,
        agreements_mock,
        product,
):
    app_helper = helper.ProductHelper(
        core_client_mock,
        applications_mock,
        userinfo_mock,
        core_current_account_mock,
        agreements_mock,
        processing,
    )
    app_helper.set_values(product=product)
    app_helper.prepare_mocks()
    with stq.flushing():
        stq_name = 'bank_applications_product_status_polling'
        event_id = await app_helper.send_product_event(
            already_flushing_stq=True,
        )

        assert stq[stq_name].times_called == 1
        call = stq[stq_name].next_call()
        assert call['id'] == f'bank_applications_{common.APPLICATION_ID}'
        expected_call = {
            'application_id': common.APPLICATION_ID,
            'buid': common.BUID,
            'idempotency_token': event_id,
            'request_id': common.CORE_BANKING_REQUEST_ID,
            'client_ip': common.IP,
            'session_uuid': common.SESSION_UUID,
            'product': product,
            'yuid': common.YUID,
            'log_extra': call['kwargs']['log_extra'],
        }
        assert call['kwargs'] == expected_call
    app_helper.check_product_calls(default_value=1)
    await app_helper.send_product_after_event()
    if product == common.PRODUCT_WALLET:
        app_helper.check_after_calls(
            default_value=1,
            get_client_details=2,
            create_simplified=0,
            get_personal_data=0,
            submit_simplified=0,
        )
    else:
        app_helper.check_after_calls(default_value=1, get_client_details=2)


async def test_no_agreement_version(
        processing,
        core_client_mock,
        applications_mock,
        userinfo_mock,
        core_current_account_mock,
        agreements_mock,
):
    app_helper = helper.ProductHelper(
        core_client_mock,
        applications_mock,
        userinfo_mock,
        core_current_account_mock,
        agreements_mock,
        processing,
    )
    app_helper.set_values(agreement_version=None)
    app_helper.prepare_mocks()
    await app_helper.send_product_event()

    app_helper.check_product_calls(default_value=1, accept_agreement=0)


@pytest.mark.config(
    BANK_APPLICATIONS_PRODUCT_STAGE_ENABLED_MAP={'__default__': True},
    BANK_AGREEMENTS_INIT_UPFRONT_ACCEPTS_FROM_PROCAAS_ENTITIES=[
        'eda',
        'market',
    ],
)
@pytest.mark.parametrize(
    'product', [common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
async def test_upfront_accept_ok(
        mockserver,
        processing,
        stq,
        core_client_mock,
        applications_mock,
        userinfo_mock,
        core_current_account_mock,
        agreements_mock,
        product,
):
    app_helper = helper.ProductHelper(
        core_client_mock,
        applications_mock,
        userinfo_mock,
        core_current_account_mock,
        agreements_mock,
        processing,
    )
    app_helper.set_values(product=product)
    app_helper.prepare_mocks()

    @mockserver.json_handler('/agreements-internal/v1/init_upfront_accepts')
    def _mock_init_upfront_accepts(request):
        assert request.headers['X-Idempotency-Token'] == common.APPLICATION_ID
        assert request.json == {
            'buid': app_helper.buid,
            'source': 'PRO_REGISTRATION',
            'entities': ['eda', 'market'],
        }
        return mockserver.make_response(status=200)

    with stq.flushing():
        stq_name = 'bank_applications_product_status_polling'
        event_id = await app_helper.send_product_event(
            already_flushing_stq=True,
        )

        assert stq[stq_name].times_called == 1
        call = stq[stq_name].next_call()
        assert call['id'] == f'bank_applications_{common.APPLICATION_ID}'
        expected_call = {
            'application_id': common.APPLICATION_ID,
            'buid': common.BUID,
            'idempotency_token': event_id,
            'request_id': common.CORE_BANKING_REQUEST_ID,
            'client_ip': common.IP,
            'session_uuid': common.SESSION_UUID,
            'product': product,
            'yuid': common.YUID,
            'log_extra': call['kwargs']['log_extra'],
        }
        assert call['kwargs'] == expected_call
    app_helper.check_product_calls(default_value=1)
    await app_helper.send_product_after_event()
    if product == common.PRODUCT_WALLET:
        app_helper.check_after_calls(
            default_value=1,
            get_client_details=2,
            create_simplified=0,
            get_personal_data=0,
            submit_simplified=0,
        )
    else:
        app_helper.check_after_calls(default_value=1, get_client_details=2)
    assert _mock_init_upfront_accepts.times_called == (
        1 if product == common.PRODUCT_PRO else 0
    )


async def test_user_identified(
        processing,
        stq,
        core_client_mock,
        applications_mock,
        userinfo_mock,
        core_current_account_mock,
        agreements_mock,
):
    app_helper = helper.ProductHelper(
        core_client_mock,
        applications_mock,
        userinfo_mock,
        core_current_account_mock,
        agreements_mock,
        processing,
    )
    app_helper.set_values(
        product=common.PRODUCT_PRO, auth_level=common.AUTH_LEVEL_IDENTIFIED,
    )
    app_helper.prepare_mocks()
    with stq.flushing():
        stq_name = 'bank_applications_product_status_polling'
        event_id = await app_helper.send_product_event(
            already_flushing_stq=True,
        )

        assert stq[stq_name].times_called == 1
        call = stq[stq_name].next_call()
        assert call['id'] == f'bank_applications_{common.APPLICATION_ID}'
        expected_call = {
            'application_id': common.APPLICATION_ID,
            'buid': common.BUID,
            'idempotency_token': event_id,
            'request_id': common.CORE_BANKING_REQUEST_ID,
            'client_ip': common.IP,
            'session_uuid': common.SESSION_UUID,
            'product': common.PRODUCT_PRO,
            'yuid': common.YUID,
            'log_extra': call['kwargs']['log_extra'],
        }
        assert call['kwargs'] == expected_call
    app_helper.check_product_calls(default_value=1)
    await app_helper.send_product_after_event()
    app_helper.check_after_calls(
        default_value=1,
        get_client_details=2,
        create_simplified=0,
        get_personal_data=0,
        submit_simplified=0,
    )
