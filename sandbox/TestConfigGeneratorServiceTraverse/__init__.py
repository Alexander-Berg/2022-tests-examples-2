# -*- coding: utf-8 -*-

from sandbox.sandboxsdk.process import run_process

from sandbox.projects.common.gencfg.task import IGencfgTask


class TestConfigGeneratorServiceTraverse(IGencfgTask):
    type = 'TEST_CONFIG_GENERATOR_SERVICE_TRAVERSE'

    def on_enqueue(self):
        pass

    def on_execute(self):
        bootstrap = self.abs_path("bootstrap.sh")
        run_process(['curl', '-f', 'http://api.gencfg.yandex-team.ru/bootstrap.sh', "-o", bootstrap], work_dir=self.abs_path(), log_prefix='get bootstrap')
        gencfg_dir = self.abs_path('gencfg')
        run_process(['chmod', "755", bootstrap], work_dir=self.abs_path(), log_prefix='chmod')
        run_process([bootstrap, 'full', gencfg_dir], work_dir=self.abs_path(), log_prefix='run bootstrap')
        run_process(['web_utils/run_dolbilo_on_prod.sh'], work_dir=gencfg_dir, log_prefix='run dolbilo')


__Task__ = TestConfigGeneratorServiceTraverse
