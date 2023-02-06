import pytest

from clownductor.internal.service_yaml import models as yaml_models


@pytest.fixture(name='expected_multi_units')
def _expected_multi_units(uservices_yaml_url):
    service_url = uservices_yaml_url('tags')
    return yaml_models.ServiceYamlRepresentation(
        service_type='uservices',
        service_yaml_url=service_url,
        service_name='tags',
        wiki_path='https://wiki.yandex-team.ru/taxi'
        '/backend/architecture/tags/',
        maintainers=[
            'Dmitrii Raspopov <mordeth@yandex-team.ru>',
            'Aleksei Kokhanov <kokhanov@yandex-team.ru>',
        ],
        debian_units=[
            yaml_models.DebianUnit(
                name='tags',
                tvm_name='tags',
                hostnames={
                    'production': ['tags.taxi.yandex.net'],
                    'testing': ['tags.taxi.tst.yandex.net'],
                    'unstable': ['tags.taxi.dev.yandex.net'],
                },
            ),
            yaml_models.DebianUnit(
                name='passenger-tags',
                tvm_name='passenger-tags',
                hostnames={
                    'production': ['passenger-tags.taxi.yandex.net'],
                    'testing': ['passenger-tags.taxi.tst.yandex.net'],
                    'unstable': ['passenger-tags.taxi.dev.yandex.net'],
                },
            ),
        ],
        tvm_name='tags',
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='tags',
                units=['tags'],
                description='Tags service instance, responsible '
                'for driver entities tagging',
                grafana=None,
            ),
            aliases=[
                yaml_models.ServiceInfo(
                    name='passenger-tags',
                    units=['passenger-tags'],
                    description='Tags service instance, responsible '
                    'for passenger entities tagging',
                    grafana=None,
                ),
            ],
        ),
    )


@pytest.fixture(name='expected_multi_aliases')
def _expected_multi_aliases(uservices_yaml_url):
    service_url = uservices_yaml_url('api-proxy')
    return yaml_models.ServiceYamlRepresentation(
        service_type='uservices',
        service_yaml_url=service_url,
        service_name='api-proxy',
        wiki_path='https://wiki.yandex-team.ru/taxi'
        '/backend/architecture/protocol-4.0/',
        maintainers=[
            'Igor Berezniak <bznk@yandex-team.ru>',
            'Ilya Sidorov <lol4t0@yandex-team.ru>',
        ],
        debian_units=[
            yaml_models.DebianUnit(
                name='api-proxy',
                tvm_name=None,
                hostnames={
                    'production': ['api-proxy.taxi.yandex.net'],
                    'testing': ['api-proxy.taxi.tst.yandex.net'],
                    'unstable': ['api-proxy.taxi.dev.yandex.net'],
                },
            ),
        ],
        tvm_name='api-proxy',
        clownductor_info=yaml_models.ClownductorServiceInfo(
            service=yaml_models.ServiceInfo(
                name='api-proxy',
                units=['api-proxy'],
                description='Provides API for complex handlers',
                grafana={'production': 'grafana'},
            ),
            aliases=[
                yaml_models.ServiceInfo(
                    name='api-proxy-manager',
                    units=['api-proxy-manager'],
                    description='Provides API for complex handlers',
                    grafana={'production': 'grafana'},
                ),
            ],
        ),
    )


@pytest.fixture(name='yaml_new_multi')
def _yaml_new_multi(uservices_yaml_url):
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
                tvm_name='eats-couriers-equipment',
                hostnames={
                    'production': ['eats-couriers-equipment.eda.yandex.net'],
                    'testing': ['eats-couriers-equipment.eda.tst.yandex.net'],
                    'unstable': ['eats-couriers-equipment.eda.dev.yandex.net'],
                },
            ),
            yaml_models.DebianUnit(
                name='eats-couriers-equipment-crit',
                tvm_name='eats-couriers-equipment-crit',
                hostnames={
                    'production': [
                        'eats-couriers-equipment-crit.eda.yandex.net',
                    ],
                    'testing': [
                        'eats-couriers-equipment-crit.eda.tst.yandex.net',
                    ],
                    'unstable': [
                        'eats-couriers-equipment-crit.eda.dev.yandex.net',
                    ],
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
                    'production': {'name': 'default'},
                    'testing': {
                        'name': 'default',
                        'overrides': [
                            {'path': '/logs', 'size': 10000, 'type': 'hdd'},
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
            aliases=[
                yaml_models.ServiceInfo(
                    name='eats-couriers-equipment-crit',
                    has_unstable=True,
                    has_balancers=True,
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
                        'production': {'name': 'default'},
                        'testing': {
                            'name': 'default',
                            'overrides': [
                                {
                                    'path': '/logs',
                                    'size': 10000,
                                    'type': 'hdd',
                                },
                            ],
                        },
                    },
                    abc=None,
                    duty_group_id='5b69be79c5755f678048a169',
                    design_review='https://st.yandex-team.ru/'
                    'TAXIARCHREVIEW-265',
                    units=['eats-couriers-equipment-crit'],
                    description='Service for managing couriers equipment crit',
                    grafana={
                        'production': (
                            'https://grafana.yandex-team.ru/d/'
                            'rPACzomGk/'
                            'nanny_eda_eats-couriers-equipment_stable'
                        ),
                        'testing': (
                            'https://grafana.yandex-team.ru/d/'
                            'RD4pWomMk/'
                            'nanny_eda_eats-couriers-equipment_testing'
                        ),
                    },
                ),
            ],
        ),
    )


async def test_multi_units(test_parse_yaml, expected_multi_units):
    await test_parse_yaml(
        'tags', 'uservices_multi_units.yaml', expected_multi_units,
    )


async def test_multi_aliases(test_parse_yaml, expected_multi_aliases):
    await test_parse_yaml(
        'api-proxy', 'uservices_multi_aliases.yaml', expected_multi_aliases,
    )


async def test_new_multi(test_parse_yaml, yaml_new_multi):
    await test_parse_yaml(
        'eats-couriers-equipment', 'uservices_new_multi.yaml', yaml_new_multi,
    )
