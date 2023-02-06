import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_yaml_repr')
def _expected_new_yaml_repr(backend_py3_yaml_url):
    service_url = backend_py3_yaml_url('transactions')
    env_default_profile = {
        'name': 'default',
        'overrides': [
            {
                'path': '/logs',
                'size': 100000,
                'type': 'hdd',
                'bandwidth_guarantee_mb_per_sec': 25,
            },
        ],
    }
    default_profile = {
        'production': env_default_profile,
        'testing': env_default_profile,
        'unstable': env_default_profile,
    }
    return yaml_models.ServiceYamlRepresentation(
        service_type='backendpy3',
        service_yaml_url=service_url,
        service_name='transactions',
        wiki_path='https://wiki.yandex-team.ru',
        maintainers=['Ivan Kolosov <ivankolosov@yandex-team.ru>'],
        debian_units=[
            yaml_models.DebianUnit(
                name='web',
                tvm_name='transactions',
                hostnames={
                    'production': ['transactions.taxi.yandex.net'],
                    'testing': ['transactions.taxi.tst.yandex.net'],
                    'unstable': ['transactions.taxi.dev.yandex.net'],
                },
            ),
            yaml_models.DebianUnit(
                name='stq3', tvm_name='transactions', hostnames=None,
            ),
            yaml_models.DebianUnit(
                name='persey_web',
                tvm_name='transactions-persey',
                hostnames={
                    'production': ['transactions-persey.taxi.yandex.net'],
                    'testing': ['transactions-persey.taxi.tst.yandex.net'],
                    'unstable': ['transactions-persey.taxi.dev.yandex.net'],
                },
            ),
            yaml_models.DebianUnit(
                name='persey_stq3',
                tvm_name='transactions-persey-stq',
                hostnames=None,
            ),
            yaml_models.DebianUnit(
                name='eda_web',
                tvm_name='transactions_eda',
                hostnames={
                    'production': ['transactions-eda.taxi.yandex.net'],
                    'testing': ['transactions-eda.taxi.tst.yandex.net'],
                    'unstable': ['transactions-eda.taxi.dev.yandex.net'],
                },
            ),
            yaml_models.DebianUnit(
                name='eda_stq3', tvm_name='transactions_eda', hostnames=None,
            ),
            yaml_models.DebianUnit(
                name='eda_cron', tvm_name='transactions_eda', hostnames=None,
            ),
        ],
        tvm_name=None,
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='transactions',
                units=['web'],
                has_unstable=True,
                has_balancers=True,
                duty_group_id='5b69be79c5755f678048a169',
                disk_profile=default_profile,
                description='Transactions main',
                design_review='https://st.yandex-team.ru/TAXIADMIN-0001',
                clownductor_project='taxi-devops',
                preset={
                    'production': {
                        'name': 'x2micro',
                        'overrides': {'cpu': 4, 'root_size': 2},
                    },
                },
            ),
            aliases=[
                yaml_models.ServiceInfo(
                    name='transactions-eda',
                    description='Transactions eda alias',
                    units=['eda_web', 'eda_cron'],
                    has_unstable=True,
                    has_balancers=True,
                    duty_group_id='5b69be79c5755f678048a169',
                    disk_profile=default_profile,
                    design_review='https://st.yandex-team.ru/TAXIADMIN-0001',
                    clownductor_project='taxi-devops',
                    preset={
                        'production': {
                            'name': 'x2micro',
                            'overrides': {'cpu': 4, 'root_size': 2},
                        },
                    },
                ),
                yaml_models.ServiceInfo(
                    name='transactions-eda-stq',
                    description='Transactions eda stq alias',
                    units=['eda_stq3'],
                    has_unstable=True,
                    has_balancers=True,
                    disk_profile={
                        'production': {
                            'name': 'default',
                            'root_override': {
                                'work_dir_size': 512,
                                'type': 'hdd',
                                'size': 1689,
                            },
                        },
                    },
                    duty_group_id='5b69be79c5755f678048a169',
                    design_review='https://st.yandex-team.ru/TAXIADMIN-0001',
                    clownductor_project='taxi-devops',
                    preset={
                        'production': {
                            'name': 'x2micro',
                            'overrides': {
                                'cpu': 0.261,
                                'root_size': 1.65,
                                'datacenters_count': 3,
                                'stable_instances': 2,
                            },
                        },
                    },
                    release_flow={'single_approve': True},
                ),
                yaml_models.ServiceInfo(
                    name='transactions-persey',
                    description='Transactions persey alias',
                    units=['persey_web'],
                    has_unstable=True,
                    duty_group_id='5b69be79c5755f678048a169',
                    has_balancers=False,
                    disk_profile={
                        'production': {
                            'name': 'default',
                            'overrides': [
                                {
                                    'path': '/var/cache/yandex',
                                    'size': 10240,
                                    'type': 'ssd',
                                    'bandwidth_guarantee_mb_per_sec': 2,
                                },
                                {
                                    'path': '/var/custom',
                                    'size': 1024,
                                    'type': 'hdd',
                                },
                                {'path': '/cores', 'size': 0, 'type': 'hdd'},
                            ],
                        },
                    },
                    design_review='https://st.yandex-team.ru/TAXIADMIN-0001',
                    clownductor_project='taxi-devops',
                    preset={
                        'production': {
                            'name': 'x2micro',
                            'overrides': {'cpu': 4, 'root_size': 2},
                        },
                    },
                ),
                yaml_models.ServiceInfo(
                    name='transactions-persey-stq',
                    description='Transactions persey stq alias',
                    units=['persey_stq3'],
                    has_unstable=False,
                    has_balancers=True,
                    duty_group_id='transactions-persey-stq-duty-id',
                    disk_profile=default_profile,
                    design_review='https://st.yandex-team.ru/TAXIADMIN-0002',
                    clownductor_project='taxi-devops',
                    preset={
                        'production': {
                            'name': 'x2micro',
                            'overrides': {'cpu': 4, 'root_size': 2},
                        },
                    },
                ),
                yaml_models.ServiceInfo(
                    name='transactions-stq',
                    description='Transactions stq alias',
                    units=['stq3'],
                    has_unstable=False,
                    has_balancers=False,
                    duty_group_id='transactions-stq-duty-id',
                    deploy_callback_url='http://callback.yandex.net/'
                    'transactions-stq',
                    disk_profile=default_profile,
                    design_review='https://st.yandex-team.ru/TAXIADMIN-0001',
                    clownductor_project='taxi-devops',
                    preset={
                        'production': {
                            'name': 'x2micro',
                            'overrides': {'cpu': 4, 'root_size': 2},
                        },
                    },
                ),
            ],
        ),
    )


async def test_parse_py3_multi(test_parse_yaml, expected_yaml_repr):
    await test_parse_yaml('transactions', 'py3_multi.yaml', expected_yaml_repr)
