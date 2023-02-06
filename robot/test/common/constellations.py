#!/usr/bin/env python

import copy
import logging

from robot.jupiter.test.common.table_wrappers import TableSetBuffer
from robot.jupiter.protos.compatibility import urldat_pb2
from robot.jupiter.protos import duplicates_pb2
from robot.jupiter.protos.external import host_mirror_pb2
from robot.jupiter.protos import gemini_pb2
from robot.jupiter.protos import externaldat_pb2

CURRENT_STATE = "20170709-100351"
BUCKETS_COUNT = 2

DEFAULT_LANGUAGE = 1


class ConstellationsException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super(ConstellationsException, self).__init__()


class InputData(TableSetBuffer):
    def __init__(self):
        TableSetBuffer.__init__(self)
        self._add_table(
            "Urldat",
            "//home/jupiter/urldat/{}/[bucket]/data".format(CURRENT_STATE),
            urldat_pb2.TUrldat,
            base_buckets_count=BUCKETS_COUNT)
        self._add_table(
            "HostMirror",
            "//home/jupiter/delivery_snapshot/{}/HostMirrorCompound/HostMirror".format(CURRENT_STATE),
            host_mirror_pb2.THostMirror)
        self._add_table(
            "BeautyHostNames",
            "//home/jupiter/delivery_snapshot/{}/BeautyHostNamesProto/BeautyHostNamesProto".format(CURRENT_STATE),
            gemini_pb2.TBeautyHostNameData)

        self._add_delivery_table("UserBrowse", "UserBrowseIndexAnn")
        self._add_delivery_table("UserBrowse", "UserBrowseQueryUrlUserData")
        self._add_delivery_table("UserBrowse", "UserBrowseStaticUserData")
        self._add_delivery_table("MiscData", "MiscDataIndexAnn")
        self._add_delivery_table("MiscData", "MiscDataQueryUrlUserData")
        self._add_delivery_table("MiscData", "MiscDataStaticUserData")
        self._add_delivery_table("UserCountersStaticUserData", "UserCountersStaticUserData")
        for shard in range(17):
            self._add_delivery_table("JupiterLemurPreparat", "{:02}".format(shard))

    def _add_delivery_table(self, directory, table, sharded=False):
        self._add_table(
            "{}_{}".format(directory, table),
            "//home/jupiter/delivery_snapshot/{}/{}/{}".format(CURRENT_STATE, directory, table),
            externaldat_pb2.TExternalUrldat)

    def add_urldat(self, **kwargs):
        self.Urldat.add(**kwargs)

    def add_beauty_host(self, host, beauty_host):
        self.BeautyHostNames.add(Host=host, BeautyHost=beauty_host)

    def add_factors(self, host, path, weight):
        self.UserBrowse_UserBrowseIndexAnn.add(Host=host, Path=path, Weight=weight)

    def log_urldat(self):
        logging.debug("------------ Urldat ------------ ")
        for u in sorted(self.Urldat.itervalues(), key=lambda u: (u.Host, u.Path)):
            logging.debug("%s%s | %d", u.Host, u.Path, u.HttpCode)
        logging.debug("------------ ****** ------------ ")


class OutputData(TableSetBuffer):
    def __init__(self, duplicates_path_template="//home/jupiter/constellations/{}/duplicates"):
        TableSetBuffer.__init__(self)
        self._add_table(
            "Duplicates",
            duplicates_path_template.format(state=CURRENT_STATE),
            duplicates_pb2.TDuplicateInfo)

    def log_duplicates(self):
        logging.info("------------ Duplicates ------------ ")
        for dup in sorted(self.Duplicates.itervalues(), key=lambda u: (u.Host, u.Path)):
            logging.info("%s%s -> %s%s | %s", dup.Host, dup.Path, dup.MainHost, dup.MainPath, dup.BeautyUrl)
        logging.info("------------ ********** ------------ ")


