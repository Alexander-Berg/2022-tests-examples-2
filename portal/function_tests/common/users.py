# -*- coding: utf-8 -*-
import logging
from datetime import timedelta
from time import sleep

from common import geobase
from common.geobase import Regions
from common.mongo import qamongo

_ACC_DELAY = 5
_ACC_TIMEOUT = 30
_RELEASE_TIMEOUT = 1200

_USERS = qamongo().users
logger = logging.getLogger(__name__)

DEFAULT = 'default'
WIDGET = 'widget'
LONG = 'long'
NO_MAIL = 'no_mail'
MAIL_0 = 'mail_0'
MAIL_1 = 'mail_1'
MAIL_2 = 'mail_2'
MAIL_5 = 'mail_5'


class UserNotFoundException(Exception):
    def __init__(self, *args):
        super(UserNotFoundException, self).__init__(*args)


class User(object):
    def __init__(self, *args):
        self.tags = args

    def __repr__(self):
        return 'User: {}'.format(self.tags)

    def __enter__(self):
        self._get_user()
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._release_user()

    def _get_user(self):
        logger.debug('Getting user with tags: {}'.format(self.tags))
        now = geobase.get_time(Regions.MOSCOW)
        time_end = now + timedelta(seconds=_ACC_TIMEOUT)

        while now < time_end:
            user = self._try_get_user(now)
            if user:
                self.data = user
                logger.debug('Got user: {}'.format(user.get('login')))
                return
            sleep(_ACC_DELAY)
            now = geobase.get_time(Regions.MOSCOW)

        raise UserNotFoundException('Failed to get user with tags {}'.format(self.tags))

    def _try_get_user(self, now):
        last_used = now - timedelta(seconds=_RELEASE_TIMEOUT)

        query = {
            '$or': [
                {'lastUsed': None},
                {'lastUsed': {'$lt': last_used}}
            ]
        }

        if self.tags:
            query['tags'] = {'$all': self.tags}

        update = {'$set': {'lastUsed': now}}

        return _USERS.find_one_and_update(query, update)

    def _release_user(self):
        if not self.data and not self.data.get('_id'):
            return

        logger.debug('Releasing user: {}'.format(self.data.get('login')))
        update = {'$unset': {'lastUsed': ''}}

        _USERS.find_one_and_update({'_id': self.data['_id']}, update)
