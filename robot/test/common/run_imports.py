from robot.blrt.test.common.testing_current_state import set_testing_current_state
from os.path import join as pj


def run_imports(local_blrt):
    local_blrt.cm.set_var("ImportCDict.CDictTablesSourceDir", pj(local_blrt.yt_prefix, "external_data", "cdict"))
    local_blrt.cm.set_var("ImportExternal.DseSourceTablePath", pj(local_blrt.yt_prefix, "external_data", "external", "dse", "dse_banners"))
    local_blrt.cm.set_var("ImportExternal.WmClustersPerfSourceTablePath", pj(local_blrt.yt_prefix, "external_data", "external", "wm_clusters", "final"))

    IMPORTS_STATE = "20200101-000000"

    set_testing_current_state(local_blrt, {
        "blrt_cdict": IMPORTS_STATE,
        "blrt_external_dse": IMPORTS_STATE,
        "blrt_external_wm_clusters_perf": IMPORTS_STATE,
    })

    local_blrt.cm.check_call_targets([
        "import_cdict.finish",
        "import_external.finish.dse",
        "import_external.finish.wm_clusters_perf",
    ], timeout=5 * 60)
