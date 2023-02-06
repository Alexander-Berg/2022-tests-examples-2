from sandbox import sdk2
import json
import os
import logging
import math
import sandbox.common.types.task as ctt
from sandbox.projects.catboost.util.resources import (
    CatBoostBinary,
    CatBoostPythonPackageWheel,
    CatBoostRunPythonPackageTrain,
    CatBoostPerformanceEvaluationBinary,
    CatBoostPerfTestJsonTask,
    CatBoostDataPrepParamsJson)
from sandbox.projects.catboost.util.utils import (
    get_ctx_for_make_catboost,
    parse_used_ram_limit)
from sandbox.projects.catboost.make_python_package_wheel import CatBoostMkWheel, MakeCatBoostPythonPackageWheel
from sandbox.projects.catboost.run_perf_test_on_two_binaries import CatBoostRunPerfTestOnTwoBinaries
from sandbox.sdk2.service_resources import SandboxTasksBinary
from sandbox.sandboxsdk.errors import SandboxTaskFailureError

_logger = logging.getLogger(__name__)

_MAX_CORES = 32
_DEFAULT_CPU_RAM_IN_MB = 8 * 1000  # 8 Gb by default to be compatible with previous default
_MAX_CPU_RAM_IN_MB = 128 * 1000


class CatBoostNPerfTestsReport(sdk2.Resource):
    pass


class CatBoostRunNPerfTestsOnTwoBinariesParameters(sdk2.Task.Parameters):
    with sdk2.parameters.Group("speed_bench parameters"):
        with sdk2.parameters.RadioGroup('API type') as api_type:
            api_type.values['cli'] = api_type.Value('cli', default=True)
            api_type.values['python-package'] = api_type.Value('python-package')
        use_last_binary = sdk2.parameters.Bool(
            'use last binary archive',
            default=True, )
        with use_last_binary.value[True]:
            with sdk2.parameters.RadioGroup('Binary release type') as release_type:
                release_type.values['stable'] = release_type.Value('stable', default=True)
                release_type.values['test'] = release_type.Value('test')
        with use_last_binary.value[False]:
            custom_tasks_archive_resource = sdk2.parameters.Resource(
                'task archive resource',
                default=None, )

        run_on_yt = sdk2.parameters.Bool('run on YT', default=False)
        with run_on_yt.value[True]:
            yt_proxy = sdk2.parameters.String('yt proxy to run on', required=True)
            yt_gpu_limit = sdk2.parameters.Integer('yt gpu limit to run with', default=1, required=True)
            yt_pool_tree = sdk2.parameters.String('yt pool_tree to run on', required=True)
        with run_on_yt.value[False]:
            cpu_model_tag = sdk2.parameters.CustomClientTags(
                'CPU model client tag',
                default=sdk2.parameters.ctc.Tag.INTEL_E5_2660V4)

        performance_evaluation_binary = sdk2.parameters.Resource(
            'performance_evaluation binary (arcadia-built)',
            resource_type=CatBoostPerformanceEvaluationBinary,
            default=None, )
        with api_type.value['python-package']:
            with sdk2.parameters.RadioGroup('booster') as booster:
                booster.values['catboost'] = booster.Value('catboost', default=True)
                booster.values['lightgbm'] = booster.Value('lightgbm')
                booster.values['xgboost'] = booster.Value('xgboost')
            run_python_package_train = sdk2.parameters.Resource(
                'run_python_package_train script (not arcadia build python binary!)',
                resource_type=CatBoostRunPythonPackageTrain,
                default=None, )
        use_first_catboost_binary = sdk2.parameters.Bool(
            'use first catboost binary',
            default=False, )
        with use_first_catboost_binary.value[False]:
            first_revision_number = sdk2.parameters.Integer(
                'first revision number',
                default=None, )
        with api_type.value['cli']:
            first_catboost_binary = sdk2.parameters.Resource(
                'first catboost binary',
                resource_type=CatBoostBinary,
                default=None, )
        with api_type.value['python-package']:
            first_catboost_python_package_wheel = sdk2.parameters.Resource(
                'first catboost python package wheel',
                resource_type=CatBoostPythonPackageWheel,
                default=None, )
        first_name = sdk2.parameters.String(
            'first name',
            default='booster_1',)
        first_catboost_additional_args = sdk2.parameters.String('first catboost additional args')
        use_second_catboost_binary = sdk2.parameters.Bool(
            'use second catboost binary',
            default=False, )
        with use_second_catboost_binary.value[False]:
            second_revision_number = sdk2.parameters.Integer(
                'second revision number',
                description='baseline revision',
                default=None, )
        with api_type.value['cli']:
            second_catboost_binary = sdk2.parameters.Resource(
                'second catboost binary',
                resource_type=CatBoostBinary,
                default=None, )
        with api_type.value['python-package']:
            second_catboost_python_package_wheel = sdk2.parameters.Resource(
                'second catboost python package wheel',
                resource_type=CatBoostPythonPackageWheel,
                default=None, )
        second_name = sdk2.parameters.String(
            'second name',
            default='booster_2',)
        second_catboost_additional_args = sdk2.parameters.String('second catboost additional args')
        token_name = sdk2.parameters.String(
            'token name',
            default='yt_token',)
        perf_test_json_task = sdk2.parameters.Resource(
            'json task',
            resource_type=CatBoostPerfTestJsonTask,
            required=True, )
        with api_type.value['python-package']:
            first_data_prep_params_json = sdk2.parameters.Resource(
                'first data prep params json',
                resource_type=CatBoostDataPrepParamsJson,
                default=None, )
            second_data_prep_params_json = sdk2.parameters.Resource(
                'second data prep params json',
                resource_type=CatBoostDataPrepParamsJson,
                default=None, )
        number_of_runs = sdk2.parameters.Integer(
            'number of runs',
            default=1, )
        required_fraction_of_successful_tasks = sdk2.parameters.Float(
            'required fraction of successful tasks',
            default=0.7, )


