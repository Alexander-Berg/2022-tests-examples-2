# -*- coding: utf-8 -*-
"""
    Please obey PEP8 in this file as much as possible
"""

import os
import logging

import sandbox.common.types.client as ctc

from sandbox.sandboxsdk import errors as se
from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk import paths
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.task import SandboxTask

from sandbox.projects import resource_types
from sandbox.projects.common import dolbilka
from sandbox.projects.common.dolbilka import stats_parser
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import file_utils as fu
from sandbox.projects.common import footers
from sandbox.projects.common import utils
from sandbox.projects.common.base_search_quality import settings as bss
from sandbox.projects.common.search import components as sc
from sandbox.projects.common.search.basesearch.task import DisableMD5Calculations


class PlanParameter(sp.ResourceSelector):
    name = 'dolbilo_plan_resource_id'
    description = 'Plan'
    resource_type = [
        resource_types.BASESEARCH_PLAN,
        resource_types.ADDRESSNIP_SEARCH_PLAN,
        resource_types.SERPAPI_SEARCH_PLAN,
    ]
    required = False


class MinDataReadPerRequestParameter(sp.SandboxIntegerParameter):
    name = 'min_data_read_per_request'
    description = 'Min avg bytes read per request'
    group = 'Response verification'
    default_value = 0


class FailRateThreshold(sp.SandboxFloatParameter):
    name = 'fail_rate_threshold'
    description = 'Fail rate threshold'
    group = 'Response verification'
    default_value = 0.005


class NotFoundRateThreshold(sp.SandboxFloatParameter):
    name = 'notfound_rate_threshold'
    description = 'Not found rate threshold'
    group = 'Response verification'
    default_value = 0.01


class IgnoreFirstNSessions(sp.SandboxIntegerParameter):
    name = 'ignore_first_n_sessions'
    group = 'Response verification'
    description = 'Ignore first N sessions'
    default_value = 0


class SaveLoadLogParameter(sp.SandboxBoolParameter):
    name = 'save_load_log'
    description = 'Save load log'
    group = 'Response verification'
    default_value = False


class RunProfilerParameter(sp.SandboxBoolParameter):
    name = 'run_profiler'
    description = 'Run profiler'
    group = 'Profiling'
    default_value = False


class UseGPerfToolsParameter(sp.SandboxBoolParameter):
    name = 'use_gperftools'
    description = 'Use GPerfTools'
    group = 'Profiling'
    default_value = False


class RunSpecialFinalSessionParameter(sp.SandboxBoolParameter):
    name = 'run_special_final_session'
    description = 'Run special final session (finger mode, 4 requests)'
    group = 'Priemka special options'
    default_value = False


class VmTouchModelsArchive(sp.SandboxBoolParameter):
    name = 'vmtouch_models_archive'
    description = 'Measure models.archive active pages using vmtouch (affects performance), see SEARCH-3070'
    group = 'Memory management'
    default_value = False


class VmTouchShard(sp.SandboxBoolParameter):
    name = 'vmtouch_shard'
    description = 'Measure shard active pages using vmtouch (affects performance), see SEARCH-3070'
    group = 'Memory management'
    default_value = False


class PmapModelsArchive(sp.SandboxBoolParameter):
    name = 'pmap_models_archive'
    description = 'Get models.archive RSS via pmap'
    group = 'Memory management'
    default_value = False


class UsePhantomDump(sp.SandboxBoolParameter):
    name = 'use_phantom_dump'
    description = 'Use phantom dump'
    default_value = False


class CollectPGOProfile(sp.SandboxBoolParameter):
    name = 'collect_pgo_profile'
    description = 'Collect PGO profile'
    default_value = False


_PGO_PROFILE_NAME = 'default.profraw'


