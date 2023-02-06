import datetime


def get_local_blrt_config_override_for_tests():
    binary_config = {
        "env": {
            "SET_DEFAULT_LOCAL_YT_PARAMETERS": "true",
            "Y_TEST_FIXED_TIME": datetime.datetime(year=2022, month=1, day=1, tzinfo=datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        }
    }
    return {
        "worker_configs": {
            "config_override_files": ["blrt_config_override_test.pb.txt"]
        },
        "cm": {
            "testing_flag": True
        },
        "setup_yt_env": {
            "queue_shards": 1
        },
        "offer_worker": binary_config.copy(),
        "worker": binary_config.copy(),
        "preview_worker": binary_config.copy(),
        "resharder": binary_config.copy(),
        "selection_rank_worker": binary_config.copy(),
        "task_worker": binary_config.copy()
    }