class CatBoostRunNPerfTestsOnTwoBinaries(sdk2.Task):
    TASK_TYPE = 'CAT_BOOST_RUN_N_PERF_TESTS_ON_TWO_BINARIES'

    def _make_catboost_binary_resource(self, api_type, revision_number):
        if self.Parameters.booster != 'catboost':
            raise Exception('Building binaries is supported only for "booster"=="catboost"')

        if api_type == 'cli':
            task_description = 'Build catboost binary'
            task_type = 'YA_MAKE'
            task_context = get_ctx_for_make_catboost(revision_number)
            task = self.server.task({
                'type': task_type,
                'description': task_description,
                'children': True,
                'owner': self.owner,
                'context': task_context})
            self.server.batch.tasks.start.update([task['id']])
            return task['id']
        elif api_type == 'python-package':
            kwargs = {
                'mk_wheel': CatBoostMkWheel.find(attrs={'release': 'stable'}).first().id,
                'svn_revision': revision_number,
                'with_cuda_support': self.Parameters.run_on_yt and (self.Parameters.yt_gpu_limit > 0)
            }
            make_catboost_python_package_wheel_task = MakeCatBoostPythonPackageWheel(
                self,
                description="Make catboost python package wheel",
                **kwargs
            ).enqueue()
            return make_catboost_python_package_wheel_task.id
        else:
            raise Exception('Bad api_type %s' % api_type)

    def _get_dataset_names(self, catboost_perf_test_json_task):
        dataset_names = []
        json_task_path = str(sdk2.ResourceData(catboost_perf_test_json_task).path)
        with open(json_task_path, 'r') as json_task:
            tasks_dict = json.load(json_task)
        for evaluation_task in tasks_dict:
            dataset_names.append(evaluation_task['name'])
        return dataset_names

    def _get_number_of_required_cores(self, catboost_perf_test_json_task):
        cores = 1
        json_task_path = str(sdk2.ResourceData(catboost_perf_test_json_task).path)
        with open(json_task_path, 'r') as json_task:
            tasks_dict = json.load(json_task)
        for evaluation_task in tasks_dict:
            if self.Parameters.api_type == 'cli':
                params = evaluation_task['cmd_params']
                params = params.split(' ')
                params = [param.strip() for param in params]
                for opt_param in ('-T', '--thread-count', ):
                    if opt_param in params:
                        cores = max(cores, int(params[params.index(opt_param) + 1]))
            elif self.Parameters.api_type == 'python-package':
                params = evaluation_task[self.Parameters.booster + '_train_params']
                thread_count_param_names = {
                    'catboost': ['thread_count'],
                    'lightgbm': ['num_threads', 'num_thread', 'nthread', 'nthreads', 'n_jobs'],
                    'xgboost': ['nthread']
                }[self.Parameters.booster]
                for thread_count_param_name in thread_count_param_names:
                    if thread_count_param_name in params:
                        if self.Parameters.booster == 'lightgbm':
                            # LightGBM recommends setting this param equal to the number of real cores, without
                            # taking hyperthreading into account
                            cores = max(cores, 2 * int(params[thread_count_param_name]))
                        else:
                            cores = max(cores, int(params[thread_count_param_name]))
        return min(cores, _MAX_CORES)

    def _get_required_cpu_ram_in_mb(self, catboost_perf_test_json_task):
        cpu_ram_in_mb = 0
        json_task_path = str(sdk2.ResourceData(catboost_perf_test_json_task).path)
        with open(json_task_path, 'r') as json_task:
            tasks_dict = json.load(json_task)
        for evaluation_task in tasks_dict:
            if self.Parameters.api_type == 'cli':
                params = evaluation_task['cmd_params']
                params = params.split(' ')
                params = [param.strip() for param in params]
                if '--used-ram-limit' in params:
                    cpu_ram_in_mb = max(cpu_ram_in_mb, parse_used_ram_limit(params[params.index('--used-ram-limit') + 1]))
            elif self.Parameters.api_type == 'python-package':
                if self.Parameters.booster != 'catboost':
                    continue
                params = evaluation_task['catboost_train_params']
                if 'used_ram_limit' in params:
                    cpu_ram_in_mb = max(cpu_ram_in_mb, parse_used_ram_limit(params['used_ram_limit']))

        if cpu_ram_in_mb == 0:
            # not set - return default
            return _DEFAULT_CPU_RAM_IN_MB
        return min(cpu_ram_in_mb, _MAX_CPU_RAM_IN_MB)

    def _collect_metrics_from_subtasks(self, dataset_names, binary_number):
        if binary_number == 1:
            training_result_file = 'training_result_on_first_binary.json'
        else:
            training_result_file = 'training_result_on_second_binary.json'
        metrics_dict = {
            dataset_name: {'clean_time': [], 'total_time': [], "max_rss": []} for dataset_name in dataset_names
        }
        for i in range(self.Parameters.number_of_runs):
            if not self.Context.perf_test_task_succeeded[i]:
                continue
            perf_test_task_id = self.Context.perf_test_task_ids[i]
            report_resource = sdk2.Resource["CAT_BOOST_PERF_TEST_REPORT"].find(task_id=perf_test_task_id).first()
            report_path = str(sdk2.ResourceData(report_resource).path)
            for dataset_name in dataset_names:
                try:
                    with open(os.path.join(report_path, dataset_name, training_result_file), 'r') as json_report:
                        cur_metrics_dict = json.load(json_report)
                    for metric in ('clean_time', 'total_time', 'max_rss'):
                        metrics_dict[dataset_name][metric].append(cur_metrics_dict[metric])
                except Exception as e:
                    _logger.exception(e)
        return metrics_dict

    def _aggregate_metrics_from_one_binary(self, metrics_dict, dataset_names):
        metrics = dict()
        quantiles = [50, 75, 90, 95, 99]
        for dataset_name in dataset_names:
            metrics[dataset_name] = {
                'number_of_runs': self.Parameters.number_of_runs,
                'number_of_successful_runs': self.Context.number_of_successful_runs
            }

            for metric in ('clean_time', 'total_time', 'max_rss'):
                metric_values = sorted(metrics_dict[dataset_name][metric])
                def _get_value_or_zero(idx):
                    return 0 if metric_values == [] else metric_values[idx]
                metrics[dataset_name][metric] = {'min': _get_value_or_zero(0), 'max': _get_value_or_zero(-1)}
                for quantile in quantiles:
                    metrics[dataset_name][metric][str(quantile)] = _get_value_or_zero(int(len(metric_values) * (quantile / 100.)))

        return metrics

    def _aggregate_metrics_from_two_binaries(self, first_metrics_dict, second_metrics_dict, dataset_names):
        metrics = dict()
        for dataset_name in dataset_names:
            first_clean_time = sorted(first_metrics_dict[dataset_name]['clean_time'])
            first_total_time = sorted(first_metrics_dict[dataset_name]['total_time'])
            first_max_rss = sorted(first_metrics_dict[dataset_name]['max_rss'])

            second_clean_time = sorted(second_metrics_dict[dataset_name]['clean_time'])
            second_total_time = sorted(second_metrics_dict[dataset_name]['total_time'])
            second_max_rss = sorted(second_metrics_dict[dataset_name]['max_rss'])

            metrics[dataset_name] = {
                'number_of_runs': self.Parameters.number_of_runs,
                'number_of_successful_runs': self.Context.number_of_successful_runs,
                'first_clean_time': first_clean_time[0],
                'first_total_time': first_total_time[0],
                'first_max_rss': first_max_rss[0],
                'second_clean_time': second_clean_time[0],
                'second_total_time': second_total_time[0],
                'second_max_rss': second_max_rss[0],
                'total_time_coef': first_total_time[0] / second_total_time[0],
                'clean_time_coef': first_clean_time[0] / second_clean_time[0]
            }
        return metrics

    def _get_metrics(self):
        dataset_names = self._get_dataset_names(self.Parameters.perf_test_json_task)
        first_metrics_dict = self._collect_metrics_from_subtasks(dataset_names, 1)
        if self.Parameters.use_second_catboost_binary:
            second_metrics_dict = self._collect_metrics_from_subtasks(dataset_names, 2)
            metrics = self._aggregate_metrics_from_two_binaries(first_metrics_dict, second_metrics_dict, dataset_names)
        else:
            metrics = self._aggregate_metrics_from_one_binary(first_metrics_dict, dataset_names)

        with open('training_result.json', 'w') as json_result:
            json.dump(metrics, json_result)
        perf_test_result_res = sdk2.ResourceData(CatBoostNPerfTestsReport(
            self,
            "catbost performance tests result resources", 'training_result.json'))
        perf_test_result_res.ready()

    def _run_perf_test_on_two_binaries(self, perf_test_json_task_id, cores, cpu_ram_in_mb):
        kwargs = {
            'api_type': self.Parameters.api_type,
            'booster': self.Parameters.booster,
            'performance_evaluation_binary': self.Context.performance_evaluation_binary_id,
            'perf_test_json_task': perf_test_json_task_id,
            'number_of_cores': cores,
            'cpu_ram_in_mb': cpu_ram_in_mb,
            'first_name': self.Parameters.first_name,
            'second_name': self.Parameters.second_name,
            'first_catboost_additional_args': self.Parameters.first_catboost_additional_args,
            'second_catboost_additional_args': self.Parameters.second_catboost_additional_args,
            'token_name': self.Parameters.token_name,
            'kill_timeout': self.Parameters.kill_timeout}

        if self.Parameters.run_on_yt:
            kwargs['run_on_yt'] = True
            kwargs['yt_proxy'] = self.Parameters.yt_proxy
            kwargs['yt_gpu_limit'] = self.Parameters.yt_gpu_limit
            kwargs['yt_pool_tree'] = self.Parameters.yt_pool_tree
        else:
            kwargs['cpu_model_tag'] = self.Parameters.cpu_model_tag

        if self.Parameters.api_type == 'cli':
            kwargs['catboost_binary_1'] = self.Context.first_catboost_binary_id
            kwargs['catboost_binary_2'] = self.Context.second_catboost_binary_id
        elif self.Parameters.api_type == 'python-package':
            kwargs['run_python_package_train'] = self.Context.run_python_package_train_id
            kwargs['catboost_python_package_wheel_1'] = self.Context.first_catboost_python_package_wheel_id
            kwargs['catboost_python_package_wheel_2'] = self.Context.second_catboost_python_package_wheel_id
            kwargs['data_prep_params_json_1'] = self.Context.first_data_prep_params_json_id
            kwargs['data_prep_params_json_2'] = self.Context.second_data_prep_params_json_id

        run_catboost_speed_bench_task = CatBoostRunPerfTestOnTwoBinaries(
            self,
            description="run catboost speed bench",
            **kwargs).enqueue()
        return run_catboost_speed_bench_task.id

    class Requirements(sdk2.Requirements):
        cores = 1
        disk_space = 1024  # 1 GB
        ram = 512  # 512 MB

    class Parameters(CatBoostRunNPerfTestsOnTwoBinariesParameters):
        pass

    def _check_task_for_success(self, task_id):
        if self.server.task[task_id].read()["status"] != 'SUCCESS':
            raise SandboxTaskFailureError('error in task {})'.format(task_id))

    def _check_catboost_run_for_success(self, task_id):
        if self.server.task[task_id].read()["status"] != 'SUCCESS':
            self.Context.perf_test_task_succeeded.append(False)
        else:
            self.Context.perf_test_task_succeeded.append(True)
            self.Context.number_of_successful_runs += 1

    def on_save(self):
        if self.Parameters.use_last_binary:
            self.Requirements.tasks_resource = SandboxTasksBinary.find(
                attrs={'target': 'catboost/bin', 'release': self.Parameters.release_type or 'stable'}
            ).first().id
        else:
            self.Requirements.tasks_resource = self.Parameters.custom_tasks_archive_resource

    def on_execute(self):
        if self.Parameters.performance_evaluation_binary is None:
            self.Context.performance_evaluation_binary_id = CatBoostPerformanceEvaluationBinary.find(
                attrs={'release': 'stable'}
            ).first().id
        else:
            self.Context.performance_evaluation_binary_id = self.Parameters.performance_evaluation_binary.id

        if self.Parameters.api_type == 'python-package':
            if self.Parameters.run_python_package_train is None:
                self.Context.run_python_package_train_id = CatBoostRunPythonPackageTrain.find(
                    attrs={'release': 'stable'}
                ).first().id
            else:
                self.Context.run_python_package_train_id = self.Parameters.run_python_package_train.id

        self.Context.second_catboost_binary_id = None
        self.Context.first_catboost_python_package_wheel_id = None
        self.Context.second_catboost_python_package_wheel_id = None

        with self.memoize_stage.make_first_catboost_binaries:
            if not self.Parameters.use_first_catboost_binary and (self.Parameters.booster == 'catboost'):
                self.Context.first_catboost_binary_task_id = self._make_catboost_binary_resource(
                    self.Parameters.api_type,
                    self.Parameters.first_revision_number)

        with self.memoize_stage.make_sacond_catboost_binaries:
            if not self.Parameters.use_second_catboost_binary and self.Parameters.second_revision_number is not None:
                self.Context.second_catboost_binary_task_id = self._make_catboost_binary_resource(
                    self.Parameters.api_type,
                    self.Parameters.second_revision_number)

        with self.memoize_stage.wait_first_catboost_binaries:
            if not self.Parameters.use_first_catboost_binary and (self.Parameters.booster == 'catboost'):
                raise sdk2.WaitTask(self.Context.first_catboost_binary_task_id, ctt.Status.Group.SUCCEED + ctt.Status.Group.FINISH + ctt.Status.Group.BREAK)

        with self.memoize_stage.wait_sacond_catboost_binaries:
            if not self.Parameters.use_second_catboost_binary and self.Parameters.second_revision_number is not None:
                raise sdk2.WaitTask(self.Context.second_catboost_binary_task_id, ctt.Status.Group.SUCCEED + ctt.Status.Group.FINISH + ctt.Status.Group.BREAK)

        if not self.Parameters.use_first_catboost_binary and (self.Parameters.booster == 'catboost'):
            self._check_task_for_success(self.Context.first_catboost_binary_task_id)

        if not self.Parameters.use_second_catboost_binary and self.Parameters.second_revision_number is not None:
            self._check_task_for_success(self.Context.second_catboost_binary_task_id)

        if self.Parameters.use_first_catboost_binary:
            if self.Parameters.api_type == 'cli':
                self.Context.first_catboost_binary_id = self.Parameters.first_catboost_binary.id
            elif self.Parameters.api_type == 'python-package':
                self.Context.first_catboost_python_package_wheel_id = self.Parameters.first_catboost_python_package_wheel.id
        elif self.Parameters.booster == 'catboost':
            if self.Parameters.api_type == 'cli':
                self.Context.first_catboost_binary_id = sdk2.Resource['CAT_BOOST_BINARY'].find(
                    task_id=self.Context.first_catboost_binary_task_id).first().id
            elif self.Parameters.api_type == 'python-package':
                self.Context.first_catboost_python_package_wheel_id = sdk2.Resource['CAT_BOOST_PYTHON_PACKAGE_WHEEL'].find(
                    task_id=self.Context.first_catboost_binary_task_id).first().id

        if self.Parameters.use_second_catboost_binary:
            if self.Parameters.api_type == 'cli':
                self.Context.second_catboost_binary_id = self.Parameters.second_catboost_binary.id
            elif self.Parameters.api_type == 'python-package':
                self.Context.second_catboost_python_package_wheel_id = self.Parameters.second_catboost_python_package_wheel.id
        elif self.Parameters.second_revision_number is not None:
            if self.Parameters.api_type == 'cli':
                self.Context.second_catboost_binary_id = sdk2.Resource['CAT_BOOST_BINARY'].find(
                    task_id=self.Context.second_catboost_binary_task_id).first().id
            elif self.Parameters.api_type == 'python-package':
                self.Context.second_catboost_python_package_wheel_id = sdk2.Resource['CAT_BOOST_PYTHON_PACKAGE_WHEEL'].find(
                    task_id=self.Context.second_catboost_binary_task_id).first().id

        self.Context.perf_test_json_task_id = self.Parameters.perf_test_json_task.id

        self.Context.first_data_prep_params_json_id = None
        self.Context.second_data_prep_params_json_id = None
        if self.Parameters.first_data_prep_params_json:
            self.Context.first_data_prep_params_json_id = self.Parameters.first_data_prep_params_json.id
        if self.Parameters.second_data_prep_params_json:
            self.Context.second_data_prep_params_json_id = self.Parameters.second_data_prep_params_json.id

        with self.memoize_stage.run_n_speed_bench:
            self.Context.perf_test_task_ids = []
            cores = self._get_number_of_required_cores(self.Parameters.perf_test_json_task)
            cpu_ram_in_mb = self._get_required_cpu_ram_in_mb(self.Parameters.perf_test_json_task)
            for i in range(self.Parameters.number_of_runs):
                self.Context.perf_test_task_ids.append(self._run_perf_test_on_two_binaries(
                    perf_test_json_task_id=self.Context.perf_test_json_task_id,
                    cores=cores,
                    cpu_ram_in_mb=cpu_ram_in_mb))

        self.Context.perf_test_task_succeeded = []
        self.Context.number_of_successful_runs = 0
        for i in range(self.Parameters.number_of_runs):
            with self.memoize_stage['wait_perf_test_{}'.format(str(i))]:
                raise sdk2.WaitTask(self.Context.perf_test_task_ids[i], ctt.Status.Group.SUCCEED + ctt.Status.Group.FINISH + ctt.Status.Group.BREAK)
            self._check_catboost_run_for_success(self.Context.perf_test_task_ids[i])

        if math.ceil(self.Parameters.number_of_runs * self.Parameters.required_fraction_of_successful_tasks) > self.Context.successful_task_count:
            failure_task_count = self.Parameters.number_of_runs - self.Context.number_of_successful_runs
            raise SandboxTaskFailureError("failure task count too big({} of {})".format(str(failure_task_count), str(self.Parameters.number_of_runs)))

        self._get_metrics()
