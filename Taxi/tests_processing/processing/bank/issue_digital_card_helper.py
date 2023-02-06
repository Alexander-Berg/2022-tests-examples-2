PUBLIC_AGREEMENT_ID = 'test_public_agreement_id'
CARD_TYPE = 'DIGITAL'
SESSION_UUID = 'fac13679-73f7-465f-b94e-f359525850ec'


class DigitalCardHelper:
    def __init__(
            self,
            core_card_mock,
            applications_mock,
            processing_mock,
            processing,
    ):
        self.core_card_mock = core_card_mock
        self.applications_mock = applications_mock
        self.processing_mock = processing_mock
        self.processing = processing
        self.yuid = None
        self.buid = None
        self.core_banking_request_id = None
        self.application_id = None
        self.public_agreement_id = None

    def set_values(
            self,
            yuid,
            buid,
            core_banking_request_id,
            application_id,
            public_agreement_id=None,
    ):
        self.yuid = yuid
        self.buid = buid
        self.core_banking_request_id = core_banking_request_id
        self.application_id = application_id
        self.public_agreement_id = public_agreement_id

    def prepare_mocks(self):
        self.core_card_mock.application_id = self.application_id
        self.core_card_mock.public_agreement_id = self.public_agreement_id
        self.core_card_mock.core_banking_request_id = (
            self.core_banking_request_id
        )
        self.applications_mock.application_id = self.application_id
        self.processing_mock.buid = self.buid
        self.processing_mock.application_id = self.application_id
        self.processing_mock.core_banking_request_id = (
            self.core_banking_request_id
        )

    async def create_digital_card_application(self):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={'kind': 'init', 'type': 'DIGITAL_CARD_ISSUE'},
            stq_queue='bank_applications_procaas',
        )
        assert event_id

    async def start_digital_card_stage(
            self, stage_id, started_shared, expected_shared,
    ):
        shared_state = (
            await self.processing.bank.applications.handle_single_event(
                item_id=self.application_id,
                pipeline='digital-card-creation-pipeline',
                payload={
                    'type': 'DIGITAL_CARD_ISSUE',
                    'buid': self.buid,
                    'yuid': self.yuid,
                    'request_id': self.core_banking_request_id,
                    'public_agreement_id': PUBLIC_AGREEMENT_ID,
                    'agreement_id': PUBLIC_AGREEMENT_ID,
                    'session_uuid': SESSION_UUID,
                },
                initial_state=started_shared,
                stage_id=stage_id,
            )
        )
        assert shared_state == expected_shared

    def check_digital_card_calls(
            self,
            default_value=0,
            set_status=None,
            create_event=0,
            digital_card_create=None,
    ):
        assert self.core_card_mock.request_create.handler.times_called == (
            digital_card_create
            if digital_card_create is not None
            else default_value
        )

        assert self.applications_mock.set_status.handler.times_called == (
            set_status if set_status is not None else default_value
        )
        assert (
            self.processing_mock.create_event.handler.times_called
            == create_event
        )
