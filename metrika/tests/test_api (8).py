import json

import metrika.admin.python.zooface.frontend.tests.helper as helper


GROUP = 'recipe_group'
ENVIRONMENT = 'recipe_environment'
ROOT = '/zooface_test'


class TestApi(helper.ZoofaceApiTestCase):
    def test_audit(self):
        post_data = json.dumps({
            'created': '2020-01-19 00:45:25',
            'group': 'test_group',
            'environment': 'test_environment',
            'uuid': 'uuid',
            'action': 'create',
            'nodes': [
                '/asdf',
                '/ctf'
            ],
            'nodes_text': 'hello',
            'username': 'robert',
        })
        response = self.client.post(
            f'/api/v1/clusters/{GROUP}/{ENVIRONMENT}/audit/',
            post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
