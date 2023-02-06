import pytest
from tests_processing.processing.bank import common


SET_APPLICATIONS_PROCESSING = [
    common.STATUS_PROCESSING,
    common.STATUS_CORE_BANKING,
    common.STATUS_SUCCESS,
]

SUCCESS_DEFAULTS_GROUPS_LIST = [
    'test_simplified_identification_esia_status_processing',
    'test_simplified_identification_esia_status_success',
]


class SimplifiedIdentificationEsiaHelper:
    def __init__(
            self,
            core_client_mock,
            applications_mock,
            processing_mock,
            notifications_mock,
            core_current_account_mock,
            processing,
    ):
        self.core_client_mock = core_client_mock
        self.applications_mock = applications_mock
        self.processing_mock = processing_mock
        self.notifications_mock = notifications_mock
        self.processing = processing
        self.core_current_account_mock = core_current_account_mock

        self.ip_address = None
        self.yuid = None
        self.buid = None
        self.redirect_url = None
        self.core_banking_request_id = None
        self.application_id = None
        self.application_status = None
        self.set_application_status = None

        self.remote_ip = None
        self.session_uuid = None
        self.consumer = None
        self.processing_notification_events = None
        self.defaults_groups = None
        self.agreement_title = None
        self.agreement_version = None
        self.core_banking_status = None
        self.core_banking_is_error = None
        self.esia_auth_code = None
        self.data_revision = None

    def set_values(
            self,
            ip_address=common.IP,
            yuid=common.YUID,
            buid=common.BUID,
            core_banking_request_id=common.CORE_BANKING_REQUEST_ID,
            application_id=common.APPLICATION_ID,
            application_status=common.STATUS_SUCCESS,
            core_banking_status=common.STATUS_SUCCESS,
            core_banking_is_error=False,
            remote_ip=common.IP,
            session_uuid=common.SESSION_UUID,
            consumer=common.CONSUMER,
            processing_notification_events=None,
            defaults_groups=None,
            set_application_status=None,
            esia_auth_code=common.DEFAULT_ESIA_AUTH_CODE,
            redirect_url=common.DEFAULT_ESIA_REDIRECT_URL,
            data_revision=common.DEFAULT_DATA_REVISION,
    ):
        if defaults_groups is None:
            defaults_groups = SUCCESS_DEFAULTS_GROUPS_LIST
        if set_application_status is None:
            set_application_status = SET_APPLICATIONS_PROCESSING
        self.ip_address = ip_address
        self.yuid = yuid
        self.buid = buid
        self.redirect_url = redirect_url
        self.core_banking_request_id = core_banking_request_id
        self.application_id = application_id
        self.application_status = application_status
        self.core_banking_status = core_banking_status
        self.set_application_status = set_application_status
        self.core_banking_is_error = core_banking_is_error
        self.remote_ip = remote_ip
        self.session_uuid = session_uuid
        self.consumer = consumer
        self.processing_notification_events = processing_notification_events
        self.defaults_groups = defaults_groups
        self.esia_auth_code = esia_auth_code
        self.data_revision = data_revision

    def prepare_mocks(self):
        # prepare core-client
        self.core_client_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.core_client_mock.application_id = self.application_id
        self.core_client_mock.core_banking_status = self.core_banking_status
        self.core_client_mock.is_error = self.core_banking_is_error

        # prepare bank-apps
        self.applications_mock.buid = self.buid
        self.applications_mock.application_id = self.application_id
        self.applications_mock.status = self.application_status
        self.applications_mock.set_application_status = (
            self.set_application_status
        )
        self.applications_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.applications_mock.remote_ip = self.remote_ip
        self.applications_mock.session_uuid = self.session_uuid

        # prepare processing
        self.processing_mock.buid = self.buid
        self.processing_mock.application_id = self.application_id
        self.processing_mock.core_banking_request_id = (
            self.core_banking_request_id
        )

        # preapre notifications
        self.notifications_mock.consumer = self.consumer
        self.notifications_mock.processing_notification_events = (
            self.processing_notification_events
        )
        self.notifications_mock.buid = self.buid
        self.notifications_mock.defaults_groups = self.defaults_groups

        # prepare core_current_account_mock
        self.core_current_account_mock.core_request_id = (
            self.core_banking_request_id
        )
        self.core_current_account_mock.application_status = (
            self.core_banking_status
        )

    async def create_simplified_esia_app(self):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'init',
                'type': 'SIMPLIFIED_IDENTIFICATION_ESIA',
                'auth_code': self.esia_auth_code,
            },
            stq_queue='bank_applications_procaas',
        )
        assert event_id

    async def send_simplified_esia_event(
            self, stq_fail=False, already_flushing_stq=False,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': 'SIMPLIFIED_IDENTIFICATION_ESIA',
                'buid': self.buid,
                'remote_ip': self.ip_address,
                'session_id': self.session_uuid,
                'auth_code': self.esia_auth_code,
                'redirect_url': self.redirect_url,
            },
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
            already_flushing_stq=already_flushing_stq,
        )
        assert event_id
        return event_id

    async def send_core_account_check_event(
            self, stq_fail=False, already_flushing_stq=False,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': (
                    'simplified_identification_esia_client_account_check_start'
                ),
                'buid': self.buid,
                'remote_ip': self.ip_address,
                'session_id': self.session_uuid,
                'data_revision': self.data_revision,
            },
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
            already_flushing_stq=already_flushing_stq,
        )
        assert event_id
        return event_id

    async def send_finish_event(
            self, stq_fail=False, already_flushing_stq=False,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': 'simplified_identification_esia_finish',
                'buid': self.buid,
                'application_status': self.application_status,
            },
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
            already_flushing_stq=already_flushing_stq,
        )
        assert event_id
        return event_id

    def check_simplified_esia_calls(
            self,
            default_value=0,
            core_client_calls=None,
            core_current_account_calls=None,
            notifications_sended=None,
    ):
        assert (
            self.notifications_mock.send_notification.handler.times_called
            == (
                notifications_sended
                if notifications_sended is not None
                else default_value
            )
        )
        assert self.core_client_mock.esia_put.handler.times_called == (
            core_client_calls
            if core_client_calls is not None
            else default_value
        )
        assert (
            self.core_current_account_mock.request_upgrade.handler.times_called
            == (
                core_current_account_calls
                if core_current_account_calls is not None
                else default_value
            )
        )

    def check_application_status_calls(
            self,
            default_value=0,
            esia_set_status=None,
            create_event=1,
            set_status=0,
    ):
        assert (
            self.applications_mock.simplified_esia_set_status.handler.times_called  # noqa
            == (
                esia_set_status
                if esia_set_status is not None
                else default_value
            )
        )
        assert self.applications_mock.set_status.handler.times_called == (
            set_status if set_status is not None else default_value
        )
        assert (
            self.processing_mock.create_event.handler.times_called
            == create_event
        ), self.processing_mock.create_event.handler.times_called