class TestBasesearchPerformance(SandboxTask):
    """
        Измеряет производительность базового поиска с заданным планом обстрела.
        Проводит 1 серию из N стрельб, замеряет RPS с помощью dolbilo.

        В качестве результата выбирается наилучший RPS.
        Используется в качестве подзадачи для TEST_BASESEARCH_PERFORMANCE_BEST.

        Имеет встроенную систему контроля ответов. Вычисляет среднюю длину ответа,
        и если она меньше заданного порога, завершает задачу в состоянии FAILURE.

        При обстреле вычисляется fail rate (количество неответов по таймауту).
        Если минимальный fail rate по сессиям превышает заданный порог, задача
        также завершается в состоянии FAILURE. Данный тест особенно актуален
        для режима обстрела ``plan`` (см. также SEARCH-754).
    """

    type = 'TEST_BASESEARCH_PERFORMANCE'

    execution_space = bss.RESERVED_SPACE + bss.DOLBILKA_SPACE
    required_ram = 100 << 10
    client_tags = ctc.Tag.LINUX_PRECISE

    additional_performance_params = (
        PlanParameter,
        # profiling
        RunProfilerParameter,
        UseGPerfToolsParameter,
        CollectPGOProfile,
        # verification
        MinDataReadPerRequestParameter,
        IgnoreFirstNSessions,
        FailRateThreshold,
        NotFoundRateThreshold,
        SaveLoadLogParameter,
        # memory management
        VmTouchModelsArchive,
        VmTouchShard,
        PmapModelsArchive,
        # priemka
        RunSpecialFinalSessionParameter,
        # other
        DisableMD5Calculations,
        UsePhantomDump,
    ) + dolbilka.DolbilkaExecutor.input_task_parameters

    @property
    def footer(self):
        return footers.exec_stats_footer(self)

    input_parameters = (
        sc.DefaultBasesearchParams.params +
        additional_performance_params
    )

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        channel.task = self

        if (
            utils.get_or_default(self.ctx, VmTouchModelsArchive) and
            not self.ctx.get(sc.DefaultBasesearchParams.ArchiveModel.name)
        ):
            raise se.SandboxTaskFailureError("Models archive not specified")

        if self.ctx[SaveLoadLogParameter.name]:
            self.ctx['load_log_resource_id'] = self.create_resource(
                '{0}, load log'.format(self.descr), 'load.log',
                resource_types.LOAD_LOG,
                arch='any'
            ).id

        # prepare resources for possible further profile comparing
        # svg/pdf profiles emitted by gperftools are not listed here
        # because they can't be compared
        if utils.get_or_default(self.ctx, RunProfilerParameter):
            self.ctx['txt_profile_resource_id'] = self.create_resource(
                '{0}, text profile'.format(self.descr), 'profile.txt',
                resource_types.PROFILE_STAT
            ).id

            self.ctx['raw_profile_resource_id'] = self.create_resource(
                '{0}, raw profile'.format(self.descr), 'profile.raw.log',
                resource_types.RAW_PROFILE_STAT
            ).id

        if utils.get_or_default(self.ctx, CollectPGOProfile):
            self.ctx["pgo_profile_resource_id"] = self.create_resource(
                '{} PGO profile'.format(self.descr), _PGO_PROFILE_NAME,
                resource_types.PGO_PROFILE_RESOURCE
            ).id

    def on_execute(self):
        component_creator = sc.BasesearchWebWithProfilerResources

        self._vmtouch_models()
        self._vmtouch_shard()

        use_profiler = self.ctx.get(RunProfilerParameter.name, False)
        use_gperftools = self.ctx.get(UseGPerfToolsParameter.name, False)

        basesearch = sc.get_basesearch(
            use_profiler=use_profiler or use_gperftools,
            use_gperftools=use_gperftools,
            component_creator=component_creator,
        )

        if utils.get_or_default(self.ctx, DisableMD5Calculations):
            # get rid of long calculations that may affect performance
            basesearch.replace_config_parameter("Collection/CalculateBinaryMD5", 'no')
            basesearch.replace_config_parameter("Collection/CalculateModelsMD5", 'no')

        if basesearch.use_profiler:
            basesearch.profile_res_id = self.ctx['txt_profile_resource_id']
            basesearch.raw_profile_res_id = self.ctx['raw_profile_resource_id']

        self.init_search_component(basesearch)
        plan = self.sync_resource(self.ctx[PlanParameter.name])

        # delay set in task context has higher priority than delay from plan attribute
        delay_multiplier = self.ctx.get(dolbilka.DolbilkaDelayMultiplier.name, None)
        if not delay_multiplier:
            logging.info(
                "Delay modifier is not set in task context, "
                "obtaining delay multiplier from plan 'delay_multiplier' attribute"
            )
            delay_multiplier = channel.sandbox.get_resource_attribute(
                self.ctx[PlanParameter.name],
                'delay_multiplier',
            )
        if not delay_multiplier:
            delay_multiplier = 1.0
            logging.info("Using default delay multiplier: %s", delay_multiplier)
        else:
            delay_multiplier = float(delay_multiplier)
            logging.info("Using delay multiplier: %s", delay_multiplier)

        d_executor = dolbilka.DolbilkaExecutor()
        results = []

        def on_session_end(session):
            self._get_pmap_rss_for_model_archive(basesearch)

            if session == (d_executor.sessions - 1):
                if utils.get_or_default(self.ctx, VmTouchModelsArchive):
                    self.ctx['model_archive_resident_percent'] = _vmtouch_file(self.models_path)

                if utils.get_or_default(self.ctx, VmTouchShard):
                    shard_vmtouch_log_name = "shard_vmtouch_result.txt"
                    vmtouch_res = self.create_resource(
                        "Database vmtouch result", shard_vmtouch_log_name, resource_types.OTHER_RESOURCE
                    )
                    self.ctx['shard_resident_percent'] = _vmtouch_file(self.shard_path, vmtouch_res.path)

                if self.ctx.get(RunSpecialFinalSessionParameter.name, False):
                    # run additional session after last session
                    # this is for task PRIEMKA_BASESEARCH_DATABASE
                    d_executor.mode = 'finger'
                    d_executor.max_simultaneous_requests = 4
                    parsed_stat = basesearch.use_component(
                        lambda: d_executor.run_session_and_dumper(plan, basesearch, "finger4", run_once=True)
                    )
                    results.append(parsed_stat)

        results[:0] = d_executor.run_sessions(
            plan,
            basesearch,
            run_once=True,
            need_warmup=True if self.ctx[SaveLoadLogParameter.name] else False,
            callback=on_session_end,
            delay_multiplier=delay_multiplier,
            phantom=self.ctx.get(UsePhantomDump.name, False)
        )

        if self.ctx[SaveLoadLogParameter.name]:
            if os.path.getsize(basesearch.get_loadlog()) == 0:
                raise se.SandboxTaskFailureError("load log is empty")

            resource = channel.sandbox.get_resource(self.ctx['load_log_resource_id'])
            logging.info('moving %s to %s', basesearch.get_loadlog(), resource.path)
            logging.info('isfile(%s) = %s', basesearch.get_loadlog(), os.path.isfile(basesearch.get_loadlog()))
            logging.info(
                'isdir(%s) = %s',
                os.path.dirname(resource.path),
                os.path.isdir(os.path.dirname(resource.path))
            )
            os.rename(basesearch.get_loadlog(), resource.path)
            self.mark_resource_ready(resource)

        dolbilka.DolbilkaPlanner.fill_rps_ctx(results, self.ctx)

        if utils.get_or_default(self.ctx, CollectPGOProfile):
            self.set_info("Dumped profile of {} bytes size".format(os.path.getsize(_PGO_PROFILE_NAME)))

        # fail task at last
        if self.ctx[MinDataReadPerRequestParameter.name]:
            self._check_min_data_read()

        notfound_rate_threshold = self.ctx.get(NotFoundRateThreshold.name, 0.0)
        fail_rate_threshold = self.ctx.get(FailRateThreshold.name, 0.0)
        check_rate(fail_rate_threshold, self.ctx.get('min_fail_rate', 0.0), 'Fail')
        check_rate(notfound_rate_threshold, self.ctx.get('min_notfound_rate', 0.0), 'NotFound')

    def _get_pmap_rss_for_model_archive(self, basesearch):
        if utils.get_or_default(self.ctx, PmapModelsArchive):
            try:
                cmd = "pmap -x {}".format(basesearch.get_pid())
                p = process.run_process(cmd, outs_to_pipe=True, timeout=60)
                out, _ = p.communicate()
                for line in out.split('\n'):
                    if "models.archive" in line:
                        logging.info("done pmap: {}".format(line))
                        self.ctx["pmap_RSS"] = max(int(line.split()[2]), self.ctx.get("pmap_RSS", 0))
                        break
            except Exception as e:
                logging.info("Exception: %s", e)

    def _check_min_data_read(self):
        resources = self.list_resources(resource_type=resource_types.EXECUTOR_STAT)
        if not resources:
            raise se.SandboxTaskUnknownError("No EXECUTOR_STAT resources")

        ignore_count = self.ctx.get(IgnoreFirstNSessions.name, 0)
        for stats_res in resources:
            if ignore_count > 0:
                session_index = int(stats_res.attrs['session_name'])
                if session_index < ignore_count:
                    logging.debug("Ignore session %s", session_index)
                    continue

            stats = stats_parser.StatsParser(stats_res.file_name)
            if stats.vars['requests'] > 0:
                stats_data_read_per_request = int(stats.vars['data readed'] / stats.vars['requests'])
            else:
                stats_data_read_per_request = 0
            min_data_read_per_request = self.ctx['min_data_read_per_request']
            eh.ensure(
                stats_data_read_per_request >= min_data_read_per_request,
                'Too few data ({0} bytes) were read per request on an average'.format(
                    stats_data_read_per_request,
                )
            )

    def init_search_component(self, search_component):
        """
        Stub. Can be overloaded in subclasses.
        """
        pass

    @staticmethod
    def _vmtouch_evict(path, timeout=60):
        cmd = "vmtouch -e -m 100G -f {}".format(path)
        process.run_process(cmd, timeout=timeout)

    def _vmtouch_models(self):
        if not utils.get_or_default(self.ctx, VmTouchModelsArchive):
            return

        # save path for further vmtouch-ing
        self.models_path = self.sync_resource(self.ctx.get(sc.DefaultBasesearchParams.ArchiveModel.name))
        self._vmtouch_evict(self.models_path, timeout=30)

    def _vmtouch_shard(self):
        if not utils.get_or_default(self.ctx, VmTouchShard):
            return
        self.shard_path = self.sync_resource(self.ctx.get(sc.DefaultBasesearchParams.Database.name))
        self._vmtouch_evict(self.shard_path, timeout=120)

    def get_results(self):
        if not self.is_completed():
            return 'Results are not ready yet.'

        return 'Max RPS: {}. All RPS: {}'.format(
            self.ctx.get('max_rps', 'unknown'), self.ctx.get('requests_per_sec', 'unknown')
        )

    def get_short_task_result(self):
        if not self.is_completed():
            return None

        rps = self.ctx.get('max_rps', None)
        if rps:
            return str(rps)


