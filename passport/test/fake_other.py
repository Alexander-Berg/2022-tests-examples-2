# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import (
    Mock,
    patch,
)
from passport.backend.social.common.random import (
    get_randomizer,
    urandom,
)
from passport.backend.social.common.task import TaskId
from passport.backend.social.common.test.consts import (
    APPLICATION_NAME1,
    REQUEST_ID1,
    TASK_ID1,
)


class BaseFakeFunction(object):
    PATH = None
    DEFAULT_VALUE = None

    def __init__(self):
        name = self.PATH.rsplit('.', 1)[1]
        self._mock = Mock(name=name, return_value=self.DEFAULT_VALUE)
        self._patch = patch(self.PATH, self._mock)

    def start(self):
        self._patch.start()
        return self

    def stop(self):
        self._patch.stop()

    def set_retval(self, value):
        self._mock.return_value = value


class FakeGenerateTaskId(BaseFakeFunction):
    PATH = 'passport.backend.social.common.task._generate_task_id'
    DEFAULT_VALUE = TASK_ID1

    @staticmethod
    def build_fake_task_id(environment_id=0):
        return TaskId(_bytes=urandom(get_randomizer(), 16), environment_id=environment_id).hex


class FakeBuildRequestId(BaseFakeFunction):
    PATH = 'passport.backend.social.common.web_service.build_request_id'
    DEFAULT_VALUE = REQUEST_ID1


class FakeBuildApplicationName(BaseFakeFunction):
    PATH = 'passport.backend.social.common.application._build_application_name'
    DEFAULT_VALUE = APPLICATION_NAME1
