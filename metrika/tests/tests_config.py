import django.test
import metrika.admin.python.bishop.frontend.bishop.models as bp_models


class BishopConfigApiTestcase(django.test.TestCase):
    fixtures = ('metrika/admin/python/bishop/frontend/bishop/fixtures/tests_data.json',)

    def setUp(self):
        self.client = django.test.Client()


class TestVersionHandler(BishopConfigApiTestcase):
    program_name = 'httpd'
    environment_name = 'root.programs.httpd.production'
    url = '/api/v2/version/{}/{}'.format(
        program_name,
        environment_name,
    )

    def test_normal(self):
        config = bp_models.Config.objects.get(
            program__name=self.program_name,
            environment__name=self.environment_name,
            active=True,
        )
        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            int(response['bishop-config-version']),
            config.version,
        )
        self.assertEqual(
            response['bishop-config-format'],
            config.format,
        )

    def test_missing_program(self):
        missing_program_url = '/api/v2/version/{}/{}'.format(
            self.program_name[:-1],
            self.environment_name,
        )
        response = self.client.head(missing_program_url)
        self.assertEqual(response.status_code, 404)

    def test_missing_environment(self):
        missing_environment_url = '/api/v2/version/{}/{}'.format(
            self.program_name,
            self.environment_name[:-1],
        )
        response = self.client.head(missing_environment_url)
        self.assertEqual(response.status_code, 404)

    def test_get_restricted(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_restricted(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class TestConfigHandler(BishopConfigApiTestcase):
    program_name = 'httpd'
    environment_name = 'root.programs.httpd.production'
    url = '/api/v2/config/{}/{}'.format(
        program_name,
        environment_name,
    )

    def test_normal(self):
        config = bp_models.Config.objects.get(
            program__name=self.program_name,
            environment__name=self.environment_name,
            active=True,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), config.text)
        self.assertEqual(
            int(response['bishop-config-version']),
            config.version,
        )
        self.assertEqual(
            response['bishop-config-format'],
            config.format,
        )

    def test_missing_program(self):
        missing_program_url = '/api/v2/config/{}/{}'.format(
            self.program_name[:-1],
            self.environment_name,
        )
        response = self.client.get(missing_program_url)
        self.assertEqual(response.status_code, 404)

    def test_missing_environment(self):
        missing_environment_url = '/api/v2/config/{}/{}'.format(
            self.program_name,
            self.environment_name[:-1],
        )
        response = self.client.get(missing_environment_url)
        self.assertEqual(response.status_code, 404)

    def test_not_attached(self):
        missing_environment_url = '/api/v2/config/{}/{}'.format(
            self.program_name,
            'root.programs',
        )
        response = self.client.get(missing_environment_url)
        self.assertEqual(response.status_code, 400)

    def test_post_restricted(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    def test_head_restricted(self):
        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 405)
