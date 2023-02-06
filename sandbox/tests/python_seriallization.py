import os
import textwrap

from sandbox.projects.browser.merge.common import python_seriallization


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(SCRIPT_DIR, 'test_data')


class TestsGclientConfig(object):
    def test_load_gclient_config(self):
        gclient_config = textwrap.dedent('''\
            solutions = [
              { "name"        : "src",
                "url"         : "https://bitbucket.browser.yandex-team.ru/scm/CHROMIUM/src.git",
                "deps_file"   : ".DEPS.git",
                "managed"     : False,
                "custom_deps" : {
                },
              },
            ]
            cache_dir = None
            ''')

        data = python_seriallization.load_python_code(gclient_config)

        assert data == {
            'solutions': [
                {
                    'name': 'src',
                    'url': 'https://bitbucket.browser.yandex-team.ru/scm/CHROMIUM/src.git',
                    'deps_file': '.DEPS.git',
                    'managed': False,
                    'custom_deps': {
                    },
                },
            ],
            'cache_dir': None,
        }

    def test_save_gclient_config(self):
        data = {
            'solutions': [
                {
                    'name': 'src',
                    'url': None,
                    'deps_file': '.DEPS.git',
                    'managed': False,
                    'custom_deps': {
                    },
                },
            ],
            'cache_dir': None,
        }

        gclient_config = python_seriallization.format_as_python(
            data, indent=' '*2, pretty=True)
        assert gclient_config == textwrap.dedent('''\

            cache_dir = None

            solutions = [
              {
                'custom_deps': {},
                'deps_file': '.DEPS.git',
                'managed': False,
                'name': 'src',
                'url': None,
              },
            ]
            ''')
