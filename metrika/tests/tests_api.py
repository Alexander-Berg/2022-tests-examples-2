import copy

import jsonschema

import metrika.pylib.noodle.response as nresponse
import metrika.admin.python.clickhouse_rbac.frontend.tests.helper as tests_helper

import metrika.admin.python.clickhouse_rbac.frontend.rbac.idm.permissions as rbac_permissions


USERS_SCHEMA = copy.deepcopy(nresponse.API_RESPONSE_SCHEMA)
USERS_SCHEMA['properties']['data'] = {
    'type': 'object',
    'properties': {
        'users': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                    },
                    'password_sha256_hex': {
                        'type': 'string',
                    },
                    'networks': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        },
                    },
                    'quota': {
                        'type': 'string',
                    },
                    'profile': {
                        'type': 'string',
                    },
                    'source': {
                        'type': 'string',
                    },
                },
                'required': [
                    'name',
                    'password_sha256_hex',
                    'networks',
                    'quota',
                    'profile',
                    'source',
                ],
                'additionalProperties': False,
            },
        },
    },
    'required': [
        'users',
    ]
}


class TestUsers(tests_helper.ClickHouseRBACTestCase):
    def test_normal(self):
        response = self.client.get(f'/api/v1/cluster/{rbac_permissions.METRIKA_CLUSTER}/users')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        jsonschema.validate(
            data,
            USERS_SCHEMA,
        )
        self.assertTrue(data['result'])

    def test_missing_cluster(self):
        response = self.client.get('/api/v1/cluster/not_exist/users')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        jsonschema.validate(
            data,
            nresponse.API_RESPONSE_SCHEMA,
        )
        self.assertFalse(data['result'])
