# -*- coding: utf-8 -*-
import json
import random
import string

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api import forms
from passport.backend.api.common.processes import PROCESS_RESTORE
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.core.conf import settings
from passport.backend.core.host.host import get_current_host
from passport.backend.core.redis_manager.redis_manager import (
    get_redis_mgr,
    RedisError,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.exceptions import TrackNotFoundError
from passport.backend.core.tracks.model import (
    AuthTrack,
    TrackField,
    TrackFlagField,
)
from passport.backend.core.tracks.utils import create_track_id


eq_ = iterdiff(eq_)


@with_settings_hosts(
    TRACK_TTL=10,
    TRACK_TTL_OFFSET=2,
    OAUTH_TOKEN_TO_TRACK_SCOPE='scope',
)
class TestTracks(BaseTestViews):
    """
    Проверяет что в редис отправляются команды о сохранении полей в трэк
    """

    def setUp(self):
        self.track_type = 'register'
        self.common_track_data = {
            'track_type': 'register',
            'created': TimeNow(),
            'consumer': 'dev',
        }
        self.extra_track_data = {
            'language': 'ru',
            'display_language': 'ru',
            'country': 'ru',
            'retpath': 'http://ya.ru/retpath',
            'origin': 'origin',
            'service': 'serv',
            'frontend_state': u'{"process":"2fa_enable","field":"значение"}',
        }
        self.all_track_data = dict(self.common_track_data, **self.extra_track_data)

        self.track_id = create_track_id()

        self.env = ViewsTestEnvironment(mock_redis=True)
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'track': ['*']}))

        self.host_id = get_current_host().get_id()
        self.redis_manager = get_redis_mgr(self.host_id)

        self.pipeline_execute_mock = mock.Mock(return_value=[0, None, {}])
        self.pipeline_mock = mock.Mock()
        self.pipeline_mock.parent = self.redis_manager
        self.pipeline_mock.execute = self.pipeline_execute_mock
        self.redis_manager.pipeline = mock.Mock(return_value=self.pipeline_mock)
        self.redis_manager.hgetall = mock.Mock(return_value={})
        self.redis_manager.get = mock.Mock(return_value=1)

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.redis_manager
        del self.pipeline_execute_mock
        del self.pipeline_mock

    def pipe_call_args_list(self):
        return [
            (name, args)  # kwargs нигде не используются
            for name, args, kwargs in self.pipeline_mock.method_calls
            if not name.startswith('parent')  # иначе это уже вызов редиса напрямую, в обход пайпа
        ]

    def read_track_response(self, data=None):
        return [
            (5, 1, data or self.common_track_data),  # чтение трека
            ([],),  # чтение списков
        ]

    def write_track_response(self):
        return [
            (None,),  # возвращаемое значение нам не важно
        ]

    def mock_existing_track(self, data=None):
        # Если в запросе есть track_id, трек дважды читается в logs.py для получения логина и уида.
        # И только потом дело доходит до вьюхи, где он читается всегда.
        self.pipeline_execute_mock.side_effect = (
            self.read_track_response(data) * 3 +
            self.write_track_response()
        )

    def check_pipeline_calls(self, transaction_count, read_count, is_create=False, has_lists=True,
                             data_written=None, is_delete=False, version_updated=False):
        expected_call_args_list = []
        track_key = 'track:%s' % self.track_id
        track_list_keys = sorted([
            '%s:phone_operation_confirmations' % track_key,
            '%s:restore_methods_select_order' % track_key,
            '%s:suggested_logins' % track_key,
            '%s:totp_push_device_ids' % track_key,
        ])

        eq_(self.redis_manager.pipeline.call_count, transaction_count)

        # Создание
        if is_create:
            expected_call_args_list.extend([
                ('multi', ()),
                ('set', ('%s:version' % track_key, 1)),
                ('expire', ('%s:version' % track_key, 10)),
                ('hmset', (track_key, self.common_track_data)),
                ('expire', (track_key, 10)),
            ])
            if has_lists:
                for track_list_key in track_list_keys:
                    expected_call_args_list.extend([
                        ('rpush', (track_list_key, '<root>')),
                        ('expire', (track_list_key, 10)),
                    ])
            expected_call_args_list.extend([
                ('execute', ()),
            ])

        # Чтение данных
        if read_count:
            submit = [
                ('multi', ()),
                ('ttl', (track_key,)),
                ('get', ('%s:version' % track_key,)),
                ('hgetall', (track_key,)),
                ('execute', ()),
                ('multi', ()),
            ]
            for track_list_key in track_list_keys:
                submit.extend([
                    ('lrange', (track_list_key, 1, -1)),
                ])
            submit.extend([
                ('execute', ()),
            ])
            expected_call_args_list.extend(
                submit * read_count,
            )

        if data_written:
            expected_call_args_list.extend([
                ('watch', ('%s:version' % track_key,)),
                ('multi', ()),
            ])
            if version_updated:
                expected_call_args_list.extend([
                    ('incr', ('%s:version' % track_key,))
                ])
            expected_call_args_list.extend([
                ('hmset', (track_key, data_written)),
                ('execute', ()),
            ])

        if is_delete:
            expected_call_args_list.extend([
                ('multi', ()),
                ('delete', (track_key,)),
                ('delete', ('%s:version' % track_key,)),
            ])
            if has_lists:
                for track_list_key in track_list_keys:
                    expected_call_args_list.extend([
                        ('delete', (track_list_key,)),
                    ])
            expected_call_args_list.extend([
                ('execute', ()),
            ])

        eq_(self.pipe_call_args_list(), expected_call_args_list)

    def test_track_create(self):
        rv = self.env.client.post('/1/track/?consumer=dev')
        eq_(rv.status_code, 200)

        resp = json.loads(rv.data)
        ok_('id' in resp)
        self.track_id = resp['id']
        eq_(int(self.track_id[-2:], 16), self.host_id, 16)

        self.check_pipeline_calls(transaction_count=1, read_count=0, is_create=True)

    def test_track_create_with_process_name(self):
        rv = self.env.client.post('/1/track/?consumer=dev', data={'process_name': PROCESS_RESTORE})
        eq_(rv.status_code, 200)

        resp = json.loads(rv.data)
        ok_('id' in resp)
        self.track_id = resp['id']

        self.common_track_data.update(process_name=PROCESS_RESTORE)
        self.check_pipeline_calls(
            transaction_count=1,
            read_count=0,
            is_create=True,
        )

    def test_track_create_with_oauth_token(self):
        self.pipeline_execute_mock.side_effect = (
            self.write_track_response() +  # создание трека
            self.read_track_response() +
            self.write_track_response()  # запись полей трека
        )
        blackbox_response = blackbox_oauth_response(
            uid=123,
            scope=settings.OAUTH_TOKEN_TO_TRACK_SCOPE,
            login='test-login',
        )
        self.env.blackbox.set_blackbox_response_value('oauth', blackbox_response)
        rv = self.env.client.post('/1/track/?consumer=dev', data={
            'track_type': 'complete',
            'token': '123aaa',
        })
        eq_(rv.status_code, 200)

        resp = json.loads(rv.data)
        ok_('id' in resp)

        self.track_id = resp['id']
        self.common_track_data.update(track_type='complete')
        self.check_pipeline_calls(
            transaction_count=4,  # создание трека, чтение его тела и списков, и его заполнение
            read_count=1,
            is_create=True,
            data_written={'uid': 123, 'login': 'test-login'},
            version_updated=True,
        )

    def test_authorize_track_create_with_oauth_token_cannot_override_protected_fields(self):
        self.pipeline_execute_mock.side_effect = (
            self.write_track_response() +  # создание трека
            self.read_track_response() +
            self.write_track_response()  # запись полей трека
        )
        blackbox_response = blackbox_oauth_response(
            uid=123,
            scope=settings.OAUTH_TOKEN_TO_TRACK_SCOPE,
            login='test-login',
        )
        self.env.blackbox.set_blackbox_response_value('oauth', blackbox_response)
        rv = self.env.client.post('/1/track/?consumer=dev', data={
            'track_type': 'authorize',
            'token': '123aaa',
            'uid': 456,  # вот он! 456 отличается от 123
            'allow_authorization': '1',
            'allow_oauth_authorization': '1',
            'is_captcha_recognized': '1',
            'foo': 'bar',
        })
        eq_(rv.status_code, 200)

        resp = json.loads(rv.data)
        ok_('id' in resp)

        self.track_id = resp['id']
        self.common_track_data.update(track_type='authorize')
        self.check_pipeline_calls(
            transaction_count=1,  # создание трека, чтение его тела и списков, и его заполнение
            read_count=0,
            is_create=True,
        )

    def test_track_create_with_oauth_errors(self):
        blackbox_response = blackbox_oauth_response(status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS)
        self.env.blackbox.set_blackbox_response_value('oauth', blackbox_response)
        rv = self.env.client.post('/1/track/?consumer=dev', data={
            'track_type': 'complete',
            'token': 'eeeeerrr',
        })
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'OAuth token is invalid',
                          u'code': u'invalidoauthtoken'}]})
        ok_('execute' not in self.pipe_call_args_list())

        rv = self.env.client.post('/1/track/?consumer=dev', data={
            'track_type': 'complete',
        })
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': 'token',
                          u'message': u'Missing value',
                          u'code': u'missingvalue'}]})
        ok_('execute' not in self.pipe_call_args_list())

        blackbox_response = blackbox_oauth_response(scope='wrong')
        self.env.blackbox.set_blackbox_response_value('oauth', blackbox_response)
        rv = self.env.client.post('/1/track/?consumer=dev', data={
            'track_type': 'complete',
            'token': 'aaaaa',
        })
        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'OAuth scope is invalid',
                          u'code': u'invalidoauthscope'}]})
        ok_('execute' not in self.pipe_call_args_list())

    def test_track_create_with_params(self):
        self.pipeline_execute_mock.side_effect = (
            self.write_track_response() +  # создание трека
            self.read_track_response() +
            self.write_track_response()  # запись полей трека
        )
        extra_track_data = dict(self.extra_track_data)
        extra_track_data.update({
            'device_language_sys': 'ls',
            'device_locale': 'loc',
            'device_geo_coarse': 'geo',
            'device_hardware_id': 'hid',
            'device_os_id': 'os',
            'device_application': 'app',
            'device_cell_provider': 'cell',
            'device_hardware_model': 'hm',
            'device_clid': 'clid',
            'device_app_uuid': 'uuid',
        })
        rv = self.env.client.post('/1/track/?consumer=dev', data=extra_track_data)
        eq_(rv.status_code, 200)

        resp = json.loads(rv.data)
        ok_('id' in resp)
        self.track_id = resp['id']
        eq_(int(self.track_id[-2:], 16), self.host_id, 16)

        self.check_pipeline_calls(
            transaction_count=4,  # создание трека, чтение его тела и списков, и его заполнение
            read_count=1,
            is_create=True,
            data_written=extra_track_data,
        )

    def test_track_get(self):
        track_data = dict(self.all_track_data, created=100)
        self.mock_existing_track(data=track_data)

        rv = self.env.client.get('/1/track/%s/?consumer=dev' % self.track_id)
        eq_(rv.status_code, 200)

        response = dict(track_data, status='ok')
        eq_(json.loads(rv.data), response)

    def test_not_existing_track_get(self):
        self.redis_manager.get = mock.Mock(side_effect=TrackNotFoundError)
        rv = self.env.client.get('/1/track/%s/?consumer=dev' % self.track_id)
        eq_(rv.status_code, 400)

    def test_track_save_bad_id(self):
        rv = self.env.client.post('/1/track/wrong_id/?consumer=dev')
        eq_(rv.status_code, 400)

    def test_track_bad_node(self):
        track_id = self.track_id[:-2] + "00"
        rv = self.env.client.get('/1/track/%s/?consumer=dev' % track_id)
        eq_(rv.status_code, 400)
        rv = self.env.client.post('/1/track/%s/?consumer=dev' % track_id)
        eq_(rv.status_code, 400)

    def test_track_save(self):
        self.mock_existing_track()

        rv = self.env.client.post('/1/track/%s/?consumer=dev' % self.track_id, data=self.extra_track_data)
        eq_(rv.status_code, 200)

        self.check_pipeline_calls(
            transaction_count=7,  # 3 * 2 на чтение, 1 на запись
            read_count=3,
            data_written=self.extra_track_data,
        )

    def test_track_save__with_blank_fields__writes_blank_values_to_track(self):
        """
        Пустое значение в трэк должно записываться как ''.
        Это ранее использовалось для "зануления" внесенного ранее значения.
        Теперь же из трека можно удалять поля "по-честному".
        """
        self.mock_existing_track()

        data = dict(self.extra_track_data)
        data['service'] = '    '
        data['origin'] = '  abc   '
        data['frontend_state'] = ''

        rv = self.env.client.post('/1/track/%s/?consumer=dev' % self.track_id, data=data)
        eq_(rv.status_code, 200)

        data['service'] = ''
        data['origin'] = 'abc'

        self.check_pipeline_calls(
            transaction_count=7,  # 3 * 2 на чтение, 1 на запись
            read_count=3,
            data_written=data,
        )

    def test_track_save_redis_error(self):
        self.pipeline_execute_mock.side_effect = RedisError
        rv = self.env.client.post('/1/track/%s/?consumer=dev' % self.track_id, data=self.extra_track_data)
        eq_(rv.status_code, 503)

    def test_track_version_changed_while_saving(self):
        self.mock_existing_track()
        self.redis_manager.get.return_value = 2

        rv = self.env.client.post('/1/track/%s/?consumer=dev' % self.track_id, data=self.extra_track_data)
        eq_(rv.status_code, 503)

    def test_track_delete(self):
        self.mock_existing_track()
        rv = self.env.client.delete('/1/track/%s/?consumer=dev' % self.track_id)
        eq_(rv.status_code, 200)

        self.check_pipeline_calls(
            transaction_count=7,  # 3 * 2 на чтение, 1 на удаление
            read_count=3,
            is_delete=True,
        )


