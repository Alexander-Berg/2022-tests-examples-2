import copy
import json

import pytest

BUID = 'buid-1'
UID = '12345'
AGREEMENT_ID = 'agreement123'
APPLICATION_ID = 'application123'
RISK_CONTEXT_ID = 'context123'

STATUS_SUBMITTED = 'SUBMITTED'
STATUS_PROCESSING = 'PROCESSING'

SPLIT_CARD_ISSUE = 'SPLIT_CARD_ISSUE'
STQ_QUEUE = 'bank_applications_procaas'


class KycClientInfo:
    def __init__(
            self,
            only_required=False,
            phone_number='+79000000000',
            last_name='Петров',
            first_name='Петр',
            birth_date='2021-08-30',
            id_doc_type='PASSPORT',
            id_doc_series='0001',
            id_doc_number='123456',
            id_doc_issued='2021-08-30',
            patronymic='Петрович',
            sex='M',  # M, F, NA
            birth_place='Москва',
            nationality='Россия',
            resident=True,
            inn='123456789012',
            snils='12345678901',
            id_doc_issued_by='МВД по г.Москве',
            id_doc_expiry='2031-08-30',
            id_doc_department_code='123456',
            address_registration={
                'country': 'Россия',
                'city': 'Москва',
                'street': 'Садовническая',
                'building': '82',
            },  # pylint: disable=dangerous-default-value
            address_actual={
                'country': 'Россия',
                'city': 'Москва',
                'street': 'Садовническая',
                'building': '82',
                'postal_code': '000000',
                'apartment': '5',
                'free_form': 'some free form',
            },  # pylint: disable=dangerous-default-value
            address_mail={
                'country': 'Россия',
                'city': 'Москва',
                'street': 'Садовническая',
                'building': '82',
            },  # pylint: disable=dangerous-default-value
    ):
        self.only_required = only_required
        self.phone_number = phone_number
        self.last_name = last_name
        self.first_name = first_name
        self.birth_date = birth_date
        self.id_doc_type = id_doc_type
        self.id_doc_series = id_doc_series
        self.id_doc_number = id_doc_number
        self.id_doc_issued = id_doc_issued
        self.patronymic = patronymic if not self.only_required else None
        self.sex = sex if not self.only_required else None
        self.birth_place = birth_place if not self.only_required else None
        self.nationality = nationality if not self.only_required else None
        self.resident = resident if not self.only_required else None
        self.inn = inn if not self.only_required else None
        self.snils = snils if not self.only_required else None
        self.id_doc_issued_by = (
            id_doc_issued_by if not self.only_required else None
        )
        self.id_doc_expiry = id_doc_expiry if not self.only_required else None
        self.id_doc_department_code = (
            id_doc_department_code if not self.only_required else None
        )
        self.address_registration = (
            address_registration if not self.only_required else None
        )
        self.address_actual = (
            address_actual if not self.only_required else None
        )
        self.address_mail = address_mail if not self.only_required else None

    def dump(self):
        res = {
            'phone_number': self.phone_number,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'birth_date': self.birth_date,
            'id_doc_type': self.id_doc_type,
            'id_doc_series': self.id_doc_series,
            'id_doc_number': self.id_doc_number,
            'id_doc_issued': self.id_doc_issued,
        }
        if not self.only_required:
            if self.patronymic:
                res['patronymic'] = self.patronymic
            if self.sex:
                res['sex'] = self.sex
            if self.birth_place:
                res['birth_place'] = self.birth_place
            if self.nationality:
                res['nationality'] = self.nationality
            if self.resident:
                res['resident'] = self.resident
            if self.inn:
                res['inn'] = self.inn
            if self.snils:
                res['snils'] = self.snils
            if self.id_doc_issued_by:
                res['id_doc_issued_by'] = self.id_doc_issued_by
            if self.id_doc_expiry:
                res['id_doc_expiry'] = self.id_doc_expiry
            if self.id_doc_department_code:
                res['id_doc_department_code'] = self.id_doc_department_code
            if self.address_registration:
                res['address_registration'] = self.address_registration
            if self.address_actual:
                res['address_actual'] = self.address_actual
            if self.address_mail:
                res['address_mail'] = self.address_mail
        return res


