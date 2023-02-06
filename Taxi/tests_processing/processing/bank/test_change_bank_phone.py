import pytest
from tests_processing.processing.bank import common

AF_INFO = {'device_id': 'some_device_id'}

PHONE_1 = '+71234567111'

PHONE_2 = '+71234567112'

BUID_STATUS = 'CHANGING_PHONE'
CORE_BANKING_REQUEST_ID = 'aa1234'
NEW_PHONE_ID = 'phone_id_112'
OLD_PHONE_ID = 'phone_id_111'
NO_YUID = None
NEW_PHONE_NUMBER = PHONE_2
OLD_PHONE_NUMBER = PHONE_1


class ChangePhoneHelper:
    def __init__(
            self,
            passport_mock,
            core_client_mock,
            userinfo_mock,
            applications_mock,
            processing_mock,
            risk_mock,
            processing,
    ):
        self.passport_mock = passport_mock
        self.core_client_mock = core_client_mock
        self.userinfo_mock = userinfo_mock
        self.applications_mock = applications_mock
        self.processing_mock = processing_mock
        self.risk_mock = risk_mock
        self.processing = processing
        self.ip_address = common.IP
        self.yuid = None
        self.buid = None
        self.buid_status = None
        self.phone_number = None
        self.new_phone_id = None
        self.old_phone_id = None
        self.core_banking_request_id = None
        self.core_banking_status = None
        self.application_id = None
        self.session_uuid = None
        self.old_phone_number = None
        self.application_status = None
        self.mocks = {
            'phone_check': self.risk_mock.phone_check,
            'get_info_by_phone': self.userinfo_mock.get_info_by_phone,
            'update_buid_status': self.userinfo_mock.update_buid_status,
            'get_phone_number': self.userinfo_mock.get_phone_number,
            'bind_phone': self.passport_mock.bind_phone,
            'set_bank_phone': self.userinfo_mock.set_bank_phone,
            'phone_update': self.core_client_mock.phone_update,
        }

    def set_values(
            self,
            ip_address=common.IP,
            yuid=common.YUID,
            buid=common.BUID,
            phone_number=NEW_PHONE_NUMBER,
            core_banking_request_id=CORE_BANKING_REQUEST_ID,
            application_id=common.APPLICATION_ID,
            session_uuid=common.SESSION_UUID,
            buid_status=BUID_STATUS,
            old_phone_number=OLD_PHONE_NUMBER,
            application_status=common.STATUS_PENDING,
            new_phone_id=NEW_PHONE_ID,
            old_phone_id=OLD_PHONE_ID,
            core_banking_status=None,
    ):
        self.ip_address = ip_address
        self.yuid = yuid
        self.buid = buid
        self.buid_status = buid_status
        self.phone_number = phone_number
        self.core_banking_request_id = core_banking_request_id
        self.new_phone_id = new_phone_id
        self.old_phone_id = old_phone_id
        self.core_banking_status = core_banking_status
        self.application_id = application_id
        self.session_uuid = session_uuid
        self.old_phone_number = old_phone_number
        self.application_status = application_status

    def prepare_mocks(self):
        self.passport_mock.ip_address = self.ip_address
        self.passport_mock.yuid = self.yuid
        self.passport_mock.phone_number = self.phone_number
        self.passport_mock.old_phone_number = self.old_phone_number
        self.core_client_mock.phone_number = self.phone_number
        self.core_client_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.core_client_mock.application_id = self.application_id
        self.core_client_mock.application_status = self.application_status
        self.userinfo_mock.buid = self.buid
        self.userinfo_mock.yuid = self.yuid
        self.userinfo_mock.phone_number = self.phone_number
        self.userinfo_mock.buid_status = self.buid_status
        self.applications_mock.remote_ip = self.ip_address
        self.applications_mock.session_uuid = self.session_uuid
        self.applications_mock.application_id = self.application_id
        self.applications_mock.phone_number = self.phone_number
        self.applications_mock.session_uuid = self.session_uuid
        self.applications_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.processing_mock.buid = self.buid
        self.processing_mock.application_id = self.application_id
        self.processing_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.risk_mock.phone_number = self.phone_number
        self.risk_mock.application_id = self.application_id

    async def create_change_phone_application(
            self, pipeline_type='CHANGE_NUMBER',
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={'kind': 'init', 'type': pipeline_type},
            stq_queue='bank_applications_procaas',
        )
        assert event_id

    async def send_change_phone_event(
            self,
            falling=False,
            already_flushing_stq=False,
            pipeline_type='CHANGE_NUMBER',
    ):
        payload_data = {
            'kind': 'update',
            'type': pipeline_type,
            'buid': self.buid,
            'yuid': self.yuid,
            'client_ip': self.ip_address,
            'session_uuid': self.session_uuid,
            'new_phone_id': self.new_phone_id,
            'old_phone_id': self.old_phone_id,
            'core_banking_status': self.core_banking_status,
            'core_banking_request_id': self.core_banking_request_id,
        }
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload=payload_data,
            stq_queue='bank_applications_procaas',
            expect_fail=falling,
            already_flushing_stq=already_flushing_stq,
        )
        assert event_id
        return event_id

    async def start_single_stage(
            self,
            stage_id,
            started_shared,
            expected_shared,
            pipeline='change-bank-phone-pipeline',
            payload=None,
    ):
        if payload is None:
            payload = {
                'buid': self.buid,
                'client_ip': self.ip_address,
                'new_phone_id': self.new_phone_id,
            }
        shared_state = (
            await self.processing.bank.applications.handle_single_event(
                item_id=self.application_id,
                pipeline=pipeline,
                payload=payload,
                initial_state=started_shared,
                stage_id=stage_id,
            )
        )
        assert shared_state == expected_shared, shared_state

    def check_stage_calls(
            self,
            default_value=0,
            phone_check=None,
            get_info_by_phone=None,
            update_buid_status=None,
            bind_phone=None,
            get_phone_number=None,
            set_bank_phone=None,
            phone_update=None,
            create_event=0,
            **kwargs,
    ):
        assert self.risk_mock.phone_check.handler.times_called == (
            phone_check if phone_check is not None else default_value
        )
        assert self.userinfo_mock.get_info_by_phone.handler.times_called == (
            get_info_by_phone
            if get_info_by_phone is not None
            else default_value
        )
        assert self.userinfo_mock.set_bank_phone.handler.times_called == (
            set_bank_phone if set_bank_phone is not None else default_value
        )
        assert self.userinfo_mock.update_buid_status.handler.times_called == (
            update_buid_status
            if update_buid_status is not None
            else default_value
        )
        assert self.userinfo_mock.get_phone_number.handler.times_called == (
            get_phone_number if get_phone_number is not None else default_value
        )
        assert self.passport_mock.bind_phone.handler.times_called == (
            bind_phone if bind_phone is not None else default_value
        )
        assert self.core_client_mock.phone_update.handler.times_called == (
            phone_update if phone_update is not None else default_value
        )

        assert (
            self.processing_mock.create_event.handler.times_called
            == create_event
        )


