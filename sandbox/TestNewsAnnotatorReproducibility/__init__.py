# -*- coding: utf-8 -*-


from sandbox.common.errors import TaskFailure, TaskError

from sandbox import sdk2

import sandbox.common.types.client as ctc
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt

from sandbox.projects.common import utils2
from sandbox.projects.news import resources

from sandbox.projects.news.GetNewsAnnotatorResponses import GetNewsAnnotatorResponses
from sandbox.projects.news.CompareNewsAnnotatorResponses import CompareNewsAnnotatorResponses, NEWS_ANNOTATOR_RESPONSES_COMPARE_RESULT

import logging


class TestNewsAnnotatorReproducibility(sdk2.Task):
    '''
        Запускает идентичный аннотатор несколько раз и сравнивает результаты между собой
    '''

    class Parameters(GetNewsAnnotatorResponses.Parameters):
        with sdk2.parameters.Group("test parameters") as test_parameters:
            subtasks_to_test = sdk2.parameters.Integer('subtasks to test', default=2)

    class Requirements(sdk2.Task.Requirements):
        client_tags = ctc.Tag.Group.LINUX
        disk_space = 5 * 1024
        ram = 1 * 1024
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    def on_enqueue(self):
        if self.Parameters.subtasks_to_test < 2:
            raise TaskError("Not enougth resources to compare: {}. Need at least 2.".format(self.Parameters.subtasks_to_test))

        if self.Context.out_resource_ids is ctm.NotExists:
            sub_res = []
            for idx in xrange(self.Parameters.subtasks_to_test):
                sub_res.append(resources.NEWS_NEWS_DOC_INFO_DUMP(self, "annotator responses", "info_{}.yson".format(idx)))
            self.Context.out_resource_ids = [r.id for r in sub_res]

    def on_execute(self):
        with self.memoize_stage.enqueue_get_subtasks(commit_on_entrance=False):
            get_sub_tasks, _ = self._enqueue_sub_tasks()
            raise sdk2.WaitTask(get_sub_tasks, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=True)

        with self.memoize_stage.check_get_subtasks(commit_on_entrance=False):
            #  Если get-задача завершилась ошибкой, то compare-задача может ожидать ресурса бесконечно,
            #  так как владельцем ресурса является не get-задача и он не переходит автоматически в статус
            #  broken. Поэтому явно проверяем сначала все get-задачи, а лишь потом ожидаем compare-задачи.
            get_sub_tasks = self._tasks_from_id_list(self.Context.get_task_ids)
            for get_sub_task in get_sub_tasks:
                if get_sub_task.status != ctt.Status.SUCCESS:
                    raise TaskFailure("Subtask {} failed".format(get_sub_task.id))

            compare_sub_tasks = self._tasks_from_id_list(self.Context.compare_task_ids)
            raise sdk2.WaitTask(compare_sub_tasks, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=True)

        has_diff = self._analyse_comparison_result()
        if has_diff:
            raise TaskFailure("Output is unstable")

    def _enqueue_get_sub_tasks(self):
        repeats = self.Parameters.subtasks_to_test
        get_sub_tasks = []
        for i in xrange(repeats):
            sub_parameters = dict(self.Parameters)
            sub_parameters["description"] = "Run {}/{}; {}".format(i, repeats, self.Parameters.description)
            sub_parameters["out_responses_parent_resource"] = sdk2.Resource[self.Context.out_resource_ids[i]]
            sub_task = GetNewsAnnotatorResponses(self, **sub_parameters)
            sub_task.enqueue()
            get_sub_tasks.append(sub_task)
        self.Context.get_task_ids = self._id_list_from_tasks(get_sub_tasks)
        return get_sub_tasks

    def _enqueue_compare_sub_tasks(self):
        dump_resources = [sdk2.Resource[resource_id] for resource_id in self.Context.out_resource_ids]

        compare_sub_tasks = []
        for responses1idx, responses2idx in self._generate_comparison_pairs(len(dump_resources)):
            responses1res = dump_resources[responses1idx]
            responses2res = dump_resources[responses2idx]
            compare_sub_task = CompareNewsAnnotatorResponses(
                self,
                responses1=responses1res,
                responses2=responses2res,
                description="Compare iteration {} vs {}; {}".format(responses1idx, responses2idx, self.Parameters.description),
                owner=self.Parameters.owner,
                priority=self.Parameters.priority,
            )
            compare_sub_task.enqueue()
            compare_sub_tasks.append(compare_sub_task)
        self.Context.compare_task_ids = self._id_list_from_tasks(compare_sub_tasks)
        return compare_sub_tasks

    def _enqueue_sub_tasks(self):
        get_sub_tasks = self._enqueue_get_sub_tasks()
        compare_sub_tasks = self._enqueue_compare_sub_tasks()
        return get_sub_tasks, compare_sub_tasks

    def _analyse_comparison_result(self):
        has_diff = False
        comparison_result_links = []
        for compare_sub_task_id in self.Context.compare_task_ids:
            compare_sub_task = sdk2.Task[compare_sub_task_id]
            if compare_sub_task.status != ctt.Status.SUCCESS:
                raise TaskFailure("Comparison task {} failed".format(compare_sub_task_id))
            compare_has_diff = compare_sub_task.Context.has_diff
            logging.info("Task {} {} diff".format(compare_sub_task_id, ("has" if compare_has_diff else "has no")))
            resource = NEWS_ANNOTATOR_RESPONSES_COMPARE_RESULT.find(task=compare_sub_task).first()
            if resource:
                comparison_result_link = utils2.resource_redirect_link(
                    resource.id,
                    title="Comparison results {} ({})".format(
                        compare_sub_task_id, "diff" if compare_has_diff else "no diff"
                    )
                )
                comparison_result_links.append(comparison_result_link)
            has_diff = has_diff or compare_has_diff

        html_summary_lines = [
            "Output is {}".format("unstable" if has_diff else "stable"),
        ] + comparison_result_links
        self.set_info("<br>".join(html_summary_lines), do_escape=False)
        self.Context.has_diff = has_diff
        return has_diff

    @staticmethod
    def _generate_comparison_pairs(num):
        """
        >>> _generate_comparison_pairs(4)
        [(0, 1), (1, 2), (2, 3), (3, 0)]
        """
        r = range(num)
        pairs = zip(r, r[1:])
        if num > 2:
            pairs.append((num - 1, 0))
        return pairs

    def _tasks_from_id_list(self, id_list):
        return [sdk2.Task[nn] for nn in id_list]

    def _id_list_from_tasks(self, tasks):
        return [task.id for task in tasks]
