from sandbox.projects.k50.sow_map_reduce import get_map_reducer_builder
import tempfile
from yt.wrapper.file_commands import LocalFile
import library.python.resource as lpr
import pytest

SOURCE_DIR = 'sandbox/projects/k50/sow_map_reduce/'

HISTORICAL_TABLES = [
    '//2020-01-01',
    '//2020-01-08',
    '//2020-01-15'
]
NON_HISTORICAL_TABLES = [
    '//table1',
    '//table2',
    '//table3',

]

HISTORICAL_RES_TABLE = '//2020-01-01'
NON_HISTORICAL_RES_TABLE = '//table1'

HISTORICAL_EXPECTED_TABLE = '//expected_historical'
NON_HISTORICAL_EXPECTED_TABLE = '//expected_non_historical'


@pytest.mark.parametrize("testdata, expected", [
    ({'source_table': HISTORICAL_TABLES, 'res_table': HISTORICAL_RES_TABLE, 'historical': True},
     HISTORICAL_EXPECTED_TABLE),
    ({'source_table': NON_HISTORICAL_TABLES, 'res_table': NON_HISTORICAL_RES_TABLE, 'historical': False},
     NON_HISTORICAL_EXPECTED_TABLE)])
def test_map_reduce(yt_stuff, testdata, expected):
    yt_client = yt_stuff.get_yt_client()
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(lpr.find(f'{SOURCE_DIR}reducer.py'))
        tmp.flush()
        builder = get_map_reducer_builder(testdata['source_table'], testdata['res_table'],
                                          LocalFile(tmp.name, file_name='reducer.py'), testdata['historical'])
        yt_client.run_operation(builder)
    exp_table_content = yt_client.read_table(expected)
    res_table_content = yt_client.read_table(testdata['res_table'])

    assert list(exp_table_content) == list(res_table_content)
