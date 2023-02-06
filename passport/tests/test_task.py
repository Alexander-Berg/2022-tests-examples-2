# -*- coding: utf-8 -*-

from contextlib import contextmanager
from json import (
    dumps as json_dumps,
    loads as json_loads,
)

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.time_utils.time_utils import unixtime
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import FACEBOOK_BUSINESS_ID
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.task import (
    InvalidTaskDataError,
    load_task_from_redis,
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_NAME1,
    APPLICATION_SECRET1,
    BUSINESS_TOKEN1,
    CONSUMER1,
    EMAIL1,
    EXTERNAL_APPLICATION_ID1,
    FACEBOOK_APPLICATION_ID1,
    FACEBOOK_APPLICATION_NAME1,
    FIRSTNAME1,
    LASTNAME1,
    PROFILE_ID1,
    RETPATH1,
    SIMPLE_USERID1,
    TASK_ID1,
    TASK_ID2,
    UID1,
    UNIXTIME1,
    USERNAME1,
    VKONTAKTE_APPLICATION_ID1,
    VKONTAKTE_APPLICATION_NAME1,
    YANDEXUID1,
)
from passport.backend.social.common.test.fake_redis_client import (
    FakeRedisClient,
    RedisPatch,
)
from passport.backend.social.common.test.test_case import TestCase


class _TaskTestCase(TestCase):
    def setUp(self):
        super(_TaskTestCase, self).setUp()
        self._fake_redis = FakeRedisClient()
        self._redis_patch = RedisPatch(self._fake_redis).start()
        LazyLoader.register('slave_db_engine', lambda: self._fake_db.get_engine())

    def tearDown(self):
        LazyLoader.flush()
        self._redis_patch.stop()
        super(_TaskTestCase, self).tearDown()

    def _build_minimal_task(self, task_id=TASK_ID1, created_at=unixtime(2000, 1, 1),
                            state='catatonia'):
        task = Task()
        task.task_id = task_id
        task.created = created_at
        task.state = state
        task.start_args = dict()
        return task


class TestTaskMinimal(_TaskTestCase):
    def test_dump_session_data(self):
        task = self._build_minimal_task(
            task_id=TASK_ID2,
            created_at=unixtime(1998, 1, 1),
            state='dyslexia',
        )

        session_data = task.dump_session_data()

        session_data = json_loads(session_data)
        self.assertEqual(
            session_data,
            {
                'tid': TASK_ID2,
                'ts': unixtime(1998, 1, 1),
                'state': 'dyslexia',
                'args': {},
            },
        )

    def test_parse_session_data(self):
        task = self._build_minimal_task(
            task_id=TASK_ID2,
            created_at=unixtime(1998, 1, 1),
            state='dyslexia',
        )
        session_data = task.dump_session_data()

        task = Task()
        task.parse_session_data(session_data)

        expected_task = self._build_minimal_task(
            task_id=TASK_ID2,
            created_at=unixtime(1998, 1, 1),
            state='dyslexia',
        )
        self.assertEqual(task.to_json_dict(), expected_task.to_json_dict())


