# pylint: disable=too-many-lines
import pytest

from testsuite.utils import matching

from tests_cargo_crm import const

PREFIX_INTERNAL_TICKET = '/cargo-crm/internal/cargo-crm/flow/phoenix/ticket'
ADD_INDEX_ROW = (
    'INSERT INTO cargo_crm.tickets '
    '    (yandex_uid, phone_pd_id, ticket_id, corp_client_id) '
    f'VALUES (\'{const.UID}\', \'ppi\', \'{const.TICKET_ID}\', \'cci\')'
)
UTM_PARAMS = {
    'utm_source': 'source1',
    'utm_medium': 'medium1',
    'utm_campaign': 'campaign1',
    'utm_term': 'cargo',
    'utm_content': 'desktop|main',
}

CARGO_CRM_TICKET_PIPEDRIVE_ACTIVITY_DEFAULT = {
    'check_period': 60,
    'steps': {
        'card_bound_form': {
            'activity_after': 60,
            'activity_deadline': 600,
            'activity_note': 'text',
            'activity_subject': 'Регистрация Феникс.',
            'activity_type': 'call',
            'activity_user_id': 11962494,
            'amo_task_type_id': 1,
        },
        'company_info_form': {
            'activity_after': 60,
            'activity_deadline': 600,
            'activity_note': 'text',
            'activity_subject': 'Регистрация Феникс.',
            'activity_type': 'call',
            'activity_user_id': 11962494,
            'amo_task_type_id': 1,
        },
    },
}


class TestFlowState:
    @pytest.fixture(autouse=True)
    def init(self, happy_path_env):
        pass

    @pytest.fixture
    async def flow_state(self, get_flow_state):
        flow_state = await get_flow_state()
        return flow_state

    @pytest.fixture
    async def flow_state_opened(self, get_flow_state, acquire_ticket_lock):
        await acquire_ticket_lock(const.UID, const.TICKET_ID)
        flow_state = await get_flow_state()
        return flow_state

    @pytest.fixture
    async def phone_limit_test_prepare(
            self, blackbox_response, create_tickets,
    ):
        async def wrapper(
                phone,
                phone_pd_id,
                phone_usages_count,
                are_tickets_closed=True,
                are_tickets_successful=True,
        ):
            blackbox_response.switch_user_secured_phone(phone)
            create_tickets(
                count=phone_usages_count,
                phone_pd_id=phone_pd_id,
                are_closed=are_tickets_closed,
                are_successful=are_tickets_successful,
            )

        return wrapper

    async def test_has_token_without_tickets(self, flow_state):
        some_token = flow_state['new_ticket'].get('token')

        assert not flow_state['tickets']
        assert flow_state['new_ticket'] == {'token': some_token}

    async def test_new_token_on_each_request(self, get_flow_state):
        first = await get_flow_state()
        second = await get_flow_state()
        assert first['new_ticket']['token'] != second['new_ticket']['token']

    @pytest.mark.parametrize(
        'phone',
        (
            pytest.param(const.PHONE, id='phone passed'),
            pytest.param(None, id='no phone passed'),
        ),
    )
    async def test_chosen_phone_is_deprecated(self, get_flow_state, phone):
        state = await get_flow_state(chosen_phone=phone)
        assert 'token' in state['new_ticket']
        assert 'disable_reason' not in state['new_ticket']

    @pytest.mark.pgsql('cargo_crm', queries=[ADD_INDEX_ROW])
    async def test_can_open_only_one_ticket(
            self, flow_state_opened, get_translation,
    ):
        some_message = _flow_message(flow_state_opened)

        assert flow_state_opened['tickets'] == [
            {'ticket_id': const.TICKET_ID, 'corp_client_id': 'cci'},
        ]
        assert flow_state_opened['new_ticket'] == {
            'disable_reason': {
                'code': 'has_unresolved_tickets',
                'message': some_message,
                'details': {'ticket_id': const.TICKET_ID},
            },
        }
        assert some_message == get_translation(
            'ru', 'cargo_crm.fail_reasons.has_unresolved_tickets',
        )

    @pytest.mark.config(CARGO_CRM_NEW_PHOENIX_TICKETS_ENABLED=False)
    async def test_service_disabled(self, flow_state, get_translation):
        disable_message = _flow_message(flow_state)

        assert flow_state['new_ticket'] == {
            'disable_reason': {
                'code': 'manually_disabled',
                'message': disable_message,
                'details': {},
            },
        }
        assert disable_message == get_translation(
            'ru', 'cargo_crm.fail_reasons.manually_disabled',
        )

    def test_passport_account(self, flow_state):
        assert flow_state['passport_account'] == {
            'name': 'John',
            'surname': 'Smith',
            'phones': [{'phone': const.PHONE, 'need_confirmation': False}],
        }

    # FIXME ticket on automation to fix this, names in tests can be long
    # pylint: disable=C0103
    @pytest.mark.parametrize(
        'accept_lang',
        (
            pytest.param('ru', id='ru locale'),
            pytest.param('en', id='en locale'),
        ),
    )
    async def test_incomplete_passport_account(
            self,
            blackbox_response,
            get_flow_state,
            get_translation,
            accept_lang,
    ):
        del blackbox_response.user['attributes']
        del blackbox_response.user['phones'][0]['attributes']['108']
        state = await get_flow_state(accept_lang=accept_lang)
        assert state['passport_account'] == {'phones': []}
        assert _flow_message(state) == get_translation(
            accept_lang, 'cargo_crm.fail_reasons.unbound_phone_number',
        )

    @pytest.mark.parametrize(
        'accept_lang',
        (
            pytest.param('ru', id='ru locale'),
            pytest.param('en', id='en locale'),
        ),
    )
    async def test_unauthenticated(
            self, get_flow_state, get_translation, accept_lang,
    ):
        state = await get_flow_state(
            uid=None, chosen_phone=None, accept_lang=accept_lang,
        )
        message = _flow_message(state)
        assert message == get_translation(
            accept_lang, 'cargo_crm.fail_reasons.unauthenticated',
        )
        assert state == {
            'tickets': [],
            'client_events_channels': [
                {'channel': 'b2bweb:phoenix'},
                {'channel': 'tariff-editor:phoenix'},
            ],
            'new_ticket': {
                'disable_reason': {
                    'code': 'unauthenticated',
                    'message': message,
                    'details': {},
                },
            },
        }

    @pytest.mark.config(
        CARGO_CRM_REGISTRATION_LIMIT_BY_PHONE={
            '__default__': 10,
            const.ANOTHER_PHONE_PD_ID: 20,
        },
    )
    @pytest.mark.parametrize(
        (
            'is_limit_exceeded',
            'phone_usages_count',
            'phone',
            'phone_pd_id',
            'are_tickets_successful',
        ),
        (
            pytest.param(
                False, 5, const.PHONE, const.PHONE_PD_ID, True, id='ok',
            ),
            pytest.param(
                True,
                10,
                const.PHONE,
                const.PHONE_PD_ID,
                True,
                id='limit exceeded',
            ),
            pytest.param(
                False,
                15,
                const.ANOTHER_PHONE,
                const.ANOTHER_PHONE_PD_ID,
                True,
                id='ok exception',
            ),
            pytest.param(
                True,
                20,
                const.ANOTHER_PHONE,
                const.ANOTHER_PHONE_PD_ID,
                True,
                id='exception limit exceeded',
            ),
            pytest.param(
                False,
                20,
                const.PHONE,
                const.PHONE_PD_ID,
                False,
                id='closed unsuccessful tickets',
            ),
        ),
    )
    async def test_phone_limit(
            self,
            get_flow_state,
            phone_limit_test_prepare,
            get_translation,
            is_limit_exceeded,
            phone_usages_count,
            phone,
            phone_pd_id,
            are_tickets_successful,
    ):
        await phone_limit_test_prepare(
            phone=phone,
            phone_pd_id=phone_pd_id,
            phone_usages_count=phone_usages_count,
            are_tickets_successful=are_tickets_successful,
        )

        state = await get_flow_state(chosen_phone=phone)
        disable_reason = state['new_ticket'].get('disable_reason', {})
        if is_limit_exceeded:
            assert disable_reason == {
                'code': 'phone_usage_limit_exceeded',
                'message': get_translation(
                    'ru', 'cargo_crm.fail_reasons.phone_usage_limit_exceeded',
                ),
                'details': {},
            }
        else:
            assert disable_reason == {}

    async def test_channels(self, get_flow_state):
        state = await get_flow_state()
        assert state['client_events_channels'] == [
            {'channel': 'b2bweb:phoenix'},
            {'channel': 'tariff-editor:phoenix'},
            {
                'channel': (
                    'b2bweb:phoenix:37860dfe71ca51c379b44d197bc3ec9a2ec1da97'
                ),
            },
            {
                'channel': (
                    'tariff-editor:'
                    'phoenix:37860dfe71ca51c379b44d197bc3ec9a2ec1da97'
                ),
            },
        ]


