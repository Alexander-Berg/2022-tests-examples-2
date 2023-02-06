from robot.cmpy.library.config import Configuration, cmpy_config_creator
from robot.jupiter.cmpy.config import (
    add_control_modules,
    add_jupiter_common_modules,
    check_jupiter_config,
    update_config)


@cmpy_config_creator(Configuration.RTHUB_TEST, check_jupiter_config)
def create_config(config):
    config.MrPrefix = '//home/kwyt-test/rthub_test'

    config.QA.Baseline = "rthubbaseline"
    config.QA.Beta = "rthubtest"
    config.QA.PRS.TimeoutMinutes = 300
    config.Callisto.Prefix = ""
    config.Cleanup.AcceptanceStates = 3
    config.Delivery.MrPrefix = config.MrPrefix
    config.YtUser = "robot-kwyt-test"
    config.IntermediateDataAccount = "kwyt-test"
    config.QA.MetricsTemplateId = {None: "aa828638508b2b0501508f31225301ab"}
    config.PudgeEnabled = False
    config.ShardDeploy.BetaConfiguration = "rthub"
    config.ShardDeploy.QueueServer = 'arnold.yt.yandex.net'
    config.ShardDeploy.NodePrefix = '//home/kwyt-test'
    config.ShardDeploy.HasMiddleSearchShard = False
    config.ShardDeploy.CheckStatusTable = True
    config.ShardDeploy.CheckViewer = False
    config.Stats.SolomonCluster = "rthub-test"
    config.SpreadRTHub.DeleteExport = "--spread-remove-export"
    config.HostdatAsync.DeleteExport = "--spread-remove-export"
    config.YtPool = "kwyt-test"
    config.SkipSwitchBranch = True

    config.IncrementalMode = False
    config.PudgeEnabled = False

    config.YtTokenName = "robot-kwyt-test"
    config.NirvanaTokenName = "robot-kwyt-test-nirvana"
    config.MetricsTokenName = "robot-kwyt-test-metrics"
    config.SandboxTokenName = "robot-kwyt-test-sandbox"
    config.NannyTokenName = "robot-kwyt-test-nanny"
    config.YappyTokenName = "robot-kwyt-test-yappy"

    config.MetricsToNotify = ""
    config.MetricsWebQualityMails = ";".join(["rthub@yandex-team.ru"])

    config.NannyDeploy.ServiceId = "rthub_test_cm"
    config.NannyDeploy.ReleaseType = "stable"

    config.OperationOwners = [
        'kwyt'
    ]

    update_config(config)

    add_control_modules(config, 'rthub_test.cm')
    add_jupiter_common_modules(config)

    return config
