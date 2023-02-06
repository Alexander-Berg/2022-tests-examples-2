# coding: utf-8

import collections
import logging
import os
import shutil
import tempfile

from sandbox import sandboxsdk
from sandbox import sdk2
from sandbox.common import fs
from sandbox.projects import resource_types
from sandbox.projects.common import constants as const
from sandbox.projects.common.arcadia import sdk as arcadiasdk


logger = logging.getLogger(__name__)


def get_arc_url(revision):
    rev = 'r{}'.format(revision) if revision.isdigit() else revision
    return 'arcadia-arc:/#{}'.format(rev)


def make_arcadia_url(arcadia_url=None, revision=None):
    url = None
    if revision is not None:
        url = get_arc_url(revision)
    else:
        rev = arcadia_url.split('@')[-1]
        url = arcadia_url if rev == 'HEAD' else get_arc_url(rev)
    return url


def convert_lite_test_arg_value(value):
    if isinstance(value, bool):
        value = int(value)
    return str(value)


def convert_lite_test_args_for_ya_make(lite_test_args):
    test_args = None
    if lite_test_args:
        test_args = ' '.join([
            '{}={}'.format(name, convert_lite_test_arg_value(value))
            for name, value in lite_test_args.items()
            if value is not None
        ])
    return test_args or None


def get_unique_file_path(folder_path, file_name):
    # function returns file path instead of name actually
    return fs.get_unique_file_name(str(folder_path), file_name)


class BuildLogsCollector(arcadiasdk.AutoLinks):
    def __init__(self):
        super(BuildLogsCollector, self).__init__()
        self._log_path = tempfile.mkdtemp()
        os.chmod(self._log_path, 0o755)

    @property
    def path(self):
        return self._log_path

    def add(self, name, *args, **kwargs):
        return get_unique_file_path(self._log_path, name)

    def finalize(self, *args, **kwargs):
        pass


class LiteTestRunnerBase(object):
    def __init__(
        self,
        task,
        arc_token=None,
        yt_store_token=None,
        ya_token=None,
        arcadia_url=None,
        revision=None,
        attempts_number=1,
        failed_attempt_callback=None,
    ):
        self._target = 'market/report/lite'
        self._task = task
        self._arc_token = arc_token
        self._yt_store_token = yt_store_token
        self._ya_token = ya_token
        self._arcadia_url = make_arcadia_url(arcadia_url=arcadia_url, revision=revision)
        self._attempts_number = attempts_number
        self._failed_attempt_callback = failed_attempt_callback
        self._arcadia = None
        self._source_root = None

    @property
    def source_root(self):
        self._check_arc_mounted()
        return self._source_root

    def __enter__(self):
        self._set_info('INFO: Mount arcadia url {}'.format(self._arcadia_url))
        self._arcadia = arcadiasdk.mount_arc_path(
            self._arcadia_url,
            use_arc_instead_of_aapi=True,
            arc_oauth_token=self._arc_token,
            fetch_all=False
        )
        self._source_root = self._arcadia.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._arcadia.__exit__(exc_type, exc_value, traceback)
        self._arcadia = None
        self._source_root = None

    def _check_arc_mounted(self):
        if self._arcadia is None:
            raise RuntimeError('Arc not mounted')

    def _run_test_attempts(self, lite_test_args=None, **ya_make_args):
        result = True
        for attempt in range(self._attempts_number):
            try:
                self._set_info('INFO: Try to run tests, attempt {}/{}'.format(attempt + 1, self._attempts_number))
                self._launch_tests(attempt, lite_test_args, **ya_make_args)
                break
            except sdk2.helpers.ProcessLog.CalledProcessError as e:
                if self._handle_exception(e):
                    break
            except sandboxsdk.errors.SandboxSubprocessError as e:
                if self._handle_exception(e):
                    break
            except Exception as e:
                logger.exception(e)
                self._set_info('ERROR: {}'.format(e), do_escape=False)
        else:
            result = False
        return result

    def _set_info(self, msg, *args, **kwargs):
        self._task.set_info(msg, *args, **kwargs)

    def _launch_tests(self, attempt, lite_test_args, **ya_make_args):
        pass

    def _handle_exception(self, exception):
        logger.exception(exception)
        self._set_info('ERROR: {}'.format(exception.get_task_info()), do_escape=False)
        if exception.returncode == arcadiasdk.TEST_FAILED_EXIT_CODE:
            failed_tests = self._parse_test_results()
            self._log_failed_tests(failed_tests)
            if self._failed_attempt_callback is not None and self._failed_attempt_callback(failed_tests):
                return True
        return False

    def _parse_test_results(self):
        return collections.defaultdict(set)

    def _log_failed_tests(self, failed_tests):
        fails = failed_tests.get('fail', set())
        timeouts = failed_tests.get('timeout', set())
        self._set_info(
            'ERROR: Report LITE tests failed:\n* fail: {}\n* timeout: {}'.format(', '.join(fails), ', '.join(timeouts)))

    def _run_ya_make(self, build_system=None, targets=None, **kwargs):
        build_system = build_system or const.SEMI_DISTBUILD_BUILD_SYSTEM
        build_targets = targets or set()
        build_targets.add(self._target)
        build_logs_collector = BuildLogsCollector()
        yt_store_params = arcadiasdk.YtStoreParams(True, self._yt_store_token)
        if self._ya_token is not None:
            if not 'env' in kwargs:
                kwargs['env'] = dict()
            kwargs['env'].update({'YA_TOKEN': self._ya_token})
        try:
            arcadiasdk.do_build(
                build_system=build_system,
                build_type=const.RELEASE_BUILD_TYPE,
                source_root=self._source_root,
                targets=build_targets,
                target_platform='linux',
                clear_build=False,
                yt_store_params=yt_store_params,
                auto_links=build_logs_collector,
                dump_graph_for_debug=False,
                **kwargs
            )
        finally:
            self._save_build_logs(build_logs_collector.path)

    def _save_build_logs(self, build_logs_path):
        if os.path.exists(build_logs_path):
            target_path = get_unique_file_path(self._task.log_resource.path, 'build_logs')
            logger.info('Move build logs {} to {}'.format(build_logs_path, target_path))
            shutil.move(build_logs_path, target_path)

    def _get_last_run_log(self, file_name):
        task_log_path = str(self._task.log_resource.path)
        if not os.path.exists(task_log_path):
            return None
        log_files = sorted([
            os.path.join(task_log_path, name)
            for name in os.listdir(task_log_path)
            if name.startswith(file_name)
        ])
        return log_files[-1] if log_files else None