class TestTask(_TaskTestCase):
    def setUp(self):
        super(TestTask, self).setUp()
        providers.init()
        self.task = Task()

    def test_all(self):
        with self.assertRaises(InvalidTaskDataError):
            self.task.parse_session_data(None)

        data = {
            'tid': TASK_ID1,
            'args': {'foo': 'bar'},
            'uid': UID1,
            'state': 'state',
            'req_t': None,
            'code': '12345',
            'useless': 'param',
            'retpath': RETPATH1,
            'consumer': CONSUMER1,
            'application': FACEBOOK_APPLICATION_ID1,
            'yandexuid': YANDEXUID1,
            'provider': {'code': 'fb', 'name': 'facebook', 'id': 2},
        }

        mapping = dict((v, k) for k, v in self.task.dump_fields_mapping.iteritems())

        with self.assertRaises(InvalidTaskDataError):
            self.task.parse_session_data(json_dumps(data))

        CREATED = now.f()
        data['ts'] = CREATED

        self.task.parse_session_data(json_dumps(data))

        for key, val in data.iteritems():
            if key in {'useless', 'application'}:
                continue
            c_key = mapping.get(key, key)
            eq_(getattr(self.task, c_key), val)
        ok_(not getattr(self.task, 'useless', None))
        eq_(self.task.application.identifier, data['application'])

        # теперь сдампим данные обратно
        with self.assertRaises(AttributeError):
            self.task.created = None
            self.task.dump_session_data()
        self.task.created = CREATED
        self.task.access_token = {'value': '123', 'refresh': 'refresh-123'}
        self.task.profile = {
            'userid': 100,
            'firstname': 'Petr',
            'username': 'mario',
            'useless': 'key',
        }
        self.task.uid = UID1
        dumped_data = self.task.dump_session_data()
        dumped_data = json_loads(dumped_data)
        expected_data = {
            'tid': TASK_ID1,
            'uid': UID1,
            'code': '12345',
            'ts': CREATED,
            'state': 'state',
            'consumer': CONSUMER1,
            'retpath': RETPATH1,
            'provider': {'code': 'fb', 'name': 'facebook', 'id': 2},
            'application': FACEBOOK_APPLICATION_ID1,
            'yandexuid': YANDEXUID1,
            'args': {'foo': 'bar'},
        }
        self.assertDictEqual(expected_data, dumped_data)

        # проверим, что будет использоваться для генераци профиля
        self.assertEqual(
            self.task.get_social_userinfo(),
            {
                'userid': 100,
                'firstname': 'Petr',
                'provider': {'code': 'fb', 'name': 'facebook', 'id': 2},
                'username': 'mario',
            },
        )

        response = self.task.get_dict_for_response()

        expected_data = {
            'profile': {
                'userid': 100,
                'firstname': 'Petr',
                'provider': {'code': 'fb', 'name': 'facebook', 'id': 2},
                'username': 'mario',
            },
            'token': {
                'value': '123',
                'refresh': 'refresh-123',
                'application': FACEBOOK_APPLICATION_NAME1,
                'application_attributes': {
                    'id': FACEBOOK_APPLICATION_NAME1,
                    'third_party': False,
                },
            },
            'task_id': TASK_ID1,
            'created': CREATED,
            'yandexuid': YANDEXUID1,
        }
        self.assertDictContainsSubset(expected_data, response)

    def test_business_token_survives_redis(self):
        self.task.access_token = dict()
        self.task.application = Application(
            identifier=FACEBOOK_APPLICATION_ID1,
            name=FACEBOOK_APPLICATION_NAME1,
        )
        provider = {'code': 'fb', 'name': 'facebook', 'id': 2}
        self.task.provider = provider
        self.task.profile = {'token_for_business': BUSINESS_TOKEN1}

        save_task_to_redis(self._fake_redis, TASK_ID1, self.task)
        restored_task = load_task_from_redis(self._fake_redis, TASK_ID1)

        self.assertEqual(restored_task.profile, self.task.profile)


class TestTaskPassthroughErrors(_TaskTestCase):
    def test_dump_session_data(self):
        task = self._build_minimal_task()
        task.passthrough_errors = ['foo', 'bar']

        session_data = task.dump_session_data()

        session_data = json_loads(session_data)
        self.assertIn('passthrough_errors', session_data)
        self.assertEqual(session_data['passthrough_errors'], 'bar,foo')

    def test_parse_session_data(self):
        old_task = self._build_minimal_task()
        old_task.passthrough_errors = ['foo', 'bar']
        session_data = old_task.dump_session_data()

        new_task = Task()
        new_task.parse_session_data(session_data)

        self.assertEqual(new_task.passthrough_errors, ['bar', 'foo'])


