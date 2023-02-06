# coding=utf-8
from sandbox.projects.metrika.utils.pipeline.contextable import Contextable


class State(Contextable):
    def __init__(self, storage=None):
        super(State, self).__init__(storage)

    @property
    def start_date(self):
        return self._default_getter()

    @start_date.setter
    def start_date(self, value):
        self._default_setter(value)

    @property
    def finish_date(self):
        return self._default_getter()

    @finish_date.setter
    def finish_date(self, value):
        self._default_setter(value)

    @property
    def b2b_tests_tasks(self):
        return self._default_getter()

    @b2b_tests_tasks.setter
    def b2b_tests_tasks(self, value):
        self._default_setter(value)

    @property
    def mobmetd_hostname_ref(self):
        return self._default_getter()

    @mobmetd_hostname_ref.setter
    def mobmetd_hostname_ref(self, value):
        self._default_setter(value)

    @property
    def mobmetd_hostname_test(self):
        return self._default_getter()

    @mobmetd_hostname_test.setter
    def mobmetd_hostname_test(self, value):
        self._default_setter(value)

    @property
    def faced_hostname_ref(self):
        return self._default_getter()

    @faced_hostname_ref.setter
    def faced_hostname_ref(self, value):
        self._default_setter(value)

    @property
    def faced_hostname_test(self):
        return self._default_getter()

    @faced_hostname_test.setter
    def faced_hostname_test(self, value):
        self._default_setter(value)
