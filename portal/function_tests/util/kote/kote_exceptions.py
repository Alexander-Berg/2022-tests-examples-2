# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)


class CheckException(Exception):
    def __str__(self):
        (prev_exception, test_path, message) = self.args
        text = ['check_exception']
        if prev_exception:
            text.append('{}'.format(prev_exception))
        if test_path:
            text.append('Failed on test {}'.format(test_path))

        return '\n'.join(text)


class MissedException(Exception):
    def __str__(self):
        return 'Missed exception: {}'.format(self.args[0])


class PathNotFound(Exception):
    def __str__(self):
        return 'Path: {} not found'.format(self.args[0])


class BadType(Exception):
    def __str__(self):
        return 'BadType: {}'.format(self.args[0])


class BadYamlFormat(Exception):
    def __str__(self):
        (prev_exception, message) = self.args
        return 'BadYamlFormat: {}\n{}'.format(message, prev_exception)


class BadClient(Exception):
    def __str__(self):
        (prev_exception, test_path, message) = self.args
        text = ['Bad client: {}'.format(message)]
        if prev_exception:
            text.append('{}'.format(prev_exception))
        if test_path:
            text.append('Failed on test {}'.format(test_path))

        return '\n'.join(text)