class TestOfferTicketState:
    @pytest.fixture(autouse=True)
    def init(self, happy_path_env, procaas_ctx, happy_path_offer_events):
        procaas_ctx.events = happy_path_offer_events

    @pytest.fixture
    async def state_happy_path_passed(self, get_ticket_state):
        return await get_ticket_state()

    @pytest.mark.config(CARGO_CRM_OFFER_BY_DEFAULT_ENABLED=True)
    def test_happy_path_passed_state(
            self, state_happy_path_passed, offer_ticket_closed_state_expected,
    ):
        assert state_happy_path_passed == offer_ticket_closed_state_expected


class TestTicketState:
    @pytest.fixture(autouse=True)
    def init(self, happy_path_env):
        pass

    @pytest.fixture
    async def state_happy_path_passed(self, get_ticket_state):
        return await get_ticket_state()

    @pytest.fixture
    async def state_expired(
            self, procaas_ctx, happy_path_events, get_ticket_state,
    ):
        procaas_ctx.events = happy_path_events
        fail_reason = {'code': 'expired', 'message': '', 'details': {}}
        procaas_ctx.events[-1]['payload']['data']['fail_reason'] = fail_reason
        return await get_ticket_state()

    @pytest.fixture
    async def state_unfinished_op(
            self, procaas_ctx, get_ticket_state, happy_path_events,
    ):
        procaas_ctx.events = happy_path_events[:1]
        return await get_ticket_state()

    @pytest.fixture
    async def state_company_created(
            self, procaas_ctx, get_ticket_state, happy_path_events,
    ):
        procaas_ctx.events = happy_path_events[:3]
        return await get_ticket_state()

    def test_happy_path_passed_state(
            self, state_happy_path_passed, ticket_closed_state_expected,
    ):
        assert state_happy_path_passed == ticket_closed_state_expected

    # FIXME ticket on automation to fix this, names in tests can be long
    # pylint: disable=C0103
    def test_expired_without_awaited_step(self, state_expired):
        progress = state_expired['progress']
        keys = list(sorted(progress.keys()))
        # no `awaited_step`
        assert keys == ['last_modified_at', 'resolution', 'steps']
        assert progress['resolution']['fail_reason']['code'] == 'expired'

    def test_unfinished_op(self, state_unfinished_op):
        # Unfinished ops are always pending.
        # Even if were run long time ago.
        assert state_unfinished_op['pending_operations'] == [
            {
                'id': 'opid_1',
                'kind': 'initial_form',
                'requested_at': '2021-06-20T10:00:00+00:00',
            },
        ]

        assert state_unfinished_op['next_step'] == {
            'disable_reason': {
                'code': 'awaiting_step_resolution',
                'message': _ticket_message(state_unfinished_op),
                'details': {},
            },
        }

    @pytest.mark.now('2021-06-20T10:00:02+00:00')
    def test_recently_finished_ops(self, state_happy_path_passed):
        assert state_happy_path_passed['pending_operations'] == [
            {
                'id': 'opid_1',
                'kind': 'initial_form',
                'requested_at': '2021-06-20T10:00:00+00:00',
                'resolved_at': '2021-06-20T10:00:01+00:00',
            },
            {
                'id': 'opid_6',
                'kind': 'company_info_form',
                'requested_at': '2021-06-20T10:03:00+00:00',
                'resolved_at': '2021-06-20T10:03:01+00:00',
            },
        ]

    @pytest.mark.now('2021-06-20T10:00:02+00:00')
    def test_token_with_recently_finished_ops(self, state_company_created):
        assert 'pending_operations' in state_company_created
        assert 'token' in state_company_created['next_step']

    async def test_bearer_verification(self, request_ticket_state):
        response = await request_ticket_state(uid=const.ANOTHER_UID)
        assert response.status_code == 403

    @pytest.mark.parametrize(
        'push_event_id,expected_policy',
        [(None, 'stale'), ('some_event_id', 'primary')],
    )
    async def test_caching_proxy_stale_policy(
            self,
            proxy_handler_get_events,
            request_ticket_state,
            push_event_id,
            expected_policy,
    ):
        response = await request_ticket_state(push_event_id=push_event_id)
        assert response.status_code == 200

        assert proxy_handler_get_events.times_called == 1
        request = proxy_handler_get_events.next_call()['request']
        assert request.query == {
            'read_preferences': expected_policy,
            'scope': 'cargo',
            'queue': 'crm_flow_phoenix',
            'item_id': const.TICKET_ID,
        }

    async def test_proxing_to_internal(
            self,
            ticket_closed_state_expected,
            mock_ticket_state,
            request_b2b_ticket_state,
    ):
        response = await request_b2b_ticket_state()
        assert response.status_code == 200
        assert response.json() == ticket_closed_state_expected

        assert mock_ticket_state.times_called == 1
        request = mock_ticket_state.next_call()['request']
        assert request.method == 'GET'
        assert request.query == {
            'ticket_id': const.TICKET_ID,
            'push_event_id': const.PUSH_EVENT_ID,
        }
        expected_headers = {'X-Request-Mode': 'b2b', 'X-Yandex-Uid': const.UID}
        resp_headers = {k: request.headers[k] for k in expected_headers}
        assert expected_headers == resp_headers

    async def test_expired_after_init(
            self,
            procaas_ctx,
            happy_path_events,
            get_ticket_state,
            fail_reason_expired,
    ):
        procaas_ctx.events = happy_path_events[:2]  # has initial result
        procaas_ctx.events += happy_path_events[-1:]  # resolution
        resolution = procaas_ctx.events[-1]['payload']['data']
        resolution['fail_reason'] = fail_reason_expired

        state = await get_ticket_state()
        assert 'resolution' in state['progress']
        assert 'awaited_step' not in state['progress']


