import robot.jupiter.test.common as jupiter_integration
from robot.jupiter.library.python.jupiter_util import add_time_to_state

from os.path import join as pj
import re


def process(lj, env):
    # Must be CM var, not just environment var
    # We have to disable it because we don't have shards_prepare's walrus in previous state
    lj.get_cm().set_var("INCREMENTAL_MODE", "false")
    lj.get_cm().set_var("PudgeEnabled", "false")
    lj.get_cm().set_var("Selectionrank.UpdateTierConfigNoCheck", "true")

    lj.get_cm().set_var("CanonizedFactors.LaunchBeforeSnapshot", "false")
    lj.get_cm().set_var("Hostdat.LaunchBeforeSnapshot", "false")

    sample_move_prefix = lj.get_prefix() + "_old"
    lj.get_cm().set_var("DeploySample.MrPrefixOldSample", sample_move_prefix)
    lj.get_cm().set_var("DeploySample.SrcMrPrefix", sample_move_prefix)

    lj.get_cm().toggle_target_restarts("yandex.finish", False)
    lj.get_cm().toggle_target_restarts("rt_yandex.finish", False)
    lj.get_cm().toggle_target_restarts("sample.finish", False)

    lj.get_cm().check_call_target("hostdat_async.finish", timeout=10 * 60)
    lj.get_cm().call_target_async("canonized_factors_async.finish")
    lj.get_cm().wait_target_complete("canonized_factors_async.init_new_state", timeout=2 * 60)

    lj.get_cm().check_call_target("yandex.finish", timeout=60 * 60,
                                  ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re())
    lj.get_cm().check_call_target("rt_yandex.finish", timeout=2 * 60 * 60)

    lj.get_cm().check_call_target("sample.finish", timeout=60 * 60, ignore_failed_log_re=re.compile(r"^sample\.run"))

    first_state = lj.get_current_state("rt_yandex")

    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "sample",
        first_state,
        "urls_without_duplicates",
        bucketed=False)

    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "sample",
        first_state,
        "urls",
        bucketed=False)

    testing_first_states = lj.get_testing_current_state()
    lj.get_cm().check_call_target("deploy_sample.finish", timeout=10 * 60,
                                  ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re())
    lj.set_testing_current_state({key: add_time_to_state(value, 24 * 60 * 60) for key, value in testing_first_states.items()})

    lj.get_cm().check_call_target("hostdat_async.finish", timeout=10 * 60, reset_path=True)
    lj.get_cm().call_target_async("canonized_factors_async.finish", reset_path=True)
    lj.get_cm().wait_target_complete("canonized_factors_async.init_new_state", timeout=2 * 60)

    lj.get_cm().check_call_target("yandex.finish", timeout=60 * 60, reset_path=True,
                                  ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re())
    lj.get_cm().check_call_target("rt_yandex.finish", timeout=2 * 60 * 60, reset_path=True)

    # Dump spread's tables to validate result of sample.spread
    spread_rtdelta_async_path = pj(lj.get_prefix(), "spread_rtdelta_async")
    for state in lj.get_yt().list(spread_rtdelta_async_path):
        spread_rtdelta_state_path = pj(spread_rtdelta_async_path, state)
        for bucket in lj.get_yt().list(spread_rtdelta_state_path):
            lj.dump_jupiter_table(
                env.table_dumps_dir,
                "spread_rtdelta_async",
                state,
                "urldat.delta",
                bucketed=False,
                subdirectory=bucket)

    for state in lj.get_yt().list(pj(lj.get_prefix(), "spread_rthub_hosts_async")):
        lj.dump_jupiter_table(
            env.table_dumps_dir,
            "spread_rthub_hosts_async",
            state,
            "hostdat.delta",
            bucketed=False)

    # Dump shards to validate result of whole sample
    lj.dump_jupiter_table(
        env.table_dumps_dir,
        "selectionrank",
        lj.get_current_state("rt_yandex"),
        "url_to_shard",
        bucketed=True,
        sort_by=["Host", "Path", "Shard"],
    )

    lj.build_shards()
    lj.dump_shards()
