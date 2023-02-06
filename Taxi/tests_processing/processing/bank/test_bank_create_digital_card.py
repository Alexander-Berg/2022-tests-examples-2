import json

import pytest
from tests_processing.processing.bank import issue_digital_card_helper

BUID = 'buid-1'
YUID = '8421'
SESSION_UUID = 'fac13679-73f7-465f-b94e-f359525850ec'
CORE_BANKING_REQUEST_ID = 'some_javist_id'
APPLICATION_ID = '123456789abcdefgh'

STATUS_SUCCESS = 'SUCCESS'
PROCESSING_SUCCESS = 'PROCESSING'
STATUS_FAILED = 'FAILED'
STATUS_PENDING = 'PENDING'

PUBLIC_AGREEMENT_ID = 'test_public_agreement_id'
CARD_TYPE = 'DIGITAL'


@pytest.mark.parametrize(
    'card_type_payload,card_type_request',
    [
        ('DIGITAL', 'DIGITAL'),
        ('MIR_DIGITAL', 'MIR_DIGITAL'),
        (None, 'DIGITAL'),
    ],
)
async def test_bank_applications_create_digital_card_ok(
        processing, mockserver, card_type_payload, card_type_request,
):
    @mockserver.json_handler('/processing/v1/bank/applications/create-event')
    async def mock_send_event_to_processing(request):
        return {'result': 'ok'}

    @mockserver.json_handler('/v1/card/issue')
    async def mock_core_card(request):
        data = json.loads(request.get_data())
        assert data['public_agreement_id'] == PUBLIC_AGREEMENT_ID
        assert data['card_type'] == card_type_request
        return {
            'request_id': CORE_BANKING_REQUEST_ID,
            'status': STATUS_SUCCESS,
        }

    # create_application
    event_id = await processing.bank.applications.send_event(
        item_id=APPLICATION_ID,
        payload={'kind': 'init', 'type': 'DIGITAL_CARD_ISSUE'},
        stq_queue='bank_applications_procaas',
    )
    assert event_id

    # submit_code
    update_payload = {
        'kind': 'update',
        'type': 'DIGITAL_CARD_ISSUE',
        'buid': BUID,
        'agreement_id': PUBLIC_AGREEMENT_ID,
        'session_uuid': SESSION_UUID,
    }
    if card_type_payload:
        update_payload['card_type'] = card_type_payload
    event_id = await processing.bank.applications.send_event(
        item_id=APPLICATION_ID,
        payload=update_payload,
        stq_queue='bank_applications_procaas',
    )
    assert event_id

    assert mock_core_card.times_called == 1
    assert mock_send_event_to_processing.times_called == 1


