import pytest

from tests_cargo_corp import utils


CARGO_CORP_LIST_RESPONSE = [
    {
        'id': 'corp_client_id_1',
        'name': 'Карго компания 1',
        'is_registration_finished': False,
    },
    {
        'id': 'corp_client_id_2',
        'name': 'Карго компания 2',
        'is_registration_finished': True,
    },
]


@pytest.fixture(name='request_launch')
def _request_launch(taxi_cargo_corp):
    async def wrapper(yandex_uid=utils.YANDEX_UID):
        url = '/v1/launch'
        headers = {'X-Yandex-Uid': yandex_uid} if yandex_uid else {}

        return await taxi_cargo_corp.post(url, headers=headers)

    return wrapper


@pytest.fixture(name='launch_response_ok')
async def _launch_response_ok(request_launch):
    async def wrapper(yandex_uid=utils.YANDEX_UID):
        response = await request_launch(yandex_uid)
        assert response.status_code == 200
        return response.json()

    return wrapper


def get_response_corp_parts(response):
    return (
        response['companies'],
        response.get('error_messages'),
        response['allowed_new_registrations']['corp_offer'],
    )


def get_response_phoenix_parts(response):
    return (
        response['tickets'],
        response.get('passport_account'),
        response.get('error_messages'),
        response['allowed_new_registrations']['cargo_phoenix'],
    )


def assert_cargos_in_lauch_response(mocked_clients, launch_companies):
    for corp_client in mocked_clients:
        assert {
            'source': 'cargo',
            'id': corp_client['id'],
            'name': corp_client['name'],
            'is_registration_finished': corp_client[
                'is_registration_finished'
            ],
        } in launch_companies


def get_error_codes(error_messages):
    return set(error['code'] for error in error_messages or [])


def assert_reg(new_reg, reason=None):
    if reason:
        assert new_reg['allowed'] is False
        assert new_reg['disable_reason']['code'] == reason
    else:
        assert new_reg['allowed'] is True
        assert 'disable_reason' not in new_reg


class TestLaunchCargoCorpResponse:
    @pytest.mark.config(CARGO_CORP_TAXI_AT_LAUNCH_ENABLED=False)
    @pytest.mark.config(CARGO_CORP_FRONT_FIX_AT_LAUNCH_ENABLED=True)
    async def test_cargo_corp_front_fix(
            self,
            launch_response_ok,
            get_flow_phoenix_state,
            get_cargo_corp_list,
    ):
        get_flow_phoenix_state.set_response_details(tickets=[])
        get_cargo_corp_list.set_ok_response(corp_clients=[])

        tickets, _, errors, new_reg = get_response_phoenix_parts(
            await launch_response_ok(),
        )
        assert tickets == []
        assert errors is None
        assert new_reg['disable_reason']['code'] == 'unbound_phone_number'

    @pytest.mark.parametrize(
        'cargo_corp_clients', [CARGO_CORP_LIST_RESPONSE, []],
    )
    async def test_cargo_corp_ok(
            self, launch_response_ok, get_cargo_corp_list, cargo_corp_clients,
    ):
        get_cargo_corp_list.set_ok_response(corp_clients=cargo_corp_clients)

        companies, errors, _ = get_response_corp_parts(
            await launch_response_ok(),
        )
        assert_cargos_in_lauch_response(cargo_corp_clients, companies)
        assert errors is None

    async def test_no_cargo_corps(
            self, launch_response_ok, get_cargo_corp_list,
    ):
        get_cargo_corp_list.set_response_by_code(response_code=404)

        companies, errors, _ = get_response_corp_parts(
            await launch_response_ok(),
        )
        for corp_client in companies:
            assert corp_client['source'] != 'cargo'
        assert errors is None

    async def test_fail_cargo_corp(
            self, launch_response_ok, get_cargo_corp_list,
    ):
        get_cargo_corp_list.set_response_by_code(response_code=500)

        companies, errors, _ = get_response_corp_parts(
            await launch_response_ok(),
        )
        for corp_client in companies:
            assert corp_client['source'] != 'cargo'
        assert 'retry_due_cargo_corp_error' in get_error_codes(errors)

    @pytest.mark.parametrize(
        'cargo_corp_code, expected_times_called',
        [(200, 1), (404, 1), (500, 2)],
    )
    async def test_cargo_corp_cache(
            self,
            request_launch,
            get_cargo_corp_list,
            cargo_corp_code,
            expected_times_called,
    ):
        get_cargo_corp_list.set_response_by_code(response_code=cargo_corp_code)

        for _ in range(2):
            await request_launch()

        assert get_cargo_corp_list.times_called == expected_times_called