@pytest.fixture(name='custom_applications_mock')
async def _applications_mock(mockserver):
    class Context:
        def __init__(self):
            self.set_application_status_mock = None
            self.application_status = STATUS_SUBMITTED
            self.http_status_code = 200

        def set_application_status(self, status):
            self.application_status = status

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/applications-internal/v1/split_card_issue/set_application_status',
    )
    async def _set_application_status(request):
        data = json.loads(request.get_data())
        assert data['application_id'] == APPLICATION_ID
        assert data['status'] in [STATUS_PROCESSING]
        if context.http_status_code == 200:
            return {}
        if context.http_status_code == 400:
            return mockserver.make_response(
                status=400,
                json={'code': 'BadRequest', 'message': 'bad request'},
            )
        if context.http_status_code == 404:
            return mockserver.make_response(
                status=404, json={'code': 'NotFound', 'message': 'not found'},
            )
        if context.http_status_code == 500:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'internal error'},
            )
        raise Exception('unsupported error code')

    context.set_application_status_mock = _set_application_status
    return context


@pytest.fixture(name='custom_core_client_mock')
async def _core_client_mock(mockserver):
    class Context:
        def __init__(self):
            self.get_kyc_client_mock = None
            self.kyc_client_info = KycClientInfo()
            self.http_status_code = 200

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler('/v1/client/kyc/get')
    async def _get_kyc_client(request):
        assert request.headers['X-Yandex-BUID'] == BUID
        if context.http_status_code == 200:
            return mockserver.make_response(
                status=200, json=context.kyc_client_info.dump(),
            )
        if context.http_status_code == 404:
            return mockserver.make_response(
                status=404, json={'code': 'NotFound', 'message': 'not found'},
            )
        if context.http_status_code == 500:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'internal error'},
            )
        raise Exception('unsupported error code')

    context.get_kyc_client_mock = _get_kyc_client
    return context