async def test_change_bank_phone_check_full_pipelines(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
):
    helper = ChangePhoneHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values()
    await helper.create_change_phone_application()
    helper.prepare_mocks()
    event_id = await helper.send_change_phone_event(falling=False)
    assert event_id
    helper.check_stage_calls(default_value=1, set_bank_phone=0, bind_phone=2)


@pytest.mark.parametrize(
    'falled_stage, kwargs',
    [
        (
            'update_buid_status',
            {
                'default_value': 0,
                'phone_check': 1,
                'get_info_by_phone': 1,
                'update_buid_status': 2,
                'get_phone_number': 1,
            },
        ),
        ('get_phone_number', {'default_value': 0, 'get_phone_number': 2}),
        (
            'bind_phone',
            {
                'default_value': 1,
                'phone_update': 0,
                'set_bank_phone': 0,
                'bind_phone': 2,
            },
        ),
    ],
)
async def test_change_bank_phone_check_problems_turn_stages(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        falled_stage,
        kwargs,
):
    helper = ChangePhoneHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values()
    await helper.create_change_phone_application()
    helper.prepare_mocks()
    helper.mocks[falled_stage].response_code = 500
    event_id = await helper.send_change_phone_event(falling=True)
    assert event_id
    helper.check_stage_calls(**kwargs)