class InputDataBuilder(object):
    def __init__(self, input_tables):
        self.input_tables = input_tables
        self.urls = []
        self.beauty_hosts = {}
        self.checks = []

    def check_custom_group(self, main_host, main_path, beauty_host, beauty_path, others, desc):
        beauty_url = self.beauty_hosts.get(beauty_host, beauty_host) + beauty_path

        def check(output_tables):
            ok = True
            for key_prefix in others + [(main_host, main_path)]:
                key = (key_prefix[0], key_prefix[1])
                if key not in output_tables.Duplicates:
                    logging.error("No %s%s in duplicates table", key[0], key[1])
                    ok = False
                    continue
                dup = output_tables.Duplicates[key]
                if dup.MainHost != main_host or dup.MainPath != main_path:
                    logging.error(
                        "Main %s%s != %s%s for %s%s",
                        dup.MainHost,
                        dup.MainPath,
                        main_host,
                        main_path,
                        dup.Host,
                        dup.Path)
                    ok = False
                if dup.BeautyUrl != beauty_url:
                    logging.error("Beauty %s != %s for %s%s", dup.BeautyUrl, beauty_url, dup.Host, dup.Path)
                    ok = False
            if not ok:
                raise ConstellationsException("Failed checks: " + desc)
            else:
                logging.info("Good: %s", desc)

        self.checks.append(check)
        return self

    def check_no_url(self, host, path, desc):
        def check(output_tables):
            if (host, path) in output_tables.Duplicates:
                raise ConstellationsException("{}{} should not exist in duplicates: {}".format(host, path, desc))
            else:
                logging.info("Good: %s", desc)

        self.checks.append(check)
        return self

    def check_whole_group(self, main_host, main_path, beauty_host, beauty_path, desc):
        group = [(host, path) for (host, path) in self.urls if not (host == main_host and path == main_path)]
        return self.check_custom_group(main_host, main_path, beauty_host, beauty_path, group, desc)

    def get_checks(self):
        return self.checks

    def with_beauty_host(self, host, beauty_host):
        self.beauty_hosts[host] = beauty_host
        self.input_tables.add_beauty_host(host, beauty_host)
        return self

    def with_factors(self, host, path, weight=1):
        self.input_tables.add_factors(host, path, weight)
        return self

    def add_url(self, host, path, **kwargs):
        kwargs_copy = copy.deepcopy(kwargs)
        kwargs_copy["Host"] = host
        kwargs_copy["Path"] = path
        kwargs_copy["CanonizedPath"] = path
        if "RedirTarget" in kwargs_copy:
            kwargs_copy["CanonizedRedirTarget"] = kwargs_copy.get("CanonizedRedirTarget", kwargs_copy["RedirTarget"])

        self.input_tables.add_urldat(**kwargs_copy)
        self.urls.append((kwargs_copy['Host'], kwargs_copy['Path']))
        return self

    def add_content_url(self, host, path, simhash, **kwargs):
        kwargs_copy = copy.deepcopy(kwargs)
        kwargs_copy["HttpCode"] = kwargs_copy.get("HttpCode", 200)
        kwargs_copy["Language"] = kwargs_copy.get("Language", DEFAULT_LANGUAGE)
        kwargs_copy["HasContent"] = kwargs_copy.get("HasContent", True)
        kwargs_copy["Simhash"] = simhash
        kwargs_copy["SimhashDocLength"] = kwargs_copy.get("SimhashDocLength", kwargs_copy["Simhash"] & 0xffff)
        kwargs_copy["TitleHash"] = kwargs_copy.get("TitleHash", 0)
        return self.add_url(host, path, **kwargs_copy)

    def add_nocontent_url(self, host, path, **kwargs):
        kwargs_copy = copy.deepcopy(kwargs)
        kwargs_copy["HasContent"] = False
        return self.add_url(host, path, **kwargs)

    def add_redirect(self, host, path, redir_target, HttpCode=301):
        return self.add_nocontent_url(host, path, RedirTarget=redir_target, HttpCode=HttpCode, IsRedirect=True)

    def clear_urls(self):
        self.urls = []
        return self