@pytest.fixture(name='custom_risk_mock')
async def _risk_mock(mockserver):
    class Context:
        def __init__(self):
            self.risk_calculation_mock = None
            self.kyc_client_info = KycClientInfo()
            self.uid = UID
            self.buid = BUID
            self.http_status_code = 200

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler('/risk/calculation/dmc_credit_card')
    async def _risk_calculation_dmc_credit_card(request):
        data = json.loads(request.get_data())
        request_info = data.get('request_info')
        assert request_info
        assert request_info['class_name'] == 'inquiry_info'
        inquiry_info = request_info.get('inquiry_info')
        assert inquiry_info
        assert inquiry_info['application_id'] == APPLICATION_ID
        assert inquiry_info['inquiry'] == {
            'currency_code': 'RUB',
            'amount': 100000,
            'purpose': 9,
        }
        features = inquiry_info.get('user_features', {}).get('features')
        assert isinstance(features, list)

        assert features[0] == {
            'class_name': 'ypuid',
            'yandex_id': {'puid': int(context.uid)},
        }

        assert features[1] == {
            'class_name': 'buid',
            'bank_uid': {'id': context.buid},
        }

        assert features[2] == {
            'class_name': 'phone',
            'phone': {'number': context.kyc_client_info.phone_number},
        }

        fiodr = {
            'last_name': context.kyc_client_info.last_name,
            'first_name': context.kyc_client_info.first_name,
            'birth_date': {'date': context.kyc_client_info.birth_date},
        }
        if context.kyc_client_info.patronymic:
            fiodr['patronymic'] = context.kyc_client_info.patronymic
        assert features[3] == {'class_name': 'fiodr', 'fiodr': fiodr}

        passport = {
            'series': context.kyc_client_info.id_doc_series,
            'number': context.kyc_client_info.id_doc_number,
            'when': {'date': context.kyc_client_info.id_doc_issued},
        }
        if context.kyc_client_info.id_doc_department_code:
            passport[
                'region_id'
            ] = context.kyc_client_info.id_doc_department_code
        if context.kyc_client_info.id_doc_issued_by:
            passport['who'] = context.kyc_client_info.id_doc_issued_by
        assert features[4] == {'class_name': 'passport', 'passport': passport}

        idx = 5

        if context.kyc_client_info.sex:
            gender = ''
            if context.kyc_client_info.sex == 'NA':
                gender = 'undefined'
            elif context.kyc_client_info.sex == 'M':
                gender = 'male'
            elif context.kyc_client_info.sex == 'F':
                gender = 'female'
            assert features[idx] == {
                'class_name': 'gender',
                'gender': {'kind': gender},
            }
            idx += 1

        if context.kyc_client_info.inn:
            assert features[idx] == {
                'class_name': 'inn',
                'inn': {'number': context.kyc_client_info.inn},
            }
            idx += 1

        if context.kyc_client_info.snils:
            assert features[idx] == {
                'class_name': 'snils',
                'snils': {'number': context.kyc_client_info.snils},
            }
            idx += 1

        if context.kyc_client_info.address_registration:
            address = {
                'country': context.kyc_client_info.address_registration[
                    'country'
                ],
                'locality': context.kyc_client_info.address_registration[
                    'city'
                ],
                'street': context.kyc_client_info.address_registration[
                    'street'
                ],
                'house': context.kyc_client_info.address_registration[
                    'building'
                ],
            }
            apartment = context.kyc_client_info.address_registration.get(
                'apartment',
            )
            if apartment:
                address['room'] = apartment

            assert features[idx] == {
                'class_name': 'address',
                'address': {
                    'kind': 'registration',
                    'address': {
                        'detailed_address': address,
                        'detail_level': 'detailed',
                    },
                },
            }
            idx += 1

        if context.kyc_client_info.address_actual:
            address = {
                'country': context.kyc_client_info.address_actual['country'],
                'locality': context.kyc_client_info.address_actual['city'],
                'street': context.kyc_client_info.address_actual['street'],
                'house': context.kyc_client_info.address_actual['building'],
            }
            apartment = context.kyc_client_info.address_actual.get('apartment')
            if apartment:
                address['room'] = apartment

            assert features[idx] == {
                'class_name': 'address',
                'address': {
                    'kind': 'accomodation',
                    'address': {
                        'detailed_address': address,
                        'detail_level': 'detailed',
                    },
                },
            }
            idx += 1

        if context.kyc_client_info.birth_place:
            assert features[idx] == {
                'class_name': 'address',
                'address': {
                    'kind': 'birthplace',
                    'address': {
                        'simple_address': {
                            'full_address': (
                                context.kyc_client_info.birth_place
                            ),
                        },
                        'detail_level': 'simple',
                    },
                },
            }
            idx += 1

        assert len(features) == idx

        if context.http_status_code == 200:
            return mockserver.make_response(
                status=200, json={'context_id': RISK_CONTEXT_ID},
            )
        if context.http_status_code == 400:
            return mockserver.make_response(
                status=400,
                json={'code': 'BadRequest', 'message': 'bad request'},
            )
        if context.http_status_code == 500:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'internal error'},
            )
        raise Exception('unsupported error code')

    context.risk_calculation_mock = _risk_calculation_dmc_credit_card
    return context


