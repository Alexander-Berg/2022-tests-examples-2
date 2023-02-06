BUID = 'buid-1'
YUID = '8421'
PHONE_NUMBER = '+79037842423'
CORE_BANKING_REQUEST_ID = 'some_javist_id'
APPLICATION_ID = '123456789abcdefgh'

FINAL_BUID_STATUS = 'FINAL'
STATUS_SUCCESS = 'SUCCESS'
STATUS_FAILED = 'FAILED'
STATUS_PENDING = 'PENDING'
STATUS_PROCESSING = 'PROCESSING'
STATUS_AGREMENTS_ACCEPTED = 'AGREEMENTS_ACCEPTED'
STATUS_CORE_BANKING = 'CORE_BANKING'
SET_APPLICATIONS_SUCCESS = [
    STATUS_PROCESSING,
    STATUS_AGREMENTS_ACCEPTED,
    STATUS_SUCCESS,
]
SET_APPLICATIONS_FAILED = [
    STATUS_PROCESSING,
    STATUS_AGREMENTS_ACCEPTED,
    STATUS_FAILED,
]
SET_APPLICATIONS_PROCESSING = [
    STATUS_PROCESSING,
    STATUS_AGREMENTS_ACCEPTED,
    STATUS_CORE_BANKING,
    STATUS_SUCCESS,
]

LAST_NAME = 'volodya'
FIRST_NAME = 'petrov'
PATR = 'viktorovich'
MIDDLE_NAME = PATR
BIRTHDAY = '10.03.1989'
ID_TYPE = 'PASSPORT'
ID_DOC_TYPE = ID_TYPE
ID_NUMBER = '123123'
PASSPORT_NUMBER = ID_NUMBER
INN = '1488228'
SNILS = '2281488'
SEX = 'M'
IP = '127.0.0.1'
SESSION_UUID = 'fac13679-73f7-465f-b94e-f359525850ec'
CONSUMER = 'PROCESSING'
BIRTH_PLACE_INFO = {'country_code': 'RU', 'place': 'Москва'}
ID_DOC_ISSUED = '10.03.2000'
ID_DOC_ISSUED_BY = 'МВД РФ'
ID_DOC_DEPARTAMENT_CODE = '000-000'
DEFAULT_ESIA_AUTH_CODE = '12341234-1111-1111-1111-123412341234'
DEFAULT_ESIA_REDIRECT_URL = 'http://pod.url'
DEFAULT_DATA_REVISION = 1000_000_000_000
ADDRESS_REGISTRATION = {
    'country': 'Россия',
    'postal_code': '350000',
    'region': 'Московская обл.',
    'city': 'Москва',
    'area': 'Раменки',
    'street': 'ул. Пушкина',
    'house': 'Колотушкина',
    'building': '1',
    'flat': '1',
}
SIMPLIFIED_PROCESSING_ACTION = 'TEST_SIMPLIFIED_IN_PROCESSING'
SIMPL_MERGE_KEY_PREFIX = 'TEST_MERGE_KEY_PREFIX_SIMPL'

FAILED_DEFAULTS_GROUP = 'test_simplified_identification_status_failed'
PROGRESS_DEFAULTS_GROUP = 'test_simplified_identification_status_processing'
SUCCESS_DEFAULTS_GROUP = 'test_simplified_identification_status_success'
SUCCESS_DEFAULTS_GROUPS_LIST = [
    PROGRESS_DEFAULTS_GROUP,
    SUCCESS_DEFAULTS_GROUP,
]

SIMPLIFIED_IDENTIFICATION_AGREEMENT_TITLE = 'SIMPLIFIED_IDENTIFICATION'
KYC_AGREEMENT_TITLE = 'KYC'
AGREEMENT_VERSION = 1

PRODUCT_WALLET = 'WALLET'
PRODUCT_PRO = 'PRO'
AUTH_LEVEL_ANONYMOUS = 'ANONYMOUS'
AUTH_LEVEL_IDENTIFIED = 'IDENTIFIED'


