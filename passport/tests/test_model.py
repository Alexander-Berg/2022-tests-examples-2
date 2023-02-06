# -*- coding: utf-8 -*-
import json
import time
import unittest

import mock
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.test.consts import (
    TEST_CONFIRMATION_CODE1,
    TEST_PHONE_NUMBER1,
    TEST_UNIXTIME1,
    TEST_UNIXTIME2,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.exceptions import TrackNotFoundError
from passport.backend.core.tracks.faker import FakeTrackManager
from passport.backend.core.tracks.fields import (
    TrackCounter,
    TrackCounterField,
    TrackField,
    TrackFieldBase,
    TrackFlagField,
    TrackJsonSerializableField,
    TrackList,
    TrackListField,
    TrackReadOnlyField,
    TrackUnixtimeField,
)
from passport.backend.core.tracks.model import (
    RegisterTrack,
    TrackBase,
)
from passport.backend.core.tracks.utils import create_track_id


class TrackModelBaseTestCase(unittest.TestCase):
    # дефолтный тип трека для создания в тестах
    track_type_to_create = 'register'
    track_class = None

    def setUp(self):
        self.manager = FakeTrackManager()
        self.manager.start()
        # Такой track_manager создаст 'register' трек для работы
        self.track_manager, self.track_id = self.manager.get_manager_and_trackid(self.track_type_to_create)
        self.track = self.track_manager.read(self.track_id)

    def tearDown(self):
        self.manager.stop()
        del self.manager
        del self.track_manager


@with_settings_hosts()
class TrackFieldsTestCase(TrackModelBaseTestCase):

    base_field = TrackFieldBase('base_field')
    field = TrackField('field')
    readonly_field = TrackReadOnlyField('ro_field')
    flag = TrackFlagField('flag')
    list_field = TrackListField('suggested_logins')
    counter = TrackCounterField('counter')
    json_field = TrackJsonSerializableField('json_field')
    unixtime_field = TrackUnixtimeField('unixtime_field')

    def setUp(self):
        super(TrackFieldsTestCase, self).setUp()
        self._data = {}
        self._lists = {}
        self._counters = {}

    def test_base_field__read_or_write__raises_attribute_error(self):
        with assert_raises(AttributeError):
            self.base_field = '123'
        with assert_raises(AttributeError):
            ok_(self.base_field)

    def test_track_field__read_and_write__ok(self):
        self.field = '123'
        eq_(self._data['field'], '123')

    @raises(ValueError)
    def test_track_field__write_bad_value__error(self):
        self.field = True

    def test_read_only_field__write_value__raises_attribute_error(self):
        self._data['ro_field'] = 'abc'
        eq_(self.readonly_field, 'abc')
        with assert_raises(AttributeError):
            self.readonly_field = 'bbb'

    def test_flag_field__read_and_write_all_possible_values__ok(self):
        """Проверим что flag_field правильно обрабатывает ВСЕ допустимые значения до и после изменения"""
        eq_(self.flag, None)
        self.flag = True
        eq_(self._data['flag'], '1')
        self.flag = False
        eq_(self._data['flag'], '0')
        self.flag = None
        eq_(self.flag, None)
        ok_('flag' not in self._data)

    def test_counter__get_and_incr__ok(self):
        eq_(self.counter.get(), None)
        eq_(self.counter.get(default=0), 0)
        self.counter.incr()
        eq_(self._counters['counter'], 1)

    def test_counter__reset__ok(self):
        eq_(self.counter.get(), None)
        self.counter.incr()
        eq_(self.counter.get(), 1)
        self.counter.reset()
        ok_('counter' in self._counters)
        ok_('counter' not in self._data)
        eq_(self.counter.get(), 0)
        self.counter.incr()
        eq_(self.counter.get(), 1)

    def test_counter__set_other_counter(self):
        other_track = mock.Mock(_counters=dict(c1=2))
        other_counter = TrackCounter(other_track, 'c1')
        self.counter.incr()
        eq_(self.counter.get(), 1)
        eq_(other_counter.get(), 2)

        # Копируем значение счётчика из другого трека
        self.counter = other_counter
        eq_(self.counter.get(), 2)

        # Изменения в счётчике не влияют на его копии
        other_counter.incr()
        eq_(self.counter.get(), 2)

    def test_counter__set_unkown_type(self):
        with self.assertRaises(TypeError) as assertion:
            self.counter = None

        eq_(str(assertion.exception), 'Unable to set value None (NoneType) to counter (TrackCounterField)')

    def test_list__append_get__ok(self):
        self.list_field.append('1', '2')
        ok_('suggested_logins' in self._lists)
        eq_(self._lists['suggested_logins'], ['1', '2'])
        eq_(self.list_field.get(), ['1', '2'])

    def test_list__set_other_list(self):
        other_track = mock.Mock(_lists=dict(s1=[1, 2]))
        other_list = TrackList(other_track, 's1')
        self.list_field.append(3, 4, 5)
        eq_(self.list_field.get(), [3, 4, 5])
        eq_(other_list.get(), [1, 2])

        # Копируем значение списка из другого трека
        self.list_field = other_list
        eq_(self.list_field.get(), [1, 2])

        # Изменения в счётчике не влияют на его копии
        other_list.append(3)
        eq_(self.list_field.get(), [1, 2])

    def test_list__set_unkown_type(self):
        with self.assertRaises(TypeError) as assertion:
            self.list_field = None

        eq_(str(assertion.exception), 'Unable to set value None (NoneType) to suggested_logins (TrackListField)')

    def test_json_field__write__stores_serialized_to_json_value(self):
        eq_(self.json_field, None)

        self.json_field = {'foo': [1, 2, 3]}
        eq_(self._data['json_field'], '{"foo": [1, 2, 3]}')
        eq_(self.json_field, {'foo': [1, 2, 3]})

        self.json_field = None
        eq_(self._data['json_field'], 'null')
        eq_(self.json_field, None)

    def test_unixtime__write__stores_string_value(self):
        timestamp = 123456.78
        self.unixtime_field = timestamp
        eq_(self._data['unixtime_field'], '123456.78')
        eq_(self.unixtime_field, timestamp)

    @raises(ValueError)
    def test_unixtime__write_none__error(self):
        self.unixtime_field = None

    @raises(ValueError)
    def test_unixtime__write_bad_value__error(self):
        self.unixtime_field = 'bad-float-value'

    @raises(ValueError)
    def test_unixtime__read_bad_string__error(self):
        self._data['unixtime_field'] = 'bad-float-value'
        self.unixtime_field

    def test_unixtime__read_none__error(self):
        self._data['unixtime_field'] = None
        assert_is_none(self.unixtime_field)

    def test_field_access_on_type_object__works(self):
        class_field_types = [
            (TrackFieldsTestCase.field, TrackField),
            (TrackFieldsTestCase.readonly_field, TrackReadOnlyField),
            (TrackFieldsTestCase.flag, TrackFlagField),
            (TrackFieldsTestCase.list_field, TrackListField),
            (TrackFieldsTestCase.counter, TrackCounterField),
            (TrackFieldsTestCase.json_field, TrackJsonSerializableField),
            (TrackFieldsTestCase.unixtime_field, TrackUnixtimeField),
        ]
        for class_field, type_ in class_field_types:
            eq_(type(class_field), type_)


@with_settings_hosts()
class SimpleTrackModelTestCase(TrackModelBaseTestCase):
    track_type_to_create = 'register'
    track_class = RegisterTrack

    @raises(AttributeError)
    def test_unknown_field(self):
        self.track.some_strange_field = 'test'

    def test_snapshot(self):
        snapshot = self.track.snapshot()
        eq_(snapshot.track_id, self.track.track_id)
        eq_(snapshot._data, self.track._data)
        eq_(snapshot._counters, self.track._counters)
        eq_(snapshot._lists, self.track._lists)
        ok_(snapshot is not self.track)

    def test_repr(self):
        eq_(
            repr(self.track),
            '<RegisterTrack: %s>' % self.track.track_id,
        )

    def test_track_unicode_conversion(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms = 'русский'

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_sms, u'русский')

    def test_read__wrong_track_type__raises_value_error(self):
        """Если в треке записано непонятно что в поле track_type,
        то десериализатор трека не сможет найти нужный класс для разбора данных"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track._data['track_type'] = 'unknown'

        with assert_raises(ValueError):
            self.track_manager.read(self.track_id)


@with_settings_hosts()
class GenericTrackModelTestCase(TrackModelBaseTestCase):
    """
    Здесь описаны тесты общего функционала трека на примере трека для авторизации.
    Запись и чтение полей разных типов, вызов ошибок в случае передачи неверных данных и тп.
    """

    track_type_to_create = 'authorize'

    def test_counter_field__have_data_in_track__incr_continues(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track._counters['captcha_generate_count'] = 4

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.captcha_generate_count.incr()

        track = self.track_manager.read(self.track_id)
        eq_(track._counters['captcha_generate_count'], 5)

    def test_parse__with_unexpected_field__raises_attribute_error(self):
        data = {
            'uid': '12345',
            'lalala': 'something-unexpected',
        }
        track = self.track_manager.read(self.track_id)
        with assert_raises(AttributeError):
            track.parse(data)

    def test_model__read_track_fields__track_not_modified_and_no_save_action(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = '12345'
            track.have_password = True

        redis_node = mock.Mock()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            self.track_manager.redis_track_managers = mock.Mock()
            self.track_manager.redis_track_managers.get.return_value = redis_node

            ok_(track.have_password)
            eq_(track.uid, '12345')

        eq_(redis_node.pipeline.call_count, 0)

    def test_parse__trackfield_and_flagfield__ok(self):
        data = {
            'have_password': True,
            'uid': '12345',
        }
        track = self.track_manager.read(self.track_id)
        track.have_password = False
        track.parse(data)
        eq_(track.uid, '12345')
        ok_(track.have_password)

    @raises(AttributeError)
    def test_parse__with_wrong_field_type__raises_attribute_error(self):
        data = {
            'have_password': True,
            'captcha_generate_count': '123',  # Ожидается число
        }
        track = self.track_manager.read(self.track_id)
        track.parse(data)

    def test_read__existing_track__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = '1234'
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, '1234')

    @raises(TrackNotFoundError)
    def test_read__not_existing_track__raises_error(self):
        self.track_manager.read(create_track_id())

    def test_logout_checkpoint_timestamp(self):
        """
        Проверим свойство logout_checkpoint_timestamp.
        Оно должно возрващать время создания трека, если не
        было задано поле password_verification_passed_at. Иначе возвращать
        значение поля password_verification_passed_at.
        """
        track = self.track_manager.read(self.track_id)
        eq_(track.logout_checkpoint_timestamp, TimeNow())

        expected = 123456789
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.password_verification_passed_at = expected
        track = self.track_manager.read(self.track_id)
        eq_(track.logout_checkpoint_timestamp, expected)


@with_settings_hosts()
class TrackMetaclassTestCase(TrackModelBaseTestCase):

    def test_sensitive_fields(self):
        """
        Проверяем, что только поля модели трека с отметкой "секретные"
        попадают в список секретных полей.
        """
        model = type(
            'MockTrackModel',
            (TrackBase,),
            {
                'public_field': TrackField('public'),
                'sensitive_field': TrackField('secret', is_sensitive=True),
            },
        )
        track = model(self.track_id)
        eq_(
            track.sensitive_fields,
            {'sensitive_field'},
        )

    def test_protected_fields(self):
        model = type(
            'MockTrackModel',
            (TrackBase,),
            {
                'public_field': TrackField('public'),
                'protected_field': TrackField('secret', allow_edit_concurrently=False),
            },
        )
        track = model(self.track_id)
        eq_(
            track.concurrent_protected_fields,
            {'protected_field'},
        )


TEST_VALUE = '123-456! hash$salt.bla:bla_bla'
TEST_JSON = {"json": "lalala", "numbers": 42, "bool": None}
TEST_LIST = [1, 'second', True]


class GenericTrackModelTestMixin(object):
    """
    Базовый класс для тестирования разных наборов полей для разных классов трека.
    По заданным спискам с именами полей разных типов проводит тестирование операций
    чтения и записи с подходящими для данного типа поля значениями.
    """

    track_type_to_create = 'universal'
    field_names = ()
    flag_field_names = ()
    counter_field_names = ()
    time_field_names = ()
    json_field_names = ()
    list_field_names = ()
    concurrent_protected_field_names = ('uid',)

    def assert_empty_track(self):
        """Проверяет, что трек еще пуст"""
        eq_(self.track._data['created'], TimeNow())
        eq_(self.track._data['track_type'], self.track_type_to_create)
        eq_(self.track.concurrent_protected_fields, set(self.concurrent_protected_field_names))

        for field_name in self.field_names:
            ok_(field_name not in self.track._data)

        for field_name in self.flag_field_names:
            ok_(field_name not in self.track._data)

        for field_name in self.counter_field_names:
            ok_(field_name not in self.track._counters)

    def get_unique_track_field_value(self, field_name, value):
        """Собираем уникальное значение для записи в строковые поля трека"""
        return '%s=%s' % (field_name, value)

    def get_unique_flag_field_value(self, field_name):
        """Собираем уникальное значение для записи в булевы поля трека"""
        return len(field_name) % 2

    def get_unique_counter_field_value(self, field_name):
        """Собираем уникальное значение для записи в поля-счетчики трека"""
        return (len(field_name) % 4) + 1

    def get_unique_json_field_value(self, field_name, base_value):
        value = base_value.copy()
        value[field_name] = 'yes'
        return value

    def get_unique_list_field_value(self, field_name, base_value):
        value = list(base_value)
        value.append(field_name)
        return value

    def write_to_track_fields(self, value):
        """Записывает уникальные значения во все строковые поля трека"""
        for field_name in self.field_names:
            # Пустое значение в треке
            default_value = getattr(self.track, field_name)
            ok_(default_value is None)
            value_to_track = self.get_unique_track_field_value(field_name, value)
            setattr(self.track, field_name, value_to_track)

    def write_to_flag_fields(self):
        """Записывает уникальные значения во все булевы поля трека"""
        for field_name in self.flag_field_names:
            # Пустое значение в треке
            default_value = getattr(self.track, field_name)
            ok_(default_value is None)
            # Записываем в поле True или False
            value_to_track = bool(self.get_unique_flag_field_value(field_name))
            setattr(self.track, field_name, value_to_track)

    def write_to_counter_fields(self):
        """Увеличивает все поля-счетчики в треке некоторое число раз"""
        for field_name in self.counter_field_names:
            counter = getattr(self.track, field_name)
            # Пустое значение в треке
            default_value = counter.get()
            ok_(default_value is None, 'default value of {} is {}'.format(field_name, default_value))
            # Увеличиваем счетчик несколько раз
            value_to_track = self.get_unique_counter_field_value(field_name)
            for i in range(value_to_track):
                counter.incr()
                expected_value = i + 1
                value = self.track._counters[field_name]
                eq_(value, expected_value, [field_name, value, expected_value])

    def write_to_time_fields(self, numeric_value):
        """Записывает уникальные значения во все поля трека, используемые для хранения времени(timestamp)"""
        for index, field_name in enumerate(self.time_field_names):
            # Пустое значение в треке
            default_value = getattr(self.track, field_name)
            ok_(default_value is None)
            # Записываем в трек уникальное число
            setattr(self.track, field_name, numeric_value + index)

    def write_to_json_fields(self, json_ready_value):
        """Записывает уникальное значение в json-поля трека"""
        for field_name in self.json_field_names:
            # Пустое значение в треке
            default_value = getattr(self.track, field_name)
            ok_(default_value is None)
            # Пишем в трек словарь, сериализация происходит под капотом JsonTrackField
            value_to_track = self.get_unique_json_field_value(field_name, json_ready_value)
            setattr(self.track, field_name, value_to_track)

    def write_to_list_fields(self, list_value):
        for field_name in self.list_field_names:
            list_field = getattr(self.track, field_name)
            # Пустое значение в треке
            default_value = list_field.get()
            eq_(default_value, list())
            # В трек записываем список значений
            value_to_track = self.get_unique_list_field_value(field_name, list_value)
            list_field.append(*value_to_track)

    def assert_counter_fields(self):
        for field_name in self.counter_field_names:
            value = self.track._counters[field_name]
            expected_value = self.get_unique_counter_field_value(field_name)
            eq_(value, expected_value, [field_name, value, expected_value])

    def assert_track_fields(self, base_value):
        for field_name in self.field_names:
            value = self.track._data[field_name]
            # Читаем из track_data строку или число
            expected_value = self.get_unique_track_field_value(field_name, base_value)
            eq_(value, expected_value, [field_name, value, expected_value])

    def assert_flag_fields(self):
        for field_name in self.flag_field_names:
            value = self.track._data[field_name]
            # Читаем из track_data '1' или '0'
            expected_value = str(self.get_unique_flag_field_value(field_name))
            eq_(value, expected_value, [field_name, value, expected_value])

    def assert_time_fields(self, expected_numeric_value):
        for index, field_name in enumerate(self.time_field_names):
            value = self.track._data[field_name]
            expected_value = expected_numeric_value + index
            eq_(value, expected_value, [field_name, value, expected_value])

    def assert_json_fields(self, base_expected_value):
        for field_name in self.json_field_names:
            value = self.track._data[field_name]
            # Читаем из track_data строку
            expected_value = self.get_unique_json_field_value(field_name, base_expected_value)
            expected_value = json.dumps(expected_value)
            eq_(value, expected_value, [field_name, value, expected_value])

    def assert_list_fields(self, base_list_value):
        for field_name in self.list_field_names:
            value = self.track._lists[field_name]
            # Читаем из трек-менеджера список
            expected_value = self.get_unique_list_field_value(field_name, base_list_value)
            expected_value = expected_value
            eq_(value, expected_value, [field_name, value, expected_value])

    def abstract_model_test(self):
        """
        Абстрактный тест. Не запускается test-runner'ом.
        Чтение, запись и снова чтение по всем полям класса трека
        """
        self.assert_empty_track()

        if self.counter_field_names:
            self.write_to_counter_fields()
            self.assert_counter_fields()

        if self.field_names:
            self.write_to_track_fields(TEST_VALUE)
            self.assert_track_fields(TEST_VALUE)

        if self.flag_field_names:
            self.write_to_flag_fields()
            self.assert_flag_fields()

        if self.time_field_names:
            current_time = time.time()
            self.write_to_time_fields(current_time)
            self.assert_time_fields(current_time)

        if self.json_field_names:
            self.write_to_json_fields(TEST_JSON)
            self.assert_json_fields(TEST_JSON)

        if self.list_field_names:
            self.write_to_list_fields(TEST_LIST)
            self.assert_list_fields(TEST_LIST)

        # TODO: Проверять точное соответствие заданному списку полей(нет лишних полей)


ACCOUNT_FIELD_NAMES = (
    'uid',
    'login',
    'domain',
    'human_readable_login',
    'machine_readable_login',
    'password_hash',
    'emails',
    'birthday',
    'secure_phone_number',
    'auth_challenge_type',
    'auth_source',
)

TOTP_FIELD_NAMES = (
    'totp_pin',
    'totp_app_secret',
    'totp_secret_encrypted',
    'correct_2fa_picture',
    'correct_2fa_picture_expires_at',
    'push_setup_secret',
)

WEBAUTHN_FIELD_NAMES = (
    'webauthn_challenge',
    'webauthn_confirmed_secret_external_id',
)

TOTP_SECRET_IDS_JSON_NAMES = (
    'totp_secret_ids',
)

TOTP_PUSH_DEVICE_IDS_LIST_NAMES = (
    'totp_push_device_ids',
)

ACCOUNT_FLAG_FIELD_NAMES = (
    'have_password',
    'is_strong_password_policy_required',
    'allow_authorization',
    'allow_oauth_authorization',
    'is_password_passed',
    'has_secure_phone_number',
    'can_use_secure_number_for_password_validation',
)

OAUTH_FLAG_FIELD_NAMES = (
    'is_oauth_token_created',
)

OAUTH_FIELD_NAMES = (
    'oauth_token_created_at',
    'payment_auth_retpath',
)

CAPTCHA_FIELD_NAMES = (
    'bruteforce_status',
    'captcha_generated_at',
    'captcha_checked_at',
    'image_captcha_type',
    'voice_captcha_type',
    'captcha_key',
    'captcha_image_url',
    'captcha_voice_url',
    'captcha_voice_intro_url',
)

CAPTCHA_FLAG_FIELD_NAMES = (
    'is_captcha_checked',
    'is_captcha_required',
    'is_captcha_recognized',
)

CAPTCHA_COUNTER_FIELD_NAMES = (
    'captcha_generate_count',
    'captcha_check_count',
    'socialreg_captcha_required_count',
)

SESSION_FIELD_NAMES = (
    'session',
    'sslsession',
    'session_created_at',
    'sessguard',
    'old_session',
    'old_ssl_session',
    'old_session_ttl',
    'old_session_age',
    'old_session_create_timestamp',
    'old_session_ip',
    'old_sessguard',
    'password_verification_passed_at',
    'login_id',
    'source_authid',
)

SESSION_JSON_FIELD_NAMES = (
    'badauth_counts',
)

REQUEST_FIELD_NAMES = (
    'country',
    'csrf_token',
    'display_language',
    'language',
    'origin',
    'process_uuid',
    'retpath',
    'service',
    'ysa_mirror_resolution',
    'js_fingerprint',
    'surface',
    'browser_id',
    'os_family_id',
    'region_id',
)

DEVICE_INFO_FIELD_NAMES = (
    'account_manager_version',
    'device_language_sys',
    'device_locale',
    'device_geo_coarse',
    'device_hardware_id',
    'device_manufacturer',
    'device_hardware_model',
    'device_os_id',
    'device_os_version',
    'device_application',
    'device_application_version',
    'device_app_uuid',
    'device_cell_provider',
    'device_clid',
    'device_ifv',
    'device_id',
    'device_name',
    'cloud_token',
    'scenario',
    'avatar_size',
    'captcha_scale_factor',
    'gps_package_name',
)

OAUTH_CLIENT_INFO_FIELD_NAMES = (
    'x_token_client_id',
    'x_token_client_secret',
    'client_id',
    'client_secret',
)

SOCIAL_FIELD_NAMES = (
    'social_broker_consumer',
    'oauth_code_challenge',
    'oauth_code_challenge_method',
    'social_output_mode',
    'social_place',
    'social_register_uid',
    'social_task_id',
    'social_track_id',
)

SOCIAL_FLAG_FIELD_NAMES = (
    'social_return_brief_profile',
)

SOCIAL_JSON_FIELD_NAMES = (
    'social_task_data',
)

CONFIRMATION_FIELD_NAMES = (
    'confirmation_code',
)

PHONE_CONFIRMATION_FIELD_NAMES = (
    'phone_confirmation_phone_number',
    'phone_confirmation_phone_number_original',
    'phone_confirmation_sms',
    'phone_confirmation_code',
    'phone_validated_for_call',
    'phone_call_session_id',
    'phone_confirmation_used_gate_ids',
    'phone_confirmation_method',
)

PHONE_CONFIRMATION_FLAG_FIELD_NAMES = (
    'phone_confirmation_is_confirmed',
    'sanitize_phone_changed_phone',
    'sanitize_phone_error',
    'phone_confirmation_send_ip_limit_reached',
    'phone_confirmation_send_count_limit_reached',
    'phone_confirmation_confirms_count_limit_reached',
    'phone_valid_for_call',
    'phone_valid_for_flash_call',
    'phone_confirmation_calls_count_limit_reached',
    'phone_confirmation_calls_ip_limit_reached',
    'enable_phonenumber_alias_as_email',
    'return_masked_number',
)

PHONE_CONFIRMATION_COUNTER_FIELD_NAMES = (
    'phone_confirmation_confirms_count',
    'phone_confirmation_sms_count',
    'sanitize_phone_count',
    'phone_confirmation_calls_count',
)

PHONE_CONFIRMATION_TIME_FIELD_NAMES = (
    'phone_confirmation_last_send_at',
    'phone_confirmation_first_send_at',
    'phone_confirmation_first_checked',
    'phone_confirmation_last_checked',
    'sanitize_phone_first_call',
    'sanitize_phone_last_call',
    'phone_confirmation_first_called_at',
    'phone_confirmation_last_called_at',
)

PHONE_CONFIRMATION_LIST_FIELD_NAMES = (
    'phone_operation_confirmations',
)

STATE_FIELD_NAMES = (
    'state',
    'frontend_state',
    'next_track_id',
    'persistent_track_id',
)

STATE_FLAG_FIELD_NAMES = (
    'is_complete_autoregistered',
    'is_complete_pdd',
    'is_complete_pdd_with_password',
    'is_force_complete_lite',
    'is_password_change',
    'is_oauth_pdd_authorization',
    'is_second_step_required',

    'is_successful_registered',
    'is_successful_completed',
    'is_successful_phone_passed',

    'social_is_callbacked',

    'is_it_registration_with_phone',
    'is_it_otp_enable',
    'is_it_otp_disable',
    'is_it_otp_restore',
    'is_otp_restore_passed',

    'is_change_password_sms_validation_required',
    'is_auth_challenge_shown',
    'is_avatar_secret_checked',
    'do_not_save_fresh_profile',

    'is_pin_checked',

    'is_force_change_password',

    'is_otp_checked',

    'is_avatar_change',

    'is_web_sessions_logout',

    'is_unsubscribed',

    'is_otp_magic_passed',
    'is_x_token_magic_passed',

    'is_key_auth_passed',

    'use_non_auth_cookies_from_track',
)

STATE_JSON_FIELD_NAMES = (
    'allowed_second_steps',
)

SUBMIT_RESPONSE_CACHE_JSON_FIELD_NAMES = (
    'submit_response_cache',
    'allowed_auth_methods',

    'antifraud_tags',
)

CHALLENGE_FIELD_NAMES = (
    'antifraud_external_id',
)

USER_INPUT_FIELD_NAMES = (
    'user_entered_login',
    'user_entered_email',
)

SUGGEST_AND_VALIDATE_COUNTER_FIELD_NAMES = (
    'suggest_login_count',
    'suggest_name_count',
    'suggest_language_count',
    'suggest_gender_count',
    'suggest_country_count',
    'suggest_timezone_count',
    'phone_number_validation_count',
    'control_questions_count',
    'login_validation_count',
    'password_validation_count',
    'hint_validation_count',
    'retpath_validation_count',
    'invalid_otp_count',
)

SUGGEST_AND_VALIDATE_TIME_FIELD_NAMES = (
    'suggest_login_first_call',
    'suggest_login_last_call',
    'login_validation_first_call',
    'login_validation_last_call',
    'password_validation_first_call',
    'password_validation_last_call',
)

SUGGEST_AND_VALIDATE_LIST_FIELD_NAMES = (
    'suggested_logins',
)

AUTO_RESTORE_BASE_FIELD_NAMES = (
    'restore_state',
    'current_restore_method',
    'last_restore_method_step',
    'restoration_key_created_at',
    'support_link_type',
)

AUTO_RESTORE_BASE_FLAG_FIELD_NAMES = (
    'is_email_check_passed',
    'has_restorable_email',
)

AUTO_RESTORE_BASE_JSON_FIELD_NAMES = (
    'restore_methods_select_counters',
)

AUTO_RESTORE_BASE_LIST_FIELD_NAMES = (
    'restore_methods_select_order',
)

AUTO_RESTORE_BASE_COUNTER_FIELD_NAMES = (
    'email_checks_count',
    'restoration_emails_count',
    'restore_2fa_form_checks_count',
)

AUTO_RESTORE_USER_INPUT_FIELD_NAMES = (
    'user_entered_question_id',
    'user_entered_question',
    'user_entered_answer',
    'user_entered_phone_number',
    'user_entered_firstname',
    'user_entered_lastname',
)

SEMI_AUTO_RESTORE_FIELD_NAMES = (
    'request_source',
)

SEMI_AUTO_RESTORE_JSON_FIELD_NAMES = (
    'questions',
    'factors',
    'events_info_cache',
)

SEMI_AUTO_RESTORE_FLAG_FIELD_NAMES = (
    'is_for_learning',
    'is_unconditional_pass',
)

OTP_RESTORE_JSON_FIELD_NAMES = (
    'failed_pins',
)

OTP_RESTORE_FLAG_FIELDS = (
    'secure_phone_entered',
)

OTP_RESTORE_COUNTER_FIELDS = (
    'secure_phone_checks_count',
    'pin_check_errors_count',
)

MAGIC_LINK_FIELD_NAMES = (
    'magic_link_code',
    'magic_link_secret',
    'magic_link_send_to',
    'magic_link_start_time',
    'magic_link_start_browser',
    'magic_link_start_location',
    'magic_link_sent_time',
    'magic_link_confirm_time',
    'magic_link_invalidate_time',
    'magic_link_message_id',
)

MAGIC_LINK_FLAG_FIELD_NAMES = (
    'require_auth_for_magic_link_confirm',
)

AUTH_FIELD_NAMES = (
    'auth_method',
    'authorization_session_policy',
    'blackbox_login_status',
    'blackbox_password_status',
    'blackbox_totp_check_time',
    'change_password_reason',
    'clean',
    'cred_status',
    'fretpath',
    'login_required_for_magic',
    'magic_qr_device_code',
    'otp',
    'session_scope',
    'x_token_status',
)

AUTH_FLAG_FIELD_NAMES = (
    'allow_scholar',

    'is_allow_otp_magic',
    'is_session_restricted',
    'dont_change_default_uid',

    'is_fuzzy_hint_answer_checked',
    'is_secure_hint_answer_checked',
    'is_short_form_factors_checked',
)

AUTH_COUNTER_FIELD_NAMES = (
    'magic_link_confirms_count',
)

ROBOT_LIKE_FIELD_NAMES = (
    'page_loading_info',
)

ROBOT_LIKE_FLAG_FIELD_NAMES = (
    'check_css_load',
    'check_js_load',
)


COOKIE_FIELD_NAMES = (
    'cookie_l_value',
    'cookie_my_value',
    'cookie_yp_value',
    'cookie_ys_value',
    'cookie_yandex_login_value',
    'cookie_yandex_gid_value',
)


MIGRATION_FLAG_FIELD_NAMES = (
    'allow_session_authorization_for_migration',
    'allow_oauth_authorization_for_migration',
)

CONFIRMATION_COUNTERS_FIELD_NAMES = (
    'invalid_email_key_count',
    'answer_checks_count',
)

EMAIL_CONFIRMATION_FIELD_NAMES = (
    'email_confirmation_address',
    'email_confirmation_code',
)

EMAIL_CONFIRMATION_COUNTER_FIELD_NAMES = (
    'email_confirmation_checks_count',
)

EMAIL_CONFIRMATION_TIME_FIELD_NAMES = (
    'email_confirmation_passed_at',
)

EMAIL_CHECK_OWNERSHIP_FIELD_NAMES = (
    'email_check_ownership_code',
)

EMAIL_CHECK_OWNERSHIP_COUNTER_FIELD_NAMES = (
    'email_ownership_checks_count',
)

EMAIL_CHECK_OWNERSHIP_FLAG_FIELD_NAMES = (
    'email_check_ownership_passed',
)

PUSH_OTP_FIELD_NAMES = (
    'push_otp',
)

PUSH_OTP_FLAG_FIELD_NAMES = (
    'allow_set_xtoken_trusted',
)

TRUST_3DS_FIELD_NAMES = (
    'payment_status',
    'paymethod_id',
    'purchase_token',
)


@with_settings_hosts()
class BaseTrackModelTestMixin(GenericTrackModelTestMixin, TrackModelBaseTestCase):
    concurrent_protected_field_names = ('uid', 'email_confirmation_address')

    field_names = (
        AUTH_FIELD_NAMES +
        AUTO_RESTORE_BASE_FIELD_NAMES +
        AUTO_RESTORE_USER_INPUT_FIELD_NAMES +
        ACCOUNT_FIELD_NAMES +
        CAPTCHA_FIELD_NAMES +
        CHALLENGE_FIELD_NAMES +
        CONFIRMATION_FIELD_NAMES +
        COOKIE_FIELD_NAMES +
        DEVICE_INFO_FIELD_NAMES +
        EMAIL_CHECK_OWNERSHIP_FIELD_NAMES +
        EMAIL_CONFIRMATION_FIELD_NAMES +
        MAGIC_LINK_FIELD_NAMES +
        OAUTH_CLIENT_INFO_FIELD_NAMES +
        OAUTH_FIELD_NAMES +
        PHONE_CONFIRMATION_FIELD_NAMES +
        REQUEST_FIELD_NAMES +
        ROBOT_LIKE_FIELD_NAMES +
        SEMI_AUTO_RESTORE_FIELD_NAMES +
        SESSION_FIELD_NAMES +
        SOCIAL_FIELD_NAMES +
        STATE_FIELD_NAMES +
        TOTP_FIELD_NAMES +
        USER_INPUT_FIELD_NAMES +
        WEBAUTHN_FIELD_NAMES +
        PUSH_OTP_FIELD_NAMES +
        TRUST_3DS_FIELD_NAMES
    )

    flag_field_names = (
        ACCOUNT_FLAG_FIELD_NAMES +
        AUTH_FLAG_FIELD_NAMES +
        AUTO_RESTORE_BASE_FLAG_FIELD_NAMES +
        CAPTCHA_FLAG_FIELD_NAMES +
        EMAIL_CHECK_OWNERSHIP_FLAG_FIELD_NAMES +
        MAGIC_LINK_FLAG_FIELD_NAMES +
        MIGRATION_FLAG_FIELD_NAMES +
        OAUTH_FLAG_FIELD_NAMES +
        OTP_RESTORE_FLAG_FIELDS +
        PHONE_CONFIRMATION_FLAG_FIELD_NAMES +
        ROBOT_LIKE_FLAG_FIELD_NAMES +
        SEMI_AUTO_RESTORE_FLAG_FIELD_NAMES +
        SOCIAL_FLAG_FIELD_NAMES +
        STATE_FLAG_FIELD_NAMES +
        PUSH_OTP_FLAG_FIELD_NAMES
    )

    counter_field_names = (
        AUTH_COUNTER_FIELD_NAMES +
        AUTO_RESTORE_BASE_COUNTER_FIELD_NAMES +
        CAPTCHA_COUNTER_FIELD_NAMES +
        CONFIRMATION_COUNTERS_FIELD_NAMES +
        EMAIL_CHECK_OWNERSHIP_COUNTER_FIELD_NAMES +
        EMAIL_CONFIRMATION_COUNTER_FIELD_NAMES +
        OTP_RESTORE_COUNTER_FIELDS +
        PHONE_CONFIRMATION_COUNTER_FIELD_NAMES +
        SUGGEST_AND_VALIDATE_COUNTER_FIELD_NAMES
    )

    time_field_names = (
        EMAIL_CONFIRMATION_TIME_FIELD_NAMES +
        PHONE_CONFIRMATION_TIME_FIELD_NAMES +
        SUGGEST_AND_VALIDATE_TIME_FIELD_NAMES
    )

    list_field_names = (
        AUTO_RESTORE_BASE_LIST_FIELD_NAMES +
        PHONE_CONFIRMATION_LIST_FIELD_NAMES +
        SUGGEST_AND_VALIDATE_LIST_FIELD_NAMES +
        TOTP_PUSH_DEVICE_IDS_LIST_NAMES
    )

    json_field_names = (
        AUTO_RESTORE_BASE_JSON_FIELD_NAMES +
        OTP_RESTORE_JSON_FIELD_NAMES +
        SEMI_AUTO_RESTORE_JSON_FIELD_NAMES +
        SESSION_JSON_FIELD_NAMES +
        SOCIAL_JSON_FIELD_NAMES +
        STATE_JSON_FIELD_NAMES +
        SUBMIT_RESPONSE_CACHE_JSON_FIELD_NAMES +
        TOTP_SECRET_IDS_JSON_NAMES
    )

    def test_model(self):
        self.abstract_model_test()


class AuthTrackModelTestMixin(BaseTrackModelTestMixin):
    track_type_to_create = 'authorize'


class RegisterTrackModelTestMixin(BaseTrackModelTestMixin):
    track_type_to_create = 'register'


class CompleteTrackModelTestMixin(BaseTrackModelTestMixin):
    track_type_to_create = 'complete'


class RestoreTrackModelTestMixin(BaseTrackModelTestMixin):
    track_type_to_create = 'restore'


@with_settings_hosts()
class TestCopyPhoneConfirmationFromOtherTrack(TrackModelBaseTestCase):
    track_type_to_create = 'universal'

    def test(self):
        old_track_id = self.manager.create_test_track(manager=self.track_manager)

        with self.track_manager.transaction(old_track_id).rollback_on_error() as old_track:
            old_track.phone_confirmation_code = TEST_CONFIRMATION_CODE1
            old_track.phone_confirmation_first_checked = TEST_UNIXTIME1
            old_track.phone_confirmation_first_send_at = TEST_UNIXTIME1
            old_track.phone_confirmation_is_confirmed = True
            old_track.phone_confirmation_last_checked = TEST_UNIXTIME2
            old_track.phone_confirmation_last_send_at = TEST_UNIXTIME2
            old_track.phone_confirmation_method = 'by_sms'
            old_track.phone_confirmation_phone_number = TEST_PHONE_NUMBER1.e164
            old_track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER1.e164
            old_track.phone_operation_confirmations.append('foo', 'bar')
            old_track.phone_confirmation_sms_count.incr()
            old_track.allow_oauth_authorization = True

        old_track = self.track_manager.read(old_track_id)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.copy_phone_confirmation_from_other_track(old_track)

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_code, TEST_CONFIRMATION_CODE1)
        eq_(track.phone_confirmation_first_checked, str(TEST_UNIXTIME1))
        eq_(track.phone_confirmation_first_send_at, str(TEST_UNIXTIME1))
        eq_(track.phone_confirmation_is_confirmed, True)
        eq_(track.phone_confirmation_last_checked, str(TEST_UNIXTIME2))
        eq_(track.phone_confirmation_last_send_at, str(TEST_UNIXTIME2))
        eq_(track.phone_confirmation_method, 'by_sms')
        eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER1.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER1.e164)
        eq_(track.phone_operation_confirmations.get(), ['foo', 'bar'])
        eq_(track.phone_confirmation_sms_count.get(), 1)
        eq_(track.allow_oauth_authorization, None)
