import uuid

import pytest


_BLOCKING_TAG = 'cargo_payments_antifraud_block'


@pytest.fixture(name='call_antifraud_stq')
async def _call_antifraud_stq(stq_runner, testpoint):
    async def _wrapper(
            *, history_event_id: int, expected_testpoint: str = 'none',
    ):
        @testpoint(expected_testpoint)
        def _testpoint(data):
            pass

        await stq_runner.cargo_payments_transaction_antifraud.call(
            task_id='test',
            kwargs={'transaction_history_event_id': history_event_id},
        )

        if expected_testpoint != 'none':
            assert _testpoint.has_calls

    return _wrapper


@pytest.fixture(name='add_transaction')
async def _add_transaction(pgsql):
    def wrapper(
            *,
            payment_id,
            client_id=12345,
            transaction_id='UNUSED',
            partner_login,
    ):
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            """
                INSERT INTO cargo_payments.transactions
                (payment_id, transaction_id, currency, amount,
                partner_login, ibox_client_id, rrn, history_user_id,
                history_action)
                VALUES (%s, %s, 'RUB', '10.0', %s,
                    %s, 'rrn1', 'history-user', 'add')
                RETURNING history_event_id
            """,
            (payment_id, transaction_id, partner_login, client_id),
        )
        return cursor.fetchone()[0]

    return wrapper


@pytest.fixture(name='state_one_payment_finished')
async def _state_one_payment_finished(state_payment_authorized):
    async def wrapper(**kwargs):
        state = await state_payment_authorized(**kwargs)

        return state

    return wrapper


async def test_ok(
        state_one_payment_finished, call_antifraud_stq, add_transaction,
):
    """
        Check everything is ok.
    """
    state = await state_one_payment_finished()

    history_event_id = add_transaction(
        payment_id=state.payment_id, partner_login=state.performer.agent.login,
    )

    await call_antifraud_stq(history_event_id=history_event_id)


async def test_transaction_without_payment(
        state_one_payment_finished, call_antifraud_stq, add_transaction,
):
    """
        Check for 'transaction_without_payment' event.
    """
    state = await state_one_payment_finished()

    history_event_id = add_transaction(
        payment_id=str(uuid.uuid4()),
        partner_login=state.performer.agent.login,
    )

    await call_antifraud_stq(
        history_event_id=history_event_id,
        expected_testpoint='transaction_without_payment',
    )


async def test_transaction_without_performer(
        state_payment_created, call_antifraud_stq, add_transaction,
):
    """
        Check for 'transaction_without_performer' event.
    """
    state = await state_payment_created()

    history_event_id = add_transaction(
        payment_id=state.payment_id, partner_login='unknown@login',
    )

    await call_antifraud_stq(
        history_event_id=history_event_id,
        expected_testpoint='transaction_without_performer',
    )


async def test_transaction_by_wrong_agent(
        state_performer_found,
        call_antifraud_stq,
        add_transaction,
        get_agent_info,
):
    """
        Check for 'transaction_by_wrong_agent' event.
    """
    state = await state_performer_found()

    agent = await get_agent_info(park_id='parkid2', driver_id='driverid2')

    history_event_id = add_transaction(
        payment_id=state.payment_id, partner_login=agent['ibox']['login'],
    )

    await call_antifraud_stq(
        history_event_id=history_event_id,
        expected_testpoint='transaction_by_wrong_agent',
    )


def _config(*, limit_total=15, limit_canceled=5, block_events=None):
    config = {
        'enabled': True,
        'block_events': [],
        'activity_check': {
            'enabled': True,
            'limit_total': limit_total,
            'limit_canceled': limit_canceled,
            'check_interval_hours': 24,
        },
        'blocking_tag': _BLOCKING_TAG,
    }
    if block_events is not None:
        config['block_events'] = block_events
    return config


@pytest.mark.config(CARGO_PAYMENTS_ANTIFRAUD_PAYMENTS=_config(limit_total=0))
async def test_total_payment_limit(
        state_payment_authorized, call_antifraud_stq, add_transaction,
):
    """
        Check for too many payments by performer.
    """
    state = await state_payment_authorized()

    history_event_id = add_transaction(
        payment_id=state.payment_id, partner_login=state.performer.agent.login,
    )

    await call_antifraud_stq(
        history_event_id=history_event_id,
        expected_testpoint='total_payment_limit',
    )


@pytest.mark.config(
    CARGO_PAYMENTS_ANTIFRAUD_PAYMENTS=_config(limit_canceled=0),
)
async def test_payment_cancel_limit(
        state_performer_found,
        cancel_payment,
        call_antifraud_stq,
        add_transaction,
):
    """
        Check for too many cancels by performer.
    """
    state = await state_performer_found()
    await cancel_payment(payment_id=state.payment_id)

    history_event_id = add_transaction(
        payment_id=state.payment_id, partner_login=state.performer.agent.login,
    )

    await call_antifraud_stq(
        history_event_id=history_event_id,
        expected_testpoint='payment_cancel_limit',
    )


@pytest.mark.config(
    CARGO_PAYMENTS_ANTIFRAUD_PAYMENTS=_config(
        limit_total=0, block_events=['total_payment_limit'],
    ),
)
async def test_block(
        state_payment_authorized,
        call_antifraud_stq,
        add_transaction,
        mock_tags_upload,
        mock_web_api_agent_update,
):
    """
        Check agent block.
        1) ibox account deactivated
        2) cargo_payments_antifraud_block tag is added
    """
    state = await state_payment_authorized()

    history_event_id = add_transaction(
        payment_id=state.payment_id, partner_login=state.performer.agent.login,
    )
    mock_web_api_agent_update.flush()
    await call_antifraud_stq(
        history_event_id=history_event_id,
        expected_testpoint='total_payment_limit',
    )

    assert mock_tags_upload.handler.times_called == 1
    tags_request = mock_tags_upload.requests[0].json
    assert tags_request == {
        'append': [
            {
                'entity_type': 'dbid_uuid',
                'tags': [
                    {'entity': 'parkid1_driverid1', 'name': _BLOCKING_TAG},
                ],
            },
        ],
        'provider_id': 'cargo-payments',
    }

    assert mock_web_api_agent_update.handler.times_called == 1
    assert mock_web_api_agent_update.last_request.json == {'State': 0}


# without tests:
# payment_without_performer
# transaction_without_performer_agent
# transaction_performer_unregistered