class SplitCardIssueHelper:
    def __init__(
            self,
            applications_mock,
            processing_mock,
            core_client_mock,
            risk_mock,
            processing,
            buid,
            uid,
            application_id,
            agreement_id,
            kyc_client_info,
    ):
        self.applications_mock = applications_mock
        self.processing_mock = processing_mock
        self.core_client_mock = core_client_mock
        self.risk_mock = risk_mock
        self.processing = processing
        self.buid = buid
        self.uid = uid
        self.application_id = application_id
        self.agreement_id = agreement_id
        self.kyc_client_info = kyc_client_info

    def prepare_mocks(self):
        self.applications_mock.application_id = self.application_id
        self.processing_mock.buid = self.buid
        self.processing_mock.application_id = self.application_id
        self.core_client_mock.kyc_client_info = self.kyc_client_info
        self.risk_mock.uid = self.uid
        self.risk_mock.buid = self.buid
        self.risk_mock.kyc_client_info = self.kyc_client_info

    async def send_init_event(self):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={'kind': 'init', 'type': SPLIT_CARD_ISSUE},
            stq_queue=STQ_QUEUE,
        )
        assert event_id

    async def send_update_event(
            self, expect_fail=False, already_flushing_stq=False,
    ):
        event_id = await self.processing.bank.applications.send_event(
            item_id=self.application_id,
            payload={
                'kind': 'update',
                'type': SPLIT_CARD_ISSUE,
                'uid': self.uid,
                'buid': self.buid,
                'agreement_id': self.agreement_id,
            },
            stq_queue=STQ_QUEUE,
            expect_fail=expect_fail,
            already_flushing_stq=already_flushing_stq,
        )
        return event_id

    async def call(self, expect_fail=False):
        await self.processing.bank.applications.call(
            item_id=self.application_id,
            expect_fail=expect_fail,
            stq_queue=STQ_QUEUE,
        )

    async def run_single_stage(self, stage_id, initial_state, expected_state):
        shared_state = (
            await self.processing.bank.applications.handle_single_event(
                item_id=self.application_id,
                pipeline='split-card-issue-creation-pipeline',
                payload={
                    'type': SPLIT_CARD_ISSUE,
                    'buid': self.buid,
                    'uid': self.uid,
                    'agreement_id': AGREEMENT_ID,
                },
                initial_state=initial_state,
                stage_id=stage_id,
            )
        )
        assert shared_state == expected_state

    def check_calls(
            self,
            default_value=0,
            set_application_status=None,
            get_passport_data=None,
            risk_calculation=None,
            create_event=0,
    ):
        assert (
            self.applications_mock.set_application_status_mock.times_called
            == (
                set_application_status
                if set_application_status is not None
                else default_value
            )
        )
        assert self.core_client_mock.get_kyc_client_mock.times_called == (
            get_passport_data
            if get_passport_data is not None
            else default_value
        )
        assert self.risk_mock.risk_calculation_mock.times_called == (
            risk_calculation if risk_calculation is not None else default_value
        )
        assert (
            self.processing_mock.create_event.handler.times_called
            == create_event
        )


async def test_create_split_card_set_application_status_stage_ok(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        KycClientInfo(),
    )
    await helper.send_init_event()
    helper.prepare_mocks()
    await helper.run_single_stage(
        'set-application-status-stage-id',
        {},
        {'status': STATUS_PROCESSING, 'is_error': False, 'errors': None},
    )
    helper.check_calls(set_application_status=1)


@pytest.mark.parametrize(
    'status_code,expected_tries', [(400, 1), (404, 1), (500, 2)],
)
async def test_create_split_card_set_application_status_stage_fails(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
        status_code,
        expected_tries,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        KycClientInfo(),
    )
    await helper.send_init_event()
    helper.prepare_mocks()
    helper.applications_mock.set_http_status_code(status_code)
    with pytest.raises(Exception):
        await helper.run_single_stage(
            'set-application-status-stage-id', {}, {},
        )
    helper.check_calls(set_application_status=expected_tries)


@pytest.mark.parametrize(
    'kyc_client_info', [KycClientInfo(), KycClientInfo(only_required=True)],
)
async def test_create_split_card_get_passport_data_stage_ok(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
        kyc_client_info,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        kyc_client_info,
    )
    await helper.send_init_event()
    helper.prepare_mocks()

    shared_state_before = {
        'status': STATUS_PROCESSING,
        'is_error': False,
        'errors': None,
    }

    shared_state_after = copy.deepcopy(shared_state_before)
    shared_state_after['kyc_client_info'] = helper.kyc_client_info.dump()

    await helper.run_single_stage(
        'get-passport-data-stage-id', shared_state_before, shared_state_after,
    )
    helper.check_calls(get_passport_data=1)


@pytest.mark.parametrize('status_code,expected_tries', [(404, 1), (500, 2)])
async def test_create_split_card_get_passport_data_stage_fails(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
        status_code,
        expected_tries,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        KycClientInfo(),
    )
    await helper.send_init_event()
    helper.prepare_mocks()
    helper.core_client_mock.set_http_status_code(status_code)
    with pytest.raises(Exception):
        await helper.run_single_stage(
            'get-passport-data-stage-id',
            {'status': STATUS_PROCESSING, 'is_error': False, 'errors': None},
            {},
        )
    helper.check_calls(get_passport_data=expected_tries)


