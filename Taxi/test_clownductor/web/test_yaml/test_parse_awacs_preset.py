import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_yaml_repr_awacs')
def _expected_yaml_repr_awacs(backend_py3_yaml_url):
    service_url = backend_py3_yaml_url('service_exist')
    return yaml_models.ServiceYamlRepresentation(
        service_type='backendpy3',
        service_yaml_url=service_url,
        service_name='service_exist',
        wiki_path='https://wiki.yandex-team.ru',
        maintainers=['Zhuchkov Aleksey <azhuchkov@yandex-team.ru>'],
        debian_units=[
            yaml_models.DebianUnit(
                name='web',
                tvm_name='service_exist',
                hostnames={
                    'production': ['clownductor.taxi.yandex.net'],
                    'testing': ['clownductor.taxi.tst.yandex.net'],
                },
            ),
        ],
        tvm_name=None,
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                abc=None,
                awacs_preset={
                    'production': {
                        'instances': {'man': 3, 'sas': 1, 'vla': 2},
                        'io_intensity': 'HIGH',
                        'name': 'MEDIUM',
                    },
                },
                clownductor_project='taxi-devops',
                critical_class=None,
                deploy_callback_url=None,
                description=None,
                design_review='https://st.yandex-team.ru',
                disk_profile={
                    'production': {'name': 'default'},
                    'testing': {'name': 'default'},
                },
                duty={
                    'abc_slug': 'some_abc',
                    'primary_schedule': 'some_schedule',
                },
                duty_group_id=None,
                grafana=None,
                has_balancers=True,
                has_unstable=True,
                name='service_exist',
                networks=None,
                preset={'production': {'name': 'x2nano'}},
                reallocation_settings=None,
                release_flow=None,
                responsible_managers=None,
                robots=None,
                units=['web'],
                yt_log_replications=None,
            ),
            aliases=[],
        ),
    )


@pytest.fixture(name='expected_repr_awacs_env')
def _expected_repr_awacs_env(backend_py3_yaml_url):
    service_url = backend_py3_yaml_url('service_exist')
    return yaml_models.ServiceYamlRepresentation(
        service_type='backendpy3',
        service_yaml_url=service_url,
        service_name='service_exist',
        wiki_path='https://wiki.yandex-team.ru',
        maintainers=['Zhuchkov Aleksey <azhuchkov@yandex-team.ru>'],
        debian_units=[
            yaml_models.DebianUnit(
                name='web',
                tvm_name='service_exist',
                hostnames={
                    'production': ['clownductor.taxi.yandex.net'],
                    'testing': ['clownductor.taxi.tst.yandex.net'],
                },
            ),
        ],
        tvm_name=None,
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                abc=None,
                awacs_preset={
                    'production': {
                        'instances': {'man': 3, 'sas': 1, 'vla': 2},
                        'io_intensity': 'HIGH',
                        'name': 'NANO',
                    },
                    'testing': {'io_intensity': 'NORMAL', 'name': 'MICRO'},
                },
                clownductor_project='taxi-devops',
                critical_class=None,
                deploy_callback_url=None,
                description=None,
                design_review='https://st.yandex-team.ru',
                disk_profile={
                    'production': {'name': 'default'},
                    'testing': {'name': 'default'},
                },
                duty={
                    'abc_slug': 'some_abc',
                    'primary_schedule': 'some_schedule',
                },
                duty_group_id=None,
                grafana=None,
                has_balancers=True,
                has_unstable=True,
                name='service_exist',
                networks=None,
                preset={'production': {'name': 'x2micro'}},
                reallocation_settings=None,
                release_flow=None,
                responsible_managers=None,
                robots=None,
                units=['web'],
                yt_log_replications=None,
            ),
            aliases=[],
        ),
    )


async def test_parse_py3_awacs_preset(
        test_parse_yaml, expected_yaml_repr_awacs,
):
    await test_parse_yaml(
        'service_exist', 'service_py3_awacs.yaml', expected_yaml_repr_awacs,
    )


async def test_parse_py3_awacs_env(test_parse_yaml, expected_repr_awacs_env):
    await test_parse_yaml(
        'service_exist', 'service_py3_awacs_env.yaml', expected_repr_awacs_env,
    )
