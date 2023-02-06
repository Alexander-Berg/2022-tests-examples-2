import json
import pytest
import requests

import yt.wrapper

from passport.infra.daemons.yasms_internal.ut.common import YaSMSInternalFixture, AUTH_HEADERS, make_gate_with_id
from passport.infra.daemons.yasms_internal.ut.schemas import (
    create_regions_table,
    create_gates_table,
    REGIONS_TABLE_NAME,
    GATES_TABLE_NAME,
)

from passport.infra.recipes.common import log


def get_yt_regions_table():
    return {r['prefix']: {'name': r['name']} for r in yt.wrapper.select_rows("* FROM [%s]" % REGIONS_TABLE_NAME)}


def get_yt_gates_table():
    return {
        r['gateid']: {
            'aliase': r['aliase'],
            'fromname': r['fromname'],
            'consumer': r['consumer'],
            'contractor': r['contractor'],
        }
        for r in yt.wrapper.select_rows("* FROM [%s]" % GATES_TABLE_NAME)
    }


class TestYaSMSInternalYtExport:
    yasms = None

    @classmethod
    def setup_class(cls):
        log('Starting YaSMS-internal yt export test')
        cls.yasms = YaSMSInternalFixture()

    @pytest.fixture(autouse=True)
    def reset_yt(self):
        self.yasms.reset_yt()
        create_regions_table()
        create_gates_table()

    @pytest.fixture(autouse=True)
    def reset_mysql(self):
        self.yasms.reset_mysql()

    @classmethod
    def teardown_class(cls):
        log('Closing general YaSMS-internal regions test')
        cls.yasms.stop()

    def test_export_regions(self):
        r = requests.put(
            '{url}/1/regions'.format(url=self.yasms.url),
            json={
                "delete": ["2", "4"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        self.yasms.restart_daemon()

        assert (
            json.loads(
                '{"+": {"name": "Other"}, "+735190": {"name": "Chelyabinsk region"}, "+99833": {"name": "Uzbekistan"} }'
            )
            == get_yt_regions_table()
        )

    def test_export_gates(self):
        r = requests.put(
            '{url}/1/gates'.format(url=self.yasms.url),
            json={
                "update": [
                    make_gate_with_id("115", "2"),
                    make_gate_with_id("113", "0"),
                    make_gate_with_id("114", "1"),
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        self.yasms.restart_daemon()

        assert (
            json.loads(
                '{"113": {"aliase": "alias-0", "consumer": "consumer-0", "contractor": "contractor-0", "fromname": "fromname-0"},'
                '"114": {"aliase": "alias-1", "consumer": "consumer-1", "contractor": "contractor-1", "fromname": "fromname-1"},'
                '"115": {"aliase": "alias-2", "consumer": "consumer-2", "contractor": "contractor-2", "fromname": "fromname-2"} }'
            )
            == get_yt_gates_table()
        )
