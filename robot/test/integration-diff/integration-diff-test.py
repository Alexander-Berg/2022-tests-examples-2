import robot.jupiter.test.common as jupiter_integration
from robot.library.yuppie.modules.environment import Environment

from os.path import join as pj


def process(lj, env):
    # Must be CM var, not just environment var
    # We have to disable it because we don't have shards_prepare's walrus in previous state
    lj.get_cm().set_var("INCREMENTAL_MODE", "false")
    lj.get_cm().set_var("VERIFY_HAS_OPERATION_WEIGHT", "true")
    lj.get_cm().set_var("PudgeEnabled", "false")

    lj.get_cm().toggle_target_restarts("yandex.finish", False)
    lj.get_cm().toggle_target_restarts("rt_yandex.finish", False)
    lj.get_cm().check_call_target(
        "yandex.finish", timeout=60 * 60, ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re())
    lj.get_cm().check_call_target("rt_yandex.finish", timeout=60 * 60)
    lj.get_cm().toggle_target_restarts("cleanup.finish", False)
    lj.get_cm().check_call_target("cleanup.finish", timeout=10 * 60)
    lj.get_cm().toggle_target_restarts("cleanup_sp.finish", False)
    lj.get_cm().check_call_target("cleanup_sp.finish", timeout=10 * 60)

    lj.get_yt().remove(pj(env.mr_prefix, "delivery_snapshot"), recursive=True)  # to be sure that shards building doesn't use delivery_snapshot data at all

    lj.build_shards(tier_to_build='TestingPlatinumTier0')
    lj.build_shards(tier_to_build='MsuseardataJupiterTier0', middle=True)

    current_state = lj.get_current_state("rt_yandex")

    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "duplicates",
        current_state,
        "Duplicates")

    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "export",
        current_state,
        "metrics/in_search_history",
    )

    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "feedback",
        current_state,
        "feedback_per_url",
        bucketed=True
    )

    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "selectionrank",
        current_state,
        "url_to_shard",
        bucketed=True,
        sort_by=["Host", "Path", "Shard"],
    )

    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "acceptance",
        current_state,
        "urls_for_webmaster_simple")

    lj.dump_shards()


def test_diff(links):
    env = Environment(diff_test=True)
    cm_env = {
        "DeletionMode": "aggressive",
        "Feedback.DupGroupLimit": "3",
    }
    with jupiter_integration.launch_local_jupiter(
        env,
        cm_env=cm_env,
        test_data="integration.tar",
        yatest_links=links,
    ) as local_jupiter:
        return jupiter_integration.call_jupiter(env.hang_test, process, local_jupiter, env)
