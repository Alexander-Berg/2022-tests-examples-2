# coding: utf-8
import glob
import ipaddress
import os
import logging
import subprocess
import yaml

from sandbox import sdk2
from sandbox.sdk2.ssh import Key
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
import sandbox.common.errors as ce
import sandbox.common.types.resource as ctr
from sandbox.sdk2.service_resources import SandboxTasksBinary
try:  # python3
    from builtins import str as unicode
except ImportError:
    pass


class TankResourse(sdk2.Resource):
    """
    Directory with dockerfile.
    """
    releasable = False
    restart_policy = ctr.RestartPolicy.IGNORE


# noinspection PyTypeChecker
class TestTank(sdk2.Task):
    """
    Job to test Yandextank
    """
    class Requirements(sdk2.Task.Requirements):
        dns = ctm.DnsType.DNS64
        disk_space = 1024
        kill_timeout = 60 * 10

    class Parameters(sdk2.Task.Parameters):
        # pylint: disable=too-few-public-methods
        test_configs_path = sdk2.parameters.String(
            'Path to test configs (Arcadia url)',
            default='arcadia:/arc/trunk/arcadia/load/projects/yandex-tank-internal-pkg/tests'
        )

        with sdk2.parameters.Group('SSH parameters') as ssh_block:
            ssh_vault_name = sdk2.parameters.String(
                'Vault item with ssh key for git access',
                default='robot-lunapark-github-ssh'
            )
            ssh_vault_owner = sdk2.parameters.String('Vault item owner', default='LOAD')
            ssh_user = sdk2.parameters.String('SSH username', default='root')

        with sdk2.parameters.Group('OAuth parameters') as oauth_block:
            oauth_vault_name = sdk2.parameters.String(
                'Vault item with oauth token for registry.yandex.net (vault item name)',
                default='yp-token'
            )
            oauth_vault_owner = sdk2.parameters.String('Vault item owner for oauth token', default='LOAD')
            robot_login = sdk2.parameters.String('Robot login', default='robot-lunapark')

        with sdk2.parameters.Group('YP-Deploy parameters') as yp_deploy_block:
            dc = sdk2.parameters.String(
                'Data centre',
                default='iva'
            )
            deploy_unit_id = sdk2.parameters.String(
                "stage_name.deploy_unit_name",
                default='Yandextank_testing-acceptance.tankapi-cmd-beta'
            )
            yp_common_addr = sdk2.parameters.String(
                'yp domain:port',
                default="yp.yandex.net:8443"
            )
            tank_dns = sdk2.parameters.String(
                'tank DNS',
                default='tank-testing.in.yandex-team.ru'
            )
            tank_port = sdk2.parameters.String(
                'tank port',
                default='80'
            )

        with sdk2.parameters.Output:
            lunapark_test_ids = sdk2.parameters.List(
                'Lunapark tests ids',
                default=[]
            )

        tasks_archive_resource = sdk2.parameters.Integer('Sandbox task binary resource id')
        use_last_binary = sdk2.parameters.Bool('Use last binary archive', default=True)
        with use_last_binary.value[True]:
            with sdk2.parameters.RadioGroup("Binary release type") as ReleaseType:
                ReleaseType.values.stable = ReleaseType.Value('stable', default=True)
                ReleaseType.values.test = ReleaseType.Value('test')

    def on_save(self):
        if self.Parameters.use_last_binary:
            found_task = SandboxTasksBinary.find(
                attrs={'task_name': 'TestTank', 'release': self.Parameters.ReleaseType}
            ).first()
            if found_task is not None:
                self.Requirements.tasks_resource = found_task.id
            else:
                logging.warning("No such binary resource found")
                self.Requirements.tasks_resource = self.Parameters.tasks_archive_resource
        # else:
        #     self.Requirements.tasks_resource = self.Parameters.tasks_archive_resource

    def discover_tankapi_host(self):
        host = "{}.{}".format(self.Parameters.dc, self.Parameters.yp_common_addr)
        token = sdk2.Vault.data(self.Parameters.oauth_vault_owner, self.Parameters.oauth_vault_name)
        from yp.client import YpClient
        client = YpClient(host, transport="http", config={'token': token})

        subnet = client.select_objects(
            object_type="pod",
            selectors=['/status'],
            filter="[/meta/pod_set_id]=\"{}\"".format(self.Parameters.deploy_unit_id)
        )[0][0]['ip6_subnet_allocations'][0]['subnet']

        return ipaddress.ip_network(unicode(subnet))[1]

    def check_subtasks_status(self):
        sub_tasks = self.find()
        task_errors = ''
        for task in sub_tasks:
            if task.status not in ctt.Status.Group.SUCCEED:
                task_errors += 'Subtask {} {} is failed with status {}\n'.format(task.type, task.id, task.status)
        if task_errors:
            raise ce.TaskFailure(task_errors)

    @staticmethod
    def iter_output(cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    @staticmethod
    def __prepare_text_file(filename, form_field_name):
        path = os.path.abspath(filename)
        if not os.path.exists(path):
            raise Exception('File %s does not exist.' % path)
        if not os.path.isfile(path):
            raise Exception('%s is not a filename.' % path)
        return form_field_name, (os.path.basename(filename), open(path, 'rb'), 'text/plain')

    def ssh_tankapi_cmd(self, cmd, host):
        cmd = ['ssh', '-v', '{}@{}'.format(self.Parameters.ssh_user, host), "{}".format(cmd)]
        logging.info(str(cmd))
        return cmd

    # noinspection PyTypeChecker
    def on_execute(self):
        # checkout & prepare configs
        tests_local_path = sdk2.svn.Arcadia.checkout(url=self.Parameters.test_configs_path, path='tests/')
        configs_local_path = os.path.join(tests_local_path, 'configs/')
        configs_list = glob.glob('%s*.yml' % configs_local_path) + glob.glob('%s*.yaml' % configs_local_path)
        logging.info('Configs list:\n{}'.format(configs_list))
        with open(os.path.join(tests_local_path, 'resources.yaml')) as f:
            resources = yaml.load(f)
        lp_ids = []
        errors = []
        # call tankapi-cmd over ssh
        tankapi_host = self.discover_tankapi_host()
        with Key(self, self.Parameters.ssh_vault_owner, self.Parameters.ssh_vault_name):

            self.wait_for_target_to_be_available(tankapi_host)

            for config_name in configs_list:
                with sdk2.helpers.ProcessLog(self, logger='scp_log_%s' % os.path.basename(config_name)) as pl:
                    scp_cmd = ['scp', '{}'.format(config_name),
                               '{}@[{}]:'.format(self.Parameters.ssh_user, tankapi_host)]
                    logging.info('Executing\n>> {}'.format(scp_cmd))
                    scp_retcode = subprocess.call(scp_cmd, stdout=pl.stdout, stderr=pl.stderr)
                    logging.info('scp returned {}'.format(scp_retcode))
                    if int(scp_retcode) != 0:
                        raise Exception('scp failed')

                # download resources
                test_res = resources.get(os.path.basename(config_name))
                if test_res:
                    cmd = '; '.join(['wget {} -O {}'.format(link, fname) for fname, link in test_res.items()])
                    subprocess.call(self.ssh_tankapi_cmd(cmd, tankapi_host))
                    filenames = test_res.keys()
                else:
                    filenames = []

                # run tankapi-cmd
                cmd = 'tankapi-cmd -t {} -p {} -c {} {}'.format(self.Parameters.tank_dns,
                                                                self.Parameters.tank_port,
                                                                os.path.basename(config_name),
                                                                ' '.join(' -f %s' % fname for fname in filenames))
                popen = subprocess.Popen(self.ssh_tankapi_cmd(cmd, tankapi_host),
                                         stdout=subprocess.PIPE, universal_newlines=True)
                logging.info('Started test {}.'.format(os.path.basename(config_name)))
                for stdout_line in iter(popen.stdout.readline, ""):
                    logging.info('tanakapi-cmd stdout: {}'.format(stdout_line))
                    if 'Web link:' in stdout_line:
                        self.Parameters.description = '{dsc}\n:: {msg}'.format(dsc=self.Parameters.description,
                                                                               msg=stdout_line)
                        lp_ids.append(int(stdout_line.split('/')[-1]))
                    elif 'is not available' in stdout_line:
                        popen.terminate()
                        errors.append(stdout_line)
                    elif '[ERROR]' in stdout_line:
                        errors.append(stdout_line)
                popen.stdout.close()
                return_code = popen.wait()
                logging.info('ssh returned {}'.format(return_code))
                if return_code:
                    errors.append("Command '%s' returned non-zero exit status %d" % (cmd, return_code))
        self.Parameters.lunapark_test_ids = lp_ids
        if len(errors) > 0:
            raise Exception('\n'.join(errors))
        self.Parameters.description = link_checker(self.Parameters.description)

    def wait_for_target_to_be_available(self, tankapi_host):
        logging.info('waiting for target: started')
        try:
            timeout = 5 * 60  # seconds
            target = "target.tank-testing.in.yandex-team.ru 80"
            # https://stackoverflow.com/a/50055449
            cmd = """timeout %s bash -c 'until printf "" 2>>/dev/null >>/dev/tcp/$0/$1; do sleep 1; done' """ % timeout
            cmd += target

            popen = subprocess.Popen(
                self.ssh_tankapi_cmd(cmd, tankapi_host),
                stdout=subprocess.PIPE, universal_newlines=True)
            out, err = popen.communicate()
            if popen.returncode != 0:
                logging.error(out)
                logging.error(err)
                raise Exception("target {target} is not available after {timeout} seconds".format(
                    target=target,
                    timeout=timeout,
                ))
        except Exception:
            logging.exception('waiting for target: failed')
            raise
        else:
            logging.info('waiting for target: done')


def link_checker(msg):
    import re
    import requests

    LUNAPARK_URL = 'https://lunapark.yandex-team.ru/'
    HTTP_URL = '{}/api/job/{}/dist/http.json'
    SUMMARY_URL = '{}/api/job/{}/summary.json'

    lunapark_link = r'https?://lunapark.yandex-team.ru/\d{7,8}'
    lunapark_id = r'\d{7,8}'

    links = re.findall(lunapark_link, msg)
    logging.info('[LINK CHECKER] links: %s', links)
    if links:
        links_zwo = []
        sub_string = re.split(lunapark_link, msg)
        for link in links:
            luna_id = re.findall(lunapark_id, link)
            luna_id = luna_id[0] if luna_id else None
            logging.info('[LINK CHECKER] id: %s', luna_id)
            if luna_id:
                state = 'UNKNOWN'
                luna_http = HTTP_URL.format(LUNAPARK_URL, luna_id)
                luna_summary = SUMMARY_URL.format(LUNAPARK_URL, luna_id)
                logging.info('[LINK CHECKER] Request to lunapark: %s', luna_http)
                try:
                    codes = requests.get(luna_http).json()
                    logging.info('[LINK CHECKER] Codes: %s', codes)
                    percent = sum([float(code.get('percent', 0)) for code in codes if (200 <= int(code.get('http', 0)) < 300)])
                    quit_status = requests.get(luna_summary).json()[0].get('quit_status', 1)
                    logging.info('[LINK CHECKER] quit status: %s', quit_status)
                    state = '<span style="color: red">FAIL</span>' if percent < 50 or quit_status else '<span style="color: green">SUCCESS</span>'
                except Exception:
                    logging.error('Failed to get state for shooting %s', luna_id, exc_info=True)
                links_zwo.append('<a href={link}>{link}</a> state:{state}'.format(link=link, state=state))
        return ' '.join(['{} {}'.format(sub_string[i], links_zwo[i]) for i in range(0, len(links_zwo))])
    else:
        return msg
