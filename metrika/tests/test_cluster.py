import json
import uuid
import pytest
import jsonschema

import yatest.common
import metrika.admin.python.mtapi.lib.api.cluster.lib as cl_lib

from time import sleep
from werkzeug.exceptions import HTTPException
from flask_restful.reqparse import RequestParser

from peewee import DoesNotExist
import metrika.pylib.zkconnect as mtzk
from metrika.pylib.log import init_logger, base_logger
import metrika.pylib.config as lib_config
from metrika.admin.python.mtapi.lib.api.cluster.api import GetDataHandler, GetListHandler, GetGroupByHandler, Pinger


config_file = yatest.common.source_path('metrika/admin/python/mtapi/lib/api/cluster/tests/config.yaml')
config = lib_config.get_yaml_config_from_file(config_file)

init_logger('mtapi', stdout=True, log_format=config.log.format)
init_logger('mtutils', stdout=True, log_format=config.log.format)
init_logger('peewee', stdout=True, log_format=config.log.format)
init_logger('kazoo', stdout=True, log_format=config.log.format)
logger = base_logger.getChild(__name__)


BASE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "execute_query_time": {
                    "type": "number",
                    "minimum": 0
                },
                "parse_time": {
                    "type": "number",
                    "minimum": 0
                },
                "total_time": {
                    "type": "number",
                    "minimum": 0
                }
            },
            "additionalProperties": False,
        },
        "reason": {
            "type": "string"
        }
    },
    "required": ["meta", "data"],
    "additionalProperties": False,
}

