# -*- coding: utf-8 -*-

from frozendict import frozendict
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.mail_apis.exceptions import HuskyTaskAlreadyExistsError
from passport.backend.core.builders.mail_apis.faker import (
    FakeHuskyApi,
    husky_delete_user_response,
)
from passport.backend.core.models.account import (
    MAIL_STATUS_ACTIVE,
    MAIL_STATUS_FROZEN,
    MAIL_STATUS_NONE,
)
from passport.backend.core.models.alias import (
    AltDomainAlias,
    PddAlias,
    YandexoidAlias,
)
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.subscription import Subscription
from passport.backend.core.services import services
from passport.backend.core.subscription import (
    add_subscription,
    can_be_subscribed,
    can_be_unsubscribed,
    delete_subscription,
    is_subscription_blocked,
    is_subscription_blocked_by_zero,
    SubscriptionImpossibleError,
    SubscriptionNotAllowedError,
    SubscriptionRequiresAccountWithLoginError,
    SubscriptionRequiresAccountWithPasswordError,
    UnsubscribeBlockingServiceError,
    UnsubscribeProtectedServiceError,
    update_subscription,
    user_has_contract_with_yandex,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.totp_secret import TotpSecretType
from passport.backend.core.undefined import Undefined


@with_settings_hosts(
    HUSKY_API_URL='http://localhost/',
    HUSKY_API_TIMEOUT=1,
    HUSKY_API_RETRIES=2,
    HUSKY_ENABLED=True,
)
class TestSubscriptions(PassportTestCase):

    # Эти значения дублируют services.*
    pdd_not_allowed_sids = [14, 19, 24, 61, 64, 85, 104, 119, 669]
    sids_requires_login = [2, 5, 14, 16, 19, 24, 27, 39, 59, 85, 116]
    sids_requires_password = [19, 27, 59, 116, 117, 119]
    blocking_sids = [14, 19, 24, 64, 78, 85, 104, 116, 117, 118, 119, 125, 670]
    blocking_sids_pdd = [14, 19, 24, 64, 85, 104, 116, 117, 118, 119, 670]
    # Здесь нет блокирующих подписок и подписок без сервиса
    protected_sids = [
        8, 37, 50, 55, 56, 57, 58, 59, 60, 61, 67, 70, 74, 77,
        79, 80, 81, 86, 87, 100, 102, 208, 667, 668, 669, 671, 672,
    ]

    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'husky',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.husky_api = FakeHuskyApi()
        self.husky_api.start()
        self.husky_api.set_response_value('delete_user', husky_delete_user_response())

    def tearDown(self):
        self.husky_api.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.husky_api
        del self.fake_tvm_credentials_manager

    def get_account(self, login='test-login', alias_type='portal', password='123', **kwargs):
        account = default_account(uid=1, alias=login, alias_type=alias_type, **kwargs)
        account.password.encrypted_password = password
        return account

    def test_impossible_to_subscribe__error(self):
        for sid in services.IMPOSSIBLE_TO_SUBSCRIBE_SIDS:
            assert_raises(
                SubscriptionImpossibleError,
                can_be_subscribed,
                self.get_account(),
                services.sids[sid],
            )

    def test_mailbox_exists_but_frozen__error(self):
        account = self.get_account()
        account.mail_status = MAIL_STATUS_FROZEN
        assert_raises(
            SubscriptionImpossibleError,
            can_be_subscribed,
            account,
            services.sids[2],
        )

    def test_sid_requires_login(self):
        for sid in self.sids_requires_login:
            assert_raises(
                SubscriptionRequiresAccountWithLoginError,
                can_be_subscribed,
                self.get_account(alias_type='social'),
                services.sids[sid],
            )

    def test_sid_requires_password(self):
        for sid in self.sids_requires_password:
            assert_raises(
                SubscriptionRequiresAccountWithPasswordError,
                can_be_subscribed,
                self.get_account(password=''),
                services.sids[sid],
            )

    def test_pdd_cant_be_subscribed__error(self):
        for sid in self.pdd_not_allowed_sids:
            assert_raises(
                SubscriptionNotAllowedError,
                can_be_subscribed,
                self.get_account(login='pdd@okna.ru', alias_type='pdd'),
                services.sids[sid],
            )

    def test_pdd_can_be_subscribed__ok(self):
        # Отфильтруем все подписки, на которые нельзя подписать ПДД-аккаунт
        sids = filter(
            lambda sid: (
                sid not in self.pdd_not_allowed_sids and
                sid not in services.IMPOSSIBLE_TO_SUBSCRIBE_SIDS
            ),
            services.sids.keys(),
        )
        for sid in sids:
            can_be_subscribed(
                self.get_account(login='pdd@okna.ru', alias_type='pdd'),
                services.sids[sid],
            )

    def test_can_be_unsubscribed__blocking_sid__error(self):
        for sid in self.blocking_sids:
            assert_raises(
                UnsubscribeBlockingServiceError,
                can_be_unsubscribed,
                self.get_account(),
                services.sids[sid],
            )

    def test_can_be_unsubscribed__blocking_sid__pdd__error(self):
        for sid in self.blocking_sids_pdd:
            assert_raises(
                UnsubscribeBlockingServiceError,
                can_be_unsubscribed,
                self.get_account(alias_type='pdd'),
                services.sids[sid],
            )

    def test_can_be_unsubscribed__mail_sid__federal__error(self):
        sid = services.get_service(slug='mail').sid
        assert_raises(
            UnsubscribeProtectedServiceError,
            can_be_unsubscribed,
            self.get_account(alias_type='pdd'),
            services.sids[sid],
        )

    def test_can_be_unsubscribed__protected_sid__error(self):
        for sid in self.protected_sids:
            assert_raises(
                UnsubscribeProtectedServiceError,
                can_be_unsubscribed,
                self.get_account(),
                services.sids[sid],
            )

    def test_can_be_unsubscribed__pdd_wanna_unsubscribe_mail__error(self):
        assert_raises(
            UnsubscribeProtectedServiceError,
            can_be_unsubscribed,
            self.get_account(login='pdd@okna.ru', alias_type='pdd'),
            services.sids[2],  # Яндекс.Почта
        )

    def test_can_be_unsubscribed__ok(self):
        sids = filter(
            lambda sid: (
                (sid not in self.blocking_sids) and
                (sid not in self.protected_sids)
            ),
            services.sids.keys(),
        )
        for sid in sids:
            can_be_unsubscribed(
                self.get_account(),
                services.sids[sid],
            )

    def test_is_subscription_blocked__true(self):
        disk_sid = 44
        service = services.sids[disk_sid]
        sub = Subscription(service=service, login_rule=3)

        ok_(is_subscription_blocked(sub))

    def test_impossible_to_delete_passport_subscription(self):
        passport_sid = 8
        with assert_raises(ValueError):
            delete_subscription(self.get_account(), services.sids[passport_sid])

    def test_is_subscription_blocked_by_zero__false(self):
        service = services.get_service(slug='jabber')
        sub = Subscription(service=service, login_rule=1)

        ok_(not is_subscription_blocked_by_zero(sub))

    def test_is_subscription_blocked_by_zero__true(self):
        service = services.get_service(slug='jabber')
        sub = Subscription(service=service, login_rule=0)

        ok_(is_subscription_blocked_by_zero(sub))

    def test_is_subscription_blocked_by_zero__undefined(self):
        service = services.get_service(slug='toloka')
        sub = Subscription(service=service)

        ok_(not is_subscription_blocked_by_zero(sub))

    def test_add_subscription_yastaff__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='yastaff')

        add_subscription(account, service, login=account.login)

        eq_(account.yandexoid_alias, YandexoidAlias(account, login=account.login))
        ok_(account.is_yandexoid)
        ok_(service.sid not in account.subscriptions)

    def test_add_subscription_galatasaray__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='galatasaray')

        add_subscription(account, service, login=account.login)

        eq_(account.altdomain_alias, AltDomainAlias(account, login=account.login + '@galatasaray.net'))
        ok_(service.sid not in account.subscriptions)

    def test_add_subscription_common__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='afisha')

        add_subscription(account, service)
        ok_(account.subscriptions[service.sid])
        eq_(account.subscriptions[service.sid].login_rule, Undefined)

    def test_add_subscription_login_rule__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='jabber')

        add_subscription(account, service, login_rule=0)

        ok_(account.subscriptions[service.sid])
        eq_(account.subscriptions[service.sid].login_rule, 0)
        ok_(not account.subscriptions[service.sid].host)

    def test_add_subscription_login__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='afisha')

        add_subscription(account, service, login='a-login')

        ok_(account.subscriptions[service.sid])
        eq_(account.subscriptions[service.sid].login, 'a-login')

    def test_add_subscription_host_id__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='wwwdgt')

        add_subscription(account, service, host_id=1)

        ok_(account.subscriptions[service.sid])
        eq_(account.subscriptions[service.sid].host.id, 1)
        ok_(not account.subscriptions[service.sid].suid)

    def test_add_subscription_mail__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='mail')

        add_subscription(account, service)

        ok_(account.subscriptions[service.sid])
        eq_(account.mail_status, MAIL_STATUS_ACTIVE)

    def test_add_subscription_mail_no_experiment__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='mail')

        with settings_context():
            add_subscription(account, service)

        ok_(account.subscriptions[service.sid])
        ok_(not account.global_logout_datetime)
        eq_(account.mail_status, MAIL_STATUS_ACTIVE)

    def test_add_subscription_strongpwd__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(sid=67)

        add_subscription(account, service)

        ok_(account.subscriptions[service.sid])
        eq_(account.global_logout_datetime, DatetimeNow(convert_to_datetime=True))

    def test_add_subscription_strongpwd_with_2fa__ok(self):
        account = self.get_account(subscriptions={})
        account.totp_secret.set(TotpSecretType('encrypted_secret'))
        service = services.get_service(sid=67)

        add_subscription(account, service)

        ok_(account.subscriptions[service.sid])
        eq_(account.global_logout_datetime, Undefined)

    def test_add_subscription_galatasaray_intranet__pass(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='galatasaray')

        with settings_context(ALT_DOMAINS=frozendict({'auto.ru': 1120001})):
            add_subscription(account, service, login=account.login)

            ok_(not account.altdomain_alias)
            ok_(not account.is_subscribed(service))

    def test_update_subscription__ok(self):
        service = services.get_service(slug='afisha')
        account = self.get_account(subscriptions={
            service.sid: Subscription().parse({'sid': service.sid, 'host_id': 2}),
        })

        ok_(account.subscriptions[service.sid])
        ok_(not account.subscriptions[service.sid].login_rule)
        eq_(account.subscriptions[service.sid].host.id, 2)

        update_subscription(account, service, login_rule=2, host_id=222)

        ok_(account.subscriptions[service.sid])
        eq_(account.subscriptions[service.sid].login_rule, 2)
        eq_(account.subscriptions[service.sid].host.id, 222)

    def test_update_not_existing_subscription__error(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='afisha')
        with assert_raises(KeyError):
            update_subscription(account, service, login_rule=2)

    def test_delete_yandex_alias__ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='yastaff')
        account.yandexoid_alias = YandexoidAlias(account, login=account.login)

        ok_(account.is_subscribed(service))

        delete_subscription(account, service)

        ok_(not account.yandexoid_alias)
        ok_(not account.is_subscribed(service))

    def test_delete_galatasaray(self):
        """
        Молча не отписываем
        """
        account = self.get_account()
        service = services.get_service(slug='galatasaray')
        account.altdomain_alias = AltDomainAlias(account, login=account.login + '@galatasaray.net')

        ok_(account.is_subscribed(service))

        delete_subscription(account, service)

        ok_(account.is_subscribed(service))
        eq_(account.altdomain_alias, AltDomainAlias(account, login=account.login + '@galatasaray.net'))

    def test_delete_mail_with_extra_attr(self):
        """
        Удаляем ещё и атрибут mail_status
        """
        service = services.get_service(slug='mail')
        account = self.get_account(subscriptions={
            service.sid: Subscription().parse({'sid': service.sid}),
        })
        account.mail_status = MAIL_STATUS_ACTIVE

        delete_subscription(account, service)

        ok_(service.sid not in account.subscriptions)
        eq_(account.mail_status, MAIL_STATUS_NONE)

    def test_delete_mail_with_existing_husky_task_ok(self):
        self.husky_api.set_response_side_effect('delete_user', HuskyTaskAlreadyExistsError)
        service = services.get_service(slug='mail')
        account = self.get_account(subscriptions={
            service.sid: Subscription().parse({'sid': service.sid}),
        })

        ok_(account.subscriptions[service.sid])

        delete_subscription(account, service)
        ok_(service.sid not in account.subscriptions)

    def test_delete_not_existing_ok(self):
        account = self.get_account(subscriptions={})
        service = services.get_service(slug='afisha')
        delete_subscription(account, service)

    def test_delete_no_husky(self):
        with settings_context(HUSKY_ENABLED=False):
            service = services.get_service(slug='mail')
            account = self.get_account(subscriptions={
                service.sid: Subscription().parse({'sid': service.sid}),
            })

            ok_(account.subscriptions[service.sid])

            delete_subscription(account, service)
            ok_(service.sid not in account.subscriptions)
            ok_(not self.husky_api.requests)

    def test_user_has_contract_with_yandex(self):
        yandex_blocking_services = []
        for sid in self.blocking_sids:
            service = services.get_service(sid)
            if service.slug not in {'sauth', 'money'}:
                yandex_blocking_services.append(service)

        money_service = services.get_service(slug='money')

        for service in yandex_blocking_services:
            account = self.get_account(
                subscriptions={
                    service.sid: Subscription().parse({'sid': service.sid}),
                    # Подмешаем неяндексовую подписку для реализму
                    money_service.sid: Subscription().parse({'sid': money_service.sid}),
                },
            )
            ok_(user_has_contract_with_yandex(account))

    def test_user_not_have_contract_with_yandex(self):
        for service_name in ['sauth', 'money']:
            service = services.get_service(slug=service_name)
            account = self.get_account(
                subscriptions={
                    service.sid: Subscription().parse({'sid': service.sid}),
                },
            )
            ok_(not user_has_contract_with_yandex(account))

    def test_possible_to_delete_mailpro_subscription_if_pdd_alias_exist(self):
        service = services.get_service(slug='mailpro')
        account = self.get_account(
            subscriptions={
                service.sid: Subscription().parse({'sid': service.sid}),
            },
        )
        account.pdd_alias = PddAlias(
            parent=account,
            email='pdd@okna.ru',
        )
        delete_subscription(account, service)
        ok_(service.sid not in account.subscriptions)