def add_test_empty_esc_fragment_1(input_tables):
    host = "http://empty-esc-fragment1.ru"

    return InputDataBuilder(input_tables) \
        .with_beauty_host(host, "http://EmPtY-EsC-FrAgMeNt1.ru") \
 \
        .add_content_url(host, "/", 0xff, RelCanonicalTarget="{}/?_escaped_fragment_=".format(host)) \
        .add_content_url(host, "/?_escaped_fragment_=", 0xff0) \
        .check_whole_group(host, "/?_escaped_fragment_=", host, "/",
                           "Prefer content from url with empty escaped fragment, " +
                           "BeautyUrl should be without it. SimHash distance = 8.") \
        .clear_urls() \
 \
        .add_content_url(host, "/abc/def/", 0xff) \
        .check_whole_group(host, "/abc/def/", host, "/abc/def/",
                           "BUG: ? should be in the same group with morda (they have same simhash)") \
        .clear_urls() \
 \
        .add_content_url(host, "/ooo/zzz/", 0xff0000) \
        .check_whole_group(host, "/ooo/zzz/", host, "/ooo/zzz/",
                           "Should be self-main (different SimHash)") \
        .clear_urls() \
 \
        .add_content_url(
        host, "/more/check/", 0xff000000, RelCanonicalTarget="{}/more/check/?_escaped_fragment_=".format(host)) \
        .add_content_url(host, "/more/check/?_escaped_fragment_=", 0xff000000) \
        .check_whole_group(host, "/more/check/?_escaped_fragment_=", host, "/more/check/",
                           "Prefer content from url with empty escaped fragment, " +
                           "BeautyUrl should be without it. SimHashes are the same.") \
        .clear_urls() \
 \
        .add_content_url(host, "/without/relcanonical/", 0x12345678) \
        .add_content_url(
        host, "/without/relcanonical/?_escaped_fragment_=", 0x87654321) \
        .check_whole_group(host, "/without/relcanonical/", host, "/without/relcanonical/",
                           "BUG: when RelCanonicalTarget is not provided to url with _escaped_fragment, " +
                           "its' not selected as main") \
        .clear_urls() \
 \
        .add_redirect(host, "/redirtest/", "{}/redirtest/nexthop".format(host)) \
        .add_content_url(
        host,
        "/redirtest/nexthop",
        0xffff,
        HasContent=False,
        RelCanonicalTarget="{}/redirtest/nexthop?_escaped_fragment_=".format(host)) \
        .check_whole_group(host, "/redirtest/nexthop", host, "/redirtest/nexthop",
                           "BUG: /redirtest/nexthop and /redirtest/nexthop/ should be in one group") \
        .clear_urls() \
        .add_content_url(
        host,
        "/redirtest/nexthop/",
        0xffff,
        RelCanonicalTarget="{}/redirtest/nexthop/?_escaped_fragment_=".format(host)) \
        .add_content_url(
        host, "/redirtest/nexthop/?_escaped_fragment_=", 0xf000ffff) \
        .check_whole_group(host, "/redirtest/nexthop/?_escaped_fragment_=", host, "/redirtest/nexthop/",
                           "BUG: /redirtest/nexthop and /redirtest/nexthop/ should be in one group, " +
                           "Main should have_escaped_fragment_, but BeautyUrl should not.") \
        .get_checks()


def add_test_redirect_chains(input_tables):
    host = "http://redirect-chains.com"

    return InputDataBuilder(input_tables) \
        .add_redirect(host, "/", "{}/hop1".format(host)) \
        .add_redirect(host, "/hop1", "{}/hop1/hop2".format(host)) \
        .add_redirect(host, "/hop1/hop2", "{}/hop3".format(host)) \
        .add_content_url(host, "/hop3", 0x123) \
        .check_whole_group(host, "/hop3", host, "/",
                           "Content url must be main, beauty must be morda") \
        .get_checks()


