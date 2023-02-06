import json
import pytest
import requests

import yt.wrapper

from passport.infra.daemons.yasms_internal.ut.common import (
    YaSMSInternalFixture,
    AUTH_HEADERS,
)
from passport.infra.daemons.yasms_internal.ut.schemas import (
    create_regions_table,
    REGIONS_TABLE_NAME,
)

from passport.infra.recipes.common import log


def get_expected_regions_table():
    return {
        'regions': [
            {
                "id": '1',
                "prefix": "+",
                "name": "Other",
                'audit_create': {'change_id': '', 'ts': 0},
                'audit_modify': {'change_id': '', 'ts': 0},
            },
            {
                "id": '2',
                "prefix": "+7",
                "name": "Russia",
                'audit_create': {'change_id': '', 'ts': 0},
                'audit_modify': {'change_id': '', 'ts': 0},
            },
            {
                "id": '3',
                "prefix": "+735190",
                "name": "Chelyabinsk region",
                'audit_create': {'change_id': '', 'ts': 0},
                'audit_modify': {'change_id': '', 'ts': 0},
            },
            {
                "id": '4',
                "prefix": "+225",
                "name": "Côte d'Ivoire",
                'audit_create': {'change_id': '', 'ts': 0},
                'audit_modify': {'change_id': '', 'ts': 0},
            },
            {
                "id": '5',
                "prefix": "+99833",
                "name": "Uzbekistan",
                'audit_create': {'change_id': '', 'ts': 0},
                'audit_modify': {'change_id': '', 'ts': 0},
            },
        ]
    }


def get_yt_regions_table():
    return {r['prefix']: {'name': r['name']} for r in yt.wrapper.select_rows("* FROM [%s]" % REGIONS_TABLE_NAME)}


