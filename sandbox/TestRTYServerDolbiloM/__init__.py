# -*- coding: utf-8 -*-
import json
import os
import stat
import logging

from sandbox.common.types.client import Tag
import sandbox.common.types.task as ctt

import sandbox.sdk2 as sdk2

from sandbox.projects.saas.TestRTYServerUnit import TestRTYServer as TestRTYServerUnit
from sandbox.sandboxsdk.errors import SandboxTaskFailureError, SandboxTaskUnknownError
from sandbox.sandboxsdk.channel import channel


class TestRTYServerDolbilo(TestRTYServerUnit):

    class Parameters(TestRTYServerUnit.Parameters):
        run_n_dolbs = sdk2.parameters.Integer('Number of runs')
        child_tasks_prio = sdk2.parameters.String('child tasks prio', default='BACKGROUND_NORMAL')
        acceptable_errors_perc = sdk2.parameters.Integer('Acceptable errors %', default=1)
        save_large_logs = sdk2.parameters.Bool('save large logs', default=False)
        skip_check_rps = sdk2.parameters.Bool('skip check rps', default=False)

    class Context(TestRTYServerUnit.Context):
        plots_data = '[]'
        no_more_runs = False
        best_rps = 0
        max_errors = 0
        max_result_empty = 0
        max_result_empty_perc = 0
        max_dolbilo_errors_perc = 0

    class Requirements(TestRTYServerUnit.Requirements):
        disk_space = 150000
        client_tags = Tag.GENERIC & Tag.HDD & Tag.INTEL_E5_2660

    def on_failure(self, prev_status):
        TestRTYServerUnit.on_failure(self, prev_status)

    def on_enqueue(self):
        TestRTYServerUnit.on_enqueue(self)
        if self.owner == 'RTYSERVER-ROBOT':
            self.Requirements.semaphores = ctt.Semaphores(
                acquires=[
                    ctt.Semaphores.Acquire(name='saas-loadtest', weight=1, capacity=16)
                ]
            )
        else:
            self.Requirements.semaphores = ctt.Semaphores(
                acquires=[
                    ctt.Semaphores.Acquire(name='saas-loadtest-other', weight=1, capacity=16)
                ]
            )
        if self.Context.no_more_runs:
            self.Requirements.disk_space = 30000

    def on_execute(self):

        custom_subtasks = ',' in self.Parameters.rtyserver_other_parameter

        if self.Context.no_more_runs:
            if not self.completed_subtasks():
                self.set_info('Subtasks in BREAK statuses found')
                raise SandboxTaskUnknownError('Subtasks in BREAK statuses found')
            self.choose_best_sub()
            if custom_subtasks:
                self.get_subtasks_fields()
            self.Context.no_more_runs = False
            return

        runs = self.Parameters.run_n_dolbs or 1
        # self.ctx['run_n_dolbs'] = 1

        if not custom_subtasks and runs == 1:
            TestRTYServerUnit.on_execute(self)
        if not self.Parameters.save_large_logs:
            for fold in [str(self.log_path(f)) for f in os.listdir(str(self.log_path()))
                         if os.path.isdir(str(self.log_path(f)))] + [str(self.log_path())]:
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
            self.Context.best_rps = get_max(self.Context.dolbilo_result.get('result_rps', '0').strip(', '))
        except:
            self.Context.best_rps = 0
        try:
            self.Context.max_errors = get_max(self.Context.dolbilo_result.get('result_errors', '0').strip(', '))
        except:
            pass
        if self.Context.max_errors == 0:
            try:
                self.Context.max_errors = get_max(self.Context.dolbilo_result.get('dolbilo_errors', '0').strip(', '))
            except:
                pass
        try:
            self.Context.max_result_empty = get_max(self.Context.dolbilo_result.get('result_empty', '0').strip(', '))
        except:
            pass
        try:
            self.Context.max_result_empty_perc = get_max(self.Context.dolbilo_result.get('result_empty_perc', '0').strip(', '))
        except:
            pass
        try:
            self.Context.max_dolbilo_errors_perc = get_max(self.Context.dolbilo_result.get('dolbilo_errors_perc', '0').strip(', '))
        except:
            pass

        if 'Time' in self.Parameters.rtyserver_test_parameter:
            self.Context.best_rps = self.Context.rty_tests_work_time_seconds
            self.Context.dolbilo_result['result_rps'] = self.Context.rty_tests_work_time_seconds

        try:
            if runs == 1 and not custom_subtasks:
                self.set_info('<font color="green">best_rps: ' + str(self.Context.best_rps) + '</font>', do_escape=False)
        except:
            pass

        if runs > 1 or custom_subtasks:
            subt = []
            if custom_subtasks:
                parts = self.Parameters.rtyserver_other_parameter.split()
                if '-g' in parts:
                    i = parts.index('-g')
                    if len(parts) == i+1:
                        raise SandboxTaskFailureError('-g without parameter found')
                    for j, conf in enumerate(parts[i+1].split(',')):
                        sub_param = parts[:]
                        add_ctx = {}
                        try:
                            nbe = int(conf.split('_cluster_')[-1].split('_emuls')[0])
                            add_ctx['parser_rules'] = self.Parameters.parser_rules.replace('_NBE_', str(nbe))
                        except:
                            pass
                        sub_param[i+1] = conf
                        subt.append(self._create_subtask(j, ' '.join(sub_param), add_ctx))
            else:
                for i in range(0, runs):
                    subt.append(self._create_subtask(i))
            self.Context.no_more_runs = True
            raise sdk2.WaitTask(subt, ctt.Status.Group.FINISH + ctt.Status.Group.BREAK, wait_all=True)

        if float(self.Context.best_rps) < 1 and not self.Parameters.skip_check_rps:
            raise SandboxTaskFailureError('Resulting rps is zero. Something is wrong with task')
        max_acc_err = self.Parameters.acceptable_errors_perc or 1
        if self.Context.max_dolbilo_errors_perc > max_acc_err:
            raise SandboxTaskFailureError('Too many errors (> {0}%)'.format(max_acc_err))

    def completed_subtasks(self):
        undone_subs = list(self.find(TestRTYServerDolbilo, status=ctt.Status.Group.BREAK).limit(30))
        if undone_subs:
            logging.info('Subtasks in BREAK statuses found: %s' % undone_subs)
            return False
        return True

    def _create_subtask(self, subt_number, conf_str='', add_ctx=None):

        subt = TestRTYServerDolbilo(self,
                                    description='subtask %s %s' % (str(subt_number), self.Parameters.description))
        subt.Requirements.disk_space = self.Requirements.disk_space
        for i in self.Parameters.__custom_parameters_names__:
            try:
                attr = getattr(self.Parameters, i)
                setattr(subt.Parameters, i, attr)
                logging.debug('Successful added \'{}\' to subtask, with attr \'{}\''.format(i, attr))
            except Exception as e:
                logging.debug('Cannot get attr {}'.format(i))
                logging.debug(e)
        if conf_str:
            subt.Parameters.rtyserver_other_parameter = conf_str
        subt.Parameters.run_n_dolbs = 1
        if add_ctx and 'parser_rules' in add_ctx:
            subt.Parameters.parser_rules = add_ctx['parser_rules']
        subt.save().enqueue()
        return subt
        #  priority=self.ctx.get('child_tasks_prio', 'BACKGROUND_NORMAL').split('_')

    def choose_best_sub(self):
        subt = self.find(TestRTYServerDolbilo, status=ctt.Status.Group.FINISH).limit(30)
        self.Context.best_rps = max(
            [
                float(sub.Context.best_rps)
                for sub in subt if sub.status != ctt.Status.FAILURE
            ] + [float(self.Context.best_rps)]
        )
        self.set_info('<font color="green">best_rps: ' + str(self.Context.best_rps) + '</font>', do_escape=False)

        self.Context.dolbilo_result['results_rps'] = ', '.join(
            [
                str(sub.Context.dolbilo_result.get('result_rps', '0'))
                for sub in subt if sub.status != ctt.Status.FAILURE
            ] + [str(self.Context.dolbilo_result.get('result_rps', '0'))]
        )

        self.Context.dolbilo_result['results_errors'] = ', '.join(
            [str(sub.Context.dolbilo_result.get('result_errors', '0')) for sub in subt] +
            [str(self.Context.dolbilo_result.get('result_errors', '0'))]
        )

        self.Context.dolbilo_result['dolbilo_errors'] = ', '.join(
            [str(sub.Context.dolbilo_result.get('dolbilo_errors', '0')) for sub in subt] +
            [str(self.Context.dolbilo_result.get('dolbilo_errors', '0'))]
        )

        self.Context.dolbilo_result['results_empty'] = ', '.join(
            [str(sub.Context.dolbilo_result.get('result_empty', '0')) for sub in subt] +
            [str(self.Context.dolbilo_result.get('result_empty', '0'))]
        )

        self.Context.dolbilo_result['results_empty_perc'] = ', '.join(
            [str(sub.Context.dolbilo_result.get('result_empty_perc', '0')) for sub in subt] +
            [str(self.Context.dolbilo_result.get('result_empty_perc', '0'))]
        )

        self.Context.dolbilo_result['dolbilos_errors_perc'] = ', '.join(
            [str(sub.Context.dolbilo_result.get('dolbilo_errors_perc', '0')) for sub in subt] +
            [str(self.Context.dolbilo_result.get('dolbilo_errors_perc', '0'))]
        )

        try:
            self.Context.max_errors = max(
                [
                    float(sub.Context.max_errors)
                    for sub in subt if str(sub.Context.max_errors)
                ] + [
                    float(self.Context.max_errors)
                ]
            )
        except:
            pass

        try:
            self.Context.max_result_empty = max(
                [
                    float(sub.Context.max_result_empty)
                    for sub in subt if str(sub.Context.max_result_empty)
                ] + [
                    float(self.Context.max_result_empty)
                ]
            )
        except:
            pass

        try:
            self.Context.max_result_empty_perc = max(
                [
                    float(sub.Context.max_result_empty_perc)
                    for sub in subt if str(sub.Context.max_result_empty_perc)
                ] + [
                    float(self.Context.max_result_empty_perc)
                ]
            )
        except:
            pass

        try:
            self.Context.max_dolbilo_errors_perc = max(
                [
                    float(sub.Context.max_dolbilo_errors_perc)
                    for sub in subt if str(sub.Context.max_dolbilo_errors_perc)
                ] + [
                    float(self.Context.max_dolbilo_errors_perc)
                ]
            )
        except:
            pass

        try:
            self.Context.max_memory_gb = max(
                [float(sub.Context.max_memory_gb) for sub in subt] +
                [float(self.Context.max_memory_gb)]
            )

            self.Context.max_cpu_perc = max(
                [float(sub.Context.max_cpu_perc) for sub in subt] +
                [float(self.Context.max_cpu_perc)]
            )
        except:
            pass

        if float(self.Context.best_rps) < 1 and not self.Parameters.skip_check_rps:
            raise SandboxTaskFailureError('Resulting rps is zero. Something is wrong with task')
        max_acc_err = self.Parameters.acceptable_errors_perc or 1
        if float(self.Context.max_dolbilo_errors_perc) > max_acc_err:
            raise SandboxTaskFailureError('Too many errors (> {0}%)'.format(max_acc_err))

    def get_subtasks_fields(self):
        subt = self.find(TestRTYServerDolbilo, status=ctt.Status.Group.FINISH).limit(30)
        values = {}
        dig_values = {}
        for sub in subt:
            dolb_data = sub.Context.dolbilo_result
            for ctf in dolb_data:
                if ctf.startswith('to_parent_'):
                    values[ctf.replace('to_parent_', 'sub_')] = dolb_data[ctf]
                    try:
                        value = float(ctf.split('_')[-1])
                        descr = '_'.join(ctf.split('_')[2:-1])  # to_parent_..._10
                        if descr not in dig_values:
                            dig_values[descr] = []
                        dig_values[descr].append([value, float(dolb_data[ctf])])
                    except:
                        pass
        for desc in dig_values:
            cur_values = sorted(dig_values[desc], key=lambda x: x[0])
            self.Context.plots_values.append({'name': desc, 'data': cur_values})
            if 'response_time' in desc:
                self.Context.plots_values[-1]['y'] = 'microsec'
            elif 'result_rps' in desc:
                self.Context.plots_values[-1]['y'] = 'rps'
            if (
                'n_emuls' in self.Parameters.rtyserver_other_parameter and
                ('response_time' in desc or 'result_rps' in desc)
            ):
                self.Context.plots_values[-1]['x'] = 'backends_number'
        self.Context.dolbilo_result.update(values)

    def on_finish(self, prev_status, status):
        TestRTYServerUnit.on_finish(self, prev_status, status)
        self.Context.plots_data = json.dumps(self.Context.plots_values or [])

    def on_success(self, prev_status):
        TestRTYServerUnit.on_success(self, prev_status)
        for resource in sdk2.Resource['TASK_LOGS'].find(task=self).limit(10):
            try:
                if resource.size > 2000000:
                    channel.sandbox.set_resource_attribute(resource, 'ttl', 7)
            except Exception as e:
                self.set_info('%s' % e)
