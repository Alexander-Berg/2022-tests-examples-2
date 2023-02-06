import pytest
import yt.yson

from taxi.external import yt_wrapper
from taxi.internal.yt_tools import consts
from taxi.internal.yt_tools import table_rotate
from taxi.internal.yt_tools.table_rotate import models
from taxi.internal.yt_tools.table_rotate import schema


class FakeYsonList(list):
    def __init__(self, list_data, attributes=None):
        super(FakeYsonList, self).__init__(list_data)
        self.list_data = list_data
        self.attributes = (attributes or {}).copy()

    def __eq__(self, other):
        assert self.attributes == other.attributes, (
            'different attrs: %s != %s' % (self.attributes, other.attributes)
        )
        assert self.list_data == other.list_data, (
            'different lists values: %s != %s' % (self.list_data,
                                                  other.list_data)
        )
        return True

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return str(self)


class TableObj(object):
    def __init__(self, path, attributes):
        self.path = path
        self.attributes = (attributes or {}).copy()

    def __eq__(self, other):
        assert self.path == other.path, (
            'different paths: %s, %s' % self.path, other.path
        )
        assert self.attributes == other.attributes, (
            'different attrs: %s != %s' % (self.attributes, other.attributes)
        )
        return True

    def __str__(self):
        return self.path

    def __repr__(self):
        return str(self)


TO_PROCESS_MAP_NODE = 'features/data'
ANOTHER_MAP_NODE = 'another/tables'


class _DummyYTClient(object):
    class Transaction(object):
        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def __init__(self, client_name, data):
        self.client_name = client_name
        self.config = {
            'prefix': '//pref/',
            'token': 'secretpass',
            'proxy': {
                'url': '{}.yt.yandex.net'.format(client_name)
            },
        }
        self.data = data.copy()
        self.mapped = {}
        self.sorted = []

    def exists(self, path):
        return path in self.data

    def get(self, path):
        path, attr = path.split('/@')
        return self.data[path].attributes[attr]

    def search(self, base_path, *args, **kwargs):
        return {data for path, data in self.data.iteritems()
                if path.startswith(base_path)}

    def create_temp_table(self, path=None, prefix=None, attributes=None,
                          *args, **kwargs):
        assert path is None, 'usage client tmp? %s' % path
        assert prefix is not None, 'usage tmp tables without prefix'

        path = '//tmp/%s' % prefix
        assert path not in self.data
        self.data[path] = TableObj(path, attributes)
        return path

    def move(self, path_from, path_to):
        table = self.data.pop(path_from)
        self.data[path_to] = TableObj(path_to, table.attributes)

    def remove(self, path, force=False):
        if not force:
            assert path in self.data
            self.data.pop(path)
        else:
            self.data.pop(path, None)

    def run_map(self, mapper, tables_from, table_to, **kwargs):
        assert all(str(table) in self.data for table in tables_from)
        self.mapped[table_to] = {str(table): table for table in tables_from}

    def run_sort(self, table_obj, sort_by, **kwargs):
        path = str(table_obj)
        assert path in self.data
        self.data[path] = table_obj
        self.data[path].attributes[consts.SORTED_BY] = sort_by
        self.sorted.append(path)

    def lock(self, path, lock_type):
        assert lock_type == consts.LOCK_EXCLUSIVE


_BASE_SCHEMA = FakeYsonList([
    {consts.NAME: 'name', consts.TYPE: 'string'},
    {consts.NAME: 'name2', consts.TYPE: 'string'},
    {consts.NAME: 'name3', consts.TYPE: 'string'},
])
_BASE_ATTRIBUTES = {
    consts.SORTED: False,
    consts.SORTED_BY: None,
    consts.SCHEMA: _BASE_SCHEMA,
    consts.REVISION: 10000,
    consts.COMPRESSION_CODEC: consts.COMPRESSION_CODEC_BROTLI_8,
}

