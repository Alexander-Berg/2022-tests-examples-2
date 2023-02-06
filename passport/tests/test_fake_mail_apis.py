# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.mail_apis import (
    Collie,
    Furita,
    get_collie,
    get_furita,
    get_husky,
    get_rpop,
    get_wmi,
    RPOP,
    WMI,
)
from passport.backend.core.builders.mail_apis.exceptions import HuskyTemporaryError
from passport.backend.core.builders.mail_apis.faker import (
    collie_item,
    collie_response,
    FakeCollie,
    FakeFurita,
    FakeHuskyApi,
    FakeRPOP,
    FakeWMI,
    furita_blackwhite_response,
    husky_delete_user_response,
    rpop_list_item,
    rpop_list_response,
    wmi_folders_item,
    wmi_folders_response,
)
from passport.backend.core.test.test_utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


TEST_UID = 2323
TEST_SUID = 3211
TEST_MDB = 'pg'
TEST_SETTING_NAME = 'some-setting'
TEST_SETTING_VALUE = 'setting-value'

eq_ = iterdiff(eq_)


@with_settings_hosts(
    FURITA_API_URL='http://localhost/',
    FURITA_API_RETRIES=1,
    FURITA_API_TIMEOUT=1,
)
class FakeFuritaTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_furita = FakeFurita()
        self.fake_furita.start()

    def tearDown(self):
        self.fake_furita.stop()
        del self.fake_furita

    def test_set_response_value_blackwhite(self):
        ok_(not self.fake_furita._mock.request.called)
        response = furita_blackwhite_response(['black@black.ru'], ['white@white.ru'])
        self.fake_furita.set_response_value(
            'blackwhite',
            response,
        )
        eq_(Furita().blackwhite(TEST_UID), json.loads(response))
        ok_(self.fake_furita._mock._called)

    def test_set_response_side_effect_blackwhite(self):
        ok_(not self.fake_furita._mock.request.called)
        self.fake_furita.set_response_side_effect('blackwhite', ValueError)
        with assert_raises(ValueError):
            get_furita().blackwhite(TEST_UID)
        ok_(self.fake_furita._mock.request.called)

    @raises(ValueError)
    def test_set_response_value_for_unknown_method(self):
        self.fake_furita.set_response_value(
            u'unknown_method',
            'response',
        )

    @raises(ValueError)
    def test_set_response_side_effect_for_unknown_method(self):
        self.fake_furita.set_response_side_effect(
            u'unknown_method',
            'response',
        )


@with_settings_hosts(
    RPOP_API_URL='http://localhost/',
    RPOP_API_RETRIES=1,
    RPOP_API_TIMEOUT=1,
)
class FakeRPOPTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_rpop = FakeRPOP()
        self.fake_rpop.start()

    def tearDown(self):
        self.fake_rpop.stop()
        del self.fake_rpop

    def test_set_response_value_list(self):
        ok_(not self.fake_rpop._mock.request.called)
        response = rpop_list_response([rpop_list_item()])
        self.fake_rpop.set_response_value(
            'list',
            response,
        )
        eq_(RPOP().list(TEST_SUID, TEST_MDB), json.loads(response))
        ok_(self.fake_rpop._mock._called)

    def test_set_response_side_effect_list(self):
        ok_(not self.fake_rpop._mock.request.called)
        self.fake_rpop.set_response_side_effect('list', ValueError)
        with assert_raises(ValueError):
            get_rpop().list(TEST_SUID, TEST_MDB)
        ok_(self.fake_rpop._mock.request.called)

    @raises(ValueError)
    def test_set_response_value_for_unknown_method(self):
        self.fake_rpop.set_response_value(
            u'unknown_method',
            'response',
        )

    @raises(ValueError)
    def test_set_response_side_effect_for_unknown_method(self):
        self.fake_rpop.set_response_side_effect(
            u'unknown_method',
            'response',
        )


