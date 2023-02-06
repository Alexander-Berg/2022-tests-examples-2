# coding=utf-8
from sandbox.projects.metrika.utils.pipeline.contextable import Contextable


class ClusterConglomerate(Contextable):
    def __init__(self, storage=None):
        super(ClusterConglomerate, self).__init__(storage)

    @property
    def cluster_name(self):
        return self._default_getter()

    @cluster_name.setter
    def cluster_name(self, value):
        self._default_setter(value)

    @property
    def canonical_cluster_name(self):
        return self.cluster_name[5:]

    @property
    def old_cluster_id(self):
        return self._default_getter()

    @old_cluster_id.setter
    def old_cluster_id(self, value):
        self._default_setter(value)

    @property
    def data_resource_id(self):
        return self._default_getter()

    @data_resource_id.setter
    def data_resource_id(self, value):
        self._default_setter(value)

    @property
    def haproxy(self):
        return self._default_getter()

    @haproxy.setter
    def haproxy(self, value):
        self._default_setter(value)

    @property
    def restore_operation_id(self):
        return self._default_getter()

    @restore_operation_id.setter
    def restore_operation_id(self, value):
        self._default_setter(value)

    @property
    def new_cluster_id(self):
        return self._default_getter()

    @new_cluster_id.setter
    def new_cluster_id(self, value):
        self._default_setter(value)


class State(Contextable):
    def __init__(self, storage=None):
        super(State, self).__init__(storage)
        if storage is None:
            self._cluster_conglomerates = []

    @property
    def config(self):
        return self._default_getter()

    @config.setter
    def config(self, value):
        self._default_setter(value)

    @property
    def _cluster_conglomerates(self):
        return self._default_getter()

    @_cluster_conglomerates.setter
    def _cluster_conglomerates(self, value):
        self._default_setter(value)

    @property
    def cluster_conglomerates(self):
        return [ClusterConglomerate(state) for state in self._cluster_conglomerates]

    def add_cluster_conglomerate(self, value):
        self._cluster_conglomerates.append(value.state)

    @property
    def actual_mdb_clusters(self):
        return self._default_getter()

    @actual_mdb_clusters.setter
    def actual_mdb_clusters(self, value):
        self._default_setter(value)
