import pytest

from tests_driver_mode_subscription import booking
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

DRIVER_PROFILE = driver.Profile('parkid1_uuid1')
DRIVER_PROFILE_2 = driver.Profile('parkid2_uuid2')
DRIVER_PROFILE_3 = driver.Profile('parkid3_uuid3')
DRIVER_PROFILE_7 = driver.Profile('parkid7_uuid7')
NEXT_MODE = 'next_work_mode'
PREV_MODE = 'prev_work_mode'
_NEXT_MODE_SETTINGS = {'rule_id': 'next_rule_id', 'shift_close_time': '00:01'}
_PREV_MODE_SETTINGS = {'rule_id': 'prev_rule_id', 'shift_close_time': '00:01'}


def _check_slot_reserved(
        pgsql, slot_name: str, driver_profile: driver.Profile,
):
    reservations = booking.get_reservations(pgsql, driver_profile)
    assert len(reservations) == 1
    assert reservations[0] == (slot_name,)


def _check_saga_context(
        pgsql, driver_profile: driver.Profile, expected_slot_name: str,
):
    saga_context = saga_tools.get_saga_context(driver_profile, pgsql)
    assert (
        saga_context['prev_mode']['booking_slot']['name'] == expected_slot_name
    )


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


def _make_tags_mock(mockserver):
    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        return {'status': 'ok'}


def _make_driver_fix_mock(mockserver):
    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
    def _v1_driver_fix_mode_prepare(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.parametrize(
    'main_feature, slot_policy, expected_slot_name, ',
    (
        pytest.param(
            'geobooking',
            'key_params',
            'next_zone/next_area/next_tag',
            id='key_params policy',
        ),
        pytest.param(
            'geobooking',
            'mode_settings_rule_id',
            'next_work_mode/next_rule_id',
            id='mode_settings_rule_id policy geobooking',
        ),
        pytest.param(
            'driver_fix',
            'mode_settings_rule_id',
            'next_work_mode/next_rule_id',
            id='mode_settings_rule_id policy driver_fix',
        ),
        pytest.param(
            'driver_fix',
            'contractor_tariff_zone',
            'next_work_mode/next_context_zone',
            id='constractor_tariff_zone policy driver_fix',
        ),
    ),
)
async def test_subscription_saga_booking_reserve(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        main_feature: str,
        slot_policy: str,
        expected_slot_name: str,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name=NEXT_MODE,
                    features={
                        main_feature: {},
                        'booking': {'slot_policy': slot_policy},
                    },
                ),
                mode_rules.Patch(rule_name=PREV_MODE, features={}),
            ],
        ),
    )

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
    _make_driver_fix_mock(mockserver)

    assert not booking.get_reservations(pgsql, DRIVER_PROFILE)

    await saga_tools.call_stq_saga_task(stq_runner, DRIVER_PROFILE)

    reservations = booking.get_reservations(pgsql, DRIVER_PROFILE)
    assert len(reservations) == 1
    assert reservations[0] == (expected_slot_name,)