@pytest.mark.parametrize(
    'dif_phone_id,dif_phone_number, bank_phone_changing_status',
    [
        (NEW_PHONE_ID, NEW_PHONE_NUMBER, 'TASK_POLLING_IN_CORE_CLIENT'),
        (OLD_PHONE_ID, OLD_PHONE_NUMBER, 'NEW_PHONE_OCCUPIED'),
    ],
)
async def test_change_bank_phone_general_pipeline_1_data_flow(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        dif_phone_id,
        dif_phone_number,
        bank_phone_changing_status,
):
    helper = ChangePhoneHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(new_phone_id=dif_phone_id, phone_number=dif_phone_number)
    await helper.create_change_phone_application()
    helper.prepare_mocks()

    shared_state = await processing.bank.applications.handle_single_event(
        item_id='123456789abcdefgh',
        pipeline='change-bank-phone-pipeline',
        payload={
            'new_phone_id': dif_phone_id,
            'buid': common.BUID,
            'bank_phone_changing_status': 'INIT',
            'client_ip': common.IP,
        },
    )
    assert (
        shared_state['bank_phone_changing_status']
        == bank_phone_changing_status
    )


@pytest.mark.parametrize(
    'stage_id, started_shared,expected_shared',
    [
        (
            'get-new-number-by-phone-id-stage-id',
            {},
            {
                'bank_phone_changing_status': 'GOT_NEW_NUMBER',
                'new_bank_phone': PHONE_2,
            },
        ),
        (
            'check-bank-phone-stage-id',
            {'new_bank_phone': PHONE_2},
            {
                'new_bank_phone': PHONE_2,
                'bank_phone_changing_status': 'NEW_PHONE_CHECKED',
                'errors': None,
                'is_error': False,
            },
        ),
        (
            'set-buid-status-stage-id',
            {
                'bank_phone_changing_status': 'NEW_PHONE_CHECKED',
                'errors': None,
                'is_error': False,
                'buid_status': 'CHANGING_PHONE',
            },
            {
                'bank_phone_changing_status': 'BUID_STATUS_CHANGED',
                'buid_status': 'CHANGING_PHONE',
                'errors': None,
                'is_error': False,
            },
        ),
        (
            'get-old-number-stage-id',
            {
                'bank_phone_changing_status': 'BUID_STATUS_CHANGED',
                'is_error': False,
            },
            {
                'bank_phone_changing_status': 'GOT_OLD_NUMBER',
                'is_error': False,
                'old_bank_phone': PHONE_1,
            },
        ),
        (
            'remove-bank-mark-from-old-phone-stage-id',
            {
                'bank_phone_changing_status': 'GOT_OLD_NUMBER',
                'errors': None,
                'is_error': False,
                'old_bank_phone': PHONE_1,
                'yuid': '8421',
            },
            {
                'bank_phone_changing_status': 'BANK_MARK_REMOVED',
                'errors': None,
                'is_error': False,
                'old_bank_phone': PHONE_1,
                'yuid': '8421',
            },
        ),
        (
            'bank-risk-phone-check-stage-id',
            {'new_bank_phone': PHONE_2},
            {'new_bank_phone': PHONE_2, 'errors': None, 'is_error': False},
        ),
        (
            'bind-phone-stage-id',
            {
                'bank_phone_changing_status': 'BANK_MARK_REMOVED',
                'errors': None,
                'is_error': False,
                'old_bank_phone': PHONE_1,
                'yuid': '8421',
                'new_bank_phone': PHONE_2,
            },
            {
                'bank_phone_changing_status': 'NEW_BANK_PHONE_MARKED',
                'errors': None,
                'is_error': False,
                'old_bank_phone': PHONE_1,
                'yuid': '8421',
                'new_bank_phone': PHONE_2,
            },
        ),
        (
            'start-change-number-core-stage-id',
            {
                'bank_phone_changing_status': 'NEW_BANK_PHONE_MARKED',
                'errors': None,
                'is_error': False,
                'old_bank_phone': PHONE_1,
                'yuid': '8421',
                'new_bank_phone': PHONE_2,
            },
            {
                'bank_phone_changing_status': (
                    'SET_NEW_PHONE_STARTED_IN_CORE_CLIENT'
                ),
                'core_banking_status': 'PENDING',
                'errors': None,
                'is_error': False,
                'old_bank_phone': PHONE_1,
                'core_banking_request_id': 'aa1234',
                'yuid': '8421',
                'new_bank_phone': PHONE_2,
            },
        ),
    ],
)
async def test_change_bank_phone_general_pipeline_1_single_stages(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        stage_id,
        started_shared,
        expected_shared,
):
    helper = ChangePhoneHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values()
    await helper.create_change_phone_application()
    helper.prepare_mocks()

    await helper.start_single_stage(
        stage_id=stage_id,
        started_shared=started_shared,
        expected_shared=expected_shared,
    )


