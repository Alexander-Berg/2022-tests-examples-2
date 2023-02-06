# -*- coding: utf-8 -*-
from django.utils.encoding import smart_text
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.oauth.core.db.scope import (
    get_payment_auth_app_ids,
    is_payment_auth_required,
    list_services_with_titles,
    Scope,
)
from passport.backend.oauth.core.test.base_test_data import (
    DELETED_SCOPE_ID,
    TEST_SCOPE_LOCALIZATIONS_CONFIG,
    TEST_SCOPE_SHORT_LOCALIZATIONS_CONFIG,
    TEST_SCOPES_CONFIG,
    TEST_SERVICE_LOCALIZATIONS_CONFIG,
)
from passport.backend.oauth.core.test.framework.testcases import DBTestCase


class TestScope(DBTestCase):
    def test_list_scopes(self):
        scopes = Scope.list()
        eq_(len(scopes), len(TEST_SCOPES_CONFIG.keys()) - 1)  # list() не возвращает удалённые скоупы

    def test_scope_by_id(self):
        scope = Scope.by_id(2)

        eq_(scope.id, 2)
        eq_(scope.keyword, 'test:bar')
        eq_(scope.service_name, 'test')
        eq_(scope.default_title, 'test:bar')
        ok_(scope.ttl is None)
        ok_(not scope.is_ttl_refreshable)
        ok_(not scope.requires_approval)
        ok_(not scope.is_hidden)
        eq_(scope.visible_for_uids, set())
        ok_(not scope.has_xtoken_grant)
        ok_(not scope.allowed_for_turboapps)

    def test_scope_by_str_id(self):
        scope = Scope.by_id('2')

        eq_(scope.id, 2)
        eq_(scope.keyword, 'test:bar')
        eq_(scope.service_name, 'test')
        eq_(scope.default_title, 'test:bar')
        ok_(scope.ttl is None)
        ok_(not scope.is_ttl_refreshable)
        ok_(not scope.requires_approval)
        ok_(not scope.is_hidden)
        eq_(scope.visible_for_uids, set())
        ok_(not scope.has_xtoken_grant)
        ok_(not scope.allowed_for_turboapps)

    def test_scope_by_keyword(self):
        scope = Scope.by_keyword('test:bar')

        eq_(scope.id, 2)
        eq_(scope.keyword, 'test:bar')
        eq_(scope.service_name, 'test')
        eq_(scope.default_title, 'test:bar')
        ok_(scope.ttl is None)
        ok_(not scope.is_ttl_refreshable)
        ok_(not scope.requires_approval)
        ok_(not scope.is_hidden)
        eq_(scope.visible_for_uids, set())
        ok_(not scope.has_xtoken_grant)
        ok_(not scope.allowed_for_turboapps)

    def test_deleted_scope_by_id(self):
        scope = Scope.by_id(DELETED_SCOPE_ID)

        eq_(scope.id, DELETED_SCOPE_ID)
        eq_(scope.keyword, 'deleted:test:zar')
        eq_(scope.service_name, 'deleted')
        ok_(scope.is_deleted)

    @raises(ValueError)
    def test_scope_not_found_by_id(self):
        Scope.by_id(0)

    @raises(ValueError)
    def test_scope_not_found_by_str_id(self):
        Scope.by_id('0')

    @raises(ValueError)
    def test_scope_not_found_by_keyword(self):
        Scope.by_keyword('unknown')

    @raises(ValueError)
    def test_deleted_scope_not_found_by_keyword(self):
        Scope.by_keyword('deleted:test:zar')

    def test_magic_methods(self):
        scope_foo = Scope.by_keyword('test:foo')
        scope_bar = Scope.by_keyword('test:bar')

        eq_(scope_foo, Scope.by_keyword('test:foo'))
        ok_(scope_foo != scope_bar)
        ok_(scope_foo != 'test:foo')
        eq_(repr(scope_foo), "'test:foo'")
        eq_(str(scope_foo), 'test:foo')
        eq_(smart_text(scope_foo), 'test:foo')

    def test_localize(self):
        scope = Scope.by_keyword('test:foo')

        eq_(scope.get_title('ru'), TEST_SCOPE_LOCALIZATIONS_CONFIG['ru']['test:foo'])
        eq_(
            scope.get_title('ru', short=True),
            TEST_SCOPE_SHORT_LOCALIZATIONS_CONFIG['ru']['test:foo'],
        )
        eq_(
            scope.get_title('ru', with_slug=True),
            TEST_SCOPE_LOCALIZATIONS_CONFIG['ru']['test:foo'] + ' (test:foo)',
        )
        eq_(scope.get_service_title('ru'), TEST_SERVICE_LOCALIZATIONS_CONFIG['ru']['test'])
        eq_(scope.get_title('tr'), 'test:foo')
        eq_(scope.get_title('uk'), 'test:foo')
        eq_(scope.get_service_title('tr'), 'test')
        eq_(scope.get_service_title('uk'), 'test')

    @raises(ValueError)
    def test_localize_bad_language(self):
        scope = Scope.by_keyword('test:foo')
        scope.get_service_title('by')

    def test_lists(self):
        list1 = [Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')]
        list2 = [Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')]
        eq_(list1, list2)

        list3 = ['test:foo', 'test:bar']
        ok_(list1 != list3)

    def test_sets(self):
        set1 = set([Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')])
        set2 = set([Scope.by_keyword('test:foo')])
        ok_(set2.issubset(set1))

        set3 = set(['test:foo'])
        ok_(not set3.issubset(set1))

    def test_list_services_with_titles(self):
        eq_(
            list_services_with_titles(language='en'),
            {
                'test': 'OAuth test',
                'lunapark': 'OAuth tank',
                'app_password': 'App passwords',
                'money': 'Money',
            },
        )

    def test_visibility(self):
        scope = Scope.by_keyword('test:invisible')

        ok_(scope.is_hidden)
        eq_(scope.visible_for_uids, {2})
        eq_(scope.visible_for_consumers, {'dev'})


class TestPaymentAuth(DBTestCase):
    def test_is_payment_auth_required(self):
        ok_(is_payment_auth_required([Scope.by_keyword('money:all')]))
        ok_(is_payment_auth_required([Scope.by_keyword('money:all'), Scope.by_keyword('test:foo')]))
        ok_(not is_payment_auth_required([Scope.by_keyword('test:foo')]))

    def test_get_payment_auth_app_ids(self):
        eq_(
            get_payment_auth_app_ids([Scope.by_keyword('money:all')]),
            ['money.app.1', 'money.app.2'],
        )
        eq_(
            get_payment_auth_app_ids([Scope.by_keyword('money:all'), Scope.by_keyword('test:foo')]),
            ['money.app.1', 'money.app.2'],
        )
        eq_(
            get_payment_auth_app_ids([Scope.by_keyword('test:foo')]),
            [],
        )
