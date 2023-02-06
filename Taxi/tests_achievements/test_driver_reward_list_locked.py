import pytest

from tests_achievements import utils

PATH = '/driver/v1/achievements/v1/reward/list'
PARK_ID = 'driver_db_id1'
DRIVER_ID = 'driver_uuid1'


@pytest.mark.pgsql('achievements_pg', files=['achievements.sql'])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'udid, expect_locked, expect_unlocked',
    [
        ('udid0', {'express', 'star'}, set()),
        ('udid1', {'star'}, {'express', 'covid_hero'}),
        ('udid2', {'express'}, set()),
        ('udid_courier', {'star'}, set()),
    ],
)
async def test_driver_reward_list_locked(
        taxi_achievements,
        unique_drivers,
        driver_ui_profile_mock,
        driver_tags_mocks,
        udid,
        expect_locked,
        expect_unlocked,
):
    driver_ui_response = (
        {
            'display_mode': 'courier',
            'display_profile': 'eats_courier_pedestrian',
        }
        if udid == 'udid_courier'
        else {'display_mode': 'orders', 'display_profile': 'orders'}
    )

    driver_ui_profile_mock.set_response(driver_ui_response)

    unique_drivers.set_unique_driver(PARK_ID, DRIVER_ID, udid)
    request_data = utils.prepare_rq(PATH, PARK_ID, DRIVER_ID)
    response = await taxi_achievements.post(**request_data)
    assert response.status_code == 200

    resp_body = response.json()
    locked_rewards = {
        reward['code']
        for reward in resp_body['rewards']
        if reward['level'] == 1 and reward['state'] == 'locked'
    }
    unlocked_rewards = {
        reward['code']
        for reward in resp_body['rewards']
        if reward['level'] == 1
        and reward['state'] in ('unlocked', 'unlocked-new')
    }

    assert locked_rewards == expect_locked
    assert unlocked_rewards == expect_unlocked

    assert driver_ui_profile_mock.v1_mode_get.times_called == 1
    assert driver_tags_mocks.v1_match_profile.times_called == 1


@pytest.mark.pgsql('achievements_pg', files=['achievements.sql'])
@pytest.mark.parametrize('driver_ui_profile_ok', (False, True))
async def test_driver_reward_list_locked_not_found(
        taxi_achievements,
        unique_drivers,
        driver_ui_profile_mock,
        driver_tags_mocks,
        driver_ui_profile_ok,
):
    if driver_ui_profile_ok:
        driver_ui_profile_mock.set_response(
            {
                'display_mode': 'courier',
                'display_profile': 'eats_couriers_pedestrian',
            },
        )

    unique_drivers.set_unique_driver(PARK_ID, DRIVER_ID, 'udid3')
    request_data = utils.prepare_rq(PATH, PARK_ID, DRIVER_ID)
    response = await taxi_achievements.post(**request_data)
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['rewards'] == []
    assert resp_body['category_ordering'] == []

    assert driver_ui_profile_mock.v1_mode_get.times_called == 1
    if driver_ui_profile_ok:
        assert driver_tags_mocks.v1_match_profile.times_called == 1


@pytest.mark.pgsql('achievements_pg', files=['achievements.sql'])
@pytest.mark.experiments3(
    name='achievements_show_locked_rewards',
    consumers=['achievements/reward_list'],
    default_value={'locked': []},
    clauses=[
        {
            'predicate': {
                'type': 'contains',
                'init': {
                    'arg_name': 'driver_tags',
                    'set_elem_type': 'string',
                    'value': 'super_driver_tag',
                },
            },
            'title': 'match by tag',
            'value': {'locked': ['top_fives']},
        },
    ],
    is_config=True,
)
@pytest.mark.driver_tags_match(
    dbid=PARK_ID, uuid=DRIVER_ID, tags=['super_driver_tag'],
)
async def test_driver_reward_list_locked_by_tags(
        taxi_achievements,
        unique_drivers,
        driver_ui_profile_mock,
        driver_tags_mocks,
):
    driver_ui_profile_mock.set_response(
        {'display_mode': 'orders', 'display_profile': 'orders'},
    )

    unique_drivers.set_unique_driver(PARK_ID, DRIVER_ID, 'udid3')
    request_data = utils.prepare_rq(PATH, PARK_ID, DRIVER_ID)
    response = await taxi_achievements.post(**request_data)
    assert response.status_code == 200

    resp_body = response.json()
    first_reward = resp_body['rewards'][0]
    assert first_reward['code'] == 'top_fives'
    assert first_reward['level'] == 1
    assert first_reward['state'] == 'locked'

    assert driver_ui_profile_mock.v1_mode_get.times_called == 1
    assert driver_tags_mocks.v1_match_profile.times_called == 1