@pytest.mark.pgsql(
    'driver_mode_subscription',
    files=['sagas.sql', 'reservation_next_mode_slots.sql'],
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={'enable_saga_persistent': True},
    DRIVER_MODE_BOOKING_SLOTS={
        'default': {'kickoff_percent': 100, 'limit': 50},
        'tariff_zones': {
            'next_zone': {
                'subvention_geoareas': {
                    'next_area': {'tags': {'next_tag': {'limit': 1}}},
                },
            },
        },
    },
    DRIVER_MODE_DRIVER_FIX_SLOTS={
        'default': {'limit': 10},
        'modes': {
            'next_work_mode': {
                'default': {'limit': 3},
                'rules': {'next_rule_id': {'limit': 1}},
            },
        },
    },
    DRIVER_MODE_BOOKING_TARIFF_ZONE_SLOTS={
        'default': {'limit': 10},
        'modes': {
            'next_work_mode': {
                'default': {'limit': 3},
                'tariff_zones': {'next_context_zone': {'limit': 1}},
            },
        },
    },
)
@pytest.mark.parametrize(
    'slot_policy',
    (
        pytest.param('key_params', id='key_params policy'),
        pytest.param(
            'mode_settings_rule_id', id='mode_settings_rule_id policy',
        ),
        pytest.param(
            'contractor_tariff_zone', id='contractor_tariff_zone policy',
        ),
    ),
)
async def test_subscription_saga_booking_reserve_blocked(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        slot_policy: str,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name=NEXT_MODE,
                    features={
                        'geobooking': {},
                        'booking': {'slot_policy': slot_policy},
                    },
                ),
                mode_rules.Patch(rule_name=PREV_MODE, features={}),
            ],
        ),
    )

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

    await saga_tools.call_stq_saga_task(
        stq_runner, DRIVER_PROFILE, expect_fail=True,
    )

    assert saga_tools.get_saga_steps_db_data(pgsql, 1) == [
        ('reserve_slot', 'blocked', None),
    ]

    assert not booking.get_reservations(pgsql, DRIVER_PROFILE)


