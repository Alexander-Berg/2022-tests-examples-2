from copy import deepcopy
from hamcrest import assert_that, has_items, equal_to, has_entries, contains_inanyorder
import pytest

import sandbox.projects.market.idx.GenIdxUniversalSchedulers as lib

CFG = {
    "tasks": {
        "routines-saasdumper": {
            "type": "NOT_ROUTINES_TASK",
            "sandbox": {
                "type": "MARKET_RUN_UNIVERSAL_BUNDLE",
                "owner": "owner",
                "author": "author1",
                "task": {
                    "owner": "owner",
                    "tags": ["TEST"],
                    "kill_timeout": 10800,
                    "custom_fields": [
                        {"name": "task_name", "value": "routines-sandbox"},
                        {"name": "bundle_name", "value": "routines-sandbox"},
                        {
                            "name": "cmd",
                            "value": [
                                "{{cwd}}/path/to/bin",
                                "-c",
                                "{{cwd}}/path/to/cfg",
                                "--task",
                                "SaasDumper",
                                "--dc",
                                "{{dc}}",
                            ],
                        },
                        {"name": "environment", "value": "production"},
                        {"name": "use_its_config", "value": "True"},
                        {"name": "its_url", "value": "https://its.yandex-team.ru/v1/values/market/datacamp/routines/production-sandbox/market_datacamp_settings/"},
                        {"name": "its_path", "value": "{{cwd}}/conf/routines/its.ini"}
                    ],
                },
            },
            "juggler": {"ttl": 2160},
        },
        "not_routines": {
            "type": "NOT_ROUTINES_TASK",
            "sandbox": {
                "type": "MARKET_RUN_UNIVERSAL_BUNDLE",
                "owner": "owner",
                "author": "author2",
                "task": {
                    "owner": "owner",
                    "tags": ["TEST"],
                    "kill_timeout": 10800,
                    "custom_fields": [
                        {"name": "task_name", "value": "not-routines-sandbox"},
                        {"name": "bundle_name", "value": "not-routines-sandbox"},
                        {"name": "environment", "value": "production"},
                    ],
                },
            },
            "juggler": {"ttl": 2160},
        },
        "not_routines_2": {
            "type": "NOT_ROUTINES_TASK",
            "sandbox": {
                "type": "MARKET_RUN_UNIVERSAL_BUNDLE_2",
                "owner": "owner",
                "author": "author1",
                "task": {
                    "owner": "owner",
                    "tags": ["TEST"],
                    "kill_timeout": 10800,
                    "custom_fields": [
                        {"name": "task_name", "value": "not-routines-sandbox"},
                        {"name": "bundle_name", "value": "not-routines-sandbox"},
                        {"name": "environment", "value": "production"},
                    ],
                },
            },
            "juggler": {"ttl": 2160},
        },
    }
}

response = {
    "items": [
        {
            "status": "STOPPED",
            "task": {
                "type": "MARKET_RUN_UNIVERSAL_BUNDLE",
                "tags": ["ROUTINES-SAASDUMPER", "TESTING", "TAG"],
                "custom_fields": [
                    {"name": "task_name", "value": "routines-saasdumper"},
                ],
            },
            "id": 1,
        },
        {
            "status": "STOPPED",
            "task": {
                "type": "MARKET_RUN_UNIVERSAL_BUNDLE",
                "tags": ["ROUTINES-SAASDUMPER", "TESTING", "TAG"],
                "custom_fields": [
                    {"name": "task_name", "value": "routines-saasdumper"},
                ],
            },
            "id": 2,
        },
        {
            "status": "STOPPED",
            "task": {
                "type": "MARKET_RUN_UNIVERSAL_BUNDLE",
                "tags": ["NOT_ROUTINES", "TESTING", "TAG"],
                "custom_fields": [
                    {"name": "task_name", "value": "not_routines"},
                ],
            },
            "id": 3,
        },
        {
            "status": "STOPPED",
            "task": {
                "type": "NOT_MARKET_RUN_UNIVERSAL_BUNDLE",
                "tags": ["SOME_TYPE", "TESTING", "TAG"],
                "custom_fields": [
                    {"name": "task_name", "value": "some_type"},
                ],
            },
            "id": 4,
        },
        {
            "status": "STOPPED",
            "task": {
                "type": "MARKET_RUN_UNIVERSAL_BUNDLE",
                "tags": ["ROUTINES-SOME_TASK", "TESTING", "TAG"],
                "custom_fields": [
                    {"name": "task_name", "value": "routines-some_task"},
                ],
            },
            "id": 5,
        },
    ]
}


