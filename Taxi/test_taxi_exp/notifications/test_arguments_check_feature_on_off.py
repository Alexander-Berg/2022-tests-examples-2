import pytest

from taxi_exp.lib.notifications import arguments_types_check
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'consumers, is_disabled',
    [
        pytest.param(
            ['launch', 'z-launch', 'ignored_consumer'],
            True,
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {
                        'backend': {
                            'fill_notifications': True,
                            'kwargs_type_check': False,
                        },
                    },
                },
            ),
            id='disable_feature',
        ),
        pytest.param(
            ['launch', 'z-launch', 'ignored_consumer'],
            True,
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {
                        'backend': {
                            'fill_notifications': True,
                            'kwargs_type_check': True,
                        },
                    },
                },
                EXPERIMENTS3_SERVICE_CONSUMER_RELOAD=['ignored_consumer'],
            ),
            id='disable_feature_by_exp3_consumers',
        ),
        pytest.param(
            ['launch', 'z-launch'],
            False,
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {
                        'backend': {
                            'fill_notifications': True,
                            'kwargs_type_check': True,
                        },
                    },
                },
                EXPERIMENTS3_SERVICE_CONSUMER_RELOAD=['ignored_consumer'],
            ),
            id='enable_feature_without_exp3_consumers',
        ),
        pytest.param(
            ['launch', 'z-launch', 'ignored_consumer'],
            False,
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {
                        'backend': {
                            'fill_notifications': True,
                            'kwargs_type_check': True,
                            'check_exp3_matcher_consumers': True,
                        },
                    },
                },
                EXPERIMENTS3_SERVICE_CONSUMER_RELOAD=['ignored_consumer'],
            ),
            id='full_enable_feature',
        ),
    ],
)
async def test(taxi_exp_client, consumers, is_disabled):
    exp_body = experiment.generate(
        consumers=experiment.make_consumers(*consumers),
    )

    checker = arguments_types_check.Checker(
        context=taxi_exp_client.app, experiment=exp_body,
    )
    assert checker.is_disabled() == is_disabled