_OUTPUT_SCHEMA = [
    {
        consts.NAME: models.SOURCE_TABLE_NAME,
        consts.SORT_ORDER: consts.SORT_ORDER_ASCENDING,
        consts.TYPE: consts.TYPE_STRING
    },
]
_OUTPUT_SCHEMA.extend(_BASE_SCHEMA)
_OUTPUT_SCHEMA = FakeYsonList(_OUTPUT_SCHEMA)
_BASE_EXPECTED_ATTRIBUTES = {
    consts.OPTIMIZE_FOR: consts.OPTIMIZE_FOR_LOOKUP,
    consts.COMPRESSION_CODEC: consts.COMPRESSION_CODEC_BROTLI_8,
    consts.SCHEMA: _OUTPUT_SCHEMA,
    consts.SORTED_BY: [models.SOURCE_TABLE_NAME],
}


def _get_yt_data(map_nodes, months):
    yt_data = {}

    def _gen_dates(base_month):
        template = '%s-%%s' % base_month
        for dt in range(1, 31):
            yield template % ('0%d' % dt if dt < 10 else '%d' % dt)

    for node in map_nodes:
        for month in months:
            paths = ['%s/%s' % (node, date) for date in _gen_dates(month)]
            yt_data.update(
                {path: TableObj(path, _BASE_ATTRIBUTES) for path in paths}
            )

    return yt_data


@pytest.mark.now('2018-10-14 18:10:00 +03')
@pytest.mark.asyncenv('blocking')
def test_rotate_one_node(monkeypatch, patch):
    monkeypatch.setattr(
        models.StaticRotationModel, '_MINIMAL_DAYS_THRESHOLD', 30
    )
    monkeypatch.setattr(yt.yson, 'YsonList', FakeYsonList)
    monkeypatch.setattr(yt_wrapper, 'TablePath', TableObj)
    client_name = 'cluster_name'
    yt_client = _DummyYTClient(
        client_name,
        _get_yt_data(
            (TO_PROCESS_MAP_NODE, ANOTHER_MAP_NODE),
            ('2018-07', '2018-08', '2018-09', '2018-10'),
        )
    )

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(name, new=False, **kwargs):
        assert name == client_name
        return yt_client

    rule_name = '%s.%s.%s' % (
        'rulename', client_name, TO_PROCESS_MAP_NODE.replace('/', '_')
    )
    rules = [
        schema.RotationRule(
            rule_name, client_name, TO_PROCESS_MAP_NODE,
            models.get_model('days_by_months', days_time_threshold=40),
        )
    ]
    table_rotate.start(rules, 1)

    assert yt_client.mapped == {
        '//tmp/{}.2018-07'.format(rule_name): _get_yt_data(
            (TO_PROCESS_MAP_NODE,), ('2018-07',)
        ),
        '//tmp/{}.2018-08'.format(rule_name): _get_yt_data(
            (TO_PROCESS_MAP_NODE,), ('2018-08',)
        ),
    }
    assert sorted(yt_client.sorted) == [
        '//tmp/{}.2018-07'.format(rule_name),
        '//tmp/{}.2018-08'.format(rule_name),
    ]

    expected_yt_data = {
        # result
        path: TableObj(path, _BASE_EXPECTED_ATTRIBUTES) for path in
        ('features/data/2018-07', 'features/data/2018-08')
    }
    expected_yt_data.update(_get_yt_data(
        (ANOTHER_MAP_NODE,),
        ('2018-07', '2018-08', '2018-09', '2018-10'),
    ))
    expected_yt_data.update(_get_yt_data(
        (TO_PROCESS_MAP_NODE,),
        ('2018-09', '2018-10'),
    ))
    assert sorted(yt_client.data.keys()) == sorted(expected_yt_data.keys())
    assert yt_client.data == expected_yt_data

    assert get_client.calls == [
        {'name': 'cluster_name', 'new': False, 'kwargs': {}},  # search tables
        {'name': 'cluster_name', 'new': True,  # use performer
         'kwargs': {'dyntable': False, 'environment': True, 'pool': None,
                    'extra_config_overrides': None}},
    ]
