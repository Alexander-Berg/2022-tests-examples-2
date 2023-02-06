import pytest

ROBOT_YANDEX_UID_STR = '1111'
ROBOT_YANDEX_LOGIN = 'login'


@pytest.fixture(name='mock_execute_fine_stq_settings')
async def _mock_execute_fine_stq_settings(
        taxi_cargo_performer_fines, taxi_config, default_ticket,
):
    taxi_config.set(
        CARGO_PERFORMER_FINES_EXECUTE_FINE_SETTINGS={
            'enabled': True,
            'reschedule_delay_ms': 1000,
            'reschedule_count': -1,
            'robot_yandex_login': ROBOT_YANDEX_LOGIN,
            'robot_yandex_uid': int(ROBOT_YANDEX_UID_STR),
            'st_ticket_stub': default_ticket,
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()


@pytest.fixture(name='mock_execute_fine_stq_settings_with_reschedule')
async def _mock_execute_fine_stq_settings_with_reschedule(
        taxi_cargo_performer_fines, taxi_config, default_ticket,
):
    taxi_config.set(
        CARGO_PERFORMER_FINES_EXECUTE_FINE_SETTINGS={
            'enabled': True,
            'reschedule_delay_ms': 1000,
            'reschedule_count': 1,
            'robot_yandex_login': ROBOT_YANDEX_LOGIN,
            'robot_yandex_uid': int(ROBOT_YANDEX_UID_STR),
            'st_ticket_stub': default_ticket,
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()


@pytest.fixture(name='mock_mapping_cancel_reason_to_fine_code')
async def _mock_mapping_cancel_reason_to_fine_code(
        taxi_cargo_performer_fines, experiments3, default_fine_code,
):
    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_performer_fines_cancel_reason_to_fine_code',
        consumers=['cargo-performer-fines/execute-fine-args'],
        clauses=[],
        default_value={'enabled': True, 'fine_code': default_fine_code},
    )
    await taxi_cargo_performer_fines.invalidate_caches()


@pytest.fixture(name='mock_execute_fine_stq_critical_fails')
async def _mock_execute_fine_stq_critical_fails(
        taxi_cargo_performer_fines, taxi_config, default_ticket,
):
    taxi_config.set(
        CARGO_PERFORMER_FINES_EXECUTE_FINE_SETTINGS={
            'enabled': True,
            'reschedule_delay_ms': 1000,
            'reschedule_count': 1,
            'robot_yandex_login': ROBOT_YANDEX_LOGIN,
            'robot_yandex_uid': int(ROBOT_YANDEX_UID_STR),
            'st_ticket_stub': default_ticket,
            'update_fine_fails': {
                'non_critical': ['non_critical1', 'non_critical2'],
                'critical': ['critical2', 'critical1'],
            },
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()