@pytest.mark.pgsql(
    'driver_mode_subscription',
    files=['sagas.sql', 'reservation_next_mode_slots.sql'],
)
@pytest.mark.config(
    DRIVER_MODE_BOOKING_SLOTS={
        'default': {'kickoff_percent': 100, 'limit': 50},
        'tariff_zones': {
            'next_zone': {
                'subvention_geoareas': {
                    'next_area': {'tags': {'next_tag': {'limit': 1}}},
                },
            },
        },
    },
    DRIVER_MODE_DRIVER_FIX_SLOTS={
        'default': {'limit': 10},
        'modes': {
            'next_work_mode': {
                'default': {'limit': 3},
                'rules': {'next_rule_id': {'limit': 1}},
            },
        },
    },
    DRIVER_MODE_BOOKING_TARIFF_ZONE_SLOTS={
        'default': {'limit': 10},
        'modes': {
            'next_work_mode': {
                'default': {'limit': 3},
                'tariff_zones': {'next_context_zone': {'limit': 1}},
            },
        },
    },
)
@pytest.mark.parametrize(
    'slot_policy',
    (
        pytest.param('key_params', id='key_params policy'),
        pytest.param(
            'mode_settings_rule_id', id='mode_settings_rule_id policy',
        ),
        pytest.param(
            'contractor_tariff_zone', id='contractor_tariff_zone policy',
        ),
    ),
)
async def test_subscription_saga_booking_service_overbooking(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        slot_policy: str,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name=NEXT_MODE,
                    features={
                        'geobooking': {},
                        'booking': {'slot_policy': slot_policy},
                    },
                ),
                mode_rules.Patch(rule_name=PREV_MODE, features={}),
            ],
        ),
    )

    scene = scenario.Scene(
        profiles={
            DRIVER_PROFILE_7: driver.Mode(
                PREV_MODE, mode_settings=_PREV_MODE_SETTINGS,
            ),
        },
    )
    scene.setup(mockserver, mocked_time)
    _make_key_params_mock(mockserver)
    _make_tags_mock(mockserver)

    await saga_tools.call_stq_saga_task(stq_runner, DRIVER_PROFILE_7)

    reservations = booking.get_reservations(pgsql, DRIVER_PROFILE_7)
    assert len(reservations) == 1


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'reservation.sql'],
)
@pytest.mark.parametrize(
    'driver_profile, slot_policy, expected_slot_name',
    (
        pytest.param(
            DRIVER_PROFILE,
            'key_params',
            'prev_zone/prev_area/prev_tag',
            id='key_params policy',
        ),
        pytest.param(
            DRIVER_PROFILE_2,
            'mode_settings_rule_id',
            'prev_work_mode/prev_rule_id',
            id='mode_settings_rule_id policy',
        ),
    ),
)
async def test_subscription_saga_booking_cancel_reservation(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        driver_profile: driver.Profile,
        slot_policy: str,
        expected_slot_name: str,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(rule_name=NEXT_MODE, features={}),
                mode_rules.Patch(
                    rule_name=PREV_MODE,
                    features={
                        'geobooking': {},
                        'booking': {'slot_policy': slot_policy},
                    },
                ),
            ],
        ),
    )

    scene = scenario.Scene(profiles={driver_profile: driver.Mode(PREV_MODE)})
    scene.setup(mockserver, mocked_time)
    _make_key_params_mock(mockserver)
    _make_tags_mock(mockserver)

    reservations = booking.get_reservations(pgsql, driver_profile)
    assert len(reservations) == 1
    assert reservations[0] == (expected_slot_name,)

    await saga_tools.call_stq_saga_task(stq_runner, driver_profile)

    assert not booking.get_reservations(pgsql, driver_profile)


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'reservation.sql'],
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name=NEXT_MODE, features={}),
            mode_rules.Patch(
                rule_name=PREV_MODE,
                features={
                    'driver_fix': {},
                    'booking': {'slot_policy': 'key_params'},
                },
            ),
        ],
    ),
)
async def test_subscription_saga_booking_load_context(
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
    _make_driver_fix_mock(mockserver)

    expected_slot_name = 'prev_zone/prev_area/prev_tag'

    _check_slot_reserved(pgsql, expected_slot_name, DRIVER_PROFILE)

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop_blocked(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    await saga_tools.call_stq_saga_task(
        stq_runner, DRIVER_PROFILE, expect_fail=True,
    )

    _check_saga_context(pgsql, DRIVER_PROFILE, expected_slot_name)
    _check_slot_reserved(pgsql, expected_slot_name, DRIVER_PROFILE)

    expected_new_slot_name = 'new_slot_key'
    new_slot_id = 9999
    booking.remove_reservations(pgsql, DRIVER_PROFILE)
    booking.insert_slot(pgsql, expected_new_slot_name, new_slot_id)
    booking.make_reservation(pgsql, new_slot_id, DRIVER_PROFILE)

    await saga_tools.call_stq_saga_task(
        stq_runner, DRIVER_PROFILE, expect_fail=True,
    )

    _check_saga_context(pgsql, DRIVER_PROFILE, expected_slot_name)
    _check_slot_reserved(pgsql, expected_new_slot_name, DRIVER_PROFILE)

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, DRIVER_PROFILE)

    _check_slot_reserved(pgsql, expected_new_slot_name, DRIVER_PROFILE)


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'reservation.sql'],
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=NEXT_MODE,
                features={
                    'driver_fix': {},
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                },
            ),
            mode_rules.Patch(
                rule_name=PREV_MODE,
                features={
                    'driver_fix': {},
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                },
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'driver_profile, is_error_expected, is_trackstory_call_expected',
    [(DRIVER_PROFILE_2, True, True), (DRIVER_PROFILE_3, False, False)],
)
async def test_subscription_saga_booking_no_tariff_zone_context(
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        pgsql,
        mockserver,
        mocked_time,
        driver_profile: driver.Profile,
        is_error_expected: bool,
        is_trackstory_call_expected: bool,
):
    scene = scenario.Scene(
        profiles={
            DRIVER_PROFILE_2: driver.Mode(
                PREV_MODE, mode_settings=_PREV_MODE_SETTINGS,
            ),
            DRIVER_PROFILE_3: driver.Mode(
                NEXT_MODE, mode_settings=_PREV_MODE_SETTINGS,
            ),
        },
    )
    scene.setup(mockserver, mocked_time)

    _make_driver_fix_mock(mockserver)

    await saga_tools.call_stq_saga_task(
        stq_runner, driver_profile, is_error_expected,
    )

    reservations = booking.get_reservations(pgsql, driver_profile)
    assert len(reservations) == 1
    # this is slot for another slot policy, but it doesn't matter in this test
    assert reservations[0] == ('prev_work_mode/prev_rule_id',)

    if is_trackstory_call_expected:
        assert scene.driver_trackstory_mock.has_calls
