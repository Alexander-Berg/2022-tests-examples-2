# coding: utf8
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from sandbox.projects.release_machine.components.configs.rasp.api_public import ApiPublicCfg
from sandbox.projects.release_machine.components.configs.rasp.blablacar import BlablacarCfg
from sandbox.projects.release_machine.components.configs.rasp.content_admin import ContentAdminCfg
from sandbox.projects.release_machine.components.configs.rasp.content_backend import ContentBackendCfg
from sandbox.projects.release_machine.components.configs.rasp.crosslink import CrosslinkCfg
from sandbox.projects.release_machine.components.configs.rasp.export import ExportCfg
from sandbox.projects.release_machine.components.configs.rasp.http_proxy_cache import HttpProxyCacheCfg
from sandbox.projects.release_machine.components.configs.rasp.info_center import InfoCenterCfg
from sandbox.projects.release_machine.components.configs.rasp.morda import MordaCfg
from sandbox.projects.release_machine.components.configs.rasp.morda_backend import MordaBackendCfg
from sandbox.projects.release_machine.components.configs.rasp.pathfinder_maps import PathfinderMapsCfg
from sandbox.projects.release_machine.components.configs.rasp.pathfinder_proxy import PathfinderProxyCfg
from sandbox.projects.release_machine.components.configs.rasp.suburban_selling import SuburbanSellingCfg
from sandbox.projects.release_machine.components.configs.rasp.suburban_widget import SuburbanWidgetCfg
from sandbox.projects.release_machine.components.configs.rasp.suburban_wizard_api import SuburbanWizardApiCfg
from sandbox.projects.release_machine.components.configs.rasp.suggests import SuggestsCfg
from sandbox.projects.release_machine.components.configs.rasp.touch import TouchCfg
from sandbox.projects.release_machine.components.configs.rasp.train_api import TrainApiCfg
from sandbox.projects.release_machine.components.configs.rasp.train_offer_storage import TrainOfferStorageCfg
from sandbox.projects.release_machine.components.configs.rasp.train_wizard_api import TrainWizardApiCfg
from sandbox.projects.release_machine.components.configs.rasp.wizard_proxy_api import WizardProxyApiCfg


class TestFinalConfigs(unittest.TestCase):
    @classmethod
    def _test_config_creation(cls, config_cls):
        config = config_cls()
        objects = [
            config,
            MordaBackendCfg.Testenv(config.name),
            MordaBackendCfg.Testenv.JobGraph(config.name),
            MordaBackendCfg.Releases(config, config.name, config.responsible),
            MordaBackendCfg.Notify(config.name),
        ]
        return objects

    def test_creation(self):
        config_classes = [
            ApiPublicCfg,
            BlablacarCfg,
            ContentAdminCfg,
            ContentBackendCfg,
            CrosslinkCfg,
            ExportCfg,
            HttpProxyCacheCfg,
            InfoCenterCfg,
            MordaCfg,
            MordaBackendCfg,
            PathfinderMapsCfg,
            PathfinderProxyCfg,
            SuburbanSellingCfg,
            SuburbanWidgetCfg,
            SuburbanWizardApiCfg,
            SuggestsCfg,
            TouchCfg,
            TrainApiCfg,
            TrainOfferStorageCfg,
            TrainWizardApiCfg,
            WizardProxyApiCfg,
        ]
        objects = []
        for cfg_cls in config_classes:
            objects += TestFinalConfigs._test_config_creation(cfg_cls)
        for o in objects:
            assert o

        # check that all with unique names
        configs = [cfg_cls() for cfg_cls in config_classes]
        config_dict = {cfg.name: cfg for cfg in configs}
        assert len(configs) == len(config_dict)
