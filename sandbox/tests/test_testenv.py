import pytest

from sandbox.projects.yabs.qa.hamster import testenv


SERVICE_TAGS = {
    "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT": "yabs_hit_models",
    "YABS_SERVER_ADV_MACHINE_KNN_ENDPOINT": "adv_machine_knn",
    "YABS_SERVER_GOALNET_ENDPOINT": "goalnet",
}


def patched_get_service_tag_from_testenv_resource_info(testenv_resource_info):
    return SERVICE_TAGS[testenv_resource_info['name']]


class TestFilterTestenvResources(object):
    @pytest.mark.parametrize(('testenv_resources', 'ignore_statuses', 'expected_active_endpoints'), (
        (
            [],
            (),
            {}
        ),
        (
            [
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK",
                    "resource_id": 1,
                    "resource_timestamp": 1,
                },
            ],
            (),
            {
                "yabs_hit_models": [1]
            }
        ),
        (
            [
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK",
                    "resource_id": 1,
                    "resource_timestamp": 1,
                },
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "BAD",
                    "resource_id": 2,
                    "resource_timestamp": 2,
                },
            ],
            (),
            {
                "yabs_hit_models": [1, 2]
            }
        ),
        (
            [
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK",
                    "resource_id": 1,
                    "resource_timestamp": 1,
                },
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "BAD",
                    "resource_id": 2,
                    "resource_timestamp": 2,
                },
            ],
            ("BAD", ),
            {
                "yabs_hit_models": [1]
            }
        ),
        (
            [
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK",
                    "resource_id": 1,
                    "resource_timestamp": 1,
                },
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK",
                    "resource_id": 2,
                    "resource_timestamp": 2,
                },
            ],
            (),
            {
                "yabs_hit_models": [2]
            }
        ),
        (
            [
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK",
                    "resource_id": 1,
                    "resource_timestamp": 1,
                },
                {
                    "name": "YABS_SERVER_ADV_MACHINE_KNN_ENDPOINT",
                    "status": "OK",
                    "resource_id": 3,
                    "resource_timestamp": 2,
                },
            ],
            (),
            {
                "adv_machine_knn": [3],
                "yabs_hit_models": [1],
            }
        ),
    ))
    def test_get_testenv_hamster_endpoints(self, monkeypatch, testenv_resources, ignore_statuses, expected_active_endpoints):
        monkeypatch.setattr(
            testenv,
            "get_service_tag_from_testenv_resource_info",
            patched_get_service_tag_from_testenv_resource_info)

        assert testenv.get_testenv_hamster_endpoints(
            testenv_resources,
            ignore_statuses=ignore_statuses,
        ) == expected_active_endpoints

    @pytest.mark.parametrize(('testenv_resources', 'expected_active_endpoints'), (
        (
            [
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK",
                    "resource_id": 10,
                    "resource_timestamp": 10,
                },
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "BAD",
                    "resource_id": 9,
                    "resource_timestamp": 9,
                },
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK_OLD",
                    "resource_id": 8,
                    "resource_timestamp": 8,
                },
                {
                    "name": "YABS_SERVER_GOALNET_ENDPOINT",
                    "status": "OK",
                    "resource_id": 7,
                    "resource_timestamp": 7,
                },
                {
                    "name": "YABS_SERVER_GOALNET_ENDPOINT",
                    "status": "OK_OLD",
                    "resource_id": 6,
                    "resource_timestamp": 6,
                },
                {
                    "name": "YABS_SERVER_GOALNET_ENDPOINT",
                    "status": "BAD",
                    "resource_id": 5,
                    "resource_timestamp": 5,
                },
                {
                    "name": "YABS_SERVER_YABS_HIT_MODELS_ENDPOINT",
                    "status": "OK_OLD",
                    "resource_id": 4,
                    "resource_timestamp": 4,
                },
            ],
            {
                "yabs_hit_models": [10, 8],
                "goalnet": [7]
            }
        ),
    ))
    def test_keep_old_hamster(self, monkeypatch, testenv_resources, expected_active_endpoints):
        monkeypatch.setattr(
            testenv,
            "get_service_tag_from_testenv_resource_info",
            patched_get_service_tag_from_testenv_resource_info)
        assert testenv.get_testenv_hamster_endpoints(
            testenv_resources,
            ok_old_resources_to_keep=['yabs_hit_models']
        ) == expected_active_endpoints
