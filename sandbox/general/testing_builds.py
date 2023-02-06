# -*- coding: utf-8 -*-
import logging
from copy import deepcopy

from enum import Enum

from sandbox.projects.browser.autotests_qa_tools.common import (
    BROWSER_BITBUCKET_PROJECT, BROWSER_BITBUCKET_REPO, TEAMCITY_URL)
from sandbox.projects.browser.common.teamcity import run_teamcity_build

logger = logging.getLogger(__file__)


class BuildTemplate(object):

    def __init__(self, build_configuration_name, params=None, tags=None):
        self.build_configuration_name = build_configuration_name
        self.params = params if params is not None else {}
        self.tags = tags if tags is not None else []


class RegressionBuildsKit(object):

    def __init__(self, browser=None, autotests=None, fake_browser=None):
        self.browser = browser
        self.autotests = autotests
        self.fake_browser = fake_browser


class AutotestsBuilds(Enum):

    android = BuildTemplate(
        build_configuration_name='Browser_Tests_Build_Android'
    )
    ios = BuildTemplate(
        build_configuration_name='Browser_Tests_Build_Ios',
        tags=['trigger:nightly_tests_trigger.yaml:nightly_ios_automation']
    )
    win = BuildTemplate(
        build_configuration_name='Browser_Tests_Build_Win',
        params={
            "env.MDS_EXPIRE_DEFAULT": "3d",
            "env.MDS_EXPIRE_MASTER": "3d",
            "env.MDS_EXPIRE_MERGE": "3d"
        }
    )
    mac = BuildTemplate(
        build_configuration_name='Browser_Tests_Build_Mac',
        params={
            "env.MDS_EXPIRE_DEFAULT": "3d",
            "env.MDS_EXPIRE_MASTER": "3d",
            "env.MDS_EXPIRE_MERGE": "3d"
        }
    )


class ReleaseKits(Enum):

    android_alpha = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_AndroidBuilds_ReleaseBuilds_Alpha'
        ),
        autotests=AutotestsBuilds.android.value
    )
    android_beta = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_AndroidBuilds_ReleaseBuilds_Beta'
        ),
        autotests=AutotestsBuilds.android.value
    )
    android_broteam = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_AndroidBuilds_ReleaseBuilds_Broteam'
        ),
        autotests=AutotestsBuilds.android.value
    )
    android_custom_internal = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_AndroidBuilds_ReleaseBuilds_CustomInternalBuild'
        ),
        autotests=AutotestsBuilds.android.value
    )
    android_internal = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_AndroidBuilds_ReleaseBuilds_Internal'
        ),
        autotests=AutotestsBuilds.android.value
    )
    android_stable = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_AndroidBuilds_ReleaseBuilds_Stable'
        ),
        autotests=AutotestsBuilds.android.value
    )
    ios_canary = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_IOSBuilds_Canary'
        ),
        autotests=AutotestsBuilds.ios.value
    )
    ios_public_beta = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_IOSBuilds_Beta'
        ),
        autotests=AutotestsBuilds.ios.value
    )
    ios_searchapp_stable = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_IOSBuilds_Releases_SearchAppStable'
        ),
        autotests=AutotestsBuilds.ios.value
    )
    ios_stable = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_IOSBuilds_Stable'
        ),
        autotests=AutotestsBuilds.ios.value
    )
    android_autotests_nightly = RegressionBuildsKit(
        browser=BuildTemplate(
            build_configuration_name='Browser_AndroidBuilds_ReleaseBuilds_Internal'
        ),
        autotests=AutotestsBuilds.android.value
    )
    android_searchapp_nightly = RegressionBuildsKit(
        autotests=AutotestsBuilds.android.value
    )
    ios_autotests_nightly = RegressionBuildsKit(
        autotests=AutotestsBuilds.ios.value
    )
    desktop_win_binary_tests = RegressionBuildsKit(
        autotests=AutotestsBuilds.win.value
    )
    desktop_mac_binary_tests = RegressionBuildsKit(
        autotests=AutotestsBuilds.mac.value
    )
    desktop_win = RegressionBuildsKit(
        autotests=AutotestsBuilds.win.value,
        browser=BuildTemplate(
            build_configuration_name='BrowserBrandedDistributives_BrandedBetaWin',
            tags=['n-beta'],
            params={
                "partner-names": "@nightly",
                "brand-names": "yandex int tb by"
            }
        ),
        fake_browser=BuildTemplate(
            build_configuration_name='BrowserBrandedDistributives_BrandedBetaWin',
            tags=['n-beta'],
            params={
                "partner-names": "@nightly",
                "brand-names": "yandex int tb by"
            }
        )
    )
    desktop_mac = RegressionBuildsKit(
        autotests=AutotestsBuilds.mac.value,
        browser=BuildTemplate(
            build_configuration_name='BrowserBrandedDistributives_BrandedBetaMac',
            tags=['n-beta'],
            params={
                "partner-names": "@nightly",
                "brand-names": "yandex int tb by",
                "sandbox.disable_notarization": True
            }
        ),
        fake_browser=BuildTemplate(
            build_configuration_name='BrowserBrandedDistributives_BrandedBetaMac',
            tags=['n-beta'],
            params={
                "partner-names": "@nightly",
                "brand-names": "yandex int tb by",
                "sandbox.disable_notarization": True
            }
        )
    )


class Builder(object):

    def __init__(self, ya_clients):
        self.clients = ya_clients

    def build_kit(self, kit_name, branch, commit, params=None, tags=None, build_autotests=True):
        params = params or {}
        tags = tags or []
        buils_kit = ReleaseKits[kit_name].value
        commit = commit or self.clients.bitbucket.get_latest_commit(
            BROWSER_BITBUCKET_PROJECT, BROWSER_BITBUCKET_REPO, branch)
        result = {}
        if buils_kit.browser:
            result["browser"] = self.run_build_template(buils_kit.browser, branch, commit, params, tags)
        if buils_kit.fake_browser:
            result["fake_browser"] = self.run_build_template(buils_kit.fake_browser, branch, commit, params, tags)
        if build_autotests and buils_kit.autotests is not None:
            result["autotests"] = self.run_build_template(buils_kit.autotests, branch, commit, params={}, tags=[])
        return result

    def run_build_template(self, template, branch, commit, params, tags):
        params = params or {}
        tags = tags or []
        change = self.clients.get_change(commit, template.build_configuration_name)
        merged_params = deepcopy(template.params)
        merged_params.update(params)
        merged_tags = set(template.tags + tags)
        build = run_teamcity_build(
            tc=self.clients.teamcity,
            branch=branch,
            build_type=template.build_configuration_name,
            parameters=merged_params,
            comment=None,
            tags=merged_tags,
            pool=None,
            change=change,
            snapshot_dependencies=None,
            make_unique=True,
            make_deps_unique=True,
            put_to_top=False
        )
        logger.info("Triggered build: {}/viewLog.html?buildId={}".format(TEAMCITY_URL, build.id))
        return build
