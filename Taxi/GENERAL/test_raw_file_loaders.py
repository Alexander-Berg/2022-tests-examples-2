import datetime
import pathlib

import pytest

EXPECTED_VALUE: dict = {
    'address': None,
    'assortment_id': 'id',
    'cluster': 'Москва',
    'created': datetime.datetime(2020, 6, 26, 12, 14, 46),
    'currency': 'RUB',
    'errors': ['assortment:none'],
    'polygon_field': [[0.1, 0.2], [2.1, 3.4]],
    'price_list_id': 'id',
    'print_id': 'id',
    'region_id': None,
    'samples': '[]',
    'serial': 107,
    'slug': None,
    'source': 'wms',
    'status': 'searching',
    'store_id': '5f6471a785eb4458ba3d485d96c337b9000200010000',
    'timetable': '[]',
    'title': 'test_sklad',
    'type': 'lavka',
    'tz': 'Europe/Moscow',
    'updated': datetime.datetime(2020, 6, 26, 12, 14, 46),
    'user_id': 'id',
    'zone': [],
}


@pytest.mark.parametrize('extension', ['.json', '.yaml'])
def test_loaders(_loaders_by_extension, static_dir, extension):
    static_path = pathlib.Path(static_dir)
    loader = _loaders_by_extension[extension]
    path = pathlib.Path.joinpath(static_path, 'raw' + extension)
    raw_dct = loader(path)
    assert raw_dct == EXPECTED_VALUE
