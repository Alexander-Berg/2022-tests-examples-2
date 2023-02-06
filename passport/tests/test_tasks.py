# -*- coding: utf-8 -*-

from datetime import datetime
import json

from nose.tools import eq_
from passport.backend.core import Undefined
from passport.backend.social.common.db.schemas import sub_table as st
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Facebook import Facebook
from passport.backend.social.common.providers.MailRu import MailRu
from passport.backend.social.common.refresh_token.utils import find_refresh_token_by_token_id
from passport.backend.social.common.task import (
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    MAIL_RU_APPLICATION_NAME1,
    SIMPLE_USERID1,
    TASK_ID2,
    UNIXTIME1,
)
from passport.backend.social.common.token.utils import find_token_by_value_for_account
from sqlalchemy.sql.expression import (
    and_,
    select,
)

from .base_test_data import (
    TEST_APP_ID,
    TEST_APP_ID_2,
    TEST_BUSINESS_TOKEN,
    TEST_BUSINESS_USERID,
    TEST_CONSUMER,
    TEST_SIMLE_USERID,
    TEST_SIMLE_USERID_2,
    TEST_TASK_FINISHED,
    TEST_TASK_ID,
    TEST_TASK_STARTED,
    TEST_UID,
    TEST_YANDEXUID,
)
from .common import TestApiViewsCase


APPLICATIONS_CONF = [
    dict(
        provider_id=Facebook.id,
        application_id=20,
        application_name='facebook',
        default=True,
        provider_client_id='facebook',
        key='',
        secret='',
    ),
]


class _BaseTaskViewTestCase(TestApiViewsCase):
    def _build_task(self, task_id=TEST_TASK_ID, uid=None, userid=SIMPLE_USERID1,
                    provider=Undefined, application_name=MAIL_RU_APPLICATION_NAME1,
                    profile=None, access_token=None):
        task = Task()
        task.task_id = task_id
        task.uid = uid
        task.created = TEST_TASK_STARTED
        task.finished = TEST_TASK_FINISHED
        task.consumer = TEST_CONSUMER
        task.yandexuid = TEST_YANDEXUID

        if provider is Undefined:
            provider = dict(id=MailRu.id, code=MailRu.code, name='mailru')
        if provider:
            task.provider = provider

        task.application = providers.get_application_by_name(application_name)
        if profile is None:
            profile = {
                'userid': userid,
                'username': 'arji.barjanian@mail.ru',
                'firstname': 'Arji',
                'lastname': 'Barjanian',
                'birthday': '1988-12-23',
                'gender': 'm',
                'email': 'arji.barjanian@mail.ru',
                'links': ['http://my.mail.ru/mail/arji.barjanian'],
                'avatar': {
                    '45x0': 'http://avt.appsmail.ru/mail/arji.barjanian/_avatarsmall',
                    '90x0': 'http://avt.appsmail.ru/mail/arji.barjanian/_avatar',
                },
            }
        task.profile = profile
        if access_token is None:
            access_token = {
                'value': APPLICATION_TOKEN1,
                'expires': 1408104159,
                'scope': '',
            }
        task.access_token = access_token
        return task


