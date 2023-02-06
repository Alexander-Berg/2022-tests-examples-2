import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_yaml_repr')
def _expected_yaml_repr(repo_yaml_url):
    service_url = repo_yaml_url(
        'some-another-repo', 'common-service', 'master',
    )
    env_profile = {
        'name': 'default',
        'overrides': [
            {'path': '/var/cache/yandex', 'size': 10240, 'type': 'ssd'},
            {
                'path': '/var/custom',
                'size': 1024,
                'type': 'hdd',
                'bandwidth_guarantee_mb_per_sec': 12,
            },
            {'path': '/cores', 'size': 0, 'type': 'hdd'},
        ],
    }
    default_profile = {
        'production': env_profile,
        'testing': env_profile,
        'unstable': env_profile,
    }
    return yaml_models.ServiceYamlRepresentation(
        service_type='some-another-repo',
        service_yaml_url=service_url,
        service_name='common-service',
        wiki_path='https://wiki.yandex-team.ru/taxi/'
        'backend/architecture/common-service/',
        maintainers=['Dmitrii Karachev <karachevda@yandex-team.ru>'],
        debian_units=[
            yaml_models.DebianUnit(name='web', tvm_name=None, hostnames=None),
            yaml_models.DebianUnit(name='stq3', tvm_name=None, hostnames=None),
            yaml_models.DebianUnit(
                name='eda_web', tvm_name='common-service-eda', hostnames=None,
            ),
            yaml_models.DebianUnit(
                name='eda_stq3', tvm_name='common-service-eda', hostnames=None,
            ),
            yaml_models.DebianUnit(
                name='eda_cron', tvm_name='common-service-eda', hostnames=None,
            ),
        ],
        tvm_name='common-service',
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                has_balancers=True,
                has_unstable=True,
                name='common-service',
                clownductor_project='taxi',
                preset={
                    'production': {'name': 'x2micro', 'overrides': {'cpu': 4}},
                },
                disk_profile=default_profile,
                abc=None,
                description='Main alias. Name would be taken from '
                'meta.service_name if not overrided.',
                design_review='https://st.yandex-team.ru/TAXIADMIN-9711',
                grafana=None,
                robots=None,
                deploy_callback_url=None,
                duty_group_id=None,
                duty={
                    'abc_slug': 'some_abc',
                    'primary_schedule': 'some_schedule',
                },
                units=['web', 'stq3'],
                yt_log_replications=[
                    {
                        'table': 'taxi-api-yandex-taxi-protocol-cxx-log',
                        'url': (
                            'https://yt.yandex-team.ru/hahn/navigation?'
                            'path=//logs/taxi-api-yandex-taxi-protocol-cxx-log'
                        ),
                    },
                ],
                critical_class='A',
            ),
            aliases=[
                yaml_models.ServiceInfo(
                    has_balancers=True,
                    has_unstable=True,
                    name='common-service-critical',
                    description='Same as main alias, yet different instance. '
                    'Other fields will be derived from main alias.',
                    clownductor_project='taxi',
                    preset={
                        'production': {
                            'name': 'x2micro',
                            'overrides': {'cpu': 4},
                        },
                    },
                    disk_profile=default_profile,
                    design_review='https://st.yandex-team.ru/TAXIADMIN-9711',
                    units=['web', 'stq3'],
                    yt_log_replications=[
                        {
                            'table': 'taxi-api-yandex-taxi-protocol-cxx-log',
                            'url': (
                                'https://yt.yandex-team.ru/hahn/navigation?'
                                'path=//logs/'
                                'taxi-api-yandex-taxi-protocol-cxx-log'
                            ),
                        },
                    ],
                    critical_class='A',
                    duty={
                        'abc_slug': 'some_abc',
                        'primary_schedule': 'some_schedule',
                    },
                ),
                yaml_models.ServiceInfo(
                    has_balancers=True,
                    has_unstable=True,
                    name='common-service-eda',
                    networks={'production': '__STABLE__'},
                    clownductor_project='eda',
                    preset={
                        'production': {
                            'name': 'x2nano',
                            'overrides': {'ram': 1},
                        },
                    },
                    abc=None,
                    description='Eda',
                    grafana={
                        'production': (
                            'https://grafana.yandex-team.ru/d/'
                            'LVu3OitWk/nanny_common_service_eda_stable'
                        ),
                    },
                    robots={
                        'production': ['robot-tester', 'nanny-robot'],
                        'testing': ['nanny-robot'],
                    },
                    deploy_callback_url='http://frontend-dev-api.'
                    'taxi.yandex.net/api/webhook/clownductor/deploy',
                    duty_group_id='common-service-eda-id',
                    units=['eda_web', 'eda_stq3', 'eda_cron'],
                    disk_profile=default_profile,
                    design_review='https://st.yandex-team.ru/TAXIADMIN-9711',
                    yt_log_replications=[
                        {
                            'table': 'taxi-api-yandex-taxi-protocol-cxx-log',
                            'url': (
                                'https://yt.yandex-team.ru/hahn/navigation?'
                                'path=//logs/'
                                'taxi-api-yandex-taxi-protocol-cxx-log'
                            ),
                        },
                    ],
                    critical_class='A',
                ),
            ],
        ),
    )


async def test_parse_common(test_parse_yaml, expected_yaml_repr):
    await test_parse_yaml('common-service', 'common.yaml', expected_yaml_repr)