def add_test_beauty_urls_two_hosts(input_tables):
    host = "http://beauty-urls-two-hosts.com"
    main_host = "https://www.beauty-urls-two-hosts.com"

    return InputDataBuilder(input_tables) \
        .add_redirect(host, "/", "{}/".format(main_host)) \
        .check_whole_group(host, "/", host, "/",
                           "BUG: Looks like they should be clayed, but there is fake redirect") \
        .clear_urls() \
        .add_redirect(main_host, "/backward", "{}/backward".format(host)) \
        .check_whole_group(main_host, "/backward", main_host, "/backward",
                           "BUG: backward redirect should work as well but its fake") \
        .clear_urls() \
        .add_content_url(host, "/backward", 0xff0000) \
        .add_content_url(host, "/test/content/longer", 0xff0000) \
        .check_whole_group(host, "/backward", host, "/backward",
                           "Inner content dups should be glued") \
        .clear_urls() \
        .add_content_url(main_host, "/test/content/longer", 0xff0000) \
        .check_whole_group(main_host, "/test/content/longer", main_host, "/test/content/longer",
                           "Cross-host content dups should not be glued") \
        .clear_urls() \
        .add_content_url(
        host,
        "/test/content/relcanonical",
        0xff777777,
        RelCanonicalTarget="{}/test/content/relcanonical/target".format(host)) \
        .add_content_url(host, "/test/content/relcanonical/target", 0xffffffff) \
        .check_whole_group(
        host,
        "/test/content/relcanonical/target",
        host,
        "/test/content/relcanonical/target",
        "RelCanonicalTarget should be main and beauty") \
        .clear_urls() \
        .add_content_url(
        main_host,
        "/test/content/relcanonical",
        0xff777777,
        RelCanonicalTarget="{}/test/content/relcanonical/target".format(host)) \
        .check_whole_group(main_host, "/test/content/relcanonical", main_host, "/test/content/relcanonical",
                           "Cross-host relcanonical dups should not be glued") \
        .get_checks()


def add_test_404(input_tables):
    host = "http://test-404.com"
    return InputDataBuilder(input_tables) \
        .add_redirect(host, "/404/redirect", "{}/404/redirect/target".format(host), HttpCode=404) \
        .check_no_url(host, "/404/redirect", "404 should be filtered out") \
        .clear_urls() \
        .add_content_url(host, "/404/redirect/target", 0x123) \
        .check_whole_group(
        host,
        "/404/redirect/target",
        host,
        "/404/redirect/target",
        "404 should not be in duplicates at all even if it is redirect (JUPITER-668)") \
        .clear_urls() \
 \
        .add_nocontent_url(host, "/404/absent", HttpCode=404) \
        .check_no_url(host, "/404/absent", "404 should be filtered out") \
        .get_checks()


def add_test_banned(input_tables):
    host = "http://test-banned.com"
    return InputDataBuilder(input_tables) \
        .add_content_url(host, "/noindex", 0x123, HttpCode=2005, HasContent=False) \
        .check_whole_group(
        host, "/noindex", host, "/noindex", "NoIndex should be treated same was as banned by robots (fake)") \
        .clear_urls() \
        .add_content_url(host, "/better/longer/content", 0x123) \
        .check_whole_group(
        host,
        "/better/longer/content",
        host,
        "/better/longer/content",
        "Noindex should not be included into group (JUPITER-592)") \
        .clear_urls() \
 \
        .add_content_url(host, "/banned", 0x123000, UrlIsBannedByRobotTxt=True) \
        .check_whole_group(host, "/banned", host, "/banned", "Banned url should not be in group") \
        .clear_urls() \
        .add_content_url(host, "/another/longer/content", 0x123000) \
        .check_whole_group(
        host, "/another/longer/content", host, "/another/longer/content", "Banned url should not be in group") \
        .get_checks()


