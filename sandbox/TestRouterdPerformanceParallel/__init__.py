# -*- coding: utf-8 -*-

from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk import paths

from sandbox.projects.common.news.parallel_performance_task import BaseTestPerformanceParallelTask
from sandbox.projects.common.news.routerd import Routerd, create_routerd_params


class Binary1(sp.ResourceSelector):
    name = "routerd_executable_1"
    description = "Executable first"
    resource_type = [
        'NEWS_APPHOST_ROUTERD_EXECUTABLE'
    ]
    group = "Rourterd params"
    requred = True


class Binary2(sp.ResourceSelector):
    name = "routerd_executable_2"
    description = "Executable second"
    resource_type = [
        'NEWS_APPHOST_ROUTERD_EXECUTABLE'
    ]
    group = "Rourterd params"
    requred = True


class TestRouterdPerformanceParallel(BaseTestPerformanceParallelTask):
    """
        Параллельный запуск тестирования
    """

    type = 'TEST_ROUTERD_PERFORMANCE_PARALLEL'

    routerd_params = create_routerd_params()
    input_routerd_params = routerd_params.params[1:]  # without binary

    input_parameters = (
        (
            Binary1,
            Binary2,
        ) +
        BaseTestPerformanceParallelTask.input_parameters +
        input_routerd_params
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

        routerd = Routerd(binary=self.sync_resource(self.ctx.get(binary.name)),
                          workdir=workdir,
                          port=port,
                          geobase=self.sync_resource(self.ctx[self.routerd_params.Geobase.name]),
                          newsdata=self.sync_resource(self.ctx[self.routerd_params.NewsData.name]) + "/newsdata2.json",
                          newsdata_exp=self.sync_resource(self.ctx[self.routerd_params.NewsDataExp.name]) + "/newsdata2.json",
                          device_data=self.sync_resource(self.ctx[self.routerd_params.DeviceData.name]),
                          allowed_origins=self.sync_resource(self.ctx[self.routerd_params.AllowedOrigins.name]),
                          dynamic_robots_txt=self.sync_resource(self.ctx[self.routerd_params.DynamicRobotsTxtConfig.name])
                          )

        return routerd

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


__Task__ = TestRouterdPerformanceParallel