async def test_bank_applications_processing_finish_event(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values(
        defaults_groups=['test_simplified_identification_esia_status_success'],
    )
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    await helper.send_finish_event()
    helper.check_application_status_calls(create_event=0)
    helper.check_simplified_esia_calls(notifications_sended=1)


async def test_bank_applications_processing_simpl_esia_ok(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    await helper.send_simplified_esia_event()
    helper.check_application_status_calls(esia_set_status=2, create_event=0)
    helper.check_simplified_esia_calls(
        core_client_calls=1, notifications_sended=1,
    )


@pytest.mark.config(
    BANK_APPLICATIONS_SET_CORE_BANKING_STATUS_SIMPLIFIED_IDENTIFICATION_ESIA_ENABLED=False,  # noqa
)
async def test_bank_applications_processing_no_set_core_banking_status(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    await helper.send_simplified_esia_event()
    helper.check_application_status_calls(esia_set_status=1, create_event=0)
    helper.check_simplified_esia_calls(
        core_client_calls=1, notifications_sended=1,
    )


@pytest.mark.parametrize(
    'error_code, expected_tries', [(400, 1), (409, 1), (500, 3)],
)
async def test_bank_applications_processing_put_bad_response(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        error_code,
        expected_tries,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    core_client_mock.esia_put.response_code = error_code
    await helper.send_simplified_esia_event(stq_fail=True)
    helper.check_application_status_calls(esia_set_status=1, create_event=0)
    helper.check_simplified_esia_calls(
        core_client_calls=expected_tries, notifications_sended=1,
    )


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_applications_processing_put_first_fail(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        error_type,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    if error_type == '500':
        core_client_mock.esia_put.first_fail = True
    elif error_type == 'timeout':
        core_client_mock.esia_put.first_timeout = True
    await helper.send_simplified_esia_event()
    helper.check_application_status_calls(esia_set_status=2, create_event=0)
    helper.check_simplified_esia_calls(
        core_client_calls=1, notifications_sended=1,
    )


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_applications_processing_upgrade_first_fail(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        error_type,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    if error_type == '500':
        core_current_account_mock.request_upgrade.first_fail = True
    elif error_type == 'timeout':
        core_current_account_mock.request_upgrade.first_timeout = True
    await helper.send_core_account_check_event()
    helper.check_application_status_calls(create_event=0)
    helper.check_simplified_esia_calls(core_current_account_calls=2)


@pytest.mark.parametrize(
    'error_code, expected_tries', [(400, 1), (409, 1), (500, 3)],
)
async def test_bank_applications_processing_upgrade_bad_response(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        error_code,
        expected_tries,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    core_current_account_mock.request_upgrade.response_code = error_code
    await helper.send_core_account_check_event(stq_fail=True)
    helper.check_application_status_calls(create_event=0)
    helper.check_simplified_esia_calls(
        core_current_account_calls=expected_tries,
    )


@pytest.mark.parametrize('error_type', ['500', 'timeout'])
async def test_bank_applications_processing_set_app_status_first_fail(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        error_type,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    if error_type == '500':
        applications_mock.simplified_esia_set_status.first_fail = True
    elif error_type == 'timeout':
        applications_mock.simplified_esia_set_status.first_timeout = True
    await helper.send_simplified_esia_event()
    helper.check_application_status_calls(esia_set_status=3, create_event=0)
    helper.check_simplified_esia_calls(
        core_client_calls=1, notifications_sended=1,
    )


@pytest.mark.parametrize(
    'error_code, expected_tries', [(400, 1), (409, 1), (500, 3)],
)
async def test_bank_applications_processing_set_app_status_bad_response(
        processing,
        mockserver,
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        error_code,
        expected_tries,
):
    helper = SimplifiedIdentificationEsiaHelper(
        core_client_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        core_current_account_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simplified_esia_app()
    helper.prepare_mocks()
    applications_mock.simplified_esia_set_status.response_code = error_code
    await helper.send_simplified_esia_event(stq_fail=True)
    helper.check_application_status_calls(
        esia_set_status=expected_tries, create_event=0,
    )
    helper.check_simplified_esia_calls()


async def test_start_simpl_esia_ensure_stq_polling_stage(
        processing,
        mockserver,
        stq,
        processing_mock,
        core_client_mock,
        applications_mock,
        notifications_mock,
        core_current_account_mock,
):
    stq_name = (
        'bank_applications_simplified_identification_esia_status_polling'
    )
    with stq.flushing():
        helper = SimplifiedIdentificationEsiaHelper(
            core_client_mock,
            applications_mock,
            processing_mock,
            notifications_mock,
            core_current_account_mock,
            processing,
        )
        helper.set_values()
        await helper.create_simplified_esia_app()
        helper.prepare_mocks()
        event_id = await helper.send_simplified_esia_event(
            already_flushing_stq=True,
        )

        assert stq[stq_name].times_called == 1
        call = stq[stq_name].next_call()
        assert call['id'] == f'bank_applications_{common.APPLICATION_ID}'
        assert call['kwargs']['buid'] == common.BUID
        assert call['kwargs']['idempotency_token'] == event_id
        assert call['kwargs']['application_id'] == common.APPLICATION_ID
        assert call['kwargs']['ip_address'] == common.IP
        assert call['kwargs']['session_id'] == common.SESSION_UUID
        assert call['kwargs']['data_revision'] is not None
        helper.check_simplified_esia_calls(
            core_client_calls=1,
            core_current_account_calls=0,
            notifications_sended=1,
        )


async def test_start_simpl_esia_core_account_stq_polling_stage(
        processing,
        mockserver,
        stq,
        processing_mock,
        core_client_mock,
        applications_mock,
        notifications_mock,
        core_current_account_mock,
):
    stq_name = (
        'bank_applications_simplified_identification_account_check_polling'
    )
    with stq.flushing():
        helper = SimplifiedIdentificationEsiaHelper(
            core_client_mock,
            applications_mock,
            processing_mock,
            notifications_mock,
            core_current_account_mock,
            processing,
        )
        helper.set_values()
        await helper.create_simplified_esia_app()
        helper.prepare_mocks()
        event_id = await helper.send_core_account_check_event(
            already_flushing_stq=True,
        )

        assert stq[stq_name].times_called == 1
        call = stq[stq_name].next_call()
        assert call['id'] == f'bank_applications_{common.APPLICATION_ID}'
        assert call['kwargs']['buid'] == common.BUID
        assert call['kwargs']['idempotency_token'] == event_id
        assert call['kwargs']['application_id'] == common.APPLICATION_ID
        assert call['kwargs']['session_id'] == common.SESSION_UUID
        assert call['kwargs']['request_id'] == common.CORE_BANKING_REQUEST_ID

        helper.check_simplified_esia_calls(core_current_account_calls=1)
