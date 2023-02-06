# -*- coding: utf-8 -*-

class Singleton:
    # On @ decoration
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    # On instance creation
    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = self.klass(*args, **kwargs)
        return self.instance


@Singleton
class PytestConfig():
    def __init__(self, config):
        self._config = config

    @property
    def config(self):
        return self._config
