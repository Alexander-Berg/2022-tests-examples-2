# -*- coding: utf-8 -*-

import copy
import os
import json
import logging

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk import parameters
from sandbox.sandboxsdk.channel import channel

from sandbox.projects import resource_types
from sandbox.projects.common import apihelpers
from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import utils
from sandbox.projects.common import dolbilka
from sandbox.projects.common.search import components as sc
from sandbox.projects.common import profiling


_EXPERIMENTS_SETTINGS = "Experiments settings"
_BASESEARCH_SETTINGS = "BaseSearch settings"


class AddCgi(parameters.SandboxStringParameter):
    name = 'new_cgi_params'
    description = (
        "New cgi params. Each line must be properly %-encoded. ';' separates groups of params "
        "(will be looped through plan), see task docs for details"
    )
    required = True
    multiline = True
    group = _EXPERIMENTS_SETTINGS


class RemoveCgi(parameters.SandboxStringParameter):
    name = 'remove_cgi_params'
    description = (
        "Remove specified cgi params. Must be properly %-encoded. "
        "See task docs for details"
    )
    required = False
    default_value = ''
    group = _EXPERIMENTS_SETTINGS


class TestBaselinePerformance(parameters.SandboxBoolParameter):
    name = 'test_baseline_performance'
    description = 'Test baseline performance'
    default_value = True
    group = _EXPERIMENTS_SETTINGS


class TestMemoryUsage(parameters.SandboxBoolParameter):
    name = 'test_memory_usage'
    description = 'Test memory usage'
    default_value = False
    group = _EXPERIMENTS_SETTINGS


class Tier(parameters.SandboxStringParameter):
    name = 'tier'
    description = 'Tier (PlatinumTier0 by default)'
    default_value = 'PlatinumTier0'
    required = False
    group = _BASESEARCH_SETTINGS


class Binary(parameters.LastReleasedResource):
    name = 'basesearch_executable_resource_id'
    description = 'Executable (if omitted, last released will be used)'
    resource_type = resource_types.BASESEARCH_EXECUTABLE
    required = False
    group = _BASESEARCH_SETTINGS


class ModelsArchive(parameters.LastReleasedResource):
    name = 'models_archive_resource_id'
    description = 'Models archive (if omitted, last released will be used)'
    resource_type = resource_types.DYNAMIC_MODELS_ARCHIVE_BASE
    required = False
    group = _BASESEARCH_SETTINGS


class Plan(parameters.ResourceSelector):
    name = 'dolbilo_plan_resource_id'
    description = 'Plan (if omitted, default tier test plan is used)'
    resource_type = [
        resource_types.BASESEARCH_PLAN,
        resource_types.ADDRESSNIP_SEARCH_PLAN,
        resource_types.SERPAPI_SEARCH_PLAN,
    ]
    required = False
    group = _BASESEARCH_SETTINGS


class Shard(sc.DefaultBasesearchParams.Database):
    required = False
    default_value = None
    description = 'Database (if omitted, last production will be used)'
    group = _BASESEARCH_SETTINGS


class Config(sc.DefaultBasesearchParams.Config):
    required = True
    description = 'Basesearch config'
    group = _BASESEARCH_SETTINGS


class RequestsLimit(parameters.SandboxIntegerParameter):
    name = 'requests_limit'
    description = 'Requests limit'
    default_value = 200000
    required = False
    group = _BASESEARCH_SETTINGS


_CHILD_TASK_IDS_KEY = 'child_task_ids'
_EXPERIMENTS = 'exp_data'
_EXP_WITHOUT_RPS = 'tmp_exp_data'
_BASELINE = 'baseline'


