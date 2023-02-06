import unittest.mock

import metrika.admin.python.bishop.frontend.bishop.utils as bp_utils

import metrika.admin.python.bishop.frontend.bishop.models as bp_models

import metrika.admin.python.bishop.frontend.tests.data as tests_data
import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas


class TestRefreshYandexCloudHosts(tests_helper.BishopApiTestCase):
    def _get_active_config(self, program, environment):
        config = bp_models.Config.objects.get(
            program=program,
            environment=environment,
            active=True,
        )
        self.assertTrue(config.active)
        return config

    @unittest.mock.patch.object(
        bp_utils,
        'get_yc_clusters',
        new=unittest.mock.Mock(return_value=tests_data.yc_clusters)
    )
    def test_normal(self):
        current_1_text = 'Metrica-test'
        current_2_text = 'cdp'
        expected_1_text = 'Metrica-test-changed-for-test'
        expected_2_text = current_2_text

        environment = bp_models.Environment.objects.get(name='root.yc_clusters_test')
        program_1 = bp_models.Program.objects.get(name='yc_clusters_test_1')
        program_2 = bp_models.Program.objects.get(name='yc_clusters_test_2')

        current_1 = self._get_active_config(program_1, environment)
        current_2 = self._get_active_config(program_2, environment)

        self.assertTrue(current_1.use_yc_clusters)
        self.assertTrue(current_2.use_yc_clusters)
        self.assertEqual(current_1.yc_clusters_ids, ['mdb5613cdndsfitkfm7s'])
        self.assertEqual(current_2.yc_clusters_ids, ['mdbcgg3ua7bothld2oh0'])

        self.assertEqual(current_1.text, current_1_text)
        self.assertEqual(current_2.text, current_2_text)

        response = self.client.post('/api/v1/refresh_yc_clusters')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )

        latest_1 = self._get_active_config(program_1, environment)
        latest_2 = self._get_active_config(program_2, environment)

        self.assertNotEqual(current_1.version, latest_1.version)
        self.assertEqual(current_2.version, latest_2.version)

        self.assertTrue(latest_1.use_yc_clusters)

        self.assertEqual(latest_1.text, expected_1_text)
        self.assertEqual(latest_2.text, expected_2_text)

        self.assertEqual(latest_1.yc_clusters_ids, ['mdb5613cdndsfitkfm7s'])
        self.assertEqual(latest_2.yc_clusters_ids, ['mdbcgg3ua7bothld2oh0'])

    @unittest.mock.patch.object(
        bp_utils,
        'get_yc_clusters',
        new=unittest.mock.Mock(return_value={})
    )
    def test_broken(self):
        environment = bp_models.Environment.objects.get(name='root.yc_clusters_test')
        program_1 = bp_models.Program.objects.get(name='yc_clusters_test_1')
        program_2 = bp_models.Program.objects.get(name='yc_clusters_test_2')

        state_1 = bp_models.ConfigState.objects.get(program=program_1, environment=environment)
        state_2 = bp_models.ConfigState.objects.get(program=program_2, environment=environment)

        self.assertFalse(state_1.broken)
        self.assertFalse(state_2.broken)

        response = self.client.post('/api/v1/refresh_yc_clusters')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )

        state_1.refresh_from_db()
        state_2.refresh_from_db()

        self.assertTrue(state_1.broken)
        self.assertTrue(state_2.broken)

    @unittest.mock.patch.object(
        bp_utils,
        'get_yc_clusters',
        new=unittest.mock.Mock(return_value=tests_data.yc_clusters)
    )
    def test_cleanup(self):
        environment = bp_models.Environment.objects.get(name='root.yc_clusters_test')
        program = bp_models.Program.objects.get(name='yc_clusters_test_1')
        config = self._get_active_config(program, environment)
        self.assertTrue(config.use_yc_clusters)
        self.assertEqual(config.yc_clusters_ids, ['mdb5613cdndsfitkfm7s'])

        response = program.template.update(
            request=self._request,
            response=self._response,
            text="clear",
            format='plaintext',
        )
        self.assertTrue(response.result)

        config = self._get_active_config(program, environment)
        self.assertFalse(config.use_yc_clusters)
        self.assertEqual(config.yc_clusters_ids, [])

    @unittest.mock.patch.object(
        bp_utils,
        'get_yc_clusters',
        new=unittest.mock.Mock(return_value=tests_data.yc_clusters)
    )
    def test_single_yc_cluster_ids(self):
        environment = bp_models.Environment.objects.get(name='root.yc_clusters_test')
        program = bp_models.Program.objects.get(name='yc_clusters_test_3')

        config = self._get_active_config(program, environment)
        self.assertFalse(config.use_yc_clusters)
        self.assertEqual(config.yc_clusters_ids, [])

        response = program.template.update(
            request=self._request,
            response=self._response,
            text="{{ yc_clusters['mdb5613cdndsfitkfm7s']['name'] }}",
            format='plaintext',
        )
        self.assertTrue(response.result)

        config = self._get_active_config(program, environment)
        self.assertTrue(config.use_yc_clusters)
        self.assertEqual(config.yc_clusters_ids, ['mdb5613cdndsfitkfm7s'])

    @unittest.mock.patch.object(
        bp_utils,
        'get_yc_clusters',
        new=unittest.mock.Mock(return_value=tests_data.yc_clusters)
    )
    def test_double_yc_cluster_ids(self):
        environment = bp_models.Environment.objects.get(name='root.yc_clusters_test')
        program = bp_models.Program.objects.get(name='yc_clusters_test_3')

        config = self._get_active_config(program, environment)
        self.assertFalse(config.use_yc_clusters)
        self.assertEqual(config.yc_clusters_ids, [])

        response = program.template.update(
            request=self._request,
            response=self._response,
            text="{{ yc_clusters['mdb5613cdndsfitkfm7s']['name'] }}{{ yc_clusters['mdbcgg3ua7bothld2oh0']['name'] }}",
            format='plaintext',
        )
        self.assertTrue(response.result)

        config = self._get_active_config(program, environment)
        self.assertTrue(config.use_yc_clusters)
        self.assertEqual(
            sorted(config.yc_clusters_ids),
            sorted(['mdb5613cdndsfitkfm7s', 'mdbcgg3ua7bothld2oh0'])
        )

    @unittest.mock.patch.object(
        bp_utils,
        'get_yc_clusters',
        new=unittest.mock.Mock(return_value=tests_data.yc_clusters)
    )
    def test_yc_cluster_ids_with_items(self):
        environment = bp_models.Environment.objects.get(name='root.yc_clusters_test')
        program = bp_models.Program.objects.get(name='yc_clusters_test_3')

        config = self._get_active_config(program, environment)
        self.assertFalse(config.use_yc_clusters)
        self.assertEqual(config.yc_clusters_ids, [])

        response = program.template.update(
            request=self._request,
            response=self._response,
            text="{% for cid, value in yc_clusters.items() %}{{ cid }}{% endfor %}",
            format='plaintext',
        )
        self.assertTrue(response.result)

        config = self._get_active_config(program, environment)
        self.assertTrue(config.use_yc_clusters)
        self.assertEqual(
            sorted(config.yc_clusters_ids),
            sorted(tests_data.yc_clusters.keys())
        )
