from sandbox import sdk2
from sandbox.projects.resource_types.releasers import experiment_releasers


class TEST_ABT_METRICS_RUN_CONFIGURATION(sdk2.Resource):
    """
    Deprecated. Divided to RUN_ABT_RESOURCES and RUN_ABT_METRICS
    Prepared resources for running stat_collector and stat_fetcher
    like geodata3.bin, browser.xml and metrics file
    """
    any_arch = False


class RUN_ABT_RESOURCES(sdk2.Resource):
    """
    Prepared resources for running stat_collector and stat_fetcher
    like geodata3.bin, browser.xml
    """
    any_arch = True
    auto_backup = True


class RUN_ABT_CALC_METRICS(sdk2.Resource):
    """
    Deprecated. JSON metrics file for running stat_collector and stat_fetcher
    """
    any_arch = True
    auto_backup = True


class RUN_ABT_STAT_COLLECTOR_CONFIG(sdk2.Resource):
    """
    Config file for stat_collector
    """
    any_arch = True
    auto_backup = True


class RUN_ABT_STAT_FETCHER_CONFIG(sdk2.Resource):
    """
    Config file for stat_fetcher
    """
    any_arch = True
    auto_backup = True


class RUN_ABT_METRICS_REPORT(sdk2.Resource):
    """
    File with calculated metrics and file with calculated features
    """
    any_arch = True
    auto_backup = True


class COMPARE_ABT_METRICS_REPORT(sdk2.Resource):
    """
    Diff json file with added, removed, not changed and changed metrics
    """
    any_arch = True
    auto_backup = True


class TEST_ABT_METRICS_DIFF_REPORT(sdk2.Resource):
    """
    Diff report file with added, removed and changed metrics
    """
    any_arch = True
    auto_backup = True


class TEST_ABT_METRICS_DIFF_REPORT_PREVIEW(sdk2.Resource):
    """
    Diff report review file with added, removed, not changed and changed metrics
    """
    any_arch = True
    auto_backup = True


class ABT_METRICS_DIFF_REPORT_TEXT(sdk2.Resource):
    """
    Data diff report file with added, removed and changed metrics
    """
    any_arch = True
    auto_backup = True


class PREPARE_ABT_REGRESSION_SAMPLE_REPORT(sdk2.Resource):
    """
    Information about released sessions sample
    """
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers


class SESSION_MANAGER_RPC_EXECUTABLE(sdk2.Resource):
    """
        session manager rpc binary
    """
    releasable = True
    any_arch = False
    executable = True
    auto_backup = True
    releasers = experiment_releasers


class EXP_DAEMON_EXECUTABLE(sdk2.Resource):
    """
        exp daemon binary
    """
    releasable = True
    any_arch = False
    executable = True
    auto_backup = True
    releasers = experiment_releasers + ["robot-testenv"]


class BROWSER_XML_RESOURCE(sdk2.Resource):
    """
        browser xml resource (using in usersplit)
    """
    releasable = True
    executable = False
    auto_backup = True
    releasers = experiment_releasers


class SESSION_MANAGER_FRONTEND(sdk2.Resource):
    """
        session manager frontend tar
    """
    releasable = True
    any_arch = False
    executable = True
    auto_backup = True
    releasers = experiment_releasers + ['nerevar']


class ABT_COFE_BEAN(sdk2.Resource):
    """
    Files for a single test at 'quality/ab_testing/tests/cofe_machine/beans/data'
    """
    any_arch = True
    auto_backup = True


class ABT_COFE_YA_PACKAGE(sdk2.Resource):
    """
        COFE YA_PACKAGE
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser', 'robot-testenv']


class BS_COLLECTOR_YA_PACKAGE(sdk2.Resource):
    """
        BS_COLLECTOR YA_PACKAGE
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class ZC_YA_PACKAGE(sdk2.Resource):
    """
        YA_PACKAGE FOR ZC TOOL
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class ZC_RESULT(sdk2.Resource):
    """
        ZC RESULT
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class ZC_CPM_YA_PACKAGE(sdk2.Resource):
    """
        YA_PACKAGE FOR ZC CPM (ZC_CALCULATOR) BINARY
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class ZC_APC_CHECK_YA_PACKAGE(sdk2.Resource):
    """
        YA_PACKAGE FOR ZC APC_CHECK BINARY
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class ZC_CPM_V2_YA_PACKAGE(sdk2.Resource):
    """
        YA_PACKAGE FOR ZC CPM_V2 (ZC_CALCULATOR_V2) BINARY
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class COFE_FETCH_RESULT(sdk2.Resource):
    """
        cofe fetcher result
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class ABT_EXPERIMENTS_CONFIG_MERGER(sdk2.Resource):
    '''
    excomer binary tar
    '''
    releasable = True
    any_arch = False
    auto_backup = True
    releasers = experiment_releasers


class WEB_FLAGS_COLLISIONS_RESAULT(sdk2.Resource):
    """
    Prepare resource for scripts.yql and flags
    """
    any_arch = True
    auto_backup = True


class PORTO_LAYER_PYTHON23_JAVA11_XENIAL(sdk2.Resource):
    """
    Interpreters layer for Razladki-wow
    """
    releasable = True


class PORTO_LAYER_RAZLADKI_WOW_ENV(sdk2.Resource):
    """
    Python environment for Razladki-wow
    Should be used on top of PORTO_LAYER_PYTHON23_JAVA11_XENIAL
    """
    releasable = True


class STAFF_JUICE_RESOURCE(sdk2.Resource):
    """Staff juice resource. It using in USaaS (UserSplitAsAService)"""
    releasable = True


class AB_TESTING_YA_PACKAGE(sdk2.Resource):
    """
        ABT YA_PACKAGE
    """
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class AB_TESTING_PREPARE_YA_PACKAGE(sdk2.Resource):
    """
        ABT prepare YA_PACKAGE
    """
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class AB_TESTING_SESSION_ANALYSIS_YA_PACKAGE(sdk2.Resource):
    """
        ABT session viewer session analysis YA_PACKAGE
    """
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class AB_TESTING_LSD_YA_PACKAGE(sdk2.Resource):
    """
        ABT LSD YA_PACKAGE
    """
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class ABT_EMS_EXECUTABLE(sdk2.Resource):
    """
        EMS binary
    """
    any_arch = False
    executable = True
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']


class AB_PLATFORM_SERVER(sdk2.Resource):
    """
        ab_platform package
    """
    any_arch = False
    releasable = True
    releasers = experiment_releasers + ['robot-srch-releaser']
