"""
    Describe here happy path target states.
"""

import dataclasses
import typing as tp

import pytest

DEFAULT_VIRTUAL_CLIENT_ID = '07e65253-1b77-4872-b994-fd8d13c2294f'
EATS_VIRTUAL_CLIENT_ID = 'f7cc2fd6-78e3-4e97-9e64-9143d7613d45'


@dataclasses.dataclass
class Agent:
    login: str
    secret_key: str
    pin_code: str


@dataclasses.dataclass
class Performer:
    park_id: str
    driver_id: str
    agent: tp.Optional[Agent] = None


# contains current state info
@dataclasses.dataclass
class CurrentState:
    payment_id: tp.Optional[str] = None
    performer: tp.Optional[Performer] = None

    eats_virtual_client_id: str = EATS_VIRTUAL_CLIENT_ID
    default_virtual_client_id: str = DEFAULT_VIRTUAL_CLIENT_ID

    eats_token = b'default@eats:234234234'
    deafult_token = b'default@yandex:234234234'


@pytest.fixture(name='state_context')
async def _state_context(mock_web_api_agent_create, mock_web_api_agent_update):
    """
        Usage:
            1) Add field to Context.
            2) Add behavior by field in Context
            3) Override context by calling custom_context first
    """

    # overrides default behaviour of state fixtures
    @dataclasses.dataclass
    class Context:
        virtual_client_id: str
        supplier_inn: str
        is_diagnostics_confirmed: bool
        agent_type: str

        def use_eats_client(self, eats_token=b'default@eats:234234234'):
            self.virtual_client_id = EATS_VIRTUAL_CLIENT_ID
            mock_web_api_agent_create.expected_token = eats_token
            mock_web_api_agent_update.expected_token = eats_token

    context = Context(
        virtual_client_id=DEFAULT_VIRTUAL_CLIENT_ID,
        supplier_inn='9705114405',
        is_diagnostics_confirmed=False,
        agent_type=None,
    )

    return context


# fake state (creates State object)
@pytest.fixture(name='current_state')
async def _current_state():
    state = CurrentState()

    return state


@pytest.fixture(name='state_configs_set')
async def _state_configs_set(current_state, setup_virtual_clients_settings):
    async def wrapper(**kwargs):
        await setup_virtual_clients_settings(**kwargs)

        return current_state

    return wrapper


# virtual_clients registered
@pytest.fixture(name='state_virtual_client_created')
async def _state_virtual_client_created(state_configs_set, add_virtual_client):
    async def wrapper(**kwargs):
        state = await state_configs_set(**kwargs)

        state.default_virtual_client_id = add_virtual_client(
            virtual_client_id=DEFAULT_VIRTUAL_CLIENT_ID,
        )
        state.eats_virtual_client_id = add_virtual_client(
            virtual_client_id=EATS_VIRTUAL_CLIENT_ID,
        )

        return state

    return wrapper


# virtual_clients registered
@pytest.fixture(name='state_tid_pulls_initialized')
async def _state_tid_pulls_initialized(state_virtual_client_created, add_tid):
    async def wrapper(**kwargs):
        state = await state_virtual_client_created(**kwargs)
        add_tid(tid='1111', virtual_client_id=DEFAULT_VIRTUAL_CLIENT_ID)
        add_tid(tid='1112', virtual_client_id=DEFAULT_VIRTUAL_CLIENT_ID)
        add_tid(tid='ya.eda', virtual_client_id=EATS_VIRTUAL_CLIENT_ID)
        state.default_tids = {'1111', '1112'}
        state.eats_tids = {'ya.eda'}
        return state

    return wrapper


# agent login generator initilized
@pytest.fixture(name='state_agent_pulls_initailized')
async def _state_agent_pulls_initailized(
        state_tid_pulls_initialized,
        init_agents_pull,
        exp_cargo_payments_agent_creator,
        state_context,
):
    async def wrapper(**kwargs):
        state = await state_tid_pulls_initialized(**kwargs)

        init_agents_pull()
        await exp_cargo_payments_agent_creator(
            virtual_client_id=state_context.virtual_client_id,
        )

        return state

    return wrapper


# state agents created
@pytest.fixture(name='state_agents_created')
async def _state_agents_created(
        state_context,
        state_agent_pulls_initailized,
        register_special_agents,
        register_agent,
        confirm_diagnostics,
        mock_web_api_agent_create,
):
    async def wrapper(**kwargs):
        state = await state_agent_pulls_initailized(**kwargs)

        register_special_agents()
        await register_agent()
        if state_context.is_diagnostics_confirmed:
            await confirm_diagnostics()

        mock_web_api_agent_create.ibox_id = 11112
        await register_agent(park_id='parkid2', driver_id='driverid2')
        if state_context.is_diagnostics_confirmed:
            await confirm_diagnostics(park_id='parkid2', driver_id='driverid2')

        return state

    return wrapper


