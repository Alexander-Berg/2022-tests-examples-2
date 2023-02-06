# -*- coding:utf-8 -*-
from sandbox.projects.horizon.resources import HorizonAgentConfig, AppHostStableBranch


class HorizonAgentConfigTest(HorizonAgentConfig):
    releasers = HorizonAgentConfig.releasers + ["APP_HOST"]


class AppHostStableBranchTest(AppHostStableBranch):
    releasers = AppHostStableBranch.releasers + ["APP_HOST"]
