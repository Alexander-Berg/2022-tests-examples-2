import os
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Union

import pytest

SCHEMA = {
    'paths': {
        '/': {
            'get': {
                'description': None,
                'responses': {'200': {'description': 'OK'}},
            },
        },
        '/ping': {
            'x-generator-tags': ['tag1'],
            'get': {
                'summary': 'Ping',
                'responses': {
                    '200': {'description': 'OK'},
                    '500': {'description': 'Guess I die.'},
                },
            },
        },
        '/example/{id}': {
            'get': {
                'summary': 'Example handler',
                'responses': {
                    '405': {'description': 'Method not allowed'},
                    '403': {'description': 'Nah.'},
                },
            },
        },
        '/hello/': {
            'get': {
                'summary': 'International greetings!',
                'responses': {
                    '406': {
                        'description': (
                            'Sadly, this language\n' 'is not supported'
                        ),
                    },
                    '410': {'description': 'This language is dead'},
                },
            },
            'post': {
                'summary': 'Add international greeting',
                'responses': {
                    '422': {
                        'description': 'Sadly, this language is not supported',
                    },
                    '423': {
                        'description': 'This language is locked for adding',
                    },
                },
            },
        },
        '/hello/world': {
            'get': {
                'summary': 'Hello, world!',
                'responses': {
                    '406': {'description': 'Everybody hates you.'},
                    '410': {'description': 'The World is gone.'},
                },
            },
        },
    },
}

DORBLU_INCLUDE = (
    """
    test-service.taxi.yandex.net/custom_GET:
        And:
          - Equals: { http_host: "test-service.taxi.yandex.net" }
          - Equals: { request_method: "GET" }
          - Or: # Custom handler
            - StartsWith: { request_url: "/custom/" }
        Options:
            CustomHttp:
              - 400 # Bad request

""".lstrip(
        '\n',
    )
)

DORBLU_INCLUDE_BLACKLIST = DORBLU_INCLUDE + (
    """
    Monitoring:
        vhost-500:
            Blacklist:
              - StartsWith: {request_url: "/api/custom"}

""".lstrip(
        '\n',
    )
)

COMMON_ADDITIONAL_LAYOUTS = [
    'system',
    {'userver_common': {'collapsed': True, 'uservice_name': '$unit_name'}},
    {'geobus': {'type': 'listener', 'uservice_name': '$unit_name'}},
    {'geobus': {'type': 'publisher', 'uservice_name': '$unit_name'}},
]


class Params(NamedTuple):
    template_dir: str
    project_name: str
    service_group: Optional[Dict] = None
    grafana_additional_layouts: Optional[List] = None
    common_additional_layouts: Optional[List] = None
    units: Optional[Dict] = None
    no_schemas: bool = False
    clownductor_activation: bool = False
    substitute_vars: Optional[Dict[str, dict]] = None
    custom: str = DORBLU_INCLUDE
    environments: Optional[Dict[str, bool]] = None
    awacs_namespace: Union[bool, Dict[str, str]] = False
    hostname_activations: Dict[str, List[str]] = {
        'production': ['test-service.taxi.yandex.net'],
        'testing': [
            'test-service.taxi.tst.yandex.net',
            'test-service-slave.taxi.tst.yandex.net',
        ],
    }


