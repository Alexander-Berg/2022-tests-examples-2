import pytest

from tests_driver_mode_subscription import booking
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


DRIVER_PROFILE = driver.Profile('parkid1_uuid1')
NEXT_MODE = 'next_work_mode'
PREV_MODE = 'prev_work_mode'
_NEXT_MODE_SETTINGS = {'rule_id': 'next_rule_id'}
_PREV_MODE_SETTINGS = {'rule_id': 'prev_rule_id'}


def _make_key_params_mock(mockserver):
    @mockserver.json_handler('/driver-fix/v1/view/rule_key_params')
    async def _mock_view_offer(request):
        return {
            'rules': [
                {
                    'rule_id': 'next_rule_id',
                    'key_params': {
                        'tariff_zone': 'next_zone',
                        'subvention_geoarea': 'next_area',
                        'tag': 'next_tag',
                    },
                },
                {
                    'rule_id': 'prev_rule_id',
                    'key_params': {
                        'tariff_zone': 'prev_zone',
                        'subvention_geoarea': 'prev_area',
                        'tag': 'prev_tag',
                    },
                },
            ],
        }

    return _mock_view_offer


def _make_tags_mock(mockserver):
    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        return {'status': 'ok'}


def _make_tags_mock_failed(mockserver):
    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        return mockserver.make_response(status=500)


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name=NEXT_MODE, features={'geobooking': {}}),
            mode_rules.Patch(rule_name=PREV_MODE, features={}),
        ],
    ),
)
async def test_book_slot(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
):
    scene = scenario.Scene(
        profiles={
            DRIVER_PROFILE: driver.Mode(
                PREV_MODE, mode_settings=_PREV_MODE_SETTINGS,
            ),
        },
    )
    scene.setup(mockserver, mocked_time)
    _make_key_params_mock(mockserver)
    _make_tags_mock(mockserver)

    assert not booking.get_reservations(pgsql, DRIVER_PROFILE)

    await saga_tools.call_stq_saga_task(stq_runner, DRIVER_PROFILE)

    reservations = booking.get_reservations(pgsql, DRIVER_PROFILE)
    assert len(reservations) == 1
    assert reservations[0] == ('next_zone/next_area/next_tag',)


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'reservation.sql'],
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name=NEXT_MODE, features={}),
            mode_rules.Patch(rule_name=PREV_MODE, features={'geobooking': {}}),
        ],
    ),
)
async def test_cancel_reservation(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
):
    scene = scenario.Scene(profiles={DRIVER_PROFILE: driver.Mode(PREV_MODE)})
    scene.setup(mockserver, mocked_time)
    _make_key_params_mock(mockserver)
    _make_tags_mock(mockserver)

    reservations = booking.get_reservations(pgsql, DRIVER_PROFILE)
    assert len(reservations) == 1
    assert reservations[0] == ('prev_zone/prev_area/prev_tag',)

    await saga_tools.call_stq_saga_task(stq_runner, DRIVER_PROFILE)

    assert not booking.get_reservations(pgsql, DRIVER_PROFILE)


@pytest.mark.pgsql(
    'driver_mode_subscription',
    files=['sagas.sql'],
    queries=[
        booking.reserve(
            slot='prev_zone/prev_area/prev_tag', driver_profile=DRIVER_PROFILE,
        ),
    ],
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name=NEXT_MODE, features={'geobooking': {}}),
            mode_rules.Patch(rule_name=PREV_MODE, features={'geobooking': {}}),
        ],
    ),
)
async def test_book_another_slot(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
):
    scene = scenario.Scene(profiles={DRIVER_PROFILE: driver.Mode(PREV_MODE)})
    scene.setup(mockserver, mocked_time)
    _make_key_params_mock(mockserver)
    _make_tags_mock(mockserver)

    reservations = booking.get_reservations(pgsql, DRIVER_PROFILE)
    assert len(reservations) == 1
    assert reservations[0] == ('prev_zone/prev_area/prev_tag',)

    await saga_tools.call_stq_saga_task(stq_runner, DRIVER_PROFILE)

    reservations = booking.get_reservations(pgsql, DRIVER_PROFILE)
    assert len(reservations) == 1
    assert reservations[0] == ('next_zone/next_area/next_tag',)


@pytest.mark.pgsql(
    'driver_mode_subscription',
    files=['sagas.sql'],
    queries=[
        booking.reserve(
            slot='prev_zone/prev_area/prev_tag', driver_profile=DRIVER_PROFILE,
        ),
    ],
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name=NEXT_MODE, features={'geobooking': {}}),
            mode_rules.Patch(rule_name=PREV_MODE, features={'geobooking': {}}),
        ],
    ),
)
async def test_geobooking_context(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
):
    scene = scenario.Scene(profiles={DRIVER_PROFILE: driver.Mode(PREV_MODE)})
    scene.setup(mockserver, mocked_time)
    key_params_mock = _make_key_params_mock(mockserver)
    _make_tags_mock_failed(mockserver)

    await saga_tools.call_stq_saga_task(
        stq_runner, DRIVER_PROFILE, expect_fail=True,
    )

    assert key_params_mock.times_called == 1
    # remove call from queue
    key_params_mock.next_call()

    saga_context = saga_tools.get_saga_context(DRIVER_PROFILE, pgsql)

    assert saga_context['prev_mode']['subvention_key_params'] == {
        'subvention_geoarea': 'prev_area',
        'tag': 'prev_tag',
        'tariff_zone': 'prev_zone',
    }
    assert saga_context['next_mode']['subvention_key_params'] == {
        'subvention_geoarea': 'next_area',
        'tag': 'next_tag',
        'tariff_zone': 'next_zone',
    }

    _make_tags_mock(mockserver)

    await saga_tools.call_stq_saga_task(stq_runner, DRIVER_PROFILE)

    assert key_params_mock.times_called == 0
