# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import mock
import unittest
from collections import defaultdict

import sandbox.sdk2 as sdk2
import sandbox.projects.release_machine.components.components_info as rm_comp
import sandbox.projects.release_machine.components.all as rmc
import sandbox.projects.release_machine.components.configs as configs
import sandbox.projects.release_machine.components.configs.all as all_cfgs
import sandbox.projects.release_machine.core.const as rm_const
import sandbox.projects.release_machine.core as rm_core
import sandbox.projects.release_machine.helpers.responsibility_helper as rm_responsibility
from sandbox.projects.release_machine.components.configs.release_machine_test import ReleaseMachineTestCfg
from sandbox.projects.release_machine.components.custom.release_machine_test import ReleaseMachineTestInfo
from sandbox.common.errors import TaskError, VaultError

#  These imports are necessary for test_resources_types test, don't remove them!
import sandbox.projects.ab_testing.resource_types as abt_resource_types  # noqa: UnusedImport
import sandbox.projects.adfox.resource_types as adfox_resource_types  # noqa: UnusedImport
from sandbox.projects.ads.infra.ads_infra_release_builder.resources import LogosBinary, LogosMonoNileUdf, AdsLogosDocs, LogosGraphDoc  # noqa: UnusedImport
import sandbox.projects.Afisha.resource_types as afisha_resource_types  # noqa: UnusedImport
import sandbox.projects.agency_rewards.resources  # noqa: UnusedImport
import sandbox.projects.altay  # noqa: UnusedImport
import sandbox.projects.answers.resources as answers_resource_types  # noqa: UnusedImport
import sandbox.projects.antirobot.resources  # noqa: UnusedImport
import sandbox.projects.app_host.resources as app_host_resource_type  # noqa: UnusedImport
import sandbox.projects.apphost_cachedaemon.resource_types  # noqa: UnusedImport
import sandbox.projects.april.multik.resources  # noqa: UnusedImport
import sandbox.projects.arc  # noqa: UnusedImport
import sandbox.projects.arcanum  # noqa: UnusedImport
import sandbox.projects.archive  # noqa: UnusedImport
import sandbox.projects.balance.resources  # noqa: UnusedImport
import sandbox.projects.balance_dcsaap.resources as balance_dcsaap_resources    # noqa: UnusedImport
import sandbox.projects.balancer.resources as balancer_resources  # noqa: UnusedImport
import sandbox.projects.barnavig.resources as barnavig_resources  # noqa: UnusedImport
import sandbox.projects.berthub.resources as berthub_resources  # noqa: UnusedImport
import sandbox.projects.bnpl.resources as fintech_bnpl_resources  # noqa: UnusedImport
import sandbox.projects.boltalka.resource_types as boltalka_resource_types  # noqa: UnusedImport
import sandbox.projects.bsyeti.common as bigb_resources  # noqa: UnusedImport
import sandbox.projects.clickdaemon.resources  # noqa: UnusedImport
import sandbox.projects.codesearch.resources  # noqa: UnusedImport
import sandbox.projects.common.search.gdb  # noqa: UnusedImport
import sandbox.projects.common.dynamic_models.resources as models_res  # noqa: UnusedImport
import sandbox.projects.common.wizard.resources as wizard_resources  # noqa: UnusedImport
import sandbox.projects.common_server_service_monitor.resources as cs_sm_resources  # noqa: UnusedImport
import sandbox.projects.cores.resources as cores_resources  # noqa: UnusedImport
import sandbox.projects.dialogovo.resource_types  # noqa: UnusedImport
import sandbox.projects.paskills_billing.resource_types  # noqa: UnusedImport
import sandbox.projects.dj.unity.resources  # noqa: UnusedImport
import sandbox.projects.dj.rthub.resources  # noqa: UnusedImport
import sandbox.projects.dwh.resources  # noqa: UnusedImport
import sandbox.projects.education.resource_types as education_resource_types  # noqa: UnusedImport
import sandbox.projects.EntitySearch.resource_types as es_resource_types  # noqa: UnusedImport
import sandbox.projects.favicon as resources_favicon  # noqa: UnusedImport
import sandbox.projects.feedback_platform.resources as feedback_resources  # noqa: UnusedImport
import sandbox.projects.findurl.resources as findurl_res  # noqa: UnusedImport
import sandbox.projects.fintech_risk.fallback_proxy.resources as fintech_fallback_proxy_resources  # noqa: UnusedImport
import sandbox.projects.fintech_risk.resources as fintech_risk_resources  # noqa: UnusedImport
import sandbox.projects.fintech_risk.sources.resources as fintech_risk_source_resources  # noqa: UnusedImport
import sandbox.projects.floyd.resources as floyd_resources  # noqa: UnusedImport
import sandbox.projects.garden.resources  # noqa: UnusedImport
import sandbox.projects.gemini as resources_gemini  # noqa: UnusedImport
import sandbox.projects.geosearch.resource_types as geo_types  # noqa: UnusedImport
import sandbox.projects.geosuggest.resources as geosuggest_resources  # noqa: UnusedImport
import sandbox.projects.home.resources as home_resources  # noqa: UnusedImport
import sandbox.projects.hollywood.common  # noqa: UnusedImport
import sandbox.projects.horadric.resources  # noqa: UnusedImport
import sandbox.projects.images.basesearch.resources as images_basesearch_resources  # noqa: UnusedImport
import sandbox.projects.images.daemons.resources as images_daemons_resources  # noqa: UnusedImport
import sandbox.projects.images.resource_types as images_resource_types  # noqa: UnusedImport
import sandbox.projects.images.robot.resources as images_robot_resources  # noqa: UnusedImport
import sandbox.projects.infra.resources as infra_resources  # noqa: UnusedImport
import sandbox.projects.infra.yp_dns.resources  # noqa: UnusedImport
import sandbox.projects.infra.yp_service_discovery.resources  # noqa: UnusedImport
import sandbox.projects.iot.common  # noqa: UnusedImport
import sandbox.projects.iot.common.resources  # noqa: UnusedImport
import sandbox.projects.irt.bannerland as resources_bannerland  # noqa: UnusedImport
import sandbox.projects.irt.bannerland.resources as bannerland_resources  # noqa: UnusedImport
import sandbox.projects.irt.blrt as resources_blrt  # noqa: UnusedImport
import sandbox.projects.irt.common  # noqa: UnusedImport
import sandbox.projects.jupiter as resources_jupiter  # noqa: UnusedImport
import sandbox.projects.kwyt.resources as resources_kwyt  # noqa: UnusedImport
import sandbox.projects.logs.resources  # noqa: UnusedImport
import sandbox.projects.media_crm.resource_types as media_crm_resource_types  # noqa: UnusedImport
import sandbox.projects.media_stories.resource_types as media_stories_resource_types  # noqa: UnusedImport
import sandbox.projects.memento.resource_types  # noqa: UnusedImport
import sandbox.projects.melter as resources_melter  # noqa: UnusedImport
import sandbox.projects.mercury as resources_mercury  # noqa: UnusedImport
import sandbox.projects.mirrors  # noqa: UnusedImport
import sandbox.projects.modadvert.resource_types as modadvert_resource_types  # noqa: UnusedImport
import sandbox.projects.morty.resources # noqa: UnusedImport
import sandbox.projects.mssngr.runtime.resources as mssngr_resources   # noqa: UnusedImport
import sandbox.projects.my_alice.resource_types  # noqa: UnusedImport
import sandbox.projects.news.resources as news_resources  # noqa: UnusedImport
import sandbox.projects.passport.create_passport_api_release_machine_marker_resource as passport_api_resources  # noqa: UnusedImport
import sandbox.projects.prs_ops.resources as prs_ops_resources  # noqa: UnusedImport
import sandbox.projects.quasar.resource_types as quasar_resource_types  # noqa: UnusedImport
import sandbox.projects.quasar.resource_types.deprecated  # noqa: UnusedImport
import sandbox.projects.quasar.resource_types.tv  # noqa: UnusedImport
import sandbox.projects.rasp.resource_types as rasp_resources  # noqa: UnusedImport
import sandbox.projects.rt_money.resources as rt_money_resources  # noqa: UnusedImport
import sandbox.projects.rasp.bus.utils.resources as bus_resources  # noqa: UnusedImport
import sandbox.projects.rtx as rtx_resources  # noqa: UnusedImport
import sandbox.projects.avia.resource_types as avia_resources  # noqa: UnusedImport
import sandbox.projects.kinopoisk.resource_types as kinopoisk_resources  # noqa: UnusedImport
import sandbox.projects.release_machine.resources as rm_resources  # noqa: UnusedImport
import sandbox.projects.report.resources as report_resources  # noqa: UnusedImport
import sandbox.projects.resource_types as resource_types  # noqa: UnusedImport
import sandbox.projects.rt_transcoder  # noqa: UnusedImport
import sandbox.projects.rthub.resources as resources_rthub  # noqa: UnusedImport
import sandbox.projects.rtmr.resources as resources_rtmr  # noqa: UnusedImport
import sandbox.projects.sawmill.resources  # noqa: UnusedImport
import sandbox.projects.scraper_over_yt.resources as scraper_over_yt_resources  # noqa: UnusedImport
import sandbox.projects.search_pers.resources as search_pers_resources  # noqa: UnusedImport
import sandbox.projects.setrace.resource_types as setrace_resource_types  # noqa: UnusedImport
import sandbox.projects.smarttv.resource_types as smarttv_resource_types  # noqa: UnusedImport
import sandbox.projects.smelter as resources_smelter # noqa: UnusedImport
import sandbox.projects.sprav.feedback  # noqa: UnusedImport
import sandbox.projects.supportai  # noqa: UnusedImport
import sandbox.projects.taxi.resources  # noqa: UnusedImport
import sandbox.projects.turbo.resources as turbo_resource_types  # noqa: UnusedImport
import sandbox.projects.ugc.resources as resources_ugc  # noqa: UnusedImport
import sandbox.projects.userdata.resources as userdata_resources  # noqa: UnusedImport
import sandbox.projects.VideoSearch.video_resource_types as video_resource_types  # noqa: UnusedImport
import sandbox.projects.vins.common.resources as vins_resources  # noqa: UnusedImport
import sandbox.projects.bass.common.resources as videobass_resources  # noqa: UnusedImport
import sandbox.projects.voicetech.resource_types as voicetech_resources  # noqa: UnusedImport
import sandbox.projects.weather as weather_resources  # noqa: UnusedImport
import sandbox.projects.websearch.basesearch.resources as websearch_basesearch_resources  # noqa: UnusedImport
import sandbox.projects.websearch.begemot.resources as bgr  # noqa: UnusedImport
import sandbox.projects.websearch.flags_provider.resources as flags_provider_resources  # noqa: UnusedImport
import sandbox.projects.websearch.middlesearch.resources as middle_resources  # noqa: UnusedImport
import sandbox.projects.websearch.rpslimiter.resources as rpslimiter_resources  # noqa: UnusedImport
import sandbox.projects.websearch.tunneller.resources as tunneller_resources  # noqa: UnusedImport
import sandbox.projects.websearch.upper.resources as upper_resources  # noqa: UnusedImport
import sandbox.projects.woland.resources as woland_resources  # noqa: UnusedImport
import sandbox.projects.workplace.resource_types as workplace_resources  # noqa: UnusedImport
import sandbox.projects.xurma.resources  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.FuryBuildAdfox as fury_build_adfox_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.FuryBuildCaptcha as fury_build_captcha_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.FuryBuildMarket as fury_build_market_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.FuryBuildRtXaron as fury_build_rtxaron_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.FuryBuildSuperMod as fury_build_supermod_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.FuryBuildMegaera as fury_build_megaera_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.FuryBuildRtPrebilling as fury_build_rtprebilling_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildAdmet as xurma_build_admet_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildAdmod as xurma_build_admod_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildAfraudita as xurma_build_afraudita_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildBs as xurma_build_bs_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildBtr as xurma_build_btr_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildDsp as xurma_build_dsp_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildEdadeal as xurma_build_edadeal_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildOnline as xurma_build_online_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildPrebilling as xurma_build_prebilling_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildTaxi as xurma_build_taxi_resource_types  # noqa: UnusedImport
import sandbox.projects.xurma.tasks.XurmaBuildZen as xurma_build_zen_resource_types  # noqa: UnusedImport
import sandbox.projects.yabs.infra.resource_types as yabs_infra_resource_types  # noqa: UnusedImport
import sandbox.projects.yabs.url_monitoring.resources as url_monitoring_resources  # noqa: UnusedImport
import sandbox.projects.ydo.resource_types  # noqa: UnusedImport
import sandbox.projects.ydo.backend.YdoBackendApphostSource.resource_types  # noqa: UnusedImport
import sandbox.projects.ydo.backend.YdoSaasSearchProxy.resource_types  # noqa: UnusedImport
import sandbox.projects.younglings.tutor.resources as tutor_resources  # noqa: UnusedImport
import sandbox.projects.yt.legacy.resource_types  # noqa: UnusedImport
import sandbox.projects.yp.resources  # noqa: UnusedImport
import sandbox.projects.yaphone.resource_types as yaphone_resource_types  # noqa: UnusedImport
import sandbox.projects.yabs.dropstat.resources  # noqa: UnusedImport
import sandbox.projects.yabs.ArtmonMetricProxy  # noqa: UnusedImport
import sandbox.projects.yabs.release_resources  # noqa: UnusedImport
import sandbox.projects.vh.frontend as frontend_vh_resourses  # noqa: UnusedImport
import sandbox.projects.voicetech.resource_types  # noqa: UnusedImport
from sandbox.projects.alisa_skills_rec.common import resources as alisa_skills_rec_resources  # noqa: UnusedImport
from sandbox.projects.collections import resources as collections_resources  # noqa: UnusedImport
from sandbox.projects.common.build.YaPackage import YaPackageResource  # noqa: UnusedImport
from sandbox.projects.cvdup import resource_types as cvdup_resources  # noqa: UnusedImport
from sandbox.projects.cvsearch.resources import AUTO_RU_360_POI_EXECUTABLE  # noqa: UnusedImport
from sandbox.projects.cvsearch.resources import CV_UNIVERSAL_PY_DAEMON_EXECUTABLE  # noqa: UnusedImport
from sandbox.projects.horizon.resources import news_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import health_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import zen_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import geo_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import ugc_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import antiadbtest_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import example_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import fei_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import caesar_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import jobs_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import faas_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import kinopoisk_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import lpc_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import market_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import newtestt_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import testing_vertical_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import newspartner_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import hiworld_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import lego_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import goods_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import newsrobot_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import myvert_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import rrload_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import booktaas_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import forms_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import garage_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import ydo_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import schoolbook_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import report_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import marketreport_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import smartcamerafront_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import laas_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import crm_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import stateful_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import begemot_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import sport_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import sportnewsrobot_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources import alicerpc_graphs_resources  # noqa: UnusedImport
from sandbox.projects.horizon import resources as horizon_res  # noqa: UnusedImport
from sandbox.projects.horizon.resources import vkus_graphs_resources as horizon_vkus_graph_resources  # noqa: UnusedImport
from sandbox.projects.horizon.resources.binaries import HorizonModelBinary  # noqa: UnusedImport
from sandbox.projects.images.cvdupacceptance import resources as cvdupacceptance_resources  # noqa: UnusedImport
from sandbox.projects.mssngr.rtc import resource_types as rtc_resources  # noqa: UnusedImport
from sandbox.projects.release_machine.release_engine import resources as re_resources  # noqa: UnusedImport
from sandbox.projects.stoker import resource_types as stoker_resources  # noqa: UnusedImport
from sandbox.projects.Travel import resources as travel_resources  # noqa: UnusedImport
from sandbox.projects.yabs.qa import resource_types as yabs_qa_resource_types  # noqa: UnusedImport
from sandbox.projects.yabs.infra import resource_types as yabs_infra_resource_types  # noqa: UnusedImport
from sandbox.projects.yappy import resource_types as yappy_resources  # noqa: UnusedImport
from sandbox.projects.yabs.YqlQueries import SerpDomainShows  # noqa: UnusedImport
from sandbox.projects.ydo.testenv import YdoSearchproxyTestPortalResponses, YdoSearchproxyTestWizardResponses  # noqa: UnusedImport
from sandbox.projects.BuildRTLine import rtline_resource_types  # noqa: UnusedImport
from sandbox.projects.dj.shard2_services.vhs import resources as vhs_resources # noqa: UnusedImport
from sandbox.projects.rmp.uac import resources as uac_resources  # noqa: UnusedImport
from sandbox.projects.zephyr import resources  # noqa: UnusedImport
from sandbox.projects.personal_cards.resources import (  # noqa: UnusedImport
    PersonalCardsBinary,

    PersonalCardsConfigProduction,
    PersonalCardsConfigTesting,

    PersonalCardsTvmConfigProduction,
    PersonalCardsTvmConfigTesting,

    PersonalCardsInstancectlConfig,
)
from sandbox.projects.matrix.resources import (  # noqa: UnusedImport
    # Matrix
    MatrixBinary,

    MatrixConfigDev,
    MatrixConfigProduction,
    MatrixConfigTesting,

    MatrixInstancectlConfig,
    MatrixLogrotateConfig,
    MatrixPushClientConfig,
    MatrixTvmToolConfig,

    # Matrix scheduler
    MatrixSchedulerBinary,

    MatrixSchedulerConfigProduction,
    MatrixSchedulerConfigTesting,

    MatrixSchedulerInstancectlConfig,
    MatrixSchedulerLogrotateConfig,
    MatrixSchedulerPushClientConfig,

    # Matrix worker
    MatrixWorkerBinary,

    MatrixWorkerConfigProduction,
    MatrixWorkerConfigTesting,

    MatrixWorkerInstancectlConfig,
    MatrixWorkerLogrotateConfig,
    MatrixWorkerPushClientConfig,
)
from sandbox.projects.blender import resource_types # noqa: UnusedImport
from sandbox.projects.bnpl import resources # noqa: UnusedImport
from sandbox.projects.chz import resources # noqa: UnusedImport
from sandbox.projects.user_sessions_rt import resources  # noqa: UnusedImport
from sandbox.projects.vcs_indexer import resources  # noqa: UnusedImport
from sandbox.projects.xml_counter import resources  # noqa: UnusedImport
from sandbox.projects.avia_resources import resources  # noqa: UnusedImport
from sandbox.projects import src_setup  # noqa: UnusedImport
# from sandbox.projects.itditp.BuildRecommenderManager import RecommenderManagerExecutable  # noqa: UnusedImport
# from sandbox.projects.rps_limiter import resource_types  # noqa: UnusedImport
# from sandbox.projects.sass.common.resources import SaasSsmPackage # noqa: UnusedImport
from sandbox.projects.YabsLmService import resource_types as yabs_lm_service_resource_types # noqa: UnusedImport


