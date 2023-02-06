from tests_processing.processing.bank import common


class ProductHelper:
    def __init__(
            self,
            core_client_mock,
            applications_mock,
            userinfo_mock,
            core_current_account_mock,
            agreements_mock,
            processing,
    ):
        self.core_client_mock = core_client_mock
        self.applications_mock = applications_mock
        self.userinfo_mock = userinfo_mock
        self.core_current_account_mock = core_current_account_mock
        self.agreements_mock = agreements_mock
        self.processing = processing

        self.application_id = None
        self.core_banking_request_id = None
        self.simpl_application_id = None
        self.session_uuid = None
        self.remote_ip = None
        self.last_name = None
        self.first_name = None
        self.middle_name = None
        self.passport_number = None
        self.birthday = None
        self.inn = None
        self.buid = None
        self.yuid = None
        self.product = None
        self.client_revision = None
        self.auth_level = None
        self.agreement_version = None

    def set_values(
            self,
            remote_ip=common.IP,
            yuid=common.YUID,
            buid=common.BUID,
            core_banking_request_id=common.CORE_BANKING_REQUEST_ID,
            application_id=common.APPLICATION_ID,
            last_name=common.LAST_NAME,
            first_name=common.FIRST_NAME,
            middle_name=common.MIDDLE_NAME,
            birthday=common.BIRTHDAY,
            passport_number=common.PASSPORT_NUMBER,
            product=common.PRODUCT_PRO,
            inn=common.INN,
            session_uuid=common.SESSION_UUID,
            client_revision='1',
            auth_level=common.AUTH_LEVEL_ANONYMOUS,
            agreement_version=0,
    ):
        self.remote_ip = remote_ip
        self.yuid = yuid
        self.buid = buid
        self.core_banking_request_id = core_banking_request_id
        self.application_id = application_id
        self.product = product
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.birthday = birthday
        self.passport_number = passport_number
        self.inn = inn
        self.session_uuid = session_uuid
        self.client_revision = client_revision
        self.auth_level = auth_level
        self.agreement_version = agreement_version

    def prepare_mocks(self):
        self.core_client_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.core_client_mock.client_revision = self.client_revision
        self.core_client_mock.application_id = self.application_id
        self.core_client_mock.buid = self.buid
        self.core_client_mock.remote_ip = self.remote_ip
        self.core_client_mock.session_uuid = self.session_uuid
        self.core_client_mock.auth_level = self.auth_level

        self.applications_mock.application_id = self.application_id
        self.applications_mock.yandex_uid = self.yuid
        self.applications_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.applications_mock.simpl_application_id = self.simpl_application_id
        self.applications_mock.session_uuid = self.session_uuid
        self.applications_mock.remote_ip = self.remote_ip
        self.applications_mock.last_name = self.last_name
        self.applications_mock.first_name = self.first_name
        self.applications_mock.middle_name = self.middle_name
        self.applications_mock.passport_number = self.passport_number
        self.applications_mock.birthday = self.birthday
        self.applications_mock.inn = self.inn
        self.applications_mock.product = self.product

        self.userinfo_mock.buid = self.buid
        self.userinfo_mock.yuid = self.yuid
        self.userinfo_mock.product = self.product

        self.core_current_account_mock.buid = self.buid
        self.core_current_account_mock.session_uuid = self.session_uuid
        self.core_current_account_mock.remote_ip = self.remote_ip
        self.core_current_account_mock.core_request_id = (
            self.core_banking_request_id
        )
        self.core_current_account_mock.product = self.product
        self.core_current_account_mock.client_revision = self.client_revision

        self.agreements_mock.agreement_version = self.agreement_version

    async def send_product_event(
            self, stq_fail=False, already_flushing_stq=False,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'run',
                'type': 'PRODUCT',
                'yuid': self.yuid,
                'buid': self.buid,
                'client_ip': self.remote_ip,
                'session_uuid': self.session_uuid,
                'product': self.product,
                'agreement_version': self.agreement_version,
            },
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
            already_flushing_stq=already_flushing_stq,
        )
        assert event_id
        return event_id

    async def send_product_after_event(self, stq_fail=False):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'run',
                'type': 'product_after',
                'yuid': self.yuid,
                'buid': self.buid,
                'client_ip': self.remote_ip,
                'session_uuid': self.session_uuid,
                'product': self.product,
                'core_request_id': self.core_banking_request_id,
            },
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
        )
        assert event_id

    async def start_single_stage(
            self,
            stage_id,
            started_shared,
            expected_shared,
            pipeline='create-product-pipeline',
    ):
        shared_state = (
            await self.processing.bank.applications.handle_single_event(
                item_id=self.application_id,
                pipeline=pipeline,
                payload={
                    'type': 'PRODUCT',
                    'yuid': self.yuid,
                    'buid': self.buid,
                    'client_ip': self.remote_ip,
                    'session_uuid': self.session_uuid,
                    'product': self.product,
                },
                initial_state=started_shared,
                stage_id=stage_id,
            )
        )
        assert shared_state == expected_shared, shared_state

    def check_product_calls(
            self,
            default_value=0,
            set_current_status=None,
            accept_agreement=None,
            get_client_details=None,
            open_product=None,
            set_core_request_id=None,
    ):
        assert (
            self.applications_mock.product_set_status.handler.times_called
            == (
                set_current_status
                if set_current_status is not None
                else default_value
            )
        )
        assert (
            self.agreements_mock.accept_agreement.handler.times_called
            == accept_agreement
            if accept_agreement is not None
            else default_value
        )
        assert (
            self.core_client_mock.client_details_get.handler.times_called
            == (
                get_client_details
                if get_client_details is not None
                else default_value
            )
        )
        assert (
            self.core_current_account_mock.open_product.handler.times_called
            == (open_product if open_product is not None else default_value)
        )
        assert (
            self.applications_mock.set_core_request_id.handler.times_called
            == (
                set_core_request_id
                if set_core_request_id is not None
                else default_value
            )
        )

    def check_after_calls(
            self,
            default_value=0,
            get_agreement_id=None,
            add_product=None,
            create_card=None,
            submit_card=None,
            get_client_details=None,
            create_simplified=None,
            get_personal_data=None,
            submit_simplified=None,
    ):
        assert (
            self.core_current_account_mock.agreement_get_by_request_id.handler.times_called  # noqa
            == (
                get_agreement_id
                if get_agreement_id is not None
                else default_value
            )
        )
        assert self.userinfo_mock.add_product.handler.times_called == (
            add_product if add_product is not None else default_value
        )
        assert (
            self.applications_mock.card_internal_create_app.handler.times_called  # noqa
            == (create_card if create_card is not None else default_value)
        )
        assert (
            self.applications_mock.card_internal_submit.handler.times_called
            == (submit_card if submit_card is not None else default_value)
        )
        assert (
            self.core_client_mock.client_details_get.handler.times_called
            == (
                get_client_details
                if get_client_details is not None
                else default_value
            )
        )
        assert (
            self.applications_mock.simplified_internal_create_app.handler.times_called  # noqa
            == (
                create_simplified
                if create_simplified is not None
                else default_value
            )
        )
        assert (
            self.applications_mock.reg_get_personal_data.handler.times_called
            == (
                get_personal_data
                if get_personal_data is not None
                else default_value
            )
        )
        assert (
            self.applications_mock.simplified_internal_submit_app.handler.times_called  # noqa
            == (
                submit_simplified
                if submit_simplified is not None
                else default_value
            )
        )
