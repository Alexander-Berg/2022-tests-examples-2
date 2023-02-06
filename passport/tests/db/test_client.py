# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from time import time
from urllib.parse import urlparse

from django.conf import settings
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.oauth.core.common.blackbox import get_blackbox
from passport.backend.oauth.core.common.utils import now
from passport.backend.oauth.core.db.client import (
    ApprovalStatus,
    Client,
    EventType,
    is_redirect_uri_insecure,
    list_clients_by_creator,
    PLATFORM_ANDROID,
    PLATFORM_IOS,
    PLATFORM_TURBOAPP,
    will_require_approval,
)
from passport.backend.oauth.core.db.eav import (
    CREATE,
    EntityNotFoundError,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.attributes import (
    attr_by_name,
    VIRTUAL_ATTR_ENTITY_ID,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.test.base_test_data import DELETED_SCOPE_ID
from passport.backend.oauth.core.test.db_utils import model_to_bb_response
from passport.backend.oauth.core.test.framework import BaseTestCase
from passport.backend.oauth.core.test.framework.testcases import DBTestCase


TEST_UID = 1
TEST_OTHER_UID = 2
TEST_USER_IP = '192.168.0.1'
TEST_YANDEX_IP = '37.9.101.188'


class TestClient(DBTestCase):
    def setUp(self):
        super(TestClient, self).setUp()
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
            ],
            default_title='Тестовое приложение',
            default_description='Описание',
        )) as client:
            client.title_ru = 'Русское название'
            client.title_uk = 'Украинское название'
            client.title_en = ''
            client.description_ru = 'Русское описание'
            client.description_uk = 'Украинское описание'
            client.description_en = ''
            self.test_client = client

        self.fake_db.reset_mocks()

    def test_title_localizations(self):
        eq_(self.test_client.default_title, 'Тестовое приложение')
        eq_(self.test_client.get_title(), 'Русское название')
        eq_(self.test_client.get_title(language='ru'), 'Русское название')
        eq_(self.test_client.get_title(language='uk'), 'Украинское название')
        eq_(self.test_client.get_title(language='en'), 'Тестовое приложение')
        eq_(self.test_client.get_title(language='tr'), 'Тестовое приложение')
        eq_(self.test_client.get_title(language='bd'), 'Тестовое приложение')

    def test_description_localizations(self):
        eq_(self.test_client.default_description, 'Описание')
        eq_(self.test_client.get_description(), 'Русское описание')
        eq_(self.test_client.get_description(language='ru'), 'Русское описание')
        eq_(self.test_client.get_description(language='uk'), 'Украинское описание')
        eq_(self.test_client.get_description(language='en'), 'Описание')
        eq_(self.test_client.get_description(language='tr'), 'Описание')
        eq_(self.test_client.get_description(language='bd'), 'Описание')

    def test_get_icon_url(self):
        self.test_client.icon_id = 'gid/icon-id-0'

        icon_url = self.test_client.get_icon_url(size='XXL')
        parsed = urlparse(icon_url)
        eq_(parsed.scheme, 'https')
        eq_(parsed.path, '/get-oauth/gid/icon-id-0/XXL')

    def test_by_display_id(self):
        client = Client.by_display_id(self.test_client.display_id)
        eq_(client.id, self.test_client.id)

    def test_by_invalid_display_id(self):
        client = Client.by_display_id('id приложения')
        ok_(client is None)

    def test_list_clients_by_uid(self):
        client_ids = [client.id for client in list_clients_by_creator(TEST_UID)]
        eq_(client_ids, [self.test_client.id])

    def test_yandex_clients(self):
        eq_(
            [cl.id for cl in Client.by_index('params', is_yandex=True)],
            [],
        )

        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        eq_(
            [cl.id for cl in Client.by_index('params', is_yandex=True)],
            [self.test_client.id],
        )

    def test_secret(self):
        old_secret = self.test_client.secret

        with UPDATE(self.test_client) as client:
            client.make_new_secret()

        client = Client.by_id(self.test_client.id)
        ok_(client.secret != old_secret)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE
        self.fake_db.reset_mocks()

        with UPDATE(self.test_client) as client:
            client.restore_old_secret()

        client = Client.by_id(self.test_client.id)
        eq_(client.secret, old_secret)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_approval_not_required(self):
        eq_(self.test_client.approval_status, ApprovalStatus.NotRequired)
        eq_(self.test_client._events, ())

    def test_approval_required(self):
        new_scopes = [Scope.by_keyword('test:foo'), Scope.by_keyword('test:premoderate')]
        ok_(will_require_approval(new_scopes, client=self.test_client))
        with UPDATE(self.test_client) as client:
            client.set_scopes(new_scopes)

        client = Client.by_id(self.test_client.id)
        eq_(client.approval_status, ApprovalStatus.Pending)
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.ApprovalRequired)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_approval_required_again(self):
        with UPDATE(self.test_client) as client:
            client.approval_status = ApprovalStatus.Approved
            client.set_scopes([Scope.by_keyword('test:foo'), Scope.by_keyword('test:premoderate')])

        client = Client.by_id(self.test_client.id)
        eq_(client.approval_status, ApprovalStatus.Pending)
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.ApprovalRequiredAgain)

    def test_approval_status_not_changed(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:premoderate'),
            ])
            client.approval_status = ApprovalStatus.Approved

        new_scopes = [
            Scope.by_keyword('test:foo'),
            Scope.by_keyword('test:bar'),
            Scope.by_keyword('test:premoderate'),
        ]
        ok_(not will_require_approval(new_scopes, client=self.test_client))
        with UPDATE(self.test_client) as client:
            client.set_scopes(new_scopes)

        client = Client.by_id(self.test_client.id)
        eq_(client.approval_status, ApprovalStatus.Approved)
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.ApprovalRequired)

    def test_approval_not_required_any_more(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([
                Scope.by_keyword('test:premoderate'),
            ])

        new_scopes = [Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')]
        ok_(not will_require_approval(new_scopes, client=self.test_client))
        with UPDATE(self.test_client) as client:
            client.set_scopes(new_scopes)

        client = Client.by_id(self.test_client.id)
        eq_(client.approval_status, ApprovalStatus.NotRequired)
        eq_(len(client._events), 2)
        eq_(client._events[0].type, EventType.ApprovalRequired)
        eq_(client._events[1].type, EventType.ApprovalNotRequired)

    def test_approval_not_required_for_yandex_client(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        new_scopes = [Scope.by_keyword('test:foo'), Scope.by_keyword('test:premoderate')]
        ok_(not will_require_approval(new_scopes, client=self.test_client))
        with UPDATE(self.test_client) as client:
            client.set_scopes(new_scopes)

        eq_(self.test_client.approval_status, ApprovalStatus.NotRequired)
        eq_(self.test_client._events, ())

    def test_block(self):
        with UPDATE(self.test_client) as client:
            client.block()
            client.block()

        client = Client.by_id(self.test_client.id)
        ok_(client.is_blocked)
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.Blocked)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_unblock(self):
        with UPDATE(self.test_client) as client:
            client.is_blocked = True
            client.unblock()
            client.unblock()

        client = Client.by_id(self.test_client.id)
        ok_(not client.is_blocked)
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.Unblocked)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_glogout(self):
        with UPDATE(self.test_client) as client:
            client.glogout()

        client = Client.by_id(self.test_client.id)
        self.assertAlmostEqual(
            client.glogouted,
            datetime.now(),
            delta=timedelta(seconds=3),
        )
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.Glogouted)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_approve(self):
        with UPDATE(self.test_client) as client:
            client.approval_status = ApprovalStatus.Pending
            client.approve()
            client.approve()

        client = Client.by_id(self.test_client.id)
        eq_(client.approval_status, ApprovalStatus.Approved)
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.ApprovalGranted)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_reject_approval(self):
        with UPDATE(self.test_client) as client:
            client.approval_status = ApprovalStatus.Pending
            client.reject_approval()
            client.reject_approval()

        client = Client.by_id(self.test_client.id)
        eq_(client.approval_status, ApprovalStatus.Rejected)
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.ApprovalRejected)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_change_creator(self):
        with UPDATE(self.test_client) as client:
            client.change_creator(uid=3)
            client.change_creator(uid=3)

        client = Client.by_id(self.test_client.id)
        eq_(client.uid, 3)
        ok_(client.is_created_by(3))
        eq_(len(client._events), 1)
        eq_(client._events[0].type, EventType.CreatorChanged)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_too_many_events(self):
        with UPDATE(self.test_client) as client:
            for i in range(settings.CLIENT_MAX_EVENTS_COUNT + 1):
                client.add_event(event_type=EventType.CreatorChanged)

        client = Client.by_id(self.test_client.id)
        eq_(len(client._events), settings.CLIENT_MAX_EVENTS_COUNT)
        eq_(client._events[0].type, EventType.Truncated)
        eq_(client._events[1].type, EventType.CreatorChanged)
        eq_(client._events[-1].type, EventType.CreatorChanged)

        eq_(self.fake_db.query_count('oauthdbcentral'), 1)  # by_id
        eq_(self.fake_db.transaction_count('oauthdbcentral'), 1)  # UPDATE

    def test_events_as_string(self):
        with UPDATE(self.test_client) as client:
            client.change_creator(uid=3)

        with UPDATE(self.test_client) as client:
            client.block()

        eq_(len(client.events), 2)
        ok_(client.events[0].endswith(' Owner changed'), client.events[0])
        ok_(client.events[1].endswith(' Blocked'), client.events[1])

    def test_deleted_scopes(self):
        eq_(self.test_client.scopes, set([Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')]))
        eq_(self.test_client.deleted_scopes, set())

        deleted_scope = Scope.by_id(DELETED_SCOPE_ID)  # получить по кейворду не можем - сами закрыли такую возможность
        ok_(deleted_scope.is_deleted)

        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:foo'), deleted_scope])

        eq_(client.deleted_scopes, set([deleted_scope]))
        eq_(client.scopes, set([Scope.by_keyword('test:foo')]))

    def test_deleted_client_not_found(self):
        """
        Убедимся, что удалённое приложение нельзя получить никакими способами,
        если явно этого не просить
        """
        with UPDATE(self.test_client) as client:
            client.deleted = now()

        with assert_raises(EntityNotFoundError):
            Client.by_id(self.test_client.id)

        eq_(Client.by_ids([self.test_client.id]), {})
        assert_is_none(Client.by_display_id(self.test_client.display_id))

    def test_deleted_client_found(self):
        """
        Убедимся, что удалённое приложение можно получить,
        если об этом явно попросить
        """
        with UPDATE(self.test_client):
            self.test_client.deleted = now()

        eq_(
            Client.by_id(self.test_client.id, allow_deleted=True),
            self.test_client,
        )
        eq_(
            Client.by_ids([self.test_client.id], allow_deleted=True),
            {self.test_client.id: self.test_client},
        )
        eq_(
            Client.by_display_id(self.test_client.display_id, allow_deleted=True),
            self.test_client,
        )

    def test_owners(self):
        ok_(not self.test_client.can_be_edited(uid=TEST_OTHER_UID, user_ip=TEST_YANDEX_IP))
        ok_(not self.test_client.is_owned_by(TEST_OTHER_UID))

        with UPDATE(self.test_client) as client:
            client.owner_uids = [TEST_OTHER_UID]

        ok_(self.test_client.can_be_edited(uid=TEST_OTHER_UID, user_ip=TEST_YANDEX_IP))
        ok_(self.test_client.is_owned_by(TEST_OTHER_UID))
        eq_(Client.by_owner(TEST_OTHER_UID), [self.test_client])

    def test_can_yandex_be_edited(self):
        ok_(not self.test_client.can_be_edited(uid=TEST_OTHER_UID, user_ip=TEST_YANDEX_IP))

        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        ok_(not self.test_client.can_be_edited(uid=TEST_UID, user_ip=TEST_USER_IP))
        ok_(self.test_client.can_be_edited(uid=TEST_UID, user_ip=TEST_YANDEX_IP))

    def test_redirect_uris(self):
        eq_(self.test_client.redirect_uris, [])

        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['http://foo', 'http://bar']
            client._callback = 'https://zar'
        client = Client.by_id(self.test_client.id)
        eq_(
            client.redirect_uris,
            [
                'https://zar',
                'http://foo',
                'http://bar',
            ],
        )

    def test_default_redirect_uri(self):
        ok_(self.test_client.default_redirect_uri is None)

        with UPDATE(self.test_client) as client:
            client._redirect_uris = ['http://foo', 'http://bar']
        client = Client.by_id(self.test_client.id)
        eq_(
            client.default_redirect_uri,
            'http://foo',
        )

        with UPDATE(self.test_client) as client:
            client._callback = 'https://zar'
        client = Client.by_id(self.test_client.id)
        eq_(
            client.default_redirect_uri,
            'https://zar',
        )

    def test_platforms_missing(self):
        eq_(self.test_client.platforms, set())
        eq_(self.test_client.platform_specific_redirect_uris, [])

    def test_platform_android(self):
        self.test_client.android_default_package_name = 'some-package-name'
        self.test_client.android_extra_package_names = ['package-name-1', 'package-name-2']
        self.test_client.android_cert_fingerprints = ['some-fingerprint']

        eq_(
            self.test_client.platforms,
            {PLATFORM_ANDROID}
        )
        eq_(
            self.test_client.android_package_names,
            ['some-package-name', 'package-name-1', 'package-name-2'],
        )
        eq_(
            self.test_client.platform_specific_redirect_uris,
            [
                'https://yx%s.oauth.yandex.ru/auth/finish?platform=android' % self.test_client.display_id,
                'https://yx%s.oauth.yandex.com/auth/finish?platform=android' % self.test_client.display_id,
                'yx%s:///auth/finish?platform=android' % self.test_client.display_id,
            ],
        )

    def test_platform_ios(self):
        self.test_client.ios_default_app_id = 'some-app-id'
        self.test_client.ios_extra_app_ids = ['app-id-1', 'app-id-2']

        eq_(
            self.test_client.platforms,
            {PLATFORM_IOS}
        )
        eq_(
            self.test_client.ios_app_ids,
            ['some-app-id', 'app-id-1', 'app-id-2'],
        )
        eq_(
            self.test_client.platform_specific_redirect_uris,
            [
                'https://yx%s.oauth.yandex.ru/auth/finish?platform=ios' % self.test_client.display_id,
                'https://yx%s.oauth.yandex.com/auth/finish?platform=ios' % self.test_client.display_id,
                'yx%s:///auth/finish?platform=ios' % self.test_client.display_id,
            ],
        )

    def test_platform_turboapp(self):
        self.test_client.turboapp_base_url = 'https://ozon.ru'

        eq_(
            self.test_client.platforms,
            {PLATFORM_TURBOAPP}
        )
        eq_(
            self.test_client.platform_specific_redirect_uris,
            [
                'yandexta://ozon.ru',
            ],
        )

    def test_platforms_all(self):
        self.test_client.android_default_package_name = 'some-package-name'
        self.test_client.android_cert_fingerprints = ['some-fingerprint']
        self.test_client.ios_default_app_id = 'some-app-id'
        self.test_client.turboapp_base_url = 'https://ozon.ru'

        eq_(
            self.test_client.platforms,
            {PLATFORM_ANDROID, PLATFORM_IOS, PLATFORM_TURBOAPP}
        )
        eq_(
            self.test_client.platform_specific_redirect_uris,
            [
                'https://yx%s.oauth.yandex.ru/auth/finish?platform=ios' % self.test_client.display_id,
                'https://yx%s.oauth.yandex.com/auth/finish?platform=ios' % self.test_client.display_id,
                'yx%s:///auth/finish?platform=ios' % self.test_client.display_id,
                'https://yx%s.oauth.yandex.ru/auth/finish?platform=android' % self.test_client.display_id,
                'https://yx%s.oauth.yandex.com/auth/finish?platform=android' % self.test_client.display_id,
                'yx%s:///auth/finish?platform=android' % self.test_client.display_id,
                'yandexta://ozon.ru',
            ],
        )

    def test_visible_scopes(self):
        eq_(self.test_client.extra_visible_scopes, set())
        eq_(self.test_client.scopes_invisible_for_creator, set())

        self.test_client.set_scopes([Scope.by_keyword('test:foo'), Scope.by_keyword('test:invisible')])
        ok_(Scope.by_keyword('test:invisible') in self.test_client.visible_scopes)
        eq_(
            self.test_client.scopes_invisible_for_creator,
            {Scope.by_keyword('test:invisible')},
        )

        self.test_client.set_extra_visible_scopes([Scope.by_keyword('test:invisible')])
        eq_(self.test_client.extra_visible_scopes, {Scope.by_keyword('test:invisible')})
        ok_(Scope.by_keyword('test:invisible') in self.test_client.visible_scopes)
        eq_(
            self.test_client.scopes_invisible_for_creator,
            {Scope.by_keyword('test:invisible')},
        )

    def test_extra_visible_scopes_for_phone_scope(self):
        eq_(self.test_client.extra_visible_scopes, set())
        self.test_client.set_scopes([Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')])
        eq_(self.test_client.extra_visible_scopes, {Scope.by_keyword('test:default_phone')})

    def test_extra_visible_scopes_for_phone_scope_and_special_client(self):
        eq_(self.test_client.extra_visible_scopes, set())
        self.fake_client_lists.set_data({'whitelist_for_scope': {'test:default_phone': [self.test_client.display_id]}})
        eq_(self.test_client.extra_visible_scopes, {Scope.by_keyword('test:default_phone')})


class TestClientParse(DBTestCase):
    def setUp(self):
        super(TestClientParse, self).setUp()
        self.fake_blackbox = FakeBlackbox()
        self._apply_patches({
            'blackbox': self.fake_blackbox,
        })

    @staticmethod
    def attr_type(attr_name, entity='client'):
        attr_type_, _ = attr_by_name(entity, attr_name)
        return str(attr_type_)

    def test_ok_synthetic(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(oauth_token_info={
                'client_attributes': {
                    self.attr_type('uid'): str(TEST_UID),
                    self.attr_type('scope_ids'): '|%s|' % Scope.by_keyword('test:foo').id,
                    self.attr_type('secret'): 'secret*',
                    self.attr_type('display_id'): 'deadbeed',
                    self.attr_type('created'): str(int(time())),
                    str(VIRTUAL_ATTR_ENTITY_ID): '123',
                },
            }),
        )
        bb_response = get_blackbox().oauth(oauth_token='token', ip='127.0.0.1')
        client = Client.parse(bb_response)
        eq_(client.id, 123)
        eq_(client.uid, TEST_UID)
        eq_(client.scopes, {Scope.by_keyword('test:foo')})
        eq_(client.secret, 'secret*')
        eq_(client.display_id, 'deadbeed')
        eq_(client.created, DatetimeNow())

    def test_ok_existing(self):
        with CREATE(Client.create(
                uid=TEST_UID,
                scopes=[
                    Scope.by_keyword('test:foo'),
                    Scope.by_keyword('test:bar'),
                ],
                default_title='Тестовое приложение',
                default_description='Описание',
        )) as client:
            pass

        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(oauth_token_info={
                'client_attributes': model_to_bb_response(client),
            }),
        )
        bb_response = get_blackbox().oauth(oauth_token='token', ip='127.0.0.1')
        parsed_client = Client.parse(bb_response)
        eq_(parsed_client, client)


class TestUtils(BaseTestCase):
    def test_is_redirect_uri_insecure(self):
        for secure_url in (
            'https://yandex.ru',
            'https://окна.рф',
            'http://localhost/foo',
            'http://localhost:80/bar',
            'http://127.0.0.1/foo',
            'http://127.0.0.1:80/bar',
            'http://[::1]/foo',
            'http://[::1]:80/foo',
            'scheme:///zar',
        ):
            ok_(not is_redirect_uri_insecure(secure_url), '%s must be secure' % secure_url)

        for insecure_url in (
            'http://yandex.ru',
            'http://127.0.0.2',
            'http:///path',
        ):
            ok_(is_redirect_uri_insecure(insecure_url), '%s must be insecure' % insecure_url)