class TestTicketInit:
    @pytest.fixture(autouse=True)
    def init(self, happy_path_env, procaas_ctx):
        # no events before init
        procaas_ctx.events = []

    @pytest.fixture
    async def state(self, get_flow_state):
        return await get_flow_state()

    async def test_awaited_step(self, get_ticket_state):
        state = await get_ticket_state()
        assert state['progress']['awaited_step'] == 'initial_form'

    @pytest.mark.parametrize('include_utm_in_query', [False, True])
    @pytest.mark.parametrize('corp_payment_type', [None, 'card', 'offer'])
    async def test_procaas_event(
            self,
            request_ticket_init,
            procaas_only_request,
            state,
            initial_form,
            include_utm_in_query,
            corp_payment_type,
    ):
        expected_form_data = initial_form.copy()
        expected_form_data['contact_phone'] = ''  # personal data erased
        expected_form_data['utm_parameters'] = (
            UTM_PARAMS if include_utm_in_query else {}
        )
        expected_payment_type = (
            {'corp_payment_type': corp_payment_type}
            if corp_payment_type
            else {}
        )

        response = await request_ticket_init(
            _flow_token(state),
            include_utm_in_query=include_utm_in_query,
            corp_payment_type=corp_payment_type,
        )
        assert response.status_code == 200
        ticket_id = response.json()['ticket_id']
        operation_id = response.json()['operation_id']
        expected_idempotency_token = '%s:request' % operation_id

        request = procaas_only_request(expected_idempotency_token, ticket_id)
        assert request.json == {
            'kind': 'initial_form_request',
            'data': dict(
                {
                    'operation_id': operation_id,
                    'revision': 0,
                    'requester_uid': const.UID,
                    'requester_login': const.LOGIN,
                    'form_data': expected_form_data,
                    'form_pd': {'contact_phone_pd_id': const.PHONE_PD_ID},
                },
                **expected_payment_type,
            ),
        }

    async def test_ticket_id(self, request_ticket_init, state):
        response = await request_ticket_init(_flow_token(state))
        assert response.status_code == 200
        assert response.json()['ticket_id'] == response.json()['operation_id']

    async def test_doesnt_check_login(
            self, procaas_handler_create_event, request_ticket_init, state,
    ):
        token = _flow_token(state)
        response = await request_ticket_init(token, login=const.ANOTHER_LOGIN)
        assert response.status_code == 200
        request = procaas_handler_create_event.next_call()['request']
        assert request.json['data']['requester_login'] == const.ANOTHER_LOGIN

    async def test_rejects_fake_token(self, request_ticket_init):
        response = await request_ticket_init('fake_token')
        assert response.status_code == 409
        assert response.json()['code'] == 'invalid_token'

    async def test_verifies_uid(self, request_ticket_init, state):
        token = _flow_token(state)
        response = await request_ticket_init(token, uid=const.ANOTHER_UID)
        assert response.status_code == 409
        assert response.json()['code'] == 'invalid_token'