@pytest.fixture(name='state_payment_created')
async def _state_payment_created(
        state_agents_created, create_payment, get_payment, state_context,
):
    async def wrapper(*, virtual_client_id=None, **kwargs):
        if not virtual_client_id:
            virtual_client_id = state_context.virtual_client_id

        state = await state_agents_created(**kwargs)
        payment = await create_payment(
            supplier_inn=state_context.supplier_inn,
            virtual_client_id=virtual_client_id,
            agent_type=state_context.agent_type,
            **kwargs,
        )
        state.payment_id = payment['payment_id']
        state.payment_revision = payment['revision']

        return state

    return wrapper


@pytest.fixture(name='state_performer_found')
async def _state_performer_found(
        state_payment_created,
        create_payment,
        get_agent_info,
        set_payment_performer,
):
    async def wrapper(**kwargs):
        state = await state_payment_created(**kwargs)

        state.performer = Performer(park_id='parkid1', driver_id='driverid1')

        await set_payment_performer(
            payment_id=state.payment_id,
            park_id=state.performer.park_id,
            driver_id=state.performer.driver_id,
        )

        agent = await get_agent_info(
            park_id=state.performer.park_id,
            driver_id=state.performer.driver_id,
        )
        ibox = agent['ibox']

        state.performer.agent = Agent(
            login=ibox['login'],
            secret_key=ibox['secret_code'],
            pin_code=ibox['pin_code'],
        )

        return state

    return wrapper


@pytest.fixture(name='state_agent_unblocked')
async def _state_agent_unblocked(
        state_performer_found, stq_runner, get_payment_performer,
):
    async def wrapper(**kwargs):
        state = await state_performer_found(**kwargs)

        await stq_runner.cargo_payments_sync_performer_agent.call(
            task_id='test',
            kwargs={
                'payment_id': state.payment_id,
                'park_id': state.performer.park_id,
                'driver_id': state.performer.driver_id,
                'performer_version': 0,
            },
        )
        return state

    return wrapper


@pytest.fixture(name='state_payment_confirmed')
async def _state_payment_confirmed(
        state_agent_unblocked, state_virtual_client_created, confirm_payment,
):
    async def wrapper(payment_method='card', **kwargs):
        state = await state_agent_unblocked(**kwargs)
        await confirm_payment(
            payment_id=state.payment_id,
            revision=state.payment_revision,
            paymethod=payment_method,
        )
        return state

    return wrapper


@pytest.fixture(name='state_payment_authorized')
async def _state_payment_authorized(
        state_payment_confirmed,
        run_operations_executor,
        taxi_cargo_payments,
        load_json_var,
        get_payment,
        get_payment_amount,
):
    async def wrapper(payment_method='card', **kwargs):
        state = await state_payment_confirmed(
            payment_method=payment_method, **kwargs,
        )

        payment_amount = await get_payment_amount(state.payment_id)
        response = await taxi_cargo_payments.post(
            '2can/status',
            json=load_json_var(
                'pay_event.json',
                payment_id=state.payment_id,
                amount=str(payment_amount),
            ),
        )
        assert response.status_code == 200
        await run_operations_executor()

        payment = await get_payment(state.payment_id)
        state.payment_revision = payment['revision']
        assert payment['status'] == 'authorized'

        return state

    return wrapper


@pytest.fixture(name='state_payment_finished')
async def _state_payment_finished(
        state_payment_authorized,
        taxi_cargo_payments,
        load_json_var,
        get_payment,
):
    async def wrapper(payment_method='card', **kwargs):
        state = await state_payment_authorized(
            payment_method=payment_method, **kwargs,
        )

        response = await taxi_cargo_payments.post(
            '2can/status',
            json=load_json_var(
                'fiscal_event.json', payment_id=state.payment_id, amount='40',
            ),
        )

        assert response.status_code == 200

        payment = await get_payment(state.payment_id)
        state.payment_revision = payment['revision']
        assert payment['status'] == 'finished'

        return state

    return wrapper


@pytest.fixture(name='register_special_agents')
async def _register_special_agents(pgsql):
    def wrapper():
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            """
            INSERT INTO cargo_payments.agents (
                virtual_client_id,
                partner_login, secret_code, pin_code,
                agent_password, ibox_id)
            VALUES (
                %s,
                'default@yandex',
                'sJHaDdflv3k0ROrVRqzp3AnQ+cCGaLXliF7Gzp6zU/0=', -- 123123123
                '000000',
                'ylcwmgp3NfykjMz6X7ZcW1YW6Z9ouPdRQJGIn2cVo2k=', -- 234234234
                12345),
                (
                %s,
                'default@eats',
                'sJHaDdflv3k0ROrVRqzp3AnQ+cCGaLXliF7Gzp6zU/0=', -- 123123123
                '000000',
                'ylcwmgp3NfykjMz6X7ZcW1YW6Z9ouPdRQJGIn2cVo2k=', -- 234234234
                54321)
            """,
            (DEFAULT_VIRTUAL_CLIENT_ID, EATS_VIRTUAL_CLIENT_ID),
        )

    return wrapper
