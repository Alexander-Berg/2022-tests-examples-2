# coding=utf-8

from sandbox.projects.metrika.utils.pipeline.contextable import Contextable


class DeployTestStand(Contextable):

    @property
    def name(self):
        return self._default_getter()

    @name.setter
    def name(self, value):
        self._default_setter(value)

    def with_name(self, value):
        return self._default_fluent_setter(value)

    @property
    def daemon_name(self):
        return self._default_getter()

    @daemon_name.setter
    def daemon_name(self, value):
        self._default_setter(value)

    def with_daemon_name(self, value):
        return self._default_fluent_setter(value)

    @property
    def version(self):
        return self._default_getter()

    @version.setter
    def version(self, value):
        self._default_setter(value)

    def with_version(self, value):
        return self._default_fluent_setter(value)

    @property
    def bishop_environment_prefix(self):
        return self._default_getter()

    @bishop_environment_prefix.setter
    def bishop_environment_prefix(self, value):
        self._default_setter(value)

    def with_bishop_environment_prefix(self, value):
        return self._default_fluent_setter(value)

    @property
    def maas_parent(self):
        return self._default_getter()

    @maas_parent.setter
    def maas_parent(self, value):
        self._default_setter(value)

    def with_maas_parent(self, value):
        return self._default_fluent_setter(value)

    @property
    def fqdn(self):
        return self._default_getter()

    @fqdn.setter
    def fqdn(self, value):
        self._default_setter(value)

    def with_fqdn(self, value):
        return self._default_fluent_setter(value)
