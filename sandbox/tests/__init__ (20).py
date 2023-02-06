from __future__ import absolute_import, unicode_literals

import itertools as it

import pytest

from sandbox.common import platform
from sandbox.common.types import misc as ctm


class TestGetPlatformAlias(object):

    def test__empty_platform_alias(self):
        result = platform.get_platform_alias(None)
        assert result == ""

    @pytest.mark.parametrize(
        "platform_name, alias",
        [
            ("Darwin-13.4.0-x86_64-i386-64bit".lower(), "osx_10.9_mavericks"),
            ("Darwin-14.0.0-x86_64-i386-64bit".lower(), "osx_10.10_yosemite"),
            ("Linux.3.2.0-38-generic".lower(), "linux_ubuntu_12.04_precise"),
            ("FreeBSD.8.2-STABLE".lower(), "freebsd8"),
        ]
    )
    def test__platform_aliases(self, platform_name, alias):
        assert platform.get_platform_alias(platform_name) == alias

    @pytest.mark.parametrize(
        "platform_name, alias",
        [
            ("aarch64_trusty_linux", "linux_ubuntu_14.04_trusty_aarch64"),
            ("aarch64_strange_platform", "aarch64_strange_platform"),
            ("lucid_lynx", "linux_ubuntu_10.04_lucid"),
            ("precise_pangolin", "linux_ubuntu_12.04_precise"),
            ("trusty_tahr", "linux_ubuntu_14.04_trusty"),
            ("xenial_xerus", "linux_ubuntu_16.04_xenial"),
            ("bionic_beaver", "linux_ubuntu_18.04_bionic"),
            ("focal_fossa", "linux_ubuntu_20.04_focal"),
            ("rhel_santiago", "linux_rhel_santiago"),
            ("rhel", "linux_rhel"),
            ("cygwin_nt-6.1-wow64", "cygwin_6.1"),
        ]
    )
    def test__marginal_platform_aliases(self, platform_name, alias):
        assert platform.get_platform_alias(platform_name) == alias

    def test__unknown_platform_alias(self):
        result = platform.get_platform_alias("unknown_platform")
        assert result == "unknown_platform"


class TestComparePlatforms(object):

    def test__equal_platforms(self):
        result = platform.compare_platforms("Platform", "Platform")
        assert result is True

    def test__equal_aliases(self):
        result = platform.compare_platforms(
            "Linux.3.2.0-43-generic".lower(),
            "Linux-3.2.0-51-generic-x86_64-with-Ubuntu-12.04-precise".lower()
        )
        assert result is True

    def test__unequal_platforms(self):
        result = platform.compare_platforms(
            "Darwin-16.5.0-x86_64-i386-64bit".lower(),
            "Linux-3.2.0-51-generic-x86_64-with-Ubuntu-12.04-precise".lower()
        )
        assert result is False


class TestIsBinaryCompatible(object):

    def test__compatible_platforms(self):
        result = platform.is_binary_compatible(
            "Linux.3.2.0-43-generic".lower(),
            "Linux-3.2.0-51-generic-x86_64-with-Ubuntu-12.04-precise".lower()
        )
        assert result is True

    def test__equal_platforms_different_versions(self):
        result = platform.is_binary_compatible(
            "Darwin-14.0.0-x86_64-i386-64bit".lower(),
            "Darwin-17.4.0-x86_64-i386-64bit".lower()
        )
        assert result is True

    def test__unknown_platforms(self):
        result = platform.is_binary_compatible(
            "unknown_platform_1",
            "unknown_platform_2"
        )
        assert result is None


class TestGetArchFromPlatform(object):

    def test__empty_platform(self):
        result = platform.get_arch_from_platform(None)
        assert result == ctm.OSFamily.ANY

    def test__arch_platform(self):
        result = platform.get_arch_from_platform("osx")
        assert result == "osx"

        result = platform.get_arch_from_platform("cygwin")
        assert result == "cygwin"

    def test__linux_arm_platform(self):
        result = platform.get_arch_from_platform("linux_ubuntu_14.04_trusty_aarch64")
        assert result == "linux_arm"

    @pytest.mark.parametrize(
        "platform_name, arch",
        [
            ("FreeBSD.9.0-STABLE".lower(), "freebsd"),
            ("Linux.2.6.32-42-server".lower(), "linux"),
            ("Darwin-13.4.0-x86_64-i386-64bit".lower(), "osx"),
            ("cygwin_nt-6.1-wow64", "cygwin"),
            ("win_nt-platform", "win_nt"),
        ]
    )
    def test__all_platforms(self, platform_name, arch):
        assert platform.get_arch_from_platform(platform_name) == arch

    def test__unknown_platform(self):
        with pytest.raises(ValueError):
            platform.get_arch_from_platform("unknown-platform")


