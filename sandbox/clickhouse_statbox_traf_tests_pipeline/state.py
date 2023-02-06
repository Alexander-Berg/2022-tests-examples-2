# coding=utf-8

from sandbox.projects.metrika.utils.pipeline.contextable import Contextable


class State(Contextable):
    def __init__(self, storage=None):
        super(State, self).__init__(storage)

    @property
    def caas_id_ref(self):
        return self._default_getter()

    @caas_id_ref.setter
    def caas_id_ref(self, value):
        self._default_setter(value)

    @property
    def caas_id_test(self):
        return self._default_getter()

    @caas_id_test.setter
    def caas_id_test(self, value):
        self._default_setter(value)

    @property
    def start_date(self):
        return self._default_getter()

    @start_date.setter
    def start_date(self, value):
        self._default_setter(value)

    @property
    def queries_task_id(self):
        return self._default_getter()

    @queries_task_id.setter
    def queries_task_id(self, value):
        self._default_setter(value)

    @property
    def queries_resource_id(self):
        return self._default_getter()

    @queries_resource_id.setter
    def queries_resource_id(self, value):
        self._default_setter(value)

    @property
    def b2b_tests_task_id(self):
        return self._default_getter()

    @b2b_tests_task_id.setter
    def b2b_tests_task_id(self, value):
        self._default_setter(value)
