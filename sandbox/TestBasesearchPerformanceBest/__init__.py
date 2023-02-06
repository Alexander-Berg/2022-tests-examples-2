# -*- coding: utf-8 -*-

from sandbox.sandboxsdk import parameters

from sandbox.projects.websearch.basesearch import TestBasesearchPerformance as tbp
from sandbox.projects.websearch.basesearch.TestBasesearchPerformanceTank import TestBasesearchPerformanceTank
from sandbox.projects.common.TestPerformanceBest import BaseTestPerformanceBestTask
from sandbox.projects.common import utils
from sandbox.projects.common.search import components as sc
from sandbox.projects.common.search import params_handler


class UseTank(parameters.SandboxBoolParameter):
    name = 'use_tank'
    description = 'Use TANK performance task'
    default_value = False


class TestBasesearchPerformanceBest(BaseTestPerformanceBestTask):
    """
        Параллельный запуск тестирования базового с последующей агрегацией результатов.
        Запускается указанное количество подзадач типа TEST_BASESEARCH_PERFORMANCE (параметр number_of_runs)

        Выбирается лучший обстрел.
    """

    type = 'TEST_BASESEARCH_PERFORMANCE_BEST'
    execution_space = 1024  # 1 Gb
    cores = 1

    input_parameters = (
        (
            UseTank,
            params_handler.QueryType,
            params_handler.TierName,
        ) +
        BaseTestPerformanceBestTask.input_parameters +
        sc.create_basesearch_params(
            config_required=False,
            database_required=False,
            archive_model_required=False,
        ).params +
        tbp.TestBasesearchPerformance.additional_performance_params
    )

    def _get_performance_task_type(self):
        return (
            TestBasesearchPerformanceTank.type
            if utils.get_or_default(self.ctx, UseTank) else tbp.TestBasesearchPerformance.type
        )

    def set_optional_input_params(self):
        """SEARCH-2352"""
        params_handler.set_optional_param(sc.DefaultBasesearchParams.Config)
        params_handler.set_optional_param(sc.DefaultBasesearchParams.ArchiveModel)
        params_handler.set_interrelated_params(
            tbp.PlanParameter,
            "TE_web_base_prod_queries_{}_{}".format(
                self.ctx.get(params_handler.QueryType.name),
                self.ctx.get(params_handler.TierName.name)
            ),
            sc.DefaultBasesearchParams.Database,
            "TE_web_base_prod_resources_{}_{}".format(
                self.ctx.get(params_handler.QueryType.name),
                self.ctx.get(params_handler.TierName.name),
            )
        )


__Task__ = TestBasesearchPerformanceBest
