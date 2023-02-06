# -*- coding: utf-8 -*-
from copy import deepcopy

from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import make_clean_web_test_mixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mixins.account import GetAccountBySessionOrTokenMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_ACCOUNT_DATA,
    TEST_AUTH_HEADER,
    TEST_BIRTHDAY,
    TEST_CITY,
    TEST_CONTACT_PHONE_NUMBER_SID,
    TEST_COUNTRY_CODE,
    TEST_DISPLAY_NAME,
    TEST_FIRSTNAME,
    TEST_GENDER,
    TEST_HOST,
    TEST_LANGUAGE,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_OAUTH_SCOPE,
    TEST_PDD_DOMAIN_TEMPLATE,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_NUMBER,
    TEST_PUBLIC_ID,
    TEST_SID_ADDED,
    TEST_SOCIAL_DISPLAY_NAME,
    TEST_SOCIAL_NAME,
    TEST_SOCIAL_PROFILE_ID,
    TEST_SOCIAL_PROVIDER,
    TEST_TZ,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.models.account import Account
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.login.login import normalize_login
from passport.backend.utils.string import (
    smart_str,
    smart_text,
)


ACCOUNT_PERSON_BY_UID_GRANT = 'account_person.by_uid'
ACCOUNT_PERSON_PDD_BY_UID_GRANT = 'account_person.pdd_by_uid'
ACCOUNT_PERSON_WRITE_GRANT = 'account_person.write'
ACCOUNT_PERSON_CHANGE_LANGUAGE_GRANT = 'account_person.change_language'

TEST_NEW_TZ = 'America/New_York'
TEST_NEW_COUNTRY = 'us'
TEST_NEW_LANGUAGE = 'en'
TEST_NEW_CITY = 'New York'
TEST_NEW_GENDER = 2

TEST_ACCOUNT_INIT_DATA = deepcopy(TEST_ACCOUNT_DATA)
TEST_ACCOUNT_INIT_DATA[u'account'][u'display_name'].update(name=u'')
TEST_ACCOUNT_INIT_DATA[u'account'][u'person'].update(
    firstname='f',
    lastname='l',
    birthday='1970-01-01',
)
TEST_DISPLAY_NAME_PASSPORT_PREFIX = 'p'


def decode_gender(gender):
    return 'm' if gender == 1 else 'f'


