# -*- coding: utf-8 -*-
import copy
import json
import os
import stat
import logging

from sandbox.common.types.client import Tag
import sandbox.common.types.task as ctt

import sandbox.sdk2 as sdk2

from sandbox.projects.TestRTYServerUnit import TestRTYServerUnit
from sandbox.sandboxsdk.errors import SandboxTaskFailureError, SandboxTaskUnknownError
from sandbox.sandboxsdk.channel import channel


class TestDolbParameters(sdk2.Parameters):
    run_n_dolbs = sdk2.parameters.Integer('Number of runs')
    child_tasks_prio = sdk2.parameters.String('child tasks prio', default='BACKGROUND_NORMAL')
    acceptable_errors_perc = sdk2.parameters.Integer('Acceptable errors %', default=1)
    save_large_logs = sdk2.parameters.Bool('save large logs', default=False)


class TestRTYServerDolbiloM(TestRTYServerUnit):

    type = 'TEST_RTYSERVER_DOLBILOM'
    client_tags = Tag.GENERIC & Tag.HDD & Tag.INTEL_E5_2660
    input_parameters = list(TestDolbParameters) \
        + TestRTYServerUnit.input_parameters

    execution_space = 150000

    def initCtx(self):
        TestRTYServerUnit.initCtx(self)
        self.ctx['plots_data'] = '[]'
        self.ctx['plots_values'] = []

    def on_failure(self):
        TestRTYServerUnit.on_failure(self)

    def postprocess(self):
        TestRTYServerUnit.postprocess(self)

    def on_enqueue(self):
        TestRTYServerUnit.on_enqueue(self)
        if self.owner == 'RTYSERVER-ROBOT':
            self.semaphores(ctt.Semaphores(
                acquires=[
                    ctt.Semaphores.Acquire(name='saas-loadtest', weight=1, capacity=16)
                ]
            ))
        else:
            self.semaphores(ctt.Semaphores(
                acquires=[
                    ctt.Semaphores.Acquire(name='saas-loadtest-other', weight=1, capacity=16)
                ]
            ))

    def on_execute(self):

        custom_subtasks = ',' in self.ctx.get('rtyserver_other_parameter')

        if self.ctx.get('no_more_runs', False):
            if not self.completed_subtasks():
                self.set_info('Subtasks in BREAK statuses found')
                raise SandboxTaskUnknownError('Subtasks in BREAK statuses found')
            self.choose_best_sub()
            if custom_subtasks:
                self.get_subtasks_fields()
            self.ctx['no_more_runs'] = False
            return

        runs = self.ctx.get('run_n_dolbs', 1)
        self.ctx['run_n_dolbs'] = 1

        if not custom_subtasks and runs == 1:
            TestRTYServerUnit.on_execute(self)
        if not self.ctx.get('save_large_logs'):
            for fold in [self.log_path(f) for f in os.listdir(self.log_path())
                         if os.path.isdir(self.log_path(f))] + [self.log_path()]:
                for evlog in [os.path.join(fold, f) for f in os.listdir(fold)
                              if 'event.log' in f or 'incoming.log' in f]:
                    logging.info('file %s will be deleted' % evlog)
                    os.unlink(evlog)
                for evlog in [os.path.join(fold, f) for f in os.listdir(fold)
                              if ('dolb_dump' in f or 'access.log' in f)
                              and os.stat(os.path.join(fold, f))[stat.ST_SIZE] > 1000000000]:
                    logging.info('file %s with size %s will be deleted' % (evlog, os.stat(evlog)[stat.ST_SIZE]))
                    os.unlink(evlog)

        def get_max(res_str):
            return max([float(v.strip()) for v in res_str.split(',') if len(v.strip()) > 0])

        try:
            self.ctx['best_rps'] = get_max(self.ctx.get('result_rps', '0').strip(', '))
        except:
            self.ctx['best_rps'] = 0
        try:
            self.ctx['max_errors'] = get_max(self.ctx.get('result_errors', '0').strip(', '))
        except:
            self.ctx['max_errors'] = 0
        if self.ctx['max_errors'] == 0:
            try:
                self.ctx['max_errors'] = get_max(self.ctx.get('dolbilo_errors', '0').strip(', '))
            except:
                self.ctx['max_errors'] = 0
        try:
            self.ctx['max_result_empty'] = get_max(self.ctx.get('result_empty', '0').strip(', '))
        except:
            self.ctx['max_result_empty'] = 0
        try:
            self.ctx['max_result_empty_perc'] = get_max(self.ctx.get('result_empty_perc', '0').strip(', '))
        except:
            self.ctx['max_result_empty_perc'] = 0
        try:
            self.ctx['max_dolbilo_errors_perc'] = get_max(self.ctx.get('dolbilo_errors_perc', '0').strip(', '))
        except:
            self.ctx['max_dolbilo_errors_perc'] = 0

        if 'Time' in self.ctx.get('rtyserver_test_parameter', ''):
            self.ctx['best_rps'] = self.ctx['rty_tests_work_time_seconds']
            self.ctx['result_rps'] = self.ctx['rty_tests_work_time_seconds']

        try:
            if runs == 1 and not custom_subtasks:
                self.set_info('<font color="green">best_rps: ' + str(self.ctx['best_rps']) + '</font>', do_escape=False)
        except:
            pass

        if runs > 1 or custom_subtasks:
            subt = []
            if custom_subtasks:
                parts = self.ctx.get('rtyserver_other_parameter').split()
                if '-g' in parts:
                    i = parts.index('-g')
                    if len(parts) == i+1:
                        raise SandboxTaskFailureError('-g without parameter found')
                    for j, conf in enumerate(parts[i+1].split(',')):
                        sub_param = parts[:]
                        add_ctx = {}
                        try:
                            nbe = int(conf.split('_cluster_')[-1].split('_emuls')[0])
                            add_ctx['parser_rules'] = self.ctx.get('parser_rules', '').replace('_NBE_', str(nbe))
                        except:
                            pass
                        sub_param[i+1] = conf
                        subt.append(self._create_subtask(j, ' '.join(sub_param), add_ctx))
            else:
                for i in range(0, runs):
                    subt.append(self._create_subtask(i))
            self.ctx['no_more_runs'] = True
            self.execution_space = 30000
            self.wait_all_tasks_stop_executing(subt)
            # self.wait_all_tasks_completed(subt)

        if float(self.ctx['best_rps']) < 1 and not self.ctx.get('skip_check_rps'):
            raise SandboxTaskFailureError('Resulting rps is zero. Something is wrong with task')
        max_acc_err = self.ctx.get('acceptable_errors_perc', 1) or 1
        if float(self.ctx.get('max_dolbilo_errors_perc', 0)) > max_acc_err:
            raise SandboxTaskFailureError('Too many errors (> {0}%)'.format(max_acc_err))

    def completed_subtasks(self):
        subt = self.list_subtasks(load=True)
        undone_subs = [s for s in subt if s.status in self.Status.Group.BREAK]
        if undone_subs:
            logging.info('Subtasks in BREAK statuses found: %s' % undone_subs)
            return False
        return True

    def _create_subtask(self, subt_number, conf_str='', add_ctx=None):
        child_ctx = copy.deepcopy(self.ctx)
        child_ctx['result_rps'] = ''
        child_ctx['best_rps'] = ''
        child_ctx['max_errors'] = ''
        child_ctx['result_errors'] = ''
        child_ctx['dolbilo_errors'] = ''
        child_ctx['result_empty'] = ''
        child_ctx['max_result_empty'] = ''
        child_ctx['result_empty_perc'] = ''
        child_ctx['max_result_empty_perc'] = ''
        child_ctx['dolbilo_errors_perc'] = ''
        child_ctx['max_dolbilo_errors_perc'] = ''
        child_ctx['max_memory_gb'] = 0
        if conf_str:
            child_ctx['rtyserver_other_parameter'] = conf_str
        if add_ctx:
            child_ctx.update(add_ctx)
        return self.create_subtask(self.type, 'subtask %s %s' % (str(subt_number), self.descr),
                                   input_parameters=child_ctx, execution_space=self.execution_space)
        #  priority=self.ctx.get('child_tasks_prio', 'BACKGROUND_NORMAL').split('_')

    def choose_best_sub(self):
        subt = self.list_subtasks(load=True, completed_only=True)
        self.ctx['best_rps'] = max(
            [
                float(sub.ctx.get('best_rps', 0) or 0)
                for sub in subt if sub.status != self.Status.FAILURE
            ] + [float(self.ctx['best_rps'] or 0)]
        )
        self.set_info('<font color="green">best_rps: ' + str(self.ctx['best_rps']) + '</font>', do_escape=False)

        self.ctx['results_rps'] = ', '.join(
            [
                str(sub.ctx.get('result_rps', '0'))
                for sub in subt if sub.status != self.Status.FAILURE
            ] + [str(self.ctx.get('result_rps', '0'))]
        )

        self.ctx['results_errors'] = ', '.join(
            [str(sub.ctx.get('result_errors', '0')) for sub in subt] +
            [str(self.ctx.get('result_errors', '0'))]
        )

        self.ctx['dolbilo_errors'] = ', '.join(
            [str(sub.ctx.get('dolbilo_errors', '0')) for sub in subt] +
            [str(self.ctx.get('dolbilo_errors', '0'))]
        )

        self.ctx['results_empty'] = ', '.join(
            [str(sub.ctx.get('result_empty', '0')) for sub in subt] +
            [str(self.ctx.get('result_empty', '0'))]
        )

        self.ctx['results_empty_perc'] = ', '.join(
            [str(sub.ctx.get('result_empty_perc', '0')) for sub in subt] +
            [str(self.ctx.get('result_empty_perc', '0'))]
        )

        self.ctx['dolbilos_errors_perc'] = ', '.join(
            [str(sub.ctx.get('dolbilo_errors_perc', '0')) for sub in subt] +
            [str(self.ctx.get('dolbilo_errors_perc', '0'))]
        )

        try:
            self.ctx['max_errors'] = max(
                [
                    float(sub.ctx.get('max_errors', 0))
                    for sub in subt if str(sub.ctx.get('max_errors', 0))
                ] + [
                    float(self.ctx.get('max_errors', 0))
                    if str(self.ctx.get('max_errors', 0)) else
                    0
                ]
            )

        except:
            self.ctx['max_errors'] = 0

        try:
            self.ctx['max_result_empty'] = max(
                [
                    float(sub.ctx.get('max_result_empty', 0))
                    for sub in subt if str(sub.ctx.get('max_result_empty', 0))
                ] + [
                    float(self.ctx.get('max_result_empty', 0))
                    if str(self.ctx.get('max_result_empty', 0)) else
                    0
                ]
            )

        except:
            self.ctx['max_result_empty'] = 0

        try:
            self.ctx['max_result_empty_perc'] = max(
                [
                    float(sub.ctx.get('max_result_empty_perc', 0))
                    for sub in subt if str(sub.ctx.get('max_result_empty_perc', 0))
                ] + [
                    float(self.ctx.get('max_result_empty_perc', 0))
                    if str(self.ctx.get('max_result_empty_perc', 0)) else 0
                ]
            )

        except:
            self.ctx['max_result_empty_perc'] = 0

        try:
            self.ctx['max_dolbilo_errors_perc'] = max(
                [
                    float(sub.ctx.get('max_dolbilo_errors_perc', 0))
                    for sub in subt if str(sub.ctx.get('max_dolbilo_errors_perc', 0))
                ] + [
                    float(self.ctx.get('max_dolbilo_errors_perc', 0))
                    if str(self.ctx.get('max_dolbilo_errors_perc', 0)) else
                    0
                ]
            )

        except:
            self.ctx['max_dolbilo_errors_perc'] = 0

        try:
            self.ctx['max_memory_gb'] = max(
                [float(sub.ctx.get('max_memory_gb', 0)) for sub in subt] +
                [float(self.ctx.get('max_memory_gb', 0))]
            )

            self.ctx['max_cpu_perc'] = max(
                [float(sub.ctx.get('max_cpu_perc', 0)) for sub in subt] +
                [float(self.ctx.get('max_cpu_perc', 0))]
            )

        except:
            pass

        if float(self.ctx['best_rps']) < 1 and not self.ctx.get('skip_check_rps'):
            raise SandboxTaskFailureError('Resulting rps is zero. Something is wrong with task')
        max_acc_err = self.ctx.get('acceptable_errors_perc', 1) or 1
        if float(self.ctx.get('max_dolbilo_errors_perc', 0)) > max_acc_err:
            raise SandboxTaskFailureError('Too many errors (> {0}%)'.format(max_acc_err))

    def get_subtasks_fields(self):
        subt = self.list_subtasks(load=True, completed_only=True)
        values = {}
        dig_values = {}
        for sub in subt:
            for ctf in sub.ctx:
                if ctf.startswith('to_parent_'):
                    values[ctf.replace('to_parent_', 'sub_')] = sub.ctx[ctf]
                    try:
                        value = float(ctf.split('_')[-1])
                        descr = '_'.join(ctf.split('_')[2:-1])  # to_parent_..._10
                        if descr not in dig_values:
                            dig_values[descr] = []
                        dig_values[descr].append([value, float(sub.ctx[ctf])])
                    except:
                        pass
        for desc in dig_values:
            cur_values = sorted(dig_values[desc], key=lambda x: x[0])
            self.ctx['plots_values'].append({'name': desc, 'data': cur_values})
            if 'response_time' in desc:
                self.ctx['plots_values'][-1]['y'] = 'microsec'
            elif 'result_rps' in desc:
                self.ctx['plots_values'][-1]['y'] = 'rps'
            if (
                'n_emuls' in self.ctx['rtyserver_other_parameter'] and
                ('response_time' in desc or 'result_rps' in desc)
            ):
                self.ctx['plots_values'][-1]['x'] = 'backends_number'
        self.ctx.update(values)

    def on_finish(self):
        TestRTYServerUnit.on_finish(self)
        self.ctx['plots_data'] = json.dumps(self.ctx.get('plots_values', []))
        self.cleanup()

    def on_success(self):
        TestRTYServerUnit.on_success(self)
        for resource in self.list_resources(resource_type='TASK_LOGS'):
            try:
                if resource.size > 2000000:
                    channel.sandbox.set_resource_attribute(resource, 'ttl', 7)
            except Exception as e:
                self.set_info('%s' % e)


__Task__ = TestRTYServerDolbiloM
