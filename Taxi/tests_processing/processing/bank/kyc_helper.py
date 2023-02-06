from tests_processing.processing.bank import common


class KycHelper:
    def __init__(
            self,
            core_client_mock,
            applications_mock,
            processing_mock,
            notifications_mock,
            agreement_mock,
            processing,
    ):
        self.core_client_mock = core_client_mock
        self.applications_mock = applications_mock
        self.processing_mock = processing_mock
        self.notifications_mock = notifications_mock
        self.agreement_mock = agreement_mock
        self.processing = processing
        self.ip_address = None
        self.yuid = None
        self.buid = None
        self.phone_number = None
        self.core_banking_request_id = None
        self.application_id = None
        self.application_status = None
        self.set_application_status = None

        self.last_name = None
        self.first_name = None
        self.middle_name = None
        self.birthday = None
        self.id_doc_type = None
        self.passport_number = None
        self.core_banking_status = None
        self.core_banking_is_error = None
        self.inn = None
        self.snils = None
        self.inn_or_snils = None

        self.remote_ip = None
        self.session_uuid = None
        self.consumer = None
        self.processing_notification_events = None
        self.defaults_groups = None
        self.agreement_title = None
        self.agreement_version = None

        # kyc form fields
        self.sex = None
        self.birth_place_info = None
        self.id_doc_issued = None
        self.id_doc_issued_by = None
        self.id_doc_department_code = None
        self.address_registration = None
        self.address_actual = None

    def set_values(
            self,
            ip_address=common.IP,
            yuid=common.YUID,
            buid=common.BUID,
            phone_number=common.PHONE_NUMBER,
            core_banking_request_id=common.CORE_BANKING_REQUEST_ID,
            application_id=common.APPLICATION_ID,
            last_name=common.LAST_NAME,
            first_name=common.FIRST_NAME,
            middle_name=common.MIDDLE_NAME,
            birthday=common.BIRTHDAY,
            id_doc_type=common.ID_DOC_TYPE,
            passport_number=common.PASSPORT_NUMBER,
            application_status=common.STATUS_SUCCESS,
            core_banking_status=common.STATUS_SUCCESS,
            core_banking_is_error=False,
            inn=common.INN,
            snils=common.SNILS,
            inn_or_snils=common.INN,
            remote_ip=common.IP,
            session_uuid=common.SESSION_UUID,
            consumer=common.CONSUMER,
            processing_notification_events=None,
            defaults_groups=None,
            set_application_status=None,
            agreement_title=common.KYC_AGREEMENT_TITLE,
            agreement_version=common.AGREEMENT_VERSION,
            sex=common.SEX,
            birth_place_info=common.BIRTH_PLACE_INFO,
            id_doc_issued=common.ID_DOC_ISSUED,
            id_doc_issued_by=common.ID_DOC_ISSUED_BY,
            id_doc_department_code=common.ID_DOC_DEPARTAMENT_CODE,
            address_registration=common.ADDRESS_REGISTRATION,
            address_actual=common.ADDRESS_REGISTRATION,
    ):
        if defaults_groups is None:
            defaults_groups = common.SUCCESS_DEFAULTS_GROUPS_LIST
        if set_application_status is None:
            set_application_status = common.SET_APPLICATIONS_PROCESSING
        self.ip_address = ip_address
        self.yuid = yuid
        self.buid = buid
        self.phone_number = phone_number
        self.core_banking_request_id = core_banking_request_id
        self.application_id = application_id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.birthday = birthday
        self.id_doc_type = id_doc_type
        self.passport_number = passport_number
        self.application_status = application_status
        self.core_banking_status = core_banking_status
        self.set_application_status = set_application_status
        self.core_banking_is_error = core_banking_is_error
        self.inn = inn
        self.snils = snils
        self.inn_or_snils = inn_or_snils
        self.remote_ip = remote_ip
        self.session_uuid = session_uuid
        self.consumer = consumer
        self.processing_notification_events = processing_notification_events
        self.defaults_groups = defaults_groups
        self.agreement_title = agreement_title
        self.agreement_version = agreement_version
        self.sex = sex
        self.birth_place_info = birth_place_info
        self.id_doc_issued = id_doc_issued
        self.id_doc_issued_by = id_doc_issued_by
        self.id_doc_department_code = id_doc_department_code
        self.address_registration = address_registration
        self.address_actual = address_actual

    def prepare_mocks(self):
        self.core_client_mock.phone_number = self.phone_number
        self.core_client_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.core_client_mock.application_id = self.application_id
        self.core_client_mock.last_name = self.last_name
        self.core_client_mock.first_name = self.first_name
        self.core_client_mock.patronymic = self.middle_name
        self.core_client_mock.birth_date = self.birthday
        self.core_client_mock.id_doc_number = self.passport_number
        self.core_client_mock.core_banking_status = self.core_banking_status
        self.core_client_mock.is_error = self.core_banking_is_error
        self.core_client_mock.inn = self.inn
        self.core_client_mock.snils = self.snils

        # kyc form fields
        self.core_client_mock.sex = self.sex
        self.core_client_mock.birth_place_info = self.birth_place_info
        self.core_client_mock.id_doc_issued = self.id_doc_issued
        self.core_client_mock.id_doc_issued_by = self.id_doc_issued_by
        self.core_client_mock.id_doc_department_code = (
            self.id_doc_department_code
        )
        self.core_client_mock.address_registration = self.address_registration
        self.core_client_mock.address_actual = self.address_actual

        self.applications_mock.application_id = self.application_id
        self.applications_mock.application_status = self.application_status
        self.applications_mock.set_application_status = (
            self.set_application_status
        )
        self.applications_mock.phone_number = self.phone_number
        self.applications_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.applications_mock.middle_name = self.middle_name
        self.applications_mock.set_status_iterator = 1
        self.applications_mock.last_name = self.last_name
        self.applications_mock.first_name = self.first_name
        self.applications_mock.birthday = self.birthday
        self.applications_mock.passport_number = self.passport_number
        self.applications_mock.inn = self.inn
        self.applications_mock.snils = self.snils
        self.applications_mock.remote_ip = self.remote_ip
        self.applications_mock.session_uuid = self.session_uuid

        # kyc form fields
        self.applications_mock.sex = self.sex
        self.applications_mock.birth_place_info = self.birth_place_info
        self.applications_mock.id_doc_issued = self.id_doc_issued
        self.applications_mock.id_doc_issued_by = self.id_doc_issued_by
        self.applications_mock.id_doc_department_code = (
            self.id_doc_department_code
        )
        self.applications_mock.address_registration = self.address_registration
        self.applications_mock.address_actual = self.address_actual

        self.processing_mock.buid = self.buid
        self.processing_mock.application_id = self.application_id
        self.processing_mock.core_banking_request_id = (
            self.core_banking_request_id
        )

        self.notifications_mock.consumer = self.consumer
        self.notifications_mock.processing_notification_events = (
            self.processing_notification_events
        )
        self.notifications_mock.buid = self.buid
        self.notifications_mock.defaults_groups = self.defaults_groups

        self.agreement_mock.agreement_title = self.agreement_title
        self.agreement_mock.agreement_version = self.agreement_version
        self.agreement_mock.yandex_uid = self.yuid
        self.agreement_mock.buid = self.buid

    async def create_kyc_application(self):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={'kind': 'init', 'type': 'KYC'},
            stq_queue='bank_applications_procaas',
        )
        assert event_id

    async def send_kyc_event(self, stq_fail=False, already_flushing_stq=False):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': 'KYC',
                'buid': self.buid,
                'client_ip': self.ip_address,
                'session_uuid': self.session_uuid,
                'agreement_title': self.agreement_title,
                'agreement_version': self.agreement_version,
            },
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
            already_flushing_stq=already_flushing_stq,
        )
        assert event_id
        return event_id

    async def send_kyc_finish_event(
            self, stq_fail=False, application_status=common.STATUS_SUCCESS,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': 'kyc_identification_finish',
                'buid': self.buid,
                'application_status': application_status,
            },
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
        )
        assert event_id

    async def send_application_status_event0(
            self, stq_fail=False, errors=None,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': 'application_status_result',
                'core_banking_request_id': self.core_banking_request_id,
                'buid': self.buid,
                'status': 'SUCCESS',
                'errors': errors,
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
            pipeline='create-kyc-pipeline',
    ):
        shared_state = (
            await self.processing.bank.applications.handle_single_event(
                item_id=self.application_id,
                pipeline=pipeline,
                payload={
                    'type': 'KYC',
                    'buid': self.buid,
                    'client_ip': self.ip_address,
                    'session_uuid': self.session_uuid,
                    'core_banking_request_id': self.core_banking_request_id,
                    'agreement_title': self.agreement_title,
                    'agreement_version': self.agreement_version,
                },
                initial_state=started_shared,
                stage_id=stage_id,
            )
        )
        assert shared_state == expected_shared, shared_state

    def check_kyc_calls(
            self,
            default_value=0,
            get_application_data=None,
            kyc_get_application_data=None,
            kyc_upgrade=None,
            set_core_banking_request_id=None,
            notifications_sended=None,
            create_event=0,
            accept_agreement=None,
    ):
        assert (
            self.applications_mock.set_core_request_id.handler.times_called
            == (
                set_core_banking_request_id
                if set_core_banking_request_id is not None
                else default_value
            )
        )
        assert (
            self.applications_mock.kyc_get_application_data.handler.times_called  # noqa
            == (
                kyc_get_application_data
                if kyc_get_application_data is not None
                else default_value
            )
        )
        assert (
            self.applications_mock.get_application_data.handler.times_called  # noqa
            == (
                get_application_data
                if get_application_data is not None
                else default_value
            )
        )
        assert (
            self.core_client_mock.kyc_request_upgrade.handler.times_called
            == (kyc_upgrade if kyc_upgrade is not None else default_value)
        )
        assert self.processing_mock.create_event.handler.times_called == (
            create_event
        )
        assert (
            self.notifications_mock.send_notification.handler.times_called
            == (
                notifications_sended
                if notifications_sended is not None
                else default_value
            )
        )
        assert self.agreement_mock.accept_agreement.handler.times_called == (
            accept_agreement if accept_agreement is not None else default_value
        )

    def check_application_status_calls(
            self,
            default_value=0,
            kyc_set_status=None,
            create_event=1,
            set_status=0,
    ):
        assert self.applications_mock.kyc_set_status.handler.times_called == (
            kyc_set_status if kyc_set_status is not None else default_value
        )
        assert self.applications_mock.set_status.handler.times_called == (
            set_status if set_status is not None else default_value
        )
        assert (
            self.processing_mock.create_event.handler.times_called
            == create_event
        ), self.processing_mock.create_event.handler.times_called

    def check_finish_calls(self, default_value=0, notifications_sended=1):
        assert (
            self.notifications_mock.send_notification.handler.times_called
            == (
                notifications_sended
                if notifications_sended is not None
                else default_value
            )
        )