async def test_bank_applications_create_digital_card_duplicate(
        processing, mockserver,
):
    @mockserver.json_handler('/processing/v1/bank/applications/create-event')
    async def mock_send_event_to_processing(request):
        return {'result': 'ok'}

    @mockserver.json_handler('/v1/card/issue')
    async def mock_core_card(request):
        data = json.loads(request.get_data())
        assert data['public_agreement_id'] == PUBLIC_AGREEMENT_ID
        assert data['card_type'] == CARD_TYPE
        return {
            'request_id': CORE_BANKING_REQUEST_ID,
            'status': STATUS_SUCCESS,
        }

    # create_application
    event_id = await processing.bank.applications.send_event(
        item_id=APPLICATION_ID,
        payload={'kind': 'init', 'type': 'DIGITAL_CARD_ISSUE'},
        stq_queue='bank_applications_procaas',
        idempotency_token='foo',
    )
    assert event_id

    # create_application with same idempotency token
    event_id_duplicate = await processing.bank.applications.send_event(
        item_id=APPLICATION_ID,
        payload={'kind': 'init', 'type': 'DIGITAL_CARD_ISSUE'},
        stq_queue='bank_applications_procaas',
        idempotency_token='foo',
    )
    assert event_id == event_id_duplicate

    # submit_code
    event_id = await processing.bank.applications.send_event(
        item_id=APPLICATION_ID,
        payload={
            'kind': 'update',
            'type': 'DIGITAL_CARD_ISSUE',
            'buid': BUID,
            'agreement_id': PUBLIC_AGREEMENT_ID,
            'session_uuid': SESSION_UUID,
        },
        stq_queue='bank_applications_procaas',
    )
    assert event_id

    assert mock_core_card.times_called == 1
    assert mock_send_event_to_processing.times_called == 1


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {'public_agreement_id': PUBLIC_AGREEMENT_ID},
            'none_success',
            {
                'public_agreement_id': PUBLIC_AGREEMENT_ID,
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            1,
        ),
        (
            {'public_agreement_id': PUBLIC_AGREEMENT_ID},
            'none_failed',
            {
                'public_agreement_id': PUBLIC_AGREEMENT_ID,
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_FAILED,
            },
            1,
        ),
        (
            {'public_agreement_id': PUBLIC_AGREEMENT_ID},
            'none_pending',
            {
                'public_agreement_id': PUBLIC_AGREEMENT_ID,
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_PENDING,
            },
            1,
        ),
        (
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            'fail_before',
            {
                'is_error': True,
                'errors': ['unknown error at get-application-data-stage'],
            },
            0,
        ),
        (
            {'public_agreement_id': PUBLIC_AGREEMENT_ID},
            'one_fail',
            {
                'public_agreement_id': PUBLIC_AGREEMENT_ID,
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            2,
        ),
        (
            {'public_agreement_id': PUBLIC_AGREEMENT_ID},
            'one_timeout',
            {
                'public_agreement_id': PUBLIC_AGREEMENT_ID,
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            2,
        ),
        (
            {'public_agreement_id': PUBLIC_AGREEMENT_ID},
            'none_success_errors_list',
            {
                'public_agreement_id': PUBLIC_AGREEMENT_ID,
                'is_error': False,
                'errors': ['0:no errors', '1:but in lines'],
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            1,
        ),
        (
            {'public_agreement_id': PUBLIC_AGREEMENT_ID},
            'none_success_empty_errors_list',
            {
                'public_agreement_id': PUBLIC_AGREEMENT_ID,
                'is_error': False,
                'errors': ['0:no errors'],
                'core_banking_request_id': CORE_BANKING_REQUEST_ID,
                'core_banking_status': STATUS_SUCCESS,
            },
            1,
        ),
    ],
)
async def test_bank_digital_card_stage_digital_card_create(
        processing,
        core_card_mock,
        applications_mock,
        processing_mock,
        started_shared,
        error_type,
        expected_shared,
        expected_tries,
):
    helper = issue_digital_card_helper.DigitalCardHelper(
        core_card_mock, applications_mock, processing_mock, processing,
    )
    helper.set_values(
        YUID,
        BUID,
        CORE_BANKING_REQUEST_ID,
        APPLICATION_ID,
        PUBLIC_AGREEMENT_ID,
    )
    await helper.create_digital_card_application()
    helper.prepare_mocks()
    if error_type == 'none_failed':
        core_card_mock.application_status = STATUS_FAILED
    elif error_type == 'none_success':
        core_card_mock.application_status = STATUS_SUCCESS
    elif error_type == '400':
        core_card_mock.request_create.response_code = 400
    elif error_type == 'one_fail':
        core_card_mock.request_create.first_fail = True
        core_card_mock.application_status = STATUS_SUCCESS
    elif error_type == 'one_timeout':
        core_card_mock.request_create.first_timeout = True
        core_card_mock.application_status = STATUS_SUCCESS
    elif error_type == 'none_success_errors_list':
        core_card_mock.request_create.errors_list = True
        core_card_mock.application_status = STATUS_SUCCESS
    elif error_type == 'none_success_empty_errors_list':
        core_card_mock.request_create.empty_errors_list = True
        core_card_mock.application_status = STATUS_SUCCESS
    await helper.start_digital_card_stage(
        'create-digital-card-stage-id', started_shared, expected_shared,
    )
    helper.check_digital_card_calls(digital_card_create=expected_tries)


async def test_start_card_status_stq_polling_stage(
        processing, mockserver, stq,
):
    @mockserver.json_handler('/v1/card/issue')
    async def mock_core_card(request):
        data = json.loads(request.get_data())
        assert data['public_agreement_id'] == PUBLIC_AGREEMENT_ID
        assert data['card_type'] == CARD_TYPE
        return {
            'request_id': CORE_BANKING_REQUEST_ID,
            'status': STATUS_PENDING,
        }

    stq_name = 'bank_applications_digital_card_status_polling'
    with stq.flushing():
        # create_application
        await processing.bank.applications.send_event(
            item_id=APPLICATION_ID,
            payload={'kind': 'init', 'type': 'DIGITAL_CARD_ISSUE'},
            stq_queue='bank_applications_procaas',
            idempotency_token='foo',
        )

        # card_submit
        await processing.bank.applications.send_event(
            item_id=APPLICATION_ID,
            payload={
                'kind': 'update',
                'type': 'DIGITAL_CARD_ISSUE',
                'buid': BUID,
                'agreement_id': PUBLIC_AGREEMENT_ID,
                'session_uuid': SESSION_UUID,
            },
            stq_queue='bank_applications_procaas',
            already_flushing_stq=True,
        )

        assert stq[stq_name].times_called == 1
        call = stq[stq_name].next_call()
        assert call['kwargs']['buid'] == BUID
        assert call['kwargs']['session_uuid'] == SESSION_UUID
        assert call['kwargs']['request_id'] == CORE_BANKING_REQUEST_ID
        assert call['kwargs']['application_id'] == APPLICATION_ID
    assert mock_core_card.times_called == 1
