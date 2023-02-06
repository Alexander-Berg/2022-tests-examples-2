# -*- coding: utf-8 -*-

import copy
from sandbox import common

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.parameters import SandboxIntegerParameter
from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import utils


class NumberOfRunsParameter(SandboxIntegerParameter):
    name = 'number_of_runs'
    description = 'How many tests to execute'
    default_value = 5


class BaseTestPerformanceBestTask(SandboxTask):
    """
        Базовый класс для параллельного запуска тестирования поисков с последующей агрегацией результатов.
        Дочерние классы должны запускать 'number_of_runs' подзадач заданного типа.

        Выбирается лучший обстрел.
    """

    type = 'TEST_PERFORMANCE_BEST'

    input_parameters = (
        NumberOfRunsParameter,
    )

    @property
    def footer(self):
        client = common.rest.Client()
        info = client.task.read(
            parent=self.id,
            fields='context.requests_per_sec,context.results',
            limit=utils.get_or_default(self.ctx, NumberOfRunsParameter),
            hidden=True,
        ).get('items')
        foot = []
        if info:
            foot.extend(self._get_rps_results(info))
            foot.extend(self._get_response_time_quantile_info(info))
        return foot

    def _get_rps_results(self, info):
        if not any(i.get("context.requests_per_sec") for i in info):
            return []
        rps_list = []
        round_to = 1
        max_rps = round(max(self.ctx.get("requests_per_sec", [0])), round_to)
        for child_info in info:
            req_per_sec = child_info.get("context.requests_per_sec") or [0] * self.ctx.get("dolbilka_executor_sessions", 1)
            req_per_sec = [round(i, round_to) for i in req_per_sec]
            max_rps_in_row = max(req_per_sec)
            colored = ' style="color:red"' if max_rps in req_per_sec else ""
            req_per_sec[req_per_sec.index(max_rps_in_row)] = "<b{}>{}</b>".format(colored, max_rps_in_row)
            rps_dict = dict(enumerate(req_per_sec))
            rps_dict['Task id'] = lb.task_link(child_info.get("id", "-"))
            rps_list.append(rps_dict)
        return [{
            'helperName': '',
            'content': rps_list
        }]

    def _get_response_time_quantile_info(self, info):
        # skip first shoot, it's irrelevant
        child_result = (self._skip_first_result(child.get("context.results")) for child in info if child.get("context.results"))
        total_avg = self._count_response_time_avg_quantile(child_result)
        return [{
            'helperName': '',
            'content': "<h4>Average Q95 response time: <strong>{}</strong> (usec)</h4>".format(total_avg)
        }] if total_avg else []

    @staticmethod
    def _count_response_time_avg_quantile(child_result):
        """SEARCH-1921"""
        avg_results = []
        for r in child_result:
            avg_results.append(utils.count_avg([shoot_result.get("latency_0.95", 0) for shoot_result in r]))
        total_avg = utils.count_avg(avg_results, precision=1)
        return total_avg

    def on_execute(self):
        number_of_runs = utils.get_or_default(self.ctx, NumberOfRunsParameter)
        subtasks = self.list_subtasks(load=True)
        if not subtasks:
            self.set_optional_input_params()
            for i in range(int(number_of_runs)):
                self._start_performance_subtask(i)
            utils.wait_all_subtasks_stop()
        elif utils.check_all_subtasks_done():
            # See https://ml.yandex-team.ru/thread/2370000002596347627/
            completed_count = len([subtask for subtask in subtasks if subtask.is_completed()])
            eh.verify(
                completed_count == number_of_runs,
                'Incorrect number of completed child tasks, {} != {}'.format(completed_count, number_of_runs)
            )
            utils.check_subtasks_fails()
        else:
            utils.restart_broken_subtasks()

        # even if children are not finished yet, we still can collect stats,
        # this also covers stupid race conditions like multiple DRAFTs of single run
        self._collect_reqs_stats(subtasks)

    def _start_performance_subtask(self, run_number):
        sub_ctx = copy.deepcopy(self.ctx)
        sub_ctx['notify_via'] = ''
        sub_ctx['notify_if_failed'] = self.owner
        subtasks_model = self.cpu_model_filter or self._get_default_cpu_model()
        subtasks_host = self.client_hostname_filter
        subtasks_execution_space = self._get_subtasks_execution_space()
        subtasks_priority = self._get_subtasks_priority()
        return self.create_subtask(
            task_type=self._get_performance_task_type(),
            input_parameters=sub_ctx,
            description="{} #{}".format(self.descr, run_number),
            model=subtasks_model,
            host=subtasks_host,
            execution_space=subtasks_execution_space,
            priority=subtasks_priority
        )

    def _collect_reqs_stats(self, subtasks):
        rps_2d = [s.ctx['requests_per_sec'] for s in subtasks if 'requests_per_sec' in s.ctx]
        self.ctx['requests_per_sec_2d'] = rps_2d
        self.ctx['requests_per_sec'] = sorted([max(rps) for rps in rps_2d], reverse=True)
        total_measurements = sum([len(rps) for rps in rps_2d])
        if not total_measurements:
            raise SandboxTaskFailureError('No measurements succeeded. Check the child tasks.')
        self.ctx['requests_avg_all'] = sum([sum(rps) for rps in rps_2d]) / total_measurements

        # new way to count rps:
        top_runs = 3 if len(rps_2d) > 3 else 1
        self.ctx['rps_by_shoots'] = [
            sum(sorted(r)[-top_runs:]) / top_runs
            for r in self._skip_first_result(zip(*rps_2d))
        ]

        rss_2d = [s.ctx['memory_rss'] for s in subtasks if 'memory_rss' in s.ctx]
        self.ctx['memory_rss_2d'] = rss_2d
        self.ctx['memory_rss'] = sorted([max(rss) for rss in rss_2d], reverse=True)

        child_result = (self._skip_first_result(s.ctx.get("results")) for s in subtasks if s.ctx.get("results"))
        self.ctx["average_q95_response_time"] = self._count_response_time_avg_quantile(child_result)

    @staticmethod
    def _skip_first_result(data):
        return data[1:] if len(data) > 1 else data

    def get_all_subtasks_data(self):
        """
            Получить список rps'ов  с подсвеченными максимумами
            Вызывается из view таска
            @return: список с результатами в виде кортежа (task_id, requests_per_sec)
                где task_id - идентификатор подзадачи, где был выполнен обстрел
                    requests_per_sec - список результатов с отмеченными максимумами

                Например:
                (2306716, [224.19499999999999, 1008.575, 975.18299999999999, 976.85000000000002,
                           1018.308, 1022.904, 995.58500000000004, 989.32000000000005,
                           "<b style='color: red'>1040.519</b>", 1028.828]),
                 2306714, [229.98400000000001, 986.17899999999997, 1025.5599999999999,
                           973.57899999999995, 922.52800000000002, 965.87699999999995,
                           '<b>1029.954</b>',
                           1026.046, 1017.337, 976.06700000000001],
                 ...)
        """
        res = []
        child_tasks = getattr(self, 'child_tasks', None)
        if child_tasks is not None:
            # оптимизация для случая когда view вызывается из родительского таска PRIEMKA_BASESEARCH_BINARY
            # в этом случае task имеет свойство child_tasks, заполненное в get_child_tree (yasandbox/manager.py)
            child_tasks = [task for id, task in child_tasks]
        else:
            child_tasks = self.list_subtasks(load=True, completed_only=True)

        for st in child_tasks:
            # упавшие таски пропускаем
            if not st.ctx.get('requests_per_sec'):
                continue
            requests_per_sec = st.ctx['requests_per_sec']

            res.append((st.id, requests_per_sec, requests_per_sec.index(max(requests_per_sec))))

        res = sorted(res, key=lambda x: x[1][x[2]], reverse=True)

        for i in xrange(len(res)):
            res[i][1][res[i][2]] = ("<b style='color: red'>%s</b>" if i == 0 else "<b>%s</b>") % res[i][1][res[i][2]]

        return [(task_id, _requests_per_sec) for task_id, _requests_per_sec, index_of_max_value in res]

    def get_short_task_result(self):
        if self.is_completed():
            requests_per_sec = self.ctx.get('requests_per_sec', None)
            if requests_per_sec:
                return str(max(requests_per_sec))
        return None

    def _get_default_cpu_model(self):
        return 'e5-2650'

    def set_optional_input_params(self):
        pass

    def _get_subtasks_execution_space(self):
        """
            Returns subtasks execution_space. Override this method to set execution_space explicitly.
        """
        return None

    def _get_subtasks_priority(self):
        """
            Returns subtasks priority. Override this method to set subtasks priority explicitly.
        """
        return self.priority

    def _get_performance_task_type(self):
        """
            Возвращается имя теста проверки производительности
        """

        raise NotImplementedError()