class AnonHelper:
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
        self.ip_address = None
        self.yuid = None
        self.buid = None
        self.phone_number = None
        self.core_banking_request_id = None
        self.application_id = None
        self.session_uuid = None
        self.product = None
        self.has_ya_plus = None
        self.plus_offer_accepted = None

    def set_values(
            self,
            ip_address=IP,
            yuid=YUID,
            buid=BUID,
            phone_number=PHONE_NUMBER,
            core_banking_request_id=CORE_BANKING_REQUEST_ID,
            application_id=APPLICATION_ID,
            session_uuid=SESSION_UUID,
            product=None,
            has_ya_plus=None,
            plus_offer_accepted=None,
    ):
        self.ip_address = ip_address
        self.yuid = yuid
        self.buid = buid
        self.phone_number = phone_number
        self.core_banking_request_id = core_banking_request_id
        self.application_id = application_id
        self.session_uuid = session_uuid
        self.product = product
        self.has_ya_plus = has_ya_plus
        self.plus_offer_accepted = plus_offer_accepted

    def prepare_mocks(self):
        self.passport_mock.ip_address = self.ip_address
        self.passport_mock.yuid = self.yuid
        self.passport_mock.phone_number = self.phone_number
        self.core_client_mock.phone_number = self.phone_number
        self.core_client_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.core_client_mock.application_id = self.application_id
        self.core_client_mock.product = self.product
        self.userinfo_mock.buid = self.buid
        self.userinfo_mock.phone_number = self.phone_number
        self.userinfo_mock.product = self.product
        self.userinfo_mock.session_uuid = self.session_uuid
        self.applications_mock.remote_ip = self.ip_address
        self.applications_mock.session_uuid = self.session_uuid
        self.applications_mock.application_id = self.application_id
        self.applications_mock.yandex_uid = self.yuid
        self.applications_mock.phone_number = self.phone_number
        self.applications_mock.session_uuid = self.session_uuid
        self.applications_mock.product = self.product
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

    async def create_anon_application(self):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={'kind': 'init', 'type': 'REGISTRATION'},
            stq_queue='bank_applications_procaas',
        )
        assert event_id

    async def send_anon_event(
            self, stq_fail=False, already_flushing_stq=False,
    ):
        payload = {
            'kind': 'update',
            'type': 'REGISTRATION',
            'buid': self.buid,
            'yuid': self.yuid,
            'client_ip': self.ip_address,
            'session_uuid': self.session_uuid,
        }
        if self.product is not None:
            payload['product'] = self.product
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload=payload,
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
            already_flushing_stq=already_flushing_stq,
        )
        assert event_id
        return event_id

    async def send_update_buid_event(self, stq_fail=False):
        payload = {
            'kind': 'update',
            'type': 'update_buid_result',
            'core_banking_request_id': self.core_banking_request_id,
            'session_uuid': self.session_uuid,
            'buid': self.buid,
            'core_banking_status': 'SUCCESS',
            'client_ip': self.ip_address,
            'yuid': self.yuid,
        }
        if self.product is not None:
            payload['product'] = self.product
        if self.has_ya_plus is not None:
            payload['has_ya_plus'] = self.has_ya_plus
        if self.plus_offer_accepted is not None:
            payload['accepted_plus_offer'] = self.plus_offer_accepted
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload=payload,
            stq_queue='bank_applications_procaas',
            expect_fail=stq_fail,
        )
        assert event_id

    async def send_application_status_event(self, stq_fail=False, errors=None):
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
            pipeline='anon-creation-pipeline',
    ):
        payload = {
            'type': 'REGISTRATION',
            'buid': self.buid,
            'yuid': self.yuid,
            'client_ip': self.ip_address,
            'core_banking_request_id': self.core_banking_request_id,
            'session_uuid': self.session_uuid,
        }
        if self.product is not None:
            payload['product'] = self.product
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

    def check_anon_calls(
            self,
            default_value=0,
            get_application_data=None,
            get_antifraud_info_check=None,
            risk_phone_check=None,
            set_bank_phone=None,
            bind_phone=None,
            subscribe_sid=None,
            anonymous_create=None,
            set_core_banking_request_id=None,
            create_event=0,
    ):
        assert (
            self.applications_mock.get_application_data.handler.times_called
            == (
                get_application_data
                if get_application_data is not None
                else default_value
            )
        )
        assert self.userinfo_mock.get_antifraud_info.handler.times_called == (
            get_antifraud_info_check
            if get_antifraud_info_check is not None
            else default_value
        )
        assert self.risk_mock.phone_check.handler.times_called == (
            risk_phone_check if risk_phone_check is not None else default_value
        )
        assert self.userinfo_mock.set_bank_phone.handler.times_called == (
            set_bank_phone if set_bank_phone is not None else default_value
        )
        assert self.passport_mock.bind_phone.handler.times_called == (
            bind_phone if bind_phone is not None else default_value
        )
        assert self.passport_mock.subscribe_sid.handler.times_called == (
            subscribe_sid if subscribe_sid is not None else default_value
        )
        assert self.core_client_mock.request_create.handler.times_called == (
            anonymous_create if anonymous_create is not None else default_value
        )
        assert (
            self.applications_mock.set_core_request_id.handler.times_called
            == (
                set_core_banking_request_id
                if set_core_banking_request_id is not None
                else default_value
            )
        )
        assert (
            self.processing_mock.create_event.handler.times_called
            == create_event
        )

    def check_update_buid_calls(
            self,
            default_value=0,
            update_buid_status=None,
            add_product=None,
            update_app_status=None,
    ):
        assert self.userinfo_mock.update_buid_status.handler.times_called == (
            update_buid_status
            if update_buid_status is not None
            else default_value
        )
        assert self.userinfo_mock.add_product.handler.times_called == (
            add_product if add_product is not None else default_value
        )
        assert self.applications_mock.set_status.handler.times_called == (
            update_app_status
            if update_app_status is not None
            else default_value
        )

    def check_application_status_calls(
            self, default_value=0, set_status=None, create_event=1,
    ):
        assert self.applications_mock.set_status.handler.times_called == (
            set_status if set_status is not None else default_value
        )
        assert (
            self.processing_mock.create_event.handler.times_called
            == create_event
        ), self.processing_mock.create_event.handler.times_called


