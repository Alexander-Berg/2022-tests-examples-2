import logging
import signal
import subprocess
import time

import os

import sandbox.projects.vins.vins_perf_test_lib.constants as consts


class Runner(object):
    def __init__(self, vins_package_path, vins_package_name, log_dir):
        self._package_path = vins_package_path
        self._vins_package_name = vins_package_name
        self._log_dir = log_dir
        self._port = None
        self._name = None
        self._pid = None

    def get_address(self):
        return 'localhost:{}'.format(self._port)

    def get_url(self):
        return 'http://' + self.get_address() + '/'

    def _start(self):
        raise NotImplementedError()

    def start(self):
        logging.info('Starting {}...'.format(self._name))
        self._start()
        logging.info('{} started'.format(self._name))

    def _check_started(self, check_status_cmd, successful_answer):
        try_num = 0
        while True:
            try:
                ret = subprocess.check_output([check_status_cmd], shell=True)
                if ret == successful_answer:
                    break
            except subprocess.CalledProcessError, e:
                logging.info('Ping returned: {}'.format(e.returncode))
                time.sleep(consts.WAIT_TIME_BETWEEN_TRIES)
                try_num += 1
                if try_num == consts.RETRY_TIMES_TO_RUN:
                    raise RuntimeError('{} service {} didn\'t start!'.format(self._name, self._vins_package_name))

    def stop(self):
        if self._pid is not None:
            logging.info('Stopping {}...'.format(self._name))
            os.killpg(os.getpgid(self._pid.pid), signal.SIGTERM)
            self._pid.wait()
            self._pid = None


class VinsRunner(Runner):
    def __init__(self, vins_package_path, vins_package_name, log_dir, port=consts.DEFAULT_VINS_PORT,
                 vins_resources_path=None, bass_url=None):
        super(VinsRunner, self).__init__(vins_package_path, vins_package_name, log_dir)
        self._port = port
        self._bass_url = bass_url
        if vins_resources_path:
            self._resources_path = vins_resources_path
        else:
            self._resources_path = os.path.join(self._package_path, 'resources')
        self._name = 'VINS'

    def _start(self):
        logging.info('Setting environment variables...')

        if self._bass_url:
            if os.environ.get('VINS_DEV_BASS_API_URL') is not None:
                logging.warning('Rewrote BASS URL with the local one')
            os.environ['VINS_DEV_BASS_API_URL'] = self._bass_url
        os.environ['VINS_LOG_FILE'] = os.path.join(self._log_dir,
                                                   '{}_{}'.format(self._vins_package_name, consts.VINS_LOG_FILENAME))

        os.environ['VINS_METRICS_FILE'] = os.path.join(self._log_dir, '{}_{}'.format(self._vins_package_name,
                                                                                     consts.VINS_SENSORS_FILENAME))
        service_stdout = os.path.join(self._log_dir,
                                      '{}_{}'.format(self._vins_package_name, consts.VINS_STDOUT_FILENAME))
        work_dir = os.getcwd()
        os.chdir(self._package_path)
        logging.info('env: {}'.format(os.environ))
        with open(service_stdout, 'w+') as logfile:
            pid = subprocess.Popen([
                os.path.join(self._package_path, 'run-vins.py'),
                '--conf-dir', os.path.join(self._package_path, 'cit_configs'),
                '--component', 'speechkit-api-pa',
                '--env', 'shooting-ground',
                '--port', self._port
            ], preexec_fn=os.setsid, stdout=logfile, stderr=subprocess.STDOUT)
        check_status_cmd = 'curl {}ping'.format(self.get_url())
        super(VinsRunner, self)._check_started(check_status_cmd, 'Ok')

        os.chdir(work_dir)
        self._pid = pid

    def vmtouch_resources(self):
        vmtouch_bin = os.path.join(self._resources_path, 'vmtouch')
        res_list = []
        for res in os.listdir(self._resources_path):
            res_list.append(os.path.join(self._resources_path, res))
        subprocess.Popen([vmtouch_bin, '-l', '-v', '-f'] + res_list, stderr=subprocess.STDOUT)