class TestCompanyCreated:
    @pytest.fixture(autouse=True)
    def init(self, procaas_ctx, happy_path_env, happy_path_events):
        # initial_form passed, awaited company_created_form
        procaas_ctx.events = happy_path_events[:2]

    @pytest.fixture
    async def state(self, get_ticket_state):
        return await get_ticket_state()

    def test_awaited_step(self, state):
        assert state['progress']['awaited_step'] == 'company_created_form'

    def test_no_token(self, state):
        # no token, wait while robot will finish next step
        assert state['next_step'] == {
            'disable_reason': {
                'code': 'awaiting_step_resolution',
                'message': _ticket_message(state),
                'details': {},
            },
        }

    async def test_procaas_event(
            self,
            request_company_created,
            procaas_only_request,
            company_created_form,
    ):
        response = await request_company_created(company_created_form)
        assert response.status_code == 200
        expected_idempotency_token = 'company_created_notification'

        request = procaas_only_request(expected_idempotency_token)
        assert request.json == {
            'kind': 'company_created_notification',
            'data': {'form_data': company_created_form, 'form_pd': {}},
        }


class TestCompanyInfo:
    @pytest.fixture(autouse=True)
    def init(self, procaas_ctx, happy_path_env, happy_path_events):
        # company_created_form passed, awaited company_info_form
        procaas_ctx.events = happy_path_events[:3]

    @pytest.fixture
    async def state(self, get_ticket_state):
        return await get_ticket_state()

    def test_awaited_step(self, state):
        assert state['progress']['awaited_step'] == 'company_info_form'

    @pytest.mark.parametrize(
        'email_in_company_info_form, expected_form_pd',
        [
            pytest.param(
                const.EMAIL,
                {'email_pd_id': const.EMAIL_PD_ID},
                id='form with email',
            ),
            pytest.param(None, {}, id='form without email'),
        ],
    )
    async def test_procaas_event(
            self,
            request_fill_company_info,
            procaas_only_request,
            state,
            company_info_form,
            email_in_company_info_form,
            expected_form_pd,
    ):
        form = company_info_form.copy()
        if email_in_company_info_form:
            form['email'] = email_in_company_info_form
        else:
            del form['email']
        response = await request_fill_company_info(_ticket_token(state), form)
        assert response.status_code == 200
        operation_id = response.json()['operation_id']
        expected_idempotency_token = '%s:request' % operation_id

        request = procaas_only_request(expected_idempotency_token)
        assert request.json == {
            'kind': 'company_info_form_request',
            'data': {
                'operation_id': operation_id,
                'revision': 3,
                'requester_uid': const.UID,
                'requester_login': const.LOGIN,
                'form_data': company_info_form,
                'form_pd': expected_form_pd,
            },
        }

    async def test_rejects_fake_token(
            self, request_fill_company_info, company_info_form,
    ):
        response = await request_fill_company_info(
            'fake_token', company_info_form,
        )
        assert response.status_code == 409
        assert response.json()['code'] == 'invalid_token'

    async def test_verifies_uid(
            self, request_fill_company_info, state, company_info_form,
    ):
        response = await request_fill_company_info(
            _ticket_token(state), company_info_form, uid=const.ANOTHER_UID,
        )
        assert response.status_code == 409
        assert response.json()['code'] == 'invalid_token'

    async def test_verifies_ticket(
            self, request_fill_company_info, state, company_info_form,
    ):
        response = await request_fill_company_info(
            _ticket_token(state),
            company_info_form,
            ticket_id=const.ANOTHER_TICKET_ID,
        )
        assert response.status_code == 409
        assert response.json()['code'] == 'invalid_token'


class TestCardBound:
    @pytest.fixture(autouse=True)
    def init(self, procaas_ctx, happy_path_env, happy_path_events):
        # company_info_form passed, awaited card_bound_form
        procaas_ctx.events = happy_path_events[:5]

    @pytest.fixture
    async def state(self, get_ticket_state):
        return await get_ticket_state()

    def test_awaited_step(self, state):
        assert state['progress']['awaited_step'] == 'card_bound_form'

    def test_no_token(self, state):
        # no token, wait while robot will finish next step
        assert state['next_step'] == {
            'disable_reason': {
                'code': 'awaiting_step_resolution',
                'message': _ticket_message(state),
                'details': {},
            },
        }

    @pytest.mark.config(CARGO_CRM_OFFER_BY_DEFAULT_ENABLED=True)
    def test_token_for_offer(self, state):
        assert state['next_step'] == {'token': matching.any_string}

    async def test_procaas_event(
            self, request_card_bound, procaas_only_request, card_bound_form,
    ):
        response = await request_card_bound(card_bound_form)
        assert response.status_code == 200
        expected_idempotency_token = 'card_bound_notification'

        request = procaas_only_request(expected_idempotency_token)
        assert request.json == {
            'kind': 'card_bound_notification',
            'data': {'form_data': card_bound_form, 'form_pd': {}},
        }


class TestFormResult:
    @pytest.fixture
    def fail_result(self):
        return {
            'operation_id': 'failed_op_id',
            'fail_reason': {
                'code': 'some_code',
                'message': 'some message',
                'details': {'some': 'details'},
            },
        }

    @pytest.fixture
    def ok_result(self):
        return {'operation_id': 'ok_op_id'}

    @pytest.mark.parametrize('event_kind', ['initial_form_result'])
    @pytest.mark.parametrize('result', ['ok_result', 'fail_result'])
    async def test_procaas_event(
            self,
            request_form_result,
            procaas_only_request,
            ok_result,
            fail_result,
            event_kind,
            result,
    ):
        reqbody = ok_result if result == 'ok_result' else fail_result

        response = await request_form_result(event_kind, reqbody)
        assert response.status_code == 200

        expected_token = '%s:result' % reqbody['operation_id']
        request = procaas_only_request(expected_token)
        assert request.json == {'kind': event_kind, 'data': reqbody}

    async def test_unknown_event_kind(self, request_form_result, ok_result):
        response = await request_form_result('unknown', ok_result)
        assert response.status_code == 500


