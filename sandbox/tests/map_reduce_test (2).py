from map_reduce import Mapper


class TestMapReduce(object):
    class TestGetLegacyCounters(object):
        def test_get_legacy_counters(self):
            blocks = '/\t0\t/tr/images/index\t0\t/tr/images/index\t0\t/image/new/head/logo\t0\t'
            row = Row({'blocks': blocks})
            mapper = Mapper(10)
            expected = set(['/', '/tr/images/index', '/image/new/head/logo'])
            assert mapper.get_legacy_counters(row) == expected

    class TestGetBaobabCounters(object):
        def test_get_baobab_counters(self):
            json_blocks = '{"event":"show","tree":{"name":"$page","id":"ba0bab"}}'
            row = Row({'json_blocks': json_blocks})
            mapper = Mapper(10, ['$page'])
            expected = set(['$page'])
            assert mapper.get_baobab_counters(row, 'tld') == expected

    class TestGetCounters(object):
        def test_get_counters(self):
            blocks = '/\t0\t/tr/images/index\t0\t/tr/images/index\t0\t/image/new/head/logo\t0\t'
            json_blocks = '{"event":"show","tree":{"name":"$page","id":"ba0bab"}}'
            row = Row({
                'blocks': blocks,
                'json_blocks': json_blocks
            })
            mapper = Mapper(10, ['$page'])
            expected = set(['/', '/tr/images/index', '/image/new/head/logo', '$page'])
            assert mapper.get_counters(row, 'tld') == expected

        def test_get_granny_counters(self):
            blocks = '/\t0\t/tr/images/index\t0\t/tr/images/index\t0\t/image/new/head/logo\t0\t'
            json_blocks = '{"event":"show","tree":{"name":"$page","id":"ba0bab","attrs":{"service":"web","subservice":"granny"}}}'
            row = Row({
                'blocks': blocks,
                'json_blocks': json_blocks
            })
            mapper = Mapper(10, ['$page'])
            assert mapper.get_counters(row, 'tld') == set()


class Row:
    def __init__(self, dict):
        self._dict = dict

    def get(self, field):
        return self._dict[field]