class TestBasesearchExperiment(SandboxTask):
    """
        Проверка экспериментальных CGI-параметров базового поиска на производительность,
        падения и потребление памяти.

        Цель: убедиться, что новый параметр не убивает базовый поиск и не замедляет слишком сильно.

        Как работает:
        * Получает на вход несколько наборов CGI-параметров (по набору на 1 строку текстового поля)
        * Для каждого из наборов создаёт план запросов (на базе плана запросов с продакшена),
            запуская таск PATCH_PLAN.
        * Если в наборе параметров присутствует ';', они разбиваются на группы по этому разделителю
            и добавляются в план по циклу. Т.е. для &param1;&param2;&param3=qqq и пачки запросов
            query1, query2, query3, query4, ... получим
            такой план:
            * query1&param1
            * query2&param2
            * query3&param3=qqq
            * query4&param1
            * query5&param2
            и далее по циклу.

        * Удаление параметров: разделённый ';' список параметров (если в самом параметре
            присутствует ';', она должна быть кодирована как %3B). Можно использовать '*'
            для обрезания параметра по префиксу (в этом случае эскейпинг самого префикса
            должен быть валидным regex-ом).
            Пример: ``&pron=termtpsz*;&pron=notermsearch``.

        * Для каждого из полученных планов обстрела запускает TEST_BASESEARCH_PERFORMANCE_BEST).
        * Остальные параметры берёт из продакшена/приёмочных тестов, типа PRIEMKA_BASESEARCH_BINARY.
    """

    type = 'TEST_BASESEARCH_EXPERIMENT'
    input_parameters = [
        # _EXPERIMENTS_SETTINGS
        AddCgi,
        RemoveCgi,
        TestBaselinePerformance,
        TestMemoryUsage,
        # _BASESEARCH_SETTINGS
        Tier,
        Binary,
        ModelsArchive,
        Shard,
        Plan,
        Config,
        RequestsLimit,
        # Profiling
        profiling.ProfilingTypeParameter,
    ]

    _binary_resource_id = None
    _db_resource_id = None
    _config_resource_id = None

    @property
    def footer(self):
        rps_list = []
        exp_data = json.loads(self.ctx.get(_EXPERIMENTS, '{}'))

        exp_count = len(exp_data) - 1
        baseline_rps = None
        if _BASELINE in exp_data:
            baseline_rps = exp_data[_BASELINE]['rps']
        if baseline_rps < 0.1:
            baseline_rps = 0.1

        for exp_index in xrange(exp_count):
            exp = exp_data[str(exp_index)]
            cgi_params = exp['cgi_params']
            exp_rps = int(float(exp['rps']) * 10) / 10.0
            delta_rps_percent = int(10000.0 * (exp_rps - baseline_rps) / baseline_rps) / 100.0
            if delta_rps_percent > 0.1:
                delta_rps_percent = "+" + str(delta_rps_percent) + "%"
            else:
                delta_rps_percent = str(delta_rps_percent) + "%"

            profile_results = apihelpers.list_task_resources(
                task_id=exp['task_id'],
                resource_type=resource_types.PROFILE_RESULTS,
            )
            columns = {
                'Task': lb.task_link(exp['task_id']),
                'RPS': exp_rps,
                'Baseline delta': delta_rps_percent,
                'CGI params': cgi_params,
            }
            if profile_results:
                columns['Flame Graph'] = lb.HREF_TO_ITEM.format(
                    link=os.path.join(profile_results[0].proxy_url, profiling.FLAMEGRAPH_NAME),
                    name="flamegraph",
                )
            rps_list.append(columns)

        foot = [{
            'helperName': '',
            'content': rps_list,
        }]
        return foot

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        channel.task = self

    def on_execute(self):
        test_memory_usage = utils.get_or_default(self.ctx, TestMemoryUsage)
        test_baseline_performance = utils.get_or_default(self.ctx, TestBaselinePerformance)

        if _CHILD_TASK_IDS_KEY not in self.ctx:
            # find plan for testing basesearch
            tier = utils.get_or_default(self.ctx, Tier)
            plan_resource_id = self.ctx.get(Plan.name, None)
            if not plan_resource_id:
                attr = 'TE_web_base_prod_queries_search_{}'.format(tier)
                logging.info("Taking tier-specific test plan using attribute %s", attr)
                plan_resource_id = apihelpers.get_last_resource_with_attribute(
                    resource_type=resource_types.BASESEARCH_PLAN,
                    attribute_name=attr,
                ).id

            # find database
            db_resource_id = utils.get_or_default(self.ctx, Shard)
            if not db_resource_id:
                shard_attr = 'TE_web_base_prod_resources_{}'.format(tier)
                logging.info(
                    "Shard is not set, try to search last production shard for tier %s with attribute %s",
                    tier, shard_attr
                )
                db_resource_id = apihelpers.get_last_resource_with_attribute(
                    resource_type=resource_types.SEARCH_DATABASE,
                    attribute_name=shard_attr,
                ).id
            self._db_resource_id = db_resource_id

            # set config
            self._config_resource_id = utils.get_or_default(self.ctx, Config)

            binary_resource_id = utils.get_or_default(self.ctx, Binary)
            if not binary_resource_id:
                binary_resource_id = utils.get_and_check_last_released_resource_id(
                    resource_type=resource_types.BASESEARCH_EXECUTABLE,
                )
            self._binary_resource_id = binary_resource_id

            sub_tasks = []
            exp_data = {}

            if test_baseline_performance:
                self._test_baseline_performance(plan_resource_id, exp_data, sub_tasks)

            if test_memory_usage:
                self._test_memory_usage(plan_resource_id, sub_tasks)

            exp_index = 0
            all_cgi_params = utils.get_or_default(self.ctx, AddCgi)
            remove_cgi_params = utils.get_or_default(self.ctx, RemoveCgi).strip()
            params_list = all_cgi_params.split('\n')

            with dolbilka.tmpfile() as plan_queries:
                dolbilka.unpack_plan_resource(plan_resource_id, plan_queries)
                for cgi_params in params_list:
                    cgi_params = cgi_params.strip()
                    if not cgi_params:
                        continue

                    self._test_exp_performance(
                        plan_resource_id,
                        plan_queries,
                        exp_index,
                        cgi_params,
                        remove_cgi_params,
                        exp_data,
                        sub_tasks
                    )
                    exp_index += 1

            self.ctx[_EXP_WITHOUT_RPS] = exp_data
            # wait all tasks
            self.ctx[_CHILD_TASK_IDS_KEY] = sub_tasks

        utils.wait_all_subtasks_stop()

        exp_data = self.ctx.get(_EXP_WITHOUT_RPS, '{}')

        for exp_index in exp_data:
            exp = exp_data[exp_index]
            task_id = exp['task_id']
            child = channel.sandbox.get_task(task_id)

            max_rps = max(child.ctx.get('requests_per_sec', [0]))
            logging.debug("task_id: {} rps: {}".format(task_id, child.ctx.get('requests_per_sec', [0])))
            exp_data[exp_index]['rps'] = max_rps

        if _BASELINE not in exp_data:
            exp_data[_BASELINE] = copy.deepcopy(exp_data['0'])
            logging.debug("add '0'-baseline, because we hasn't got true baseline")

        self.ctx[_EXPERIMENTS] = json.dumps(exp_data)

        if test_memory_usage:
            memory_task = channel.sandbox.get_task(self.ctx['test_basesearch_memory_task_id'])
            self.ctx['pmap_RSS_for_models'] = memory_task.ctx.get('pmap_RSS', 0)

    def _test_exp_performance(
            self,
            plan_resource_id,
            plan_queries,
            exp_index,
            cgi_params,
            remove_cgi_params,
            exp_data,
            sub_tasks
    ):
        logging.info("Running experiment #%s with cgi params '%s'", exp_index, cgi_params)
        # test basesearch with patched plan
        exp_performance_task_id = self._test_basesearch(
            dolbilka.patch_plan_queries(plan_resource_id, plan_queries, cgi_params, remove_cgi_params).id,
            description="{} [{}]".format(self.descr, cgi_params),
            profiling_type=utils.get_or_default(self.ctx, profiling.ProfilingTypeParameter),
        )
        exp_data[str(exp_index)] = {
            'task_id': exp_performance_task_id,
            'cgi_params': cgi_params,
        }
        sub_tasks.append(exp_performance_task_id)
        logging.debug("adding exp_perf_task_id: {} into subtasks".format(exp_performance_task_id))

    def _test_memory_usage(self, plan_resource_id, sub_tasks):
        # run basesearch with memory usage measurement (without plan patch)
        task_id = self._test_basesearch(
            plan_resource_id,
            description="Baseline memory usage",
            pmap=True
        )
        self.ctx['test_basesearch_memory_task_id'] = task_id
        sub_tasks.append(task_id)
        logging.debug("adding memusage_task: {} into sub_tasks".format(task_id))

    def _test_baseline_performance(self, plan_resource_id, exp_data, sub_tasks):
        # test basesearch without patching the plan
        baseline_task_id = self._test_basesearch(
            plan_resource_id,
            description="{} [{}]".format(self.descr, "baseline"),
            profiling_type=utils.get_or_default(self.ctx, profiling.ProfilingTypeParameter),
        )
        exp_data[_BASELINE] = {
            'task_id': baseline_task_id,
            'cgi_params': "(baseline)",
        }
        sub_tasks.append(baseline_task_id)
        logging.debug("adding baseline_task_id: {} into sub_tasks".format(baseline_task_id))

    def _test_basesearch(
        self,
        plan_resource_id,
        description,
        pmap=False,
        profiling_type=profiling.ProfilingTypeParameter.NONE,
    ):
        """
        Creates basesearch performance task.
        @param plan_resource_id: plan resource id
        @param description: task description
        @param pmap: run memory test
        @param profiling_type: profiling type (see 'profiling' module for details)
        @return: created task id
        """
        model_archive_res_id = self.ctx.get(ModelsArchive.name)
        if not model_archive_res_id:
            model_archive_res_id = utils.get_and_check_last_released_resource_id(ModelsArchive.resource_type)
        use_profiling = profiling_type != profiling.ProfilingTypeParameter.NONE
        sub_ctx = {
            'basesearch_executable_resource_id': self._binary_resource_id,
            'basesearch_config_resource_id': self._config_resource_id,
            'basesearch_database_resource_id': self._db_resource_id,
            'basesearch_models_archive_resource_id': model_archive_res_id,
            'basesearch_polite_mode': False,
            'dolbilo_plan_resource_id': plan_resource_id,
            'dolbilka_executor_requests_limit': int(utils.get_or_default(self.ctx, RequestsLimit)),
            'dolbilka_executor_mode': 'finger',
            'dolbilka_executor_max_simultaneous_requests': 21,
            'dolbilka_executor_sessions': 20,
            'notify_via': '',
            'pmap_models_archive': pmap,
            'number_of_runs': 3 if use_profiling else 1,
            profiling.ProfilingTypeParameter.name: profiling_type,
        }

        task_type = "TEST_BASESEARCH_PERFORMANCE_BEST"
        cpu_model_filter = self.cpu_model_filter
        if use_profiling:
            task_type = "TEST_BASESEARCH_PERFORMANCE_TANK"
            # SEARCH-3990
            cpu_model_filter = 'e5-2650'

        return self.create_subtask(
            task_type=task_type,
            input_parameters=sub_ctx,
            description=description,
            model=cpu_model_filter,
            host=self.client_hostname_filter,
            arch=self.arch,
        ).id


__Task__ = TestBasesearchExperiment