get_json_schema = {
    "type": "array",
    "minItems": 0,
    "items": {
        "type": "object",
        "properties": {
            "dc_name": {
                "anyOf": [
                    {
                        "type": "string"
                    },
                    {
                        "type": "null"
                    }
                ]
            },
            "dc_suff": {
                "anyOf": [
                    {
                        "type": "string"
                    },
                    {
                        "type": "null"
                    }
                ]
            },
            "environment": {
                "type": "string",
                "enum": ["production", "prestable", "testing", "development", "unsupported"]
            },
            "fqdn": {
                "type": "string"
            },
            "groups": {
                "type": "array",
                "items": {
                    "type": "string",
                    "minItems": 1
                }
            },
            "index": {
                "type": "integer"
            },
            "layer": {
                "anyOf": [
                    {
                        "type": "integer"
                    },
                    {
                        "type": "null"
                    }
                ]
            },
            "replica": {
                "type": "integer"
            },
            "root_group": {
                "type": "string"
            },
            "project": {
                "type": "string"
            },
            "shard": {
                "anyOf": [
                    {
                        "type": "integer"
                    },
                    {
                        "type": "null"
                    }
                ]
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "type": {
                "anyOf": [
                    {
                        "type": "string"
                    },
                    {
                        "type": "null"
                    }
                ]
            },
            "shard_id": {
                "type": "string"
            },
        },
        "additionalProperties": False,
    }
}

list_json_schema = {
    "type": "array",
    "minItems": 0,
    "items": {
        "anyOf": [
            {
                "type": "string"
            },
            {
                "type": "integer"
            }
        ]
    }
}

group_by_one_field_schema = {
    "type": "object",
    "patternProperties": {
        ".*": get_json_schema,
    },
}


def get_refresher():
    zk = mtzk.get_zk(**config.cluster.zk)
    return cl_lib.ConductorRefresh(config.cluster, zk, '/')


def validate(o, data_schema):
    schema = BASE_JSON_SCHEMA.copy()
    schema['properties']['data'] = data_schema
    try:
        jsonschema.validate(o, schema)
    except jsonschema.ValidationError:
        logger.exception("Validate error")
        return False
    except jsonschema.SchemaError:
        logger.exception("schema error")
        return False
    else:
        return True


def mock_req_parser(monkeypatch, body):
    monkeypatch.setattr(RequestParser, 'parse_args', lambda *args, **kwargs: body)


def normalize_hosts(list_of_hosts):
    for host in list_of_hosts:
        for k, v in host.items():
            if isinstance(v, list):
                assert len(v) == len(set(v))
                host[k] = set(v)


versions = []


class TestUpdate:
    def test_refresh_from_conductor(self, prepare_refresh, database):
        refresher = get_refresher()
        result = refresher.refresh()

        assert result == 'done'

        version = cl_lib.GetLastVersion.get_version()
        assert isinstance(version, uuid.UUID) and version.version == 4
        versions.append(version)

    def test_refresh_with_updates(self, monkeypatch, database):
        def gen_mock_get_hosts(filename):
            def mock_get_hosts(*args):
                with open(yatest.common.work_path('test_data//{}'.format(filename))) as f_h:
                    data = f_h.read()

                return data.strip()

            return mock_get_hosts

        def gen_mock_get_project(filename):
            def mock_get_project(*args):
                with open(yatest.common.work_path('test_data//{}'.format(filename))) as f_h:
                    data = f_h.read()

                data = json.loads(data)
                return data

            return mock_get_project

        def gen_mock_get_tags(ablazh_filename, civil_filename):
            def mock_get_tags(*args):
                with open(yatest.common.work_path('test_data//{}'.format(ablazh_filename))) as f_h:
                    ablazh = f_h.read()

                with open(yatest.common.work_path('test_data//{}'.format(civil_filename))) as f_h:
                    civil = f_h.read()

                a = [l.split(';') for l in civil.split('\n') if l]
                b = json.loads(ablazh)
                x = [(a[i][0], b[a[i][1]][a[i][0]]['tags']) for i in range(len(a))]

                return dict(x)

            return mock_get_tags

        monkeypatch.setattr(cl_lib, '_get_hosts_from_condutor', gen_mock_get_hosts('civil.txt'))
        monkeypatch.setattr(cl_lib, '_get_project_from_conductor', gen_mock_get_project('ablazh.json'))
        monkeypatch.setattr(cl_lib, '_get_hosts_tags_from_conductor', gen_mock_get_tags('ablazh.json', 'civil.txt'))

        refresher = get_refresher()
        result = refresher.refresh()

        assert result == 'done'

        version = cl_lib.GetLastVersion.get_version()
        assert isinstance(version, uuid.UUID) and version.version == 4
        versions.append(version)

        monkeypatch.setattr(cl_lib, '_get_hosts_from_condutor', gen_mock_get_hosts('civil_mtcalclog.txt'))
        monkeypatch.setattr(cl_lib, '_get_project_from_conductor', gen_mock_get_project('ablazh_mtcalclog.json'))
        monkeypatch.setattr(cl_lib, '_get_hosts_tags_from_conductor',
                            gen_mock_get_tags('ablazh_mtcalclog.json', 'civil_mtcalclog.txt'))

        result = refresher.refresh()
        assert result == 'done'

        version = cl_lib.GetLastVersion.get_version()
        assert isinstance(version, uuid.UUID) and version.version == 4
        versions.append(version)

        monkeypatch.setattr(cl_lib, '_get_hosts_from_condutor', gen_mock_get_hosts('civil.txt'))
        monkeypatch.setattr(cl_lib, '_get_project_from_conductor', gen_mock_get_project('ablazh.json'))
        monkeypatch.setattr(cl_lib, '_get_hosts_tags_from_conductor', gen_mock_get_tags('ablazh.json', 'civil.txt'))

        result = refresher.refresh()

        assert result == 'done'

        version = cl_lib.GetLastVersion.get_version()
        assert isinstance(version, uuid.UUID) and version.version == 4
        versions.append(version)

        assert len(versions) == len(set(versions)) == 4


class TestLib:

    @pytest.mark.parametrize("test_input,expected", config.tests.test_get_custom_data)
    def test_get_data(self, test_input, expected, database):
        getter = cl_lib.GetCustomData()
        data = getter.get_data(**test_input)

        assert isinstance(data, list)
        assert len(data) == len(expected)

        normalize_hosts(expected)
        normalize_hosts(data)

        for host in expected:
            assert host in data
        for host in data:
            assert host in expected

        logger.info(getter.meta)
        for value in getter.meta.values():
            assert isinstance(value, (int, float))

    def test_unknown_key(self, database):
        getter = cl_lib.GetCustomData()
        with pytest.raises(KeyError):
            getter.get_data(unknown='blah')

    def not_test_refresh_thread(self, monkeypatch, database):
        class Counter(object):
            count = 0

        def mock_refresh(self, *args, **kwargs):
            self.counter.count += 1
            return 'done'

        counter = Counter()
        monkeypatch.setattr(cl_lib.ConductorRefresh, 'counter', counter, raising=False)
        monkeypatch.setattr(cl_lib.ConductorRefresh, 'refresh', mock_refresh)

        t = cl_lib.RefreshThread(config.cluster, database)
        t.start()
        sleep(5)

        assert counter.count == 1

        sleep(7)

        assert counter.count == 2

    @pytest.mark.parametrize("test_input,expected", config.tests.test_get_list)
    def test_get_list(self, test_input, expected, database):
        kwargs = test_input.copy()
        field = kwargs.pop('field')
        getter = cl_lib.GetList(field)
        data = getter.get_data(**kwargs)

        assert isinstance(data, list)
        assert len(data) == len(expected)
        assert set(data) == set(expected)

        logger.info(getter.meta)
        for value in getter.meta.values():
            assert isinstance(value, (int, float))

    def test_get_list_exceptions(self, database):
        with pytest.raises(TypeError):
            cl_lib.GetList(123)

        with pytest.raises(DoesNotExist):
            getter = cl_lib.GetList('asd')
            getter.get_data()

        with pytest.raises(KeyError):
            getter = cl_lib.GetList('root_group')
            getter.get_data(field='layer')


class TestSuccessUrls:

    def test_ping(self, database):
        assert Pinger().get() == 'OK'

    def test_get(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict())
        data = GetDataHandler().get()

        shard_ids = "\n".join(["shard_id={shard_id}\tfqdn={fqdn}\ttype={type}\tlayer={layer}\tshard={shard}\tenvironment={environment}".format(**r) for r in data["data"] if r["shard_id"] is None])

        logger.debug("None shard ids:\n{}".format(shard_ids))
        assert validate(data, get_json_schema)
        assert len(data['data']) == 1331

    def test_get_group_tag_field(self, monkeypatch, field, database):
        mock_req_parser(monkeypatch, dict(group=['mtstat'], tag=['ipvs_tun'], field=[field]))
        req = GetDataHandler().get()
        assert validate(req, get_json_schema)
        if field == 'dc_name':
            assert len(req['data']) == 2
            assert set([i['dc_name'] for i in req['data']]) == {'iva', 'myt'}
        elif field == 'dc_suff':
            assert len(req['data']) == 2
            assert set([i['dc_suff'] for i in req['data']]) == {'e', 'f'}
        elif field == 'fqdn':
            assert len(req['data']) == 2
            assert set([i['fqdn'] for i in req['data']]) == {'mtstat01-1.yandex.ru', 'mtstat01-2.yandex.ru'}
        elif field == 'root_group':
            assert set([i['root_group'] for i in req['data']]) == {'mtstat'}

    def test_get_many_groups_many_tags(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(group=['mt-daemon', 'mtsmart'], tag=['ipvs_tun', 'wr']))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert len(data['data']) == 2
        normalize_hosts(data['data'])
        assert data['data'][0]['dc_name'] == 'man'
        assert data['data'][1]['dc_name'] == 'man'
        assert data['data'][0]['tags'] == {"ipvs", "ipvs_tun", "wr"}
        assert data['data'][1]['tags'] == {"ipvs", "ipvs_tun", "wr"}
        assert data['data'][0]['dc_suff'] == 'k'
        assert data['data'][1]['dc_suff'] == 'k'
        assert data['data'][0]['replica'] == 1
        assert data['data'][1]['replica'] == 2
        assert data['data'][0]['fqdn'] == 'mtsmart001-1.yandex.ru'
        assert data['data'][1]['fqdn'] == 'mtsmart001-2.yandex.ru'

    def test_get_many_groups_many_tags_one_field(self, monkeypatch, field, database):
        mock_req_parser(monkeypatch, dict(group=['mt-daemon', 'mtsmart'], tag=['ipvs_tun', 'wr'], field=[field]))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        normalize_hosts(data['data'])
        if field == 'dc_name':
            assert len(data['data']) == 2
            assert data['data'][0]['dc_name'] == 'man'
            assert data['data'][1]['dc_name'] == 'man'
        elif field == 'tags':
            assert len(data['data']) == 2
            assert data['data'][0]['tags'] == {"ipvs", "ipvs_tun", "wr"}
            assert data['data'][1]['tags'] == {"ipvs", "ipvs_tun", "wr"}
        elif field == 'dc_suff':
            assert len(data['data']) == 2
            assert data['data'][0]['dc_suff'] == 'k'
            assert data['data'][1]['dc_suff'] == 'k'
        elif field == 'replica':
            assert len(data['data']) == 2
            assert {'replica': 1} in data['data']
            assert {'replica': 2} in data['data']

    def test_list(self, monkeypatch, field, database):
        mock_req_parser(monkeypatch, dict())
        req = GetListHandler().get(field=field)
        assert validate(req, list_json_schema)
        if field == 'dc_name':
            assert set(req['data']) == {'iva', 'myt', 'sas', 'fol', 'ugr', 'man'}
        elif field == 'dc_suff':
            assert set(req['data']) == {'e', 'd', 'g', 'f', 'i', 'h', 'k', 'j'}
        elif field == 'index':
            assert set(req['data']) == set(range(25))
        elif field == 'replica':
            assert set(req['data']) == set(range(3))

    def test_list_group(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(group=['mtstat']))
        req = GetListHandler().get(field='fqdn')
        assert validate(req, list_json_schema)
        assert len(req['data']) == 40
        assert "mtstat14-2.yandex.ru" in req['data']
        assert "mtstat10-1.yandex.ru" in req['data']

    def test_list_group_tag(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(group=['mtstat'], tag=['ipvs_tun']))
        req = GetListHandler().get(field='fqdn')
        assert validate(req, list_json_schema)
        assert len(req['data']) == 2
        assert set(req['data']) == {'mtstat01-1.yandex.ru', 'mtstat01-2.yandex.ru'}

    def test_list_many_groups_many_tags(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(group=['mt-daemon', 'mtsmart'], tag=['wr', 'ipvs_tun']))
        req = GetListHandler().get(field='fqdn')
        assert validate(req, list_json_schema)
        assert len(req['data']) == 2
        assert set(req['data']) == {'mtsmart001-1.yandex.ru', 'mtsmart001-2.yandex.ru'}


class TestDifferentConditions:

    def test_get_different_conditions_and_one_field(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(group=['mt-daemon'], tag=['ipvs_tun'], field=['fqdn'], type='mtstat'))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert len(data['data']) == 2
        assert data['data'][0]['fqdn'] == 'mtstat01-1.yandex.ru'
        assert data['data'][1]['fqdn'] == 'mtstat01-2.yandex.ru'

    def test_get_different_conditions_and_all_fields(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(group=['mt-daemon'], tag=['ipvs_tun'], type='mtstat'))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert len(data['data']) == 2
        normalize_hosts(data['data'])
        assert data['data'][0]['dc_name'] == 'iva'
        assert data['data'][1]['dc_name'] == 'myt'
        assert data['data'][0]['tags'] == {"ipvs_tun", "wr"}
        assert data['data'][1]['tags'] == {"ipvs_tun", "wr"}
        assert data['data'][0]['fqdn'] == 'mtstat01-1.yandex.ru'
        assert data['data'][1]['fqdn'] == 'mtstat01-2.yandex.ru'
        assert data['data'][0]['replica'] == 1
        assert data['data'][1]['replica'] == 2
        assert data['data'][0]['dc_suff'] == 'e'
        assert data['data'][1]['dc_suff'] == 'f'
        assert data['data'][0]['root_group'] == 'mtstat'
        assert data['data'][1]['root_group'] == 'mtstat'

    def test_get_different_conditions_and_all_fields_with_multiply_tags(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(group=['metrika'], tag=['ipvs_tun', 'ipvs'], environment='production'))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert len(data['data']) == 2
        normalize_hosts(data['data'])
        assert data['data'][0]['dc_name'] == 'man'
        assert data['data'][1]['dc_name'] == 'man'
        assert data['data'][0]['tags'] == {"ipvs", "ipvs_tun", "wr"}
        assert data['data'][1]['tags'] == {"ipvs", "ipvs_tun", "wr"}
        assert data['data'][0]['dc_suff'] == 'k'
        assert data['data'][1]['dc_suff'] == 'k'
        assert data['data'][0]['replica'] == 1
        assert data['data'][1]['replica'] == 2

    def test_get_different_conditions_and_many_fields(self, monkeypatch, database):
        mock_req_parser(monkeypatch,
                        dict(group=['mt-daemon'], tag=['ipvs_tun'], type='mtstat', field=['fqdn', 'dc_name']))
        req = GetDataHandler().get()
        assert validate(req, get_json_schema)
        assert len(req['data']) == 2
        assert req['data'][0]['dc_name'] == 'iva'
        assert req['data'][1]['dc_name'] == 'myt'
        assert req['data'][0]['fqdn'] == 'mtstat01-1.yandex.ru'
        assert req['data'][1]['fqdn'] == 'mtstat01-2.yandex.ru'


class TestCommonCondition:

    def test_get_all_fields(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(fqdn='mtstat01-1.yandex.ru'))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert data['data'][0]['dc_name'] == 'iva'
        assert data['data'][0]['fqdn'] == 'mtstat01-1.yandex.ru'
        assert len(data['data'][0]['groups']) == 6
        assert data['data'][0]['root_group'] == 'mtstat'

    def test_multiple_selection(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(fqdn='mtstat01-1.yandex.ru|mtstat01-2.yandex.ru'))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert len(data['data']) == 2
        normalize_hosts(data['data'])
        assert data['data'][0]['dc_name'] == 'iva'
        assert data['data'][1]['dc_name'] == 'myt'
        assert data['data'][0]['tags'] == {"ipvs_tun", "wr"}
        assert data['data'][1]['tags'] == {"ipvs_tun", "wr"}
        assert data['data'][0]['fqdn'] == 'mtstat01-1.yandex.ru'
        assert data['data'][1]['fqdn'] == 'mtstat01-2.yandex.ru'
        assert data['data'][0]['replica'] == 1
        assert data['data'][1]['replica'] == 2
        assert data['data'][0]['dc_suff'] == 'e'
        assert data['data'][1]['dc_suff'] == 'f'
        assert data['data'][0]['root_group'] == 'mtstat'
        assert data['data'][1]['root_group'] == 'mtstat'

    def test_get_one_field(self, monkeypatch, field, database):
        mock_req_parser(monkeypatch, dict(fqdn='mtstat01-1.yandex.ru', field=[field]))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert len(data['data'][0].keys()) == 1
        normalize_hosts(data['data'])
        assert data['data'][0][field] in ('iva', 'e', 'production', 'mtstat01-1.yandex.ru',
                                          {'metrika', 'metrika-clickhouse', 'mt-daemon', 'mt-daemon-prod', 'mt-geo',
                                           'mtstat'},
                                          0, None, 'metrika', 1, 'mtstat', {'ipvs_tun', 'wr'}, 'mtstat-1-production')

    def test_list_one_field(self, monkeypatch, field, database):
        mock_req_parser(monkeypatch, dict(fqdn='mtmoblog02-01-1.yandex.ru'))
        data = GetListHandler().get(field=field)
        assert validate(data, list_json_schema)
        data['data'] = set(data['data'])
        if field == 'groups':
            assert data['data'] == {'metrika-clickhouse', 'mt-daemon', 'metrika', 'mt-daemon-prod', 'mtmoblog'}
        elif field == 'tags':
            assert data['data'] == {'wr'}
        elif field == 'dc_name':
            assert data['data'] == {'man'}
        elif field == 'root_group':
            assert data['data'] == {'mtmoblog'}


class TestProperties:

    def test_get_property(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(fqdn='mtstat03-1.yandex.ru', field=['dc_name', 'shard_id']))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert data['data'][0]['dc_name'] == 'iva'
        assert data['data'][0]['shard_id'] == 'mtstat-3-production'

    def test_get_all_fields(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(fqdn='mtstat01-1.yandex.ru'))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert len(data['data'][0].keys()) == 14
        normalize_hosts(data['data'])
        assert data['data'][0]['dc_name'] == 'iva'
        assert data['data'][0]['tags'] == {"ipvs_tun", "wr"}
        assert data['data'][0]['fqdn'] == 'mtstat01-1.yandex.ru'
        assert data['data'][0]['replica'] == 1
        assert data['data'][0]['dc_suff'] == 'e'
        assert data['data'][0]['root_group'] == 'mtstat'
        assert data['data'][0]['shard_id'] == 'mtstat-1-production'

    def test_get_property_condition(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(dc_name='myt', type='mtstatlog'))
        data = GetDataHandler().get()
        assert validate(data, get_json_schema)
        assert data['data'][0]['fqdn'] == 'mtstatlog01f.yandex.ru'

    def test_list_property(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(fqdn='mtstat01-1.yandex.ru'))
        data = GetListHandler().get(field='dc_name')
        assert validate(data, list_json_schema)
        assert data['data'][0] == 'iva'

        data = GetListHandler().get(field='shard_id')
        assert validate(data, list_json_schema)
        assert data['data'][0] == 'mtstat-1-production'

    def test_list_property_with_multiple_choise(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(
            fqdn='mtstat01-1.yandex.ru|mtstat01-2.yandex.ru|mtstat01-3.yandex.ru|mtstat01-4.yandex.ru'))
        data = GetListHandler().get(field='dc_name')
        assert validate(data, list_json_schema)
        assert len(data['data']) == 2
        assert set(data['data']) == {'iva', 'myt'}

    def test_list_property_condition(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(dc_name='myt', type='mtstatlog'))
        data = GetListHandler().get(field='fqdn')
        assert validate(data, list_json_schema)
        assert data['data'][0] == 'mtstatlog01f.yandex.ru'

    def test_list_property_condition_with_multiple_choise(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(dc_name='sas|myt', type='mtlog'))
        data = GetListHandler().get(field='fqdn')
        assert validate(data, list_json_schema)
        assert 'mtlog03-02-1.yandex.ru' in data['data']
        assert "mtlog23-03-1.yandex.ru" in data['data']
        assert "mtlog13-04-2.yandex.ru" in data['data']
        assert "mtlog34-02-1.yandex.ru" in data['data']


class TestGroupBy:

    def test_group_by_one_field(self, monkeypatch, field, database):
        ggbh = GetGroupByHandler()
        if field in ('groups', 'tags'):
            with pytest.raises(ValueError):
                ggbh.check_group_by_choice(field)
            return

        mock_req_parser(monkeypatch, dict(group_by_fields=ggbh.check_group_by_choice(field), group=['mtmoblog-test'],
                                          field=['fqdn']))
        data = ggbh.get()
        assert validate(data, group_by_one_field_schema)
        if field == 'dc_name':
            assert data['data']['fol'][0]['fqdn'] == 'mtmoblog01-01-2t.yandex.ru'
            assert data['data']['ugr'][0]['fqdn'] == 'mtmoblog02-01-2t.yandex.ru'
            assert len(data['data']['sas']) == 2
        elif field == 'shard_id':
            assert 'mtmoblog01-01-2t.yandex.ru' in map(lambda x: x['fqdn'], data['data']['mtmoblog-1-1-testing'])
            assert 'mtmoblog02-01-2t.yandex.ru' in map(lambda x: x['fqdn'], data['data']['mtmoblog-2-1-testing'])
            assert len(data['data']['mtmoblog-2-1-testing']) == 2
        elif field == 'fqdn':
            assert len(data['data']) == 4
            assert "mtmoblog01-01-2t.yandex.ru" in data['data']
            assert "mtmoblog01-01-1t.yandex.ru" in data['data']
            assert "mtmoblog02-01-2t.yandex.ru" in data['data']
            assert "mtmoblog02-01-1t.yandex.ru" in data['data']
        elif field == 'shard':
            assert len(data['data']['1']) == 4

    def test_double_group(self, monkeypatch, database):
        ggbh = GetGroupByHandler()
        mock_req_parser(monkeypatch,
                        dict(group_by_fields=ggbh.check_group_by_choice('environment,index'), type='mtcalclog',
                             field=['fqdn']))

        data = ggbh.get()
        assert len(data['data']) == 2
        assert len(data['data']['production']) == 7

        assert len(data['data']['production']['1']) == 5
        assert {"fqdn": "mtcalclog01e.yandex.ru"} in data['data']['production']['1']
        assert {"fqdn": "mtcalclog01i.yandex.ru"} in data['data']['production']['1']
        assert {"fqdn": "mtcalclog01g.yandex.ru"} in data['data']['production']['1']
        assert {"fqdn": "mtcalclog01f.yandex.ru"} in data['data']['production']['1']
        assert {"fqdn": "mtcalclog01k.yandex.ru"} in data['data']['production']['1']

        assert len(data['data']['production']['3']) == 5
        assert {"fqdn": "mtcalclog03g.yandex.ru"} in data['data']['production']['3']
        assert {"fqdn": "mtcalclog03i.yandex.ru"} in data['data']['production']['3']
        assert {"fqdn": "mtcalclog03k.yandex.ru"} in data['data']['production']['3']
        assert {"fqdn": "mtcalclog03f.yandex.ru"} in data['data']['production']['3']
        assert {"fqdn": "mtcalclog03e.yandex.ru"} in data['data']['production']['3']

        assert len(data['data']['production']['6']) == 4
        assert {"fqdn": "mtcalclog06k.yandex.ru"} in data['data']['production']['6']
        assert {"fqdn": "mtcalclog06g.yandex.ru"} in data['data']['production']['6']
        assert {"fqdn": "mtcalclog06e.yandex.ru"} in data['data']['production']['6']
        assert {"fqdn": "mtcalclog06i.yandex.ru"} in data['data']['production']['6']


class TestErrors:

    def test_unknown_arg_get(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(not_existing_arg='mtstat01-1.yandex.ru'))
        with pytest.raises(KeyError):
            GetDataHandler().get()

    def test_unknown_field_get(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(field='asd', fqdn='mtstat01-1.yandex.ru'))
        with pytest.raises(HTTPException) as e:
            GetDataHandler().get()

        assert e.value.code == 404

    def test_unknown_field_list(self, monkeypatch, database):
        mock_req_parser(monkeypatch, dict(fqdn='mtstat01-1.yandex.ru'))
        with pytest.raises(HTTPException) as e:
            GetListHandler().get(field='asd')

        assert e.value.code == 404
