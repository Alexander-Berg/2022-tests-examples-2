import pytest

import metrika.pylib.bstr.getter as bstr_getter


class BstrTestGetter(bstr_getter.MainGetter):
    def __init__(self):
        super(BstrTestGetter, self).__init__(
            name="MainGetter",
            checks=[
                {'name': 'bstr_runner', 'slave_class': bstr_getter.BstrThread},
                {'name': 'dicts_checker', 'slave_class': bstr_getter.FilesChecker},
            ]
        )

    def get_config(self):
        return {
            'bstr': {
                'root': 'qwe',
                'files': ['asd', 'qwe']
            },
            'master': {
                'logger_settings': {
                    'stdout': True,
                },
            },
        }


@pytest.fixture()
def getter():
    # TODO: use YT mocks
    BstrTestGetter()


def test_simple(getter):
    assert True
