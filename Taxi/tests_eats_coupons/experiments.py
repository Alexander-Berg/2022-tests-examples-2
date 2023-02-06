import pytest


def use_glue_uids():
    return pytest.mark.experiments3(
        name='use_glue_uids',
        consumers=['eats_coupons/user_only'],
        is_config=False,
        default_value={'enabled': True},
    )


def eats_coupons_validators(validators):
    return pytest.mark.experiments3(
        name='eats_coupons_validators',
        consumers=['eats_coupons/user_only'],
        is_config=True,
        default_value={'enabled_validators': validators},
    )


def eats_coupons_new_user_antifraud(enabled=True):
    return pytest.mark.experiments3(
        name='eats_coupons_new_user_antifraud',
        consumers=['eats_coupons/user_only'],
        is_config=True,
        default_value={
            'enabled': enabled,
            'attempts_before_ban': 2,
            'warning_ban_duration_hours': 48,
        },
    )


def eats_excluded_validators(validators):
    return pytest.mark.experiments3(
        name='exclude_checkers_by_source',
        consumers=['eats_coupons/source_api'],
        is_config=False,
        default_value={'excluded_checkers': validators},
    )
