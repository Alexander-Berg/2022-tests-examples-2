import django.contrib.auth.models as auth_models

import kazoo.exceptions
import kazoo.protocol.states

import metrika.pylib.structures.dotdict as mdd

import metrika.admin.python.zooface.frontend.tests.helper as helper

import metrika.admin.python.zooface.frontend.zooface.utils as utils
import metrika.admin.python.zooface.frontend.zooface.models as models
import metrika.admin.python.zooface.frontend.zooface.exceptions as exceptions


GROUP = 'recipe_group'
ENVIRONMENT = 'recipe_environment'
ROOT = '/zooface_test'
USERNAME = 'volozh'


class TestMisc(helper.ZoofaceBaseTestCase):
    @property
    def user(self):
        return auth_models.User.objects.get(username=USERNAME)

    def test_get_config_clusters(self):
        clusters = utils.get_config_clusters()
        for cluster in clusters:
            self.assertTrue(
                isinstance(cluster, mdd.DotDict)
            )
            for attr in ['group', 'environment', 'hosts']:
                self.assertTrue(
                    hasattr(cluster, attr)
                )

    def test_get_clusters_map(self):
        clusters = utils.get_clusters_map()
        self.assertTrue(
            isinstance(clusters, mdd.DotDict)
        )
        cluster = clusters['test_group']['test_environment']
        self.assertEqual(cluster.group, 'test_group')
        self.assertEqual(cluster.environment, 'test_environment')
        expected_hosts = [
            {'hostname': '127.0.0.1', 'port': 2183},
            {'hostname': '127.0.0.33', 'port': 2188},
        ]
        self.assertEqual(cluster.hosts, expected_hosts)
        self.assertEqual(cluster.hosts_str, '127.0.0.1:2183,127.0.0.33:2188')

    def test_get_favorite(self):
        favorite = utils.get_favorite(self.user)
        self.assertTrue(
            isinstance(favorite, models.Favorite)
        )

    def test_get_favorite_clusters(self):
        favorites = utils.get_favorite_clusters(self.user)
        value = favorites[0]
        self.assertEqual(value, 'test_group:test_environment')

    def test_is_favorite(self):
        clusters = utils.get_favorite_clusters(self.user)
        self.assertTrue(
            utils.is_favorite(clusters, 'test_group', 'test_environment'),
        )
        self.assertFalse(
            utils.is_favorite(clusters, GROUP, ENVIRONMENT),
        )

    def test_splitpath(self):
        paths = utils.splitpath('/one/two/three')
        self.assertTrue(
            isinstance(paths, list)
        )
        expected_data = [
            {'item': '/', 'path': '/'},
            {'item': 'one', 'path': '/one'},
            {'item': 'two', 'path': '/one/two'},
            {'item': 'three', 'path': '/one/two/three'}
        ]
        self.assertEqual(paths, expected_data)

        with self.assertRaises(exceptions.ZoofaceException):
            utils.splitpath(None)

        with self.assertRaises(exceptions.ZoofaceException):
            utils.splitpath(False)

        with self.assertRaises(exceptions.ZoofaceException):
            utils.splitpath('')

    def test_get_node_children(self):
        children, stat = utils.get_node_children(
            GROUP,
            ENVIRONMENT,
            f'/{ROOT}/children',
        )
        self.assertEqual(stat.numChildren, 5)
        expected_data = [
            '123',
            '5',
            'abc',
            'Abcd',
            'abcd',
        ]
        self.assertEqual(
            children,
            expected_data,
        )

        with self.assertRaises(kazoo.exceptions.NoNodeError):
            utils.get_node_children(
                GROUP,
                ENVIRONMENT,
                f'/{ROOT}/path_does_not_exist',
            )


