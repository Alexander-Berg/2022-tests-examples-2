from sandbox import sdk2, common
from sandbox.common.types.misc import DnsType
from sandbox.common.errors import TaskFailure
from sandbox.projects.common import binary_task
from sandbox.projects.common.vcs.arc import Arc, ArcCommandFailed

import jinja2
import logging
import shutil
import os


# unfortunately we can't use dataclass nor even class in sdk2.Context.
def resource_info(res_type, name, http_proxy):
    return {
        'res_type': res_type,
        'name': name,
        'http_proxy': http_proxy,
    }


ARC_MOUNT_MAX_ATTEMPTS = 5


class TestLog(sdk2.Resource):
    """ Test log """
    pass


class TestLogDir(sdk2.Resource):
    """ Test log directory """
    pass


class TrScriptBundle(sdk2.Resource):
    """ Translation script bundle """
    pass


def mount_arc_with_retries(arc, mount_point, attempt=0):
    try:
        return arc.mount_path(None, None, mount_point=mount_point, fetch_all=False)
    except ArcCommandFailed as e:
        if attempt < ARC_MOUNT_MAX_ATTEMPTS:
            return mount_arc_with_retries(arc, mount_point, attempt + 1)
        else:
            raise e


class MtMtdTrScriptTest(binary_task.LastBinaryTaskRelease, sdk2.Task):
    """
    Run MTD + browser translation script
    """

    class Requirements(sdk2.Requirements):
        cores = 16
        ram = 16000
        disk_space = 16000
        dns = DnsType.DNS64

        # TODO: use latest container (here required move sandbox/projects/mt/product.py to independent PY23_LIBRARY)
        #   to reuse TranslateWebLxcContainer
        container_resource = 2317159860

    class Parameters(sdk2.Parameters):
        description = "Test together MTD + browser translation script"
        arc_pr_id = sdk2.parameters.String("Pull Request ID")
        arc_revision_hash = sdk2.parameters.String("Arc revision hash")
        secret = sdk2.parameters.YavSecret("YAV secret identifier (with optional version)")
        ext_params = binary_task.binary_release_parameters(stable=True)

    class Context(sdk2.Context):
        run_log = None
        log_dir = None
        canon_diff = None
        task_log_names = []

    @sdk2.header(title="Summary")
    def header(self):
        canon_diff = self.Context.canon_diff and self.Context.canon_diff['http_proxy']

        try:  # DEVTOOLSSUPPORT-14041
            template_path = os.path.join(os.path.dirname(__file__), 'header.html')

            template = jinja2.Template(common.fs.read_file(template_path))
            template_context = {
                'resources_info': [
                    self.Context.run_log,
                    self.Context.log_dir,
                    self.Context.canon_diff,
                ] + [
                    self.task_log_resource_info(log_name)
                    for log_name in self.Context.task_log_names
                ],
                'show_recanonize_help': canon_diff,
            }
            return template.render(template_context)

        except Exception as e:
            return 'Exception ' + str(type(e)) + ': ' + str(e)

    def on_execute(self):
        super(MtMtdTrScriptTest, self).on_execute()
        self.Context.task_log_names.append('common.log')

        self.work_dir = os.getcwd()
        self.arc_mount_dir = os.path.join(self.work_dir, 'arc')

        arc_token = self.Parameters.secret.data()['arc-token']
        arc = Arc(arc_oauth_token=arc_token)

        env = {
            'YA_TOKEN': self.Parameters.secret.data()['ya-token'],
            'YT_TOKEN': self.Parameters.secret.data()['yt-token']
        }

        with mount_arc_with_retries(arc, mount_point=self.arc_mount_dir):
            if self.Parameters.arc_revision_hash:
                arc.checkout(self.arc_mount_dir, self.Parameters.arc_revision_hash, force=True)
            elif self.Parameters.arc_pr_id:
                arc.pr_checkout(self.arc_mount_dir, self.Parameters.arc_pr_id)
            else:
                raise RuntimeError('arc: PR id or revision hash must be specified.')

            self.build_bundle()
            test_success = self.run_test(env)

        if not test_success:
            raise TaskFailure('Test run failed')

    def build_bundle(self):
        arc_ui_dir = os.path.join(self.arc_mount_dir, 'dict/mt/web/ui')
        arc_tr_script_bundle_path = os.path.join(self.arc_mount_dir, 'dict/mt/web/ui/dist/scripts/addons/tr_page_bundle.js')

        with sdk2.helpers.ProcessLog(self, logger='build_bundle') as pl:
            sdk2.helpers.subprocess.check_call(
                ['npm', 'install'],
                cwd=arc_ui_dir, stdout=pl.stdout, stderr=pl.stderr,
            )

            sdk2.helpers.subprocess.check_call(
                ['npm', 'run', 'addons:build'],
                cwd=arc_ui_dir, stdout=pl.stdout, stderr=pl.stderr,
            )
        self.Context.task_log_names.append('build_bundle.out.log')
        self.Context.task_log_names.append('build_bundle.err.log')

        self.save_resource(TrScriptBundle, arc_tr_script_bundle_path, copy=True)

    def run_test(self, env):
        page_quality_rel_path = 'dict/mt/web/ui/tools/tr-page-quality'
        test_rel_path = os.path.join(page_quality_rel_path, 'vh/tests_e2e')

        test_output_root = os.path.join(self.work_dir, 'test-output')
        test_result_path = os.path.join(test_output_root, test_rel_path, 'test-results/py3test')

        with sdk2.helpers.ProcessLog(self, logger='tr-page-quality-npm-install') as pl:
            sdk2.helpers.subprocess.check_call(
                ['npm', 'install'],
                cwd=os.path.join(self.arc_mount_dir, page_quality_rel_path), stdout=pl.stdout, stderr=pl.stderr,
            )
        self.Context.task_log_names.append('tr-page-quality-npm-install.out.log')
        self.Context.task_log_names.append('tr-page-quality-npm-install.err.log')

        # TODO(golovanov-i). Run tests_e2e on GPU:
        # 1. Pack $page_quality_rel_path JS files (including: src/, *.js, package.json, package-lock.json)
        # 2. Run test on YT dict/mt/web/ui/tools/tr-page-quality/vh/tests_e2e -tAZ -F "test_mtd_tr_script.py::*" and pass packed JS files to YT env

        with sdk2.helpers.ProcessLog(self, logger='tests_e2e') as pl:
            os.mkdir(test_output_root)
            run_info = sdk2.helpers.subprocess.run(
                [
                    os.path.join(self.arc_mount_dir, "ya"),
                    'make', '-tA', '--test-tag', 'ya:manual', '--show-passed-tests',
                    os.path.join(self.arc_mount_dir, test_rel_path),
                    '--output', test_output_root,
                ],
                cwd=self.arc_mount_dir, env=env,
                stdout=pl.stdout, stderr=pl.stderr,
            )
        self.Context.task_log_names.append('tests_e2e.out.log')
        self.Context.task_log_names.append('tests_e2e.err.log')

        self.save_test_logs(test_result_path)

        success = run_info.returncode == 0
        return success

    def save_resource(self, res_type, path, copy=False):
        if not os.path.exists(path):
            logging.error('Not found file: ' + path)
            return None

        if copy:
            new_path = os.path.join(self.work_dir, os.path.basename(path))
            shutil.copy(path, new_path)
            path = new_path

        res = res_type(self, os.path.basename(path), path)
        sdk2.ResourceData(res).ready()
        return res.http_proxy

    def save_test_logs(self, test_result_path):
        self.Context.log_dir = resource_info(
            'Directory with all test logs', 'log_dir', self.save_resource(TestLogDir, test_result_path),
        )

        canon_diff_dir_rel = 'testing_out_stuff/test_mtd_tr_script.test_translate_with_frozen_models'
        canon_diff_dir = os.path.join(test_result_path, canon_diff_dir_rel)
        if self.Context.log_dir['http_proxy'] and os.path.exists(canon_diff_dir) and os.listdir(canon_diff_dir):
            self.Context.canon_diff = resource_info(
                'Canonization diff', 'canon_diff_dir', os.path.join(self.Context.log_dir['http_proxy'], canon_diff_dir_rel))

        run_log_path = os.path.join(test_result_path, 'test-results/py3test/testing_out_stuff/run.log')
        self.Context.run_log = resource_info(
            'Test main log', os.path.basename(run_log_path), self.save_resource(TestLog, run_log_path, copy=True)
        )

    def task_log_resource_info(self, log_name):
        log_link = 'https://proxy.sandbox.yandex-team.ru/task/{}/log1/{}'.format(self.id, log_name)
        return resource_info(log_name, log_name, log_link)
