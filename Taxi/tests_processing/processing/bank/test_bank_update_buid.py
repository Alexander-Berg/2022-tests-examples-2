import pytest
from tests_processing.processing.bank import common

BUID = 'buid-1'
YUID = '8421'
PHONE_NUMBER = '+79037842423'

STATUS_SUCCESS = 'SUCCESS'
STATUS_FAILED = 'FAILED'
STATUS_PENDING = 'PENDING'

CORE_BANKING_REQUEST_ID = 'some_javist_id'
APPLICATION_ID = '123456789abcdefgh'

IP = '127.0.0.1'


@pytest.mark.parametrize(
    'product, has_ya_plus, plus_offer_accepted, plus_created',
    [
        (None, None, None, False),
        (common.PRODUCT_WALLET, False, True, True),
        (common.PRODUCT_WALLET, None, None, False),
        (common.PRODUCT_PRO, False, True, False),
    ],
)
async def test_bank_applications_good_anon_with_phone_number_final(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        product,
        has_ya_plus,
        plus_offer_accepted,
        plus_created,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP,
        YUID,
        BUID,
        PHONE_NUMBER,
        CORE_BANKING_REQUEST_ID,
        APPLICATION_ID,
        common.SESSION_UUID,
        product=product,
        has_ya_plus=has_ya_plus,
        plus_offer_accepted=plus_offer_accepted,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    await helper.send_anon_event()
    helper.check_anon_calls(default_value=1)
    assert not helper.processing_mock.received_events
    core_client_mock.application_status = STATUS_SUCCESS
    assert helper.processing_mock.create_event.handler.times_called == 0
    await helper.send_update_buid_event()
    assert helper.userinfo_mock.update_buid_status.handler.times_called == 1
    assert helper.processing_mock.create_event.handler.times_called == 0
    assert helper.applications_mock.set_status.handler.times_called == 1
    assert (
        helper.applications_mock.create_plus_subscription.handler.times_called
        == (1 if plus_created else 0)
    )
    helper.check_update_buid_calls(
        update_buid_status=1,
        add_product=(product is not None),
        update_app_status=1,
    )
    assert applications_mock.card_internal_create_app.handler.times_called == 1
    assert applications_mock.card_internal_submit.handler.times_called == 1
    assert (
        core_client_mock.agreement_get_by_request_id.handler.times_called == 1
    )


@pytest.mark.config(
    BANK_AGREEMENTS_INIT_UPFRONT_ACCEPTS_FROM_PROCAAS_ENABLED=True,
    BANK_AGREEMENTS_INIT_UPFRONT_ACCEPTS_FROM_PROCAAS_ENTITIES=[
        'eda',
        'market',
    ],
)
@pytest.mark.parametrize(
    'product', [None, common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
async def test_bank_applications_good_anon_with_phone_number_final_upfront_accepts(
        mockserver,
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        product,
):
    @mockserver.json_handler('/agreements-internal/v1/init_upfront_accepts')
    def _mock_phone_update(request):
        assert request.headers['X-Idempotency-Token'] == APPLICATION_ID
        assert request.json == {
            'buid': BUID,
            'source': 'PRO_REGISTRATION',
            'entities': ['eda', 'market'],
        }
        return mockserver.make_response(status=200)

    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP,
        YUID,
        BUID,
        PHONE_NUMBER,
        CORE_BANKING_REQUEST_ID,
        APPLICATION_ID,
        common.SESSION_UUID,
        product=product,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    await helper.send_anon_event()
    helper.check_anon_calls(default_value=1)
    assert not helper.processing_mock.received_events
    core_client_mock.application_status = STATUS_SUCCESS
    assert helper.processing_mock.create_event.handler.times_called == 0
    await helper.send_update_buid_event()
    assert helper.userinfo_mock.update_buid_status.handler.times_called == 1
    assert helper.processing_mock.create_event.handler.times_called == 0
    assert helper.applications_mock.set_status.handler.times_called == 1
    helper.check_update_buid_calls(
        update_buid_status=1,
        add_product=(product is not None),
        update_app_status=1,
    )
    assert applications_mock.card_internal_create_app.handler.times_called == 1
    assert applications_mock.card_internal_submit.handler.times_called == 1
    assert (
        core_client_mock.agreement_get_by_request_id.handler.times_called == 1
    )
    assert _mock_phone_update.times_called == (
        1 if product == common.PRODUCT_PRO else 0
    )


@pytest.mark.parametrize(
    'error_code, expected_tries, create_event_times, buid_stq_fail',
    [(400, 1, 1, True), (500, 2, 1, True)],
)
async def test_bank_anon_update_buid_response_error(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        error_code,
        expected_tries,
        create_event_times,
        buid_stq_fail,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP, YUID, BUID, PHONE_NUMBER, CORE_BANKING_REQUEST_ID, APPLICATION_ID,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = STATUS_SUCCESS
    userinfo_mock.update_buid_status.response_code = error_code

    await helper.send_anon_event()
    await helper.send_update_buid_event(stq_fail=buid_stq_fail)
    assert (
        helper.processing_mock.create_event.handler.times_called
        == create_event_times
    )
    helper.check_update_buid_calls(update_buid_status=expected_tries)


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_anon_set_update_buid_response_first_fail(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        error_type,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP, YUID, BUID, PHONE_NUMBER, CORE_BANKING_REQUEST_ID, APPLICATION_ID,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = STATUS_SUCCESS
    if error_type == '500':
        userinfo_mock.update_buid_status.first_fail = True
    elif error_type == 'timeout':
        userinfo_mock.update_buid_status.first_timeout = True
    else:
        assert False

    await helper.send_anon_event()
    await helper.send_update_buid_event()
    helper.check_update_buid_calls(update_buid_status=2, update_app_status=1)


@pytest.mark.parametrize(
    'error_code, expected_tries, buid_stq_fail',
    [(400, 1, True), (500, 2, True)],
)
@pytest.mark.parametrize(
    'product', [common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
async def test_bank_anon_add_product_response_error(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        error_code,
        expected_tries,
        buid_stq_fail,
        product,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP,
        YUID,
        BUID,
        PHONE_NUMBER,
        CORE_BANKING_REQUEST_ID,
        APPLICATION_ID,
        product=product,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = STATUS_SUCCESS
    userinfo_mock.add_product.response_code = error_code

    await helper.send_anon_event()
    await helper.send_update_buid_event(stq_fail=buid_stq_fail)
    helper.check_update_buid_calls(
        default_value=1, add_product=expected_tries, update_app_status=0,
    )


@pytest.mark.parametrize(
    'product', [common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_anon_add_response_response_first_fail(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        error_type,
        product,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP,
        YUID,
        BUID,
        PHONE_NUMBER,
        CORE_BANKING_REQUEST_ID,
        APPLICATION_ID,
        product=product,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = STATUS_SUCCESS
    if error_type == '500':
        userinfo_mock.add_product.first_fail = True
    elif error_type == 'timeout':
        userinfo_mock.add_product.first_timeout = True
    else:
        assert False

    await helper.send_anon_event()
    await helper.send_update_buid_event()
    helper.check_update_buid_calls(
        default_value=1, add_product=2, update_app_status=1,
    )


# test that we don't register user and create wallet
# if not create card because got 4* during card issue starting
@pytest.mark.parametrize(
    'get_agreement_code,create_app_code,submit_app_code',
    [
        (400, 200, 200),
        (409, 200, 200),
        (200, 400, 200),
        (200, 409, 200),
        (200, 200, 400),
        (200, 200, 409),
    ],
)
async def test_bank_anon_create_application_card_fail(
        processing,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        create_app_code,
        submit_app_code,
        get_agreement_code,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP,
        YUID,
        BUID,
        PHONE_NUMBER,
        CORE_BANKING_REQUEST_ID,
        APPLICATION_ID,
        common.SESSION_UUID,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = STATUS_SUCCESS

    core_client_mock.agreement_get_by_request_id.response_code = (
        get_agreement_code
    )
    applications_mock.card_internal_create_app.response_code = create_app_code
    applications_mock.card_internal_submit.response_code = submit_app_code

    await helper.send_anon_event()
    await helper.send_update_buid_event(stq_fail=True)

    helper.check_update_buid_calls(update_buid_status=1)

    assert (
        core_client_mock.agreement_get_by_request_id.handler.times_called == 1
    )
    assert applications_mock.card_internal_create_app.handler.times_called == (
        get_agreement_code == 200
    )
    assert applications_mock.card_internal_submit.handler.times_called == (
        get_agreement_code == 200 and create_app_code == 200
    )


@pytest.mark.parametrize(
    'create_simplified_code,get_personal_data_code,submit_simplified_code,update_app_status',
    [
        (400, 200, 200, 0),
        (409, 200, 200, 0),
        (200, 400, 200, 1),
        (200, 409, 200, 1),
        (200, 200, 400, 1),
        (200, 200, 409, 1),
    ],
)
async def test_bank_anon_create_application_simpl_fail(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        create_simplified_code,
        get_personal_data_code,
        submit_simplified_code,
        update_app_status,
):
    helper = common.AnonHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        IP,
        YUID,
        BUID,
        PHONE_NUMBER,
        CORE_BANKING_REQUEST_ID,
        APPLICATION_ID,
        common.SESSION_UUID,
        product=common.PRODUCT_PRO,
    )
    await helper.create_anon_application()
    helper.prepare_mocks()
    core_client_mock.application_status = STATUS_SUCCESS

    applications_mock.simplified_internal_create_app.response_code = (
        create_simplified_code
    )
    applications_mock.reg_get_personal_data.response_code = (
        get_personal_data_code
    )
    applications_mock.simplified_internal_submit_app.response_code = (
        submit_simplified_code
    )

    await helper.send_anon_event()
    await helper.send_update_buid_event(stq_fail=True)

    helper.check_update_buid_calls(
        default_value=1, update_app_status=update_app_status,
    )

    assert (
        applications_mock.simplified_internal_create_app.handler.times_called
        == 1
    )
    assert applications_mock.reg_get_personal_data.handler.times_called == (
        create_simplified_code == 200
    )
    assert (
        applications_mock.simplified_internal_submit_app.handler.times_called
        == (create_simplified_code == 200 and get_personal_data_code == 200)
    )