class TestLaunchTaxiCorpResponse:
    async def test_taxi_corp_ok(self, launch_response_ok):
        companies, errors, new_offer_reg = get_response_corp_parts(
            await launch_response_ok(),
        )
        assert companies == [
            {
                'id': utils.CORP_CLIENT_ID,
                'name': 'Ромашки и цветы',
                'source': 'taxi',
                'is_registration_finished': True,
            },
        ]
        assert errors is None
        assert_reg(new_offer_reg, 'another_ya_acc_due_limit')

    async def test_no_taxi_corp(
            self, launch_response_ok, get_taxi_corp_id, get_taxi_corp_info,
    ):
        get_taxi_corp_id.set_response_by_code(response_code=404)

        companies, errors, new_offer_reg = get_response_corp_parts(
            await launch_response_ok(),
        )
        assert companies == []
        assert errors is None
        assert_reg(new_offer_reg)

        assert get_taxi_corp_info.times_called == 0

    @pytest.mark.config(CARGO_CORP_TAXI_AT_LAUNCH_ENABLED=False)
    async def test_no_taxi_corp_due_config(
            self, launch_response_ok, get_taxi_corp_id, get_taxi_corp_info,
    ):
        companies, errors, new_offer_reg = get_response_corp_parts(
            await launch_response_ok(),
        )
        assert companies == []
        assert errors is None
        assert_reg(new_offer_reg)

        assert get_taxi_corp_id.times_called == 0
        assert get_taxi_corp_info.times_called == 0

    async def test_fail_taxi_corp_id(
            self, launch_response_ok, get_taxi_corp_id, get_taxi_corp_info,
    ):
        get_taxi_corp_id.set_response_by_code(response_code=500)

        companies, errors, new_offer_reg = get_response_corp_parts(
            await launch_response_ok(),
        )
        assert companies == []
        assert 'retry_due_taxi_corp_error' in get_error_codes(errors)
        assert_reg(new_offer_reg, 'retry_due_taxi_corp_error')

        assert get_taxi_corp_info.times_called == 0

    @pytest.mark.parametrize('taxi_corp_info_code', [400, 404, 500])
    async def test_fail_taxi_corp_info(
            self, launch_response_ok, get_taxi_corp_info, taxi_corp_info_code,
    ):
        get_taxi_corp_info.set_response_by_code(
            response_code=taxi_corp_info_code,
        )

        companies, errors, new_offer_reg = get_response_corp_parts(
            await launch_response_ok(),
        )
        assert companies == []
        assert 'retry_due_taxi_corp_error' in get_error_codes(errors)
        assert_reg(new_offer_reg, 'retry_due_taxi_corp_error')

    @pytest.mark.parametrize(
        'taxi_corp_id_code, expected_times_called',
        [(200, 1), (404, 1), (500, 6)],
    )
    async def test_taxi_corp_cache(
            self,
            request_launch,
            get_taxi_corp_id,
            taxi_corp_id_code,
            expected_times_called,
    ):
        get_taxi_corp_id.set_response_by_code(response_code=taxi_corp_id_code)

        for _ in range(2):
            await request_launch()

        assert get_taxi_corp_id.times_called == expected_times_called


