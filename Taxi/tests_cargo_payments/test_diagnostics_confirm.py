import datetime

import pytest
import pytz

DIAGNOSTICS_TAG = {'name': 'postpayment_diagnostics'}


@pytest.fixture(name='get_performer_diagnostics')
async def _get_performer_diagnostics(pgsql):
    def wrapper(park_id, driver_id):
        cursor = pgsql['cargo_payments'].dict_cursor()
        cursor.execute(
            """
            SELECT
                diagnostics_ts,
                diagnostics_result,
                diagnostics_tags_version
            FROM cargo_payments.performer_agents
            WHERE park_id=%s AND driver_id=%s
            """,
            (park_id, driver_id),
        )

        result = [dict(row) for row in cursor]
        if not result:
            return None
        return result[0]

    return wrapper


@pytest.mark.parametrize('is_diagnostics_passed', [True, False])
@pytest.mark.now('2021-01-01T00:00:00Z')
async def test_diagnostics_passed(
        state_performer_found,
        mocked_time,
        confirm_diagnostics,
        get_performer_diagnostics,
        is_diagnostics_passed: bool,
):
    """
        Check diagnostics flag is set/removed on confirm.
    """
    now = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=pytz.utc)
    mocked_time.set(now)

    state = await state_performer_found()

    await confirm_diagnostics(
        is_diagnostics_passed=is_diagnostics_passed, has_nfc=False,
    )

    diagnostics = get_performer_diagnostics(
        state.performer.park_id, state.performer.driver_id,
    )
    assert diagnostics['diagnostics_ts'] == now  # check timestamp updated
    assert diagnostics['diagnostics_result'] == {
        'is_passed': is_diagnostics_passed,
        'has_nfc': False,
        'has_nfc_enabled': True,
        'user_agent': 'Taximeter 9.40',
    }
    assert diagnostics['diagnostics_tags_version'] == 1


@pytest.mark.parametrize('is_diagnostics_passed', [True, False])
async def test_stq_arguments(
        state_performer_found,
        confirm_diagnostics,
        stq,
        is_diagnostics_passed: bool,
        idempotency_token='idempotency_token_1',
):
    """
        Check cargo_payments_update_driver_tags was set with right parameters.
    """
    state = await state_performer_found()

    stq.cargo_payments_update_driver_tags.flush()
    await confirm_diagnostics(
        is_diagnostics_passed=is_diagnostics_passed,
        idempotency_token=idempotency_token,
        has_nfc=False,
    )
    # stq was called
    assert stq.cargo_payments_update_driver_tags.times_called == 1

    kwargs = stq.cargo_payments_update_driver_tags.next_call()['kwargs']
    kwargs.pop('log_extra', None)

    assert kwargs == {
        'park_id': state.performer.park_id,
        'driver_id': state.performer.driver_id,
        'diagnostics_tags_version': 1,
    }


@pytest.mark.parametrize('expect_upload_tags', [False, True])
async def test_diagnostics_before_registration(
        state_agent_pulls_initailized,
        confirm_diagnostics,
        exp_cargo_payments_diagnostics_tags,
        driver_headers,
        get_performer_diagnostics,
        stq,
        expect_upload_tags,
):
    """
        Diagnostics may be called before driver is registered
        in ibox, this is OK.
        For couriers with link only registration in ibox is not needed.
    """
    await state_agent_pulls_initailized()

    park_id = driver_headers['X-YaTaxi-Park-Id']
    driver_id = driver_headers['X-YaTaxi-Driver-Profile-Id']

    stq.cargo_payments_update_driver_tags.flush()
    await exp_cargo_payments_diagnostics_tags(enabled=expect_upload_tags)
    await confirm_diagnostics()

    diagnostics = get_performer_diagnostics(park_id, driver_id)
    assert diagnostics['diagnostics_result'] == {
        'is_passed': True,
        'has_nfc': True,
        'has_nfc_enabled': True,
        'user_agent': 'Taximeter 9.40',
    }
    # stq was called
    if expect_upload_tags:
        assert stq.cargo_payments_update_driver_tags.times_called == 1
    else:
        assert stq.cargo_payments_update_driver_tags.times_called == 0


async def test_diagnostics_before_registration_fix(
        state_agent_pulls_initailized,
        confirm_diagnostics,
        driver_headers,
        get_performer_diagnostics,
        state_context,
        exp_cargo_payments_agent_creator,
):
    """
        Diagnostics may be called before driver is registered
        in ibox, this is OK.
        But for taximeters 9.76, 9.77 diagnostics is called
        even when it is not expected with trash result (
        with every check passed even when it is not).
        We still store it and set tags but only after agent
        is registered in ibox.
    """
    await state_agent_pulls_initailized()
    await exp_cargo_payments_agent_creator(
        virtual_client_id=state_context.virtual_client_id,
        min_diagnostics_user_agent='9.78',
    )

    park_id = driver_headers['X-YaTaxi-Park-Id']
    driver_id = driver_headers['X-YaTaxi-Driver-Profile-Id']

    await confirm_diagnostics(status_code=409)

    diagnostics = get_performer_diagnostics(park_id, driver_id)
    assert not diagnostics
