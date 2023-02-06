import django.http
from unittest.mock import Mock

from django.contrib.auth.models import User
from django.test import RequestFactory
from parameterized import parameterized

from metrika.admin.python.zooface.frontend.tests.helper import ZoofaceBaseTestCase
from metrika.admin.python.zooface.frontend.zooface.decorators import check_cluster, roles_required
from metrika.admin.python.zooface.frontend.zooface.models import UserRole
from metrika.admin.python.zooface.frontend.zooface.utils import get_clusters_map


class TestCheckCluster(ZoofaceBaseTestCase):
    @staticmethod
    @check_cluster
    def func(request, *args, **kwargs):
        return True

    def test_check_cluster_exists(self):
        request = Mock()
        self.assertTrue(self.func(request, group='test1', environment='test2'))
        self.assertEqual(request.cluster, get_clusters_map()['test1']['test2'])

    def test_check_cluster_doesnt_exist(self):
        with self.assertRaises(django.http.Http404):
            self.func(Mock(), group='lul', environment='kek')


class TestRolesRequired(ZoofaceBaseTestCase):
    @staticmethod
    @roles_required(UserRole.WRITER)
    def writer(request, *args, **kwargs):
        return True

    @staticmethod
    @roles_required(UserRole.WRITER, UserRole.READER)
    def reader_or_writer(request, *args, **kwargs):
        return True

    @parameterized.expand([
        (1, 'test1', 'test1', {'writer'}),
        (2, 'test1', 'test1', {'writer', 'reader'}),
    ])
    def test_check_writer_ok(self, user, group, environment, roles):
        request = Mock()
        request.user = User.objects.get(id=user)
        self.assertTrue(self.writer(request, group=group, environment=environment))
        self.assertEqual(request.user_roles, roles)

    @parameterized.expand([
        (1, 'test2', 'test1'),
        (2, 'test2', 'test2'),
    ])
    def test_check_writer_error(self, user, group, environment):
        request = RequestFactory().get('/')
        request.user = User.objects.get(id=user)
        self.assertTrue(self.writer(request, group=group, environment=environment).status_code, 403)

    @parameterized.expand([
        (1, 'test1', 'test1', {'writer'}),
        (1, 'test2', 'test1', {'reader'}),
        (2, 'test1', 'test1', {'writer', 'reader'}),
    ])
    def test_check_reader_or_writer_ok(self, user, group, environment, roles):
        request = Mock()
        request.user = User.objects.get(id=user)
        self.assertTrue(self.reader_or_writer(request, group=group, environment=environment))
        self.assertEqual(request.user_roles, roles)

    @parameterized.expand([
        (2, 'test2', 'test2'),
    ])
    def test_check_reader_or_writer_error(self, user, group, environment):
        request = RequestFactory().get('/')
        request.user = User.objects.get(id=user)
        self.assertTrue(self.reader_or_writer(request, group=group, environment=environment).status_code, 403)
