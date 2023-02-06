import os
import re

from sandbox import sdk2
from sandbox.common.types import misc as ctm

from .docker_base import DockerBaseMixin
from .processes import ProcessesMixin
from .report import ReportMixin
from .resources import ResourcesMixin


class GriddicTankDockerComposeTest(sdk2.Task,
                                   ReportMixin, ResourcesMixin, DockerBaseMixin, ProcessesMixin):
    """GRIDDIC_TANK_DOCKER_COMPOSE_TEST"""

    class Requirements(sdk2.Requirements):
        privileged = True
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        container = sdk2.parameters.Container(
            "Образ LXC-Контейнера с Docker'ом и Docker Compose'ом",
            default_value=3045926579,  # https://sandbox.yandex-team.ru/task/1293286290/view
            required=True,
        )

        vault_secret_id = sdk2.parameters.YavSecret(
            'Secret with docker credentials.',
            default='sec-01g18rxf0x526sn21pn4b5qt0m'
        )

        tank_image_tag = sdk2.parameters.String(
            "Тэг образ танка для интеграционных тестов.",
            default_value='d64cc36324cebdb5b325a8bb124f41d973a378e0',
            required=True,
        )

        tests_resource_id = sdk2.parameters.String(
            "Ресурс с тестами",
            default_value=3143013052,
        )

    class Context(sdk2.Task.Context):
        tests = []

    def on_execute(self):
        self._download_resource_files()
        self._restart_docker()
        self._login_to_docker_registry()

        with self._docker_compose_started():
            try:
                for _, test_name in self._tests_dirs():
                    self._run_test(test_name)
            finally:
                self._store_tests_with_logs_as_resource()

    def _run_test(self, test_name):
        test_report = {
            'name': test_name,
            'status': 'started',
            'link': None
        }
        self.Context.tests.append(test_report)
        log_lines = []
        try:
            self._run(
                ['docker-compose', 'exec', '-T', 'tank',
                 'tankapi-cmd', '-t', 'localhost', '-c', f'/data/{test_name}/config.yaml'],
                log_lines=log_lines
            )
        except Exception as e:
            run_error = e
            test_report['status'] = 'failed'
        else:
            run_error = None
            test_report['status'] = 'done'

        test_id, link = self._extract_test_id_and_link_from_log_lines(log_lines)
        if test_id:
            self._run('docker-compose exec -T tank '
                      f'cp -r /var/lib/tankapi/tests/{test_id}/ /data/{test_name}/run/{test_id}/'.split())
        if link:
            test_report['link'] = link

        if run_error:
            raise run_error

    def _extract_test_id_and_link_from_log_lines(self, log_lines):
        link = None
        test_id = None
        for line in log_lines:
            if link and test_id:
                break
            if not test_id:
                test_ids = re.findall(r'Got test ID at localhost: (.*)', line)
                if test_ids:
                    test_id = test_ids[0].strip()
            if not link:
                links = re.findall(r'Web link: (.*)', line)
                if links:
                    link = links[0].strip()
        return test_id, link

    @staticmethod
    def _tests_dirs():
        for test_name in os.listdir('data'):
            dir_path = os.path.join('data', test_name)
            if os.path.isdir(dir_path):
                yield dir_path, test_name
