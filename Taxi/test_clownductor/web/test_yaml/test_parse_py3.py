import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_yaml_repr')
def _expected_yaml_repr(backend_py3_yaml_url):
    service_url = backend_py3_yaml_url('clownductor')
    profile = {
        'production': {'name': 'default'},
        'testing': {'name': 'default'},
        'unstable': {'name': 'default'},
    }
    return yaml_models.ServiceYamlRepresentation(
        service_type='backendpy3',
        service_yaml_url=service_url,
        service_name='clownductor',
        wiki_path='https://wiki.yandex-team.ru',
        maintainers=['Karachev Dmitriy <karachevda@yandex-team.ru>'],
        debian_units=[
            yaml_models.DebianUnit(
                name='web',
                tvm_name='clownductor',
                hostnames={
                    'production': ['clownductor.taxi.yandex.net'],
                    'testing': ['clownductor.taxi.tst.yandex.net'],
                },
            ),
        ],
        tvm_name='clownductor',
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='clownductor',
                units=['web'],
                has_unstable=True,
                has_balancers=True,
                duty_group_id='5b69be79c5755f678048a169',
                disk_profile=profile,
                abc={
                    'description': {
                        'en': 'The cool one',
                        'ru': 'Крутой сервис',
                    },
                    'service_name': {'en': 'clownductor', 'ru': 'clownductor'},
                },
                description=None,
                grafana=None,
                robots={
                    'production': ['robot-tester', 'nanny-robot'],
                    'testing': ['robot-tester'],
                },
                design_review='https://st.yandex-team.ru',
                clownductor_project='taxi-devops',
                preset={
                    'production': {'name': 'x2nano', 'overrides': {'ram': 2}},
                },
                networks={
                    'production': '_TAXI_BOT_YANFORMATOR_NETS_',
                    'testing': '_TAXI_TEST_BOT_YANFORMATOR_NETS_',
                },
            ),
            aliases=[],
        ),
    )


@pytest.fixture(name='expected_yaml_repr_preset')
def _expected_yaml_repr_preset(backend_py3_yaml_url):
    service_url = backend_py3_yaml_url('clownductor')
    profile = {
        'production': {
            'name': 'default',
            'overrides': [{'path': '/cores', 'size': 0, 'type': 'hdd'}],
        },
        'testing': {
            'name': 'default',
            'overrides': [
                {'path': '/cores', 'size': 0, 'type': 'hdd'},
                {
                    'path': '/var/custom',
                    'size': 1024,
                    'type': 'hdd',
                    'bandwidth_guarantee_mb_per_sec': 2,
                },
            ],
        },
    }
    return yaml_models.ServiceYamlRepresentation(
        service_type='backendpy3',
        service_yaml_url=service_url,
        service_name='clownductor',
        wiki_path='https://wiki.yandex-team.ru',
        maintainers=['Karachev Dmitriy <karachevda@yandex-team.ru>'],
        debian_units=[
            yaml_models.DebianUnit(
                name='web',
                tvm_name='clownductor',
                hostnames={
                    'production': ['clownductor.taxi.yandex.net'],
                    'testing': ['clownductor.taxi.tst.yandex.net'],
                },
            ),
        ],
        tvm_name=None,
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='clownductor',
                units=['web'],
                has_unstable=True,
                has_balancers=True,
                duty_group_id=None,
                duty={
                    'abc_slug': 'some_abc',
                    'primary_schedule': 'some_schedule',
                },
                disk_profile=profile,
                design_review='https://st.yandex-team.ru',
                clownductor_project='taxi-devops',
                preset={
                    'production': {'name': 'x2micro'},
                    'testing': {
                        'name': 'x2nano',
                        'overrides': {'instances_count': 3, 'ram': 2},
                    },
                },
            ),
            aliases=[],
        ),
    )


async def test_parse_service_py3(test_parse_yaml, expected_yaml_repr):
    await test_parse_yaml(
        'clownductor', 'service_py3.yaml', expected_yaml_repr,
    )


async def test_parse_py3_new_preset(
        test_parse_yaml, expected_yaml_repr_preset,
):
    await test_parse_yaml(
        'clownductor',
        'service_py3_new_preset.yaml',
        expected_yaml_repr_preset,
    )
