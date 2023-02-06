import pytest

from payments_eda import consts as service_consts
from test_payments_eda import consts


def add_experiment(experiment_name: str, experiment_value=None):
    experiment_value = (
        experiment_value if experiment_value is not None else {'enabled': True}
    )
    return pytest.mark.client_experiments3(
        consumer=service_consts.EXP3_CONSUMER_WEB,
        experiment_name=experiment_name,
        args=[
            {
                'name': 'yandex_uid',
                'type': 'string',
                'value': consts.DEFAULT_YANDEX_UID,
            },
            {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
            {'name': 'service', 'type': 'string', 'value': 'eats'},
        ],
        value=experiment_value,
    )


def make_stat(labels: dict):
    return {'kind': 'IGAUGE', 'labels': labels, 'timestamp': None, 'value': 1}