@pytest.mark.parametrize(
    'params',
    [
        Params(
            template_dir='test_generate_conductor',
            service_group={
                'conductor_groups': {
                    'production': 'netaxi_test-service',
                    'testing': 'netaxi_test_test-service',
                },
            },
            grafana_additional_layouts=[
                'rps_share',
                {'userver_common': {'uservice_name': 'test-service'}},
                {
                    'include': {
                        'path': 'xxx',
                        'title': 'title',
                        'variables': {'cluster': '$cluster'},
                    },
                },
            ],
            project_name='netaxi',
        ),
        Params(
            template_dir='test_generate_rtc',
            service_group={'rtc': {'name': 'test-service'}},
            grafana_additional_layouts=['system', 'rps_share'],
            project_name='lavka',
        ),
        Params(
            template_dir='test_generate_environments',
            service_group={'rtc': {'name': 'test-service'}},
            grafana_additional_layouts=['system', 'rps_share'],
            project_name='lavka',
            environments={'production': True, 'testing': False},
        ),
        Params(
            template_dir='test_generate_http_collapse',
            service_group={'rtc': {'name': 'test-service'}},
            grafana_additional_layouts=[
                'system',
                'rps_share',
                {'http': {'collapsed': True}},
            ],
            project_name='lavka',
        ),
        Params(
            template_dir='test_generate_rtc_awacs',
            service_group={'rtc': {'name': 'test-service'}},
            grafana_additional_layouts=['system', 'rps_share'],
            project_name='lavka',
            awacs_namespace=True,
            hostname_activations={
                'production': ['test-service.taxi.yandex.net'],
                'testing': ['test-service.taxi.tst.yandex.net'],
            },
        ),
        Params(
            template_dir='test_generate_rtc_awacs_custom',
            service_group={'rtc': {'name': 'test-service'}},
            grafana_additional_layouts=['system', 'rps_share'],
            project_name='lavka',
            awacs_namespace={'testing': 'no-lb-in-awacs.taxi.tst.yandex.net'},
        ),
        Params(
            template_dir='test_generate_rtc_blacklist',
            service_group={'rtc': {'name': 'test-service'}},
            grafana_additional_layouts=['system', 'rps_share'],
            project_name='lavka',
            custom=DORBLU_INCLUDE_BLACKLIST,
        ),
        Params(
            template_dir='test_generate_rtc_no_hostnames',
            service_group={'rtc': {'name': 'test-service'}},
            project_name='lavka',
            clownductor_activation=True,
            hostname_activations={},
            grafana_additional_layouts=['system'],
        ),
        Params(
            template_dir='test_generate_rtc_no_schemas',
            service_group={'rtc': {'name': 'test-service'}},
            grafana_additional_layouts=[
                'system',
                'rps_share',
                {
                    'include': {
                        'title': 'Hardware Interrupts ${some_var}',
                        'path': 'wmi_export/cpu_interrupts.json',
                    },
                },
            ],
            project_name='taxi',
            no_schemas=True,
            clownductor_activation=True,
            substitute_vars={
                'some_var': {
                    'production': 'On production',
                    'testing': 'On testing',
                },
            },
        ),
    ],
)
def test_dashboards(
        tmpdir, plugin_manager_test, dir_comparator, base_service, params,
):
    repo_dir = tmpdir.mkdir('repo')
    tmp_dir = tmpdir.mkdir('tmp')

    service_yaml_activation = {
        'use_api_flow': False,
        'service_group': params.service_group,
        'grafana_additional_layouts': params.grafana_additional_layouts,
        'dorblu_custom': {
            'production': {'$ref': '../../tmp/dorblu_include.yaml.template'},
        },
        'include_stq_clients': True,
        'project_name': params.project_name,
    }

    if params.substitute_vars:
        service_yaml_activation['substitute_vars'] = params.substitute_vars
    if params.awacs_namespace:
        service_yaml_activation['awacs_namespace'] = params.awacs_namespace

    stq_worker_activation = {
        'stq_workers': ['test_fast_worker', 'test_slow_worker'],
    }

    stq_client_activation = {'stq_clients': ['test_awesome_client']}

    schemas = [SCHEMA]
    if params.no_schemas:
        schemas = []

    web_unit_activation_params = {
        'solomon_cluster_suffixes': {
            'testing': 'testing_cluster',
            'stable': 'production_cluster',
        },
        'schemas': schemas,
    }
    if params.hostname_activations:
        web_unit_activation_params['hostnames'] = params.hostname_activations

    if params.environments:
        web_unit_activation_params['environments'] = params.environments

    class SomePlugin:
        name = 'some-plugin'
        scope = 'unit'
        depends = ['dashboards']

        def __init__(self):
            pass

        @staticmethod
        def configure(manager):
            manager.activate('dashboards', stq_worker_activation)
            manager.activate('dashboards', stq_client_activation)
            manager.activate('dashboards', web_unit_activation_params)

    _write_file(
        os.path.join(tmp_dir, 'dorblu_include.yaml.template'), params.custom,
    )
    service = base_service
    if params.clownductor_activation:
        service_yaml_activation.update({'project_name': params.project_name})

    service['dashboards'] = service_yaml_activation
    plugin_manager_test(repo_dir, service=service, plugins=[SomePlugin])
    template_name = os.path.join('test_dashboards', params.template_dir)
    dir_comparator(repo_dir, template_name)