class TestYaSMSInternalRegions:
    yasms = None

    @classmethod
    def setup_class(cls):
        log('Starting YaSMS-internal regions test')
        cls.yasms = YaSMSInternalFixture()

    @pytest.fixture(autouse=True)
    def reset_yt(self):
        self.yasms.reset_yt()
        create_regions_table()
        yt.wrapper.insert_rows(
            REGIONS_TABLE_NAME,
            [
                {"prefix": "+", "name": "Other"},
                {"prefix": "+7", "name": "Russia"},
                {"prefix": "+99833", "name": "Uzbekistan"},
                {"prefix": "+225", "name": "Côte d'Ivoire"},
                {"prefix": "+735190", "name": "Chelyabinsk region"},
            ],
        )

    @pytest.fixture(autouse=True)
    def reset_mysql(self):
        self.yasms.reset_mysql()

    @classmethod
    def teardown_class(cls):
        log('Closing general YaSMS-internal regions test')
        cls.yasms.stop()

    @classmethod
    def get_audit_log(cls, table_name, id_field):
        return cls.yasms.get_audit_log(table_name, id_field)

    @classmethod
    def check_regions(cls, expected_regions):
        r = requests.get('{url}/1/regions'.format(url=cls.yasms.url), headers=AUTH_HEADERS)
        assert r.status_code == 200
        assert r.headers.get("X-Ya-Read-Only", "false") == "false"

        handle_response = json.loads(r.content)
        for i in range(0, len(handle_response['regions'])):
            assert 'audit_create' in handle_response['regions'][i]
            assert 'audit_modify' in handle_response['regions'][i]
            if handle_response['regions'][i]['audit_create']['ts'] != 0:
                handle_response['regions'][i]['audit_create']['ts'] = "TS_HOLDER"
            if handle_response['regions'][i]['audit_modify']['ts'] != 0:
                handle_response['regions'][i]['audit_modify']['ts'] = "TS_HOLDER"

        assert handle_response == expected_regions

    @classmethod
    def check_yt_regions(cls):
        r = requests.get('{url}/1/regions'.format(url=cls.yasms.url), headers=AUTH_HEADERS)
        assert r.status_code == 200
        handle_response = json.loads(r.content)

        result_map = {}

        for i in range(0, len(handle_response['regions'])):
            assert 'audit_create' in handle_response['regions'][i]
            assert 'audit_modify' in handle_response['regions'][i]
            result_map[handle_response['regions'][i]['prefix']] = {'name': handle_response['regions'][i]['name']}

        assert result_map == get_yt_regions_table()

    def test_delete_regions(self):
        expected_regions = get_expected_regions_table()
        self.check_regions(expected_regions)
        expected_regions['regions'].pop(1)
        expected_regions['regions'].pop(2)

        r = requests.put(
            '{url}/1/regions'.format(url=self.yasms.url),
            json={
                "delete": ["2", "4"],
                "change_info": {"issue": ["PASSP-1"], "comment": "delete regions"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_regions(expected_regions)

        audit_bulk, audit_row, _ = self.get_audit_log('sms.regions', 'id')
        assert audit_bulk == [(1, 'test_login', 'PASSP-1', 'delete regions')]
        assert audit_row == [(1, 1, 'regions', 'delete', '', 2), (2, 1, 'regions', 'delete', '', 4)]

        self.yasms.restart_daemon()

        self.check_regions(expected_regions)
        self.check_yt_regions()

    def test_delete_regions_failed(self):
        expected_regions = get_expected_regions_table()

        r = requests.put(
            '{url}/1/regions'.format(url=self.yasms.url),
            json={
                "delete": ["770001"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_regions(expected_regions)
        self.check_yt_regions()

    def test_set_regions(self):
        r = requests.put(
            '{url}/1/regions'.format(url=self.yasms.url),
            json={
                "create": [
                    {
                        "prefix": "+7123",
                        "name": "Russia",
                    },
                    {
                        "prefix": "+7812",
                        "name": "Saint Petersburg",
                    },
                ],
                "update": [
                    {
                        "id": "2",
                        "prefix": "+7",
                        "name": "Russia Updated",
                    },
                    {
                        "id": "3",
                        "prefix": "+735190",
                        "name": "Chelyabinsk region Updated",
                    },
                ],
                "delete": ["4", "5"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        audit_bulk, audit_row, data_row = self.get_audit_log('sms.regions', 'id')
        assert audit_bulk == [(1, 'test_login', '', '')]
        # because of undefined order in map iteration
        assert audit_row[0] == (1, 1, 'regions', 'delete', '', 4)
        assert audit_row[1] == (2, 1, 'regions', 'delete', '', 5)

        assert audit_row[2] == (3, 1, 'regions', 'update', 'name=Russia Updated,prefix=+7', 2)
        assert audit_row[3] == (4, 1, 'regions', 'update', 'name=Chelyabinsk region Updated,prefix=+735190', 3)

        assert audit_row[4] == (5, 1, 'regions', 'add', 'name=Russia,prefix=+7123', 6)
        assert audit_row[5] == (6, 1, 'regions', 'add', 'name=Saint Petersburg,prefix=+7812', 7)
        assert data_row == [
            (1, None, None),
            (2, None, 3),
            (3, None, 4),
            (6, 5, 5),
            (7, 6, 6),
        ]

        self.yasms.restart_daemon()

        expected_regions = {
            'regions': [
                {
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'id': '1',
                    'name': 'Other',
                    'prefix': '+',
                },
                {
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '3', 'ts': 'TS_HOLDER'},
                    'id': '2',
                    'name': 'Russia Updated',
                    'prefix': '+7',
                },
                {
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '4', 'ts': 'TS_HOLDER'},
                    'id': '3',
                    'name': 'Chelyabinsk region Updated',
                    'prefix': '+735190',
                },
                {
                    'audit_create': {'change_id': '5', 'ts': 'TS_HOLDER'},
                    'audit_modify': {'change_id': '5', 'ts': 'TS_HOLDER'},
                    'id': '6',
                    'name': 'Russia',
                    'prefix': '+7123',
                },
                {
                    'audit_create': {'change_id': '6', 'ts': 'TS_HOLDER'},
                    'audit_modify': {'change_id': '6', 'ts': 'TS_HOLDER'},
                    'id': '7',
                    'name': 'Saint Petersburg',
                    'prefix': '+7812',
                },
            ]
        }

        self.check_regions(expected_regions)
        self.check_yt_regions()

    def test_get_regions(self):
        r = requests.get('{url}/1/regions'.format(url=self.yasms.url), headers=AUTH_HEADERS)
        assert r.status_code == 200
        assert r.headers.get("X-Ya-Read-Only", "false") == "false"

        handle_response = json.loads(r.content)
        assert handle_response == {
            'regions': [
                {
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'id': '1',
                    'name': 'Other',
                    'prefix': '+',
                },
                {
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'id': '2',
                    'name': 'Russia',
                    'prefix': '+7',
                },
                {
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'id': '3',
                    'name': 'Chelyabinsk region',
                    'prefix': '+735190',
                },
                {
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'id': '4',
                    'name': "Côte d'Ivoire",
                    'prefix': '+225',
                },
                {
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'id': '5',
                    'name': 'Uzbekistan',
                    'prefix': '+99833',
                },
            ]
        }

    def test_get_regions_with_filter(self):
        r = requests.get(
            '{url}/1/regions'.format(url=self.yasms.url),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "name",
                                "compare_op": "NOT_EQUAL",
                                "values": ["Russia"],
                            },
                            {
                                "field": "prefix",
                                "compare_op": "STARTS_WITH",
                                "values": ["+998"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 200
        assert json.loads(r.content) == json.loads(
            '{"regions": [{"audit_create": {"change_id": "", "ts": 0}, "audit_modify": {"change_id": "", "ts": 0}, "id": "5", "name": "Uzbekistan", "prefix": "+99833"}]}'
        )
