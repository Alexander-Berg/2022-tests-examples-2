# -*- coding: utf-8 -*-

from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk import paths

from sandbox.projects.common.news.parallel_performance_task import BaseTestPerformanceParallelTask
from sandbox.projects.common.news.newsd import create_newsd_params, SlaveNewsd


class Binary1(sp.ResourceSelector):
    name = "newsd_executable_1"
    description = "Executable first"
    resource_type = [
        'SLAVE_NEWSD_EXECUTABLE'
    ]
    group = "Newsd params"
    requred = True


class Binary2(sp.ResourceSelector):
    name = "newsd_executable_2"
    description = "Executable second"
    resource_type = [
        'SLAVE_NEWSD_EXECUTABLE'
    ]
    group = "Newsd params"
    requred = True


class ApphostMode(sp.SandboxBoolParameter):
    name = 'apphost_mode'
    description = 'Shoot to AppHost port'
    default_value = False
    group = "Newsd apphost params"


class RedefineApphostSlaveQueueSize(sp.SandboxBoolParameter):
    name = 'redefine_apphost_slave_queue_size'
    description = 'Redefine apphost slave queue size'
    default_value = False
    group = "Newsd apphost params"


class ApphostSlaveQueueSize(sp.SandboxIntegerParameter):
    name = 'apphost_slave_queue_size'
    description = 'Apphost slave queue size (It\'s better to be more than <Max simultaneous requests> param in dolbilo params )'
    default_value = 300
    group = "Newsd apphost params"


class TestNewsdPerformanceParallel(BaseTestPerformanceParallelTask):
    """
        Параллельный запуск тестирования
    """

    type = 'TEST_NEWSD_PERFORMANCE_PARALLEL'

    newsd_params = create_newsd_params()
    input_newsd_params = newsd_params.params[1:]  # without binary

    input_parameters = (
        (
            Binary1,
            Binary2,
        ) +
        BaseTestPerformanceParallelTask.input_parameters +
        input_newsd_params +
        (
            ApphostMode,
            RedefineApphostSlaveQueueSize,
            ApphostSlaveQueueSize,
        )
    )

    def _get_binary(self, index):
        binary_map = {
            1: Binary1,
            2: Binary2,
        }
        binary = binary_map[index]

        workdir = self.path('work')
        paths.make_folder(workdir, True)
        port = 17171

        newsd = SlaveNewsd(workdir=workdir,
                           binary=self.sync_resource(self.ctx.get(binary.name)),
                           cfg=self.sync_resource(self.ctx[self.newsd_params.Config.name]),
                           port=port,
                           state=self.sync_resource(self.ctx[self.newsd_params.StateDump.name]),
                           geobase=self.sync_resource(self.ctx[self.newsd_params.Geobase.name]),
                           index_config_path=self.sync_resource(self.ctx[self.newsd_params.IndexConfig.name]),
                           app_host_mode=self.ctx.get(ApphostMode.name),
                           app_host_queue_size=self.ctx.get(ApphostSlaveQueueSize.name) if self.ctx.get(RedefineApphostSlaveQueueSize.name) else None,
                           )

        return newsd

    def _get_first_bin(self):
        """
             Возвращает первый бинарник
        """

        return self._get_binary(index=1)

    def _get_second_bin(self):
        """
            Возвращает второй бинарник
        """

        return self._get_binary(index=2)


__Task__ = TestNewsdPerformanceParallel
