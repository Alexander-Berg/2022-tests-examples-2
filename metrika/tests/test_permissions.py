from django.contrib.auth.models import User
from parameterized import parameterized

from metrika.admin.python.zooface.frontend.tests.helper import ZoofaceBaseTestCase
from metrika.admin.python.zooface.frontend.zooface.idm import permissions


class TestPermissions(ZoofaceBaseTestCase):
    @parameterized.expand([
        (
            1,
            {
                'recipe_environment': {'recipe_group': {'writer'}},
                'test1': {'test1': {'writer'}, 'test2': {'reader'}},
                'test2': {'test2': {'reader'}},
            }
        ),
        (
            2,
            {
                'test1': {'test1': {'reader', 'writer'}, 'test2': {'reader'}},
            }
        ),
    ])
    def test_get_user_clusters(self, user, clusters):
        self.assertEqual(
            permissions.get_user_clusters(User.objects.get(id=user)),
            clusters,
            msg=user
        )

    @parameterized.expand([
        (
            1,
            [
                ('recipe_group', 'recipe_environment', {'writer'}),
                ('test_group', 'test_environment', None),
                ('test1', 'test1', {'writer'}),
                ('test2', 'test1', {'reader'}),
                ('test1', 'test2', None),
                ('test2', 'test2', {'reader'}),
            ]
        ),
        (
            2,
            [
                ('recipe_group', 'recipe_environment', None),
                ('test_group', 'test_environment', None),
                ('test1', 'test1', {'reader', 'writer'}),
                ('test2', 'test1', {'reader'}),
                ('test1', 'test2', None),
                ('test2', 'test2', None),
            ]
        ),
    ])
    def test_get_clusters(self, user, clusters):
        expected = [
            dict(group=cluster[0], environment=cluster[1], roles=cluster[2])
            for cluster in clusters
        ]
        actual = [
            dict(group=cluster['group'], environment=cluster['environment'], roles=cluster['roles'])
            for cluster in permissions.get_clusters(User.objects.get(id=user))
        ]
        self.assertCountEqual(expected, actual, msg=f'{user} {actual}')

    @parameterized.expand([
        (1, 'test1', 'test1', {'writer'}),
        (1, 'test2', 'test1', {'reader'}),
        (1, 'test1', 'test2', set()),
        (2, 'test1', 'test1', {'writer', 'reader'}),
        (2, 'test2', 'test1', {'reader'}),
        (2, 'test1', 'test2', set()),
    ])
    def test_get_roles(self, user, group, environment, roles):
        self.assertEqual(
            permissions.get_roles(User.objects.get(id=user), group, environment),
            roles,
            msg=f'{user} {group} {environment}'
        )
