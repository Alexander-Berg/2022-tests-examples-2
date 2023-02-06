import re

import pytest

from testsuite.utils import matching


DEFAULT_RATE_LIMITS = {'limit': 1, 'burst': 2, 'interval': 1}


async def test_basic_ibox(
        state_performer_found, mock_driver_profiles_retrieve, register_agent,
):
    """
        Check ibox account info data.
    """
    state = await state_performer_found()

    response_body = await register_agent()
    assert response_body == {
        'ibox': {
            'login': state.performer.agent.login,
            'secret_code': state.performer.agent.secret_key,
            'pin_code': '000000',
        },
    }

    assert re.match(
        r'^\w{3}\d{3}@go.ya', response_body['ibox']['login'],
    ), response_body['ibox']['login']


async def test_ibox_request(
        state_performer_found,
        mock_web_api_agent_create,
        register_agent,
        driver_headers,
):
    """
        Check ibox create agent request fields.
    """
    state = await state_performer_found()

    assert mock_web_api_agent_create.handler.times_called == 2

    assert mock_web_api_agent_create.requests[0] == {
        'BranchID': 12345,
        'ClientID': 12345,
        'TID': '1111',
        'Email': state.performer.agent.login,
        'IP': driver_headers['X-Remote-IP'],
        'Lang': driver_headers['Accept-Language'],
        'Name': 'Курьер Я',
        'SecretKey': matching.RegexString(r'^\d{9}$'),
        'Password': matching.RegexString(r'^.{12}$'),
        'Phone': '+71234567890',
        'SendWelcomeEmail': False,
        'State': 1,
    }


async def test_registration_idempotency(
        state_performer_found, mock_driver_profiles_retrieve, register_agent,
):
    """
        Check ibox account is created only once.
    """
    state = await state_performer_found()
    mock_driver_profiles_retrieve.handler.flush()

    response_body = await register_agent()
    assert response_body == {
        'ibox': {
            'login': state.performer.agent.login,
            'secret_code': state.performer.agent.secret_key,
            'pin_code': '000000',
        },
    }
    assert mock_driver_profiles_retrieve.handler.times_called == 0


async def test_ibox_already_registered(
        state_performer_found,
        mock_web_api_agent_create,
        mock_web_api_agent_list,
        register_agent,
        driver_headers,
):
    """
        Check ibox agent is registered already (due to timeout).
    """
    mock_web_api_agent_create.with_pos = False

    state = await state_performer_found()

    assert (
        mock_web_api_agent_create.handler.times_called
        == mock_web_api_agent_list.handler.times_called
    )

    assert mock_web_api_agent_list.requests[0] == {
        'Email': state.performer.agent.login,
    }


async def test_stq_arguments(state_agents_created, register_agent, stq):
    """
        Check cargo_payments_update_driver_tags was set with right parameters.
    """
    await state_agents_created()

    # stq was called
    assert stq.cargo_payments_update_driver_tags.times_called == 2

    kwargs = stq.cargo_payments_update_driver_tags.next_call()['kwargs']
    kwargs.pop('log_extra', None)

    assert kwargs == {
        'park_id': 'parkid1',
        'driver_id': 'driverid1',
        'diagnostics_tags_version': 0,
    }


async def test_eats_ibox_account(
        state_performer_found,
        mock_driver_profiles_retrieve,
        exp_cargo_payments_agent_creator,
        mock_web_api_agent_create,
        register_agent,
        state_context,
):
    """
        Check eats ibox account succesfully registered.
    """
    state_context.use_eats_client()

    state = await state_performer_found()

    mock_web_api_agent_create.requests.clear()
    await register_agent(park_id='eatsparkid', driver_id='eatsdriverid')

    assert len(mock_web_api_agent_create.requests) == 1

    agent_request = mock_web_api_agent_create.requests[0]
    assert agent_request['BranchID'] == 54321
    assert agent_request['ClientID'] == 54321
    assert agent_request['TID'] in state.eats_tids


@pytest.mark.config(
    CARGO_PAYMENTS_IBOX_RATE_LIMITS={
        '/web-api-2can/api/v1/merchant/{merchant_id}/pos/create': (
            DEFAULT_RATE_LIMITS
        ),
    },
)
@pytest.mark.parametrize('expect_fail', [False, True])
async def test_rps_limiter_accounted(
        state_agent_pulls_initailized,
        mock_web_api_agent_create,
        rps_limiter,
        register_special_agents,
        register_agent,
        expect_fail: bool,
):
    """
        Check rps limiter accounted create requests
    """
    await state_agent_pulls_initailized()

    rps_limiter.set_budget(
        '/web-api-2can/api/v1/merchant/{merchant_id}/pos/create',
        0 if expect_fail else 2,
    )

    register_special_agents()
    await register_agent(expect_fail=expect_fail)

    assert (
        mock_web_api_agent_create.handler.times_called == 0
        if expect_fail
        else 1
    )
