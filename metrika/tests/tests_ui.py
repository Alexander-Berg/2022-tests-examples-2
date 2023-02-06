from django.test.utils import override_settings

import metrika.admin.python.clickhouse_rbac.frontend.tests.helper as tests_helper

import metrika.admin.python.clickhouse_rbac.frontend.rbac.models as rbac_models


class TestViews(tests_helper.ClickHouseRBACTestCase):
    def test_main(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_profile(self):
        user = rbac_models.ClickHouseUser.objects.get(name='volozh')
        response = self.client.get('/ui/profile')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn(
            'this is awesome yav uuid',
            content,
        )
        for access in user.access_set.all():
            access_marker = f'{access.cluster} MARKER'
            self.assertIn(
                access_marker,
                content,
            )

    def test_users(self):
        response = self.client.get('/ui/users')
        self.assertEqual(response.status_code, 200)

    def test_system(self):
        response = self.client.get('/ui/system')
        self.assertEqual(response.status_code, 200)

    def test_users_no_access(self):
        with override_settings(YAUTH_TEST_USER='misha'):
            response = self.client.get('/ui/users')
            self.assertEqual(response.status_code, 302)

    def test_system_no_access(self):
        with override_settings(YAUTH_TEST_USER='misha'):
            response = self.client.get('/ui/system')
            self.assertEqual(response.status_code, 302)


class TestAjax(tests_helper.ClickHouseRBACTestCase):
    def test_users(self):
        response = self.client.get('/ui/ajax/users')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(
            'vova',
            data['html'],
        )
        self.assertIn(
            'volozh',
            data['html'],
        )

    def test_users_no_access(self):
        with override_settings(YAUTH_TEST_USER='misha'):
            response = self.client.get('/ui/ajax/users')
            self.assertEqual(response.status_code, 403)
            data = response.json()
            self.assertEqual(
                'Access Denied',
                data['error'],
            )
