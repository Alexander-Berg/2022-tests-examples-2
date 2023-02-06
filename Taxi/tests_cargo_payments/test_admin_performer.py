import pytest

from testsuite.utils import matching


PARK_ID = 'parkid1'
DRIVER_ID = 'driverid1'

BLOCKING_TAG = 'cargo_postpayment_option_block'
DISABLED_TAG = 'cargo_postpayment_option_disabled'

DEFAULT_IDEMPOTENCY_TOKEN = 'idempotency_token_1'
DEFAULT_SUPPORT_COMMENT = 'comment_1'
DEFAULT_SUPPORT_TICKET = 'ticket_1'


@pytest.fixture(name='admin_performer_info')
async def _admin_performer_info(taxi_cargo_payments):
    async def wrapper(*, park_id=PARK_ID, driver_id=DRIVER_ID):
        response = await taxi_cargo_payments.post(
            'v1/admin/performer/info',
            params={
                'park_id': park_id,
                'driver_profile_id': driver_id,
                'Accept-Language': 'ru',
            },
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='admin_performer_action')
async def _admin_performer_action(taxi_cargo_payments):
    async def wrapper(
            actions,
            *,
            park_id=PARK_ID,
            driver_id=DRIVER_ID,
            idempotency_token=DEFAULT_IDEMPOTENCY_TOKEN,
            support_comment=DEFAULT_SUPPORT_COMMENT,
            support_ticket=DEFAULT_SUPPORT_TICKET,
    ):
        response = await taxi_cargo_payments.post(
            'v1/admin/performer/update',
            headers={'X-Idempotency-Token': idempotency_token},
            params={
                'park_id': park_id,
                'driver_profile_id': driver_id,
                'Accept-Language': 'ru',
            },
            json={
                'actions': actions,
                'comment': support_comment,
                'ticket': support_ticket,
            },
        )
        assert response.status_code == 200

    return wrapper


async def test_basic_info(
        admin_performer_info,
        state_agents_created,
        driver_tags_mocks,
        exp_cargo_payments_performer_diagnostics,
):
    """
        Check common fields.
    """
    await state_agents_created()
    driver_tags_mocks.set_tags_info(PARK_ID, DRIVER_ID, tags=[])

    response_body = await admin_performer_info()

    assert response_body == {
        'post_payment_status': 'Оплата при получении недоступна',
        'actions_history': [],
        'available_actions': [
            {
                'title': 'Заблокировать заказы с постоплатой',
                'type': 'block_from_orders',
            },
            {
                'title': 'Деактивировать агента ibox',
                'type': 'deactivate_agent',
            },
            {
                'title': 'Отключить заказы с постоплатой',
                'type': 'disable_post_payment',
            },
        ],
        'ibox': {
            'auth': {
                'login': matching.any_string,
                'pin_code': '000000',
                'secret_code': matching.any_string,
            },
            'status': 'Активен',
        },
        'is_blocked_from_orders': False,
        'is_post_payment_disabled': False,
        'postpayment_tags': [],
    }


async def test_unknown_agent(
        admin_performer_info,
        state_agents_created,
        exp_cargo_payments_performer_diagnostics,
):
    """
        Check behaviour for unregistered in payments couriers.
    """
    await state_agents_created()
    response_body = await admin_performer_info(driver_id='unknown')

    assert response_body['ibox'] == {}
    assert not response_body['available_actions']


async def test_agent_deactivated(
        admin_performer_info,
        state_agents_created,
        mock_web_api_agent_list,
        exp_cargo_payments_performer_diagnostics,
):
    """
        Check activate_agent action.
    """
    await state_agents_created()
    mock_web_api_agent_list.is_active = False

    response_body = await admin_performer_info()

    assert {
        'title': 'Активировать агента ibox',
        'type': 'activate_agent',
    } in response_body['available_actions']


async def test_tags_actions(
        admin_performer_info,
        state_agents_created,
        driver_tags_mocks,
        exp_cargo_payments_performer_diagnostics,
):
    """
        Check different available actions in the case driver
        has specific tags.
    """
    await state_agents_created()
    driver_tags_mocks.set_tags_info(
        PARK_ID, DRIVER_ID, tags=[BLOCKING_TAG, DISABLED_TAG],
    )

    response_body = await admin_performer_info()

    assert response_body['available_actions'] == [
        {
            'title': 'Разблокировать заказы с постоплатой',
            'type': 'unblock_from_orders',
        },
        {'title': 'Деактивировать агента ibox', 'type': 'deactivate_agent'},
        {
            'title': 'Включить заказы с постоплатой',
            'type': 'enable_post_payment',
        },
    ]
    assert response_body['is_blocked_from_orders']
    assert response_body['is_post_payment_disabled']
    assert response_body['postpayment_tags'] == [
        {'name': BLOCKING_TAG},
        {'name': DISABLED_TAG},
    ]


@pytest.mark.skip()
async def test_action_with_comment(
        admin_performer_info,
        admin_performer_action,
        state_agents_created,
        exp_cargo_payments_performer_diagnostics,
):
    """
        Check actions applied, and it is shown in actions_history.
    """
    await state_agents_created()

    await admin_performer_action(
        actions=['deactivate_agent', 'block_from_orders'],
    )

    response_body = await admin_performer_info()

    assert response_body['actions_history'] == [
        {
            'action': 'deactivate_agent',
            'comment': 'comment_1',
            'source': 'support',
            'status': 'Ожидается выполнение',
            'ticket': 'ticket_1',
            'title': 'Деактивировать агента ibox',
        },
        {
            'action': 'block_from_orders',
            'comment': 'comment_1',
            'source': 'support',
            'status': 'Ожидается выполнение',
            'ticket': 'ticket_1',
            'title': 'Заблокировать заказы с постоплатой',
        },
    ]


@pytest.mark.skip()
async def test_action_without_comment(
        admin_performer_info,
        admin_performer_action,
        state_agents_created,
        exp_cargo_payments_performer_diagnostics,
):
    """
        Check action without audit.
    """
    await state_agents_created()

    await admin_performer_action(
        actions=['deactivate_agent', 'block_from_orders'],
    )

    response_body = await admin_performer_info()

    assert response_body['actions_history'] == [
        {
            'action': 'deactivate_agent',
            'comment': 'comment_1',
            'source': 'support',
            'status': 'Ожидается выполнение',
            'ticket': 'ticket_1',
            'title': 'Деактивировать агента ibox',
        },
        {
            'action': 'block_from_orders',
            'comment': 'comment_1',
            'source': 'support',
            'status': 'Ожидается выполнение',
            'ticket': 'ticket_1',
            'title': 'Заблокировать заказы с постоплатой',
        },
    ]


@pytest.mark.skip()
async def test_action_idempotency(
        admin_performer_info,
        admin_performer_action,
        state_agents_created,
        exp_cargo_payments_performer_diagnostics,
):
    """
        Call twice with same idempotency_token, expected single update.
    """
    await state_agents_created()

    for _ in range(2):
        await admin_performer_action(
            actions=['deactivate_agent', 'block_from_orders'],
        )

    response_body = await admin_performer_info()

    assert len(response_body['actions_history']) == 2
