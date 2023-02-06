import os
import gzip

import django.test

import kazoo.client


class ZoofaceBaseTestCase(django.test.TestCase):
    fixtures = ('metrika/admin/python/zooface/frontend/zooface/fixtures/tests_data.json',)

    def setUp(self):
        self.client = django.test.Client()


class ZoofaceApiTestCase(ZoofaceBaseTestCase):
    pass


class ZoofaceUiTestCase(ZoofaceBaseTestCase):
    def get_success_response(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response

    def get_missing_response(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        return response


def get_zk_client():
    zk_host = os.environ['RECIPE_ZOOKEEPER_HOST']
    zk_port = os.environ['RECIPE_ZOOKEEPER_PORT']
    zk_string = f'{zk_host}:{zk_port}'
    return kazoo.client.KazooClient(hosts=zk_string)


def load_zk_data():
    try:
        zk = get_zk_client()
        zk.start()
        root_path = '/zooface_test'
        zk.create('/zooface_test')
        audit_path = f'{root_path}/audit'
        children_path = f'{root_path}/children'
        children_delete_path = f'{root_path}/children_delete'
        zk.create(audit_path)
        zk.create(children_path)
        zk.create(children_delete_path)

        zk.create(f'{children_path}/Abcd')
        zk.create(f'{children_path}/abc')
        zk.create(f'{children_path}/abcd')
        zk.create(f'{children_path}/5')
        zk.create(f'{children_path}/123')

        zk.create(f'{children_delete_path}/some_name')
        zk.create(f'{children_delete_path}/some_name/child1')
        zk.create(f'{children_delete_path}/some_name/child2')
        zk.create(f'{children_delete_path}/another_name')

        json_value = '{"Hello": ["World"]}'.encode()
        json_value_compressed = gzip.compress(json_value)
        null_value = None
        string_value = 'Hello, World'.encode()
        string_value_compressed = gzip.compress(string_value)

        zk.create(f'{root_path}/json_node', json_value)
        zk.create(f'{root_path}/json_node_compressed', json_value_compressed)
        zk.create(f'{root_path}/string_node', string_value)
        zk.create(f'{root_path}/string_node_compressed', string_value_compressed)
        zk.create(f'{root_path}/null_node', null_value)

        zk.create(f'{root_path}/update_node', null_value)
        zk.create(f'{root_path}/delete_node', null_value)

    finally:
        try:
            zk.stop()
        except Exception:
            pass