class ClientMock:
    class SchedulerMock:
        def __init__(self, idx=0):
            self.call_requests = []
            if idx != 0:
                self.response = response["items"][0]
            else:
                self.response = response

        def __call__(self, req):
            self.call_requests.append(req)
            return {"id": 10}

        def __getitem__(self, num):
            res = deepcopy(self)
            res.__init__(1)
            return res

        def update(self, sid):
            pass

        def read(self, search=None):
            if search:
                answer = {"items": []}
                for i in self.response["items"]:
                    if set(search["tags"]).intersection(set(i["task"]["tags"])) == set(search["tags"]):
                        answer["items"].append(i)
                return answer
            return self.response

    class Batch:
        class Schedulers:
            delete = 0

            def __init__(self):
                class MockStart:
                    def update(self, s_id):
                        pass

                self.start = MockStart()

        def __init__(self):
            self.schedulers = self.Schedulers()

    def __init__(self):
        self.scheduler = self.SchedulerMock()
        self.batch = self.Batch()


@pytest.fixture(scope="module")
def sandbox_client():
    return ClientMock()


def test_get_task_name():
    value = {
        'custom_fields': [
            {"name": "some_name", "value": 1},
            {"name": "task_name", "value": 2},
            {"name": "sOme_n@me", "value": 3},
        ]
    }

    assert_that(lib.get_task_name(value), equal_to(2))


def test_generate_routines_scheduler():
    config = {
        "tasks": {
            "routines-saasdumper": {
                "type": "ROUTINES_TASK",
                "sandbox": {
                    "task_name": "SaasDumper",
                    "interval": 1800,
                    "sequential_run": True,
                },
                "juggler": {"ttl": 2160},
            }
        }
    }

    scheduler = lib.generate_schedulers_from_config(config, 'production', 'robot-mrkt-idx-sb')[0].upcoming_cfg
    assert_that(scheduler, has_entries({
        'owner': 'MARKET-IDX',
        'author': 'robot-mrkt-idx-sb',
        'schedule': has_entries({
            'sequential_run': True,
            'repetition': has_entries({
                'interval': 1800
            })
        }),
        'task': has_entries({
            'type': 'MARKET_RUN_UNIVERSAL_BUNDLE',
            'owner': 'MARKET-IDX',
            'custom_fields': contains_inanyorder(
                {'name': 'task_name', 'value': 'routines-saasdumper'},
                {'name': 'bundle_name', 'value': 'routines-sandbox'},
                {
                    'name': 'cmd',
                    'value': [
                        '{{cwd}}/bin/routines',
                        '-c',
                        '{{cwd}}/conf/routines/common.ini,{{cwd}}/conf/routines/conf-available/{{environment}}.white.ini,{{its}}',
                        '--task',
                        'SaasDumper',
                        '--dc',
                        '{{dc}}',
                    ],
                },
                {'name': 'environment', 'value': 'production'},
                {'name': 'use_its_config', 'value': 'True'},
                {'name': 'its_url', 'value': 'https://its.yandex-team.ru/v1/values/market/datacamp/routines/production-sandbox/market_datacamp_settings/'},
                {'name': 'its_path', 'value': '{{cwd}}/conf/routines/its.ini'},
                {'name': 'its_secret_name', 'value': 'nanny-oauth'},
                {'name': 'send_metrics_to_solomon', 'value': 'True'},
                {'name': 'solomon_project', 'value': 'market.datacamp'},
                {'name': 'solomon_cluster', 'value': 'production'},
                {'name': 'solomon_service', 'value': 'routines'},
                {'name': 'solomon_secret_name', 'value': 'solomon-oauth'},
                {'name': 'solomon_extra_labels', 'value': {
                    'task': 'SaasDumper'
                }}
            ),
            'tags': contains_inanyorder('PRODUCTION', 'MARKET_UNIVERSAL_SCHEDULER', 'ROUTINES-SAASDUMPER')
        })
    }))


def test_generate_routines_scheduler_with_datagetter():
    config = {
        "tasks": {
            "routines-saasdumper": {
                "type": "ROUTINES_TASK",
                "sandbox": {
                    "task_name": "SaasDumper",
                    "interval": 1800,
                    "sequential_run": True,
                    'fetch_datagetter': True
                },
                "juggler": {"ttl": 2160},
            }
        }
    }

    scheduler = lib.generate_schedulers_from_config(config, 'production', 'robot-mrkt-idx-sb')[0].upcoming_cfg
    assert_that(scheduler, has_entries({
        'task': has_entries({
            'custom_fields': has_items(
                {'name': 'use_resource', 'value': 'True'},
                {'name': 'resources', 'value': {
                    'MARKET_DATA_SHOPSDAT': '{{cwd}}/data-getter-mbi/shopsdat'
                }},
            ),
        })
    }))


