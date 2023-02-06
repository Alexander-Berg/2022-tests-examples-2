import logging
import os
import shutil
import time
from collections import defaultdict

import sandbox.common.types.client as ctc
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess as sp


class BrowserMobileAllureReport(sdk2.Resource):
    pass


class BrowserMobileAllureSrc(sdk2.Resource):
    pass


class BrowserMobileAppiumLogs(sdk2.Resource):
    pass


class BrowserMobileRunAppiumTests(sdk2.Task):
    DEFAULT_OLD_CONTAINER = 'registry.yandex.net/mbro/appium-android-emulator-x86_64'
    DEFAULT_OLD_CONFIG = 'https://s3.mds.yandex.net/mbro-test-bucket/autotests/images.x86_64.json'

    DEFAULT_NEW_CONTAINER = 'registry.yandex.net/mbro/selenoid-android-emulator-x86_64'
    DEFAULT_NEW_CONFIG = 'https://s3.mds.yandex.net/mbro-test-bucket/autotests/browsers.x86_64.json'

    class Parameters(sdk2.Parameters):
        _container = sdk2.parameters.Container("Container", default_value=1544621795, required=True)
        test_archive = sdk2.parameters.String("Test archive url", required=True)
        test_container = sdk2.parameters.String("Test container name", required=False)
        selenoud_config = sdk2.parameters.String("Selenoud config url", required=False)
        test_parameters = sdk2.parameters.Dict("Test parameters", sdk2.parameters.String, required=True)
        swarm = sdk2.parameters.Bool("Split into multiple tasks", default=False, required=True)
        chunk_size = sdk2.parameters.Integer("Amount of tests for each task when swarmed", default_value=10, required=True)
        new_appium = sdk2.parameters.Bool("Use new appium", default=False, required=True)
        priority = ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)
        kill_timeout = 8 * 60 * 60  # 8 hours

    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.DNS64
        client_tags = ctc.Tag.BROWSER & ctc.Tag.LINUX_TRUSTY
        ram = 8 * 1024
        disk_space = 48 * 1024
        cores = 17

        class Caches(sdk2.Requirements.Caches):
            pass

    def swarm_tests(self, test):
        tests = sorted(test.split(','))
        amount = len(tests) / self.Parameters.chunk_size
        if len(tests) % self.Parameters.chunk_size > self.Parameters.chunk_size / 3:
            amount += 1
        if amount == 0:
            amount = 1
        buckets = defaultdict(list)
        i = 0
        while len(tests) > 0:
            buckets[i].append(tests.pop())
            if i == amount - 1:
                i = 0
            else:
                i += 1
        for v in buckets.values():
            yield ','.join(v)

    def start_task(self, test):
        test_parameters = self.Parameters.test_parameters
        test_parameters['test'] = test
        params = {
            'kill_timeout': self.Parameters.kill_timeout,
            '_container': self.Parameters._container,
            'test_archive': self.Parameters.test_archive,
            'test_container': self.Parameters.test_container,
            'selenoud_config': self.Parameters.selenoud_config,
            'new_appium': self.Parameters.new_appium,
            'test_parameters': test_parameters,
            'swarm': False,
        }
        child_task = BrowserMobileRunAppiumTests(
            self,
            description='Run tests for {}'.format(self.Parameters.description),
            priority=min(
                self.Parameters.priority,
                # default API limitation
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)
            ),
            **params
        )
        child_task.Requirements.tasks_resource = self.Requirements.tasks_resource
        child_task.Requirements.dns = self.Requirements.dns
        child_task.save().enqueue()
        return child_task

    def prepare_vpn_config(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("vpn")) as pl:
            with open('ca.crt', "w+") as f:
                f.write(sdk2.Vault.data('ABRO_VPN_CA'))
            with open('client.conf', "w+") as f:
                f.write(sdk2.Vault.data('ABRO_VPN_CONFIG'))
            with open('client.crt', "w+") as f:
                f.write(sdk2.Vault.data('ABRO_VPN_CRT'))
            with open('client.key', "w+") as f:
                f.write(sdk2.Vault.data('ABRO_VPN_KEY'))
            sp.check_call('sudo mv ca.crt /etc/openvpn/ca.crt', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            sp.check_call('sudo mv client.conf /etc/openvpn/client.conf', shell=True, stdout=pl.stdout,
                          stderr=sp.STDOUT)
            sp.check_call('sudo mv client.crt /etc/openvpn/client.crt', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            sp.check_call('sudo mv client.key /etc/openvpn/client.key', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)

    def set_vpn_enabled(self, state):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("vpn")) as pl:
            if state:
                sp.check_call('sudo service openvpn start', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
                retry(lambda: sp.check_call("sudo ip route add default via $(ip -o -4 a | grep tun0 | awk '{print $4}')", shell=True, stdout=pl.stdout, stderr=sp.STDOUT), count=5, sleep=5, backoff=2)
            else:
                sp.check_call('sudo service openvpn stop', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)

    def prepare_docker(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("docker")) as pl:
            sp.check_call("sudo ip6tables -t nat -A POSTROUTING -s fd00::/8 -j MASQUERADE", shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            sp.check_call('sudo service docker restart', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            sp.check_call(
                'docker login -u robot-mbro-infra -p {} -e robot-mbro-infra@yandex-team.ru registry.yandex.net'.format(
                    sdk2.Vault.data('ROBOT_MBRO_INFRA_DOCKER_REGISTRY_TOKEN')),
                shell=True, stdout=pl.stdout, stderr=sp.STDOUT
            )

            self.download(self.get_container_config(), 'images.json')
            sp.check_call('sudo mv images.json /etc/selenoud/images.json', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)

            sp.check_call('docker pull {}'.format(self.get_test_container()), shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            if self.Parameters.new_appium:
                sp.check_call('docker pull registry.yandex.net/mbro/selenoid', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
                self.run_selenoid()
            else:
                sp.check_call('docker pull registry.yandex.net/mbro/selenoud', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
                self.run_selenoud()

    def run_selenoud(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("selenoud")) as pl:
            java_options = " ".join((
                "-DimagesFile=/etc/selenoud/images.json",
                "-Dlogs.dir=/var/log/selenoud/logs",
                "-Dlimit.count=10",
                "-Dlimit.startupSec=360",
                "-Dlimit.readTimeoutSec=660",
                "-Dlimit.inactivitySec=720",
            ))
            sp.call(
                (
                    'docker run '
                    '-v /etc/selenoud/:/etc/selenoud:ro '
                    '-v /var/log/selenoud/:/var/log/selenoud '
                    '-v /var/run/docker.sock:/var/run/docker.sock '
                    '--name selenoud --privileged --restart=always --net host '
                    '-e JAVA_OPTS="{java_options}" '
                    '-d registry.yandex.net/mbro/selenoud'.format(java_options=java_options)
                ), shell=True, stdout=pl.stdout, stderr=sp.STDOUT
            )

    def run_selenoid(self):
        appium_logs = self.path('appium-logs-volume')
        appium_logs.mkdir(exist_ok=True)

        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("selenoid")) as pl:
            sp.call(
                (
                    'docker run '
                    '-e DOCKER_API_VERSION=1.24 '
                    '-d '
                    '--name selenoid '
                    '-p 4444:4444 '
                    '-v /var/run/docker.sock:/var/run/docker.sock '
                    '-v /etc/selenoud/:/etc/selenoid/:ro '
                    '-v {log_dir}:/opt/selenoid/logs/ '
                    'registry.yandex.net/mbro/selenoid '
                    '-conf /etc/selenoid/images.json '
                    '-service-startup-timeout 300s '
                    '-session-attempt-timeout 300s '
                    '-log-output-dir /opt/selenoid/logs '
                    '-timeout 300s'.format(
                        log_dir=appium_logs,
                    )
                ), shell=True, stdout=pl.stdout, stderr=sp.STDOUT
            )

    def get_test_container(self):
        if self.Parameters.test_container:
            return self.Parameters.test_container
        else:
            return self.DEFAULT_NEW_CONTAINER if self.Parameters.new_appium else self.DEFAULT_OLD_CONTAINER

    def get_container_config(self):
        if self.Parameters.selenoud_config:
            return self.Parameters.selenoud_config
        else:
            return self.DEFAULT_NEW_CONFIG if self.Parameters.new_appium else self.DEFAULT_OLD_CONFIG

    def prepare_emulator(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("emulator")) as pl:
            self.download('https://s3.mds.yandex.net/mbro-test-bucket/autotests/emulator/emulator')
            sp.check_call('sudo mv emulator /opt/android-sdk-linux/tools/emulator', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            sp.check_call('sudo chmod 777 /opt/android-sdk-linux/tools/emulator', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)

    def shutdown_docker(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("docker")) as pl:
            sp.check_call('docker ps -aq | xargs -I {} docker rm -f {} ', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            sp.check_call('sudo service docker stop', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)

    def on_prepare(self):
        if not self.Parameters.swarm:
            self.prepare_docker()
            if not self.Parameters.new_appium:
                self.prepare_emulator()
                self.prepare_vpn_config()
                self.set_vpn_enabled(True)

    def download(self, url, destination=None):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("download")) as pl:
            if destination:
                sp.check_call('wget -O {} {}'.format(destination, url), shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            else:
                sp.check_call('wget {}'.format(url), shell=True, stdout=pl.stdout, stderr=sp.STDOUT)

    def prepare_autotests(self):
        self.download(self.Parameters.test_archive)
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("autotests")) as pl:
            sp.check_call('tar xzf {}'.format(os.path.basename(self.Parameters.test_archive)), shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
            sp.check_call('/opt/apache-maven-3.3.9/bin/mvn install -f autotests', shell=True, stdout=pl.stdout, stderr=sp.STDOUT)

    def make_allure_report(self, allure_results, appium_logs_resource):
        allure_report = self.path('allure-report')
        if appium_logs_resource:
            with open(str(allure_results) + '/environment.properties', 'w') as environment_f:
                environment_f.write('logs={}'.format(appium_logs_resource.http_proxy))
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("report")) as pl:
            sp.check_call(
                '/opt/apache-maven-3.3.9/bin/mvn -B allure:report -Dallure.results.directory={} -Dallure.report.directory={}'.format(
                    str(allure_results), str(allure_report)
                ),
                shell=True, stdout=pl.stdout, stderr=sp.STDOUT
            )
        allure_report_resource = BrowserMobileAllureReport(self, 'Allure report', str(allure_report))
        sdk2.ResourceData(allure_report_resource).ready()

    def collect_child_resources(self, resource_type, destination_path):
        for child_task in self.find():
            resource = resource_type.find(task=child_task).first()
            if resource:
                resource_data = sdk2.ResourceData(resource)
                destination_path.mkdir(exist_ok=True)
                for resource_file in os.listdir(str(resource_data.path)):
                    shutil.copy(str(resource_data.path.joinpath(resource_file)), str(destination_path.joinpath(resource_file)))
            else:
                logging.warning('Failed to get resource {} from {}'.format(str(resource_type), str(child_task)))

    def on_execute(self):
        self.download('https://bitbucket.browser.yandex-team.ru/projects/STARDUST/repos/mobile-functests-runner/raw/func_test_runner/pom.xml?at=refs%2Fheads%2Fmaster', 'pom.xml')

        allure_results = self.path('allure-results')
        allure_results.mkdir(exist_ok=True)

        appium_logs = self.path('appium-logs')
        appium_logs_volume = self.path('appium-logs-volume')

        if self.Parameters.swarm:
            with self.memoize_stage.create_children:
                child_tasks = []
                for test in self.swarm_tests(self.Parameters.test_parameters.pop('test')):
                    child_tasks.append(self.start_task(test))
                raise sdk2.WaitTask(child_tasks, (ctt.Status.Group.FINISH, ctt.Status.Group.BREAK))

            self.collect_child_resources(BrowserMobileAllureSrc, allure_results)
            self.collect_child_resources(BrowserMobileAppiumLogs, appium_logs)
        else:
            self.prepare_autotests()
            with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("run_tests")) as pl:
                if not self.Parameters.new_appium:
                    selenoud_log_path = '/var/log/selenoud/logs'
                    for log_file in os.listdir(selenoud_log_path):
                        sp.check_call('sudo rm {}'.format(os.path.join(selenoud_log_path, log_file)), shell=True, stdout=pl.stdout, stderr=sp.STDOUT)
                self.Parameters.test_parameters['allure.results.directory'] = str(allure_results)
                mvn_params = ['/opt/apache-maven-3.3.9/bin/mvn', 'clean', 'test', '-B']
                for k, v in self.Parameters.test_parameters.iteritems():
                    mvn_params.append('-D{}={}'.format(k, v))
                sp.check_call(mvn_params, stdout=pl.stdout, stderr=sp.STDOUT)
                if not self.Parameters.new_appium:
                    for log_file in os.listdir(selenoud_log_path):
                        shutil.copy(os.path.join(selenoud_log_path, log_file), str(appium_logs.joinpath(log_file)))

        allure_results_resource = BrowserMobileAllureSrc(self, 'Allure report', str(allure_results))
        sdk2.ResourceData(allure_results_resource).ready()

        if os.path.exists(str(appium_logs_volume)) and os.listdir(str(appium_logs_volume)):
            shutil.copytree(str(appium_logs_volume), str(appium_logs))

        if os.path.exists(str(appium_logs)) and os.listdir(str(appium_logs)):
            appium_logs_resource = BrowserMobileAppiumLogs(self, 'Appium logs', str(appium_logs))
            sdk2.ResourceData(appium_logs_resource).ready()
        else:
            appium_logs_resource = None

        if self.Parameters.swarm:
            self.make_allure_report(allure_results, appium_logs_resource)

    def on_finish(self, prev_status, status):
        if not self.Parameters.swarm:
            self.shutdown_docker()
            if not self.Parameters.new_appium:
                self.set_vpn_enabled(False)


def retry(func, count=1, sleep=0, backoff=1):
    for attempts in range(count, 0, -1):
        try:
            return func()
        except Exception:
            if attempts > 1:
                time.sleep(sleep)
                sleep *= backoff
                continue
            raise
