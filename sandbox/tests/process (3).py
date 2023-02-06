import os

from sandbox.sandboxsdk import process


class TestCustomOsEnviron:
    def test__simple_setting(self):
        with process.CustomOsEnviron({'FOO': 'BAR'}):
            assert 'FOO' in os.environ
            assert os.environ['FOO'] == 'BAR'
        assert 'FOO' not in os.environ

    def test__overwrite(self):
        os.environ['FOO'] = 'BAR'
        with process.CustomOsEnviron({'FOO': 'BAZ'}):
            assert 'FOO' in os.environ
            assert os.environ['FOO'] == 'BAZ'
        assert 'FOO' in os.environ
        assert os.environ['FOO'] == 'BAR'
        del os.environ['FOO']
