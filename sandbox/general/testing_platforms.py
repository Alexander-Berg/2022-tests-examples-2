# -*- coding: utf-8 -*-
import re

import sandbox

from enum import Enum


class SupportedPlaftorms(Enum):

    Win7x64 = dict(testpalm_automation_os_marks=["Win7 x64"],
                   allure_name="Windows 7 64bit",
                   node_label="win7-x64-ru-clos",
                   run_env_name="Windows 7 x64",
                   isolate_config_name="win_7_x64.json")

    Win7x32 = dict(testpalm_automation_os_marks=["Win7 x32"],
                   allure_name="Windows 7 32bit",
                   node_label="win7-x86-clos",
                   run_env_name="Windows 7 x86",
                   isolate_config_name="win_7_x32.json")

    # Win8x64 = dict(testpalm_automation_os_marks=["Win8.1 x64", "Win8 x64"],
    #                allure_name="Windows 8.1 64bit",
    #                node_label="win8-clos",
    #                run_env_name="Windows 8.1 x64",
    #                isolate_config_name="win_8_x64.json")

    Win10x64 = dict(testpalm_automation_os_marks=["Win10 x64"],
                    allure_name="Windows 10 64bit",
                    node_label="win10-x64-clos",
                    run_env_name="Windows 10 x64",
                    isolate_config_name="win_10_x64.json")

    # MacOS_10_13_5 = dict(testpalm_automation_os_marks=["MacOS 10.13"],
    #                      allure_name="MacOS 10.13.5 64bit",
    #                      node_label="osx",
    #                      run_env_name=None,
    #                      isolate_config_name=None)

    MacOS_10_14 = dict(isolate_config_name="mac.json")
    APad = dict(isolate_config_name="apad.json")
    APhone = dict(isolate_config_name="aphone.json")
    IPhone = dict(isolate_config_name="ios.json")
    DefaultMac = MacOS_10_14
    DefaultWin = Win10x64


class TestingPlatforms(object):

    testrun_environments = {
        "win_7_x64": SupportedPlaftorms.Win7x64,
        "win_7_x32": SupportedPlaftorms.Win7x32,
        "win_10_x64": SupportedPlaftorms.Win10x64,
        "Windows 7 32bit": SupportedPlaftorms.Win7x32,
        "Windows 7 64bit": SupportedPlaftorms.Win7x64,
        "Windows 10 64bit": SupportedPlaftorms.Win10x64,
        "Windows 7 x64": SupportedPlaftorms.Win7x64,
        "Windows 10 x64": SupportedPlaftorms.Win10x64,
        "Virtual Windows 7 x86": SupportedPlaftorms.Win7x32,
        "Virtual Windows 7 x64": SupportedPlaftorms.Win7x64,
        "Virtual Windows 10 x86": SupportedPlaftorms.Win10x64,
        "Virtual Windows 10 x64": SupportedPlaftorms.Win10x64,
        "Windows 7 x86": SupportedPlaftorms.Win7x32,
        "Windows 7": SupportedPlaftorms.Win7x64,
        "Windows 10": SupportedPlaftorms.Win10x64,
        "Virtual Windows": SupportedPlaftorms.DefaultWin,
        "Virtual Windows 10": SupportedPlaftorms.Win10x64,
        "Virtual Windows 7": SupportedPlaftorms.Win7x64,
        "Physical Windows 7": SupportedPlaftorms.Win7x64,
        "Physical Windows 10": SupportedPlaftorms.Win10x64,
        "Physical Windows": SupportedPlaftorms.DefaultWin,
        "Windows": SupportedPlaftorms.DefaultWin,
        "Windows 8.1 x86": None,
        "Physical Windows 7 x86": SupportedPlaftorms.Win7x32,
        "Physical Windows 7 x64": SupportedPlaftorms.Win7x64,
        "Physical Windows 10 x64": SupportedPlaftorms.Win10x64,

        # macos
        "Mac 10.14": SupportedPlaftorms.MacOS_10_14,
        "Physical Mac 10.14": SupportedPlaftorms.MacOS_10_14,
        "mac": SupportedPlaftorms.DefaultMac,
        "Mac": SupportedPlaftorms.DefaultMac,
        "Virtual Mac": SupportedPlaftorms.DefaultMac,
        "Physical Mac": SupportedPlaftorms.DefaultMac,
        "Mac 10.15": SupportedPlaftorms.DefaultMac,
        "Mac 11.x": SupportedPlaftorms.DefaultMac,

        # android example
        "apad": SupportedPlaftorms.APad,
        "aphone": SupportedPlaftorms.APhone,
        "Android 9.x.x Smart": SupportedPlaftorms.APhone,
        "Android Pad >= 5.x.x": SupportedPlaftorms.APad,
        "iphone": SupportedPlaftorms.IPhone,
        "ipad": None,
    }

    @classmethod
    def get_autotest_platform(cls, testrun_environment):
        platform = cls.testrun_environments.get(testrun_environment)
        if platform is None:
            if re.match(re.compile(r"Android Pad", re.IGNORECASE), testrun_environment):
                platform = cls.testrun_environments["apad"]
            elif re.match(re.compile(r"Android", re.IGNORECASE), testrun_environment):
                platform = cls.testrun_environments["aphone"]
            elif re.match(re.compile("ipad.*|ios.*pad.*", re.IGNORECASE), testrun_environment):
                platform = cls.testrun_environments["ipad"]
            elif re.match(re.compile("iphone.*|ios.*", re.IGNORECASE), testrun_environment):
                platform = cls.testrun_environments["iphone"]
        return platform

    @classmethod
    def get_allure_platform_name(cls, testrun_environment):
        platform = cls.get_autotest_platform(testrun_environment)
        if platform is not None:
            return platform.value.get("allure_name")
        return None

    @classmethod
    def get_testpalm_platforms(cls, testrun_environment):
        platform = cls.get_autotest_platform(testrun_environment)
        if platform is None:
            return []
        return platform.value["testpalm_automation_os_marks"]

    @classmethod
    def get_binary_config_platform_data(cls, config_file_name):
        # TODO: временое отключение для https://st.yandex-team.ru/BYIN-12433#6066f5c32e469c397d910d69
        if config_file_name in ["win_7_x32.json", "win_8_x64.json"]:
            return None

        platform = None
        for _platform in SupportedPlaftorms:
            if _platform.value.get("isolate_config_name") == config_file_name:
                platform = _platform
                break
        if platform is None:
            return None
        return platform.value["allure_name"], platform.value["node_label"]

    @classmethod
    @sandbox.common.utils.singleton
    def get_isolates_artifact_name(cls, testrun_environment):
        platform = cls.get_autotest_platform(testrun_environment)
        if platform is None:
            return None
        return platform.value.get('isolate_config_name')