async def test_change_bank_phone_general_pipeline_1_all_stages(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
):
    helper = ChangePhoneHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values()
    await helper.create_change_phone_application()
    helper.prepare_mocks()

    shared_state = await processing.bank.applications.handle_single_event(
        item_id='123456789abcdefgh',
        pipeline='change-bank-phone-pipeline',
        payload={
            'new_phone_id': NEW_PHONE_ID,
            'buid': common.BUID,
            'bank_phone_changing_status': 'INIT',
            'client_ip': common.IP,
        },
    )
    token = shared_state['idempotency_token']
    assert shared_state == {
        'new_bank_phone': PHONE_2,
        'antifraud_info': AF_INFO,
        'old_bank_phone': PHONE_1,
        'bank_phone_changing_status': 'TASK_POLLING_IN_CORE_CLIENT',
        'buid_status': 'CHANGING_PHONE',
        'core_banking_status': 'PENDING',
        'errors': None,
        'is_error': False,
        'idempotency_token': token,
        'core_banking_request_id': 'aa1234',
        'yuid': common.YUID,
    }


async def test_change_bank_phone_general_pipeline_bad_number(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
):
    helper = ChangePhoneHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(phone_number='BAD_NUMBER')
    await helper.create_change_phone_application()
    helper.prepare_mocks()
    risk_mock.phone_check.access_deny = True

    shared_state = await processing.bank.applications.handle_single_event(
        item_id='123456789abcdefgh',
        pipeline='change-bank-phone-pipeline',
        payload={
            'new_phone_id': 'BAD_PHONE_ID',
            'buid': common.BUID,
            'bank_phone_changing_status': 'INIT',
            'client_ip': common.IP,
        },
    )
    token = shared_state['idempotency_token']
    assert shared_state == {
        'new_bank_phone': 'BAD_NUMBER',
        'antifraud_info': AF_INFO,
        'old_bank_phone': PHONE_1,
        'bank_phone_changing_status': 'GOT_OLD_NUMBER',
        'buid_status': 'CHANGING_PHONE',
        'errors': [
            '10.00.99:Phone analyzer: '
            'Failed Russian phone number verification',
        ],
        'idempotency_token': token,
        'is_error': True,
        'yuid': common.YUID,
    }


