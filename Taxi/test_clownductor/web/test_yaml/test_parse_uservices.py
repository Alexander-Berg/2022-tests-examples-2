import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_yaml_repr')
def _expected_yaml_repr(uservices_yaml_url):
    service_url = uservices_yaml_url('billing-commissions')
    return yaml_models.ServiceYamlRepresentation(
        service_type='uservices',
        service_yaml_url=service_url,
        service_name='billing-commissions',
        wiki_path='https://wiki.yandex-team.ru/taxi/'
        'backend/architecture/billing-commissions/',
        maintainers=[
            'Maksim Zubkov <maksimzubkov@yandex-team.ru>',
            'Ivan Kolosov <ivankolosov@yandex-team.ru>',
        ],
        debian_units=[
            yaml_models.DebianUnit(
                name='billing-commissions',
                tvm_name=None,
                hostnames={
                    'production': ['billing-commissions.taxi.yandex.net'],
                    'testing': ['billing-commissions.taxi.tst.yandex.net'],
                    'unstable': ['billing-commissions.taxi.dev.yandex.net'],
                },
            ),
        ],
        tvm_name='billing-commissions',
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='billing-commissions',
                has_unstable=True,
                has_balancers=True,
                clownductor_project='taxi-devops',
                preset={'production': {'name': 'x2nano'}},
                disk_profile=None,
                abc=None,
                duty_group_id='5b69be79c5755f678048a169',
                design_review='https://st.yandex-team.ru',
                units=['billing-commissions'],
                description=(
                    'Service for manage subventions and commissions rules'
                ),
                grafana={
                    'production': (
                        'https://grafana.yandex-team.ru/d/'
                        'Ygx9WhhZk'
                        '/nanny_taxi_billing-commissions_stable'
                    ),
                    'testing': (
                        'https://grafana.yandex-team.ru/d/'
                        'GvwEwKhWk'
                        '/nanny_taxi_billing-commissions_testing'
                    ),
                },
                critical_class='A',
            ),
            aliases=[],
        ),
    )


@pytest.fixture(name='yaml_repr_new_preset')
def _yaml_repr_new_preset(uservices_yaml_url):
    service_url = uservices_yaml_url('eats-couriers-equipment')
    return yaml_models.ServiceYamlRepresentation(
        service_type='uservices',
        service_yaml_url=service_url,
        service_name='eats-couriers-equipment',
        wiki_path='https://wiki.yandex-team.ru/taxi/'
        'backend/architecture/eats-couriers-equipment/',
        maintainers=[
            'Karachev Dmitrii <karachevda@yandex-team.ru>',
            'Petrov Mikhail <mvpetrov@yandex-team.ru>',
        ],
        debian_units=[
            yaml_models.DebianUnit(
                name='eats-couriers-equipment',
                tvm_name=None,
                hostnames={
                    'production': ['eats-couriers-equipment.eda.yandex.net'],
                    'testing': ['eats-couriers-equipment.eda.tst.yandex.net'],
                    'unstable': ['eats-couriers-equipment.eda.dev.yandex.net'],
                },
            ),
        ],
        tvm_name='eats-couriers-equipment',
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='eats-couriers-equipment',
                has_unstable=True,
                has_balancers=False,
                clownductor_project='eda',
                preset={
                    'production': {'name': 'x2micro'},
                    'testing': {'name': 'x2nano'},
                    'unstable': {
                        'name': 'x2nano',
                        'overrides': {'cpu': 0.5, 'ram': 2.5},
                    },
                },
                disk_profile={
                    'production': {
                        'name': 'ssd-default',
                        'overrides': [
                            {'path': '/logs', 'size': 50000, 'type': 'ssd'},
                        ],
                        'root_override': {
                            'bandwidth_guarantee_mb_per_sec': 6,
                            'size': 10240,
                            'type': 'ssd',
                            'work_dir_size': 256,
                        },
                    },
                    'testing': {
                        'name': 'ssd-default',
                        'overrides': [
                            {'path': '/logs', 'size': 50000, 'type': 'ssd'},
                        ],
                    },
                    'unstable': {
                        'name': 'ssd-default',
                        'overrides': [
                            {'path': '/logs', 'size': 50000, 'type': 'ssd'},
                        ],
                    },
                },
                abc=None,
                duty_group_id='5b69be79c5755f678048a169',
                design_review='https://st.yandex-team.ru/TAXIARCHREVIEW-265',
                units=['eats-couriers-equipment'],
                description='Service for managing couriers equipment',
                grafana={
                    'production': (
                        'https://grafana.yandex-team.ru/d/'
                        'rPACzomGk/nanny_eda_eats-couriers-equipment_stable'
                    ),
                    'testing': (
                        'https://grafana.yandex-team.ru/d/'
                        'RD4pWomMk/nanny_eda_eats-couriers-equipment_testing'
                    ),
                },
            ),
            aliases=[],
        ),
    )


async def test_parse_uservices(test_parse_yaml, expected_yaml_repr):
    await test_parse_yaml(
        'billing-commissions', 'uservice.yaml', expected_yaml_repr,
    )


async def test_uservices_new_preset(test_parse_yaml, yaml_repr_new_preset):
    await test_parse_yaml(
        'eats-couriers-equipment',
        'uservices_new_preset.yaml',
        yaml_repr_new_preset,
    )