ROBO_REPO = 'robots'
ROBO_COMPS = ('exp_formulas_base', 'exp_formulas_mmeta')


class TestRMComponents(unittest.TestCase):
    NETWORK_DISABLED = None

    @classmethod
    def tearDownClass(cls):
        cls.NETWORK_DISABLED = False

    @classmethod
    def setUpClass(cls):
        print("Disabling network")
        import socket
        cls.NETWORK_DISABLED = True

        def guard(*args, **kwargs):
            if cls.NETWORK_DISABLED:
                raise AssertionError("Network should not be used in tests!")
            else:
                return socket.SocketType(*args, **kwargs)

        socket.socket = guard

        ignored = set()

        with mock.patch("sandbox.projects.abc.client.AbcClient"):
            with mock.patch("sandbox.projects.release_machine.helpers.svn_helper.SvnHelper.get_highest_folder"):
                with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                    cls.TESTED_COMPONENT_CLASSES = {
                        i: rmc.COMPONENTS[i] for i in rmc.get_component_names() if i not in ignored
                    }
                    cls.TESTED_COMPONENTS = [i() for i in cls.TESTED_COMPONENT_CLASSES.values()]
        if ignored:
            print("The following components are ignored:\n{}\n".format("\n* ".join(ignored)))
        print("Test components:\n{}\n".format("\n* ".join(cls.TESTED_COMPONENT_CLASSES.keys())))

    def assertHasAttr(self, obj, attr, msg):
        try:
            attr = getattr(obj, attr)
        except AttributeError:
            self.fail(msg)
        except (TaskError, VaultError):
            pass
        except Exception as e:
            self.fail("Unknown error for attr {} of {}: {}".format(attr, obj, e))

    def test_path_for_released_resource(self):
        from sandbox.sandboxsdk.svn import Arcadia

        class MyMock(object):
            major_release = 413
            minor_release = 7

            @classmethod
            def check(cls, url, **kwargs):
                return True

        branched = rm_comp.Branched()
        tagged = rm_comp.Tagged()
        for i in [branched, tagged]:
            i.svn_cfg__tag_dir = "test_tag_dir"
            i.svn_cfg__tag_folder_name = mock.Mock(return_value="test_tag_folder_name")

        with mock.patch.object(Arcadia, "check", MyMock.check):
            self.assertEquals(
                branched.path_for_released_resource(MyMock()),
                branched.full_tag_path(MyMock.minor_release, MyMock.major_release)
            )
            self.assertEquals(
                tagged.path_for_released_resource(MyMock()),
                tagged.full_tag_path(MyMock.major_release)
            )

    def test_tested_components(self):
        for c_info in self.TESTED_COMPONENTS:
            self._test_setting_revisions(c_info)
            self._test_merge_permissions(c_info)
            self._test_release_diff(c_info)

    def _test_release_diff(self, c_info):
        curr_version = {"scope_number": "11", "tag_number": "2"}
        old_deploy_data = rm_core.ReleasedResource(major_release=10, minor_release=3)
        same_deploy_data = rm_core.ReleasedResource(major_release=11, minor_release=2)
        new_major_deploy_data1 = rm_core.ReleasedResource(major_release=12, minor_release=1)
        new_major_deploy_data2 = rm_core.ReleasedResource(major_release=12, minor_release=5)
        self.assertEqual(
            c_info.release_diff(curr_version, old_deploy_data),
            rm_core.ReleaseDiff(rm_core.ReleaseDiff.Position.old)
        )
        self.assertEqual(
            c_info.release_diff(curr_version, same_deploy_data),
            rm_core.ReleaseDiff(rm_core.ReleaseDiff.Position.same)
        )
        self.assertEqual(
            c_info.release_diff(curr_version, new_major_deploy_data1),
            rm_core.ReleaseDiff(rm_core.ReleaseDiff.Position.new)
        )
        self.assertEqual(
            c_info.release_diff(curr_version, new_major_deploy_data2),
            rm_core.ReleaseDiff(rm_core.ReleaseDiff.Position.new)
        )
        if isinstance(c_info, rm_comp.Branched):
            old_minor_deploy_data = rm_core.ReleasedResource(major_release=11, minor_release=1)
            self.assertEqual(
                c_info.release_diff(curr_version, old_minor_deploy_data),
                rm_core.ReleaseDiff(rm_core.ReleaseDiff.Position.old, rm_core.ReleaseDiff.Type.minor)
            )
            new_minor_deploy_data = rm_core.ReleasedResource(major_release=11, minor_release=6)
            self.assertEqual(
                c_info.release_diff(curr_version, new_minor_deploy_data),
                rm_core.ReleaseDiff(rm_core.ReleaseDiff.Position.new, rm_core.ReleaseDiff.Type.minor)
            )

    def _test_merge_permissions(self, c_info):
        if not isinstance(c_info, rm_comp.Branched):
            return
        permission_type, people_groups = c_info.merges_cfg__permissions
        self.assertIn(permission_type, [rm_const.PermissionType.ALLOWED, rm_const.PermissionType.BANNED])
        acceptable_types = (list, tuple, set, frozenset)
        if people_groups:
            for attr in ["abc_services", "staff_groups", "logins"]:
                if getattr(people_groups, attr, None):
                    self.assertIsInstance(
                        getattr(people_groups, attr), acceptable_types,
                        "[{}] Attribute {} in permissions should be in {}, got {}".format(
                            c_info.name, attr, acceptable_types, type(attr)
                        )
                    )

    def test_tm_chat_is_list(self):
        for c_info in self.TESTED_COMPONENTS:
            self.assertTrue(
                isinstance(c_info.notify_cfg__tg__chats, list),
                "[{}] Tm_chat for component is not list: {}".format(
                    c_info.name, c_info.notify_cfg__tg__chats
                )
            )

    def test_component_can_be_created_with_unicode_name(self):
        comps = rmc.ComponentDict()
        comps.register((ReleaseMachineTestCfg.name, ), (ReleaseMachineTestInfo,))
        try:
            comps[unicode(ReleaseMachineTestCfg.name)]()
        except TypeError as te:
            self.fail(u"Unable to create component class with unicode name. COMPONENTS should allow it. {}".format(te))

    def test_use_startrek_flag(self):
        """ If `cfg.Notify.use_startrek` is `True` then the appropriate settings should be provided """
        for c_info in self.TESTED_COMPONENTS:
            if not c_info.notify_cfg__use_startrek:
                continue
            self.assertIsNotNone(
                c_info.notify_cfg__st,
                u"{c_name} has `use_startrek` set to `True` but {c_name} config `.notify_cfg.st` is `None`".format(
                    c_name=c_info.name,
                )
            )

    def test_component_info_properties_implemented(self):

        skip_list = [
            'nie',
            'first_rev', 'last_rev', 'first_revs',
            'last_scope_num', 'last_scope_path',
            'last_branch_num', 'last_branch_path', 'next_branch_num',
            'next_branch_path', 'prev_branch_num', 'prev_branch_path',
            'prev_major_release_path',
            'releases_cfg__wait_for_deploy_time_sec',
        ]

        def props(cls):

            return filter(
                lambda x: not x.startswith('__') and x not in skip_list,
                dir(cls),
            )

        errors = defaultdict(list)

        with mock.patch("sandbox.projects.abc.client.AbcClient"):
            with mock.patch("sandbox.projects.release_machine.helpers.svn_helper.SvnHelper.get_highest_folder"):
                with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                    for c_name, c_info_cls in self.TESTED_COMPONENT_CLASSES.items():
                        c_info = c_info_cls()
                        for prop in props(c_info_cls):
                            try:
                                getattr(c_info, prop)
                            except NotImplementedError:
                                errors[c_name].append(prop)
                            except (TaskError, VaultError):
                                pass
                            except Exception as e:
                                self.fail("Forbidden {} in {},\n{}".format(prop, c_name, e))
        if errors:
            errors_dump = u"\n\n".join(
                [name + u"\n- " + u",\n- ".join(value) for name, value in errors.items()]
            )

            self.fail(u"The following properties raise NotImplementedError:\n\n{}".format(errors_dump))

    def test_resources_types(self):
        # result = []
        # success = 0
        for c_info in self.TESTED_COMPONENTS:
            self.assertIsInstance(
                c_info.releases_cfg__resources_info, list,
                "[{}] Some releases_cfg__resources_info objects are not lists: {}".format(
                    c_info.name, c_info.releases_cfg__resources_info
                )
            )
            for res in c_info.releases_cfg__resources_info:
                # if res.name != res.resource_name:
                #     result.append("[{}] {} != {}".format(c_info.name, res.name, res.resource_name))
                # else:
                #     success += 1
                self._test_resource_type(res.resource_type, c_info.name)
        # self.fail("Got {} problems ({} ok):\n{}".format(len(result), success, "\n".join(result)))

    def _test_resource_type(self, resource_type, c_name):
        self.assertIsInstance(
            resource_type, basestring,
            "[{}] Resource {} is not an instance of basestring".format(c_name, resource_type)
        )

        if resource_type in [
            "SAAS_SSM_PACKAGE",  # RMDEV-2626
            "RPS_LIMITER_BINARY",  # RMDEV-2627
            "RPS_LIMITER_AGENT_BINARY",  # RMDEV-2627
            "RPS_LIMITER_MODEL_BINARY",  # RMDEV-2627
            "RPS_LIMITER_BALANCER_EXECUTABLE",  # RMDEV-2627
            "RECOMMENDER_MANAGER_EXECUTABLE",  # RMDEV-2628
            "YABS_HIT_MODELS_DAEMON",
            "K50_SHOPPING_PACKAGE",
        ]:
            return

        try:
            # sdk2.Resource[resource_type]
            type(sdk2.Resource).__registry__[resource_type]
        except Exception:
            self.fail(
                "Resource with name {} doesn't exist!\n"
                "Resource must be imported in this test "
                "(projects/release_machine/tests/test_release_machine_components.py) "
                "with #noqa!\n"
                "Also, don't forget to add PEERDIR to ya.make!".format(resource_type)
            )

    def test_bad_resource_type(self):
        with self.assertRaises(Exception):
            sdk2.Resource["qqqqq57"]

    def test_config_types(self):
        with mock.patch("sandbox.projects.abc.client.AbcClient"):
            with mock.patch("sandbox.projects.release_machine.helpers.svn_helper.SvnHelper.get_highest_folder"):
                with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                    for component_name in rmc.get_component_names():
                        c_info = rmc.COMPONENTS[component_name]()
                        config = all_cfgs.ALL_CONFIGS[component_name]()
                        if isinstance(c_info, rm_comp.Branched):
                            self.assertIsInstance(
                                config,
                                (configs.ReferenceBranchedConfig, configs.ReferenceCIConfig),
                                "ReferenceBranchedConfig or ReferenceCIConfig expected "
                                "for {} (since it's Branched), got {}".format(component_name, type(config)),
                            )
                        elif isinstance(c_info, rm_comp.Tagged):
                            self.assertIsInstance(
                                config,
                                configs.ReferenceTaggedConfig,
                                "ReferenceTaggedConfig expected for {name} (since it's Tagged), got {cls}".format(
                                    name=component_name,
                                    cls=type(config)
                                ),
                            )

    def test_startrek_components(self):
        with mock.patch("sandbox.projects.release_machine.helpers.svn_helper.SvnHelper.get_highest_folder"):
            with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                from sandbox.projects.abc.client import AbcClient
                from sandbox.projects.release_machine.helpers import u_helper

                expected_assignee = "responsible"
                assignee_mock = mock.Mock(return_value=expected_assignee)
                abc_get_people_mock = mock.patch.object(
                    AbcClient,
                    "get_people_from_service",
                    mock.Mock(return_value=[expected_assignee]),
                )
                abc_get_duty_login_mock = mock.patch.object(AbcClient, "get_current_duty_login", assignee_mock)
                u_get_duty_mock = mock.patch.object(u_helper.UApi, "get_on_duty", assignee_mock)

                with abc_get_people_mock, abc_get_duty_login_mock, u_get_duty_mock:
                    for c_info in self.TESTED_COMPONENTS:
                        if isinstance(c_info, rm_comp.mixin.Startreked):
                            self.assertTrue(
                                hasattr(c_info, "notify_cfg__st__ticket_filter"),
                                "Component {c_info} doesn't have notify_cfg__st__ticket_filter".format(
                                    c_info=c_info.name,
                                ),
                            )
                            self.assertTrue(
                                getattr(c_info, "notify_cfg__st__assignee", None),
                                "Component {c_info} doesn't have notify_cfg__st__assignee".format(c_info=c_info.name),
                            )

    def test_required_attributes(self):
        required_attrs = (
            "name",
            "releases_cfg__responsible",
            "display_name",
        )
        required_tag_attrs = (
            "testenv_cfg__trunk_db",
            "testenv_cfg__db_template",
        )
        required_branch_attrs = (
            "testenv_cfg__trunk_db",
            "testenv_cfg__db_template",
            "testenv_cfg__trunk_task_owner",
            "testenv_cfg__job_patch__ignore_match",
            "testenv_cfg__job_patch__change_frequency",
        )
        for c_info in self.TESTED_COMPONENTS:
            for attr in required_attrs:
                self.assertHasAttr(c_info, attr, "Component {} has no attr {}".format(c_info.name, attr))
            if c_info.is_branched:
                for attr in required_branch_attrs:
                    self.assertTrue(hasattr(c_info, attr), "Component {} has no attr {}".format(c_info.name, attr))
            elif c_info.is_tagged:
                for attr in required_tag_attrs:
                    self.assertTrue(hasattr(c_info, attr), "Component {} has no attr {}".format(c_info.name, attr))

    def test_tag_paths(self):
        required_tag_methods = ('full_tag_path', 'relative_tag_path', 'tag_path')
        with mock.patch("sandbox.projects.abc.client.AbcClient"):
            with mock.patch("sandbox.projects.release_machine.helpers.svn_helper.SvnHelper.get_highest_folder"):
                with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                    for c_info in self.TESTED_COMPONENTS:
                        if c_info.is_branched:
                            for m in required_tag_methods:
                                self.assertTrue(hasattr(c_info, m))
                                c_info_method = getattr(c_info, m)
                                self.assertTrue(callable(c_info_method))
                                self.assertIn('tag_num', c_info_method.func_code.co_varnames)
                                self.assertIn('branch_num', c_info_method.func_code.co_varnames)

    def _test_setting_revisions(self, c_info):
        if isinstance(c_info, rm_comp.NoTrunkReleased):
            first_rev = 123
            last_rev = 321
            c_info.set_first_rev(first_rev)
            c_info.set_last_rev(last_rev)
            self.assertEqual(c_info.first_rev, first_rev)
            self.assertEqual(c_info.last_rev, last_rev)

    def test_get_responsible(self):
        with mock.patch("sandbox.projects.release_machine.helpers.svn_helper.SvnHelper.get_highest_folder"):
            with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                self._test_get_responsible_without_service()

                from sandbox.projects.abc.client import AbcClient
                from sandbox.projects.release_machine.helpers import u_helper

                expected_responsible = "responsible"
                responsible_mock = mock.Mock(return_value=expected_responsible)
                abc_get_people_mock = mock.patch.object(AbcClient, "get_people_from_service", mock.Mock(return_value=[expected_responsible]))
                abc_get_duty_login_mock = mock.patch.object(AbcClient, "get_current_duty_login", responsible_mock)
                abc_get_component_id_by_service_slug_mock = mock.patch.object(
                    AbcClient,
                    "get_component_id_by_service_slug",
                    mock.Mock(return_value=11111),
                )
                u_get_duty_mock = mock.patch.object(u_helper.UApi, "get_on_duty", responsible_mock)

                with abc_get_people_mock, abc_get_duty_login_mock, u_get_duty_mock, (
                    abc_get_component_id_by_service_slug_mock
                ):
                    for c_name in rmc.get_component_names():
                        c_info = rmc.get_component(c_name)
                        self._test_get_responsible(c_info)

    def _test_get_responsible(self, c_info):
        responsible = c_info.get_responsible_for_release()
        self.assertIsInstance(
            responsible, basestring,
            "[{}] Release responsible is not string: {}".format(c_info.name, responsible)
        )
        responsible = c_info.get_responsible_for_component()
        self.assertIsInstance(
            responsible, basestring,
            "[{}] Component responsible is not string: {}".format(c_info.name, responsible)
        )
        if isinstance(c_info, rm_comp.mixin.Changelogged):
            responsible = c_info.get_responsible_for_wiki_page()
            self.assertIsInstance(
                responsible, basestring,
                "[{}] Wiki page responsible is not string: {}".format(c_info.name, responsible)
            )

        if isinstance(c_info.releases_cfg__responsible, configs.Responsible):
            self.assertIsInstance(c_info.releases_cfg__responsible.login, basestring)

        if isinstance(c_info.responsible, configs.Responsible):
            self.assertIsInstance(c_info.responsible.login, basestring)

        if isinstance(c_info, rm_comp.mixin.Changelogged):
            if isinstance(c_info.changelog_cfg__wiki_page_owner, configs.Responsible):
                self.assertIsInstance(c_info.changelog_cfg__wiki_page_owner.login, basestring)

    def _test_get_responsible_without_service(self):
        responsible_nt = configs.Responsible(abc=None, u=None, login="responsible")
        self.assertEqual(
            rm_responsibility.get_responsible_user_login(responsible_nt), "responsible",
            "Get responsible for components without service (abc or u) does not work",
        )

    def test_ignored_jobs(self):
        should_be_ignored = (
            "_{}__{{}}".format(rm_const.JobTypes.NEW_BRANCH),
            "_{}__{{}}".format(rm_const.JobTypes.CLONE_DB),
            "_{}__{{}}".format(rm_const.JobTypes.CHANGELOG_MAJOR),
            "_{}__{{}}".format(rm_const.JobTypes.STARTREK),
            "_{}__{{}}".format(rm_const.JobTypes.WIKI),
            "_{}__{{}}".format(rm_const.JobTypes.ACTION_PRE_RELEASE),
        )
        should_not_be_ignored = ["HYPOTHETICAL_NOT_IGNORED_JOB_1", "HYPOTHETICAL_NOT_IGNORED_JOB_2"]
        for c_info in self.TESTED_COMPONENTS:
            if c_info.is_branched:
                should_be_ignored_jobs = [i.format(c_info.name.upper()) for i in should_be_ignored]
                should_be_ignored_jobs = self._filter_jobs(c_info, should_be_ignored_jobs)
                self.assertListEqual(should_be_ignored_jobs, [])
                should_not_be_ignored_jobs = self._filter_jobs(c_info, should_not_be_ignored)
                self.assertListEqual(should_not_be_ignored_jobs, should_not_be_ignored)

    @staticmethod
    def _filter_jobs(c_info, jobs):
        if hasattr(c_info, "testenv_cfg__job_patch__ignore_prefix"):
            jobs = [i for i in jobs if not any(i.startswith(p) for p in c_info.testenv_cfg__job_patch__ignore_prefix)]
        if hasattr(c_info, "testenv_cfg__job_patch__ignore_match"):
            jobs = [i for i in jobs if i not in c_info.testenv_cfg__job_patch__ignore_match]
        return jobs

    def test_ignored_jobs_redefine(self):
        should_be_ignored = (
            "MERGE_FUNCTIONAL",
            "ROLLBACK_TRUNK_AND_MERGE_FUNCTIONAL",
            "ROLLBACK_TRUNK_FUNCTIONAL"
        )
        should_not_be_ignored = (
            "HYPOTHETICAL_NOT_IGNORED_JOB",
        )
        test_component = self.TESTED_COMPONENT_CLASSES[ReleaseMachineTestCfg.name]()
        really_ignored = test_component.testenv_cfg__job_patch__ignore_match
        name = test_component.name.upper()
        for i in should_be_ignored:
            self.assertIn(
                i.format(name),
                really_ignored,
                u"{} should be ignored but not found {}.testenv_cfg__job_patch__ignore_match".format(
                    i, name
                )
            )
        for i in should_not_be_ignored:
            self.assertNotIn(i.format(name), really_ignored)

    def test_svn_config(self):
        with mock.patch("sandbox.projects.abc.client.AbcClient"):
            with mock.patch("sandbox.projects.release_machine.helpers.svn_helper.SvnHelper.get_highest_folder"):
                with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                    for c_info in self.TESTED_COMPONENTS:
                        self.assertTrue(
                            getattr(c_info, 'svn_cfg', False),
                            "{} does not have `svn_cfg` attr".format(c_info.name)
                        )
                        self.assertIn(c_info.svn_cfg__REPO_NAME, c_info.svn_cfg__repo_base_url)
                        try:
                            self.assertIn(c_info.svn_cfg__repo_base_url, c_info.svn_cfg__main_url)
                        except TaskError:
                            # Sometimes calculation of `main_url` requires sandbox environment,
                            # otherwise `TaskError` is raised which we skip silently since it
                            # doesn't actually indicate any configuration error
                            pass

    def test_components_state_hardcode(self):
        for c_name in ROBO_COMPS:
            c_info = rmc.get_component(c_name)
            self.assertEqual(
                c_info.svn_cfg__REPO_NAME,
                ROBO_REPO,
                u"{c_name}",
            )
            self.assertIn(ROBO_REPO, c_info.svn_cfg__main_url)

    def test_job_name(self):
        self.assertEqual(
            rm_const.JobTypes.rm_job_name(rm_const.JobTypes.TEST, "MY_SHINY_COMPONENT", "PARAMETRIZED"),
            "_TEST__MY_SHINY_COMPONENT__PARAMETRIZED",
        )
        self.assertEqual(
            rm_const.JobTypes.rm_job_name(rm_const.JobTypes.NEW_TAG, "MY_SHINY_COMPONENT"),
            "_NEW_TAG__MY_SHINY_COMPONENT",
        )
        self.assertEqual(
            rm_const.JobTypes.rm_job_name(rm_const.JobTypes.RM_CRAWLER),
            "_RM_CRAWLER",
        )

    def test_each_component_can_block_release_notifications_to_release_tickets(self):
        tested_attr_name = 'notify_on_release_to_release_st_ticket'
        for c_info in self.TESTED_COMPONENTS:
            if not c_info.notify_cfg__use_startrek:
                continue
            self.assertTrue(
                hasattr(c_info.notify_cfg__st, tested_attr_name),
                'Component {component_name} does not have {tested_attr_name} attribute!'.format(
                    component_name=c_info.name,
                    tested_attr_name=tested_attr_name,
                ),
            )

    def test_get_release_numbers(self):
        class Res(object):
            __slots__ = ("task_id", "major_release_num", "minor_release_num")

            def __init__(self, major_release_num=None, minor_release_num=None):
                self.task_id = 12345
                self.major_release_num = major_release_num
                self.minor_release_num = minor_release_num

        mock_resource1 = Res()
        mock_resource2 = Res(44, 22)
        mock_resource3 = Res(99)
        item1 = rm_core.ReleasedItem("item1", mock_resource1)
        item2 = rm_core.ReleasedItem("item2", mock_resource2)
        item3 = rm_core.ReleasedItem("item3", mock_resource3)

        with mock.patch("sandbox.projects.common.sdk_compat.task_helper.task_obj"):
            for c_info in self.TESTED_COMPONENTS:
                major, minor = self._get_release_numbers_by_url(c_info, item1, "arcadia:/trunk/arcadia")
                self.assertIsNone(major)
                self.assertIsNone(minor)
                if c_info.is_branched:
                    major, minor = self._get_release_numbers_by_url(c_info, item1, "arcadia:/trunk/arcadia@4321432")
                    self.assertIsNone(major)
                    self.assertIsNone(minor)
                    major, minor = self._get_release_numbers_by_url(
                        c_info, item1,
                        "arcadia:/arc/tags/something/bad{}/arcadia@123456".format(c_info.svn_cfg__tag_folder_name(1, 1))
                    )
                    self.assertIsNone(major)
                    self.assertIsNone(minor)
                    major, minor = self._get_release_numbers_by_url(
                        c_info, item1,
                        "arcadia:/arc/tags/c/{}/arcadia@5455238".format(c_info.svn_cfg__tag_path(249, 5))
                    )
                    self.assertEqual(major, "249")
                    self.assertEqual(minor, "5")
                    major, minor = self._get_release_numbers_by_url(c_info, item2, "any string")
                    self.assertEqual(major, "44")
                    self.assertEqual(minor, "22")
                elif c_info.is_tagged:
                    major, minor = self._get_release_numbers_by_url(
                        c_info, item1, "{}/arcadia@123456".format(c_info.svn_cfg__tag_path(1))
                    )
                    self.assertEqual(major, "1")
                    self.assertIsNone(minor)
                    major, minor = self._get_release_numbers_by_url(c_info, item3, "any string")
                    self.assertEqual(major, "99")
                    self.assertIsNone(minor)
                else:
                    major, minor = self._get_release_numbers_by_url(
                        c_info, item1, "arcadia:/mytag/trunk/arcadia@123456"
                    )
                    self.assertEqual(major, "123456")
                    self.assertIsNone(minor)

    def _get_release_numbers_by_url(self, c_info, release_item, url):
        with mock.patch(
            "sandbox.projects.release_machine.rm_utils.get_input_or_ctx_field",
            mock.MagicMock(return_value=url)
        ):
            release_numbers = c_info.get_release_numbers(release_item)
            self.assertIsInstance(
                release_numbers, tuple,
                "[{}] Method get_release_numbers should return tuple, got {}".format(c_info.name, release_numbers)
            )
            self.assertEqual(
                len(release_numbers), 2,
                "[{}] Method get_release_numbers should return tuple of exactly two elements, got {}".format(
                    c_info.name, release_numbers
                )
            )
            return release_numbers

    def test_stopping_betas(self):
        with mock.patch("sandbox.projects.abc.client.AbcClient"):
            with mock.patch("sandbox.projects.release_machine.helpers.svn_helper.SvnHelper.get_highest_folder"):
                with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                    for c_info in self.TESTED_COMPONENTS:
                        if c_info.yappy_cfg is None:
                            continue
                        for beta_name in c_info.yappy_cfg.betas:
                            self.assertGreaterEqual(c_info.yappy_cfg.get_stop_betas_gap(beta_name), 0)


if __name__ == '__main__':
    unittest.main()