class TestUpdateNode(helper.ZoofaceBaseTestCase):
    def get_node(self, path):
        try:
            zk = helper.get_zk_client()
            zk.start()
            return zk.get(path)
        finally:
            try:
                zk.stop()
            except Exception:
                pass

    def test_missing(self):
        with self.assertRaises(exceptions.ZookeeperTransactionError):
            utils.update_node(
                GROUP,
                ENVIRONMENT,
                USERNAME,
                f'/{ROOT}/node_does_not_exist',
                b'hello',
            )

    def test_normal(self):
        expected_value = b'Olala'
        path = f'{ROOT}/update_node'
        current_value, _ = self.get_node(path)

        utils.update_node(
            GROUP,
            ENVIRONMENT,
            USERNAME,
            path,
            expected_value,
        )

        new_value, _ = self.get_node(path)

        self.assertNotEqual(current_value, new_value)
        self.assertEqual(new_value, expected_value)


class TestDeleteNode(helper.ZoofaceBaseTestCase):
    def node_exists(self, path):
        try:
            zk = helper.get_zk_client()
            zk.start()
            return zk.exists(path)
        finally:
            try:
                zk.stop()
            except Exception:
                pass

    def test_missing(self):
        with self.assertRaises(exceptions.ZookeeperTransactionError):
            utils.delete_nodes(
                GROUP,
                ENVIRONMENT,
                USERNAME,
                f'/{ROOT}/node_does_not_exist',
            )

    def test_normal(self):
        path = f'{ROOT}/delete_node'

        self.assertTrue(self.node_exists(path))

        utils.delete_nodes(
            GROUP,
            ENVIRONMENT,
            USERNAME,
            path,
        )

        self.assertFalse(self.node_exists(path))

    def test_has_children(self):
        with self.assertRaises(exceptions.ZookeeperTransactionError):
            utils.delete_nodes(
                GROUP,
                ENVIRONMENT,
                USERNAME,
                [
                    f'/{ROOT}/children_delete/some_name',
                    f'/{ROOT}/children_delete/another_name',
                ],
            )


class TestGetNode(helper.ZoofaceBaseTestCase):
    def get_node(self, name):
        return utils.get_node(
            GROUP,
            ENVIRONMENT,
            f'{ROOT}/{name}',
        )

    def default_asserts(self, node, name):
        self.assertTrue(
            isinstance(node, utils.ZNode)
        )
        self.assertTrue(
            isinstance(node.stat, kazoo.protocol.states.ZnodeStat)
        )
        self.assertEqual(node.name, name)

    def json_asserts(self, node, name):
        self.default_asserts(node, name)
        self.assertTrue(node.is_json)
        self.assertTrue(
            isinstance(node.data, str)
        )
        self.assertTrue(
            isinstance(node.raw_data, bytes)
        )

    def test_missing(self):
        with self.assertRaises(kazoo.exceptions.NoNodeError):
            utils.get_node(
                GROUP,
                ENVIRONMENT,
                'f/{ROOT}/node_does_not_exist',
            )

    def test_null(self):
        name = 'null_node'
        node = self.get_node(name)
        self.default_asserts(node, name)
        self.assertEqual(node.data, node.raw_data)
        self.assertIs(node.data, None)
        self.assertFalse(node.is_gzip)
        self.assertFalse(node.is_json)

    def test_string(self):
        name = 'string_node'
        node = self.get_node(name)
        self.default_asserts(node, name)
        self.assertTrue(
            isinstance(node.data, str)
        )
        self.assertTrue(
            isinstance(node.raw_data, bytes)
        )
        self.assertFalse(node.is_gzip)
        self.assertFalse(node.is_json)

    def test_string_compressed(self):
        name = 'string_node_compressed'
        node = self.get_node(name)
        self.default_asserts(node, name)
        self.assertTrue(
            isinstance(node.data, str)
        )
        self.assertTrue(
            isinstance(node.raw_data, bytes)
        )
        self.assertTrue(node.is_gzip)
        self.assertFalse(node.is_json)

    def test_json(self):
        name = 'json_node'
        node = self.get_node(name)
        self.json_asserts(node, name)
        self.assertFalse(node.is_gzip)

    def test_json_compressed(self):
        name = 'json_node_compressed'
        node = self.get_node(name)
        self.json_asserts(node, name)
        self.assertTrue(node.is_gzip)