def add_test_relcanonical_simhash_distance(input_tables):
    host = "http://relcanonial-simhash-distance.com"

    return InputDataBuilder(input_tables) \
        .add_content_url(
        host,
        "/test/content/relcanonical",
        0xffff0000,
        RelCanonicalTarget="{}/test/content/relcanonical/target".format(host)) \
        .check_whole_group(
        host,
        "/test/content/relcanonical",
        host,
        "/test/content/relcanonical",
        "Too big Simhash distance") \
        .clear_urls() \
        .add_content_url(host, "/test/content/relcanonical/target", 0x0000ffff) \
        .check_whole_group(
        host,
        "/test/content/relcanonical/target",
        host,
        "/test/content/relcanonical/target",
        "Too big Simhash distance") \
        .clear_urls() \
        .add_content_url(
        host,
        "/test/content/relcanonical_true",
        0xdcba0000,
        RelCanonicalTarget="{}/test/content/relcanonical/target_true".format(host)) \
        .add_content_url(host, "/test/content/relcanonical/target_true", 0xdcba03ff) \
        .check_whole_group(
        host,
        "/test/content/relcanonical/target_true",
        host,
        "/test/content/relcanonical/target_true",
        "Must be together, Simhash distance = 10 (max)") \
        .clear_urls() \
        .add_content_url(
        host,
        "/fail",
        0xf0f0f0f0,
        RelCanonicalTarget="{}/incorrect_url".format(host)) \
        .add_content_url(
        host,
        "/fail2",
        0xf0f0f0f0,
        RelCanonicalTarget="{}/incorrect_url2".format(host)) \
        .check_whole_group(
        host,
        "/fail",
        host,
        "/fail",
        "Must be together if incorrect relcanonical and same simhash") \
        .clear_urls() \
        .add_content_url(
        host,
        "/fail3",
        0x70707070,
        RelCanonicalTarget="{}/correct".format(host)) \
        .add_content_url(
        host,
        "/fail_fourth",
        0x70707070,
        RelCanonicalTarget="{}/correct".format(host)) \
        .check_whole_group(
        host,
        "/fail3",
        host,
        "/fail3",
        "Must be together, too big Simhash distance with relcanonical target, same simhash with each other") \
        .clear_urls() \
        .add_content_url(
        host,
        "/correct",
        0x07070707) \
        .check_whole_group(
        host,
        "/correct",
        host,
        "/correct",
        "Must be alone, too big Simhash distance with relcanonical sources") \
        .get_checks()


def add_test_select_main_by_factors(input_tables):
    host = "http://select-main-by-factors.com"
    return InputDataBuilder(input_tables) \
        .add_content_url(host, "/page_1", 0x123) \
        .add_content_url(host, "/page_11", 0x123) \
        .with_factors(host, "/page_1") \
        .check_whole_group(
        host, "/page_1", host, "/page_1", "Url with factors must be selected as main") \
        .clear_urls() \
        .add_content_url(host, "/page_2", 0x456) \
        .add_content_url(host, "/page_22", 0x456) \
        .with_factors(host, "/page_22") \
        .check_whole_group(
        host, "/page_22", host, "/page_22", "Url with factors must be selected as main") \
        .clear_urls() \
        .add_content_url(host, "/page_3", 0x789) \
        .add_redirect(host, "/page_33", "{}/page_3".format(host)) \
        .with_factors(host, "/page_33") \
        .check_whole_group(
        host, "/page_3", host, "/page_3", "Url without content cannot be main") \
        .get_checks()


def add_tests(input_tables):
    checks = []
    checks.extend(add_test_empty_esc_fragment_1(input_tables))
    checks.extend(add_test_redirect_chains(input_tables))
    checks.extend(add_test_beauty_urls_two_hosts(input_tables))
    checks.extend(add_test_404(input_tables))
    checks.extend(add_test_banned(input_tables))
    checks.extend(add_test_relcanonical_simhash_distance(input_tables))
    checks.extend(add_test_select_main_by_factors(input_tables))
    return checks


def check_results(checks, output_data):
    passed = 0
    failed = 0
    for c in checks:
        try:
            c(output_data)
            passed += 1
        except ConstellationsException as e:
            logging.exception(e.msg)
            failed += 1

    logging.info("%s checks have passed", passed)

    assert failed == 0, "{} checks have failed".format(failed)
