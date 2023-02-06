import importlib
import os


class AlreadyStarted(Exception):
    pass


class Environment:
    def __init__(
            self, worker_id, build_dir, testsuite_dir, env=None):
        self.worker_id = worker_id
        self.build_dir = os.path.abspath(build_dir)
        self.testsuite_dir = os.path.abspath(testsuite_dir)
        self.services = {}
        self.services_start_order = []
        self.env = env

    def ensure_started(self, service_name, **kwargs):
        if service_name not in self.services:
            self.start_service(service_name, **kwargs)

    def start_service(self, service_name, **kwargs):
        if service_name in self.services:
            raise AlreadyStarted(
                'Service \'%s\' is already started' % (service_name,))

        service = self._create_service(service_name, **kwargs)
        service.ensure_started()
        self.services_start_order.append(service_name)
        self.services[service_name] = service

    def stop_service(self, service_name):
        if service_name not in self.services:
            self.services[service_name] = self._create_service(service_name)
        self.services[service_name].stop()

    def close(self):
        while self.services_start_order:
            service_name = self.services_start_order.pop()
            self.stop_service(service_name)
            self.services.pop(service_name)

    def _create_service(self, service_name, **kwargs):
        service_module = importlib.import_module(
            'taxi_tests.environment.services.%s' % service_name,
            )
        return service_module.Service(
            worker_id=self.worker_id,
            build_dir=self.build_dir,
            env=self.env,
            **kwargs,
        )


class TestsuiteEnvironment(Environment):
    def __init__(self, worker_id, build_dir, testsuite_dir, env=None):
        super(TestsuiteEnvironment, self).__init__(
            worker_id, build_dir, testsuite_dir, env,
        )
        worker_suffix = '_' + worker_id if worker_id != 'master' else ''
        testsuite_env = {
            'TAXI_BUILD_DIR': self.build_dir,
            'TAXI_TESTSUITE_DIR': self.testsuite_dir,
            'WORKER_SUFFIX': worker_suffix,
        }
        testsuite_env.update(self.env or {})
        self.env = testsuite_env
