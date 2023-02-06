import datetime
import json
import time
from sandbox import sdk2
import logging
import sandbox.common.types.task as ctt
from sandbox.projects.catboost.util.resources import (
    CatBoostBinary,
    CatBoostPythonPackageWheel,
    CatBoostRunPythonPackageTrain,
    CatBoostPerformanceEvaluationBinary,
    CatBoostPerfTestJsonTask,
    CatBoostDataPrepParamsJson)
from sandbox.projects.catboost.run_n_perf_tests_on_two_binaries import CatBoostRunNPerfTestsOnTwoBinaries
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sdk2.service_resources import SandboxTasksBinary
from sandbox.sandboxsdk import svn

_logger = logging.getLogger(__name__)


class CatBoostPerfTestMetricsReport(sdk2.Resource):
    pass


class CatBoostPerfTestTablesReport(sdk2.Resource):
    pass


class RunCatBoostPerfTestAndPushScoreParameters(sdk2.Task.Parameters):
    with sdk2.parameters.Group("CatBoost performance test parameters"):
        with sdk2.parameters.RadioGroup('API type') as api_type:
            api_type.values['cli'] = api_type.Value('cli', default=True)
            api_type.values['python-package'] = api_type.Value('python-package')
        use_last_binary = sdk2.parameters.Bool(
            'use last binary archive',
            default=True,)
        with use_last_binary.value[True]:
            with sdk2.parameters.RadioGroup('Binary release type') as release_type:
                release_type.values['stable'] = release_type.Value('stable', default=True)
                release_type.values['test'] = release_type.Value('test')
        with use_last_binary.value[False]:
            custom_tasks_archive_resource = sdk2.parameters.Resource(
                'task archive resource',
                default=None,)

        run_on_yt = sdk2.parameters.Bool('run on YT', default=False)
        with run_on_yt.value[True]:
            yt_proxy = sdk2.parameters.String('yt proxy to run on', required=True)
            yt_gpu_limit = sdk2.parameters.Integer('yt gpu limit to run with', default=1, required=True)
            yt_pool_tree = sdk2.parameters.String('yt pool_tree to run on', required=True)

        performance_evaluation_binary = sdk2.parameters.Resource(
            'performance_evaluation binary (arcadia-built)',
            resource_type=CatBoostPerformanceEvaluationBinary,
            default=None, )
        with api_type.value['python-package']:
            run_python_package_train = sdk2.parameters.Resource(
                'run_python_package_train script (not arcadia build python binary!)',
                resource_type=CatBoostRunPythonPackageTrain,
                default=None, )
        use_catboost_binary = sdk2.parameters.Bool(
            'use catboost binary',
            default=False,)
        with use_catboost_binary.value[False]:
            revision_number = sdk2.parameters.Integer(
                'revision number',
                default=None,)
        with use_catboost_binary.value[True]:
            catboost_binary = sdk2.parameters.Resource(
                'catboost binary',
                resource_type=CatBoostBinary,
                default=None,)
        with use_catboost_binary.value[True]:
            catboost_python_package_wheel = sdk2.parameters.Resource(
                'catboost python package wheel',
                resource_type=CatBoostPythonPackageWheel,
                default=None,)
        catboost_name = sdk2.parameters.String(
            'catboost name',
            default='catboost',)
        push_result_to_yt_table = sdk2.parameters.Bool(
            'push result to yt table',
            default=False,)
        with push_result_to_yt_table.value[True]:
            metrics_table_proxy = sdk2.parameters.String(
                'metrics table proxy',
                default='hahn.yt.yandex.net',)
            metrics_table_path = sdk2.parameters.String(
                'metrics table path',
                required=True,)
            create_metrics_table = sdk2.parameters.Bool(
                'create metrics table',
                default=False,)
        token_name = sdk2.parameters.String(
            'token name',
            default='yt_token',)
        push_result_to_pulsar = sdk2.parameters.Bool(
            'push result to Pulsar',
            default=False,)
        with push_result_to_pulsar.value[True]:
            pulsar_model_name = sdk2.parameters.String(
                'Pulsar model name',
                required=True,)
            pulsar_token_name = sdk2.parameters.String(
                'Pulsar token name',
                default='pulsar_token',)
            pulsar_metadata_json = sdk2.parameters.String(
                'Extra metadata to add to Pulsar model options',
                default='',)
        perf_test_json_task = sdk2.parameters.Resource(
            'json task',
            resource_type=CatBoostPerfTestJsonTask,
            required=True,)
        with api_type.value['python-package']:
            data_prep_params_json = sdk2.parameters.Resource(
                'data prep params json',
                resource_type=CatBoostDataPrepParamsJson,
                default=None,)
        number_of_runs = sdk2.parameters.Integer(
            'number of runs',
            default=1,)
        required_fraction_of_successful_tasks = sdk2.parameters.Float(
            'required fraction of successful tasks',
            default=0.7,)