class SimplHelper:
    def __init__(
            self,
            passport_mock,
            core_client_mock,
            userinfo_mock,
            applications_mock,
            processing_mock,
            notifications_mock,
            agreement_mock,
            processing,
    ):
        self.passport_mock = passport_mock
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
        self.userinfo_mock = userinfo_mock
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

    def set_values(
            self,
            ip_address=IP,
            yuid=YUID,
            buid=BUID,
            phone_number=PHONE_NUMBER,
            core_banking_request_id=CORE_BANKING_REQUEST_ID,
            application_id=APPLICATION_ID,
            last_name=LAST_NAME,
            first_name=FIRST_NAME,
            middle_name=MIDDLE_NAME,
            birthday=BIRTHDAY,
            id_doc_type=ID_DOC_TYPE,
            passport_number=PASSPORT_NUMBER,
            application_status=STATUS_SUCCESS,
            core_banking_status=STATUS_SUCCESS,
            core_banking_is_error=False,
            inn=INN,
            snils=SNILS,
            inn_or_snils=INN,
            remote_ip=IP,
            session_uuid=SESSION_UUID,
            consumer=CONSUMER,
            processing_notification_events=None,
            defaults_groups=None,
            set_application_status=None,
            agreement_title=SIMPLIFIED_IDENTIFICATION_AGREEMENT_TITLE,
            agreement_version=AGREEMENT_VERSION,
    ):
        if defaults_groups is None:
            defaults_groups = SUCCESS_DEFAULTS_GROUPS_LIST
        if set_application_status is None:
            set_application_status = SET_APPLICATIONS_PROCESSING
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

    def prepare_mocks(self):
        self.passport_mock.ip_address = self.ip_address
        self.passport_mock.yuid = self.yuid
        self.passport_mock.phone_number = self.phone_number

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

        self.userinfo_mock.buid = self.buid
        self.userinfo_mock.phone_number = self.phone_number

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
        self.applications_mock.last_name = self.last_name
        self.applications_mock.first_name = self.first_name
        self.applications_mock.birthday = self.birthday
        self.applications_mock.passport_number = self.passport_number
        self.applications_mock.inn = self.inn
        self.applications_mock.snils = self.snils
        self.applications_mock.remote_ip = self.remote_ip
        self.applications_mock.session_uuid = self.session_uuid

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

    async def create_simpl_application(self):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={'kind': 'init', 'type': 'SIMPLIFIED_IDENTIFICATION'},
            stq_queue='bank_applications_procaas',
        )
        assert event_id

    async def send_simpl_event(
            self, stq_fail=False, already_flushing_stq=False,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': 'SIMPLIFIED_IDENTIFICATION',
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

    async def send_simplified_finish_event(
            self, stq_fail=False, application_status=STATUS_SUCCESS,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': 'simplified_identification_finish',
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
            pipeline='create-simpl-pipeline',
    ):
        shared_state = (
            await self.processing.bank.applications.handle_single_event(
                item_id=self.application_id,
                pipeline=pipeline,
                payload={
                    'type': 'SIMPLIFIED_IDENTIFICATION',
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

    def check_simpl_calls(
            self,
            default_value=0,
            get_application_data=None,
            simpl_get_application_data=None,
            simplified_upgrade=None,
            set_core_banking_request_id=None,
            notifications_sended=None,
            accept_agreement=None,
            create_event=0,
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
            self.applications_mock.simpl_get_application_data.handler.times_called  # noqa
            == (
                simpl_get_application_data
                if simpl_get_application_data is not None
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
        assert self.core_client_mock.request_upgrade.handler.times_called == (
            simplified_upgrade
            if simplified_upgrade is not None
            else default_value
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
            simpl_set_status=None,
            create_event=1,
            set_status=0,
    ):
        assert (
            self.applications_mock.simpl_set_status.handler.times_called
            == (
                simpl_set_status
                if simpl_set_status is not None
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

    def check_delete_pd_calls(self, delete_data=1):
        assert (
            self.applications_mock.delete_personal_data.handler.times_called
            == delete_data
        )

    def check_finish_calls(
            self, default_value=0, notifications_sended=1, delete_pd_sended=0,
    ):
        assert (
            self.notifications_mock.send_notification.handler.times_called
            == (
                notifications_sended
                if notifications_sended is not None
                else default_value
            )
        )
        assert (
            self.applications_mock.delete_personal_data.handler.times_called
            == delete_pd_sended
        )
