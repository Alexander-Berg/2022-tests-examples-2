import metrika.admin.python.zooface.frontend.tests.helper as helper


GROUP = 'recipe_group'
ENVIRONMENT = 'recipe_environment'
ROOT = '/zooface_test'


class TestUI(helper.ZoofaceUiTestCase):
    def test_main_redirect(self):
        path = '/'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)

    def test_clusters(self):
        self.get_success_response('/ui/clusters/')
        self.get_success_response('/ui/ajax/clusters/')

    def test_cluster(self):
        self.get_success_response(f'/ui/clusters/{GROUP}/{ENVIRONMENT}/explorer/')
        response = self.get_success_response(f'/ui/ajax/clusters/{GROUP}/{ENVIRONMENT}/explorer/')
        self.assertFalse('NODE_MISSING_MARKER' in response.content.decode())

        self.get_success_response(f'/ui/ajax/clusters/{GROUP}/{ENVIRONMENT}/explorer/node_children/')

    def test_cluster_missing_path(self):
        self.get_success_response(f'/ui/clusters/{GROUP}/{ENVIRONMENT}/explorer/?path={ROOT}/node_does_not_exist')
        response = self.get_success_response(
            f'/ui/ajax/clusters/{GROUP}/{ENVIRONMENT}/explorer/?path={ROOT}/node_does_not_exist'
        )
        self.assertTrue('NODE_MISSING_MARKER' in response.content.decode())

        self.get_missing_response(
            f'/ui/ajax/clusters/{GROUP}/{ENVIRONMENT}/explorer/node_children/?path={ROOT}/node_does_not_exist'
        )

    def test_app_ping(self):
        path = '/ping/app'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