class TestTaskNonce(_TaskTestCase):
    def test_dump_session_data(self):
        task = self._build_minimal_task()
        task.nonce = 'hello'

        session_data = task.dump_session_data()

        session_data = json_loads(session_data)
        self.assertIn('nonce', session_data)
        self.assertEqual(session_data['nonce'], 'hello')

    def test_parse_session_data(self):
        old_task = self._build_minimal_task()
        old_task.nonce = 'hello'
        session_data = old_task.dump_session_data()

        new_task = Task()
        new_task.parse_session_data(session_data)

        self.assertEqual(new_task.nonce, 'hello')


class TestTaskDictForResponse(_TaskTestCase):
    def test_empty(self):
        task = Task()

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_task_id(self):
        task = Task()
        task.task_id = TASK_ID1

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                task_id=TASK_ID1,
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_state(self):
        task = Task()
        task.state = 'asia'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_created(self):
        task = Task()
        task.created = UNIXTIME1

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                created=UNIXTIME1,
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_finished(self):
        task = Task()
        task.finished = UNIXTIME1

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                finished=UNIXTIME1,
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_start_args(self):
        task = Task()
        task.start_args = dict(foo='one', bar=2, spam=None)

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_access_token(self):
        task = Task()
        task.access_token = dict(foo='one', bar=2, spam=None)

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    foo='one',
                    bar=2,
                    spam=None,
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_request_token(self):
        task = Task()
        task.request_token = dict(foo='one', bar=2)

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_exchange(self):
        task = Task()
        task.exchange = 'kek'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_code_challenge(self):
        task = Task()
        task.code_challenge = 'kek'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                code_challenge='kek',
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_code_challenge_method(self):
        task = Task()
        task.code_challenge_method = 'kek'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                code_challenge_method='kek',
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_consumer(self):
        task = Task()
        task.consumer = 'boss'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                consumer='boss',
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_yandexuid(self):
        task = Task()
        task.yandexuid = 'boss'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                yandexuid='boss',
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_provider(self):
        task = Task()
        task.provider = dict(foo='foo', bar=2, spam=None)

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(
                    provider=dict(
                        foo='foo',
                        bar=2,
                        spam=None,
                    ),
                ),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_application(self):
        task = Task()
        task.application = Application(
            identifier=APPLICATION_ID1,
            name=APPLICATION_NAME1,
        )

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=APPLICATION_NAME1,
                    application_attributes=dict(
                        id=APPLICATION_NAME1,
                        third_party=False,
                    ),
                ),
            ),
        )

    def test_application_first_party(self):
        task = Task()
        task.application = Application(
            name=APPLICATION_NAME1,
            is_third_party=False,
        )

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=APPLICATION_NAME1,
                    application_attributes=dict(
                        id=APPLICATION_NAME1,
                        third_party=False,
                    ),
                ),
            ),
        )

    def test_application_third_party(self):
        task = Task()
        task.application = Application(
            name=APPLICATION_NAME1,
            is_third_party=True,
        )

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=APPLICATION_NAME1,
                    application_attributes=dict(
                        id=APPLICATION_NAME1,
                        third_party=True,
                    ),
                ),
            ),
        )

    def test_application_related_yandex_client_id(self):
        task = Task()
        task.application = Application(
            name=APPLICATION_NAME1,
            related_yandex_client_id=EXTERNAL_APPLICATION_ID1,
        )

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=APPLICATION_NAME1,
                    application_attributes=dict(
                        id=APPLICATION_NAME1,
                        related_yandex_client_id=EXTERNAL_APPLICATION_ID1,
                        third_party=False,
                    ),
                ),
            ),
        )

    def test_application_related_yandex_client_secret(self):
        task = Task()
        task.application = Application(
            name=APPLICATION_NAME1,
            related_yandex_client_secret=APPLICATION_SECRET1,
        )

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=APPLICATION_NAME1,
                    application_attributes=dict(
                        id=APPLICATION_NAME1,
                        third_party=False,
                    ),
                ),
            ),
        )

    def test_application_related_yandex_client_secret_with_argument(self):
        task = Task()
        task.application = Application(
            name=APPLICATION_NAME1,
            related_yandex_client_secret=APPLICATION_SECRET1,
        )

        response = task.get_dict_for_response(with_related_yandex_client_secret=True)

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=APPLICATION_NAME1,
                    application_attributes=dict(
                        id=APPLICATION_NAME1,
                        related_yandex_client_secret=APPLICATION_SECRET1,
                        third_party=False,
                    ),
                ),
            ),
        )

    def test_retpath(self):
        task = Task()
        task.retpath = 'https://www.yandex.ru/'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_place(self):
        task = Task()
        task.place = 'left'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_passthrough_errors_empty(self):
        task = Task()
        task.passthrough_errors = []

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_passthrough_errors(self):
        task = Task()
        task.passthrough_errors = ['1', '2']

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_profile(self):
        task = Task()
        task.profile = dict(userid=SIMPLE_USERID1, username=USERNAME1, spam=None)

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(
                    userid=SIMPLE_USERID1,
                    username=USERNAME1,
                    provider=None,
                ),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_profile_token_for_business(self):
        task = Task()
        task.profile = dict(token_for_business='ehlo')

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(
                    business=dict(
                        id=FACEBOOK_BUSINESS_ID,
                        token='ehlo',
                    ),
                    provider=None,
                ),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_profile_id(self):
        task = Task()
        task.profile_id = PROFILE_ID1

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_uid(self):
        task = Task()
        task.uid = UID1

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                uid=UID1,
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )

    def test_sid(self):
        task = Task()
        task.sid = 'sid1'

        response = task.get_dict_for_response()

        self.assertEqual(
            response,
            dict(
                sid='sid1',
                profile=dict(provider=None),
                token=dict(
                    application=None,
                    application_attributes=dict(),
                ),
            ),
        )