def _write_file(path: str, data: str):
    with open(path, 'w', encoding='utf-8') as out:
        out.write(data)


def test_generate_multi_units(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    service_yaml_activation = {'use_api_flow': False, 'project_name': 'pn1'}

    class SomePlugin:
        name = 'some-plugin'
        scope = 'unit'
        depends = ['dashboards']

        def __init__(self):
            self.is_active = False
            self.stq = False

        def activate(self, schema: dict):
            self.stq = schema.get('stq', False)
            self.is_active = True

        def configure(self, manager):
            if not self.is_active:
                return
            if self.stq:
                manager.activate('dashboards', {'stq_workers': ['exmpl']})
                return
            manager.activate(
                'dashboards',
                {
                    'schemas': [SCHEMA],
                    'hostnames': {
                        'production': ['service.taxi.yandex.net'],
                        'testing': ['test-service.taxi.yandex.net'],
                    },
                },
            )

    service = base_service
    service['debian'].pop('binary_package_name')
    service['dashboards'] = service_yaml_activation
    plugin_manager_test(
        tmp_dir,
        service=service,
        units={
            'unit0': {
                'debian': {'binary_package_name': 'package-0'},
                'some-plugin': {'stq': True},
            },
            'unit2': {
                'dashboards': {
                    'service_group': {'rtc': {'name': 'rtc2'}},
                    'dashboard_group': 'dg2',
                },
                'debian': {'binary_package_name': 'package-2'},
                'some-plugin': {},
            },
            'unit1': {
                'dashboards': {
                    'service_group': {'rtc': {'name': 'rtc1'}},
                    'dashboard_group': 'dg1',
                },
                'debian': {'binary_package_name': 'package-1'},
            },
            'unit3': {
                'dashboards': {'dashboard_group': 'dg1'},
                'debian': {'binary_package_name': 'package-3'},
                'some-plugin': {'stq': True},
            },
        },
        plugins=[SomePlugin],
    )
    dir_comparator(
        tmp_dir, 'test_dashboards/test_generate_multi_units', 'base',
    )


@pytest.mark.parametrize(
    'service_name, params',
    [
        pytest.param(
            'test-service',
            Params(
                template_dir='test_generate_api_requests',
                service_group={'rtc': {'name': 'test-service'}},
                project_name='taxi-devops',
                custom='',
            ),
            id='all_handlers',
        ),
        pytest.param(
            'test-service',
            Params(
                template_dir='test_generate_api_requests_layouts',
                service_group={'rtc': {'name': 'test-service'}},
                project_name='taxi-devops',
                no_schemas=True,
                custom='',
                grafana_additional_layouts=[
                    {
                        'include': {
                            'title': 'testng layout',
                            'path': 'metrics_panel.json',
                        },
                    },
                ],
            ),
            id='only_layouts_with_parameters',
        ),
        pytest.param(
            'test-service',
            Params(
                template_dir='test_generate_api_requests_custom',
                service_group={'rtc': {'name': 'test-service'}},
                project_name='taxi-devops',
                custom=DORBLU_INCLUDE,
                no_schemas=True,
            ),
            id='only_dorblu_custom',
        ),
        pytest.param(
            'test-service',
            Params(
                template_dir='test_generate_api_requests_conductor',
                service_group={
                    'conductor_groups': {
                        'production': 'taxi_test-service',
                        'testing': 'taxi_unstable_test-service',
                    },
                },
                project_name='taxi-devops',
                custom='',
                no_schemas=True,
                grafana_additional_layouts=[],
            ),
            id='conductor',
        ),
        pytest.param(
            'taxi-test-service',
            Params(
                template_dir='test_generate_api_requests_with_main_alias',
                service_group={'rtc': {'name': 'test-service'}},
                project_name='taxi-devops',
                custom='',
                grafana_additional_layouts=[],
            ),
            id='main_alias_override',
        ),
        pytest.param(
            'test-service',
            Params(
                template_dir=(
                    'test_generate_api_requests_multi_units_'
                    'with_dashboard_groups'
                ),
                project_name='taxi-devops',
                units={
                    'unit0': {
                        'debian': {'binary_package_name': 'package-0'},
                        'dashboards': {
                            'service_group': {'rtc': {'name': 'rtc1'}},
                            'dashboard_group': 'dg1',
                        },
                    },
                    'unit1': {
                        'debian': {'binary_package_name': 'package-1'},
                        'dashboards': {
                            'service_group': {'rtc': {'name': 'rtc2'}},
                            'dashboard_group': 'dg2',
                            'grafana_additional_layouts': [
                                {
                                    'stq': {
                                        'queues': [
                                            'test_queue1',
                                            'test_queue2',
                                        ],
                                    },
                                },
                            ],
                        },
                    },
                },
                common_additional_layouts=COMMON_ADDITIONAL_LAYOUTS,
                custom='',
            ),
            id='test_generate_api_requests_multi_units_with_dashboard_groups',
        ),
    ],
)
def test_generate_api_requests(
        tmpdir,
        plugin_manager_test,
        dir_comparator,
        base_service,
        service_name,
        params,
):
    repo_dir = tmpdir.mkdir('repo')
    tmp_dir = tmpdir.mkdir('tmp')

    service_yaml_activation = {
        'use_api_flow': True,
        'project_name': 'taxi',
        'clownductor_project': params.project_name,
        'clownductor_main_alias': 'test-service',
        'clownductor_aliases': ['test-service'],
    }
    if params.grafana_additional_layouts:
        service_yaml_activation[
            'grafana_additional_layouts'
        ] = params.grafana_additional_layouts
    if params.service_group:
        service_yaml_activation['service_group'] = params.service_group

    class SomePlugin:
        name = 'some-plugin'
        scope = 'unit'
        depends = ['dashboards']

        def __init__(self):
            pass

        def configure(self, manager):
            manager.activate(
                'dashboards',
                {
                    'schemas': [SCHEMA] if not params.no_schemas else [],
                    'hostnames': {
                        'production': [f'test-service.taxi.yandex.net'],
                        'testing': [f'test-service.taxi.tst.yandex.net'],
                    },
                },
            )

    if params.custom:
        _write_file(
            os.path.join(tmp_dir, 'dorblu_include.yaml.template'),
            params.custom,
        )
        service_yaml_activation['dorblu_custom'] = {
            'production': {'$ref': '../../tmp/dorblu_include.yaml.template'},
        }

    service = base_service
    if params.units:
        service['debian'].pop('binary_package_name')
    service['dashboards'] = service_yaml_activation
    plugin_manager_test(
        repo_dir, service=service, units=params.units, plugins=[SomePlugin],
    )
    expected_data_path = os.path.join('test_dashboards', params.template_dir)
    dir_comparator(repo_dir, expected_data_path, 'base')
