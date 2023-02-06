# -*- coding: utf-8 -*-

from sandbox import sdk2

from sandbox.projects.sandbox_ci.task.test_task.BaseHermioneCommonTask import BaseHermioneCommonTask


class BaseHermioneTask(BaseHermioneCommonTask):
    tool = 'hermione'

    class Parameters(BaseHermioneCommonTask.Parameters):
        with sdk2.parameters.String('Режим запуска', required=True) as play_mode:
            play_mode.values['dumps'] = play_mode.Value(u'Запуск с использованием дампов', default=True)
            play_mode.values['real_data'] = u'Запуск на реальных данных'

    @property
    def run_opts(self):
        opts = []
        if (self.Parameters.play_mode == 'dumps'):
            opts.append('--play')

        opts.append(super(BaseHermioneTask, self).run_opts)

        return ' '.join(opts)