class BassRunner(Runner):
    def __init__(self, vins_package_path, vins_package_name, log_dir, robot_bassist_token, port=consts.DEFAULT_BASS_PORT):
        super(BassRunner, self).__init__(vins_package_path, vins_package_name, log_dir)
        self._robot_bassist_token = robot_bassist_token
        self._port = port
        self._name = 'BASS'

    def _start(self):
        service_stdout = os.path.join(self._log_dir,
                                      '{}_{}'.format(self._vins_package_name, consts.BASS_STDOUT_FILENAME))
        os.mkdir(os.path.join(self._log_dir, '{}_bass_logs'.format(self._vins_package_name)))
        os.environ['ROBOT_BASSIST_VAULT_TOKEN'] = self._robot_bassist_token
        with open(service_stdout, 'w+') as logfile:
            pid = subprocess.Popen([
                os.path.join(self._package_path, 'bin', 'yav_wrapper'),
                '-t', 'ROBOT_BASSIST_VAULT_TOKEN',
                'sec-01cxsqmp818f86wzv3rkshpctq',
                '--',
                os.path.join(self._package_path, 'bin', 'bass_server'),
                '--port', self._port,
                os.path.join(self._package_path, 'bass_configs', 'localhost_config.json'),
                '--logdir', os.path.join(self._log_dir, '{}_bass_logs'.format(self._vins_package_name))
            ], preexec_fn=os.setsid, stdout=logfile, stderr=subprocess.STDOUT)
        check_status_cmd = 'nc -z localhost {}'.format(self._port)
        super(BassRunner, self)._check_started(check_status_cmd, '')
        self._pid = pid


class MegamindRunner(Runner):
    def __init__(self, vins_package_path, vins_package_name, log_dir, robot_bassist_token,
                 port=consts.DEFAULT_MEGAMIND_PORT, vins_url=None, bass_url=None):
        super(MegamindRunner, self).__init__(vins_package_path, vins_package_name, log_dir)
        self._port = port
        self._vins_url = vins_url
        self._bass_url = bass_url
        self._robot_bassist_token = robot_bassist_token
        self._name = 'Megamind'

    def _start(self):
        service_stdout = os.path.join(self._log_dir,
                                      '{}_{}'.format(self._vins_package_name, consts.MEGAMIND_STDOUT_FILENAME))
        args = [
            os.path.join(self._package_path, 'bin', 'yav_wrapper'),
            '-t', 'ROBOT_BASSIST_VAULT_TOKEN',
            'sec-01cxsqmp818f86wzv3rkshpctq',
            '--',
            os.path.join(self._package_path, 'bin', 'megamind_server'),
            '--http-server-http-port', self._port,
            '--config', os.path.join(self._package_path, 'megamind_configs', 'dev', 'megamind.pb.txt'),
            '--vins-like-log-file',
            os.path.join(self._log_dir,
                         '{}_{}'.format(self._vins_package_name, consts.MEGAMIND_VINS_LIKE_LOGS_FILENAME)),
            '--file-sensors',
            os.path.join(self._log_dir, '{}_{}'.format(self._vins_package_name, consts.MM_SENSORS_FILENAME))
        ]
        if self._bass_url:
            args += [
                '--scenarios-sources-bass-url', self._bass_url
            ]
        if self._vins_url:
            args += [
                '--service-sources-vins-url', self._vins_url
            ]
        os.environ['ROBOT_BASSIST_VAULT_TOKEN'] = self._robot_bassist_token
        logging.info('{} args: {}'.format(self._name, args))
        work_dir = os.getcwd()
        os.chdir(self._package_path)
        with open(service_stdout, 'w+') as logfile:
            pid = subprocess.Popen(args, preexec_fn=os.setsid, stdout=logfile, stderr=subprocess.STDOUT)
        check_status_cmd = 'curl {}ping'.format(self.get_url())
        super(MegamindRunner, self)._check_started(check_status_cmd, 'pong')
        os.chdir(work_dir)
        self._pid = pid
