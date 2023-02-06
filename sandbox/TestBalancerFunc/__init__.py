# -*- coding: utf-8 -*-
"""
Functional balancer tests
"""
from sandbox.projects.common.balancer.task import BaseTestBalancerTask


class TestBalancerFunc(BaseTestBalancerTask):
    """
        **Описание**
            Функциональные тесты балансера.

        **Необходимые ресурсы**

            * BALANCER_EXECUTABLE - исполняемый файл балансера
    """
    type = 'TEST_BALANCER_FUNC'
    execution_space = 250 * 1024

    @staticmethod
    def get_targets():
        return ['balancer/test/functional', 'balancer/kernel', 'balancer/modules']

    def initCtx(self):
        BaseTestBalancerTask.initCtx(self)
        self.ctx['kill_timeout'] = 60 * 60 * 4


__Task__ = TestBalancerFunc