class TestChecks:
    @pytest.fixture
    def two_req_events(self, happy_path_events):
        return [happy_path_events[0], happy_path_events[0]]

    @pytest.fixture
    def double_close_events(self, happy_path_events):
        events = happy_path_events.copy()
        events.append(events[-1])
        return events

    async def test_race(self, request_check_no_races, two_req_events):
        response = await request_check_no_races(two_req_events)
        assert response.status_code == 200
        respbody = response.json()
        assert respbody == {
            'fail_reason': {
                'code': 'invalid_token',
                'message': respbody.get('fail_reason', {}).get('message'),
                'details': {},
            },
        }

    async def test_no_race(self, request_check_no_races, two_req_events):
        response = await request_check_no_races(two_req_events[:1])
        assert response.status_code == 200
        assert response.json() == {}

    async def test_is_first(
            self, request_check_resolution_is_first, happy_path_events,
    ):
        response = await request_check_resolution_is_first(happy_path_events)
        assert response.status_code == 200
        assert response.json() == {}

    async def test_already_closed(
            self, request_check_resolution_is_first, double_close_events,
    ):
        response = await request_check_resolution_is_first(double_close_events)
        assert response.status_code == 200
        respbody = response.json()
        assert respbody == {
            'fail_reason': {
                'code': 'ticket_closed',
                'message': respbody.get('fail_reason', {}).get('message'),
                'details': {},
            },
        }


class TestTicketClose:
    @pytest.mark.parametrize('has_fail_reason', [False, True])
    async def test_sent_event(
            self,
            request_ticket_close,
            procaas_only_request,
            has_fail_reason,
            fail_reason_expired,
    ):
        if has_fail_reason:
            caused_by = 'phoenix:stq:<task_id>'
            fail_reason = fail_reason_expired
            expected_payload = {
                'kind': 'resolution',
                'data': {'caused_by': caused_by, 'fail_reason': fail_reason},
            }
        else:
            caused_by = 'phoenix:event:<event_id>'
            fail_reason = None
            expected_payload = {
                'kind': 'resolution',
                'data': {'caused_by': caused_by},
            }

        response = await request_ticket_close(caused_by, fail_reason)
        assert response.status_code == 200

        request = procaas_only_request(caused_by)
        assert request.json == expected_payload

    async def test_sent_admin_event(
            self, request_admin_ticket_close, mockserver,
    ):
        @mockserver.json_handler(
            '/cargo-crm/internal/cargo-crm/flow/phoenix/ticket/close',
        )
        def _handler(request):
            expected_query = {'ticket_id': const.TICKET_ID}
            expected_json = {
                'caused_by': f'manual:admin:{const.UID}',
                'fail_reason': {
                    'code': 'closed_manually',
                    'details': {},
                    'message': '',
                },
            }

            assert request.json == expected_json
            assert request.query == expected_query
            return mockserver.make_response(status=200)

        response = await request_admin_ticket_close()
        assert response.status_code == 200


class TestUpdateIndexTicket:
    TICKET_DEFAULT_VALUES = {
        'ticket_id': const.ANOTHER_TICKET_ID,
        'yandex_uid': 'test_yandex_uid',
        'phone_pd_id': '1234567890_id',
    }

    @pytest.fixture(autouse=True)
    def init(self, happy_path_env):
        pass

    @pytest.fixture(name='get_ticket_info')
    def _get_ticket_info(self, pgsql):
        def wrapper(ticket_id=self.TICKET_DEFAULT_VALUES['ticket_id']):
            cursor = pgsql['cargo_crm'].cursor()
            cursor.execute(
                """
                SELECT
                    yandex_uid,
                    phone_pd_id,
                    corp_client_id,
                    is_closed,
                    is_successful
                FROM cargo_crm.tickets
                WHERE
                    ticket_id = '{0}'
                """.format(
                    ticket_id,
                ),
            )
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return dict(zip(columns, row))

        return wrapper

    @pytest.fixture(name='create_default_ticket')
    async def _create_default_ticket(self, create_tickets):
        create_tickets(
            ticket_ids=[self.TICKET_DEFAULT_VALUES['ticket_id']],
            yandex_uid=self.TICKET_DEFAULT_VALUES['yandex_uid'],
            phone_pd_id=self.TICKET_DEFAULT_VALUES['phone_pd_id'],
            are_closed=False,
        )

    @pytest.fixture(name='make_update_index_request')
    async def _make_update_index_request(self, taxi_cargo_crm):
        async def wrapper(request_json):
            return await taxi_cargo_crm.post(
                '/internal/cargo-crm/flow/phoenix/ticket/update-index',
                json=request_json,
                params={'ticket_id': self.TICKET_DEFAULT_VALUES['ticket_id']},
            )

        return wrapper

    async def test_ticket_created(
            self, make_update_index_request, get_ticket_info,
    ):
        for _ in range(2):
            request_json = {
                'kind': 'ticket_created',
                'author_yandex_uid': self.TICKET_DEFAULT_VALUES['yandex_uid'],
                'author_phone_pd_id': self.TICKET_DEFAULT_VALUES[
                    'phone_pd_id'
                ],
            }
            response = await make_update_index_request(request_json)
            ticket_info = get_ticket_info()

            assert response.status_code == 200
            assert (
                ticket_info['yandex_uid'] == request_json['author_yandex_uid']
            )
            assert (
                ticket_info['phone_pd_id']
                == request_json['author_phone_pd_id']
            )

    async def test_corp_created(
            self,
            make_update_index_request,
            get_ticket_info,
            create_default_ticket,
    ):
        request_json = {
            'kind': 'corp_created',
            'corp_client_id': 'corp_client_id_1234567890123456',
        }
        response = await make_update_index_request(request_json)
        ticket_info = get_ticket_info()

        assert response.status_code == 200
        assert ticket_info['corp_client_id'] == request_json['corp_client_id']

    async def test_ticket_closed(
            self,
            make_update_index_request,
            get_ticket_info,
            create_default_ticket,
    ):
        request_json = {'kind': 'ticket_closed', 'is_successful': True}
        response = await make_update_index_request(request_json)
        ticket_info = get_ticket_info()

        assert response.status_code == 200
        assert ticket_info['is_successful'] == request_json['is_successful']
        assert ticket_info['is_closed']