class TestPlatform(object):
    LUCID_PLATFORM_ALIAS = "linux_ubuntu_10.04_lucid"
    LUCID_PLATFORMS = platform.PLATFORM_ALIASES[LUCID_PLATFORM_ALIAS]

    PRECISE_PLATFORM_ALIAS = "linux_ubuntu_12.04_precise"
    PRECISE_PLATFORMS = platform.PLATFORM_ALIASES[PRECISE_PLATFORM_ALIAS]

    FREEBSD8_ALIAS = "freebsd8"
    FREEBSD8_PLATFFORMS = platform.PLATFORM_ALIASES[FREEBSD8_ALIAS]

    FREEBSD9_ALIAS = "freebsd9"
    FREEBSD9_PLATFFORMS = platform.PLATFORM_ALIASES[FREEBSD9_ALIAS]

    def test__alias_naming(self):
        """
            Check linux platform aliases
        """
        for lucid_platfrom in self.LUCID_PLATFORMS:
            assert platform.get_platform_alias(lucid_platfrom) == self.LUCID_PLATFORM_ALIAS
            assert platform.get_platform_alias(lucid_platfrom.lower()) == self.LUCID_PLATFORM_ALIAS

        for precise_platfrom in self.PRECISE_PLATFORMS:
            assert platform.get_platform_alias(precise_platfrom) == self.PRECISE_PLATFORM_ALIAS
            assert platform.get_platform_alias(precise_platfrom.lower()) == self.PRECISE_PLATFORM_ALIAS
            assert platform.compare_platforms(precise_platfrom, self.PRECISE_PLATFORM_ALIAS)

        for freebsd8_platform in self.FREEBSD8_PLATFFORMS:
            assert platform.get_platform_alias(freebsd8_platform), self.FREEBSD8_ALIAS
            assert platform.get_platform_alias(freebsd8_platform.lower()) == self.FREEBSD8_ALIAS
            assert platform.compare_platforms(freebsd8_platform, self.FREEBSD8_ALIAS)

        for freebsd9_platform in self.FREEBSD9_PLATFFORMS:
            assert platform.get_platform_alias(freebsd9_platform) == self.FREEBSD9_ALIAS
            assert platform.get_platform_alias(freebsd9_platform.lower()) == self.FREEBSD9_ALIAS
            assert platform.compare_platforms(freebsd9_platform, self.FREEBSD9_ALIAS)

    def test__compare_platforms(self):
        """
            Check platform compare method
        """
        for platfroms_list in [
            self.LUCID_PLATFORMS, self.PRECISE_PLATFORMS, self.FREEBSD9_PLATFFORMS, self.FREEBSD8_PLATFFORMS,
        ]:
            for platfrom_one, platform_two in it.combinations_with_replacement(platfroms_list, 2):
                assert platform.compare_platforms(platfrom_one, platform_two)

        def check_for_another_platforms(platforms, another_platforms, alias, another_aliases):
            for pl in platforms:
                assert platform.compare_platforms(pl, alias)
                for another_alias in another_aliases:
                    assert not platform.compare_platforms(pl, another_alias)
                for another_platform in another_platforms:
                    assert not platform.compare_platforms(pl, another_platform)

        check_for_another_platforms(
            self.LUCID_PLATFORMS,
            self.PRECISE_PLATFORMS + self.FREEBSD9_PLATFFORMS + self.FREEBSD8_PLATFFORMS,
            self.LUCID_PLATFORM_ALIAS,
            [self.PRECISE_PLATFORM_ALIAS, self.FREEBSD8_ALIAS, self.FREEBSD9_ALIAS])

        check_for_another_platforms(
            self.PRECISE_PLATFORMS,
            self.LUCID_PLATFORMS + self.FREEBSD9_PLATFFORMS + self.FREEBSD8_PLATFFORMS,
            self.PRECISE_PLATFORM_ALIAS,
            [self.LUCID_PLATFORM_ALIAS, self.FREEBSD8_ALIAS, self.FREEBSD9_ALIAS])

        check_for_another_platforms(
            self.FREEBSD9_PLATFFORMS,
            self.LUCID_PLATFORMS + self.PRECISE_PLATFORMS + self.FREEBSD8_PLATFFORMS,
            self.FREEBSD9_ALIAS,
            [self.LUCID_PLATFORM_ALIAS, self.FREEBSD8_ALIAS, self.PRECISE_PLATFORM_ALIAS])

        check_for_another_platforms(
            self.FREEBSD8_PLATFFORMS,
            self.LUCID_PLATFORMS + self.PRECISE_PLATFORMS + self.FREEBSD9_PLATFFORMS,
            self.FREEBSD8_ALIAS,
            [self.LUCID_PLATFORM_ALIAS, self.FREEBSD9_ALIAS, self.PRECISE_PLATFORM_ALIAS])
