import os.path
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Type

import pytest

from codegen import plugin_manager
from codegen import utils


class Repository:
    def __init__(
            self,
            path: str,
            units: Dict[str, Dict[str, Any]],
            service: Dict[str, Any],
            plugins: Iterable[Type],
            generate_debian: bool,
    ) -> None:
        self.root_dir: str = os.path.abspath(path)
        self.service: Service = Service(path, units, service)
        self.plugins: Iterable[Type] = plugins
        self.generate_debian: bool = generate_debian

    def register_plugins(self, manager: plugin_manager.ScopeManager) -> None:
        manager.add_plugins_path(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                os.pardir,
                'codegen',
                'plugins',
            ),
        )
        manager.add_plugins_path('.', PluginsFinder(self.plugins))
        manager.add_params(
            generated_dir=os.path.join(self.root_dir, 'generated'),
            generate_debian=self.generate_debian,
            root_dir=self.root_dir,
            root_build_dir='/path/to/build-dir',
            arcadia_root_dir='/path/to/arcadia',
            yandex_prefixed_name='yandex-taxi-test-service',
        )

        manager.register_scope_plugin(
            name='service',
            scope='service',
            plugin=self.service,
            path=self.service.service_path,
        )


class Service:
    def __init__(
            self,
            repo_path: str,
            units: Dict[str, Dict[str, Any]],
            config: Dict[str, Any],
    ) -> None:
        self.service_name = 'test-service'
        self.service_path = os.path.join(repo_path, self.service_name)
        self.config: Dict[str, Any] = config
        self.units = [Unit(name, cfg) for name, cfg in units.items()]

    def register_plugins(self, manager: plugin_manager.ScopeManager) -> None:
        manager.add_params(
            service_name=self.service_name, service_path=self.service_path,
        )
        for unit in self.units:
            manager.register_scope_plugin(
                name=unit.name,
                scope='unit',
                plugin=unit,
                path=self.service_path,
            )

    def configure(self, manager: plugin_manager.ConfigureManager) -> None:
        for name, config in self.config.items():
            manager.activate(name, config)


class Unit:
    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        self.name: str = name
        self.config: Dict[str, Any] = config

    def register_plugins(self, manager: plugin_manager.ScopeManager) -> None:
        manager.add_params(
            unit_name=self.name,
            yandex_prefixed_name='yandex-taxi-' + self.name,
        )

    def configure(self, manager: plugin_manager.ConfigureManager) -> None:
        for name, config in self.config.items():
            manager.activate(name, config)


class PluginsFinder(plugin_manager.PluginsFinder):
    def __init__(self, plugins: Iterable[Type]) -> None:
        super().__init__()
        self.plugins: Iterable[Type] = plugins

    def load_plugins(
            self, path: utils.PathLike,
    ) -> Iterable[plugin_manager.PluginGenerator]:
        for plugin_cls in self.plugins:
            yield plugin_manager.PluginGenerator(
                generator_cls=plugin_cls,
                generator_args=(),
                name=plugin_cls.name,
                scope=plugin_cls.scope,
                path='.',
                config={},
                depends=getattr(plugin_cls, 'depends', []),
                rdepends=getattr(plugin_cls, 'rdepends', []),
            )


@pytest.fixture
def plugin_manager_test(freeze_time):
    def _plugin_manager_test(
            path: str,
            *,
            units: Optional[Dict[str, Dict[str, Any]]] = None,
            service: Optional[Dict[str, Any]] = None,
            plugins: Iterable[Type] = (),
            generate_debian: bool = True,
    ) -> plugin_manager.PluginManager:
        repo_plugin = Repository(
            path,
            units=units or {'test-service-unit': {}},
            service=service or {},
            plugins=plugins,
            generate_debian=generate_debian,
        )
        manager = plugin_manager.PluginManager(repo_plugin, path)
        manager.init()
        manager.configure()
        manager.generate(parallel=True)
        return manager

    return _plugin_manager_test
