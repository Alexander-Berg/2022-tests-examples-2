import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_yaml_repr')
def _expected_yaml_repr(backend_py3_yaml_url):
    service_url = backend_py3_yaml_url('taxi-approvals')
    return yaml_models.ServiceYamlRepresentation(
        service_type='backendpy3',
        service_yaml_url=service_url,
        service_name='taxi-approvals',
        wiki_path=None,
        maintainers=['Petrov Mikhail <mvpetrov@yandex-team.ru>'],
        debian_units=[
            yaml_models.DebianUnit(
                name='web',
                tvm_name=None,
                hostnames={
                    'production': ['approvals.taxi.yandex.net'],
                    'testing': ['approvals.taxi.tst.yandex.net'],
                },
            ),
        ],
        tvm_name=None,
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='taxi-approvals',
                has_unstable=True,
                has_balancers=True,
                description='Approvals',
                disk_profile=None,
                abc=None,
                grafana=None,
                units=['web'],
                robots={'production': ['robot-tester', 'nanny-robot']},
                design_review='https://st.yandex-team.ru',
                clownductor_project='taxi',
                preset={
                    'production': {'name': 'x2nano', 'overrides': {'ram': 2}},
                },
            ),
            aliases=[],
        ),
    )


async def test_parse_service_py3_nocodegen(
        test_parse_yaml, expected_yaml_repr,
):
    await test_parse_yaml(
        'taxi-approvals', 'service_py3_nocodegen.yaml', expected_yaml_repr,
    )
