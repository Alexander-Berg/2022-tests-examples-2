# coding=utf-8

from sandbox.projects.metrika.utils.pipeline.contextable import Contextable


class State(Contextable):

    def __init__(self, storage=None):
        super(State, self).__init__(storage)
        if storage is None:
            self.instance_ports = {}
            self.dates = {}
            self.datetimes = {}
            self.cluster_hosts = {}

    @property
    def caas_host(self):
        return self._default_getter()

    @caas_host.setter
    def caas_host(self, value):
        self._default_setter(value)

    @property
    def instance_id(self):
        return self._default_getter()

    @instance_id.setter
    def instance_id(self, value):
        self._default_setter(value)

    @property
    def instance_name(self):
        return self._default_getter()

    @instance_name.setter
    def instance_name(self, value):
        self._default_setter(value)

    @property
    def instance_uri(self):
        return self._default_getter()

    @instance_uri.setter
    def instance_uri(self, value):
        self._default_setter(value)

    @property
    def instance_ports(self):
        return self._default_getter()

    @instance_ports.setter
    def instance_ports(self, value):
        self._default_setter(value)

    @property
    def dates(self):
        return self._default_getter()

    @dates.setter
    def dates(self, value):
        self._default_setter(value)

    @property
    def datetimes(self):
        return self._default_getter()

    @datetimes.setter
    def datetimes(self, value):
        self._default_setter(value)

    @property
    def cluster_hosts(self):
        return self._default_getter()

    @cluster_hosts.setter
    def cluster_hosts(self, value):
        self._default_setter(value)