class LiteTestYaMakeRunner(LiteTestRunnerBase):
    def __init__(self, parent_task, **kwargs):
        super(LiteTestYaMakeRunner, self).__init__(parent_task, **kwargs)
        self._build_path = None
        self._need_build_depends = True
        self._targets = None
        self._resource_store_path = tempfile.mkdtemp()

    def run_tests(self, targets=None, lite_test_args=None, **ya_make_args):
        self._check_arc_mounted()
        self._targets = set(targets or {})
        self._targets.add(self._target)
        self._build_depends(**ya_make_args)
        test_args = convert_lite_test_args_for_ya_make(lite_test_args)
        return self._run_test_attempts(lite_test_args=test_args, **ya_make_args)

    def _build_depends(self, **ya_make_args):
        if not self._need_build_depends:
            return
        self._set_info('INFO: Building depends for targets: {}'.format(', '.join(self._targets)))
        output_path = tempfile.mkdtemp()

        if const.YA_MAKE_EXTRA_PARAMETERS in ya_make_args:
            ya_make_args.get(const.YA_MAKE_EXTRA_PARAMETERS).append('--output={}'.format(output_path))
        else:
            ya_make_args.update({
                const.YA_MAKE_EXTRA_PARAMETERS: ['--output={}'.format(output_path)]
            })

        logger.info('INFO: Ya make extra parameters: {}'.format(', '.join(ya_make_args.get(const.YA_MAKE_EXTRA_PARAMETERS))))

        self._run_ya_make(
            targets=self._targets,
            force_build_depends=True,
            test=False,
            **ya_make_args
        )
        self._need_build_depends = False
        self._build_path = self._task.Context.first_finished_build_system_build_dir
        logger.info('All depends built, build cache: {}'.format(self._build_path))

    def _launch_tests(self, attempt, lite_test_args, **ya_make_args):
        output_path = tempfile.mkdtemp()
        junit_report_path = get_unique_file_path(self._resource_store_path, 'junit_report.xml')

        if const.YA_MAKE_EXTRA_PARAMETERS not in ya_make_args:
            ya_make_args[const.YA_MAKE_EXTRA_PARAMETERS] = list()
        ya_make_args[const.YA_MAKE_EXTRA_PARAMETERS].append('--output={}'.format(output_path))
        if attempt:  # not first attempt
            ya_make_args[const.YA_MAKE_EXTRA_PARAMETERS].append('--last-failed-tests')

        try:
            self._run_ya_make(
                build_system=const.YA_MAKE_FORCE_BUILD_SYSTEM,
                build_dir=self._build_path,
                targets=self._targets,
                force_build_depends=False,
                test=True,
                test_params=lite_test_args,
                cache_test_results=False,
                junit_report_path=junit_report_path,
                **ya_make_args
            )
        finally:
            self._save_junit_report(attempt, junit_report_path)
            self._save_test_results(output_path)

    def _save_junit_report(self, attempt, junit_report_path):
        if os.path.exists(junit_report_path):
            logger.info('Create resourse {} for {}'.format(resource_types.JUNIT_REPORT, junit_report_path))
            descr = 'JUnit report {}'.format(attempt)
            resource = resource_types.JUNIT_REPORT(self._task, descr, os.path.basename(junit_report_path))
            data = sdk2.ResourceData(resource)
            with open(junit_report_path) as f:
                data.path.write_bytes(f.read())
            data.ready()

    def _save_test_results(self, output_path):
        results_name = 'test-results'
        results_path = os.path.join(output_path, self._target, results_name)
        if os.path.exists(results_path):
            log_results_path = get_unique_file_path(self._task.log_resource.path, results_name)
            logger.info('Move test results {} to {}'.format(results_path, log_results_path))
            shutil.move(results_path, log_results_path)

    def _parse_test_results(self):
        failed_tests = collections.defaultdict(set)
        run_log_path = self._get_last_run_log('ya_make.err')
        if run_log_path:
            with open(run_log_path) as run_log:
                for line in run_log:
                    if line.startswith('[fail]') or line.startswith('[timeout]'):
                        parts = line.split(' ')
                        if len(parts) < 2:
                            logger.warn('Unable parse test name, line: %s', line)
                            continue
                        failed_tests[parts[0].strip('[]')].add(parts[1].strip())
        return failed_tests