@with_settings_hosts(
    WMI_API_URL='http://localhost/',
    WMI_API_RETRIES=1,
    WMI_API_TIMEOUT=1,
)
class FakeWMITestCase(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'wmi_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_wmi = FakeWMI()
        self.fake_wmi.start()

    def tearDown(self):
        self.fake_wmi.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_wmi
        del self.fake_tvm_credentials_manager

    def test_set_response_value_folders(self):
        ok_(not self.fake_wmi._mock.request.called)
        response = wmi_folders_response([wmi_folders_item()])
        self.fake_wmi.set_response_value(
            'folders',
            response,
        )
        eq_(WMI().folders(TEST_UID, TEST_SUID, TEST_MDB), json.loads(response))
        ok_(self.fake_wmi._mock._called)

    def test_set_response_side_effect_folders(self):
        ok_(not self.fake_wmi._mock.request.called)
        self.fake_wmi.set_response_side_effect('folders', ValueError)
        with assert_raises(ValueError):
            get_wmi().folders(TEST_UID, TEST_SUID, TEST_MDB)
        ok_(self.fake_wmi._mock.request.called)

    @raises(ValueError)
    def test_set_response_value_for_unknown_method(self):
        self.fake_wmi.set_response_value(
            u'unknown_method',
            'response',
        )

    @raises(ValueError)
    def test_set_response_side_effect_for_unknown_method(self):
        self.fake_wmi.set_response_side_effect(
            u'unknown_method',
            'response',
        )


@with_settings_hosts(
    HUSKY_API_URL='http://localhost/',
    HUSKY_API_RETRIES=1,
    HUSKY_API_TIMEOUT=1,
)
class FakeHuskyApiTestCase(unittest.TestCase):
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

        self.fake_husky_api = FakeHuskyApi()
        self.fake_husky_api.start()

    def tearDown(self):
        self.fake_husky_api.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_husky_api
        del self.fake_tvm_credentials_manager

    def test_set_response(self):
        ok_(not self.fake_husky_api._mock.request.called)

        self.fake_husky_api.set_response_value('delete_user', husky_delete_user_response())
        resp = get_husky().delete_user(TEST_UID)
        eq_(resp, json.loads(husky_delete_user_response()))
        ok_(self.fake_husky_api._mock.request.called)

    def test_set_side_effect(self):
        ok_(not self.fake_husky_api._mock.request.called)

        self.fake_husky_api.set_response_side_effect('delete_user', HuskyTemporaryError)
        with assert_raises(HuskyTemporaryError):
            get_husky().delete_user(TEST_UID)
        ok_(self.fake_husky_api._mock.request.called)


@with_settings_hosts(
    COLLIE_API_URL='http://localhost/',
    COLLIE_API_RETRIES=1,
    COLLIE_API_TIMEOUT=1,
)
class FakeCollieTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'collie',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_collie = FakeCollie()
        self.fake_collie.start()

    def tearDown(self):
        self.fake_collie.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_collie
        del self.fake_tvm_credentials_manager

    def test_set_response_value_search_contacts(self):
        ok_(not self.fake_collie._mock.request.called)
        self.fake_collie.set_response_value(
            'search_contacts',
            collie_response([collie_item()]),
        )
        eq_(Collie().search_contacts(TEST_UID), [collie_item()])
        ok_(self.fake_collie._mock._called)

    def test_set_response_side_effect_search_contacts(self):
        ok_(not self.fake_collie._mock.request.called)
        self.fake_collie.set_response_side_effect('search_contacts', ValueError)
        with assert_raises(ValueError):
            get_collie().search_contacts(TEST_UID)
        ok_(self.fake_collie._mock.request.called)

    @raises(ValueError)
    def test_set_response_value_for_unknown_method(self):
        self.fake_collie.set_response_value(
            u'unknown_method',
            collie_response([collie_item()]),
        )

    @raises(ValueError)
    def test_set_response_side_effect_for_unknown_method(self):
        self.fake_collie.set_response_side_effect(
            u'unknown_method',
            collie_response([collie_item()]),
        )
