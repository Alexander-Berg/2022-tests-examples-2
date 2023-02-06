# -*- coding: utf-8 -*-
import platform
import socket
import subprocess

import mock


TEST_IP = '1::2:3:4'
TEST_HOSTNAME = 'passport-secret-host-f99.yandex.net'


def build_ip_mock(ip):
    def _get_addr_info(fqdn, ip_family):
        if ip_family == socket.AF_INET6:
            return ip
        else:
            raise socket.error()

    return mock.Mock(side_effect=_get_addr_info)


class FakeEnvironment(object):
    def __init__(self, hostname=TEST_HOSTNAME, ip=TEST_IP, env_name='localhost', env_type='production', cpu_count=16):
        self.patches = [
            mock.patch('passport.backend.library.nginx_config_generator.configs.get_ip', build_ip_mock(ip)),
            mock.patch('passport.backend.library.nginx_config_generator.configs.get_fqdn', mock.Mock(return_value=hostname)),
            mock.patch('passport.backend.library.nginx_config_generator.configs.yenv.name', env_name),
            mock.patch('passport.backend.library.nginx_config_generator.configs.yenv.type', env_type),
            mock.patch('passport.backend.library.nginx_config_generator.configs.cpu_count', mock.Mock(return_value=cpu_count)),
        ]

    def start(self):
        for patch in self.patches:
            patch.start()

    def stop(self):
        for patch in reversed(self.patches):
            patch.stop()


def assert_configs_ok(actual_dir, expected_dir):
    if platform.system() == 'Darwin':
        diff_cmd = [
            'diff',
            actual_dir,
            expected_dir,
            '-u',
            '--exclude=.gitkeep',
            '--ignore-blank-lines',
            '--ignore-tab-expansion',
            '--ignore-space-change',
        ]
    else:
        diff_cmd = [
            'diff',
            actual_dir,
            expected_dir,
            '-u',
            '--ignore-blank-lines',
            '--ignore-trailing-space',
            '--exclude=.gitkeep',
        ]

    proc = subprocess.Popen(
        diff_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    assert stdout == b'', stdout.decode('utf8')
    assert stderr == b'', stderr.decode('utf8')
