import pytest

EXPERIMENTS3_CONSUMER = 'passenger_profile/passenger_profile'
PASSENGER_PROFILE_EXPERIMENT = 'passenger_profile'


def add_experiment3(name, *, yandex_uid: str):
    args = [{'name': 'yandex_uid', 'type': 'string', 'value': yandex_uid}]
    decorator = pytest.mark.client_experiments3(
        consumer=EXPERIMENTS3_CONSUMER,
        experiment_name=name,
        args=args,
        value={},
    )
    return decorator


# pylint: disable=invalid-name
def mark_passenger_profile_experiment(yandex_uid: str):
    return add_experiment3(PASSENGER_PROFILE_EXPERIMENT, yandex_uid=yandex_uid)
