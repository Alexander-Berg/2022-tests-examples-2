import json
import mock

from django.contrib.auth.models import User
from django.test import TestCase

from passport_grants_configurator.apps.core.export_utils import (
    BaseExporter,
    FancyEncoder,
)
from passport_grants_configurator.apps.core.models import Namespace


class TextExportUtilsCase(TestCase):
    fixtures = ['default.json']

    def test_fancy_encoder(self):
        self.assertEqual(
            json.dumps({2: [3, 1, 2], 1: {3, 1, 2}, 3: 'string'}, cls=FancyEncoder),
            '{"1": [1, 2, 3], "2": [3, 1, 2], "3": "string"}',
        )

        with self.assertRaises(TypeError):
            json.dumps(frozenset([1, 2]), cls=FancyEncoder)

    def test_base_exporter_not_implemented_methods(self):
        exporter = BaseExporter(
            namespaces=Namespace.objects.all(),
            git_api={
                'project': None,
                'working_dir': '',
                'repo': None,
            },
            user=User.objects.get(id=1),
            env_filenames={},
        )
        with self.assertRaises(NotImplementedError):
            exporter.import_grants()

        with self.assertRaises(NotImplementedError):
            exporter.update_grants()

        with self.assertRaises(NotImplementedError):
            exporter.export_grants()

    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.is_dry_run')
    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.prepare')
    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.import_grants')
    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.update_grants')
    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.export_grants')
    def test_export_grants_manual_resolve(self, export_mock, update_mock, import_mock, prepare_mock, is_dry_mock):
        exporter = BaseExporter(
            namespaces=Namespace.objects.all(),
            git_api={
                'project': None,
                'working_dir': '',
                'repo': None,
            },
            user=User.objects.get(id=1),
            env_filenames={},
        )
        diff = {'manual_resolve': [''], 'warnings': ['127.0.0.1'], 'diff': '+1'}

        is_dry_mock.__get__ = mock.Mock(return_value=0)
        prepare_mock.return_value = 1
        import_mock.return_value = 1
        update_mock.return_value = diff
        export_mock.return_value = 1

        res = exporter.export()
        self.assertEqual(res, diff)
        self.assertEqual(prepare_mock.call_count, 1)
        self.assertEqual(import_mock.call_count, 1)
        self.assertEqual(update_mock.call_count, 1)
        self.assertEqual(export_mock.call_count, 0)

    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.is_dry_run')
    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.prepare')
    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.import_grants')
    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.update_grants')
    @mock.patch('passport_grants_configurator.apps.core.export_utils.BaseExporter.export_grants')
    def test_export_grants(self, export_mock, update_mock, import_mock, prepare_mock, is_dry_mock):
        exporter = BaseExporter(
            namespaces=Namespace.objects.all(),
            git_api={
                'project': None,
                'working_dir': '',
                'repo': None,
            },
            user=User.objects.get(id=1),
            env_filenames={},
        )
        diff = {'manual_resolve': [], 'warnings': ['127.0.0.1'], 'diff': '+1'}

        is_dry_mock.__get__ = mock.Mock(return_value=0)
        prepare_mock.return_value = 1
        import_mock.return_value = 1
        update_mock.return_value = diff
        export_mock.return_value = 1

        res = exporter.export()
        self.assertEqual(res, diff)
        self.assertEqual(prepare_mock.call_count, 1)
        self.assertEqual(import_mock.call_count, 1)
        self.assertEqual(update_mock.call_count, 1)
        self.assertEqual(export_mock.call_count, 1)
