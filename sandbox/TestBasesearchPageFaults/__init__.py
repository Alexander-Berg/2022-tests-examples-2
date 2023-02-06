# -*- coding: utf-8 -*-

import logging

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import SandboxStringParameter
from sandbox.sandboxsdk.parameters import SandboxIntegerParameter
from sandbox.projects.common.dolbilka import DolbilkaExecutor
from sandbox.projects.common.base_search_quality import settings as bss
from sandbox.sandboxsdk.process import get_process_info
from sandbox.projects.common.search.components import DefaultBasesearchParams, get_basesearch

from sandbox.projects.common import apihelpers


class TestBasesearchPlansTier(SandboxStringParameter):
    name = 'basesearch_plans_tier'
    description = 'Plans for tier:'
    default_value = bss.DEFAULT_TIER


class TestBasesearchPlansNumber(SandboxIntegerParameter):
    name = 'basesearch_plans_count'
    description = 'Plans max number:'
    default_value = 10


class TestBasesearchPageFaults(SandboxTask):

    type = 'TEST_BASESEARCH_PAGE_FAULTS'

    input_parameters = (
        DefaultBasesearchParams.params + (
            TestBasesearchPlansTier,
            TestBasesearchPlansNumber
        ) +
        DolbilkaExecutor.input_task_parameters
    )

    def get_plans(self, tier, count):
        """
            Получить @count последних планов приёмки для @tier
            @channel: объект для взаимодействия с сервером Sandbox
            @tier: название tier
            @count: количество планов
            @return: список идентификаторов планов
        """
        logging.info('Get %s plans for tier %s' % (count, tier))
        attribute_name = '%s_priemka' % tier
        attribute_value = '1'
        return apihelpers.get_resources_with_attribute(
            resource_type='BASESEARCH_PLAN',
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            limit=count,
        )

    def on_execute(self):
        basesearch = get_basesearch()
        d_executor = DolbilkaExecutor()
        basesearch_plans_count = self.ctx.get('basesearch_plans_count', 10)
        basesearch_plans_tier = self.ctx.get('basesearch_plans_tier', bss.DEFAULT_TIER)
        plans = self.get_plans(basesearch_plans_tier, basesearch_plans_count)
        basesearch.start()
        basesearch.wait()

        self.ctx['results'] = []
        for plan in plans:
            plan_result = {}
            session_id = 'session_with_plan_%s' % plan.id
            page_faults_before = get_process_info(basesearch.process.pid, ('majflt', ))['majflt']
            plan_path = self.sync_resource(plan.id)
            dump_path = self.path('%s.dump' % session_id)
            logging.info('plan path %s, dump path %s' % (plan_path, dump_path))
            d_executor.run_session(plan=plan_path, dump=dump_path, port=basesearch.port,
                                   log_prefix='d_executor_%s' % session_id)
            page_faults_after = get_process_info(basesearch.process.pid, ('majflt', ))['majflt']
            result_stat = d_executor.dumper.get_results(dump_path)
            plan_result['session_id'] = session_id
            plan_result.update(d_executor.dumper.parse_dolbilka_stat(result_stat))
            plan_result['page_faults_after'] = page_faults_after
            plan_result['page_faults_before'] = page_faults_before
            plan_result['page_faults'] = int(page_faults_after) - int(page_faults_before)
            self.ctx['results'].append(plan_result)
        basesearch.stop()


__Task__ = TestBasesearchPageFaults
