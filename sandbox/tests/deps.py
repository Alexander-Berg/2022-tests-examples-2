import json
import os

from sandbox.projects.browser.merge.common import deps


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(SCRIPT_DIR, 'test_data')


class TestsDeps(object):
    def byteify(self, data):
        if isinstance(data, unicode):
            return data.encode('utf-8')
        if isinstance(data, list):
            return [self.byteify(item) for item in data]
        if isinstance(data, dict):
            return {
                self.byteify(key): self.byteify(value)
                for key, value in data.iteritems()
            }
        return data

    def test_load_chromium_deps(self):
        with open(os.path.join(TEST_DATA_DIR, 'DEPS.original')) as f:
            code = f.read()

        with open(os.path.join(TEST_DATA_DIR, 'DEPS.json')) as f:
            expected_data = deps.Deps(self.byteify(json.load(f)))

        data = deps.Deps.from_string(code)

        assert data == expected_data

    def test_save_chromium_deps(self):
        with open(os.path.join(TEST_DATA_DIR, 'DEPS.json')) as f:
            data = deps.Deps(self.byteify(json.load(f)))

        with open(os.path.join(TEST_DATA_DIR, 'DEPS.formatted')) as f:
            expected_code = f.read()

        code = data.seriallize(2017)

        assert code == expected_code
