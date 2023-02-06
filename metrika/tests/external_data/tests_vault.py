import unittest.mock

import metrika.admin.python.bishop.frontend.bishop.utils as bp_utils

import metrika.admin.python.bishop.frontend.bishop.models as bp_models

import metrika.admin.python.bishop.frontend.tests.data as tests_data
import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas


class TestRefreshVault(tests_helper.BishopApiTestCase):
    @unittest.mock.patch.object(
        bp_utils,
        'get_vault_data',
        new=unittest.mock.Mock(return_value=tests_data.vault)
    )
    def test_one_changed(self):
        program = bp_models.Program.objects.get(name='vault_test')
        environment = bp_models.Environment.objects.get(name='root.vault_test')
        current_config = bp_models.Config.objects.get(
            program=program,
            environment=environment,
            active=True,
        )

        self.assertTrue(current_config.active)
        self.assertEqual(
            current_config.text,
            'ver-01ckx62bm2j00f44sag2910hn4',
        )

        response = self.client.post(
            '/api/v1/refresh_vault',
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )

        latest_config = bp_models.Config.objects.get(
            program=program,
            environment=environment,
            active=True,
        )
        self.assertNotEqual(
            current_config.version,
            latest_config.version,
        )
        self.assertTrue(latest_config.use_vault)
        self.assertEqual(
            latest_config.text,
            'ver-01ckx62bm2j00f44sag2910hn5',
        )
        self.assertEqual(
            latest_config.vaults,
            ['sec-01ckx62bkvpee201ks4d4a1g09'],
        )

    @unittest.mock.patch.object(
        bp_utils,
        'get_vault_data',
        new=unittest.mock.Mock(return_value=tests_data.vault)
    )
    def test_one_not_changed(self):
        program = bp_models.Program.objects.get(name='vault_test_2')
        environment = bp_models.Environment.objects.get(
            name='root.vault_test',
        )
        current_config = bp_models.Config.objects.get(
            program=program,
            environment=environment,
            active=True,
        )

        self.assertTrue(current_config.active)
        self.assertEqual(
            current_config.text,
            'ver-01e20d0n56j1c4dy39mm6jzv2y',
        )

        response = self.client.post(
            '/api/v1/refresh_vault',
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )

        latest_config = bp_models.Config.objects.get(
            program=program,
            environment=environment,
            active=True,
        )
        self.assertEqual(
            current_config.version,
            latest_config.version,
        )

    @unittest.mock.patch.object(
        bp_utils,
        'get_vault_data',
        new=unittest.mock.Mock(return_value=tests_data.vault)
    )
    def test_one_broken(self):
        program = bp_models.Program.objects.get(name='vault_test_3')
        environment = bp_models.Environment.objects.get(
            name='root.vault_test',
        )
        current_config = bp_models.Config.objects.get(
            program=program,
            environment=environment,
            active=True,
        )

        self.assertTrue(current_config.active)
        self.assertEqual(
            current_config.text,
            'ver-01e1cj41kragzj58pjgapzbctj',
        )

        response = self.client.post(
            '/api/v1/refresh_vault',
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )

        latest_config = bp_models.Config.objects.get(
            program=program,
            environment=environment,
            active=True,
        )
        self.assertEqual(
            current_config.version,
            latest_config.version,
        )
        self.assertTrue(latest_config.state.broken)
