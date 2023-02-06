from contextlib import contextmanager


class DockerBaseMixin:
    def _restart_docker(self):
        try:
            self._run(['systemctl', 'restart', 'docker'])
        finally:
            self._collect_debug_info_about_docker()

    def _collect_debug_info_about_docker(self):
        self._run_ignoring_errors(['systemctl', 'status', 'docker'])
        self._run_ignoring_errors(['journalctl', '-u', 'docker'])
        self._run_ignoring_errors(['docker', 'info'])

    def _login_to_docker_registry(self):
        secrets = self.Parameters.secret_with_registry_password.data()
        docker_login = self.Parameters.docker_registry_user
        docker_password = secrets['REGISTRY_PASSWORD']

        self._run('docker login -u {login} -p {token} registry.yandex.net'.format(
            login=docker_login,
            token=docker_password,
        ).split())

    @contextmanager
    def _docker_compose_started(self):
        self._run('docker-compose up -d'.split())
        try:
            yield
        finally:
            self._run('docker-compose down'.split())
