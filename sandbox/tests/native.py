import unittest

from sandbox.projects.devtools.YaTestParent2 import native


class TestNative(unittest.TestCase):
    def test_converts_missing(self):
        result = native.convert_native_results([], '{"targets": {"devtools/ymake": {"hid": "13003758617330431651"}}}')

        self.assertEqual(
            result,
            [
                {
                    'hid': 13003758617330431651,
                    'id': '13003758617330431651',
                    'name': 'native_build',
                    'owners': {'groups': [], 'logins': []},
                    'path': "devtools/ymake",
                    'rich-snippet': 'missing',
                    'status': 'FAILED',
                    'suite': True,
                    'suite_status': 'FAILED',
                    'toolchain': 'native_build',
                    'type': 'native_build',
                    'uid': '',
                }
            ],
        )

    def test_converts(self):
        result = native.convert_native_results(
            [{"path": "devtools/ymake", "status": "OK", "uid": "test"}],
            '{"targets": {"devtools/ymake": {"hid": "13003758617330431651"}}}'
        )

        self.assertEqual(
            result,
            [
                {
                    'hid': 13003758617330431651,
                    'id': '13003758617330431651',
                    'name': 'native_build',
                    'owners': {'groups': [], 'logins': []},
                    'path': "devtools/ymake",
                    'rich-snippet': '',
                    'status': 'OK',
                    'suite': True,
                    'suite_status': 'OK',
                    'toolchain': 'native_build',
                    'type': 'native_build',
                    'uid': 'test',
                }
            ],
        )