class RunCatBoostPerfTestAndPushScore(sdk2.Task):

    # data_prep_params_json_id can be None
    def _run_perf_test(self, use_binary, revision_number, json_task_id, data_prep_params_json_id, number_of_runs):
        kwargs = {
            'api_type': self.Parameters.api_type,
            'booster': 'catboost',
            'perf_test_json_task': json_task_id,
            'number_of_runs': number_of_runs,
            'required_fraction_of_successful_tasks': self.Parameters.required_fraction_of_successful_tasks,
            'token_name': self.Parameters.token_name,
            'kill_timeout': self.Parameters.kill_timeout}

        if self.Parameters.run_on_yt:
            kwargs['run_on_yt'] = True
            kwargs['yt_proxy'] = self.Parameters.yt_proxy
            kwargs['yt_gpu_limit'] = self.Parameters.yt_gpu_limit
            kwargs['yt_pool_tree'] = self.Parameters.yt_pool_tree

        if self.Parameters.performance_evaluation_binary:
            kwargs['performance_evaluation_binary'] = self.Parameters.performance_evaluation_binary.id

        if use_binary:
            kwargs['use_first_catboost_binary'] = True
            if self.Parameters.api_type == 'cli':
                kwargs['first_catboost_binary'] = self.Parameters.catboost_binary.id
            elif self.Parameters.api_type == 'python-package':
                kwargs['first_catboost_python_package_wheel'] = self.Parameters.catboost_python_package_wheel.id
        else:
            kwargs['use_first_catboost_binary'] = False
            kwargs['first_revision_number'] = revision_number

        if self.Parameters.api_type == 'python-package':
            kwargs['first_data_prep_params_json'] = data_prep_params_json_id
            if self.Parameters.run_python_package_train:
                kwargs['run_python_package_train'] = self.Parameters.run_python_package_train.id

        run_perf_test_task = CatBoostRunNPerfTestsOnTwoBinaries(
            self,
            description="run perf test",
            **kwargs).enqueue()
        return run_perf_test_task.id

    def _create_metrics_table(self, yt_client, table_path):
        schema = [
            {"name": "date", "type": "double"},
            {"name": "dataset_name", "type": "string"},
            {"name": "arcadia_svn_revision", "type": "int64"},
            {"name": "number_of_runs", "type": "int64"},
            {"name": "number_of_successful_runs", "type": "int64"}]

        for metric in ('clean_time', 'total_time', 'max_rss'):
            schema.append({"name": "min_" + metric, "type": "double"})
            schema.append({"name": "max_" + metric, "type": "double"})
            for quantile in ('0.50', '0.75', '0.90', '0.95', '0.99'):
                schema.append({"name": metric + "_" + quantile, "type": "double"})

        if self.Parameters.api_type == 'cli':
            schema.append({"name": "binary_sandbox_id", "type": "int64"})
        elif self.Parameters.api_type == 'python-package':
            schema.append({"name": "python_package_wheel_sandbox_id", "type": "int64"})

        yt_client.create('table', table_path, attributes={"schema": schema, "optimize_for": "scan"})

    def _append_metrics_to_table(self, yt_client, table_path, rows):
        import yt.wrapper as yt

        with yt_client.Transaction():
            if not yt_client.exists(table_path):
                self._create_metrics_table(yt_client, table_path)
            yt_client.write_table(yt.TablePath(table_path, append=True), rows, format='json')

    def _get_json_from_resource(self, perf_test_json_task):
        json_task_path = str(sdk2.ResourceData(perf_test_json_task).path)
        with open(json_task_path, 'r') as json_task:
            return json.load(json_task)

    def _get_dataset_names(self, perf_test_json_task):
        dataset_names = []
        tasks_list = self._get_json_from_resource(perf_test_json_task)
        for evaluatioon_task in tasks_list:
            dataset_names.append(evaluatioon_task['name'])
        return dataset_names

    def _get_date_of_revision(self, revision_number):
        info = svn.Arcadia.info('arcadia:/arc/trunk/arcadia@{}'.format(str(revision_number)))
        date_of_revision = 0
        if 'date' in info:
            date_of_revision = time.mktime(time.strptime(info['date'], '%Y-%m-%dT%H:%M:%S.%fZ'))
        return date_of_revision

    def _get_metrics_from_dataset_name(self, dataset_name, result_metrics_dict):
        result = {
            'dataset_name': dataset_name,
            'number_of_runs': self.Parameters.number_of_runs,
            'number_of_successful_runs': result_metrics_dict[dataset_name]['number_of_successful_runs'],
            'date': self.Context.date,
            'arcadia_svn_revision': self.Context.revision_number}

        for metric in ('clean_time', 'total_time', 'max_rss'):
            result['min_' + metric] = float(result_metrics_dict[dataset_name][metric]['min'])
            result['max_' + metric] = float(result_metrics_dict[dataset_name][metric]['max'])
            for quantile_percent in ('50', '75', '90', '95', '99'):
                result[metric + '_0.' + quantile_percent] = float(
                    result_metrics_dict[dataset_name][metric][quantile_percent]
                )

        if self.Parameters.api_type == 'cli':
            result["binary_sandbox_id"] = self.Context.catboost_binary_id
        elif self.Parameters.api_type == 'python-package':
            result["python_package_wheel_sandbox_id"] = self.Context.catboost_python_package_wheel_id

        return result

    def _get_pretty_table_from_dataset_name(self, dataset_name, result_metrics_dict):
        from prettytable import PrettyTable
        th = ['', self.Parameters.catboost_name]
        table = PrettyTable(th)
        for metric in ('total_time', 'clean_time', 'max_rss'):
            table.add_row([metric, result_metrics_dict[dataset_name][metric]['min']])
        return '{}\n{}'.format(dataset_name, table.get_string())

    def _push_new_metrics_to_yt(self, yt_metrics_table_list):
        import yt.wrapper as yt
        import library.python.retry as retry
        import yt.logger as yt_logger

        yt_logger.LOGGER.setLevel(level='DEBUG')

        yt_config = {
            'proxy': {'url': self.Parameters.metrics_table_proxy},
            'token': sdk2.Vault.data(self.owner, self.Parameters.token_name)}
        client = yt.YtClient(config=yt_config)

        retry.retry_call(
            self._append_metrics_to_table,
            (client, self.Parameters.metrics_table_path, yt_metrics_table_list),
            conf=retry.RetryConf().waiting(delay=5., backoff=2., jitter=1., limit=120.).upto(minutes=5.))

    def _push_new_metrics_to_pulsar(self, data_points):
        import pulsar

        tasks_list = self._get_json_from_resource(self.Parameters.perf_test_json_task)
        tasks_train_options_dict = {}
        for task in tasks_list:
            tasks_train_options_dict[task['name']] = task['catboost_train_options']

        pc = pulsar.PulsarClient(token=sdk2.Vault.data(self.owner, self.Parameters.pulsar_token_name))

        instances = []
        for data_point in data_points:
            metrics = {}
            for k in data_point:
                if k.startswith('min') or k.startswith('max') or k.startswith('total') or k.startswith('clean'):
                    metrics[k.replace('.', '_')] = data_point[k]

            operation_options = {
                'number_of_runs': data_point['number_of_runs'],
                'number_of_successful_runs': data_point['number_of_successful_runs'],
                'arcadia_svn_revision': data_point['arcadia_svn_revision'],
                'python_package_wheel_sandbox_id': data_point['python_package_wheel_sandbox_id'],
                'train_params': tasks_train_options_dict[data_point['dataset_name']],
            }
            if self.Parameters.pulsar_metadata_json:
                operation_options.update(json.loads(self.Parameters.pulsar_metadata_json))

            if self.Parameters.api_type == 'python-package':
                if self.Parameters.data_prep_params_json is not None:
                    operation_options['data_prep_params'] = self._get_json_from_resource(
                        self.Parameters.data_prep_params_json
                    )

            instances.append(
                pulsar.InstanceInfo(
                    pulsar.ModelInfo(
                        self.Parameters.pulsar_model_name,
                        operation_options=operation_options
                    ),
                    pulsar.DatasetInfo(
                        name=data_point['dataset_name']
                    ),
                    tags=['CATBOOST_PY_PERF_TESTS'],
                    result=metrics,
                    user_datetime=datetime.datetime.fromtimestamp(data_point['date'])
                ))

        pc.add(instances)

    def _push_new_metrics(self):
        json_report_path = str(sdk2.ResourceData(sdk2.Resource["CAT_BOOST_NPERF_TESTS_REPORT"].find().first()).path)

        dataset_names = self._get_dataset_names(self.Parameters.perf_test_json_task)

        metrics_table_list = []
        self.Context.revision_number = None
        self.Context.date = self.Context.date_of_run
        self.Context.catboost_binary_id = None
        self.Context.catboost_python_package_wheel_id = None
        if not self.Parameters.use_catboost_binary:
            perf_test_task = sdk2.Task[self.Context.run_perf_test_task_id]
            if self.Parameters.api_type == 'cli':
                self.Context.catboost_binary_id = perf_test_task.Context.first_catboost_binary_id
                self.Context.revision_number = int(sdk2.Resource[self.Context.catboost_binary_id].arcadia_revision)
            elif self.Parameters.api_type == 'python-package':
                self.Context.catboost_python_package_wheel_id = perf_test_task.Context.first_catboost_python_package_wheel_id
                self.Context.revision_number = int(sdk2.Resource[self.Context.catboost_python_package_wheel_id].svn_revision)
            self.Context.date = self._get_date_of_revision(self.Context.revision_number)
        else:
            if self.Parameters.api_type == 'cli':
                self.Context.catboost_binary_id = self.Parameters.catboost_binary.id
            elif self.Parameters.api_type == 'python-package':
                self.Context.catboost_python_package_wheel_id = self.Parameters.catboost_python_package_wheel.id

        pretty_table_str = ''
        try:
            with open(json_report_path, 'r') as result_metrics_file:
                result_metrics_dict = json.load(result_metrics_file)
            for dataset_name in dataset_names:
                metrics_table_list.append(self._get_metrics_from_dataset_name(dataset_name, result_metrics_dict))
                pretty_table_str = '{}\n{}'.format(pretty_table_str, self._get_pretty_table_from_dataset_name(dataset_name, result_metrics_dict))
        except Exception as e:
            _logger.exception(e)

        with open('metrics.json', 'w') as metrics_table_result:
            json.dump(metrics_table_list, metrics_table_result)

        metrics_resource = sdk2.ResourceData(CatBoostPerfTestMetricsReport(
            self,
            "catbost performance test metrics resource", 'metrics.json'))
        metrics_resource.ready()

        with open('metrics_tables.txt', 'w') as metrics_table_result:
            metrics_table_result.write(pretty_table_str)

        metrics_tables_resource = sdk2.ResourceData(CatBoostPerfTestTablesReport(
            self,
            "catbost performance test tables resource", 'metrics_tables.txt'))
        metrics_tables_resource.ready()

        if self.Parameters.push_result_to_yt_table:
            self._push_new_metrics_to_yt(metrics_table_list)

        if self.Parameters.push_result_to_pulsar:
            self._push_new_metrics_to_pulsar(metrics_table_list)

    class Requirements(sdk2.Requirements):
        cores = 1
        disk_space = 1024  # 1 GB
        ram = 512  # 512 MB

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(RunCatBoostPerfTestAndPushScoreParameters):
        pass

    def _check_for_success(self, task_id):
        if self.server.task[task_id].read()["status"] != 'SUCCESS':
            raise SandboxTaskFailureError('error in task {})'.format(task_id))

    def on_save(self):
        if self.Parameters.use_last_binary:
            self.Requirements.tasks_resource = SandboxTasksBinary.find(
                attrs={'target': 'catboost/bin', 'release': self.Parameters.release_type or 'stable'}
            ).first().id
        else:
            self.Requirements.tasks_resource = self.Parameters.custom_tasks_archive_resource

    def on_execute(self):
        self.Context.date_of_run = time.time()

        with self.memoize_stage.run_perf_test:
            self.Context.run_perf_test_task_id = self._run_perf_test(
                use_binary=self.Parameters.use_catboost_binary,
                revision_number=self.Parameters.revision_number,
                json_task_id=self.Parameters.perf_test_json_task.id,
                data_prep_params_json_id=self.Parameters.data_prep_params_json.id if self.Parameters.data_prep_params_json else None,
                number_of_runs=self.Parameters.number_of_runs)
            raise sdk2.WaitTask(self.Context.run_perf_test_task_id, ctt.Status.Group.SUCCEED + ctt.Status.Group.FINISH + ctt.Status.Group.BREAK)

        self._check_for_success(self.Context.run_perf_test_task_id)

        self._push_new_metrics()
