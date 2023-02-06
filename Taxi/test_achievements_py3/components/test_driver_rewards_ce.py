import pytest

from achievements_py3.components.controllers import admin as admin_module
from achievements_py3.generated.web import web_context as context_module


@pytest.mark.parametrize(
    'udids, reward, expect_updated_udids',
    [
        (['udid1'], 'star', set()),
        (['udid1'], 'express', {'udid1'}),
        (['udid1', 'udid2'], 'star', {'udid2'}),
        (['udid1', 'udid2'], 'covid_hero', {'udid1'}),
        (['udid1', 'udid2', 'udid3'], 'covid_hero', {'udid1', 'udid3'}),
    ],
)
async def test_driver_rewards_ce_grant(
        web_context: context_module.Context,
        client_events_mocker,
        udids,
        reward,
        expect_updated_udids,
):
    ce_mock = client_events_mocker(
        expect_event='achievements_state', expect_udids=expect_updated_udids,
    )

    admin_controller: admin_module.Component = web_context.admin_controller
    updated_udids = await admin_controller.grant_many_driver_rewards(
        udids=udids, reward_code=reward, push_state_updated=True,
    )
    assert set(updated_udids) == expect_updated_udids

    assert ce_mock.pro_bulk_push.has_calls == bool(expect_updated_udids)


@pytest.mark.parametrize(
    'udids, reward, expect_updated_udids',
    [
        (['udid1'], 'express', set()),
        (['udid1'], 'star', {'udid1'}),
        (['udid1'], 'covid_hero', {'udid1'}),
        (['udid1', 'udid2'], 'star', {'udid1', 'udid2'}),
        (['udid1', 'udid2'], 'covid_hero', {'udid1', 'udid2'}),
        (['udid1', 'udid2', 'udid3'], 'express', {'udid2', 'udid3'}),
    ],
)
async def test_driver_rewards_ce_lock(
        web_context: context_module.Context,
        client_events_mocker,
        udids,
        reward,
        expect_updated_udids,
):
    ce_mock = client_events_mocker(
        expect_event='achievements_state', expect_udids=expect_updated_udids,
    )

    admin_controller: admin_module.Component = web_context.admin_controller
    updated_udids = await admin_controller.lock_many_driver_rewards(
        udids=udids, reward_code=reward, push_state_updated=True,
    )
    assert set(updated_udids) == expect_updated_udids

    assert ce_mock.pro_bulk_push.has_calls == bool(expect_updated_udids)


@pytest.mark.parametrize(
    'rewards, expect_updated_udids',
    [
        (['top_delivery'], set()),
        (['star'], {'udid1'}),
        (['express', 'star'], {'udid1'}),
        (['covid_hero'], {'udid2'}),
        (['covid_hero', 'express', 'star'], {'udid1', 'udid2'}),
    ],
)
async def test_driver_rewards_ce_drop_from_all(
        web_context: context_module.Context,
        client_events_mocker,
        rewards,
        expect_updated_udids,
):
    ce_mock = client_events_mocker(
        expect_event='achievements_state', expect_udids=expect_updated_udids,
    )

    admin_controller: admin_module.Component = web_context.admin_controller
    updated_count = await admin_controller.drop_rewards_from_all_drivers(
        reward_codes=rewards, push_state_updated=True,
    )
    assert updated_count == len(expect_updated_udids)

    assert ce_mock.pro_bulk_push.has_calls == bool(expect_updated_udids)


@pytest.mark.parametrize(
    'udids, expect_updated_udids',
    [
        (['bad_udid'], set()),
        (['udid1'], {'udid1'}),
        (['udid1', 'udid2'], {'udid1', 'udid2'}),
        (['udid1', 'udid2', 'udid3'], {'udid1', 'udid2'}),
    ],
)
async def test_driver_rewards_ce_drop_from_many(
        web_context: context_module.Context,
        client_events_mocker,
        udids,
        expect_updated_udids,
):
    ce_mock = client_events_mocker(
        expect_event='achievements_state', expect_udids=expect_updated_udids,
    )

    admin_controller: admin_module.Component = web_context.admin_controller
    updated_count = await admin_controller.drop_all_rewards_from_many(
        udids=udids, push_state_updated=True,
    )
    assert updated_count == len(expect_updated_udids)

    assert ce_mock.pro_bulk_push.has_calls == bool(expect_updated_udids)
