# coding: utf-8

import logging
from sandbox import sdk2
import sandbox.common.types.task as ctt

from sandbox.projects.partner.tasks.e2e_tests.e2e_all_tests.test_manager import TestManager
from sandbox.projects.partner.tasks.e2e_tests.e2e_all_tests.graph import Graph

AWAIT_START_TRACK = 'await_start'


class AutotestsTasks:
    root = 'root'
    ba = 'build_adfox'
    bb = 'build_backend'
    bf = 'build_frontend'
    bj = 'build_java'
    tp = 'test_pi'
    ta = 'test_adfox'


# Подробнее алгоритм исполнения задачи описан здесь: https://wiki.yandex-team.ru/users/sikalov/rootautoteststask/
class PartnerE2ERunAll(TestManager):
    """
    Root task to run Adfox and PI autotests.
    """
    name = 'PARTNER_E2E_RUN_ALL'

    class Context(TestManager.Context):
        pass

    class Parameters(TestManager.Parameters):
        kill_timeout = 600
        with sdk2.parameters.Group('General parameters') as test_params:
            should_test_pi = sdk2.parameters.Bool(
                'Test PI',
                description='Run PI tests',
                default=True
            )

            should_test_adfox = sdk2.parameters.Bool(
                'Test Adfox',
                description='Run Adfox tests',
                default=True
            )

            should_build_pi = sdk2.parameters.Bool(
                'Build and deploy PI',
                default=True
            )

            should_build_adfox = sdk2.parameters.Bool(
                'Build and deploy Adfox',
                default=True
            )

    def on_create(self):
        self.track_start(AWAIT_START_TRACK)

    def on_prepare(self):
        super(PartnerE2ERunAll, self).on_prepare()
        with self.memoize_stage.task_await_start:
            self.track_finish(AWAIT_START_TRACK)

    def on_enqueue(self):
        super(PartnerE2ERunAll, self).on_enqueue()
        self.Parameters.description += "\nЧастичный запуск - для поиска отчетов"
        " по пропущенным тестам будет просматриваться цепочка клонирования"
        "\nОчистка тестранов не производится - может получиться небольшой рассинхрон"

    def on_execute(self):
        super(PartnerE2ERunAll, self).on_execute()

        with self.memoize_stage.enter:
            logging.debug('on_execute enter')
            self.send_message_with_task_url('Запуск автотестов', self.id)

        # step 1: Формируем граф задач
        self.build_graph()

        # step 2: Из контекста задачи получаем wait_tasks и текущее состояние графа
        self.graph = Graph(self.Context.graph)
        self.wait_tasks = self.Context.wait_tasks

        # step 3: Обходим граф
        self.traverse_graph()

        # step 4: Обновляем контекст выполнения
        self.Context.wait_tasks = self.wait_tasks
        self.Context.graph = self.graph.serialize()
        self.Context.save()

        # step 5: Если в массиве wait_tasks остались какие-то задачи, которые ждут своего исполнения ->
        # ждем пока выполнится хотя бы одна из них
        # Иначе проверяем есть ли в нашем графе красные вершины, если есть то завршаем все рутовую задачу неуспехом
        if len(self.wait_tasks) > 0:
            logging.debug('on_execute wait_tasks')

            raise sdk2.WaitTask(
                self.wait_tasks,
                [ctt.Status.Group.FINISH, ctt.Status.Group.BREAK],
                wait_all=False
            )
        else:
            if self.Context.has_red_vertices:
                raise Exception('Some dependencies were failed')

    def build_graph(self):
        with self.memoize_stage.build_graph:
            logging.debug('build_graph')

            # строим граф
            graph = Graph()
            graph.add_vertex(
                AutotestsTasks.root,
                [
                    AutotestsTasks.ba,
                    AutotestsTasks.tp,
                    AutotestsTasks.bb,
                    AutotestsTasks.bf,
                    AutotestsTasks.bj
                ]
            )
            graph.add_vertex(AutotestsTasks.bb, [])
            graph.add_vertex(AutotestsTasks.bf, [])
            graph.add_vertex(AutotestsTasks.bj, [])
            graph.add_vertex(AutotestsTasks.ba, [AutotestsTasks.ta])

            graph.add_vertex(AutotestsTasks.tp, [])
            graph.add_vertex(AutotestsTasks.ta, [])

            self.Context.graph = graph.serialize()
            self.Context.has_red_vertices = False
            self.Context.wait_tasks = []
            self.Context.save()

    def traverse_graph(self):
        logging.debug('traverse_graph')

        # выполняем топологическую сортировку графа
        queue = self.graph.top_sort(AutotestsTasks.root)
        for vertex_name in queue:
            logging.debug('traverse_graph with vertex {}'.format(vertex_name))
            vertex = self.graph.get_vertex(vertex_name)
            if vertex.color == Graph.VertexColor.white:
                # проверяем, что все зависимости зеленые
                if self.is_vertex_ready_to_exec(vertex_name):
                    self.exec_vertex_method(vertex_name)
            elif vertex.color == Graph.VertexColor.grey:
                # обновляем цвет вершины
                self.update_vertex(vertex)

    def update_vertex(self, vertex):
        vertex_name = vertex.name
        logging.debug('update_vertex {}'.format(vertex_name))
        vertex = self.graph.get_vertex(vertex_name)
        # обновляем цвет вершины в зависимости от статуса запущенной задачи
        task_ids = vertex.task_ids
        has_failed = False
        has_not_success = False

        tasks = []

        for task_id in task_ids:
            task = self.find(id=task_id).first()
            tasks.append(task)
            if task.status == ctt.Status.SUCCESS:
                # удаляем из wait_tasks задачу, которая была в ожидании
                if task_id in self.wait_tasks:
                    self.wait_tasks.remove(task_id)
                # делаем постобработку задачи
            elif not task or self._is_task_failed(task):
                has_failed = True
                self.wait_tasks.remove(task.id)
            else:
                has_not_success = True

        if has_failed:
            vertex.color = Graph.VertexColor.red
            # статус выполнения задачи не успешный -> красим вершину в красный цвет
            self.post_exec_failure_vertex_method(vertex_name, tasks)
            self.Context.has_red_vertices = True
            self.Context.save()
        elif not has_not_success:
            # статус выполнения задачи успешный -> красим вершину в зеленую
            vertex.color = Graph.VertexColor.green
            self.post_exec_success_vertex_method(vertex_name, tasks)

    def is_vertex_ready_to_exec(self, vertex_name):
        logging.debug('is_vertex_ready_to_exec vertex={}'.format(vertex_name))

        vertex = self.graph.get_vertex(vertex_name)
        logging.debug('is_vertex_ready_to_exec vertex={},{},#{}'.format(
            vertex_name,
            vertex.color,
            vertex.task_ids
        ))

        for dep_name in vertex.depends:
            dependency_vertex = self.graph.get_vertex(dep_name)
            logging.debug('is_vertex_ready_to_exec vertex={}: dependency_vertex={},{},#{}'.format(
                vertex_name,
                dep_name,
                dependency_vertex.color,
                dependency_vertex.task_ids
            ))
            if dependency_vertex.color == Graph.VertexColor.red and dependency_vertex.allow_failure:
                continue

            if dependency_vertex.color != Graph.VertexColor.green:
                logging.debug('is_vertex_ready_to_exec vertex={}: not ready'.format(vertex_name))
                return False
        logging.debug('is_vertex_ready_to_exec vertex={}: ready'.format(vertex_name))
        return True

    def exec_vertex_method(self, vertex):
        logging.debug('exec_vertex_method "{}"'.format(vertex))

        should_build_pi = self.Parameters.should_build_pi
        should_build_adfox = self.Parameters.should_build_adfox
        should_test_pi = self.Parameters.should_test_pi
        should_test_adfox = self.Parameters.should_test_adfox

        tasks = []
        task = None

        try:
            if vertex == AutotestsTasks.bb:
                if should_build_pi:
                    task = self.build_backend()
                if task:
                    tasks.append(task)
            elif vertex == AutotestsTasks.bf:
                if should_build_pi:
                    task = self.build_frontend()
                if task:
                    tasks.append(task)
            elif vertex == AutotestsTasks.bj:
                if should_build_pi:
                    task = self.build_java()
                if task:
                    tasks.append(task)
            elif vertex == AutotestsTasks.tp:
                if should_test_pi:
                    task = self.run_pi_tests()
                else:
                    logging.debug('Skipping PI tests')
                if task:
                    tasks.append(task)
            elif vertex == AutotestsTasks.ta:
                if should_test_adfox:
                    task = self.run_adfox_tests()
                    self.send_message('Автотесты Adfox запущены')
                else:
                    logging.debug('Skipping Adfox tests')
                if task:
                    tasks.append(task)
            elif vertex == AutotestsTasks.ba:
                if should_build_adfox:
                    task = self.build_adfox_stand()
                if task:
                    tasks.append(task)

            if len(tasks):
                for task in tasks:
                    logging.debug('exec_vertex_method "{}" wait_task #{}'.format(vertex, task.id))
                    self.wait_tasks.append(task.id)
                self.graph.get_vertex(vertex).task_ids = [task.id for task in tasks]
                self.graph.get_vertex(vertex).color = Graph.VertexColor.grey
            else:
                logging.debug('exec_vertex_method "{}" task instantly finished'.format(vertex))
                self.graph.get_vertex(vertex).color = Graph.VertexColor.green
        except Exception as err:
            logging.error('exec_vertex_method "{}" task failed: {}'.format(vertex, str(err)))
            self.graph.get_vertex(vertex).color = Graph.VertexColor.red
            self.Context.has_red_vertices = True

    def post_exec_success_vertex_method(self, vertex, tasks):
        logging.debug('post_exec_success_vertex_method "{}" tasks {}'.format(
            vertex,
            ', '.join([str(task.id) for task in tasks]))
        )

        if vertex == AutotestsTasks.bb:
            self.post_build_backend(tasks[0])
        elif vertex == AutotestsTasks.bf:
            self.post_build_frontend(tasks[0])
        elif vertex == AutotestsTasks.bj:
            self.post_build_java(tasks[0])
            self.send_message('Тестовые стенды ПИ обновлены успешно')
        elif vertex == AutotestsTasks.ta:
            self.send_message('Автотесты Adfox прошли успешно')

    def post_exec_failure_vertex_method(self, vertex, tasks):
        logging.debug('post_exec_failure_vertex_method {} tasks {}'.format(vertex, ', '.join([str(task.id) for task in tasks])))

        failed_tasks = [task for task in tasks if self._is_task_failed(task)]
        if vertex == AutotestsTasks.ta:
            self.send_message_with_task_url('Тесты Adfox завершились неудачно', [task.id for task in failed_tasks])

    def _is_task_failed(self, task):
        return task.status in [
            ctt.Status.EXCEPTION,
            ctt.Status.STOPPED,
            ctt.Status.TIMEOUT,
            ctt.Status.EXPIRED,
            ctt.Status.NO_RES,
            ctt.Status.FAILURE
        ]

    @property
    def error_callback_title(self):
        return 'Неудачное выполнение автотестов ПИ и Adfox'

    def get_metrics_release_id(self):
        return '{}|{}|{}'.format(
            self.Parameters.adfox_branch,
            self.Parameters.partner_branch,
            self.Parameters.java_branch
        )

    @property
    def is_partial_run(self):
        return not (self.Parameters.should_test_pi and self.Parameters.should_test_adfox)
