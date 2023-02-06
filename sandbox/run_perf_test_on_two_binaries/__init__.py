import cStringIO
import os
import subprocess
import tarfile
import traceback
import uuid
from sandbox import sdk2
from sandbox.projects.catboost.util.resources import (
    CatBoostBinary,
    CatBoostPythonPackageWheel,
    CatBoostRunPythonPackageTrain,
    CatBoostPerformanceEvaluationBinary,
    CatBoostPerfTestJsonTask,
    CatBoostDataPrepParamsJson)
from sandbox.projects.sandbox.resources import LXC_CONTAINER
from sandbox.projects.catboost.util.resources import CatBoostPoolArchive  # noqa
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sdk2.service_resources import SandboxTasksBinary


class CatBoostPerfTestHtmlReport(sdk2.Resource):
    share = False


class CatBoostPerfTestReport(sdk2.Resource):
    share = False


def _runner(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs), None
    except:
        return None, ''.join(traceback.format_exc())


def upload_file(src, filename):
    import yt.wrapper as yt
    data_path = yt.smart_upload_file(src, placement_strategy='hash')
    print (data_path)
    # https://st.yandex-team.ru/YTADMINREQ-12273
    return yt.YPath('<file_name = "{}"; executable = true;>{}'.format(filename, data_path))


# files_map is dict: src_file_path -> file_name (as yt attribute)
# returns dict: src_file_path -> yt path
def upload(files_map, workers=2):
    result = {}
    for path, dst in files_map.items():
        result[path] = upload_file(path, dst)
    return result


class CatBoostRunPerfTestOnTwoBinariesParameters(sdk2.Task.Parameters):
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
            required=True, )
        with api_type.value['python-package']:
            with sdk2.parameters.RadioGroup('booster') as booster:
                booster.values['catboost'] = booster.Value('catboost', default=True)
                booster.values['lightgbm'] = booster.Value('lightgbm')
                booster.values['xgboost'] = booster.Value('xgboost')
            run_python_package_train = sdk2.parameters.Resource(
                'run_python_package_train script (not arcadia build python binary!)',
                resource_type=CatBoostRunPythonPackageTrain,
                required=True, )
        with api_type.value['cli']:
            catboost_binary_1 = sdk2.parameters.Resource(
                'first catboost binary',
                resource_type=CatBoostBinary,
                required=True, )
        with api_type.value['python-package']:
            catboost_python_package_wheel_1 = sdk2.parameters.Resource(
                'first catboost python package wheel',
                resource_type=CatBoostPythonPackageWheel,
                default=None,)
        first_name = sdk2.parameters.String(
            'first name',
            default='booster_1',)
        first_catboost_additional_args = sdk2.parameters.String(
            'first catboost additional args',
            default='', )
        with api_type.value['cli']:
            catboost_binary_2 = sdk2.parameters.Resource(
                'second catboost binary',
                resource_type=CatBoostBinary,
                default=None, )
        with api_type.value['python-package']:
            catboost_python_package_wheel_2 = sdk2.parameters.Resource(
                'second catboost python package wheel',
                resource_type=CatBoostPythonPackageWheel,
                default=None, )
        second_name = sdk2.parameters.String(
            'second name',
            default='booster_2',)
        second_catboost_additional_args = sdk2.parameters.String(
            'second catboost additional args',
            default='', )
        token_name = sdk2.parameters.String(
            'token name',
            default='yt_token',)
        perf_test_json_task = sdk2.parameters.Resource(
            'performance test json task',
            resource_type=CatBoostPerfTestJsonTask,
            required=True, )
        with api_type.value['python-package']:
            data_prep_params_json_1 = sdk2.parameters.Resource(
                'first data prep params json',
                resource_type=CatBoostDataPrepParamsJson,
                default=None, )
            data_prep_params_json_2 = sdk2.parameters.Resource(
                'second data prep params json',
                resource_type=CatBoostDataPrepParamsJson,
                default=None, )
        number_of_cores = sdk2.parameters.Integer(
            'number of required cores',
            required=True, )
        cpu_ram_in_mb = sdk2.parameters.Integer(
            'required CPU RAM (in Mb)',
            required=True, )
        disk_space_in_gb = sdk2.parameters.Integer(
            'required disk space (in Gb)',
            default=32, )
        container = sdk2.parameters.Container(
            "Environment container resource",
            default_value=1477520355,
            resource_type=LXC_CONTAINER,
            platform="linux_ubuntu_16.04_xenial",
            required=True,
        )


