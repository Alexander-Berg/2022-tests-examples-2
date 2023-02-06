# -*- coding: utf-8 -*-

import os
import signal
import shutil
import logging
import json
import errno
import hashlib

from sandbox.sandboxsdk.paths import copy_path

from sandbox.projects import resource_types
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.parameters import LastReleasedResource, SandboxStringParameter
from sandbox.sandboxsdk.svn import ArcadiaTestData


class SaasFmlUtResourceId(LastReleasedResource):
    resource_type = resource_types.SAAS_FML_UNITTEST
    name, description = 'saas_fml_ut_resource_id', 'SAAS FML ut binary'


class PTestDataPath(SandboxStringParameter):
    name, description = 'saas_fml_test_data_path', 'Path to svn with test data for saas_fml_test'
    default_value = ''


class TestSaasFmlUT(SandboxTask):
    type = 'TEST_SAAS_FML_UT'

    input_parameters = [SaasFmlUtResourceId, PTestDataPath]

    def on_execute(self):
        os.chdir(self.abs_path())

        test_binary = self.sync_resource(self.ctx[SaasFmlUtResourceId.name])
        test_data_path = ArcadiaTestData.get_arcadia_test_data(self, self.ctx.get(PTestDataPath.name))

        src_path = self.abs_path('src')
        logging.info("src_path: `{0}`".format(src_path))

        copy_path(test_data_path, src_path, copy_function=shutil.copy2)
        logging.info("success: copy from '{0}' to '{1}'".format(test_data_path, src_path))

        dst_path = self.abs_path('dst')
        self.mkdir_p(dst_path)
        logging.info("success: mkdir '{0}'".format(dst_path))

        config_file = os.path.join(src_path, "config.json")

        request = "task=TExternalTaskGetInternalFMLTable&srcPrefixRedirLog=redir_log&srcPrefixReqAnsLog=saas_reqans_log&periodBegin=20150101&periodEnd=20150101&service=service01&af=json"
        listeningPort = 12127

        cmd = [
            test_binary,
            '--server', 'local',
            '--dstPrefix', 'x',
            '--config', config_file,
            '--request', request,
            '--listeningPort', str(listeningPort),
            '--timeToLive', '30',
            '--testDataSrc', src_path,
            '--testDataDst', dst_path
        ]

        logging.info("cmd: `{0}`".format(' '.join(cmd)))

        logging.info("test_binary:     `{0}`".format(test_binary))
        logging.info("fs_tree: \n`{0}`".format(self.print_fs_tree(test_binary)))
        logging.info("test_data_path:  `{0}`".format(test_data_path))
        logging.info("fs_tree: \n`{0}`".format(self.print_fs_tree(test_data_path)))
        logging.info("self.abs_path(): `{0}`".format(self.abs_path()))
        logging.info("fs_tree: \n`{0}`".format(self.print_fs_tree(self.abs_path())))

        def on_timeout(process):
            process.send_signal(signal.SIGABRT)
            process.communicate()
            self.ctx['task_result_type'] = 'timeout'

        environment = os.environ.copy()
        environment["MR_USER"] = "mr_user"

        logging.info("process start")
        run_process(cmd, log_prefix='test_execution', timeout=45, timeout_sleep=1, on_timeout=on_timeout, environment=environment)
        logging.info("process finish")

        logging.info("self.abs_path(): `{0}`".format(self.abs_path()))
        logging.info("fs_tree: \n`{0}`".format(self.print_fs_tree(self.abs_path())))

        test_fail = False

        with open(config_file) as json_file:
            json_data = json.load(json_file)
            data_fh = json_data['file_hash']

            for file_name, file_md5 in data_fh.items():
                file_path = os.path.join(dst_path, file_name)
                if os.path.isfile(file_path):
                    cur_file_md5 = self.md5_checksum(file_path)
                    if file_md5 == cur_file_md5:
                        logging.info("OK: correct md5 checksum: file`{0}`".format(file_path))
                    else:
                        test_fail = True
                        logging.info("ERROR: incorrect md5 checksum: file: `{0}`; original file md5:{1}, current file md5:{2}".format(file_path, file_md5, cur_file_md5))
                else:
                    test_fail = True
                    logging.info("ERROR: missing file: `{0}`".format(file_path))

        if test_fail:
            self.status = self.Status.FAILURE

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def md5_checksum(self, file_name):
        with open(file_name) as file_to_check:
            data = file_to_check.read()
            file_md5 = hashlib.md5(data).hexdigest()
            return file_md5

    def print_fs_tree(self, startpath):
        res = ''
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            res += '{0}{1}/\n'.format(indent, os.path.basename(root))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                res += '{0}{1}\n'.format(subindent, f)
        return res


__Task__ = TestSaasFmlUT
