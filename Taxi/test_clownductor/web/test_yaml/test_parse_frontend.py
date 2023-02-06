import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_yaml_repr')
def _expected_yaml_repr(frontend_yaml_url):
    service_url = frontend_yaml_url('hiring-partners-app')
    return yaml_models.ServiceYamlRepresentation(
        service_type='frontend',
        service_yaml_url=service_url,
        service_name='partners-app',
        wiki_path='https://wiki.yandex-team.ru',
        maintainers=['Karachev Dmitrii <karachevda@yandex-team.ru>'],
        debian_units=[],
        tvm_name=None,
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='partners-app',
                duty_group_id='5b69be79c5755f678048a169',
                abc=None,
                description='Hiring partners app',
                grafana=None,
                robots={'production': ['robot-tester', 'nanny-robot']},
                design_review='https://st.yandex-team.ru/TAXIARCHREVIEW-320',
                clownductor_project='taxi-devops',
                preset={'production': {'name': 'x2nano'}},
                deploy_callback_url='http://frontend-dev-api.taxi.yandex.net'
                '/api/webhook/clownductor/deploy',
                has_unstable=True,
                has_balancers=True,
            ),
            aliases=[],
        ),
    )


async def test_parse_frontend(test_parse_yaml, expected_yaml_repr):
    await test_parse_yaml(
        'hiring-partners-app', 'frontend.yaml', expected_yaml_repr,
    )
