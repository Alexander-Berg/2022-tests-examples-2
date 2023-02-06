# -*- coding: utf-8 -*-
import os
import shutil
import re

import sandbox.common.types.client as ctc

from sandbox.sandboxsdk.process import run_process

from sandbox.sandboxsdk import parameters

from sandbox.projects.common.build.CommonBuildTask import CommonBuildTask
import sandbox.projects.common.constants as consts

from sandbox.sandboxsdk.paths import get_logs_folder
from sandbox.sandboxsdk.svn import Arcadia

from sandbox.projects import resource_types
from sandbox.sandboxsdk.errors import SandboxTaskFailureError


class TestSitaUnit(CommonBuildTask):
    type = 'TEST_SITA_UNIT'
    client_tags = ctc.Tag.Group.LINUX

    # sita params
    class BuildUnittests(parameters.SandboxBoolParameter):
        name = 'build_unittests'
        description = 'unittests'

    class BuildSquotaConfigChecker(parameters.SandboxBoolParameter):
        name = 'build_squota_config_checker'
        description = 'squota_config_checker'

    input_parameters = CommonBuildTask.input_parameters + [BuildUnittests, BuildSquotaConfigChecker]

    TARGET_PATH_TO_NAME_MAP = {
        'yweb/robot/sita/ut/yweb-robot-sita-ut': 'unittests',
    }

    TARGET_RESOURCES = (
        (resource_types.KWUNITTESTS, 'yweb/robot/sita/ut/yweb-robot-sita-ut'),
        (resource_types.KWUNITTESTS, 'yweb/robot/sita/tools/squota_config_checker/squota_config_checker'),
    )

    def on_execute(self):

        self.ctx[consts.ARCADIA_URL_KEY] = self.normalize_svn_url(self.ctx[consts.ARCADIA_URL_KEY])

#        #transform to /arcadia root
#        arc_str  = self.ctx[consts.ARCADIA_URL_KEY]
#        arc_list = arc_str.split("/arcadia")
#        arc_root = arc_list[0]
#        if len(arc_list) == 2:
#            self.ctx[consts.ARCADIA_URL_KEY] = arc_root + "/arcadia"
#            arc_rest = arc_list[1]
#            if len(arc_rest.split('@')) == 2:
#                arc_rev  = arc_rest.split('@')[1]
#                self.ctx[consts.ARCADIA_URL_KEY] += "@" + arc_rev
        os.putenv('LD_LIBRARY_PATH', '')
        CommonBuildTask.on_execute(self)

        log_path = get_logs_folder()

        if self.ctx['build_squota_config_checker']:
            # check squota configs
            squota_res = []
            count_ok = 0
            count_err = 0
            squota_config_dir = self.get_arcadia_src_dir() + "/yweb/robot/sita/configs/"
            for fname in self.get_squota_config_files(squota_config_dir):
                try:
                    run_process((self.abs_path()+'/binaries/squota_config_checker %s' % (squota_config_dir+fname)), log_prefix=fname)
                    shutil.copyfile('%s' % (squota_config_dir+fname), log_path + "/%s" % (fname))
                except Exception as e:
                    self.set_info("exception:  %s" % e)

                lines = []
                if os.path.exists(log_path + "/%s.err.txt" % fname):
                    f = open(log_path + "/%s.err.txt" % fname, "r")
                    lines += f.read().splitlines()
                    f.close()
                if os.path.exists(log_path + "/%s.out.txt" % fname):
                    f = open(log_path + "/%s.out.txt" % fname, "r")
                    lines += f.read().splitlines()
                    f.close()

                flag_ok = False
                for l in lines:
                    if l.find("All OK") > -1:
                        flag_ok = True

                if flag_ok:
                    line = "[good] %s::%s" % (fname[0:-4], fname[0:-4])
                    count_ok += 1
                else:
                    line = "[FAIL] %s::%s -> Error in config" % (fname[0:-4], fname[0:-4])
                    count_err += 1

                squota_res.append(line)
                self.set_info(line)

            if count_err:
                squota_res.append("[DONE] ok: %s, err: %s" % (count_ok, count_err))
                self.set_info("[DONE] ok: %s, err: %s" % (count_ok, count_err))
            else:
                squota_res.append("[DONE] ok: %s" % count_ok)
                self.set_info("[DONE] ok: %s" % count_ok)
            self.prepare_junitxml(squota_res, "do_tests_squota_config.out.xml", "squota_config_tests")

        if self.ctx['build_unittests']:
            # run unit tests
            try:
                run_process((self.abs_path()+'/binaries/yweb-robot-sita-ut'), log_prefix='unittests_sita')
            except Exception as e:
                f = open(log_path + "/unittests_sita.err.txt", "r")
                lines = f.read().splitlines()
                f.close()
                self.prepare_junitxml(lines)
                raise SandboxTaskFailureError('FAIL: %s' % e)

            f = open(log_path + "/unittests_sita.out.txt", "r")
            lines = f.read().splitlines()
            f.close()
            self.prepare_junitxml(lines, "do_tests_sita.out.xml", "sita_tests")

#            unittests_sita_process = run_process((os.path.join(self.abs_path(),'binaries', 'robot_sita_tests')),
#                                                 check=False, log_prefix='unittests_sita', outputs_to_one_file=False)
#
#            if unittests_sita_process.returncode:
#                self.prepare_junitxml(unittests_sita_process.stdout_path, "do_tests_sita.out.xml", "sita_tests")
#                raise SandboxTaskFailureError('FAIL: unittests sita process '
#                                              'returns code {0}'.format(unittests_sita_process.returncode))
#            self.prepare_junitxml(unittests_sita_process.stderr_path, "do_tests_sita.out.xml", "sita_tests")

    def prepare_junitxml(self, lines, dir, name):
        report_h = '<?xml version="1.0" encoding="UTF-8"?>'
        report_body = ''
        err_flag = False
        for l in lines:
            if l.split()[0] == '[FAIL]':
                err_flag = True
                report_body += '\n\t<testcase name="%s" classname="%s">' % (l.split()[1].split('::')[1], l.split()[1].split('::')[0])
                report_body += '\n\t\t<failure message="%s"/>' % " ".join(l.split()[3:]).replace('"', "'")
                report_body += '\n\t</testcase>'
            if l.split()[0] == '[good]':
                report_body += '\n\t<testcase name="%s" classname="%s"/>' % (l.split()[1].split('::')[1], l.split()[1].split('::')[0])
            if l.split()[0] == '[DONE]':
                if err_flag:
                    report_h += '\n<testsuite name="%s" tests="%s" failures="%s">' % (name, l.split()[2].split(',')[0], l.split()[4])
                else:
                    report_h += '\n<testsuite name="%s" tests="%s">' % (name, l.split()[2])
        report_body += '\n</testsuite>\n'
        report = report_h + report_body
        log_path = get_logs_folder()
        f = open(log_path + "/%s" % dir, "w")
        f.write(report.replace("&", "&amp;"))
        f.close()

    def get_squota_config_files(self, dir):
        list_files = []
        ldir = os.listdir(dir)
        for f in ldir:
            if os.path.isfile(dir + f) and f.find("squota") > -1 and f.find(".xml") > -1:
                list_files.append(f)
        return list_files

    @staticmethod
    def normalize_svn_url(svn_url):
        svn_path = re.sub(r'/arcadia.*', '/arcadia', Arcadia.parse_url(svn_url).path, count=1)
        return Arcadia.replace(svn_url, path=svn_path)


__Task__ = TestSitaUnit
