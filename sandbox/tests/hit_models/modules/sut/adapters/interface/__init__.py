from abc import ABCMeta, abstractmethod


class HitModelsSUTAdapterInterface(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_work_dir(self):
        pass

    @abstractmethod
    def get_hit_models_binary_path(self):
        pass

    @abstractmethod
    def get_hit_models_layer_path(self):
        pass

    @abstractmethod
    def get_hit_models_archive_models_path(self):
        pass
