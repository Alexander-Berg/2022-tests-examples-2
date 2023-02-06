# -*- coding: utf-8 -*-

import __builtin__
import tempfile

import mock


class OpenMock(object):
    """
    Мок, подменяющий файл при открытии через open. Реального обращения к файлу не происходит
    """
    def __init__(self, files_content):
        self._original_open = open

        def side_effect(key, mode='r'):
            if key in files_content:
                tp = tempfile.NamedTemporaryFile()
                tp.write(files_content[key])
                tp.flush()
                return file(tp.name, mode)
            else:
                return self._original_open(key, mode)

        self.mock = mock.patch.object(__builtin__, 'open', side_effect=side_effect)

    def start(self):
        self.mock.start()

    def stop(self):
        self.mock.stop()