class TestCreateProfileByTask(_BaseTaskViewTestCase):
    def setUp(self):
        super(TestCreateProfileByTask, self).setUp()

        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'task-get',
                'profile-create',
                'task-uid',
                'task-allow_auth',
            ],
        )

    def build_settings(self):
        settings = super(TestCreateProfileByTask, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings

    def set_task_data(self, uid=TEST_UID, userid=TEST_SIMLE_USERID,
                      provider=Undefined, task_id=TEST_TASK_ID):
        if provider is Undefined:
            provider = {'code': Facebook.code, 'name': 'facebook', 'id': Facebook.id}
        profile = {
            'username': 'UserName',
            'links': ['https://www.facebook.com/profile.php?id=15265000'],
            'firstname': 'First',
            'gender': 'm',
            'userid': userid,
            'token_for_business': TEST_BUSINESS_TOKEN,
            'birthday': '1989-12-28',
            'avatar': {'0x0': 'https://some/url'},
            'lastname': 'LastName',
            'email': 'email@example.com',
        }
        access_token = {
            'scope': 'public_profile,basic_info',
            'expires': UNIXTIME1,
            'value': APPLICATION_TOKEN1,
            'refresh': APPLICATION_TOKEN2,
        }
        task1 = self._build_task(
            task_id=task_id,
            uid=uid,
            userid=userid,
            provider=provider,
            application_name='facebook',
            profile=profile,
            access_token=access_token,
        )
        save_task_to_redis(self._fake_redis, task_id, task1)

    def get_ok_response(self, response):
        eq_(response.status_code, 200)
        data = json.loads(response.data)
        eq_(data['status'], 'ok')
        return data

    def assert_token_saved(
        self,
        uid=TEST_UID,
        application_id=20,
        token_value=APPLICATION_TOKEN1,
        scopes={'public_profile', 'basic_info'},
        token_expires_at=datetime.fromtimestamp(UNIXTIME1),
    ):
        token = find_token_by_value_for_account(uid, application_id, token_value, self._fake_db.get_engine())
        self.assertIsNotNone(token)

        self.assertEqual(token.profile_id, 1)
        self.assertIsNone(token.secret)

        if scopes is None:
            scopes = set([])
        self.assertEqual(token.scopes, scopes)

        self.assertEqual(token.expired, token_expires_at)

        timestamp = datetime.fromtimestamp(TEST_TASK_FINISHED)
        self.assertEqual(token.created, timestamp)
        self.assertEqual(token.verified, timestamp)
        self.assertEqual(token.confirmed, timestamp)

    def assert_refresh_token_saved(
        self,
        uid=TEST_UID,
        application_id=20,
        token_value=APPLICATION_TOKEN1,
        refresh_token_value=APPLICATION_TOKEN2,
        scopes={'public_profile', 'basic_info'},
    ):
        token = find_token_by_value_for_account(uid, application_id, token_value, self._fake_db.get_engine())
        self.assertIsNotNone(token)

        refresh_token = find_refresh_token_by_token_id(token.token_id, self._fake_db.get_engine())

        self.assertEqual(refresh_token.value, refresh_token_value)

        if scopes is None:
            scopes = set([])
        self.assertEqual(refresh_token.scopes, scopes)

    def test_create_new_profile(self):
        """
        Создаем новый профиль, такого еще нет в базе, business_token также в базе отсутствует.
        """
        self.set_task_data()

        res = self.app_client.post('/api/task/%s/bind' % TEST_TASK_ID)
        data = self.get_ok_response(res)

        self.assertDictEqual(
            self.get_profile_dict_from_db(data['profile_id']),
            self.get_profile_data(profile_id=data['profile_id']),
        )
        self.check_business_mapping({
            TEST_APP_ID: TEST_SIMLE_USERID,
        })
        self.assert_token_saved()
        self.assert_refresh_token_saved()

    def test_create_new_profile_token_exists_same_userid(self):
        """
        Создаем новый профиль, такого еще нет в базе,
        business_token уже есть в базе, но только для другого приложения, userid тот же.
        """
        self.set_task_data()
        self.add_business_userid_to_db(app_id=TEST_APP_ID_2)

        res = self.app_client.post('/api/task/%s/bind' % TEST_TASK_ID)
        data = self.get_ok_response(res)

        self.assertDictEqual(
            self.get_profile_dict_from_db(data['profile_id']),
            self.get_profile_data(profile_id=data['profile_id']),
        )
        self.check_business_mapping({
            TEST_APP_ID_2: TEST_SIMLE_USERID,
            TEST_APP_ID: TEST_SIMLE_USERID,
        })

    def test_create_new_profile_token_exists_other_userid(self):
        """
        Создаем новый профиль, такого еще нет в базе,
        business_token уже есть в базе, но только для другого приложения, userid другой.
        """
        self.set_task_data()
        self.add_business_userid_to_db(app_id=TEST_APP_ID_2, userid=TEST_SIMLE_USERID_2)

        res = self.app_client.post('/api/task/%s/bind' % TEST_TASK_ID)
        data = self.get_ok_response(res)

        self.assertDictEqual(
            self.get_profile_dict_from_db(data['profile_id']),
            self.get_profile_data(profile_id=data['profile_id']),
        )
        self.check_business_mapping({
            TEST_APP_ID_2: TEST_SIMLE_USERID_2,
            TEST_APP_ID: TEST_SIMLE_USERID,
        })

    def test_create_new_profile_token_exists(self):
        """
        Создаем новый профиль, такого еще нет в базе,
        запись в bamt уже есть, ничего не должно измениться.
        """
        self.set_task_data()
        self.add_business_userid_to_db()

        res = self.app_client.post('/api/task/%s/bind' % TEST_TASK_ID)
        data = self.get_ok_response(res)

        self.assertDictEqual(
            self.get_profile_dict_from_db(data['profile_id']),
            self.get_profile_data(profile_id=data['profile_id']),
        )
        self.check_business_mapping({
            TEST_APP_ID: TEST_SIMLE_USERID,
        })

    def test_update_existing_profile_with_simple_userid(self):
        """
        Профиль уже есть, у него простой userid.
        Должны заменить userid на business_userid, старый userid добавить
        в bamt для текущего приложения и "приложения 0".
        """
        self.set_task_data()
        self.add_profile_to_db(self.get_profile_data(userid=TEST_SIMLE_USERID))

        res = self.app_client.post('/api/task/%s/bind' % TEST_TASK_ID)
        data = self.get_ok_response(res)

        self.assertDictEqual(
            self.get_profile_dict_from_db(data['profile_id']),
            self.get_profile_data(profile_id=data['profile_id']),
        )
        self.check_business_mapping({
            0: TEST_SIMLE_USERID,
            TEST_APP_ID: TEST_SIMLE_USERID,
        })

    def test_update_existing_profile_with_business_userid(self):
        """
        Профиль уже есть, у него business_userid.
        Проверим, что в bamt добавилось новое значение.
        """
        self.set_task_data()
        self.add_profile_to_db(self.get_profile_data(userid=TEST_BUSINESS_USERID))
        self.add_business_userid_to_db(app_id=TEST_APP_ID_2, userid=TEST_SIMLE_USERID)

        res = self.app_client.post('/api/task/%s/bind' % TEST_TASK_ID)
        data = self.get_ok_response(res)

        self.assertDictEqual(
            self.get_profile_dict_from_db(data['profile_id']),
            self.get_profile_data(profile_id=data['profile_id']),
        )
        self.check_business_mapping({
            TEST_APP_ID_2: TEST_SIMLE_USERID,
            TEST_APP_ID: TEST_SIMLE_USERID,
        })

    def test_add_conflicting_profile(self):
        """
        Уже есть профиль с простым userid, business_userid.
        Данные в task приводят нас к конфликту, когда нужно удалить один из профилей.
        """
        self.add_profile_to_db(self.get_profile_data(
            userid=TEST_SIMLE_USERID,
            profile_id=1000,
        ))
        self.add_profile_to_db(self.get_profile_data(
            userid=TEST_BUSINESS_USERID,
            profile_id=2000,
        ))
        self.add_business_userid_to_db(app_id=TEST_APP_ID_2, userid=TEST_SIMLE_USERID_2)

        self.set_task_data(userid=TEST_SIMLE_USERID)

        res = self.app_client.post('/api/task/%s/bind' % TEST_TASK_ID)
        data = self.get_ok_response(res)

        eq_(data['profile_id'], 2000)

        eq_(self.get_profile_from_db(1000), None)

        self.assertDictEqual(
            self.get_profile_dict_from_db(2000),
            self.get_profile_data(profile_id=2000),
        )
        self.check_business_mapping({
            TEST_APP_ID_2: TEST_SIMLE_USERID_2,
            TEST_APP_ID: TEST_SIMLE_USERID,
        })

    def test_task_not_found(self):
        rv = self.app_client.post('/api/task/%s/bind' % TASK_ID2)

        eq_(rv.status_code, 404)
        error = json.loads(rv.data)['error']
        eq_(error['name'], 'task-not-found')
        eq_(error['description'], 'Task with the given task_id not found')

    def test_uid_arg__no_grants(self):
        self.set_task_data()
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'task-get',
                'profile-create',
                'task-allow_auth',
            ],
        )

        rv = self.app_client.post(
            '/api/task/%s/bind' % TEST_TASK_ID,
            data={'uid': 2},
        )

        eq_(rv.status_code, 403)
        error = json.loads(rv.data)['error']
        eq_(error['name'], 'access-denied')
        eq_(
            error['description'],
            'Missing grants [task-uid] from Consumer(ip = 127.0.0.1, name = dev, matching_consumers = dev)',
        )

    def test_uid(self):
        self.set_task_data(uid=None, task_id=TASK_ID2)

        rv = self.app_client.post('/api/task/%s/bind' % TASK_ID2)

        eq_(rv.status_code, 400)
        error = json.loads(rv.data)['error']
        eq_(error['name'], 'uid.empty')
        eq_(error['description'], '"uid" should be passed through either parameters or task')

    def test_subscription__ok(self):
        self.set_task_data()

        rv = self.app_client.post(
            '/api/task/%s/bind' % TEST_TASK_ID,
            data={'subscription_id': 2},
        )

        eq_(rv.status_code, 200)
        profile_id = json.loads(rv.data)['profile_id']

        query = select([st]).where(
            and_(
                st.c.profile_id == profile_id,
                st.c.sid == 2,
            ),
        )
        records = self.engine.execute(query).fetchall()
        eq_(len(records), 1)
        eq_(records[0].value, 1)

    def test_negative_subscription(self):
        self.set_task_data()

        rv = self.app_client.post(
            '/api/task/%s/bind' % TEST_TASK_ID,
            data={'subscription_id': -1},
        )

        eq_(rv.status_code, 400)
        error = json.loads(rv.data)['error']
        eq_(error['name'], 'subsciption_id-invalid')
        eq_(error['description'], 'subscription_id should be unsigned integer')

    def test_allow_auth__no_grants(self):
        self.set_task_data()
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'task-get',
                'profile-create',
            ],
        )

        rv = self.app_client.post(
            '/api/task/%s/bind' % TEST_TASK_ID,
            data={'allow_auth': 1},
        )

        eq_(rv.status_code, 403)
        error = json.loads(rv.data)['error']
        eq_(error['name'], 'access-denied')
        eq_(
            error['description'],
            'Missing grants [task-allow_auth] from Consumer(ip = 127.0.0.1, name = dev, matching_consumers = dev)',
        )

    def test_invalid_allow_auth(self):
        self.set_task_data()

        rv = self.app_client.post(
            '/api/task/%s/bind' % TEST_TASK_ID,
            data={'allow_auth': 2},
        )

        eq_(rv.status_code, 400)
        error = json.loads(rv.data)['error']
        eq_(error['name'], 'allow_auth-invalid')
        eq_(error['description'], 'allow_auth should be 0 or 1')

    def test_create_profile__fail(self):
        self.set_task_data(provider=dict(id=999999, code='unknow', name='unknown'))

        rv = self.app_client.post('/api/task/%s/bind' % TEST_TASK_ID)

        eq_(rv.status_code, 400)
        error = json.loads(rv.data)['error']
        eq_(error['name'], 'task-invalid')
        eq_(error['description'], 'Unknown provider')