@with_settings_hosts(
    CLEAN_WEB_API_ENABLED=False,
)
class TestUpdateAccountPersonalInfoBase(BaseBundleTestViews):
    default_url = '/1/bundle/account/person/?consumer=dev'
    http_query_args = dict(
        firstname=TEST_FIRSTNAME,
        lastname=TEST_LASTNAME,
        display_name=TEST_DISPLAY_NAME,
        gender=TEST_NEW_GENDER,
        birthday=TEST_BIRTHDAY,
        country=TEST_NEW_COUNTRY,
        city=TEST_NEW_CITY,
        language=TEST_NEW_LANGUAGE,
        timezone=TEST_NEW_TZ,
        contact_phone_number=TEST_PHONE_NUMBER.e164,
        public_id=TEST_PUBLIC_ID,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIE,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )
    mocked_grants = None

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE, is_child=False):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.initial_data),
        )
        if is_child:
            self.initial_data.setdefault('attributes', {})['account.is_child'] = '1'

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**self.initial_data),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                **self.initial_data
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({normalize_login(TEST_PUBLIC_ID): 'free'}),
        )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
        self.http_query_args.update(track_id=self.track_id)

        self.initial_data = {
            'uid': TEST_UID,
            'login': 'login',
            'firstname': 'f',
            'lastname': 'l',
            'birthdate': '1970-01-01',
            'gender': TEST_GENDER,
            'language': TEST_LANGUAGE,
            'country': TEST_COUNTRY_CODE,
            'city': TEST_CITY,
            'timezone': TEST_TZ,
        }
        self.set_blackbox_response()
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**self.initial_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account)
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='account_personal_info',
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['local_base'],
            _exclude=['uid'],
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'local_account_modification',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode'],
            event='account_modification',
            operation='updated',
        )
        self.env.statbox.bind_entry(
            'alias_update',
            _inherit_from=['local_account_modification'],
            operation='updated',
            entity='aliases',
        )
        self.env.statbox.bind_entry(
            'alias_add',
            _inherit_from=['alias_update'],
            operation='added',
        )

    def check_statbox_entries(self, firstname=TEST_FIRSTNAME, lastname=TEST_LASTNAME,
                              country_code=TEST_NEW_COUNTRY, language=TEST_NEW_LANGUAGE,
                              gender=TEST_NEW_GENDER, birthday=TEST_BIRTHDAY,
                              display_name_prefix=TEST_DISPLAY_NAME_PASSPORT_PREFIX, display_name=TEST_DISPLAY_NAME,
                              public_id=TEST_PUBLIC_ID, with_check_cookies=False):
        expected_entries = []
        if with_check_cookies:
            expected_entries.append(self.env.statbox.entry('check_cookies'))
        expected_entries.append(self.env.statbox.entry('submitted'))

        person = self.account.person
        # если срабатывает один из случаев что обновляем display_name, а на модели он дефолтный, то сбросим значение на модели,
        # чтобы запись в БД произошла: https://st.yandex-team.ru/PASSP-20807#1534414618000
        # если установлен флаг dont_use_displayname_as_public_name и аккаунт социальный - тоже самое: https://st.yandex-team.ru/PASSP-24975
        # в этом случае будет считаться что display_name создан, а не обновлен
        old_display_name = '' if person.is_display_name_empty or (self.account.is_social and person.dont_use_displayname_as_public_name) else person.display_name

        if self.account.user_defined_public_id != public_id:
            if self.account.public_id_alias.alias != normalize_login(public_id):
                if self.account.public_id_alias.alias is Undefined:
                    expected_entries.append(
                        self.env.statbox.entry(
                            'alias_add',
                            type=str(ANT['public_id']),
                            value=normalize_login(public_id),
                        ),
                    )
                else:
                    expected_entries.append(
                        self.env.statbox.entry(
                            'alias_update',
                            type=str(ANT['public_id']),
                            old=self.account.public_id_alias.alias,
                            new=normalize_login(public_id),
                        ),
                    )
                    if not self.account.public_id_alias.has_old_public_id(self.account.public_id_alias.alias):
                        expected_entries.append(
                            self.env.statbox.entry(
                                'alias_add',
                                entity='old_public_id',
                                type=str(ANT['old_public_id']),
                                old_public_id=self.account.public_id_alias.alias,
                            ),
                        )
            expected_entries.append(
                self.env.statbox.entry(
                    'local_account_modification',
                    entity='account.user_defined_public_id',
                    operation='updated' if self.account.user_defined_public_id else 'created',
                    old=self.account.user_defined_public_id or '-',
                    new=public_id,
                ),
            )

        for entity, old_value, new_value in (
            ('person.firstname', person.firstname, firstname),
            ('person.lastname', person.lastname, lastname),
            ('person.language', person.language, language),
            ('person.country', person.country, country_code),
            ('person.gender', decode_gender(person.gender), decode_gender(gender)),
            ('person.birthday', person.birthday, birthday),
            ('person.display_name', smart_text(old_display_name), smart_text(display_name_prefix + ':' + display_name)),
            ('person.fullname', '{} {}'.format(person.firstname, person.lastname), '{} {}'.format(firstname if firstname else person.firstname, lastname if lastname else person.lastname)),
        ):
            if new_value is not None and new_value != old_value:
                expected_entries.append(
                    self.env.statbox.entry(
                        'local_account_modification',
                        entity=entity,
                        old=old_value,
                        new=new_value,
                    ),
                )

        expected_entries += [
            self.env.statbox.entry(
                'local_account_modification',
                _exclude=['old'],
                entity='subscriptions',
                operation='added',
                sid=str(TEST_CONTACT_PHONE_NUMBER_SID),
            ),
        ]

        self.env.statbox.assert_has_written(expected_entries)

    def check_db_entries(self, firstname=TEST_FIRSTNAME, lastname=TEST_LASTNAME,
                         display_name=TEST_DISPLAY_NAME, display_name_prefix=TEST_DISPLAY_NAME_PASSPORT_PREFIX,
                         timezone=TEST_NEW_TZ, birthday=TEST_BIRTHDAY,
                         country_code=TEST_NEW_COUNTRY, language=TEST_NEW_LANGUAGE,
                         city=TEST_NEW_CITY, public_id=TEST_PUBLIC_ID,
                         gender=TEST_NEW_GENDER, phone_number=TEST_PHONE_NUMBER.digital,
                         query_count=1, query_count_db_central=1,
                         firstname_global=None, lastname_global=None):

        for predicate, attribute_name, value in (
            (firstname, 'person.firstname', firstname),
            (firstname_global, 'person.firstname_global', firstname),
            (lastname, 'person.lastname', lastname),
            (lastname_global, 'person.lastname_global', lastname_global),
            (display_name, 'account.display_name', '%s:%s' % (display_name_prefix, display_name)),
            (timezone, 'person.timezone', timezone),
            (birthday, 'person.birthday', birthday),
            (country_code, 'person.country', country_code),
            (language, 'person.language', language),
            (city, 'person.city', city),
            (gender, 'person.gender', decode_gender(gender)),
            (phone_number, 'person.contact_phone_number', phone_number),
            (public_id, 'account.user_defined_public_id', public_id),
        ):
            if predicate:
                self.env.db.check_db_attr(
                    TEST_UID,
                    attribute_name,
                    value,
                )
            else:
                self.env.db.check_db_attr_missing(
                    TEST_UID,
                    attribute_name,
                )

        if public_id:
            self.env.db.check(
                'aliases',
                'value',
                normalize_login(public_id),
                uid=TEST_UID,
                db='passportdbcentral',
                type=str(ANT['public_id']),
            )

        for db_name, expected_count in (
            ('passportdbcentral', query_count_db_central),
            ('passportdbshard1', query_count),
            ('passportdbshard2', 0),
        ):
            actual_count = self.env.db.query_count(db_name)
            eq_(
                actual_count,
                expected_count,
                'Expected %d queries into "%s", found %d.' % (
                    expected_count, db_name, actual_count,
                ),
            )
        # PASSP-23241 При изменении display name этот атрибут всегда удаляется
        self.env.db.check_db_attr_missing(
            TEST_UID,
            'person.dont_use_displayname_as_public_name',
        )

    def check_historydb_entries(self, display_name=TEST_DISPLAY_NAME,
                                display_name_prefix=TEST_DISPLAY_NAME_PASSPORT_PREFIX,
                                firstname=TEST_FIRSTNAME, lastname=TEST_LASTNAME,
                                firstname_global=None, lastname_global=None,
                                birthday=TEST_BIRTHDAY, gender=str(TEST_NEW_GENDER),
                                language=TEST_NEW_LANGUAGE, country=TEST_NEW_COUNTRY,
                                city=TEST_NEW_CITY, sid_added=TEST_SID_ADDED,
                                timezone=TEST_NEW_TZ, public_id=TEST_PUBLIC_ID):
        base_entries = {
            'consumer': 'dev',
            'action': 'person',
            'info.display_name': '%s:%s' % (display_name_prefix, display_name),
            'info.firstname': firstname,
            'info.firstname_global': firstname_global,
            'info.lastname': lastname,
            'info.lastname_global': lastname_global,
            'info.sex': gender,
            'info.birthday': birthday,
            'info.lang': language,
            'info.tz': timezone,
            'info.country': country,
            'info.city': city,
            'sid.add': sid_added,
            'user_agent': 'curl',
        }
        expected_entries = {
            k: v
            for k, v in base_entries.items()
            if v is not None
        }

        if public_id != self.account.user_defined_public_id:
            expected_entries['account.user_defined_public_id'] = public_id
            if normalize_login(public_id) != normalize_login(self.account.user_defined_public_id):
                if self.account.public_id_alias.alias is Undefined:
                    expected_entries['alias.public_id.add'] = normalize_login(public_id)
                else:
                    expected_entries['alias.public_id.upd'] = normalize_login(public_id)
                    if not self.account.public_id_alias.has_old_public_id(self.account.public_id_alias.alias):
                        expected_entries['alias.old_public_id.add'] = self.account.public_id_alias.alias

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_entries,
        )

        parsed_events = [event._asdict() for event in self.env.event_logger.parse_events()]
        # Смотрим только на поля с префиксом info., попутно удаляя этот префикс
        expected_parsed_entries = {}
        for k, v in expected_entries.items():
            if not k.startswith('info.'):
                continue
            k = k[5:]
            if k in ['lang', 'firstname_global', 'lastname_global']:
                continue
            v = v if v != '-' else None
            if k == 'display_name' and ':' in v:
                display_name_format_code = v.split(':')[0]
                display_name_format = {
                    's': 'social',
                    'p': 'passport',
                    't': 'template',
                }[display_name_format_code]
                expected_parsed_entries['display_name_format'] = display_name_format
                v = v.split(':')[-1]
            expected_parsed_entries[k] = v
        ok_(parsed_events)
        for event in parsed_events:
            eq_(event.get('event_type'), 'personal_data')
            eq_(
                event.get('actions'),
                [
                    dict(
                        type='personal_data',
                        changed_fields=sorted(set(expected_parsed_entries) - {'display_name_format'}),
                        **expected_parsed_entries
                    ),
                ],
            )


