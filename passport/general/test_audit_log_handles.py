import json

import pytest
import requests

from passport.infra.daemons.yasms_internal.ut.common import (
    YaSMSInternalFixture,
    AUTH_HEADERS,
)

from passport.infra.recipes.common import log


class TestYaSMSInternalAuditLog:
    yasms = None

    @classmethod
    def setup_class(cls):
        log('Starting YaSMS-internal audit log handles test')
        cls.yasms = YaSMSInternalFixture()

    @pytest.fixture(autouse=True)
    def reset_mysql(self):
        self.yasms.reset_mysql()

    @classmethod
    def teardown_class(cls):
        log('Closing general YaSMS-internal audit log handles test')
        cls.yasms.stop()

    def test_get_audit_bulk_info(self):
        r = requests.put(
            '{url}/1/routes'.format(url=self.yasms.url),
            json={
                'create': [
                    {'destination': '+7912', 'weight': 1, 'gates': ['114', '113', '115'], 'mode': 'validate'},
                    {'destination': '+79', 'weight': 10, 'gates': ['113', '115'], 'mode': 'default'},
                    {'destination': '+7', 'weight': 2, 'gates': ['115'], 'mode': 'default'},
                ],
                'change_info': {'issue': ['PASSP-1'], 'comment': 'create routes'},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        r = requests.get(
            '{url}/1/audit/bulk_info?bulk_id={bulk_id}'.format(url=self.yasms.url, bulk_id='1'),
            headers=AUTH_HEADERS,
        )

        assert r.status_code == 200
        handle_response = json.loads(r.content)
        assert handle_response['audit_bulk_info']['ts'] != 0
        handle_response['audit_bulk_info']['ts'] = 'TS_HOLDER'

        assert handle_response == {
            'audit_bulk_info': {
                'id': '1',
                'comment': 'create routes',
                'author': 'test_login',
                'issue': 'PASSP-1',
                'ts': 'TS_HOLDER',
                'changes': {
                    '1': {
                        'action': 'add',
                        'entity_id': '4487',
                        'payload': 'destination=+7912,gates=[114 113 115],weight=1,mode=validate',
                    },
                    '2': {
                        'action': 'add',
                        'entity_id': '4488',
                        'payload': 'destination=+79,gates=[113 115],weight=10,mode=default',
                    },
                    '3': {
                        'action': 'add',
                        'entity_id': '4489',
                        'payload': 'destination=+7,gates=[115],weight=2,mode=default',
                    },
                },
            }
        }

        r = requests.get(
            '{url}/1/audit/bulk_info?bulk_id={bulk_id}'.format(url=self.yasms.url, bulk_id='100'),
            headers=AUTH_HEADERS,
        )

        assert r.status_code == 200
        assert json.loads(r.content) == {
            'audit_bulk_info': {'id': '', 'comment': '', 'author': '', 'issue': '', 'ts': 0, 'changes': None}
        }

        r = requests.get(
            '{url}/1/audit/bulk_info'.format(url=self.yasms.url),
            headers=AUTH_HEADERS,
        )

        assert r.status_code == 400

    def test_get_audit_change_info(self):
        r = requests.put(
            '{url}/1/routes'.format(url=self.yasms.url),
            json={
                'create': [
                    {'destination': '+7912', 'weight': 1, 'gates': ['114', '113', '115'], 'mode': 'validate'},
                ],
                'change_info': {'issue': ['PASSP-1'], 'comment': 'create routes'},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        r = requests.put(
            '{url}/1/routes'.format(url=self.yasms.url),
            json={
                'create': [
                    {'destination': '+79', 'weight': 10, 'gates': ['113', '115'], 'mode': 'default'},
                    {'destination': '+7', 'weight': 2, 'gates': ['115'], 'mode': 'default'},
                ],
                'change_info': {'issue': ['PASSP-2'], 'comment': 'create routes 2'},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        r = requests.get(
            '{url}/1/audit/change_info?change_id=1,3'.format(url=self.yasms.url),
            headers=AUTH_HEADERS,
        )

        assert r.status_code == 200
        handle_response = json.loads(r.content)

        handle_response['audit_changes_info']['1']['bulk_info']['ts'] = 'TS_HOLDER'
        handle_response['audit_changes_info']['3']['bulk_info']['ts'] = 'TS_HOLDER'

        assert handle_response == {
            'audit_changes_info': {
                '1': {
                    'action': 'add',
                    'bulk_info': {
                        'author': 'test_login',
                        'comment': 'create routes',
                        'id': '1',
                        'issue': 'PASSP-1',
                        'ts': 'TS_HOLDER',
                    },
                    'entity_id': '4487',
                },
                '3': {
                    'action': 'add',
                    'bulk_info': {
                        'author': 'test_login',
                        'comment': 'create routes 2',
                        'id': '2',
                        'issue': 'PASSP-2',
                        'ts': 'TS_HOLDER',
                    },
                    'entity_id': '4489',
                },
            }
        }

        r = requests.get(
            '{url}/1/audit/change_info?change_id={change_id}'.format(url=self.yasms.url, change_id='100'),
            headers=AUTH_HEADERS,
        )

        assert r.status_code == 200
        assert json.loads(r.content) == {'audit_changes_info': {}}

        r = requests.get(
            '{url}/1/audit/change_info?change_id={change_id}'.format(url=self.yasms.url, change_id='100,1'),
            headers=AUTH_HEADERS,
        )

        assert r.status_code == 200

        handle_response = json.loads(r.content)
        handle_response['audit_changes_info']['1']['bulk_info']['ts'] = 'TS_HOLDER'

        assert handle_response == {
            'audit_changes_info': {
                '1': {
                    'action': 'add',
                    'bulk_info': {
                        'author': 'test_login',
                        'comment': 'create routes',
                        'id': '1',
                        'issue': 'PASSP-1',
                        'ts': 'TS_HOLDER',
                    },
                    'entity_id': '4487',
                }
            }
        }

        r = requests.get(
            '{url}/1/audit/change_info'.format(url=self.yasms.url),
            headers=AUTH_HEADERS,
        )

        assert r.status_code == 400