class TestGetTask(_BaseTaskViewTestCase):
    def setUp(self):
        super(TestGetTask, self).setUp()

        task = self._build_task(TEST_TASK_ID)
        save_task_to_redis(self.redis, TEST_TASK_ID, task)

        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'task-get',
                'no-cred-read-token-application:' + MAIL_RU_APPLICATION_NAME1,
            ],
        )

    def test_ok(self):
        rv = self.app_client.get('/api/task/%s' % TEST_TASK_ID)

        eq_(rv.status_code, 200)
        expected_response = {
            'task_id': TEST_TASK_ID,
            'created': TEST_TASK_STARTED,
            'finished': TEST_TASK_FINISHED,
            'consumer': TEST_CONSUMER,
            'yandexuid': TEST_YANDEXUID,
            'profile': {
                'userid': SIMPLE_USERID1,
                'username': 'arji.barjanian@mail.ru',
                'firstname': 'Arji',
                'lastname': 'Barjanian',
                'birthday': '1988-12-23',
                'gender': 'm',
                'email': 'arji.barjanian@mail.ru',
                'links': ['http://my.mail.ru/mail/arji.barjanian'],
                'provider': {'id': MailRu.id, 'code': MailRu.code, 'name': 'mailru'},
                'avatar': {
                    '45x0': 'http://avt.appsmail.ru/mail/arji.barjanian/_avatarsmall',
                    '90x0': 'http://avt.appsmail.ru/mail/arji.barjanian/_avatar',
                },
            },
            'token': {
                'application': MAIL_RU_APPLICATION_NAME1,
                'value': APPLICATION_TOKEN1,
                'expires': 1408104159,
                'scope': '',
                'application_attributes': {
                    'id': MAIL_RU_APPLICATION_NAME1,
                    'third_party': False,
                },
            },
        }
        eq_(json.loads(rv.data), expected_response)

    def test_not_found(self):
        rv = self.app_client.get('/api/task/notfound')

        eq_(rv.status_code, 404)
        error = json.loads(rv.data)['error']
        eq_(error['name'], 'task-not-found')
        eq_(error['description'], 'Task with the given task_id not found')


class TestDeleteTask(_BaseTaskViewTestCase):
    def setUp(self):
        super(TestDeleteTask, self).setUp()

        task = self._build_task(task_id=TEST_TASK_ID)
        save_task_to_redis(self._fake_redis, TEST_TASK_ID, task)

        self.grants_config.add_consumer('dev', networks=['127.0.0.1'], grants=['task-delete'])

    def test_ok(self):
        rv = self.app_client.delete('/api/task/%s' % TEST_TASK_ID)

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'deleted': True})

    def test_not_found(self):
        rv = self.app_client.delete('/api/task/notfound')

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'deleted': False})
