# pylint: disable=redefined-outer-name
import importlib
import itertools
import os
from typing import List
from typing import Optional

import pytest
import yaml

from tools import generate


@pytest.fixture
def run_codegen():
    def gen(argv):
        argv = argv or []
        argv += ['--sequential-codegen']
        return generate.main(argv)

    return gen


@pytest.fixture
def generate_service(tmpdir, monkeypatch, run_codegen, patch):
    def gen(
            package_name: str,
            service_plugins_cfg: Optional[dict] = None,
            unit_plugins_cfg_by_unit_name: Optional[dict] = None,
            swagger_schema: Optional[dict] = None,
            syspath_prepends: Optional[List[str]] = None,
    ):
        swagger_schema_default = {
            'swagger': '2.0',
            'info': {'version': '1.0', 'title': 'hello'},
            'paths': {
                '/ping': {
                    'get': {
                        'operationId': 'Ping',
                        'responses': {'200': {'description': 'OK'}},
                    },
                },
            },
        }
        swagger_schema = swagger_schema or swagger_schema_default
        service_config: dict = {
            'python_service': {
                'service_name': 'some-project',
                'package_name': package_name,
            },
            'debian': {
                'source_package_name': 'yandex-taxi-some-project',
                'maintainer_name': 'seanchaidh',
                'maintainer_login': 'seanchaidh',
            },
            'maintainers': ['Aleksandr Dorodnykh <seanchaidh@yandex-team.ru>'],
            'units': [
                {
                    'name': 'web',
                    'web': {
                        'description': 'Client user app',
                        'log_ident': 'yandex-taxi-some-project',
                        'hostname': {
                            'production': ['app.azaza.ru'],
                            'testing': ['app.test.azaza.ru'],
                        },
                        'num_procs': 1,
                    },
                },
            ],
        }
        service_plugins_cfg = service_plugins_cfg or {}
        unit_plugins_cfg_by_unit_name = unit_plugins_cfg_by_unit_name or {}
        service_config.update(service_plugins_cfg)
        for name, cfg in unit_plugins_cfg_by_unit_name.items():
            for unit in service_config['units']:
                if unit['name'] == name:
                    unit.update(cfg)
                    break
            else:
                raise RuntimeError('No unit was found with name %s' % name)

        all_services_path = str(tmpdir.mkdir(package_name + '_services'))
        service_path = os.path.join(all_services_path, 'service')
        os.makedirs(service_path)

        service_yaml_path = os.path.join(service_path, 'service.yaml')
        with open(service_yaml_path, 'w', encoding='utf-8') as fout:
            yaml.safe_dump(service_config, fout)

        api_docs_dir = os.path.join(service_path, 'docs', 'yaml', 'api')
        os.makedirs(api_docs_dir)
        api_yaml_path = os.path.join(api_docs_dir, 'api.yaml')
        with open(api_yaml_path, 'w', encoding='utf-8') as fout:
            yaml.dump(swagger_schema, fout)

        @patch('codegen.utils.load_yaml')
        def load_yaml(path):
            # pylint: disable=unused-variable
            if os.path.basename(os.path.normpath(path)) == 'services.yaml':
                return {'services': {'directory': all_services_path}}
            with open(path, encoding='utf-8') as fin:
                return yaml.load(fin, getattr(yaml, 'CLoader', yaml.Loader))

        run_codegen(['--services-to-generate', 'service'])
        common_path_prepend = [
            service_path,
            os.path.join('libraries', 'client-http'),
            os.path.join('libraries', 'client-configs'),
            os.path.join('libraries', 'client-localizations'),
        ]
        for path in itertools.chain(
                common_path_prepend, syspath_prepends or [],
        ):
            monkeypatch.syspath_prepend(path)

        return Importer(service_path, package_name, 'web')

    return gen


class Importer:
    def __init__(self, path, package_name, unit_name):
        self.path = path
        self._package_name = package_name
        self._unit_name = unit_name

    @property
    def config_class_name(self):
        return f'{self._package_name}.generated.service.config.plugin.Config'

    def web_context(self):
        return importlib.import_module(
            '%s.generated.%s.web_context'
            % (self._package_name, self._unit_name),
        )

    def middlewares_context(self):
        return importlib.import_module(
            '%s.generated.%s.middlewares_context'
            % (self._package_name, self._unit_name),
        )

    def unit_pytest_plugin(self, plugin_name):
        return importlib.import_module(
            '%s.generated.%s.%s.pytest_plugin'
            % (self._package_name, self._unit_name, plugin_name),
        )

    def service_pytest_plugin(self, plugin_name):
        return importlib.import_module(
            '%s.generated.%s.%s.pytest_plugin'
            % (self._package_name, 'service', plugin_name),
        )