@pytest.mark.parametrize(
    'old_phone_number, new_phone_number, new_phone_id, old_phone_id, pipeline_type, kwargs',
    [
        (
            OLD_PHONE_NUMBER,
            NEW_PHONE_NUMBER,
            NEW_PHONE_ID,
            OLD_PHONE_ID,
            'change_number_result',
            {'default_value': 0, 'set_bank_phone': 1, 'update_buid_status': 1},
        ),
        (
            NEW_PHONE_NUMBER,
            OLD_PHONE_NUMBER,
            OLD_PHONE_ID,
            NEW_PHONE_ID,
            'change_number_failed',
            {'default_value': 0, 'update_buid_status': 1, 'bind_phone': 2},
        ),
    ],
)
async def test_change_bank_phone_final_pipeline(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        pipeline_type,
        new_phone_number,
        old_phone_number,
        kwargs,
        new_phone_id,
        old_phone_id,
):
    helper = ChangePhoneHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        new_phone_id=new_phone_id,
        old_phone_id=old_phone_id,
        phone_number=new_phone_number,
        old_phone_number=old_phone_number,
        core_banking_status=common.STATUS_SUCCESS,
        buid_status=common.FINAL_BUID_STATUS,
    )
    await helper.create_change_phone_application(pipeline_type=pipeline_type)
    helper.prepare_mocks()
    event_id = await helper.send_change_phone_event(
        pipeline_type=pipeline_type, falling=False,
    )
    assert event_id
    helper.check_stage_calls(**kwargs)


@pytest.mark.parametrize(
    'pipeline_type, pipeline, stage_id, started_shared, expected_shared',
    [
        (
            'change_number_result',
            'change-bank-phone-final-pipeline',
            'set-bank-phone-stage-id',
            {'new_bank_phone': PHONE_1},
            {'new_bank_phone': PHONE_1, 'errors': None, 'is_error': False},
        ),
        (
            'change_number_result',
            'change-bank-phone-final-pipeline',
            'set-buid-status-stage-id',
            {
                'new_bank_phone': PHONE_2,
                'bank_phone_changing_status': 'FINAL_CHANGING_PHONE',
                'buid_status': 'FINAL',
            },
            {
                'new_bank_phone': PHONE_2,
                'bank_phone_changing_status': 'BUID_STATUS_CHANGED',
                'buid_status': 'FINAL',
            },
        ),
        (
            'change_number_failed',
            'change-bank-phone-failed-pipeline',
            'set-buid-status-stage-id',
            {
                'old_bank_phone': PHONE_2,
                'bank_phone_changing_status': 'FAILED_CHANGING_PHONE',
                'buid_status': 'FINAL',
            },
            {
                'old_bank_phone': PHONE_2,
                'bank_phone_changing_status': 'BUID_STATUS_CHANGED',
                'buid_status': 'FINAL',
            },
        ),
    ],
)
async def test_change_bank_phone_general_pipeline_2_final_single_stages(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        stage_id,
        started_shared,
        expected_shared,
        pipeline_type,
        pipeline,
):
    helper = ChangePhoneHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        risk_mock,
        processing,
    )
    helper.set_values(
        new_phone_id=NEW_PHONE_ID,
        buid_status=common.FINAL_BUID_STATUS,
        phone_number=OLD_PHONE_NUMBER,
        old_phone_number=NEW_PHONE_NUMBER,
        core_banking_status=common.STATUS_SUCCESS,
    )
    await helper.create_change_phone_application(pipeline_type=pipeline_type)
    helper.prepare_mocks()

    await helper.start_single_stage(
        stage_id=stage_id,
        started_shared=started_shared,
        expected_shared=expected_shared,
        pipeline=pipeline,
        payload={
            'buid': common.BUID,
            'client_ip': common.IP,
            'new_phone_id': NEW_PHONE_ID,
            'core_banking_status': common.STATUS_SUCCESS,
            'core_banking_request_id': common.CORE_BANKING_REQUEST_ID,
        },
    )