class TestTaskSaveTaskToRedis(_TaskTestCase):
    def setUp(self):
        super(TestTaskSaveTaskToRedis, self).setUp()
        providers.init()

    @contextmanager
    def _assert_changes_saved(self):
        task1 = Task()
        task1.task_id = TASK_ID1

        yield task1

        save_task_to_redis(self._fake_redis, TASK_ID1, task1)
        task2 = load_task_from_redis(self._fake_redis, TASK_ID1)

        self.assertEqual(
            task1.to_json_dict(),
            task2.to_json_dict(),
        )

    @contextmanager
    def _assert_changes_not_saved(self):
        task1 = Task()
        task1.task_id = TASK_ID1

        yield task1

        save_task_to_redis(self._fake_redis, TASK_ID1, task1)
        task2 = load_task_from_redis(self._fake_redis, TASK_ID1)

        task3 = Task()
        task3.task_id = TASK_ID1
        task3.in_redis = True

        self.assertEqual(
            task2.to_json_dict(),
            task3.to_json_dict(),
        )

    def test_empty(self):
        task1 = Task()
        save_task_to_redis(self._fake_redis, TASK_ID1, task1)
        task2 = load_task_from_redis(self._fake_redis, TASK_ID1)
        task1.task_id = TASK_ID1

        self.assertEqual(
            task1.to_json_dict(),
            task2.to_json_dict(),
        )

    def test_task_id(self):
        task1 = Task()
        task1.task_id = TASK_ID1
        save_task_to_redis(self._fake_redis, TASK_ID1, task1)
        task2 = load_task_from_redis(self._fake_redis, TASK_ID1)

        self.assertEqual(
            task1.to_json_dict(),
            task2.to_json_dict(),
        )

    def test_state(self):
        with self._assert_changes_not_saved() as task:
            task.state = 'asia'

    def test_created(self):
        with self._assert_changes_saved() as task:
            task.created = UNIXTIME1

    def test_finished(self):
        with self._assert_changes_saved() as task:
            task.finished = UNIXTIME1

    def test_start_args(self):
        with self._assert_changes_not_saved() as task:
            task.start_args = dict(foo='one', bar=2, spam=None)

    def test_access_token(self):
        with self._assert_changes_saved() as task:
            task.access_token = dict(foo='one', bar=2, spam=None)

    def test_request_token(self):
        with self._assert_changes_not_saved() as task:
            task.request_token = dict(foo='one', bar=2)

    def test_exchange(self):
        with self._assert_changes_not_saved() as task:
            task.exchange = 'kek'

    def test_code_challenge(self):
        with self._assert_changes_saved() as task:
            task.code_challenge = 'kek'

    def test_code_challenge_method(self):
        with self._assert_changes_saved() as task:
            task.code_challenge_method = 'kek'

    def test_consumer(self):
        with self._assert_changes_saved() as task:
            task.consumer = 'boss'

    def test_yandexuid(self):
        with self._assert_changes_saved() as task:
            task.yandexuid = 'boss'

    def test_provider(self):
        with self._assert_changes_saved() as task:
            task.provider = dict(foo='foo', bar=2, spam=None)

    def test_application(self):
        with self._assert_changes_saved() as task:
            task.application = Application(
                identifier=VKONTAKTE_APPLICATION_ID1,
                name=VKONTAKTE_APPLICATION_NAME1,
            )

    def test_retpath(self):
        with self._assert_changes_not_saved() as task:
            task.retpath = 'https://www.yandex.ru/'

    def test_place(self):
        with self._assert_changes_not_saved() as task:
            task.place = 'left'

    def test_passthrough_errors(self):
        with self._assert_changes_not_saved() as task:
            task.passthrough_errors = ['foo', 'bar']

    def test_profile(self):
        with self._assert_changes_saved() as task:
            task.profile = dict(userid=SIMPLE_USERID1, username=USERNAME1)

    def test_profile_token_for_business(self):
        with self._assert_changes_saved() as task:
            task.profile = dict(token_for_business='ehlo')

    def test_profile_id(self):
        with self._assert_changes_not_saved() as task:
            task.profile_id = PROFILE_ID1

    def test_uid(self):
        with self._assert_changes_saved() as task:
            task.uid = UID1

    def test_sid(self):
        with self._assert_changes_saved() as task:
            task.sid = 'sid1'