class TestUpdateAccountPersonalInfoView(TestUpdateAccountPersonalInfoBase,
                                        GetAccountBySessionOrTokenMixin,
                                        make_clean_web_test_mixin('test_by_track_full_ok', ['firstname', 'lastname', 'display_name', 'public_id'], statbox_action='submitted')
                                        ):
    http_method = 'post'

    def setUp(self):
        self.mocked_grants = [ACCOUNT_PERSON_WRITE_GRANT, ACCOUNT_PERSON_BY_UID_GRANT]
        super(TestUpdateAccountPersonalInfoView, self).setUp()

    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        resp = self.make_request(
            query_args={
                'uid': TEST_UID,
                field: u'Заходи дорогой, гостем будешь диваны.рф',
            },
            exclude_args=['track_id'],
        )
        self.assert_error_response(resp, ['{}.invalid'.format(field)])

    def test_by_uid_full_set_ok(self):
        resp = self.make_request(query_args=dict(uid=TEST_UID), exclude_args=['track_id'])
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries()
        self.check_statbox_entries()

    def test_by_uid_partial_set_ok(self):
        """
        Проставляем только часть атрибутов.
        """
        old_firstname = self.account.person.firstname
        resp = self.make_request(query_args={'uid': TEST_UID}, exclude_args=['track_id', 'firstname'])
        self.assert_ok_response(resp)
        self.check_db_entries(firstname=old_firstname)
        self.check_statbox_entries(firstname=None)
        self.check_historydb_entries(firstname=None)

    def test_by_uid_delete_partial_ok(self):
        resp = self.make_request(query_args=dict(uid=TEST_UID, birthday=''), exclude_args=['track_id'])
        self.assert_ok_response(resp)
        self.check_db_entries(birthday=None, query_count=2)
        self.check_statbox_entries(birthday='')
        self.check_historydb_entries(birthday='-')

    def test_by_pdd_uid_ok(self):
        self.env.grants.set_grant_list([
            ACCOUNT_PERSON_WRITE_GRANT,
            ACCOUNT_PERSON_PDD_BY_UID_GRANT,
        ])
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**dict(
                self.initial_data,
                uid=TEST_PDD_UID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            )),
        )
        resp = self.make_request(query_args=dict(uid=TEST_PDD_UID), exclude_args=['track_id'])
        self.assert_ok_response(resp)

    def test_child_restriction_error(self):
        self.set_blackbox_response(is_child=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.is_child'])

    def test_no_uid_no_track_error(self):
        resp = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(resp, ['form.invalid'])

    def test_both_uid_and_track_error(self):
        resp = self.make_request(query_args=dict(uid=TEST_UID))
        self.assert_error_response(resp, ['form.invalid'])

    def test_by_track_full_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries()
        self.check_statbox_entries(with_check_cookies=True)

    def test_by_uid_grant_missing_error(self):
        self.mocked_grants = [ACCOUNT_PERSON_WRITE_GRANT, ACCOUNT_PERSON_PDD_BY_UID_GRANT]
        self.env.grants.set_grant_list(self.mocked_grants)
        resp = self.make_request(query_args=dict(uid=TEST_UID), exclude_args=['track_id'])
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_by_track_changed_account_in_session_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 123
        resp = self.make_request()
        self.assert_error_response(resp, ['sessionid.no_uid'])

    def test_by_track_change_account_in_token_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 123
        resp = self.make_request(
            headers=dict(
                authorization=TEST_AUTH_HEADER,
            ),
            exclude_headers=['cookie'],
        )
        self.assert_error_response(resp, ['account.uid_mismatch'])

    def test_city_id_ok(self):
        resp = self.make_request(
            query_args=dict(city_id=214),
            exclude_args=['city'],
        )
        self.assert_ok_response(resp)
        self.check_db_entries(city='Долгопрудный')
        self.check_statbox_entries(with_check_cookies=True)
        self.check_historydb_entries(city='Долгопрудный')

    def test_city_and_city_id_ok(self):
        resp = self.make_request(query_args=dict(city_id=214))
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_statbox_entries(with_check_cookies=True)
        self.check_historydb_entries()

    @parameterized.expand(
        [
            TEST_SOCIAL_NAME,  # another name
            TEST_SOCIAL_DISPLAY_NAME['name'],  # same name
        ]
    )
    def test_social_display_name_from_variants(self, new_display_name):
        bb_response = blackbox_sessionid_multi_response(**dict(
            self.initial_data,
            aliases={
                'social': TEST_LOGIN,
            },
            display_name={
                'name': TEST_SOCIAL_DISPLAY_NAME['name'],
                'social': {
                    'provider': TEST_SOCIAL_PROVIDER,
                    'profile_id': TEST_SOCIAL_PROFILE_ID,
                },
                'default_avatar': '',
            },
            attributes={
                'person.dont_use_displayname_as_public_name': '1',
            },
        ))
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)
        self.account = Account().parse(
            get_parsed_blackbox_response('sessionid', bb_response),
        )

        prefix = 's:%s:%s' % (TEST_SOCIAL_PROFILE_ID, TEST_SOCIAL_PROVIDER)
        display_name = smart_str(new_display_name)

        resp = self.make_request(
            query_args=dict(
                display_name=prefix + ':' + display_name,
                is_from_variants=True,
            ),
        )
        self.assert_ok_response(resp)

        self.check_db_entries(
            display_name_prefix=prefix,
            display_name=display_name,
            query_count=2,
        )
        self.check_statbox_entries(display_name_prefix=prefix, display_name=display_name, with_check_cookies=True)
        self.check_historydb_entries(display_name_prefix=prefix, display_name=display_name)

    def test_change_display_name_fraud(self):
        resp = self.make_request(
            query_args=dict(
                display_name='s:1:fb:Заходи дорогой, www.yandex.ru',
                is_from_variants=True,
            ),
        )
        self.assert_error_response(resp, ['display_name.invalid'])

    def test_change_display_name_from_default(self):
        bb_response = blackbox_sessionid_multi_response(**dict(
            self.initial_data,
            display_name={
                'name': TEST_LOGIN,
            },
            is_display_name_empty=True,
        ))
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)
        self.account = Account().parse(
            get_parsed_blackbox_response('sessionid', bb_response),
        )

        resp = self.make_request(
            query_args=dict(
                display_name='p:%s' % TEST_LOGIN,
                is_from_variants=True,
            ),
        )
        self.assert_ok_response(resp)
        prefix, display_name = 'p', TEST_LOGIN
        self.check_db_entries(
            display_name_prefix=prefix,
            display_name=display_name,
        )
        self.check_historydb_entries(display_name_prefix=prefix, display_name=display_name)

    def test_change_display_name_not_allowed(self):
        bb_response = blackbox_sessionid_multi_response(**dict(
            self.initial_data,
            display_name={
                'name': TEST_LOGIN,
            },
            is_display_name_empty=True,
            attributes={
                'account.is_verified': True,
            },
        ))
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)
        self.account = Account().parse(
            get_parsed_blackbox_response('sessionid', bb_response),
        )

        resp = self.make_request(
            query_args=dict(
                display_name='p:%s' % TEST_LOGIN,
                is_from_variants=True,
            ),
        )
        self.assert_error_response(resp, ['display_name.update_not_allowed'])

    def test_change_display_name_from_passport_to_pdd_template(self):
        bb_response = blackbox_sessionid_multi_response(**dict(
            self.initial_data,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            display_name={
                'name': TEST_PDD_LOGIN,
                'default_avatar': '',
            },
        ))
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)
        self.account = Account().parse(
            get_parsed_blackbox_response('sessionid', bb_response),
        )

        resp = self.make_request(
            query_args=dict(
                display_name=TEST_PDD_DOMAIN_TEMPLATE,
                is_from_variants=True,
            ),
        )
        self.assert_ok_response(resp)
        prefix, display_name = TEST_PDD_DOMAIN_TEMPLATE.split(':', 1)
        self.check_db_entries(
            display_name_prefix=prefix,
            display_name=display_name,
        )
        self.check_statbox_entries(display_name_prefix=prefix, display_name=display_name, with_check_cookies=True)
        self.check_historydb_entries(display_name_prefix=prefix, display_name=display_name)

    def test_update_public_id(self):
        snapshot = self.account.snapshot()
        self.initial_data = dict(
            self.initial_data,
            aliases=dict(
                public_id='some-alias',
                portal='login',
            ),
            attributes={
                'account.user_defined_public_id': 'Some-Alias',
            },
        )
        self.set_blackbox_response()
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**self.initial_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account, snapshot)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries(query_count_db_central=3)
        self.check_statbox_entries(with_check_cookies=True)
        self.check_historydb_entries()

    def test_update_public_id_same_normalized_form(self):
        snapshot = self.account.snapshot()
        self.initial_data = dict(
            self.initial_data,
            aliases=dict(
                public_id='elon-musk',
                portal='login',
            ),
            attributes={
                'account.user_defined_public_id': 'eLoN.MusK',
            },
        )
        self.set_blackbox_response()
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**self.initial_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account, snapshot)

        resp = self.make_request(
            query_args=dict(
                firstname_global=TEST_FIRSTNAME,
                lastname_global=TEST_LASTNAME,
            ),
        )
        self.assert_ok_response(resp)
        self.check_db_entries(
            query_count_db_central=0,
            firstname_global=TEST_FIRSTNAME,
            lastname_global=TEST_LASTNAME,
        )
        self.check_statbox_entries(with_check_cookies=True)
        self.check_historydb_entries(
            firstname_global=TEST_FIRSTNAME,
            lastname_global=TEST_LASTNAME,
        )

    def test_update_public_id_change_not_allowed(self):
        snapshot = self.account.snapshot()
        self.initial_data = dict(
            self.initial_data,
            aliases=dict(
                public_id='some.alias',
                portal='login',
                old_public_id=['some.alias'],
            ),
            attributes={
                'account.user_defined_public_id': 'Some-Alias',
            },
        )
        self.set_blackbox_response()
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**self.initial_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account, snapshot)

        resp = self.make_request()
        self.assert_error_response(resp, ['public_id.update_not_allowed'])

    def test_update_public_id_has_old_public_id_but_not_public_id(self):
        snapshot = self.account.snapshot()
        self.initial_data = dict(
            self.initial_data,
            aliases=dict(
                portal='login',
                old_public_id=['some.alias'],
            ),
        )
        self.set_blackbox_response()
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**self.initial_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account, snapshot)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries(query_count_db_central=1)
        self.check_statbox_entries(with_check_cookies=True)
        self.check_historydb_entries()

    def test_occupied_public_id(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {normalize_login(TEST_PUBLIC_ID): 'occupied'},
                {normalize_login(TEST_PUBLIC_ID): '12345'},
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['public_id.not_available'])

    def test_occupied_by_self_public_id(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {normalize_login(TEST_PUBLIC_ID): 'occupied'},
                {normalize_login(TEST_PUBLIC_ID): str(TEST_UID)},
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(resp)

    @parameterized.expand(
        [
            TEST_DISPLAY_NAME,  # another name
            TEST_SOCIAL_DISPLAY_NAME['name'],  # same name
        ]
    )
    def test_unable_to_change_display_name_from_social_to_passport(self, new_display_name):
        bb_response = blackbox_sessionid_multi_response(**dict(
            self.initial_data,
            aliases={
                'social': TEST_LOGIN,
            },
            display_name={
                'name': TEST_SOCIAL_DISPLAY_NAME['name'],
                'social': {
                    'provider': TEST_SOCIAL_PROVIDER,
                    'profile_id': TEST_SOCIAL_PROFILE_ID,
                },
                'default_avatar': '',
            },
            attributes={
                'person.dont_use_displayname_as_public_name': '1',
            },
        ))
        self.env.blackbox.set_blackbox_response_value('sessionid', bb_response)
        self.account = Account().parse(
            get_parsed_blackbox_response('sessionid', bb_response),
        )

        resp = self.make_request(
            query_args=dict(
                display_name=new_display_name,
            ),
        )
        self.assert_ok_response(resp)
        prefix = 's:%s:%s' % (TEST_SOCIAL_PROFILE_ID, TEST_SOCIAL_PROVIDER)
        display_name = smart_str(new_display_name)
        self.check_db_entries(
            display_name_prefix=prefix,
            display_name=display_name,
            query_count=2,
        )
        self.check_statbox_entries(display_name_prefix=prefix, display_name=display_name, with_check_cookies=True)
        self.check_historydb_entries(display_name_prefix=prefix, display_name=display_name)


@with_settings_hosts()
class TestChangeLanguageView(BaseBundleTestViews, GetAccountBySessionOrTokenMixin):
    http_method = 'post'
    default_url = '/1/bundle/account/person/language/?consumer=dev'
    http_query_args = dict(
        language=TEST_NEW_LANGUAGE,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIE,
        user_agent=TEST_USER_AGENT,
    )

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.initial_data
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                **self.initial_data
            ),
        )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list([ACCOUNT_PERSON_CHANGE_LANGUAGE_GRANT])

        self.initial_data = {
            'uid': TEST_UID,
            'login': 'login',
            'language': TEST_LANGUAGE,
        }
        self.set_blackbox_response()
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(**self.initial_data),
            ),
        )
        self.env.db._serialize_to_eav(self.account)
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='account_change_language',
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['local_base'],
            _exclude=['uid'],
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'local_account_modification',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode'],
            event='account_modification',
            operation='updated',
        )

    def assert_statbox_ok(self, language=TEST_NEW_LANGUAGE, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('submitted'))
        if language is not None:
            entries.append(
                self.env.statbox.entry(
                    'local_account_modification',
                    entity='person.language',
                    old=self.account.person.language,
                    new=language,
                ),
            )

        self.env.statbox.assert_has_written(entries)

    def assert_db_ok(self, language=TEST_NEW_LANGUAGE, query_count=1):
        if language:
            self.env.db.check_db_attr(
                TEST_UID,
                'person.language',
                language,
            )
        else:
            self.env.db.check_db_attr_missing(
                TEST_UID,
                'person.language',
            )
        eq_(
            self.env.db.query_count('passportdbshard1'),
            query_count,

        )

    def assert_historydb_ok(self, language=TEST_NEW_LANGUAGE):
        expected_entries = {}
        if language is not None:
            base_entries = {
                'consumer': 'dev',
                'action': 'change_language',
                'info.lang': language,
                'user_agent': TEST_USER_AGENT,
            }
            expected_entries = {
                k: v
                for k, v in base_entries.items()
                if v is not None
            }

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_entries,
        )

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)

    def test_nothing_changed_ok(self):
        resp = self.make_request(query_args={'language': TEST_LANGUAGE})
        self.assert_ok_response(resp)
        self.assert_db_ok(language=None, query_count=0)
        self.assert_historydb_ok(language=None)
        self.assert_statbox_ok(language=None, with_check_cookies=True)
