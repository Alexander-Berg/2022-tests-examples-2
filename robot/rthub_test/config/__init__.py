from collections import OrderedDict
from robot.cmpy.library.config import NonOverridableConfig
from os.path import join as pj
from robot.cmpy.library.utils import export_to_env
from robot.cmpy.library.yt_tools import fill_config_with_yt_env

FUNCTIONS_CM = "functions.cm"
RTHUB_TEST_CMPY_MODULE = "robot.rthub.cmpy.rthub_test"


def create_config():
    config = NonOverridableConfig()

    config.Modules = OrderedDict()
    config.add_cmpy_modules(RTHUB_TEST_CMPY_MODULE, [
        ("deploy_cmpy", FUNCTIONS_CM),
        ("main", FUNCTIONS_CM),
        ("deploy", FUNCTIONS_CM),
        ("cleanup", FUNCTIONS_CM),
        ("index_data", FUNCTIONS_CM),
        ("build_baseline", FUNCTIONS_CM),
        ("build_test", FUNCTIONS_CM),
        ("sample", FUNCTIONS_CM),
    ])

    # Development/testing options
    config.DryRun = False

    # Paths and prefixes
    config.Jupiter = ''
    config.ScriptsDir = pj(config.Jupiter, 'scripts')
    config.JupiterCmDir = pj(config.ScriptsDir, "robot", "jupiter", "cm")
    config.JupiterScriptsDir = pj(config.JupiterCmDir, "scripts")
    config.TmpDir = '/persistent/tmp'
    config.BinDir = pj(config.Jupiter, 'bin')
    config.CmpyDir = 'cmpy/rthub_test_cmpy'
    config.TokenDir = ''

    config.ArcadiaPath = 'arcadia:/arc/trunk/arcadia'

    config.MrServer = "arnold.yt.yandex.net"
    config.YtProxy = "arnold.yt.yandex.net"
    config.YtProxyName = 'arnold'
    config.MrPrefix = "//home/kwyt-test/rthub_test"
    config.YtPrefix = "//home/kwyt-test/rthub_test"
    config.YtPool = 'kwyt-test'
    config.SampleSize = 10
    config.SampleDstDir = pj(config.YtPrefix, 'test_data')

    config.JupiterProdPrefix = '//home/jupiter'
    config.KwytYtPrefix = '//home/kwyt'

    # RTHub
    config.Baseline.RTHub = ""
    config.Baseline.PagesRTHubDir = pj(config.Jupiter, 'baseline_pages_rthub')
    config.Baseline.HostsRTHubDir = pj(config.Jupiter, 'baseline_hosts_rthub')
    config.Baseline.AppDocsRTHubDir = pj(config.Jupiter, 'baseline_app_docs_rthub')
    config.Baseline.TeBaseName = "rthub-" + str(config.Baseline.RTHub)
    config.Baseline.YtAttribute = "@prod_rthub_version"
    config.Test.RTHub = ""
    config.Test.PagesRTHubDir = pj(config.Jupiter, 'test_pages_rthub')
    config.Test.HostsRTHubDir = pj(config.Jupiter, 'test_hosts_rthub')
    config.Test.AppDocsRTHubDir = pj(config.Jupiter, 'test_app_docs_rthub')
    config.Test.TeBaseName = "rthub-" + str(config.Test.RTHub)
    config.Test.YtAttribute = "@new_rthub_version"

    # Tokens
    config.YtTokenName = "robot-kwyt-test"
    config.YdbTokenName = "robot-kwyt-ydb"
    config.NirvanaTokenName = "robot-kwyt-test-nirvana"
    config.MetricsTokenName = "robot-kwyt-test-metrics"
    config.SandboxTokenName = "robot-kwyt-test-sandbox"
    config.NannyTokenName = "robot-kwyt-test-nanny"

    # YT
    config.YtTokenPath = pj(config.TokenDir, config.YtTokenName)

    config.OperationOwners = [
        "robot-kwyt-test",
        "zagevalo",
        "lexeyo",
        "gusev-p",
        "izetag",
        "antervis",
        "zhenyok",
        "lazv85"
    ]

    fill_config_with_yt_env(
        config,
        intermediate_data_account="kwyt-test",
        operation_owners=config.OperationOwners,
        suspend_operation_if_account_limit_exceeded=True,
        yt_pool="kwyt-test",
    )
    config.VanillaYtPool = config.YtPool

    # Nanny options
    config.Nanny.ApiUrl = 'http://nanny.yandex-team.ru/'
    config.Nanny.DeployTaskType = 'YA_MAKE_RELEASE_TO_NANNY'
    config.Nanny.ServiceId = 'rthub_test_cm_control'
    config.NannyTokenPath = pj(config.TokenDir, config.NannyTokenName)

    # YDB
    config.YdbTokenPath = pj(config.TokenDir, config.YdbTokenName)

    config.RTHubTestCm = "https://rthub-test.n.yandex-team.ru"

    # Sandbox options
    config.SandboxTokenPath = pj(config.TokenDir, config.SandboxTokenName)

    # Trnasfer Manager
    config.TransferManager.Host = 'transfer-manager.yt.yandex.net'
    config.TransferManager.Port = 80

    # Z2
    config.Z2.Config = "JUPITER_BETA_VM"
    config.Z2.ApiKey = "716559e6-71e8-4f4f-92dd-6d332329148d"

    export_yt_variables(config)

    config.freeze()

    return config


def export_yt_variables(config):
    # YT_POOL is ignored if YT_SPEC is provided - see YT-5841
    export_to_env("YT_POOL", config.YtPool)
    export_to_env("YT_SPEC", config.YtSpec)
    export_to_env("YT_TOKEN_PATH", config.YtTokenPath)
