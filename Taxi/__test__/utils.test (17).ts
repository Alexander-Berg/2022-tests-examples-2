// tslint:disable: max-line-length

import {getAllPaths, jsonToTemplate, mergeTemplates, parseDeploymentData, templateToJson} from '../utils';

const TEMPLATE = (`{
	"mongo_settings": { "yyy": 1,
        "xxx": ["xxx"],
        {{ MONGODB_STRONGBOX_TAXI_DBTAXI }},
        {{ MONGODB_STRONGBOX_TAXI_DBTAXI }}, {{ MONGODB_TAXI_ANTI_FRAUD }},
        {{ MONGODB_TAXI_ANTI_FRAUD }}
	},
	"redis_settings": { {{ REDIS_TAXI_STRONGBOX }},{{ REDIS_TAXI_STRONGBOX }}},
	"settings_override": {
		"STRONGBOX_TEST_MDS_S3":
			{{ S3MDS_TAXI_STRONGBOX }},
			{{ S3MDS_TAXI_STRONGBOX }}, {{ MONGODB_TAXI_ANTI_FRAUD }},
			{{ S3MDS_TAXI_STRONGBOX }}
		"TVM_SERVICES": {
            {{ TVM_TEST_TVM_PROJECT_TEST_TVM_PROJECT_PROVIDER_NAME }}
        },
        {{ S3MDS_TAXI_STRONGBOX }}
  },
    "settings_override_2": { "STRONGBOX_TEST_MDS": {{ S3MDS_TAXI_STRONGBOX }} }
}`);

const TEMPLATE_OUT = (`{
    "mongo_settings": {
        "yyy": 1,
        "xxx": [
            "xxx"
        ],
        {{ MONGODB_STRONGBOX_TAXI_DBTAXI }},
        {{ MONGODB_STRONGBOX_TAXI_DBTAXI }},
        {{ MONGODB_TAXI_ANTI_FRAUD }},
        {{ MONGODB_TAXI_ANTI_FRAUD }}
    },
    "redis_settings": {
        {{ REDIS_TAXI_STRONGBOX }},
        {{ REDIS_TAXI_STRONGBOX }}
    },
    "settings_override": {
        "STRONGBOX_TEST_MDS_S3":
            {{ S3MDS_TAXI_STRONGBOX }},
            {{ S3MDS_TAXI_STRONGBOX }},
            {{ MONGODB_TAXI_ANTI_FRAUD }},
            {{ S3MDS_TAXI_STRONGBOX }}
        "TVM_SERVICES": {
            {{ TVM_TEST_TVM_PROJECT_TEST_TVM_PROJECT_PROVIDER_NAME }}
        },
        "STRONGBOX_TEST_MDS":
            {{ TVM_TESTTVM_TESTTVM }}
    },
    "settings_override_2": {
        "STRONGBOX_TEST_MDS":
            {{ S3MDS_TAXI_STRONGBOX }}
    }
}`);

test('templateToJson', () => {
    const obj = templateToJson(TEMPLATE);

    expect(obj).toEqual({
        mongo_settings: {
            yyy: 1,
            xxx: ['xxx'],
            template: [
                '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}'
            ]
        },
        redis_settings: {
            template: [
                '{{ REDIS_TAXI_STRONGBOX }}',
                '{{ REDIS_TAXI_STRONGBOX }}'
            ]
        },
        settings_override: {
            STRONGBOX_TEST_MDS_S3: [
                '{{ S3MDS_TAXI_STRONGBOX }}',
                '{{ S3MDS_TAXI_STRONGBOX }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                '{{ S3MDS_TAXI_STRONGBOX }}'
            ],
            TVM_SERVICES: {
                template: [
                    '{{ TVM_TEST_TVM_PROJECT_TEST_TVM_PROJECT_PROVIDER_NAME }}'
                ]
            },
            template: ['{{ S3MDS_TAXI_STRONGBOX }}']
        },
        settings_override_2: {
            STRONGBOX_TEST_MDS: ['{{ S3MDS_TAXI_STRONGBOX }}']
        }
    });
});

