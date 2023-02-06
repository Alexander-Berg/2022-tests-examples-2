import pathlib
import typing

from testsuite import annotations
from testsuite.environment import utils

from . import service


class BaseError(Exception):
    """Base class for exceptions of this module."""


class AlreadyStarted(BaseError):
    pass


class ServiceUnknown(BaseError):
    pass


class Environment:
    worker_id: str
    build_dir: pathlib.Path
    services_start_order: typing.List[str]

    _service_factories: typing.Dict[str, typing.Callable]

    def __init__(
            self,
            worker_id: str,
            build_dir: annotations.PathOrStr,
            reuse_services: bool,
            verbose: int,
            env=None,
    ) -> None:
        self.worker_id = worker_id
        self.build_dir = pathlib.Path(build_dir).resolve()
        self.services: typing.Dict[str, service.ScriptService] = {}
        self.services_start_order = []
        self.reuse_services = reuse_services
        self.env = env
        self._verbose = verbose
        self._service_factories = {}

    def register_service(self, name: str, factory) -> None:
        self._service_factories[name] = factory

    def ensure_started(self, service_name: str, **kwargs) -> None:
        if service_name not in self.services:
            self.start_service(service_name, **kwargs)

    def start_service(self, service_name: str, **kwargs) -> None:
        if service_name in self.services:
            raise AlreadyStarted(
                'Service \'%s\' is already started' % (service_name,),
            )
        script_service = self._create_service(service_name, **kwargs)
        if not (self.reuse_services and script_service.is_running()):
            script_service.ensure_started(verbose=self._verbose)
        self.services_start_order.append(service_name)
        self.services[service_name] = script_service

    def stop_service(self, service_name: str) -> None:
        if service_name not in self.services:
            self.services[service_name] = self._create_service(service_name)
        if not self.reuse_services:
            self.services[service_name].stop(verbose=self._verbose)

    def close(self) -> None:
        while self.services_start_order:
            service_name = self.services_start_order.pop()
            self.stop_service(service_name)
            self.services.pop(service_name)

    def _create_service(
            self, service_name: str, **kwargs,
    ) -> service.ScriptService:
        if service_name not in self._service_factories:
            raise ServiceUnknown(f'Unknown service {service_name} requested')
        service_class = self._service_factories[service_name]
        return service_class(
            service_name=service_name,
            working_dir=self._get_working_dir_for(service_name),
            env=self.env,
            **kwargs,
        )

    def _get_working_dir_for(self, service_name: str) -> pathlib.Path:
        working_dir = self.build_dir.joinpath(
            'testsuite', 'tmp', utils.DOCKERTEST_WORKER, service_name,
        )
        if self.worker_id != 'master':
            return working_dir.joinpath('_' + self.worker_id)
        return working_dir


class TestsuiteEnvironment(Environment):
    def __init__(
            self,
            worker_id: str,
            build_dir: annotations.PathOrStr,
            reuse_services: bool,
            verbose: int,
            env=None,
    ) -> None:
        super(TestsuiteEnvironment, self).__init__(
            worker_id, build_dir, reuse_services, verbose, env,
        )
        worker_suffix = '_' + worker_id if worker_id != 'master' else ''
        testsuite_env = {
            'TAXI_BUILD_DIR': self.build_dir,
            'WORKER_SUFFIX': worker_suffix,
        }
        testsuite_env.update(self.env or {})
        self.env = testsuite_env
