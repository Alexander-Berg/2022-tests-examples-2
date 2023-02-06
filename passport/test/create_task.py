# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from passport.backend.social.broker.handlers.base import InternalBrokerHandlerV2
from passport.backend.social.common import validators
from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import build_scope_string
from passport.backend.social.common.redis_client import (
    get_redis,
    RedisError,
)
from passport.backend.social.common.task import (
    build_provider_for_task,
    create_task,
    save_task_to_redis,
)
from passport.backend.social.common.web_service import DatabaseFailedWebServiceError
from passport.backend.utils.time import datetime_to_integer_unixtime_nullable


logger = logging.getLogger(__name__)


class _TestCreateTaskForm(validators.Schema):
    application_name = validators.ApplicationName()
    token_value = validators.Token()
    token_expired = validators.Unixtime()
    token_scope = validators.Scope()
    refresh_token_value = validators.Token(not_empty=False, if_empty=None, if_missing=None)
    profile_userid = validators.Userid()
    profile_username = validators.Username(not_empty=False, if_empty=None, if_missing=None)
    profile_email = validators.Email(not_empty=False, if_empty=None, if_missing=None)


class TestCreateTaskHandler(InternalBrokerHandlerV2):
    required_grants = ['test_create_task']
    basic_form = _TestCreateTaskForm

    def __init__(self, request):
        super(TestCreateTaskHandler, self).__init__(request)
        self._redis_client = get_redis()

    def _save_task_to_redis(self, task):
        try:
            save_task_to_redis(self._redis_client, task.task_id, task)
        except RedisError:
            logger.error('Unable to write task data to Redis')
            raise DatabaseFailedWebServiceError()

    def _process_request(self):
        app = self._get_application_from_name(self.form_values['application_name'])

        task = create_task()
        task.finished = now.f()
        task.consumer = self._consumer
        task.application = app
        task.provider = build_provider_for_task(
            code=app.provider['code'],
            name=app.provider['name'],
            id=app.provider['id'],
        )

        task.profile['userid'] = self.form_values['profile_userid']
        task.profile['username'] = self.form_values['profile_username']
        task.profile['email'] = self.form_values['profile_email']

        task.access_token = {
            'value': self.form_values['token_value'],
            'secret': None,
            'scope': build_scope_string(self.form_values['token_scope']),
            'expires': datetime_to_integer_unixtime_nullable(self.form_values['token_expired']),
            'refresh': self.form_values['refresh_token_value'],
        }

        self._save_task_to_redis(task)

        self.response_values['task_id'] = task.task_id
