import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_yaml_repr')
def _expected_yaml_repr(repo_yaml_url):
    service_url = repo_yaml_url(
        'some-another-repo', 'common-service', 'master',
    )
    env_profile = {'name': 'default'}
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
        maintainers=['Aleksei Zhuchkov <azhuchkov@yandex-team.ru>'],
        debian_units=[
            yaml_models.DebianUnit(name='web', tvm_name=None, hostnames=None),
        ],
        tvm_name='common-service',
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                has_balancers=True,
                has_unstable=True,
                name='common-service',
                clownductor_project='taxi',
                preset={
                    'production': {
                        'name': 'x2micro',
                        'overrides': {
                            'cpu': 4,
                            'datacenters': {
                                'allowed_regions': [
                                    'vla',
                                    'iva',
                                    'sas',
                                    'myt',
                                    'man',
                                ],
                                'count': 5,
                            },
                        },
                    },
                },
                disk_profile=default_profile,
                abc=None,
                description='Main alias',
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
            aliases=[],
        ),
    )


async def test_parse_common_allowed_regions(
        test_parse_yaml, expected_yaml_repr,
):
    await test_parse_yaml(
        'common-service', 'common_allowed_regions.yaml', expected_yaml_repr,
    )
