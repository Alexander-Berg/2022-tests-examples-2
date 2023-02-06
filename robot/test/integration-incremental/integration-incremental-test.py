import robot.jupiter.test.common as jupiter_integration
from robot.library.yuppie.modules.environment import Environment
from robot.jupiter.cmpy.library import state
from robot.cmpy.library import yt_tools

from os.path import join as pj, basename

PREV_TIERS_PATH = "prev_shards"
MOVED_DATA_STORAGE = "//home/storage"

SPREAD_DIRS = ["spread_rthub_async", "spread_rtdelta_async", "spread_rthub_hosts_async", pj("bert_async", "export", "jupiter")]


def move_spread(lj, env, spread_dir):
    spread_async_states = lj.get_yt().list(pj(env.mr_prefix, spread_dir))
    pivot = len(spread_async_states) // 2
    for spread_async_state in sorted(spread_async_states)[pivot:]:
        lj.get_yt().move(
            pj(env.mr_prefix, spread_dir, spread_async_state),
            pj(MOVED_DATA_STORAGE, spread_dir, spread_async_state),
            recursive=True)


def return_spread(lj, env, spread_dir):
    lj.get_yt().remove(pj(env.mr_prefix, spread_dir), force=True, recursive=True)
    lj.get_yt().move(
        pj(MOVED_DATA_STORAGE, spread_dir),
        pj(env.mr_prefix, spread_dir),
        recursive=True)


def process(lj, env):
    lj.get_cm().set_var("Selectionrank.UpdateTierConfigNoCheck", "true")
    lj.get_cm().set_var("PudgeEnabled", "false")
    lj.get_cm().set_var("VERIFY_HAS_OPERATION_WEIGHT", "true")
    lj.get_yt().touch_table(pj(env.mr_prefix, "archive", "request"))
    lj.get_yt().touch_table(pj(env.mr_prefix, "operation_statistics", "statistics_requests"))

    # Use only one state of spread_async for first run.
    # Second run will use the rest in order to test Pudge.
    for spread_dir in SPREAD_DIRS:
        move_spread(lj, env, spread_dir)
    for directory in lj.get_yt().list(env.mr_prefix, absolute=True):
        if basename(directory) in SPREAD_DIRS:  # to not harm spread_rtdelta_async & Co
            continue
        lj.get_yt().remove(pj(directory, lj.get_prev_state("rt_yandex")), recursive=True, force=True)
    for directory in lj.get_yt().list(pj(env.mr_prefix, "remerge"), absolute=True):
        lj.get_yt().remove(pj(directory, lj.get_prev_state("yandex")), recursive=True, force=True)
    lj.get_yt().remove(yt_tools.node_path(env.mr_prefix, meta_path=pj("states_meta", lj.get_prev_state("rt_yandex"))), force=True)

    # First build previous state
    second_states = lj.get_testing_current_state()
    lj.set_testing_current_state({
        "yandex": lj.get_prev_state("yandex"),
        "rt_yandex": lj.get_prev_state("rt_yandex"),
    })
    lj.erase_prev_states()
    lj.set_current_state('production', state.EMPTY_STATE)

    lj.get_cm().toggle_target_restarts("yandex.finish", False)
    lj.get_cm().toggle_target_restarts("rt_yandex.finish", False)
    lj.get_cm().check_call_target("yandex.finish", timeout=60 * 60,
                                  ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re())
    lj.get_cm().check_call_target("rt_yandex.finish", timeout=60 * 60)
    lj.get_cm().pull_target("cleanup.finish", timeout=60)

    lj.build_shards(dst_dirname=PREV_TIERS_PATH, tier_to_build='PlatinumTier0')
    lj.build_shards(dst_dirname=PREV_TIERS_PATH, tier_to_build='WebTier0')

    # ---------------- NEXT STATE ----------------
    lj.set_current_state('production', lj.get_prev_state("rt_yandex"))
    lj.set_testing_current_state(second_states)

    lj.get_cm().toggle_target_restarts("backup.finish", False)
    lj.get_cm().pull_target("backup.finish", timeout=60)
    lj.get_cm().pull_target("cleanup_remote.finish", timeout=60)

    lj.get_cm().set_var("PudgeEnabled", "true")
    for spread_dir in SPREAD_DIRS:
        return_spread(lj, env, spread_dir)

    lj.get_cm().check_call_target(
        "yandex.finish",
        timeout=60 * 60,
        reset_path=True,
        ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re())
    lj.get_cm().check_call_target("rt_yandex.finish", timeout=60 * 60, reset_path=True)
    lj.build_shards(tier_to_build='PlatinumTier0', prev=PREV_TIERS_PATH)
    lj.build_shards(tier_to_build='WebTier0', prev=PREV_TIERS_PATH)

    # ---------------- DIFF ----------------
    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "selectionrank",
        lj.get_current_state("rt_yandex"),
        "url_to_shard",
        bucketed=True,
        sort_by=["Host", "Path", "Shard"],
    )

    lj.dump_shards()
    lj.merge_shards_dump()

    lj.get_cm().wait_target_complete("backup.finish", timeout=60)


def test_incremental(links):
    env = Environment(diff_test=True)
    cm_env = {
        "DeletionMode": "aggressive",
        "SpreadRTHub.DeleteExport": "",
        "HostdatAsync.DeleteExport": ""
    }
    with jupiter_integration.launch_local_jupiter(
        env,
        cm_env=cm_env,
        test_data="integration.tar",
        yatest_links=links,
    ) as local_jupiter:
        return jupiter_integration.call_jupiter(env.hang_test, process, local_jupiter, env)
