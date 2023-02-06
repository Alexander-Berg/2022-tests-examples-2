import json
import pytest
import requests

from passport.infra.daemons.yasms_internal.ut.common import (
    YaSMSInternalFixture,
    AUTH_HEADERS,
)

from passport.infra.recipes.common import log


class TestYaSMSInternalTemplates:
    yasms = None

    @classmethod
    def setup_class(cls):
        log('Starting YaSMS-internal templates test')
        cls.yasms = YaSMSInternalFixture()

    @pytest.fixture(autouse=True)
    def reset_mysql(self):
        self.yasms.reset_mysql()

    @classmethod
    def teardown_class(cls):
        log('Closing general YaSMS-internal templates test')
        cls.yasms.stop()

    @classmethod
    def get_audit_log(cls, table_name, id_field):
        return cls.yasms.get_audit_log(table_name, id_field)

    @classmethod
    def check_templates(cls, expected_templates):
        r = requests.get(
            '{url}/1/templates?min={min}&limit={limit}'.format(url=cls.yasms.url, min="0", limit=100),
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        handle_response = json.loads(r.content)
        for idx in range(0, len(handle_response['templates'])):
            assert 'audit_create' in handle_response['templates'][idx]
            assert 'audit_modify' in handle_response['templates'][idx]
            if handle_response['templates'][idx]['audit_create']['ts'] != 0:
                handle_response['templates'][idx]['audit_create']['ts'] = "TS_HOLDER"
            if handle_response['templates'][idx]['audit_modify']['ts'] != 0:
                handle_response['templates'][idx]['audit_modify']['ts'] = "TS_HOLDER"

        assert handle_response == expected_templates

    def test_get_templates_all(self):
        expected_templates = {
            'next': '',
            'templates': [
                {
                    'abc_service': 'passport_infra',
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'fields_description': '{"code": {"privacy": "secret"}}',
                    'id': '4',
                    'sender_meta': '{"whatsapp": {"id": 1111}}',
                    'text': 'I see a {{name}} and code {{code}}',
                },
                {
                    'abc_service': 'passport_infra',
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'fields_description': '',
                    'id': '8',
                    'sender_meta': '{"whatsapp": {"id": 2222}}',
                    'text': 'New {{service}} init',
                },
            ],
            'total_count': 2,
        }
        self.check_templates(expected_templates)

    def test_get_templates_limit(self):
        url_template = '{url}/1/templates?min={min}&limit={limit}'
        for i in range(1, 2):
            r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=i), headers=AUTH_HEADERS)

            assert r.status_code == 200
            data = json.loads(r.content)
            assert len(data['templates']) == i

        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=100), headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = json.loads(r.content)
        assert len(data['templates']) == 2

    def test_get_templates_failed(self):
        url_template = '{url}/1/templates?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="4483", limit=0), headers=AUTH_HEADERS)
        assert r.status_code == 400

    def test_update_templates(self):
        r = requests.put(
            '{url}/1/templates'.format(url=self.yasms.url),
            json={
                "create": [
                    {
                        "text": "New text",
                        "abc_service": "permanent",
                        "sender_meta": "{\"whatsapp\": {\"id\": 1000}}",
                        "fields_description": "{}",
                    }
                ],
                "update": [
                    {
                        "id": "4",
                        "abc_service": "passport_api",
                        "sender_meta": "{\"whatsapp\": {\"id\": 1111}}",
                        "fields_description": "{}",
                    }
                ],
                "change_info": {"issue": ["PASSP-2"], "comment": "set templates"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        expected_templates = {
            'next': '',
            'templates': [
                {
                    'abc_service': 'passport_api',
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '1', 'ts': 'TS_HOLDER'},
                    'fields_description': '{}',
                    'id': '4',
                    'sender_meta': '{"whatsapp": {"id": 1111}}',
                    'text': 'I see a {{name}} and code {{code}}',
                },
                {
                    'abc_service': 'passport_infra',
                    'audit_create': {'change_id': '', 'ts': 0},
                    'audit_modify': {'change_id': '', 'ts': 0},
                    'fields_description': '',
                    'id': '8',
                    'sender_meta': '{"whatsapp": {"id": 2222}}',
                    'text': 'New {{service}} init',
                },
                {
                    'abc_service': 'permanent',
                    'audit_create': {'change_id': '2', 'ts': 'TS_HOLDER'},
                    'audit_modify': {'change_id': '2', 'ts': 'TS_HOLDER'},
                    'fields_description': '{}',
                    'id': '9',
                    'sender_meta': '{"whatsapp": {"id": 1000}}',
                    'text': 'New text',
                },
            ],
            'total_count': 3,
        }

        self.check_templates(expected_templates)

        audit_bulk, audit_row, data_row = self.get_audit_log('sms.templates', 'id')
        assert audit_bulk == [(1, 'test_login', 'PASSP-2', 'set templates')]
        assert audit_row == [
            (
                1,
                1,
                'templates',
                'update',
                'abc_service=passport_api,sender_meta={"whatsapp": {"id": 1111}},fields_description={}',
                4,
            ),
            (
                2,
                1,
                'templates',
                'add',
                'text=New text,abc_service=permanent,sender_meta={"whatsapp": {"id": 1000}},fields_description={}',
                9,
            ),
        ]
        assert data_row == [(4, None, 1), (8, None, None), (9, 2, 2)]

    def test_set_templates_failed(self):
        url_template = '{url}/1/templates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [
                    {
                        "text": "New text",
                        "abc_service": "permanent",
                        "sender_meta": "{\"whatsapp\": {\"id\": 1000}}",
                        "fields_description": "{}",
                    }
                ],
                "update": [
                    {
                        "id": "1",
                        "text": "New",
                        "abc_service": "passport_api",
                        "sender_meta": "{\"whatsapp\": {\"id\": 1111}}",
                        "fields_description": "{}",
                    }
                ],
                "change_info": {"issue": ["PASSP-2"], "comment": "set templates"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["1"],
                "create": [
                    {
                        "text": "New text",
                        "abc_service": "permanent",
                        "sender_meta": "{\"whatsapp\": {\"id\": 1000}}",
                        "fields_description": "{}",
                    }
                ],
                "update": [
                    {
                        "id": "1",
                        "abc_service": "passport_api",
                        "sender_meta": "{\"whatsapp\": {\"id\": 1111}}",
                        "fields_description": "{}",
                    }
                ],
                "change_info": {"issue": ["PASSP-2"], "comment": "set templates"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

    def test_set_templates_parse(self):
        url_template = '{url}/1/templates_parse'
        r = requests.post(
            url_template.format(url=self.yasms.url),
            data='My {{code}} and {{some}}',
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        handle_response = json.loads(r.content)
        assert handle_response == {"fields_list": ["code", "some"]}

        r = requests.post(
            url_template.format(url=self.yasms.url),
            data='My {{code}} and {{',
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