def test_generate_routines_scheduler_with_extra_resources():
    config = {
        "tasks": {
            "routines-saasdumper": {
                "type": "ROUTINES_TASK",
                "sandbox": {
                    "task_name": "SaasDumper",
                    "interval": 1800,
                    "sequential_run": True,
                    "extra_resources": [
                        {"resource": "MARKET_DATA_SHOPSDAT", "dest": "{{cwd}}/data-getter-mbi/shopsdat"},
                        {"resource": "OTHER_RESOURCE", "dest": "{{cwd}}/other-resource"}
                    ]
                },
                "juggler": {"ttl": 2160},
            }
        }
    }

    scheduler = lib.generate_schedulers_from_config(config, 'production', 'robot-mrkt-idx-sb')[0].upcoming_cfg

    assert_that(scheduler, has_entries({
        'task': has_entries({
            'custom_fields': has_items(
                {'name': 'use_resource', 'value': 'True'},
                {'name': 'resources', 'value': {
                    'MARKET_DATA_SHOPSDAT': '{{cwd}}/data-getter-mbi/shopsdat',
                    'OTHER_RESOURCE': '{{cwd}}/other-resource'
                }}
            )
        })
    }))


def test_generate_non_routines_scheduler():
    config = {
        'tasks': {
            "not_routines_2": {
                "sandbox": {
                    "owner": "owner",
                    "task": {
                        "type": "MARKET_RUN_UNIVERSAL_BUNDLE_2",
                        "owner": "owner",
                        "tags": ["TEST"],
                        "kill_timeout": 10800,
                        "custom_fields": [
                            {"name": "task_name", "value": "not-routines-sandbox"},
                            {"name": "bundle_name", "value": "not-routines-sandbox"},
                            {"name": "environment", "value": "production"},
                        ],
                    },
                },
            },
        }
    }

    scheduler = lib.generate_schedulers_from_config(config, 'production', 'robot-mrkt-idx-sb')[0].upcoming_cfg
    assert_that(scheduler, has_entries({
        'owner': 'owner',
        'author': 'robot-mrkt-idx-sb',
        'task': has_entries({
            'type': 'MARKET_RUN_UNIVERSAL_BUNDLE_2',
            'owner': 'owner',
            "kill_timeout": 10800,
            "custom_fields": contains_inanyorder(
                {"name": "task_name", "value": "not-routines-sandbox"},
                {"name": "bundle_name", "value": "not-routines-sandbox"},
                {"name": "environment", "value": "production"},
            ),
            'tags': contains_inanyorder('PRODUCTION', 'MARKET_UNIVERSAL_SCHEDULER', 'NOT_ROUTINES_2', 'TEST')
        })
    }))


def test_create_scheduler(sandbox_client):
    scheduler_params = {'task': {'type': 'MY_SUPER_TASK'}}
    schedulers = [
        lib.SchedulerInfo(upcoming_cfg=scheduler_params, task_name='MySuperTask')
    ]

    lib.generate_schedulers(sandbox_client, None, schedulers, 'production')
    assert_that(sandbox_client.scheduler.call_requests, has_items(has_entries({
        'data': scheduler_params,
        'task_type': 'MY_SUPER_TASK'
    })))


def test_binary_executor_release_type():
    config = {
        "tasks": {
            "routines-saasdumper": {
                "type": "ROUTINES_TASK",
                "sandbox": {
                    "task_name": "SaasDumper",
                    "interval": 1800,
                    "sequential_run": True,
                    "binary_executor_release_type": "testing_or_upper"
                },
                "juggler": {"ttl": 2160},
            }
        }
    }

    scheduler = lib.generate_schedulers_from_config(config, 'production', 'robot-mrkt-idx-sb')[0].upcoming_cfg
    assert_that(scheduler, has_entries({
        'task': has_entries({
            'custom_fields': has_items(
                {'name': 'binary_executor_release_type', 'value': 'testing_or_upper'},
            ),
        })
    }))


def test_merge_default_section():
    config = {
        'default': {
            'sandbox': {
                'owner': 'DEFAULT-OWNER',
                'task_name': 'default_task_name'
            }
        },
        'tasks': {
            'routines-some-task': {
                'type': 'ROUTINES_TASK',
                'sandbox': {
                    'task_name': 'overridden_task_name',
                    'interval': 1800,
                }
            }
        }
    }

    scheduler = lib.generate_schedulers_from_config(config, 'production', 'robot-mrkt-idx-sb')[0].upcoming_cfg
    assert_that(scheduler, has_entries({
        'owner': 'DEFAULT-OWNER',
        'task': has_entries({
            'owner': 'DEFAULT-OWNER',
            'custom_fields': has_items(
                {'name': 'task_name', 'value': 'routines-overridden_task_name'},
            ),
        })
    }))
