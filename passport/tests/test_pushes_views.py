from urllib.parse import urlencode

from django.test import SimpleTestCase
from django.urls import reverse
from passport.backend.core.builders.historydb_api.faker import (
    FakeHistoryDBApi,
    push_history_response,
    push_history_response_item,
)
from passport.backend.py_adm.core.tvm.faker.fake_tvm import FakeTvmAuthCredentialsManager


class TestViews(SimpleTestCase):
    def setUp(self):
        self._patches = []

        self.fake_historydb = FakeHistoryDBApi()
        self._patches.append(self.fake_historydb)

        self.fake_tvm_credentials_manager = FakeTvmAuthCredentialsManager()
        self.fake_tvm_credentials_manager.set_ticket_data(dict(
            historydb_api='test_ticket',
        ))
        self._patches.append(self.fake_tvm_credentials_manager)

        for patch in self._patches:
            patch.start()

    def setup_historydb(self, method='push_history_by_fields'):
        self.fake_historydb.set_response_value(
            method,
            push_history_response([
                push_history_response_item(
                    app_id='app_id1',
                    push_id='push_id1',
                    unixtime=1653310241,
                    device_id='device_id1',
                    details='details1',
                    status='ok',
                    push_event='push_event1',
                    push_service='push_service1',
                    context='context1',
                    subscription_id='subscription_id1',
                    uid=12345,
                ),
            ]),
        )

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()

    def _add_get_params(self, url, **kwargs):
        return '{}?{}'.format(url, urlencode(kwargs))

    def setup_roles(self, exist=True):
        if exist:
            roles = {'/role/user/access_type/view'}
        else:
            roles = {'/false/role'}
        self.fake_tvm_credentials_manager.set_existing_roles(roles)

    def test_push_history_view__simple(self):
        self.setup_historydb()
        self.setup_roles()
        url = self._add_get_params(
            reverse('push_history'),
            date_from='2022-01-01',
            date_to='2022-12-01',
            uid='12345',
        )
        response = self.client.get(url)

        for text in (
            'app_id1',
            'push_id1',
            'device_id1',
            'push_event1',
            'push_service1',
            '12345',
        ):
            self.assertContains(response, text)

        assert len(self.fake_historydb.requests) == 1
        request = self.fake_historydb.requests[0]
        request.assert_headers_contain({
            'X-Ya-Service-Ticket': 'test_ticket'
        })
        request.assert_query_contains({
            'from_ts': '1640984400',
            'to_ts': '1669928399',
            'uid': '12345',
            'consumer': 'passport-py-adm',
        })

    def test_push_history_view__full(self):
        self.setup_historydb()
        self.setup_roles()
        url = self._add_get_params(
            reverse('push_history'),
            date_from='2022-01-01',
            date_to='2022-12-01',
            uid='12345',
            device_id='abcdefg',
            app='app.yandex.',
        )
        response = self.client.get(url)

        for text in (
            'app_id1',
            'push_id1',
            'device_id1',
            'push_event1',
            'push_service1',
            '12345',
        ):
            self.assertContains(response, text)

        assert len(self.fake_historydb.requests) == 1
        request = self.fake_historydb.requests[0]
        request.assert_headers_contain({
            'X-Ya-Service-Ticket': 'test_ticket'
        })
        request.assert_query_contains({
            'from_ts': '1640984400',
            'to_ts': '1669928399',
            'uid': '12345',
            'device': 'abcdefg',
            'app': 'app.yandex.',
            'consumer': 'passport-py-adm',
        })

    def test_push_history_view__no_roles(self):
        self.setup_roles(exist=False)
        url = self._add_get_params(
            reverse('push_history'),
            date_from='2022-01-01',
            date_to='2022-12-01',
            uid='12345',
        )
        response = self.client.get(url)

        self.assertContains(response, '/role/user/access_type/view', status_code=403)
        assert len(self.fake_historydb.requests) == 0

    def test_push_view(self):
        self.setup_historydb(method='push_history_by_push_id')
        self.setup_roles()
        url = self._add_get_params(
            reverse('push'),
            push_id='push_id1',
        )
        response = self.client.get(url)

        for text in (
            'app_id1',
            'push_id1',
            'device_id1',
            'push_event1',
            'push_service1',
            '12345',
        ):
            self.assertContains(response, text)

        assert len(self.fake_historydb.requests) == 1
        request = self.fake_historydb.requests[0]
        request.assert_headers_contain({
            'X-Ya-Service-Ticket': 'test_ticket'
        })
        request.assert_query_contains({
            'push': 'push_id1',
            'consumer': 'passport-py-adm',
        })

    def test_push_view__no_role(self):
        self.setup_roles(exist=False)
        url = self._add_get_params(
            reverse('push'),
            push_id='push_id1',
        )
        response = self.client.get(url)

        self.assertContains(response, '/role/user/access_type/view', status_code=403)
        assert len(self.fake_historydb.requests) == 0