class TestTicketExpiration:
    NOW = '2021-06-20T11:04:00+00:00'
    LATER = '2021-06-28T11:04:00+00:00'

    @pytest.fixture(autouse=True)
    def init(self, happy_path_env):
        pass

    @pytest.fixture
    def not_resolved_yet(self, happy_path_events, procaas_ctx):
        procaas_ctx.events = happy_path_events[:3]

    @pytest.fixture
    def was_rescheduled(self, stq):
        def wrapper():
            times_called = stq.cargo_crm_ticket_check_expired.times_called
            assert times_called <= 1
            return times_called == 1

        return wrapper

    @pytest.mark.now(NOW)
    async def test_early_run_rescheduling(
            self,
            not_resolved_yet,
            run_mark_expired,
            mock_ticket_close,
            was_rescheduled,
    ):
        await run_mark_expired(started_at=self.NOW)
        assert not mock_ticket_close.has_calls
        assert was_rescheduled()

    @pytest.mark.now(LATER)
    async def test_resolved_wont_expire(
            self,
            happy_path_env,
            run_mark_expired,
            mock_ticket_close,
            was_rescheduled,
    ):
        await run_mark_expired(started_at=self.LATER)
        assert not mock_ticket_close.has_calls
        assert not was_rescheduled()

    @pytest.mark.now(LATER)
    async def test_expire_when_time_has_come(
            self,
            not_resolved_yet,
            run_mark_expired,
            mock_ticket_close,
            was_rescheduled,
    ):
        task_id = await run_mark_expired(started_at=self.LATER)

        assert not was_rescheduled()

        assert mock_ticket_close.times_called == 1
        request = mock_ticket_close.next_call()['request']
        assert request.query == {'ticket_id': const.TICKET_ID}
        assert request.json == {
            'caused_by': 'phoenix:stq:{}'.format(task_id),
            'fail_reason': {'code': 'expired', 'message': '', 'details': {}},
        }

    @pytest.mark.config(
        CARGO_CRM_TICKET_EXPIRATION_DELAY=60 * 60 * 24 * 30,
    )  # 30 days
    @pytest.mark.now(LATER)
    async def test_ticket_expire_delay_config(
            self,
            not_resolved_yet,
            run_mark_expired,
            mock_ticket_close,
            was_rescheduled,
    ):
        """ Test for another cargo_crm_ticket_expiration_delay value (not default).
        Starting conditions are similar to previous test:
        'test_expire_when_time_has_come', but config value is 30 days,
        so it is too early to close ticket, stq will be rescheduled"""
        await run_mark_expired(started_at=self.LATER)
        assert not mock_ticket_close.has_calls
        assert was_rescheduled()


class TestTicketAbandoned:
    NOW = '2021-06-28T11:04:00+00:00'
    LATER = '2021-06-28T11:04:01+00:00'

    @pytest.fixture(autouse=True)
    def init(self, happy_path_env):
        pass

    @pytest.fixture
    def unwatched_status(self, happy_path_events, procaas_ctx):
        procaas_ctx.events = happy_path_events[
            :2
        ]  # expected company_created_form

    @pytest.fixture
    def watched_status(self, happy_path_events, procaas_ctx):
        procaas_ctx.events = happy_path_events[
            :3
        ]  # expected company_info_form

    @pytest.fixture
    def was_rescheduled(self, stq):
        def wrapper():
            times_called = stq.cargo_crm_ticket_check_abandoned.times_called
            assert times_called <= 1
            return times_called == 1

        return wrapper

    @pytest.mark.now(NOW)
    async def test_rescheduling(
            self, unwatched_status, run_stq_activity_expired, was_rescheduled,
    ):
        await run_stq_activity_expired(started_at=self.NOW)
        assert was_rescheduled()

    @pytest.mark.now(LATER)
    async def test_resolved_wont_set_task(
            self, happy_path_env, run_stq_activity_expired, was_rescheduled,
    ):
        await run_stq_activity_expired(started_at=self.LATER)
        assert not was_rescheduled()

    @pytest.mark.now(LATER)
    async def test_make_task_in_pipedrive(
            self,
            mockserver,
            load_json,
            watched_status,
            run_stq_activity_expired,
            was_rescheduled,
    ):
        @mockserver.json_handler('pipedrive-api/v1/activities')
        def _handler(request):
            body = load_json(
                '../test_phoenixpipe_create_activity/activity.json',
            )
            return mockserver.make_response(status=201, json=body)

        await run_stq_activity_expired(started_at=self.LATER)

        assert not was_rescheduled()

        assert _handler.times_called == 1
        request = _handler.next_call()['request']
        assert request.query == {
            'api_token': 'bddada1443fe253a58a28a84fde6403e61ae1c03',
        }
        assert request.json == load_json('activity_request.json')


class TestAmoTicketAbandoned:
    NOW = '2021-06-28T11:04:00+00:00'
    LATER = '2021-06-29T11:04:01+00:00'

    @pytest.fixture(autouse=True)
    def init(self, happy_path_env):
        pass

    @pytest.fixture
    def unwatched_status(self, happy_path_events, procaas_ctx):
        procaas_ctx.events = happy_path_events[
            :2
        ]  # expected company_created_form

    @pytest.fixture
    def watched_status(self, happy_path_events, procaas_ctx):
        procaas_ctx.events = happy_path_events[
            :3
        ]  # expected company_info_form

    @pytest.fixture
    def was_rescheduled(self, stq):
        def wrapper():
            times_called = (
                stq.cargo_crm_amocrm_ticket_check_abandoned.times_called
            )
            assert times_called <= 1
            return times_called == 1

        return wrapper

    @pytest.mark.now(NOW)
    async def test_rescheduling(
            self,
            unwatched_status,
            run_stq_amo_activity_expired,
            was_rescheduled,
    ):
        await run_stq_amo_activity_expired(started_at=self.NOW)
        assert was_rescheduled()

    @pytest.mark.now(LATER)
    async def test_resolved_wont_set_task(
            self,
            happy_path_env,
            run_stq_amo_activity_expired,
            was_rescheduled,
    ):
        await run_stq_amo_activity_expired(started_at=self.LATER)
        assert not was_rescheduled()

    @pytest.mark.now(LATER)
    @pytest.mark.config(
        CARGO_CRM_TICKET_PIPEDRIVE_ACTIVITY=CARGO_CRM_TICKET_PIPEDRIVE_ACTIVITY_DEFAULT,  # noqa: E501
    )
    async def test_make_task_in_amo(
            self,
            mockserver,
            load_json,
            watched_status,
            run_stq_amo_activity_expired,
            was_rescheduled,
    ):
        @mockserver.json_handler(
            '/cargo-sf/internal/cargo-sf/amocrm/internal-requests/create-task',
        )
        def _amo_handler(request):
            return mockserver.make_response(status=200, json={})

        await run_stq_amo_activity_expired(started_at=self.LATER)

        assert not was_rescheduled()

        assert _amo_handler.times_called == 1
        request = _amo_handler.next_call()['request']
        assert request.json == {
            'complete_till': 1624965241,
            'external_event_id': 'main_ticket_id___________size_32',
            'task_type_id': 1,
            'text': 'text',
            'responsible_user_id': 11962494,
        }