@with_settings_hosts(
    TRACK_TTL=60,
)
class TestTracksWithFakeRedis(BaseTestViews):
    """
    Проверяет МОКИ
    """

    def setUp(self):
        self.track_id = create_track_id()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'track': ['*']}))

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_track_create(self):
        rv = self.env.client.post('/1/track/?consumer=dev')
        eq_(rv.status_code, 200)
        resp = json.loads(rv.data)
        actual_id = resp['id']
        manager = self.env.track_manager.get_manager()
        manager.read(actual_id)

    def test_track_create_with_oauth_token(self):
        blackbox_response = blackbox_oauth_response(
            uid=123,
            scope=settings.OAUTH_TOKEN_TO_TRACK_SCOPE,
        )
        self.env.blackbox.set_blackbox_response_value('oauth', blackbox_response)
        rv = self.env.client.post('/1/track/?consumer=dev', data={
            'track_type': 'complete',
            'token': 'aaabbb',
        })
        eq_(rv.status_code, 200)
        resp = json.loads(rv.data)
        actual_id = resp['id']
        manager = self.env.track_manager.get_manager()
        track = manager.read(actual_id)
        eq_(track.track_type, 'complete')
        eq_(track.uid, '123')

    def test_track_create_workaround(self):
        for deleted_type in ('account', 'social'):
            rv = self.env.client.post('/1/track/?consumer=dev', data={
                'track_type': deleted_type,
            })
            eq_(rv.status_code, 200)
            resp = json.loads(rv.data)
            manager = self.env.track_manager.get_manager()
            track = manager.read(resp['id'])
            eq_(track.track_type, 'authorize')

    def test_track_create_with_params(self):
        expected_track_data = {
            'consumer': 'dev',
            'device_language_sys': 'ls',
            'device_locale': 'loc',
            'device_geo_coarse': 'geo',
            'device_hardware_id': 'hid',
            'device_os_id': 'os',
            'device_application': 'app',
            'device_cell_provider': 'cell',
            'device_hardware_model': 'hm',
            'device_clid': 'clid',
            'device_app_uuid': 'uuid',
            'scenario': 'scn1',
        }
        rv = self.env.client.post('/1/track/?consumer=dev', data=expected_track_data)
        eq_(rv.status_code, 200)
        resp = json.loads(rv.data)
        actual_id = resp['id']
        manager = self.env.track_manager.get_manager()
        track = manager.read(actual_id)
        expected_track_data.update({
            'consumer': 'dev',
            'track_type': 'register',
            'created': TimeNow(),
        })
        eq_(track._data, expected_track_data)

    def test_track_create_with_device_info(self):
        data = dict(
            app_id='app',
            app_platform='os',
            app_version='app_version',
            consumer='dev',
            deviceid='hid',
            device_id='device_id',
            device_name='device_name',
            ifv='ifv',
            manufacturer='manufacturer',
            model='hm',
            os_version='os_version',
            uuid='uuid',
        )
        rv = self.env.client.post('/1/track/?consumer=dev', data=data)

        eq_(rv.status_code, 200)

        rv = json.loads(rv.data)
        track_id = rv['id']

        track = self.env.track_manager.get_manager().read(track_id)

        expected = dict(
            consumer='dev',
            created=TimeNow(),
            device_app_uuid='uuid',
            device_application='app',
            device_application_version='app_version',
            device_hardware_id='hid',
            device_hardware_model='hm',
            device_id='device_id',
            device_ifv='ifv',
            device_manufacturer='manufacturer',
            device_name='device_name',
            device_os_id='os',
            device_os_version='os_version',
            track_type='register',
        )
        eq_(track._data, expected)

    def test_track_save_errors(self):
        rv = self.env.client.post('/1/track/%s/?consumer=dev' % self.track_id, data={})
        eq_(rv.status_code, 400)

        rv = self.env.client.post('/1/track/%s/?consumer=dev' % "bad_id", data={})
        eq_(rv.status_code, 400)

    def test_track_save(self):
        """Запишем в трек кое-что и проверим что оно там есть"""

        manager, track_id = self.env.track_manager.get_manager_and_trackid()
        rv = self.env.client.post(
            '/1/track/%s/?consumer=dev' % track_id,
            data={
                'language': 'ru',
                'origin': 'orig',
                'device_language_sys': 'l_sys',
                'device_os_id': 'os',
                'scenario': 'scn1',
            },
        )
        eq_(rv.status_code, 200)
        track = manager.read(track_id)
        # Проверяем что записали в трек
        eq_(track.language, 'ru')
        eq_(track.origin, 'orig')
        eq_(track.device_language_sys, 'l_sys')
        eq_(track.device_os_id, 'os')
        eq_(track.scenario, 'scn1')

    def test_track_save_device_info(self):
        data = dict(
            app_id='app',
            app_platform='os',
            app_version='app_version',
            consumer='dev',
            deviceid='hid',
            device_id='device_id',
            device_name='device_name',
            ifv='ifv',
            manufacturer='manufacturer',
            model='hm',
            os_version='os_version',
            uuid='uuid',
        )
        track_manager, track_id = self.env.track_manager.get_manager_and_trackid()

        rv = self.env.client.post('/1/track/%s/?consumer=dev' % track_id, data=data)

        eq_(rv.status_code, 200)

        track = track_manager.read(track_id)
        expected = dict(
            consumer='dev',
            created=TimeNow(),
            device_app_uuid='uuid',
            device_application='app',
            device_application_version='app_version',
            device_hardware_id='hid',
            device_hardware_model='hm',
            device_id='device_id',
            device_ifv='ifv',
            device_manufacturer='manufacturer',
            device_name='device_name',
            device_os_id='os',
            device_os_version='os_version',
            track_type='register',
        )
        eq_(track._data, expected)

    def test_track_resave(self):
        """
        Повторная запись в трек должна менять значения полей вне зависимости от новых значений
        @see PASSP-4288
        """
        manager, track_id = self.env.track_manager.get_manager_and_trackid()
        params = {
            'language': 'ru',
            'origin': 'orig',
            'device_language_sys': 'l_sys',
            'device_os_id': 'os',
        }
        # Сначала запишем кое-что
        rv = self.env.client.post('/1/track/%s/?consumer=dev' % track_id, data=params)
        eq_(rv.status_code, 200)

        # Запишем новые данные
        params.update(language='en')
        rv = self.env.client.post('/1/track/%s/?consumer=dev' % track_id, data=params)
        eq_(rv.status_code, 200)

        # Проверим что записалось
        track = manager.read(track_id)
        # Неизмененные поля
        eq_(track.origin, 'orig')
        eq_(track.device_language_sys, 'l_sys')
        eq_(track.device_os_id, 'os')
        # Поля с изменениями
        eq_(track.language, 'en')

    def test_track_save_and_resave_all_fields(self):
        """test a la functional"""

        expected_fields = {
            'track_type': 'register',
            'consumer': 'dev',
        }

        # Поля с заданным набором значений и умными валидаторами
        valid_param_values = {
            'display_language': ['ru', 'en', 'uk', 'tr'],
            'language': ['ru', 'be', 'kk', 'tt', 'uk', 'az', 'en', 'tr', 'hy', 'ka', 'ro'],
            'country': ['ru', 'us', 'ua', 'tr'],
            'retpath': ['//ya.ru', 'http://yandex.com'],
        }

        def get_random_valid_params():
            return dict(
                (name, random.choice(valid_param_values[name]))
                for name in valid_param_values
            )

        # Исследуем структуру модели Трека и составим списки полей - текстовых и булевых
        text_fields = [
            field_name for field_name in AuthTrack.__dict__
            if (
                field_name in forms.SaveTrackForm.fields and
                field_name not in valid_param_values and
                isinstance(AuthTrack.__dict__[field_name], TrackField)
            )
        ]
        flag_fields = [field_name for field_name in AuthTrack.__dict__ if (
            field_name in forms.SaveTrackForm.fields and
            isinstance(AuthTrack.__dict__[field_name], TrackFlagField)
        )]

        # Помощники
        english_alphabet = string.ascii_lowercase

        def random_text(length):
            return ''.join(random.choice(english_alphabet) for i in range(length))

        def random_bool():
            random.choice(['1', '0'])

        def fill_text_fields_random_data(field_list):
            return {name: random_text(random.randint(0, 100)) for name in field_list}

        def get_random_flag_fields(field_list):
            return {name: random_bool() for name in field_list}

        # Подготовимся
        manager, track_id = self.env.track_manager.get_manager_and_trackid()

        # Первый набор параметров. Поехали!
        params = get_random_valid_params()
        # Исключим те параметры что уже использованы
        for key, value in params.items():
            valid_param_values[key].remove(value)

        params.update(fill_text_fields_random_data(text_fields))
        flags = get_random_flag_fields(flag_fields)
        params.update(flags)
        rv = self.env.client.post('/1/track/%s/?consumer=dev' % track_id, data=params)
        eq_(rv.status_code, 200)

        # Проверим что все записалось в точности
        track_data = manager.read(track_id)._data.copy()
        expected_data = params.copy()
        expected_data.update(expected_fields)
        ok_(track_data.pop('created'), '`created` track field is not present')
        eq_(track_data, expected_data)

        # Запишем новые данные в трек
        new_params = get_random_valid_params()
        new_params.update(fill_text_fields_random_data(text_fields))
        # Инвертируем ВСЕ флаги в новом наборе параметров
        new_params.update(dict((key, '0' if value == '1' else '1') for key, value in flags.items()))
        rv = self.env.client.post('/1/track/%s/?consumer=dev' % track_id, data=new_params)
        eq_(rv.status_code, 200)

        # Проверим что все ПЕРЕзаписалось
        track_data = manager.read(track_id)._data.copy()
        expected_data = new_params.copy()
        expected_data.update(expected_fields)
        ok_(track_data.pop('created'), '`created` track field is not present')
        eq_(track_data, expected_data)

    def test_track_get(self):
        manager, track_id = self.env.track_manager.get_manager_and_trackid()
        rv = self.env.client.get('/1/track/%s/?consumer=dev' % track_id)
        eq_(rv.status_code, 200)
        eq_(manager.read(track_id).track_type, 'register')

    def test_track_get_with_masked_fields(self):
        manager, track_id = self.env.track_manager.get_manager_and_trackid()
        with manager.transaction(track_id).rollback_on_error() as track:
            track.phone_confirmation_code = '1235'
            track.phone_confirmation_sms = 'sms sms'
            track.session = 'session'
            track.sslsession = 'ssl'
            track.totp_pin = '4527'
            track.totp_app_secret = 'appsecret'
        rv = self.env.client.get('/1/track/%s/?consumer=dev' % track_id)
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'track_type': 'register',
                'consumer': 'dev',
                'created': TimeNow(),
                'phone_confirmation_code': '*****',
                'phone_confirmation_sms': '*****',
                'session': '*****',
                'sslsession': '*****',
                'totp_pin': '*****',
                'totp_app_secret': '*****',
            },
        )

    def test_track_delete(self):
        manager, track_id = self.env.track_manager.get_manager_and_trackid()
        rv = self.env.client.delete('/1/track/%s/?consumer=dev' % track_id)
        eq_(rv.status_code, 200)
        self.assertRaises(TrackNotFoundError, manager.read, track_id)