class TestLaunchCargoCrmResponse:
    async def test_cargo_crm_no_auth(
            self, launch_response_ok, get_flow_phoenix_state,
    ):
        tickets, pasport_acc, errors, new_reg = get_response_phoenix_parts(
            await launch_response_ok(yandex_uid=None),
        )
        assert tickets == []
        assert pasport_acc is None
        assert errors is None
        assert_reg(new_reg, 'unauthenticated')

        assert get_flow_phoenix_state.times_called == 0

    async def test_cargo_crm_ok_with_tickets(
            self, launch_response_ok, get_flow_phoenix_state,
    ):
        tickets, pasport_acc, errors, new_reg = get_response_phoenix_parts(
            await launch_response_ok(),
        )
        assert tickets == [{'ticket_id': 'afcc418a22ba449f96c817e48afa4150'}]
        assert pasport_acc == {
            'yandex_uid': utils.YANDEX_UID,
            'details': utils.PASSPORT_ACCOUNT,
        }
        assert errors is None
        assert_reg(new_reg, 'has_unresolved_tickets')

    async def test_cargo_crm_ok_no_tickets(
            self, launch_response_ok, get_flow_phoenix_state,
    ):
        get_flow_phoenix_state.set_response_details(tickets=[])

        tickets, pasport_acc, errors, new_reg = get_response_phoenix_parts(
            await launch_response_ok(),
        )
        assert tickets == []
        assert pasport_acc == {
            'yandex_uid': utils.YANDEX_UID,
            'details': utils.PASSPORT_ACCOUNT,
        }
        assert errors is None
        assert_reg(new_reg)

    async def test_fail_cargo_crm(
            self, launch_response_ok, get_flow_phoenix_state,
    ):
        get_flow_phoenix_state.set_response(response_code=500)

        tickets, pasport_acc, errors, new_reg = get_response_phoenix_parts(
            await launch_response_ok(),
        )
        assert tickets == []
        assert pasport_acc == {
            'yandex_uid': utils.YANDEX_UID,
            'details': {'phones': []},
        }
        assert 'retry_due_cargo_crm_error' in get_error_codes(errors)
        assert_reg(new_reg, 'retry_due_cargo_crm_error')


class TestLaunchFallbackNewCargoCorpAppearance:
    @pytest.fixture
    def launch_response_companies(
            self,
            launch_response_ok,
            get_taxi_corp_id,
            get_cargo_corp_list,
            get_flow_phoenix_state,
    ):
        async def wrapper(cargo_corp_clients, extra_corp_client_id):
            ticket = {'ticket_id': 'ticket_id'}
            if extra_corp_client_id:
                ticket['corp_client_id'] = extra_corp_client_id
            get_flow_phoenix_state.set_response_details(tickets=[ticket])

            get_taxi_corp_id.set_response_by_code(response_code=404)
            get_cargo_corp_list.set_ok_response(
                corp_clients=cargo_corp_clients,
            )

            companies, errors, _ = get_response_corp_parts(
                await launch_response_ok(),
            )

            assert_cargos_in_lauch_response(cargo_corp_clients, companies)
            assert errors is None

            return companies

        return wrapper

    async def test_fallback_activated(self, launch_response_companies):
        cargo_corp_clients = CARGO_CORP_LIST_RESPONSE
        extra_corp_client_id = 'new_corp_client_id'

        companies = await launch_response_companies(
            cargo_corp_clients, extra_corp_client_id,
        )

        assert len(companies) == len(cargo_corp_clients) + 1
        assert_cargos_in_lauch_response(cargo_corp_clients, companies)

        assert {
            'source': 'cargo',
            'id': 'new_corp_client_id',
            'name': 'Новая компания',
            'is_registration_finished': False,
        } in companies

    @pytest.mark.parametrize(
        'extra_corp_client_id',
        [
            pytest.param(
                CARGO_CORP_LIST_RESPONSE[0]['id'],
                id='id already exists in list',
            ),
            pytest.param(None, id='no corp_client_id'),
        ],
    )
    async def test_fallback_not_activated(
            self, launch_response_companies, extra_corp_client_id,
    ):
        cargo_corp_clients = CARGO_CORP_LIST_RESPONSE

        companies = await launch_response_companies(
            cargo_corp_clients, extra_corp_client_id,
        )

        assert len(companies) == len(cargo_corp_clients)