test('getAllPaths', () => {
    const paths = getAllPaths({
        a: 2,
        b: {
            c: '',
            d: {
                e: [4],
                f: {
                    g: true,
                    k: null,
                    l: undefined,
                    n: {}
                }
            }
        }
    });

    expect(paths).toEqual([
        'a',
        'b.c',
        'b.d.e',
        'b.d.f.g',
        'b.d.f.k',
        'b.d.f.l',
        'b.d.f.n'
    ]);

    expect(getAllPaths({})).toEqual([]);
    expect(getAllPaths(null)).toEqual([]);
});

test('mergeTemplates', () => {
    expect(mergeTemplates(
        TEMPLATE,
        '{ "postgresql_settings": { "databases": { {{ value }} } } }',
        '{{ POSTGRES_PROJ_POSETG222SES_NAME_PROV_TEST_NAME }}'
    )).toEqual({
        mongo_settings: {
            yyy: 1,
            xxx: ['xxx'],
            template: [
                '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}'
            ]
        },
        redis_settings: {
            template: [
                '{{ REDIS_TAXI_STRONGBOX }}',
                '{{ REDIS_TAXI_STRONGBOX }}'
            ]
        },
        settings_override: {
            STRONGBOX_TEST_MDS_S3: [
                '{{ S3MDS_TAXI_STRONGBOX }}',
                '{{ S3MDS_TAXI_STRONGBOX }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                '{{ S3MDS_TAXI_STRONGBOX }}'
            ],
            TVM_SERVICES: {
                template: [
                    '{{ TVM_TEST_TVM_PROJECT_TEST_TVM_PROJECT_PROVIDER_NAME }}'
                ]
            },
            template: ['{{ S3MDS_TAXI_STRONGBOX }}']
        },
        settings_override_2: {
            STRONGBOX_TEST_MDS: ['{{ S3MDS_TAXI_STRONGBOX }}']
        },
        postgresql_settings: {
            databases: {
                template: [
                    '{{ POSTGRES_PROJ_POSETG222SES_NAME_PROV_TEST_NAME }}'
                ]
            }
        }
    });

    expect(mergeTemplates(
        TEMPLATE,
        '{ "settings_override": { "TVM_SERVICES": { {{ value }} } } }',
        '{{ TVM_TESTTVM_TESTTVM }}'
    )).toEqual({
        mongo_settings: {
            yyy: 1,
            xxx: ['xxx'],
            template: [
                '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}'
            ]
        },
        redis_settings: {
            template: [
                '{{ REDIS_TAXI_STRONGBOX }}',
                '{{ REDIS_TAXI_STRONGBOX }}'
            ]
        },
        settings_override: {
            STRONGBOX_TEST_MDS_S3: [
                '{{ S3MDS_TAXI_STRONGBOX }}',
                '{{ S3MDS_TAXI_STRONGBOX }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                '{{ S3MDS_TAXI_STRONGBOX }}'
            ],
            TVM_SERVICES: {
                template: [
                    '{{ TVM_TEST_TVM_PROJECT_TEST_TVM_PROJECT_PROVIDER_NAME }}',
                    '{{ TVM_TESTTVM_TESTTVM }}'
                ]
            },
            template: ['{{ S3MDS_TAXI_STRONGBOX }}']
        },
        settings_override_2: {
            STRONGBOX_TEST_MDS: ['{{ S3MDS_TAXI_STRONGBOX }}']
        }
    });

    expect(mergeTemplates(
        TEMPLATE,
        '{ "settings_override": { "STRONGBOX_TEST_MDS": {{ value }} } }',
        '{{ TVM_TESTTVM_TESTTVM }}'
    )).toEqual({
        mongo_settings: {
            yyy: 1,
            xxx: ['xxx'],
            template: [
                '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}'
            ]
        },
        redis_settings: {
            template: [
                '{{ REDIS_TAXI_STRONGBOX }}',
                '{{ REDIS_TAXI_STRONGBOX }}'
            ]
        },
        settings_override: {
            STRONGBOX_TEST_MDS_S3: [
                '{{ S3MDS_TAXI_STRONGBOX }}',
                '{{ S3MDS_TAXI_STRONGBOX }}',
                '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                '{{ S3MDS_TAXI_STRONGBOX }}'
            ],
            TVM_SERVICES: {
                template: [
                    '{{ TVM_TEST_TVM_PROJECT_TEST_TVM_PROJECT_PROVIDER_NAME }}'
                ]
            },
            template: ['{{ S3MDS_TAXI_STRONGBOX }}'],
            STRONGBOX_TEST_MDS: [
                '{{ TVM_TESTTVM_TESTTVM }}'
            ]
        },
        settings_override_2: {
            STRONGBOX_TEST_MDS: ['{{ S3MDS_TAXI_STRONGBOX }}']
        }
    });
});