@pytest.mark.parametrize(
    'kyc_client_info', [KycClientInfo(), KycClientInfo(only_required=True)],
)
async def test_create_split_card_risk_calculation_stage_ok(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
        kyc_client_info,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        kyc_client_info,
    )
    await helper.send_init_event()
    helper.prepare_mocks()

    shared_state_before = {
        'status': STATUS_PROCESSING,
        'is_error': False,
        'errors': None,
        'kyc_client_info': helper.kyc_client_info.dump(),
    }

    shared_state_after = copy.deepcopy(shared_state_before)
    shared_state_after['risk_context_id'] = RISK_CONTEXT_ID

    await helper.run_single_stage(
        'risk-calculation-stage-id', shared_state_before, shared_state_after,
    )
    helper.check_calls(risk_calculation=1)


@pytest.mark.parametrize('status_code,expected_tries', [(400, 1), (500, 2)])
async def test_create_split_card_risk_calculation_stage_fails(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
        status_code,
        expected_tries,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        KycClientInfo(),
    )
    await helper.send_init_event()
    helper.prepare_mocks()
    helper.risk_mock.set_http_status_code(status_code)
    with pytest.raises(Exception):
        await helper.run_single_stage(
            'risk-calculation-stage-id',
            {
                'status': STATUS_PROCESSING,
                'is_error': False,
                'errors': None,
                'kyc_client_info': helper.kyc_client_info.dump(),
            },
            {},
        )
    helper.check_calls(risk_calculation=expected_tries)


@pytest.mark.parametrize(
    'codes,expected_tries',
    [
        ([200], 1),
        ([400, 400, 200], 3),
        ([500, 500, 500, 200], 7),
        ([404, 400, 500, 500, 200], 7),
    ],
)
async def test_create_split_card_issue_set_app_status_pipeline(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
        codes,
        expected_tries,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        KycClientInfo(),
    )
    await helper.send_init_event()
    helper.prepare_mocks()

    helper.applications_mock.set_http_status_code(codes[0])
    await helper.send_update_event(expect_fail=(codes[0] != 200))

    for code in codes[1:]:
        helper.applications_mock.set_http_status_code(code)
        await helper.call(expect_fail=(code != 200))

    helper.check_calls(
        set_application_status=expected_tries,
        get_passport_data=1,
        risk_calculation=1,
    )


@pytest.mark.parametrize(
    'codes,expected_tries',
    [
        ([200], 1),
        ([404, 404, 200], 3),
        ([500, 500, 500, 200], 7),
        ([404, 404, 500, 500, 200], 7),
    ],
)
async def test_create_split_card_issue_get_passport_data_pipeline(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
        codes,
        expected_tries,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        KycClientInfo(),
    )
    await helper.send_init_event()
    helper.prepare_mocks()

    helper.core_client_mock.set_http_status_code(codes[0])
    await helper.send_update_event(expect_fail=(codes[0] != 200))

    for code in codes[1:]:
        helper.core_client_mock.set_http_status_code(code)
        await helper.call(expect_fail=(code != 200))

    helper.check_calls(
        set_application_status=1,
        get_passport_data=expected_tries,
        risk_calculation=1,
    )


@pytest.mark.parametrize(
    'codes,expected_tries',
    [
        ([200], 1),
        ([400, 400, 200], 3),
        ([500, 500, 500, 200], 7),
        ([400, 400, 500, 500, 200], 7),
    ],
)
async def test_create_split_card_issue_risk_calculation_pipeline(
        processing,
        mockserver,
        custom_applications_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing_mock,
        codes,
        expected_tries,
):
    helper = SplitCardIssueHelper(
        custom_applications_mock,
        processing_mock,
        custom_core_client_mock,
        custom_risk_mock,
        processing,
        BUID,
        UID,
        APPLICATION_ID,
        AGREEMENT_ID,
        KycClientInfo(),
    )
    await helper.send_init_event()
    helper.prepare_mocks()

    helper.risk_mock.set_http_status_code(codes[0])
    await helper.send_update_event(expect_fail=(codes[0] != 200))

    for code in codes[1:]:
        helper.risk_mock.set_http_status_code(code)
        await helper.call(expect_fail=(code != 200))

    helper.check_calls(
        set_application_status=1,
        get_passport_data=1,
        risk_calculation=expected_tries,
    )
