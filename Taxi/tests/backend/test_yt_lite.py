from odoo.tests import SavepointCase, tagged
from common.client import yt_lite
from yt.wrapper import YtHttpResponseError


'''
Тест только для локального запуска, проверки корректности работы YT клиента

раскомментирорвать только для локальных проверок
'''

# @tagged('lavka', 'yt_lite')
# class TestYTLite(SavepointCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.only_hahn_path = '//home/lavka/testing/yt_lite_test/only_hahn'
#         cls.only_arnold_path = '//home/lavka/testing/yt_lite_test/only_arnold'
#         cls.both_path = '//home/lavka/testing/yt_lite_test/both'
#         cls.nowhere_path = '//home/lavka/testing/yt_lite_test/nowhere'
#
#     def test_read_hahn(self):
#         self.assertTrue(yt_lite.table_exists(self.only_hahn_path),
#                         'only_hahn table does not exists anywhere')
#         self.assertTrue(yt_lite.table_exists(self.only_hahn_path, 'hahn'),
#                         'only_hahn table does not exists in hahn')
#         self.assertFalse(yt_lite.table_exists(self.only_hahn_path, 'arnold'),
#                          'only_hahn table should not exist in arnold')
#         self.assertIsNotNone(yt_lite.read_table(self.only_hahn_path),
#                              'no data from hahn without check_exists')
#         self.assertIsNotNone(yt_lite.read_table(self.only_hahn_path, check_exists=True),
#                              'no data from hahn with check_exists')
#         with self.assertRaises(YtHttpResponseError, msg='only_arnold table found in hahn'):
#             yt_lite.read_table(self.only_arnold_path, 'hahn')
#         self.assertIsNone(yt_lite.read_table(self.only_arnold_path, 'hahn', check_exists=True),
#                           'only_arnold table found in hahn')
#
#     def test_read_arnold(self):
#         self.assertTrue(yt_lite.table_exists(self.only_arnold_path),
#                         'only_arnold table does not exists anywhere')
#         self.assertTrue(yt_lite.table_exists(self.only_arnold_path, 'arnold'),
#                         'only_arnold table does not exists in arnold')
#         self.assertFalse(yt_lite.table_exists(self.only_arnold_path, 'hahn'),
#                          'only_arnold table table should not exist in hahn')
#         self.assertIsNotNone(yt_lite.read_table(self.only_arnold_path),
#                              'no data from arnold without check_exists')
#         self.assertIsNotNone(yt_lite.read_table(self.only_arnold_path, check_exists=True),
#                              'no data from arnold with check_exists')
#
#     def test_read_both(self):
#         self.assertTrue(yt_lite.table_exists(self.both_path),
#                         '"both" table does not exists anywhere')
#         self.assertTrue(yt_lite.table_exists(self.both_path, 'arnold'),
#                         '"both" table does not exists in arnold')
#         self.assertTrue(yt_lite.table_exists(self.both_path, 'hahn'),
#                         '"both" table does not exist in hahn')
#         self.assertIsNotNone(yt_lite.read_table(self.both_path),
#                              'no data from "both" without check_exists')
#         self.assertIsNotNone(yt_lite.read_table(self.both_path, check_exists=True),
#                              'no data from "both" with check_exists')
#
#     def test_read_nowhere(self):
#         self.assertFalse(yt_lite.table_exists(self.nowhere_path),
#                         '"nowhere" table should not exists anywhere')
#         self.assertFalse(yt_lite.table_exists(self.nowhere_path, 'arnold'),
#                         '"nowhere" table should not exists in arnold')
#         self.assertFalse(yt_lite.table_exists(self.nowhere_path, 'hahn'),
#                         '"nowhere" table should not exist in hahn')
#
#         with self.assertRaises(YtHttpResponseError, msg='nowhere table found anywhere'):
#             yt_lite.read_table(self.nowhere_path)
#         self.assertIsNone(yt_lite.read_table(self.nowhere_path, check_exists=True),
#                           'nowhere table found in anywhere')
#
#         with self.assertRaises(YtHttpResponseError, msg='nowhere table found hahn'):
#             yt_lite.read_table(self.nowhere_path, 'hahn')
#         self.assertIsNone(yt_lite.read_table(self.nowhere_path, 'hahn', check_exists=True),
#                           'nowhere table found in hahn')
#
#         with self.assertRaises(YtHttpResponseError, msg='nowhere table found arnold'):
#             yt_lite.read_table(self.nowhere_path, 'arnold')
#         self.assertIsNone(yt_lite.read_table(self.nowhere_path, 'arnold', check_exists=True),
#                           'nowhere table found in arnold')