test('jsonToTemplate', () => {
    expect(
        jsonToTemplate({
            mongo_settings: {
                yyy: 1,
                xxx: ['xxx'],
                template: [
                    '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                    '{{ MONGODB_STRONGBOX_TAXI_DBTAXI }}',
                    '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                    '{{ MONGODB_TAXI_ANTI_FRAUD }}'
                ]
            },
            redis_settings: {
                template: [
                    '{{ REDIS_TAXI_STRONGBOX }}',
                    '{{ REDIS_TAXI_STRONGBOX }}'
                ]
            },
            settings_override: {
                STRONGBOX_TEST_MDS_S3: [
                    '{{ S3MDS_TAXI_STRONGBOX }}',
                    '{{ S3MDS_TAXI_STRONGBOX }}',
                    '{{ MONGODB_TAXI_ANTI_FRAUD }}',
                    '{{ S3MDS_TAXI_STRONGBOX }}'
                ],
                TVM_SERVICES: {
                    template: [
                        '{{ TVM_TEST_TVM_PROJECT_TEST_TVM_PROJECT_PROVIDER_NAME }}'
                    ]
                },
                STRONGBOX_TEST_MDS: [
                    '{{ TVM_TESTTVM_TESTTVM }}'
                ]
            },
            settings_override_2: {
                STRONGBOX_TEST_MDS: ['{{ S3MDS_TAXI_STRONGBOX }}']
            }
        })
    ).toBe(TEMPLATE_OUT);
});

describe('parseDeploymentData', () => {
    test('should parse correct image', () => {
        const image = 'taxi/taxi-billing-replication/production:0.0.85';
        const {env, version} = parseDeploymentData(image);

        expect(env).toBe('production');
        expect(version).toBe('0.0.85');
    });

    test('should parse correct image with letters', () => {
        const image = 'taxi/clownductor/unstable:0.0.180unstable10429';
        const {env, version} = parseDeploymentData(image);

        expect(env).toBe('unstable');
        expect(version).toBe('0.0.180unstable10429');
    });

    test('should parse correct image with dash', () => {
        const image = 'taxi/tariff-editor/unstable:0.0.1917-1594730620';
        const {env, version} = parseDeploymentData(image);

        expect(env).toBe('unstable');
        expect(version).toBe('0.0.1917-1594730620');
    });

    test('should not parse incorrect image', () => {
        const image = 'eda/core-jobs:20200420153404-production-6e9d9f907ac9b488a5e2efd452eaca2ebd555f65';
        const {env, version} = parseDeploymentData(image);

        expect(env).toBe(undefined);
        expect(version).toBe(undefined);
    });

    test('should parse nothing', () => {
        const {env, version} = parseDeploymentData(undefined);

        expect(env).toBe(undefined);
        expect(version).toBe(undefined);
    });
});