class CatBoostRunPerfTestOnTwoBinaries(sdk2.Task):
    def _get_file_path_for_cmd(self, resource_id, out_yt_files_to_upload):
        """
            out_yt_files_to_upload is dict: src_file_path -> file_name (as yt attribute)

            returns path to file for cmd
        """
        local_path = str(sdk2.ResourceData(resource_id).path)
        file_name = os.path.basename(local_path)
        if self.Parameters.run_on_yt:
            out_yt_files_to_upload[local_path] = file_name
            return file_name
        else:
            return local_path

    def _get_result_from_yt(self, yt_result_dir, sub_dir):
        import yt.wrapper as yt
        fileobj = cStringIO.StringIO(yt.read_file(yt_result_dir + '/' + sub_dir + '.tgz').read())
        with tarfile.open(fileobj=fileobj, mode='r:gz') as tar:
            tar.extractall('catboost_perf_test')

    # data_prep_params_json_path can be None
    def _run_catboost_speed_bench(self):
        # dict: src_file_path -> file_name (as yt attribute)
        yt_files_to_upload = {}

        cmd = self._get_file_path_for_cmd(self.Parameters.performance_evaluation_binary, yt_files_to_upload)
        cmd += ' --booster ' + self.Parameters.booster
        if self.Parameters.api_type == 'cli':
            cmd += ' --api-type cli --cb-1 ' + self._get_file_path_for_cmd(
                self.Parameters.catboost_binary_1,
                yt_files_to_upload
            )
            if self.Parameters.catboost_binary_2:
                cmd += ' --cb-2 ' + self._get_file_path_for_cmd(
                    self.Parameters.catboost_binary_2,
                    yt_files_to_upload
                )
        if self.Parameters.api_type == 'python-package':
            cmd += (' --api-type python-package  --run-python-package-train ' + self._get_file_path_for_cmd(
                self.Parameters.run_python_package_train,
                yt_files_to_upload
            ))
            if self.Parameters.catboost_python_package_wheel_1:
                cmd += ' --cb-1 ' + self._get_file_path_for_cmd(
                    self.Parameters.catboost_python_package_wheel_1,
                    yt_files_to_upload
                )
            if self.Parameters.catboost_python_package_wheel_2:
                cmd += ' --cb-2 ' + self._get_file_path_for_cmd(
                    self.Parameters.catboost_python_package_wheel_2,
                    yt_files_to_upload
                )
            if self.Parameters.data_prep_params_json_1:
                cmd += ' --python-data-prep-params-1 ' + self._get_file_path_for_cmd(
                    self.Parameters.data_prep_params_json_1,
                    yt_files_to_upload
                )
            if self.Parameters.data_prep_params_json_2:
                cmd += ' --python-data-prep-params-2 ' + self._get_file_path_for_cmd(
                    self.Parameters.data_prep_params_json_2,
                    yt_files_to_upload
                )
        cmd += ' --cb-name-1 ' + self.Parameters.first_name
        cmd += ' --cb-name-2 ' + self.Parameters.second_name
        if self.Parameters.first_catboost_additional_args:
            cmd += ' --cb-additional-args-1="{}"'.format(self.Parameters.first_catboost_additional_args)
        if self.Parameters.second_catboost_additional_args:
            cmd += ' --cb-additional-args-2="{}"'.format(self.Parameters.second_catboost_additional_args)
        cmd += ' --task-json ' + self._get_file_path_for_cmd(
            self.Parameters.perf_test_json_task,
            yt_files_to_upload
        )
        cmd += ' --give-time-table --create-html'

        yt_token = sdk2.Vault.data(self.owner, self.Parameters.token_name)
        if self.Parameters.run_on_yt:
            import yt.wrapper as yt
            yt_result_dir = yt.config['remote_temp_tables_directory'] + '/perf_test_results_' + str(uuid.uuid1())

            cmd += ' --work-dir catboost_perf_test'
            cmd += ' --yt-token-env-var YT_SECURE_VAULT_YT_TOKEN'
            cmd += ' --yt-proxy ' + self.Parameters.yt_proxy
            cmd += ' --yt-output-dir ' + yt_result_dir

            yt.config['token'] = yt_token
            yt.config['proxy']['url'] = self.Parameters.yt_proxy
            yt.config['allow_http_requests_to_yt_from_job'] = True

            yt.create("map_node", yt_result_dir, ignore_existing=True)

            uploaded_files_map = upload(yt_files_to_upload)

            yt_op_spec = {
                'pool_trees': [self.Parameters.yt_pool_tree],
                'secure_vault': {'YT_TOKEN': yt_token},
                'pool': 'nirvana-matrixnet'
            }
            yt_task_spec = {
                'command': cmd,
                'file_paths': list(uploaded_files_map.values()),
                'layer_paths': ['//home/mltools/porto_layers/xenial_gbdt_nvidia-418_cuda-10.0.tar.gz'],
                'cpu_limit': self.Parameters.number_of_cores,
                'gpu_limit': self.Parameters.yt_gpu_limit,
                'memory_limit': self.Parameters.cpu_ram_in_mb * 1024 * 1024,
                'job_time_limit': self.Parameters.kill_timeout * 1000,
                'disk_space_limit': self.Parameters.disk_space_in_gb * 1024 * 1024 * 1024,
                'job_count': 1,
            }
            spec = yt.spec_builders.VanillaSpecBuilder().spec(yt_op_spec).task("task", yt_task_spec)
            yt.run_operation(spec, sync=True)

            os.mkdir('catboost_perf_test')
            self._get_result_from_yt(yt_result_dir, 'result_data')
            if self.Parameters.catboost_binary_2 is not None:
                self._get_result_from_yt(yt_result_dir, 'html_data')

            yt.remove(yt_result_dir, recursive=True)
        else:
            os.environ['YT_TOKEN'] = yt_token
            cmd += ' --work-dir ' + os.path.join(os.getcwd(), 'catboost_perf_test')
            cmd += ' --yt-token-env-var YT_TOKEN'
            subprocess.check_call(cmd, shell=True)

    class Requirements(sdk2.Requirements):
        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(CatBoostRunPerfTestOnTwoBinariesParameters):
        pass

    def on_save(self):
        if self.Parameters.use_last_binary:
            self.Requirements.tasks_resource = SandboxTasksBinary.find(
                attrs={'target': 'catboost/bin', 'release': self.Parameters.release_type or 'stable'}
            ).first().id
        else:
            self.Requirements.tasks_resource = self.Parameters.custom_tasks_archive_resource

        if self.Parameters.run_on_yt:
            self.Requirements.disk_space = 2000  # 2 Fb
            self.Requirements.ram = 512
            self.Requirements.cores = 1
        else:
            self.Requirements.client_tags = self.Parameters.cpu_model_tag
            self.Requirements.disk_space = self.Parameters.disk_space_in_gb * 1024  # 32 GB
            self.Requirements.ram = self.Parameters.cpu_ram_in_mb
            self.Requirements.cores = self.Parameters.number_of_cores

    def on_execute(self):
        try:
            self._run_catboost_speed_bench()
        except Exception as e:
            raise SandboxTaskFailureError(e)

        if self.Parameters.catboost_binary_2 is not None:
            perf_test_html_res = sdk2.ResourceData(CatBoostPerfTestHtmlReport(
                self,
                "catbost performance test html resource", "catboost_perf_test/html_data"))
            perf_test_html_res.ready()

        perf_test_result_res = sdk2.ResourceData(CatBoostPerfTestReport(
            self,
            "catbost performance test result resource", "catboost_perf_test/result_data"))
        perf_test_result_res.ready()
