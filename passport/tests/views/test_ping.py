# -*- coding: utf-8 -*-

from contextlib import nested
import json

import mock
import MySQLdb
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.utils import assert_errors
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views import ping
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.dbmanager.manager import get_dbm
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.useragent.sync import (
    RequestError,
    UserAgent,
)
from redis import RedisError
import sqlalchemy.exc


@with_settings_hosts(
    DB_CONFIG={'passportdbcentral': {}, 'passportdbshard1': {}},
    PING_FILE='ping.html',
    BLACKBOX_AVAILABILITY_TEST_UID=1,
    FRONTEND_HOST='frontend_url',
    FRONTEND_PING_TIMEOUT=1,
    PING_DB_NAMES=['passportdbcentral', 'passportdbshard1'],
)
class TestPing(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value({})
        self.patches = [
            mock.patch(
                'os.access',
                side_effect=lambda filepath, mode: filepath == 'ping.html',
            ),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        self.env.stop()
        for patch in reversed(self.patches):
            patch.stop()
            del patch
        del self.env

    def test_ok(self):
        rv = self.env.client.get('/ping')
        eq_(rv.status_code, 200)
        eq_(rv.data, 'Pong\n')

    def test_ok_all(self):
        self.env.blackbox.set_blackbox_response_value('userinfo',
                                                      blackbox_userinfo_response(uid=123))
        useragent_mock = mock.Mock()
        useragent_get_mock = mock.Mock()
        useragent_get_mock.content = 'Pong\n'
        useragent_mock.return_value = useragent_get_mock

        useragent_mock_post = mock.Mock()
        useragent_mock_post_result = mock.Mock()
        useragent_mock_post_result.content = '{"passport":[{"BasicFio":{"Gender":"m","FirstName":"Иван","LastName":"Иванов"}}]}'
        useragent_mock_post.return_value = useragent_mock_post_result

        connect_mock = mock.Mock()
        connect_mock.return_value = connect_mock
        connect_mock.configure_mock(**{
            'execute.return_value': True,
            'close.return_value': True,
        })

        client_mock = mock.Mock()
        client_mock.send().get.return_value = 'pong'

        redis_ping_mock = mock.Mock()
        redis_ping_mock.return_value = True

        with nested(mock.patch.object(get_dbm('passportdbcentral').get_engine(), 'connect', connect_mock),
                    mock.patch.object(get_dbm('passportdbshard1').get_engine(), 'connect', connect_mock),
                    mock.patch.object(UserAgent, 'get', useragent_mock),
                    mock.patch.object(UserAgent, 'post', useragent_mock_post),
                    mock.patch('passport.backend.core.redis_manager.redis_manager.RedisManager.ping', redis_ping_mock)):
            rv = self.env.client.get('/ping?check=db,blackbox,frontend,redis,lingvo')
            eq_(rv.status_code, 200)
            eq_(rv.data, 'Pong\n')

            # ЧЯ
            eq_(self.env.blackbox.request.called, True)
            eq_(self.env.blackbox.request.call_count, 1)

            # БД
            eq_(connect_mock.called, True)
            # 2 вызова, потому что 2 базы, а в каждой проверяем только мастер
            eq_(connect_mock.call_count, 2)

            eq_(
                connect_mock.method_calls,
                [
                    mock.call.execute('select 1'),
                    mock.call.close(),
                    mock.call.execute('select 1'),
                    mock.call.close(),
                ],
            )

            # frontend
            eq_(useragent_mock.called, True)
            eq_(useragent_mock.call_count, 1)

            # redis
            eq_(redis_ping_mock.called, True)
            eq_(redis_ping_mock.call_count, 1)

            # lingvo
            eq_(useragent_mock_post.called, True)
            eq_(useragent_mock_post.call_count, 1)

    def test_ok_db(self):
        connect_mock = mock.Mock()
        connect_mock.return_value = connect_mock
        connect_mock.configure_mock(**{
            'execute.return_value': True,
            'close.return_value': True,
        })

        with nested(mock.patch.object(get_dbm('passportdbcentral').get_engine(), 'connect', connect_mock),
                    mock.patch.object(get_dbm('passportdbshard1').get_engine(), 'connect', connect_mock)):
            rv = self.env.client.get('/ping?check=db')
            eq_(rv.status_code, 200)
            eq_(rv.data, 'Pong\n')

            eq_(connect_mock.called, True)
            # 2 вызова, потому что 2 базы, а в каждой проверяем только мастер
            eq_(connect_mock.call_count, 2)

            eq_(
                connect_mock.method_calls,
                [
                    mock.call.execute('select 1'),
                    mock.call.close(),
                    mock.call.execute('select 1'),
                    mock.call.close(),
                ],
            )

    def test_fail_db_central(self):
        central_connect_mock = mock.Mock()
        shard_connect_mock = mock.Mock()
        for side_effect in (
            sqlalchemy.exc.DatabaseError('', '', ''),
            MySQLdb.DatabaseError('', '', ''),
            sqlalchemy.exc.InterfaceError('', '', ''),
            MySQLdb.InterfaceError('', '', ''),
        ):
            central_connect_mock.side_effect = side_effect
            central_connect_mock.reset_mock()
            shard_connect_mock.side_effect = None
            shard_connect_mock.reset_mock()

            with nested(mock.patch.object(get_dbm('passportdbcentral').get_engine(), 'connect', central_connect_mock),
                        mock.patch.object(get_dbm('passportdbshard1').get_engine(), 'connect', shard_connect_mock)):
                rv = self.env.client.get('/ping?check=db')
                eq_(rv.status_code, 503)
                response = json.loads(rv.data)
                eq_(central_connect_mock.call_count, 1)
                eq_(shard_connect_mock.call_count, 1)
                ok_('errors' in response)
                assert_errors(response['errors'], [{None: 'databaseunavailable'}])

    def test_fail_db_shard(self):
        central_connect_mock = mock.Mock()
        shard_connect_mock = mock.Mock()
        for side_effect in (
            sqlalchemy.exc.DatabaseError('', '', ''),
            MySQLdb.DatabaseError('', '', ''),
            sqlalchemy.exc.InterfaceError('', '', ''),
            MySQLdb.InterfaceError('', '', ''),
        ):
            central_connect_mock.return_value = central_connect_mock
            central_connect_mock.reset_mock()
            shard_connect_mock.side_effect = side_effect
            shard_connect_mock.reset_mock()

            with nested(mock.patch.object(get_dbm('passportdbcentral').get_engine(), 'connect', central_connect_mock),
                        mock.patch.object(get_dbm('passportdbshard1').get_engine(), 'connect', shard_connect_mock)):
                rv = self.env.client.get('/ping?check=db')
                eq_(rv.status_code, 503)
                response = json.loads(rv.data)
                eq_(central_connect_mock.call_count, 1)
                eq_(shard_connect_mock.call_count, 1)
                ok_('errors' in response)
                assert_errors(response['errors'], [{None: 'databaseunavailable'}])

    def test_ok_blackbox(self):
        self.env.blackbox.set_blackbox_response_value('userinfo',
                                                      blackbox_userinfo_response(uid=123))
        rv = self.env.client.get('/ping?check=blackbox')
        eq_(rv.status_code, 200)
        eq_(rv.data, 'Pong\n')

    def test_ok_blackbox_no_uid(self):
        self.env.blackbox.set_blackbox_response_value('userinfo',
                                                      blackbox_userinfo_response(uid=None))
        rv = self.env.client.get('/ping?check=blackbox')
        eq_(rv.status_code, 200)
        eq_(rv.data, 'Pong\n')

    def test_fail_1_blackbox(self):
        self.env.blackbox.set_blackbox_response_side_effect('userinfo', RequestError)
        rv = self.env.client.get('/ping?check=blackbox')
        eq_(rv.status_code, 503)
        response = json.loads(rv.data)
        ok_('errors' in response)
        assert_errors(response['errors'], {None: 'blackboxunavailable'})

    def test_fail_2_blackbox(self):
        self.env.blackbox.set_blackbox_response_side_effect('userinfo', blackbox.BaseBlackboxError)
        rv = self.env.client.get('/ping?check=blackbox')
        eq_(rv.status_code, 503)
        response = json.loads(rv.data)
        ok_('errors' in response)
        assert_errors(response['errors'], {None: 'blackboxunavailable'})

    def test_ping_not_ok(self):
        with settings_context(PING_FILE='pong.html'):
            rv = self.env.client.get('/ping')
            eq_(rv.status_code, 503)
            response = json.loads(rv.data)
            ok_('errors' in response)
            assert_errors(response['errors'], {None: 'backendunavailable'})

    def test_ok_frontend(self):
        useragent_mock = mock.Mock()
        useragent_get_mock = mock.Mock()
        useragent_get_mock.content = 'Pong\n'
        useragent_mock.return_value = useragent_get_mock
        with mock.patch.object(UserAgent, 'get', useragent_mock):
            rv = self.env.client.get('/ping?check=frontend')
            eq_(useragent_mock.called, True)
            eq_(rv.status_code, 200)
            eq_(rv.data, 'Pong\n')

    def test_fail_1_frontend(self):
        useragent_mock = mock.Mock()
        useragent_mock.side_effect = RequestError('Frontend unavailable')
        with mock.patch.object(UserAgent, 'get', useragent_mock):
            rv = self.env.client.get('/ping?check=frontend')
            eq_(useragent_mock.called, True)
            eq_(rv.status_code, 503)
            response = json.loads(rv.data)
            ok_('errors' in response)
            assert_errors(response['errors'], {None: 'frontendunavailable'})

    def test_fail_2_frontend(self):
        useragent_mock = mock.Mock()
        useragent_get_mock = mock.Mock()
        useragent_get_mock.content = 'Not pong не понг'
        useragent_mock.return_value = useragent_get_mock
        with mock.patch.object(UserAgent, 'get', useragent_mock):
            rv = self.env.client.get('/ping?check=frontend')
            eq_(useragent_mock.called, True)
            eq_(rv.status_code, 503)
            response = json.loads(rv.data)
            ok_('errors' in response)
            assert_errors(response['errors'], {None: 'frontendnopong'})

    def test_ok_redis(self):
        redis_ping_mock = mock.Mock()
        redis_ping_mock.return_value = True
        with mock.patch('passport.backend.core.redis_manager.redis_manager.RedisManager.ping', redis_ping_mock):
            rv = self.env.client.get('/ping?check=redis')
            eq_(rv.status_code, 200)
            eq_(rv.data, 'Pong\n')
            eq_(redis_ping_mock.called, True)
            eq_(redis_ping_mock.call_count, 1)

    def test_fail_redis_1(self):
        redis_ping_mock = mock.Mock()
        redis_ping_mock.side_effect = RedisError()
        with mock.patch('passport.backend.core.redis_manager.redis_manager.RedisManager.ping', redis_ping_mock):
            rv = self.env.client.get('/ping?check=redis')
            eq_(rv.status_code, 503)
            response = json.loads(rv.data)
            ok_('errors' in response)
            assert_errors(response['errors'], [{None: 'redisunavailable'}])

    def test_fail_redis_2(self):
        redis_ping_mock = mock.Mock()
        redis_ping_mock.return_value = False
        with mock.patch('passport.backend.core.redis_manager.redis_manager.RedisManager.ping', redis_ping_mock):
            rv = self.env.client.get('/ping?check=redis')
            eq_(rv.status_code, 503)
            response = json.loads(rv.data)
            ok_('errors' in response)
            assert_errors(response['errors'], [{None: 'redisunavailable'}])

    def test_ok_lingvo(self):
        useragent_mock = mock.Mock()
        useragent_post_mock = mock.Mock()
        useragent_post_mock.content = u'{"passport":[{"BasicFio":{"Gender":"m","FirstName":"Иван","LastName":"Иванов"}}]}'
        useragent_mock.return_value = useragent_post_mock
        with mock.patch.object(UserAgent, 'post', useragent_mock):
            rv = self.env.client.get('/ping?check=lingvo')
            eq_(useragent_mock.called, True)
            eq_(rv.status_code, 200)
            eq_(rv.data, 'Pong\n')

    def test_fail_1_lingvo(self):
        useragent_mock = mock.Mock()
        useragent_mock.side_effect = RequestError('Lingvo api unavailable')
        with mock.patch.object(UserAgent, 'post', useragent_mock):
            rv = self.env.client.get('/ping?check=lingvo')
            eq_(useragent_mock.called, True)
            eq_(rv.status_code, 503)
            response = json.loads(rv.data)
            ok_('errors' in response)
            assert_errors(response['errors'], {None: 'lingvoapiunavailable'})

    def test_fail_2_lingvo(self):
        api_responses = [
            '{"passport":[{"BasicFio":{"Gender":"m","FirstName":"Ин","LastName":"И"}}]}',
            '{"passport":{"BasicFio":{"Gender":"m","FirstName":"Иван","LastName":"Иванов"}}}',
        ]

        for api_response in api_responses:
            useragent_mock = mock.Mock()
            useragent_post_mock = mock.Mock()
            useragent_post_mock.content = api_response
            useragent_mock.return_value = useragent_post_mock
            with mock.patch.object(UserAgent, 'post', useragent_mock):
                rv = self.env.client.get('/ping?check=lingvo')
                eq_(useragent_mock.called, True)
                eq_(rv.status_code, 503)
                response = json.loads(rv.data)
                ok_('errors' in response)
                assert_errors(response['errors'], {None: 'lingvoapibadresponse'})