class TestTaskGetSocialUserinfo(_TaskTestCase):
    def test_good_attributes(self):
        task = Task()
        task.profile = dict(
            userid=SIMPLE_USERID1,
            username=USERNAME1,
            firstname=FIRSTNAME1,
            lastname=LASTNAME1,
            gender='f',
            birthday='0000-05-29',
            avatar='avatar',
            email=EMAIL1,
            links=['link1', 'link2'],
            phone='60783',
        )

        userinfo = task.get_social_userinfo()

        self.assertEqual(
            userinfo,
            dict(
                provider=None,
                userid=SIMPLE_USERID1,
                username=USERNAME1,
                firstname=FIRSTNAME1,
                lastname=LASTNAME1,
                gender='f',
                birthday='0000-05-29',
                avatar='avatar',
                email=EMAIL1,
                links=['link1', 'link2'],
                phone='60783',
            ),
        )

    def test_provider(self):
        task = Task()
        task.provider = dict(foo=1, bar='bar')

        userinfo = task.get_social_userinfo()

        self.assertEqual(
            userinfo,
            dict(
                provider=dict(
                    foo=1,
                    bar='bar',
                ),
            ),
        )

    def test_provider_on_profile(self):
        task = Task()
        task.profile = dict(provider='provider')

        userinfo = task.get_social_userinfo()

        self.assertEqual(userinfo, dict(provider=None))

    def test_token_for_business(self):
        task = Task()
        task.profile = dict(token_for_business='hello')

        userinfo = task.get_social_userinfo()

        self.assertEqual(
            userinfo,
            dict(
                provider=None,
                business=dict(id=FACEBOOK_BUSINESS_ID, token='hello'),
            ),
        )