@pytest.fixture(name='get_flow_state')
def _get_flow_state(taxi_cargo_crm):
    async def wrapper(
            uid=const.UID, chosen_phone=const.PHONE, accept_lang=None,
    ):
        body = {}
        if chosen_phone is not None:
            body['chosen_phone'] = chosen_phone

        response = await taxi_cargo_crm.post(
            '/b2b/cargo-crm/flow/phoenix/state',
            headers=_headers(uid=uid, accept_lang=accept_lang),
            json=body,
        )
        assert response.status_code == 200

        return response.json()

    return wrapper


@pytest.fixture(name='request_ticket_init')
def _request_ticket_init(taxi_cargo_crm):
    async def wrapper(
            token,
            uid=None,
            contact_phone=None,
            login=const.LOGIN,
            include_utm_in_query=False,
            corp_payment_type=None,
    ):
        if uid is None:
            uid = const.UID
        if contact_phone is None:
            contact_phone = const.PHONE

        body = {
            'operation_token': token,
            'initial_form': {'contact_phone': contact_phone},
        }

        ticket_init_params = {}
        if include_utm_in_query:
            ticket_init_params.update(UTM_PARAMS)
        if corp_payment_type:
            ticket_init_params['corp_payment_type'] = corp_payment_type

        response = await taxi_cargo_crm.post(
            '/b2b/cargo-crm/flow/phoenix/ticket/init',
            headers=_headers(uid, login),
            json=body,
            params=ticket_init_params,
        )
        return response

    return wrapper


@pytest.fixture(name='request_fill_company_info')
def _request_fill_company_info(taxi_cargo_crm):
    async def wrapper(token, form, uid=const.UID, ticket_id=None):
        if ticket_id is None:
            ticket_id = const.TICKET_ID

        url = '/b2b/cargo-crm/flow/phoenix/ticket/fill-company-info'
        params = {'ticket_id': ticket_id}
        headers = _headers(uid=uid)
        body = {'operation_token': token, 'company_info_form': form}
        response = await taxi_cargo_crm.post(
            url, params=params, headers=headers, json=body,
        )
        return response

    return wrapper


@pytest.fixture(name='request_ticket_state')
def _request_ticket_state(taxi_cargo_crm):
    async def wrapper(ticket_id=None, uid=None, push_event_id=None):
        if uid is None:
            uid = const.UID
        if ticket_id is None:
            ticket_id = const.TICKET_ID

        params = {'ticket_id': ticket_id}
        if push_event_id is not None:
            params['push_event_id'] = push_event_id

        response = await taxi_cargo_crm.get(
            '/internal/cargo-crm/flow/phoenix/ticket/state',
            headers=_headers(uid),
            params=params,
        )

        return response

    return wrapper


@pytest.fixture(name='request_b2b_ticket_state')
def _request_b2b_ticket_state(taxi_cargo_crm):
    async def wrapper():
        params = {
            'ticket_id': const.TICKET_ID,
            'push_event_id': const.PUSH_EVENT_ID,
        }
        response = await taxi_cargo_crm.get(
            '/b2b/cargo-crm/flow/phoenix/ticket/state',
            headers=_headers(),
            params=params,
        )

        return response

    return wrapper


@pytest.fixture(name='request_company_created')
def _request_company_created(taxi_cargo_crm):
    async def wrapper(form):
        url = '/internal/cargo-crm/flow/phoenix/ticket/company-created'
        params = {'ticket_id': const.TICKET_ID}
        response = await taxi_cargo_crm.post(url, params=params, json=form)
        return response

    return wrapper


@pytest.fixture(name='request_card_bound')
def _request_card_bound(taxi_cargo_crm):
    async def wrapper(form):
        url = '/internal/cargo-crm/flow/phoenix/ticket/card-bound'
        params = {'ticket_id': const.TICKET_ID}
        response = await taxi_cargo_crm.post(url, params=params, json=form)
        return response

    return wrapper


@pytest.fixture(name='request_ticket_close')
def _request_ticket_close(taxi_cargo_crm):
    async def wrapper(caused_by, fail_reason=None):
        url = '/internal/cargo-crm/flow/phoenix/ticket/close'
        params = {'ticket_id': const.TICKET_ID}
        data = {'caused_by': caused_by}
        if fail_reason is not None:
            data['fail_reason'] = fail_reason
        response = await taxi_cargo_crm.post(url, params=params, json=data)
        return response

    return wrapper


@pytest.fixture(name='request_admin_ticket_close')
def _request_admin_ticket_close(taxi_cargo_crm, request_ticket_close):
    async def wrapper():
        url = '/admin/cargo-crm/flow/phoenix/ticket/close'
        params = {'ticket_id': const.TICKET_ID}
        headers = {'X-Yandex-Uid': const.UID}
        response = await taxi_cargo_crm.post(
            url, params=params, headers=headers,
        )
        return response

    return wrapper


@pytest.fixture(name='get_ticket_state')
def _get_ticket_state(request_ticket_state):
    async def wrapper():
        response = await request_ticket_state(const.TICKET_ID, const.UID)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='request_form_result')
def _get_form_result(taxi_cargo_crm):
    async def wrapper(event_kind, reqbody):
        url = '/internal/cargo-crm/flow/phoenix/ticket/send-form-request-processing-result'  # noqa: E501
        params = {'ticket_id': const.TICKET_ID, 'event_kind': event_kind}
        response = await taxi_cargo_crm.post(url, params=params, json=reqbody)
        return response

    return wrapper


