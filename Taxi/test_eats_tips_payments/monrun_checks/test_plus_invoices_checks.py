import pytest

from eats_tips_payments.generated.cron import run_monrun
from eats_tips_payments.models import plus as models_plus


ERR_TEMPLATE = '{}; Status threshold {}, next statuses triggered: {}'
OK_MESSAGE = '0; Check done'


def _get_config(status, time_window, warn, crit):
    return {
        'status': status,
        'time_window': time_window,
        'threshold': {'warn': warn, 'crit': crit},
    }


def _get_warn_message(statuses):
    return ERR_TEMPLATE.format('1', 'WARN', statuses)


def _get_crit_message(statuses):
    return ERR_TEMPLATE.format('2', 'CRIT', statuses)


@pytest.mark.parametrize(
    'too_many_count_in_status, too_low_count_in_status, expected',
    (
        # disabled
        ([], [], '0; Check done'),
        # too_many_count_in_status
        # -- too big threshold
        (
            [
                _get_config(
                    models_plus.CashbackStatus.FAILED.value, 3600, 100, 100,
                ),
            ],
            [],
            OK_MESSAGE,
        ),
        # too small window
        (
            [_get_config(models_plus.CashbackStatus.FAILED.value, 10, 1, 1)],
            [],
            OK_MESSAGE,
        ),
        # warn
        (
            [_get_config(models_plus.CashbackStatus.FAILED.value, 600, 1, 2)],
            [],
            _get_warn_message('failed (threshold: 1, level: WARN)'),
        ),
        # crit
        (
            [_get_config(models_plus.CashbackStatus.FAILED.value, 900, 1, 2)],
            [],
            _get_crit_message('failed (threshold: 2, level: CRIT)'),
        ),
        (
            [_get_config(models_plus.CashbackStatus.FAILED.value, 900, 2, 3)],
            [],
            _get_warn_message('failed (threshold: 2, level: WARN)'),
        ),
        # 2 conditions, both warn
        (
            [
                _get_config(
                    models_plus.CashbackStatus.FAILED.value, 900, 2, 3,
                ),
                _get_config(
                    models_plus.CashbackStatus.IN_PROGRESS.value, 300, 2, 3,
                ),
            ],
            [],
            _get_warn_message(
                'failed (threshold: 2, level: WARN), '
                'in-progress (threshold: 2, level: WARN)',
            ),
        ),
        # 2 conditions, 1 - ok, 2 - warn
        (
            [
                _get_config(
                    models_plus.CashbackStatus.FAILED.value, 900, 100, 100,
                ),
                _get_config(
                    models_plus.CashbackStatus.IN_PROGRESS.value, 300, 2, 3,
                ),
            ],
            [],
            _get_warn_message('in-progress (threshold: 2, level: WARN)'),
        ),
        # 2 conditions, 1 - crit, 2 - warn
        (
            [
                _get_config(
                    models_plus.CashbackStatus.FAILED.value, 900, 2, 2,
                ),
                _get_config(
                    models_plus.CashbackStatus.IN_PROGRESS.value, 300, 2, 3,
                ),
            ],
            [],
            _get_crit_message(
                'failed (threshold: 2, level: CRIT), '
                'in-progress (threshold: 2, level: WARN)',
            ),
        ),
        # -- too_low_count_in_status
        # too low threshold
        (
            [],
            [
                _get_config(
                    models_plus.CashbackStatus.SUCCESS.value, 3600, 0, 0,
                ),
            ],
            OK_MESSAGE,
        ),
        # fine
        (
            [],
            [_get_config(models_plus.CashbackStatus.SUCCESS.value, 600, 2, 1)],
            OK_MESSAGE,
        ),
        # warn
        (
            [],
            [_get_config(models_plus.CashbackStatus.SUCCESS.value, 300, 2, 1)],
            _get_warn_message('success (threshold: 2, level: WARN)'),
        ),
        # crit
        (
            [],
            [_get_config(models_plus.CashbackStatus.SUCCESS.value, 150, 2, 1)],
            _get_crit_message('success (threshold: 1, level: CRIT)'),
        ),
        # 2 conditions, 1 - warn, 2 - crit
        (
            [],
            [
                _get_config(
                    models_plus.CashbackStatus.IN_PROGRESS.value, 300, 3, 1,
                ),
                _get_config(
                    models_plus.CashbackStatus.SUCCESS.value, 150, 2, 1,
                ),
            ],
            _get_crit_message(
                'success (threshold: 1, level: CRIT), '
                'in-progress (threshold: 3, level: WARN)',
            ),
        ),
        # 2 conditions, 1 - ok, 2 - warn
        (
            [],
            [
                _get_config(
                    models_plus.CashbackStatus.SUCCESS.value, 600, 2, 1,
                ),
                _get_config(
                    models_plus.CashbackStatus.IN_PROGRESS.value, 300, 3, 1,
                ),
            ],
            _get_warn_message('in-progress (threshold: 3, level: WARN)'),
        ),
        # 2 conditions, both warn
        (
            [],
            [
                _get_config(
                    models_plus.CashbackStatus.SUCCESS.value, 300, 2, 1,
                ),
                _get_config(
                    models_plus.CashbackStatus.IN_PROGRESS.value, 300, 3, 1,
                ),
            ],
            _get_warn_message(
                'success (threshold: 2, level: WARN), '
                'in-progress (threshold: 3, level: WARN)',
            ),
        ),
        # ok
        (
            [
                _get_config(
                    models_plus.CashbackStatus.FAILED.value, 900, 100, 100,
                ),
            ],
            [_get_config(models_plus.CashbackStatus.SUCCESS.value, 600, 2, 1)],
            OK_MESSAGE,
        ),
        # ok + warn
        (
            [
                _get_config(
                    models_plus.CashbackStatus.FAILED.value, 900, 100, 100,
                ),
            ],
            [_get_config(models_plus.CashbackStatus.SUCCESS.value, 300, 2, 1)],
            _get_warn_message('success (threshold: 2, level: WARN)'),
        ),
        # ok + crit
        (
            [
                _get_config(
                    models_plus.CashbackStatus.FAILED.value, 900, 100, 100,
                ),
            ],
            [_get_config(models_plus.CashbackStatus.SUCCESS.value, 150, 2, 1)],
            _get_crit_message('success (threshold: 1, level: CRIT)'),
        ),
        # None
        (
            [_get_config('None', 3600, 1, 1)],
            [],
            _get_crit_message('None (threshold: 1, level: CRIT)'),
        ),
        (
            [_get_config('None', 3600, 1, 2)],
            [],
            _get_warn_message('None (threshold: 1, level: WARN)'),
        ),
        ([_get_config('None', 3600, 2, 2)], [], OK_MESSAGE),
    ),
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_plus_invoices_checks(
        taxi_config,
        too_many_count_in_status,
        too_low_count_in_status,
        expected,
):
    taxi_config.set_values(
        {
            'EATS_TIPS_PAYMENTS_PLUS_MONRUN_CHECKS': {
                'too_many_count_in_status': too_many_count_in_status,
                'too_low_count_in_status': too_low_count_in_status,
            },
        },
    )
    message = await run_monrun.run(
        ['eats_tips_payments.monrun_checks.plus_invoices_checks'],
    )
    assert message == expected