def check_rate(rate_threshold, rate, description):
    # ignore values too close to zero
    if rate_threshold < 0.0000001:
        return
    eh.ensure(
        rate <= rate_threshold,
        '{} rate threshold reached: {} > {}'.format(
            description,
            rate,
            rate_threshold,
        )
    )


def _vmtouch_file(path, output_file_name=None, max_size="500G"):
    """
    :param path: file or directory to examine with vmtouch
    :param output_file_name: raw vmtouch output (will write in task logs if omitted)
    :param max_size: max memory size to examine (e.g. '100G')
    :return: resident pages percent value
    """
    if output_file_name is None:
        output_file_name = paths.get_unique_file_name(paths.get_logs_folder(), "vmtouch.log")

    cmd = "vmtouch -m {max_size} -f -v {path}".format(max_size=max_size, path=path)
    logging.info(cmd)
    with open(output_file_name, 'w') as output:
        process.run_process(cmd, outputs_to_one_file=True, stdout=output, timeout=120)

    result = None
    for line in fu.read_line_by_line(output_file_name):
        line = line.strip()
        logging.info(line)
        if result is None and line.startswith("Resident Pages:"):
            result = line.split()[-1]  # "24.9%"
            result = float(result[:-1])

    return result


__Task__ = TestBasesearchPerformance