@pytest.fixture(name='request_check_no_races')
def _request_check_no_races(taxi_cargo_crm):
    async def wrapper(events):
        url = '/internal/cargo-crm/flow/phoenix/ticket/check-no-races'
        params = {'ticket_id': const.TICKET_ID}
        reqbody = {'events': events}
        response = await taxi_cargo_crm.post(url, params=params, json=reqbody)
        return response

    return wrapper


@pytest.fixture(name='request_check_resolution_is_first')
def _request_check_resolution_is_first(taxi_cargo_crm):
    async def wrapper(events):
        url = (
            '/internal/cargo-crm/flow/phoenix/ticket/check-resolution-is-first'
        )
        params = {'ticket_id': const.TICKET_ID}
        reqbody = {'events': events}
        response = await taxi_cargo_crm.post(url, params=params, json=reqbody)
        return response

    return wrapper


def _get_event_idx(events, event_kind):
    for idx, event in enumerate(events, 1):
        if event['payload']['kind'] == event_kind:
            return idx
    return len(events)


@pytest.fixture(name='happy_path_pd_values')
def _happy_path_pd_values():
    return {
        'phones': [
            {'id': const.PHONE_PD_ID, 'value': const.PHONE},
            {'id': const.ANOTHER_PHONE_PD_ID, 'value': const.ANOTHER_PHONE},
        ],
        'emails': [{'id': const.EMAIL_PD_ID, 'value': const.EMAIL}],
    }


@pytest.fixture(name='run_mark_expired')
def _run_mark_expired(stq_runner):
    async def wrapper(started_at):
        kwargs = {'ticket_id': const.TICKET_ID, 'started_at': started_at}
        task_id = 'some_id'
        await stq_runner.cargo_crm_ticket_check_expired.call(
            task_id=task_id, kwargs=kwargs,
        )
        return task_id

    return wrapper


@pytest.fixture(name='run_stq_activity_expired')
def _run_stq_activity_expired(stq_runner):
    async def wrapper(started_at):
        kwargs = {
            'ticket_id': const.TICKET_ID,
            'started_at': started_at,
            'pipedrive_account': {'deal_id': 1, 'org_id': 1, 'person_id': 1},
        }
        task_id = 'some_id'
        await stq_runner.cargo_crm_ticket_check_abandoned.call(
            task_id=task_id, kwargs=kwargs,
        )
        return task_id

    return wrapper


@pytest.fixture(name='run_stq_amo_activity_expired')
def _run_stq_amo_activity_expired(stq_runner):
    async def wrapper(started_at):
        kwargs = {'ticket_id': const.TICKET_ID, 'started_at': started_at}
        task_id = 'some_id'
        await stq_runner.cargo_crm_amocrm_ticket_check_abandoned.call(
            task_id=task_id, kwargs=kwargs,
        )
        return task_id

    return wrapper


@pytest.fixture(name='mock_ticket_close')
def _mock_ticket_close(mockserver):
    url = '{}/close'.format(PREFIX_INTERNAL_TICKET)

    @mockserver.json_handler(url)
    def handler(request):
        return {}

    return handler


@pytest.fixture(name='mock_ticket_state')
def _mock_ticket_state(mockserver, ticket_closed_state_expected):
    url = '{}/state'.format(PREFIX_INTERNAL_TICKET)

    @mockserver.json_handler(url)
    def handler(request):
        return ticket_closed_state_expected

    return handler


@pytest.fixture(name='happy_path_env')
def _happy_path_env(
        personal_handler_bulk_retrieve,
        personal_handler_find,
        personal_handler_retrieve,
        personal_handler_store,
        procaas_handler_create_event,
        proxy_handler_get_events,
        personal_ctx,
        procaas_ctx,
        happy_path_events,
        happy_path_pd_values,
        mock_ticket_close,
        blackbox,
):
    procaas_ctx.events = happy_path_events
    personal_ctx.set_phones(happy_path_pd_values['phones'])
    personal_ctx.set_emails(happy_path_pd_values['emails'])


@pytest.fixture(name='procaas_only_request')
def _procaas_only_request(procaas_handler_create_event, procaas_ctx):
    def wrapper(expected_idempotency_token, ticket_id=None):
        if ticket_id is None:
            ticket_id = const.TICKET_ID

        assert procaas_handler_create_event.times_called == 1
        request = procaas_handler_create_event.next_call()['request']
        idempotency_token = procaas_ctx.extract_idempotency_token(request)

        url = '/processing/v1/cargo/crm_flow_phoenix/create-event'
        assert request.path == url
        assert request.query['item_id'] == ticket_id
        assert idempotency_token == expected_idempotency_token
        return request

    return wrapper


@pytest.fixture(name='fail_reason_expired')
def _fail_reason_expired():
    return {
        'code': 'expired',
        'message': 'Ticket has been expired',
        'details': {},
    }


@pytest.fixture(name='get_translation')
def _get_translation(load_json):
    translations = load_json('localizations/cargo.json')

    def wrapper(language, message_key):
        for item in translations:
            if item['_id'] != message_key:
                continue
            for value in item['values']:
                if value['conditions']['locale']['language'] == language:
                    return value['value']
            return None

    return wrapper


def _headers(uid=const.UID, login=const.LOGIN, accept_lang=None):
    headers = {'X-Remote-IP': '1.0.0.0'}
    if uid is not None:
        headers['X-Yandex-Uid'] = uid
        headers['X-Ya-User-Ticket'] = const.USER_TICKET
    if login is not None:
        headers['X-Yandex-Login'] = login
    if accept_lang is not None:
        headers['Accept-Language'] = accept_lang
    return headers


def _flow_token(state):
    return state['new_ticket']['token']


def _flow_message(state):
    return state['new_ticket'].get('disable_reason', {}).get('message', '-')


def _ticket_token(state):
    return state['next_step']['token']


def _ticket_message(state):
    return state['next_step'].get('disable_reason', {}).get('message', '-')
