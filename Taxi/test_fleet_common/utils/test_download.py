import io
import zipfile

from fleet_common.utils import download

HEADERS = {
    'h1': 'h1_name',
    'h2': 'h2_name',
    'h3': 'h3_name',
    'h4': 'h4_name',
    'h5': 'h5_name',
}


FIELDNAMES = ['h1', 'h2', 'h3', 'h4', 'h5']

ROWS = [
    {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5},
    {'h1': 'a', 'h2': 'b', 'h3': 'c', 'h4': 'd', 'h5': 'e'},
]


async def test_csv(load):
    assert download.prepare_csv(
        headers=HEADERS, fieldnames=FIELDNAMES, rows=ROWS, charset='utf-8',
    ).replace('\r\n', '\n') == load('output.csv')


async def test_zipped_csv(load):
    mem = io.BytesIO(
        download.prepare_zipped_csv(
            headers=HEADERS,
            fieldnames=FIELDNAMES,
            rows=ROWS,
            charset='utf-8',
            filename='custom',
        ),
    )
    with zipfile.ZipFile(mem) as zip_file:
        assert zip_file.testzip() is None
        assert len(zip_file.namelist()) == 1
        assert zip_file.namelist()[0] == 'custom.csv'
        assert zip_file.read('custom.csv').decode(encoding='utf-8').replace(
            '\r\n', '\n',
        ) == load('output.csv')
