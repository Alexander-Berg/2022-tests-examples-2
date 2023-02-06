# -*- coding: utf-8 -*-

import six
import time
import json
import codecs
import random
import logging
import datetime
from xml import etree
from urlparse import urlparse

import sandbox.projects.release_machine.tasks.base_task as rm_bt
import sandbox.projects.release_machine.core.task_env as task_env
import sandbox.projects.release_machine.core.const as rm_const
import sandbox.projects.release_machine.helpers.startrek_helper as st_helper
import sandbox.projects.release_machine.components.all as rmc

from sandbox.projects import resource_types
from sandbox.projects.common import binary_task
from sandbox.projects.common import decorators
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import requests_wrapper
from sandbox.projects.common import utils2
from sandbox.projects.common.betas.beta_api import BetaApi
from sandbox.projects.common.search import bugbanner
from sandbox.projects.common.search.response import cgi
from sandbox.projects.release_machine import input_params2 as rm_params2
from sandbox.projects.release_machine import yappy as yappy_helper
from sandbox.projects.websearch.TestXmlSearch2 import const as txs_const
from sandbox.projects.websearch.TestXmlSearch2 import util as txs_util
from sandbox import sdk2


class TestXmlSearch2(rm_bt.BaseReleaseMachineTask):
    """
    Testing XML search. Inspired by production incidents:
    * SEARCHPRODINCIDENTS-1275
    * SEARCHPRODINCIDENTS-1783
    * SEARCHPRODINCIDENTS-2622
    * SEARCHPRODINCIDENTS-3547
    * SPINCIDENTS-841
    * SEARCH-6388
    XML search is used by Rambler Co, so it should be online.
    """

    class Requirements(task_env.StartrekRequirements):
        disk_space = 1024

    class Parameters(rm_params2.DefaultReleaseMachineParameters):
        _lbrp = binary_task.binary_release_parameters(none=True)

        beta_url = sdk2.parameters.String("Web beta URL", required=True)
        images_beta_url = sdk2.parameters.String("Images beta URL", required=False)
        video_beta_url = sdk2.parameters.String("Video beta URL", required=False)

        queries_plan = sdk2.parameters.Resource(
            "Plan for shooting",
            resource_type=resource_types.USERS_QUERIES,
            required=True,
        )
        shoots_number = sdk2.parameters.Integer(
            "Shoots number",
            default=500,
            required=True,
        )
        diff_barrier = sdk2.parameters.Float(
            "Allowed difference between JSON and XML (summary)",
            default=0.5,
            required=True,
        )

        test_video_vtop = sdk2.parameters.Bool("Test Video Top (vtop=1), see SEARCH-6388", default=False)
        add_cgi = sdk2.parameters.String("Add CGI parameters (e.g. '&test-id=62534')", default='&numdoc=10')

        add_xml_only_cgi = sdk2.parameters.String(
            "Add CGI parameters (e.g. '&test-id=62534') only for xml requests",
            default='')

        add_headers = sdk2.parameters.Dict("Add HTTP headers to request (e.g. 'X-Yandex-Internal-Request: 1')",
                                           default={}, required=False)
        timeout = sdk2.parameters.Integer("Timeout (us)", default=0)

        with sdk2.parameters.CheckGroup("Search subtypes") as search_subtypes:
            search_subtypes.values.web = 'web'
            search_subtypes.values.video = 'video'
            search_subtypes.values.images = 'images'

        validate_beta = sdk2.parameters.Bool("Validate beta before launch", default=False)

        release_number = rm_params2.release_number

        with sdk2.parameters.Output():
            xml_search_report_resource = sdk2.parameters.Resource(
                "Difference between XML and JSON",
                resource_type=resource_types.XML_SEARCH_DIFF,
            )

    class Context(rm_bt.BaseReleaseMachineTask.Context):
        xml_search_report = None
        tests_failed = False

    def on_enqueue(self):
        super(TestXmlSearch2, self).on_enqueue()
        with self.memoize_stage.create_resource_on_enqueue:
            self.Parameters.xml_search_report_resource = resource_types.XML_SEARCH_DIFF(
                task=self,
                description="{} XML search report".format(
                    self.Parameters.component_name,
                ),
                path=txs_const.OUTPUT_NAME,
            )

    def on_execute(self):
        binary_task.LastBinaryTaskRelease.on_execute(self)
        rm_bt.BaseReleaseMachineTask.on_execute(self)

        self._wait_beta_spike()

        import urllib3

        self.add_bugbanner(
            bugbanner.Banners.SearchTests,
            add_responsibles=[
                "juver",
            ],
        )

        # shut up warnings, see https://nda.ya.ru/3TVSbq
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        report = {}
        release_num = self.Parameters.release_number or None
        component_name = self.Parameters.component_name or None
        c_info = None
        st = None

        if self.Parameters.validate_beta:
            api_token = sdk2.Vault.data(rm_const.COMMON_TOKEN_OWNER, rm_const.YAPPY_TOKEN_NAME)
            api = BetaApi.fromurl(token=api_token)
            for beta_url in (
                self.Parameters.beta_url,
                self.Parameters.video_beta_url,
                self.Parameters.images_beta_url,
            ):
                self._wait_for_beta_consistency(api, self.Parameters.beta_url)

        if release_num and component_name:
            st = st_helper.STHelper(sdk2.Vault.data(rm_const.COMMON_TOKEN_OWNER, rm_const.COMMON_TOKEN_NAME))
            c_info = rmc.get_component(component_name)
            st.write_grouped_comment(
                rm_const.TicketGroups.XMLTest,
                "",
                "Start XML test {}".format(lb.task_wiki_link(self.id)),
                release_num,
                c_info,
            )

        self.set_info("Test reqids (SERP-56675) [r=mvel]")
        self._check_reqids()

        rambler_key = sdk2.Vault.data(txs_const.RAMBLER_VAULT_KEY)

        self.set_info("Test turbo pages with key (SEARCH-7199) [r=lebedev-aa]")
        self._check_turbo_with_key(rambler_key)

        self.set_info("Test key and user (REPORTINFRA-126) [r=lebedev-aa]")
        self._check_key_and_user(rambler_key)

        self.set_info("Test Qloss.debug presence (FINDURL-23) [r=lebedev-aa]")
        self._check_qloss_debug()

        self.set_info("Testing JSON vs XML responses... [r=mvel]")
        self._check_json_vs_xml_diff(report)

        if self.Parameters.test_video_vtop:
            self.set_info("Test video top [r=mincer,nbahob]")
            self._check_video_top(report)
        else:
            self.set_info("VideoTop test disabled due to SEARCH-6388")

        self.set_info("Test XML doc count [r=mvel]")
        self._check_xml_doc_count()

        self.set_info("Test XML family search [r=lebedev-aa]")
        self._check_xml_family_search()

        self.set_info("Test XML flat groupings [r=mvel]")
        self._check_xml_flat_groupings()

        self.set_info("Test Sitesearch [r=lebedev-aa]")
        self._check_sitesearch()

        self.set_info("Test operators search [r=mvel]")
        self._check_operators()

        logging.info('Fill HTML report...')
        self._fill_report(report)
        logging.info('HTML report has been filled.')

        eh.ensure(not self.Context.tests_failed, "Some tests failed. ")
        if c_info:
            st.write_grouped_comment(
                rm_const.TicketGroups.XMLTest, "", "Xml test result: **!!(green)SUCCESS!!**", release_num, c_info
            )

        self.send_rm_proto_event()

    def on_finish(self, prev_status, status):
        super(TestXmlSearch2, self).on_finish(prev_status, status)
        self.Context.xml_search_report = self.Parameters.xml_search_report_resource.id
        self.Context.save()

    @staticmethod
    def _find_groups(xml_response):
        return xml_response.findall("./response/results/grouping/group")

    @staticmethod
    def _find_docs(xml_response):
        return [i.text for i in xml_response.findall('./response/results/grouping/group/doc/url')]

    @staticmethod
    def _to_string(xml):
        return etree.ElementTree.tostring(xml)

    def _wait_beta_spike(self):
        # This is a special spike for .hamster/.yappy betas
        # that are not working at all from 0AM till 6AM due to database switching
        # So we just need to wait some time until hamster restores its consistency.
        # This check may be removed when fullmesh on hamster will be eliminated.
        current_time = datetime.datetime.now()
        if 0 <= current_time.hour <= 6:
            raise sdk2.WaitTime(3000 + int(random.random() * 1200))

    def _wait_for_beta_consistency(self, api, beta_url):
        if not beta_url:
            logging.debug("No beta name passed, do nothing.")
            return
        parsed_beta_name = urlparse(beta_url)
        beta_name = parsed_beta_name.netloc.split(".")[0]
        self.set_info("Wait for {} beta consistency".format(beta_name))
        yappy_helper.wait_consistency(self, api, beta_name)

    def _check_reqids(self):
        """
        Tests SERP-56675: Every response should contain a reqid
        """
        queries = [
            # zero docs
            "&text=sadasdasdhdhdjdasdhahahahaasdadasdasdas",
            # nonzero docs, for rambler
            (
                "&text=test"
                "&user=rambler-xml"
                "&i-m-a-hacker=1"
            ),
        ]
        for query in queries:
            # do not disable exps, maybe we catch some trash
            xml_response, text_response = self._get_xml_parsed_response(query, no_tests=False, test_name="SERP-56675")
            if not xml_response:
                # when no valid XML response obtained, error was logged above
                return

            xml_reqid = self._get_reqid(xml_response, text_response)
            if not xml_reqid:
                self._set_error("Cannot detect reqid, SERP-56675 failed")

    def _get_xml_parsed_response(
        self,
        url,
        no_tests=True,
        headers=None,
        test_name=txs_const.UNSPECIFIED,
        check_reqid=True,
    ):
        """
        Returns parsed XML response
        :param url: CGI params, e.g. "text=qqq" or UrlCgiCustomizer object
        :param no_tests: disable experiments
        :param headers: pass custom headers
        :return: tuple of (parsed xml object, text content). Both can be None in case of errors
        """
        if not headers:
            headers = {}
        headers.update(self.Parameters.add_headers)

        if isinstance(url, six.string_types):
            url = cgi.UrlCgiCustomizer(
                base_url='{}/search/xml/'.format(self.Parameters.beta_url),
                params=url,
            )

        if no_tests:
            url.disable_experiments()

        url.add_custom_cgi_string(self._add_cgi())
        url.add_custom_cgi_string(self._add_xml_only_cgi())
        url.add_custom_param('reqinfo', 'sandbox-TEST_XML_SEARCH_2-task-{}'.format(self.id))

        logging.info("[xml] Requesting %s", url)

        text_response = None
        try:
            # retries inside
            text_response = txs_util.requests_get_r(url, headers=headers, raise_for_empty_response=True).content
        except Exception as exc:
            eh.log_exception("Failed requesting xmlsearch, empty or invalid response for url {}".format(url), exc)
            self._set_error(
                "XML search test `{test_name}` failed, got empty or invalid response. "
                "See logs for request url".format(test_name=test_name),
                exc,
            )
            return None, None

        # check xml response validity: in case of HTTP 200 OK, xmlsearch response MUST be well-formed XML
        try:
            xml_response = etree.ElementTree.fromstring(text_response)
        except etree.ElementTree.ParseError as err:
            eh.log_exception("[xml] Failed parsing response for url {}".format(url), err)
            logging.debug("Invalid XML response:\n====== BEGIN ===%s\n====== END ==", text_response)
            self._set_error("Invalid XML response in test `{test_name}`".format(test_name=test_name), err)
            return None, text_response

        reqid = self._get_reqid(xml_response, text_response)
        if check_reqid and not reqid:
            self._set_error("Got invalid or empty reqid for url %s", url)

        return xml_response, text_response

    def _check_turbo_with_key(self, key):
        query = (
            '&text=как%20проверить%20авто%20по%20vin'
            '&key={access_key}'
            '&user=rambler-xml'
            # '&i-m-a-hacker=81.19.0.0'  # TODO: uncomment
            '&rearr=XmlFilter_dbg'
            '&no-tests=1'
            # '&dump=eventlog'  # handled by http-adapter. Breaks XML
            '&rearr=xml_filter_debug=1'
        ).format(access_key=key)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/69.0.3497.100 Mobile Safari/537.36"
            ),
        }

        test_name = "SEARCH-7199"
        turbo_links = []

        for attempt in range(5):
            reqid, xml_docs, xml_response = self._get_xml_response(
                query,
                test_name=test_name,
                attempts=5,
                no_tests=True,
                headers=headers,
            )
            if xml_response is None:
                # failed to obtain xml response
                logging.error('No xml response for %s test', test_name)
                break

            logging.debug('TurboLink debug response:\n%s\n\n', self._to_string(xml_response))
            turbo_links = xml_response.findall("./response/results/grouping/group/doc/properties/TurboLink")
            if turbo_links:
                # we found them, okay
                break

        if not turbo_links:
            logging.error(
                "Not enough search results, turbo link test failed:\n%s",
                self._to_string(xml_response) if xml_response is not None else '',
            )
            self._set_error(
                "Not enough turbo links for query: `{}`, reqid: `{}`.".format(query, reqid),
                test_name=test_name,
            )

        # all links should contain some chars
        eh.ensure(
            all(t.text for t in turbo_links),
            "Empty turbo link for query: `{}`".format(query)
        )

    def _get_xml_response(
        self,
        url,
        test_name=txs_const.UNSPECIFIED,
        attempts=1,
        min_docs=3,
        no_tests=True,
        headers=None,
    ):
        """
        High-level xml response querying
        :param url: UrlCgiCustomizer object or query string (e.g. `&text=test`).
        :param test_name: test case name.
        :param attempts: attempt count for trying to obtain non-empty docs list
        :param min_docs: when doc count is less than `min_docs`
            we treat response as unanswer and retry it.
        :param no_tests: disable experiments
        :param headers: pass custom headers
        :return reqid, list of urls (documents), xml root
        """
        xml_response = None
        reqid = None
        xml_docs = None

        for attempt in range(attempts):
            xml_response, text_response = self._get_xml_parsed_response(
                url,
                test_name=test_name,
                no_tests=no_tests,
                headers=headers,
            )
            if xml_response is None:  # `if not` will not work, see the docs
                logging.error('[Attempt %s] No valid XML response available for `%s`', attempt, url)
                continue

            xml_docs = self._find_docs(xml_response)
            reqid = self._get_reqid(xml_response, text_response)

            if len(xml_docs) < min_docs:
                logging.error(
                    '[Attempt %s] XML unanswer detected (no docs), reqid: `%s`, url `%s`',
                    attempt, reqid, url,
                )
                continue

            # success
            logging.debug('[Attempt %s] XML reqid: `%s`, XML docs:\n%s\n\n', attempt, reqid, xml_docs)
            break

        return reqid, xml_docs, xml_response

    def _check_key_and_user(self, key):
        query = (
            "&text=asd"
            "&key={access_key}"
            "&user=rambler-xml"
        ).format(access_key=key)
        reqid, xml_docs, xml_response = self._get_xml_response(
            query,
            test_name="REPORTINFRA-126",
            attempts=5,
            min_docs=5,
        )
        self._check_response_group_count(query, reqid, xml_response, test_name="REPORTINFRA-126")

    def _check_response_group_count(self, query, reqid, xml_response, test_name):
        if xml_response is None:
            logging.error("[_check_response_group_count] Empty XML response")
            self._set_error(
                'Empty XML root in {test_name} for query `{query}`'.format(
                    test_name=test_name,
                    query=query,
                )
            )
            return

        all_groups = self._find_groups(xml_response)
        if len(all_groups) < 8:
            logging.error(
                "Not enough search results, test `%s` failed:\n%s",
                test_name, self._to_string(xml_response),
            )
            self._set_error(
                "Not enough search results in {test_name} test, "
                "should be at least 8 groups for query: `{query}`. ".format(
                    test_name=test_name,
                    query=query,
                )
            )

    def _check_qloss_debug(self):
        """
        Test for FindUrl, check that Qloss.debug exists in response
        :return:
        """
        test_params = [
            ("text", u"Yandex"),
            ("g", "1.d.10.1.-1.0.0.-1.rlv.0."),
            ("json_dump", txs_const.JSON_RDAT_REQID_KEY),
            ("json_dump", "search_props.WEB"),
            ("nocache", "da"),
            ("noreask", "1"),
            ("flag", "disable_mda"),
            ("pron", "doc_filtering_status_Z5D9F056F5E83334E"),
            ("timeout", "100000000"),
            ("no-tests", "1"),
            ("waitall", "da"),
        ]

        test_json_url = (
            cgi.UrlCgiCustomizer(base_url=u'{}/search/'.format(self.Parameters.beta_url))
            .add_region("213")
            .add_custom_params(test_params)
            .no_cookie_support()
        )
        test_json_url.add_custom_cgi_string(self._add_cgi())
        qloss_debug_detected = False
        json_response = None
        reqid = None
        for attempt in range(10):
            json_response, text_response = self._get_json_parsed_response(
                test_json_url,
                test_name="FINDURL-23",
                reqid_key=txs_const.JSON_RDAT_REQID_KEY,
            )
            if not json_response:
                return  # cannot proceed further parsing

            if json_response["search_props.WEB"][0]["properties"].get("QLoss.debug"):
                qloss_debug_detected = True
                break

            logging.error(
                'QLoss check failed, attempt #%s, response was:\n%s\n\n',
                attempt, json.dumps(json_response, indent=2),
            )
            reqid = json_response.get(txs_const.JSON_RDAT_REQID_KEY)
            time.sleep(5 + 5 * attempt)

        if not qloss_debug_detected:
            self._set_error("QLoss.debug field is empty, FINDURL-23 is broken (sample reqid: `{}`). ".format(reqid))

    @decorators.retries(max_tries=3, delay=10)
    def _check_sitesearch_case(self, s_case):
        s_case[txs_const.CHECK_FIELD] = txs_const.SEARCHDATA_DOCS
        test_json_url = (
            cgi.UrlCgiCustomizer(
                base_url=u'{}/search/site/'.format(self.Parameters.beta_url)
            ).add_region(
                "213",
            ).add_custom_params(
                s_case["params"],
            ).add_custom_param(
                'json_dump',
                txs_const.SEARCHDATA_DOCS,
            ).add_custom_param(
                'json_dump',
                txs_const.JSON_REQID_KEY,
            ).no_cookie_support()
        )
        test_json_url.add_custom_cgi_string(self._add_cgi())
        json_data, text_response = self._get_json_parsed_response(
            test_json_url,
            test_name='sitesearch',
            reqid_key=txs_const.JSON_REQID_KEY,
        )
        self._check_case(json_data, s_case, test_name="sitesearch", non_empty=True)

        # specific check for SEARCH-10126
        for doc in json_data[txs_const.SEARCHDATA_DOCS]:
            eh.ensure(
                doc['host'] == 'ru.wikipedia.org',
                'Sitesearch output contains docs not from requested site, see SEARCH-10126. '
            )

    def _check_json_vs_xml_diff(self, report):
        fail_counter = 0
        queries = self._get_queries()
        diff_barrier = self.Parameters.shoots_number * self.Parameters.diff_barrier
        logging.debug('Diff barrier for JSON vs XML is %s', diff_barrier)
        base_error_message = (
            u'XML search responses: {} of ' +
            '{} requests failed'.format(self.Parameters.shoots_number)
        )

        # do not handle images and video on zelo, it does not work
        search_subtypes = self.Parameters.search_subtypes
        logging.info("Search subtypes are %s", search_subtypes)
        search_types = ["web"] if 'zelo' in self.Parameters.beta_url else search_subtypes
        for search_type in search_types:

            if search_type == 'video':
                logging.info('Skipped diffing video json vs xml as xml does not exists for video (see SEARCH-9953)')
                continue

            logging.info("Processing search type `%s`, max fail count: `%s`", search_type, diff_barrier)
            response_diff, fail_count = self._get_response_diff(queries, search_type, diff_barrier)
            logging.debug('Response diff: %s', response_diff)
            if len(response_diff) > diff_barrier or fail_counter >= diff_barrier:
                logging.debug('Response diff length exceeded or too many errors. Diff will be added to report')
                message = base_error_message.format(len(response_diff))
                report[message] = response_diff
                break

    def _check_video_top(self, report):
        xml_reqid, xml_docs = 'None', []
        try:
            xml_reqid, xml_docs = self._get_video_top_xml_response()
        except Exception as exc:
            eh.log_exception("Something went wrong with video top, using default values", exc)

        problem = 'unanswer' if not xml_docs else None
        problem = txs_util.check_invalid_urls(xml_docs) if not problem else problem
        if problem:
            logging.error('There is an error (%s) during video top check', problem)
            error = {
                'even': 'even',
                'text': 'None',
                'region': 'None',
                'json_reqid': '',
                'json_docs': '',
                'xml_reqid': xml_reqid,
                'xml_docs': xml_docs,
                'problem': 'vtop ' + problem,
            }
            report['Video Top'] = [error]

    def _check_xml_doc_count(self):
        """
        Tests SEARCHPRODINCIDENTS-2622 (SEARCH-4425)
        """
        query = "&text=google"
        test_name = "SEARCH-4425"
        reqid, xml_docs, xml_response = self._get_xml_response(query, test_name=test_name, attempts=5)
        if not reqid:
            logging.error('[_check_xml_doc_count] Empty response after 5 attempts, test `%s`', test_name)
            self._set_error('Empty response after 5 attempts in xml doc count check', test_name=test_name)
            return

        self._check_response_group_count(query, reqid, xml_response, test_name=test_name)

    def _check_xml_family_search(self):
        """
        Tests SPI-4740 (SEARCH-8395)
        """
        test_name = "SEARCH-8395"
        query = "&query=host:pornhub.com+|+host:www.pornhub.com&l10n=ru&sortby=tm.order=ascending&filter=strict"
        reqid, xml_docs, xml_response = self._get_xml_response(
            query,
            test_name=test_name,
            attempts=5,
            min_docs=0,  # no docs here is not an error
        )
        if not reqid:
            logging.error('[_check_xml_family_search] Empty response after 5 attempts, test `%s`', test_name)
            self._set_error('Empty response after 5 attempts in xml family search check')
            return

        all_groups = self._find_groups(xml_response)
        if len(all_groups) > 0:  # do not use `if all_groups`, see lxml docs
            logging.error("Too many search results, %s test failed:\n%s", test_name, self._to_string(xml_response))
            self._set_error(
                "Too many search results in {test_name} test, "
                "there must not be any result for query: `{query}`. ".format(
                    test_name=test_name, query=query,
                )
            )

    def _check_xml_flat_groupings(self):
        """
        Tests SEARCHPRODINCIDENTS-3547 (SEARCH-6978)
        """
        test_name = "SEARCH-6978"
        grouping = "&groupby=attr%3D%22%22.mode%3Dflat.groups-on-page%3D10.docs-in-group%3D1"
        sorting = "&sortby=tm.order%3Dascending"
        query_cgi = "&query=a"
        filtering = "&filter=strict"
        queries = [
            query_cgi + grouping + sorting,
            query_cgi + grouping,
            query_cgi + filtering,
        ]
        for query in queries:
            reqid, xml_docs, xml_response = self._get_xml_response(query, test_name=test_name, attempts=5)
            if not reqid:
                logging.error('[_check_xml_flat_groupings] Empty response after 5 attempts, test `%s`', test_name)
                self._set_error('[_check_xml_flat_groupings] Empty response after 5 attempts')
                continue

            self._check_response_group_count(query, reqid, xml_response, test_name=test_name)

    def _check_sitesearch(self):
        """
        Test for SEARCHPRODINCIDENTS-2076 (SEARCH-3216)
        """
        sitesearch_test_cases = [
            {
                "params": [
                    ("text", u"закон"),
                    ("searchid", '3971490'),
                    ("web", "0"),  # непонятно, за что отвечает этот параметр
                    ("l10n", "ru"),
                ],
                "st_issue": 'SEARCH-3216 SEARCH-9548',
            },
            {
                "params": [
                    ("text", u"техстрой"),
                    ("searchid", "3971490"),
                ],
                "st_issue": "SEARCH-5910 SEARCH-6964 SEARCH-9548",
            },
        ]
        for s_case in sitesearch_test_cases:
            try:
                self._check_sitesearch_case(s_case)
            except Exception as exc:
                self._set_error(
                    'Sitesearch is broken. {st_issue} is broken. '.format(
                        st_issue=s_case["st_issue"],
                    ),
                    exc=exc,
                )

    def _check_operators(self):
        """
        Test for site: and url: operators (SEARCH-6581, SEARCH-9548)
        """
        operators_test_cases = [
            {
                "params": [
                    ("text", "site:yandex.ru"),
                ],
            },
            {
                "params": [
                    ("text", "url:yandex.ru"),
                ],
            },
        ]
        for s_case in operators_test_cases:
            try:
                s_case['st_issue'] = 'SEARCH-6581, SEARCH-8697, SEARCH-9546, SEARCH-9548'
                self._check_operators_case(s_case)
            except Exception as exc:
                self._set_error(
                    'Operators are broken. {st_issue} is broken. '.format(
                        st_issue=s_case["st_issue"],
                    ),
                    exc=exc,
                )

    @decorators.retries(max_tries=3, delay=10)
    def _check_operators_case(self, s_case):
        s_case[txs_const.CHECK_FIELD] = txs_const.SEARCHDATA_DOCS
        test_json_url = cgi.UrlCgiCustomizer(
            base_url=u'{}/search/'.format(self.Parameters.beta_url),
        ).add_custom_params(
            s_case["params"],
        ).add_custom_param(
            'json_dump',
            txs_const.SEARCHDATA_DOCS,
        ).add_custom_param(
            'json_dump',
            txs_const.JSON_REQID_KEY,
        ).no_cookie_support()
        test_json_url.add_custom_cgi_string(self._add_cgi())
        json_data, text_response = self._get_json_parsed_response(
            test_json_url,
            test_name="operators",
            reqid_key=txs_const.JSON_REQID_KEY,
        )
        self._check_case(json_data, s_case, test_name="operators", non_empty=True)

    def _check_case(self, json_data, s_case, test_name=txs_const.UNSPECIFIED, non_empty=False):
        eh.ensure(json_data, "Test `{}` is broken, json response must be valid. ".format(test_name))
        check_key = s_case[txs_const.CHECK_FIELD]

        if check_key not in json_data:
            logging.error("Invalid answer, no %s in response:\n%s\n\n", check_key, json_data)
            raise Exception("Test `{}` is broken, no `{}` field. ".format(test_name, check_key))

        if non_empty and not json_data[check_key]:
            raise Exception('Test `{}` is broken, field `{}` is empty. '.format(test_name, check_key))

    @decorators.retries(max_tries=3, delay=3, backoff=2)
    def _get_video_top_xml_response(self):
        xml_dump_url = (
            "{}/search/xml/?type=video&vtop=1"
            "&dump_groupings=yes"
            # see https://a.yandex-team.ru/arc/trunk/arcadia/web/report/lib/YxWeb/Report/XML.pm?rev=3444772#L532
            "&dump-invalid=1".format(
                self.Parameters.beta_url,
            )
        )
        logging.debug("[Video VTOP] Requesting %s", xml_dump_url)
        # use non-retrying wrapper here
        xml_data = requests_wrapper.get(xml_dump_url).content
        xml_response = None
        try:
            xml_response = etree.ElementTree.fromstring(xml_data)
        except Exception as e:
            eh.log_exception("Cannot parse XML from string", e)
            logging.debug("XML VTOP answered with bad XML:\n%s\n\n", xml_data)
            raise

        xml_reqid = self._get_reqid(xml_response, xml_data)
        xml_docs = self._find_docs(xml_response)
        return xml_reqid, xml_docs

    def _get_json_response(self, url, query_data, reqid_key=txs_const.JSON_REQID_KEY):
        """
        Queries Yandex, obtains query reqid and list of documents (urls)
        from json response
        @param url: UrlCgiCustomizer object
        @param query_data: _QUERY_DATA restricted to current search type
        @return: reqid and list of urls (documents)
        """
        url.add_custom_cgi_string(self._add_cgi())
        json_data, text_response = self._get_json_parsed_response(url, reqid_key=reqid_key)
        if json_data is None:
            logging.error("No json response available for `%s`", url)
            return None, None

        reqid = None
        if reqid_key not in json_data:
            logging.error(
                "No reqid detected in json response for %s:\n%s\n\n",
                url, json.dumps(json_data, indent=2),
            )
        else:
            reqid = json_data[reqid_key]

        docs_key = query_data[txs_const.JSON_QUERY]
        if docs_key not in json_data:
            logging.error("Invalid json response, no `%s` key:\n%s\n\n", docs_key, json_data)
            return reqid, None

        docs = json_data[docs_key]
        json_docs = [doc['url'] for doc in docs]

        if not json_docs:
            # minor unanswer rate is allowed here
            logging.error("JSON unanswer detected (no docs), reqid: `%s`", reqid)
            return reqid, None

        logging.debug('JSON reqid: `%s`, JSON docs: %s', reqid, json_docs)
        return reqid, json_docs

    def _get_json_parsed_response(
        self,
        url,
        test_name=txs_const.UNSPECIFIED,
        reqid_key=txs_const.JSON_RDAT_REQID_KEY,
    ):
        headers = self.Parameters.add_headers
        """
        Low-level json response obtainer

        :param url: UrlCgiCustomizer object
        :return (json_response, text_response)
        """
        try:
            logging.info("[_get_json_parsed_response] Requesting `%s`, reqid key: `%s`", url, reqid_key)
            # retries inside
            r = txs_util.requests_get_r(url.base_url, params=url.params, raise_for_empty_response=True,
                                        headers=headers)
        except Exception as err:
            logging.error("Cannot obtain json response. Error: `%s`", err)
            self._set_error(
                "Cannot obtain non-empty response after retries. "
                "Test `{test_name}` seems to be broken. No reqid available. ".format(
                    test_name=test_name,
                )
            )
            return None, None

        try:
            json_response = r.json()
        except Exception as err:
            logging.error(
                "Cannot parse json response. Error: `%s`, status code: `%s`, text:\n%s\n\n",
                err, r.status_code, r.text,
            )
            self._set_error(
                "Cannot parse json response. Test `{test_name}` seems to be broken".format(
                    test_name=test_name,
                )
            )
            return None, r.text

        logging.info(
            '[_get_json_parsed_response] Got valid json response for test `%s` `%s`, reqid: `%s`',
            test_name, url, json_response.get(reqid_key, ""),
        )

        return json_response, r.text

    def _get_response_diff(self, queries, search_type, max_fail_count):
        """
        :param queries: pairs (query, region) in plain text format
        :param search_type: see _SEARCH_TYPES collection
        :param max_fail_count: when failed more than this amount of queries, stop diff
        :return: (list of diff entries, fail count)
        """
        diff = []
        even = False

        query_data = txs_const.QUERY_DATA[search_type]
        beta_url = self._select_beta("", search_type, search_type, self.Parameters.beta_url)
        beta_url = self._select_beta(beta_url, search_type, "images", self.Parameters.images_beta_url)
        beta_url = self._select_beta(beta_url, search_type, "video", self.Parameters.video_beta_url)

        common_json_url = u'{}{}'.format(beta_url, query_data[txs_const.JSON])
        common_xml_url = u'{}{}'.format(beta_url, query_data[txs_const.XML])

        common_json_url = (
            cgi.UrlCgiCustomizer(base_url=common_json_url)
            # using json_dump=1 is too heavy (see SPINCIDENTS-1248 and SEARCH-6221)
            .add_custom_param('json_dump', txs_const.JSON_REQID_KEY)
            .add_custom_param('json_dump', query_data[txs_const.JSON_QUERY])
            .no_cookie_support()
        )
        timeout = self.Parameters.timeout

        common_xml_url = cgi.UrlCgiCustomizer(base_url=common_xml_url)
        if timeout:
            timeout = str(timeout)
            common_json_url.add_custom_param("timeout", timeout)
            common_xml_url.add_custom_param("timeout", timeout)

        fail_count = 0

        for text, region in queries:

            if fail_count >= max_fail_count:
                # too much failures, abort further checks to save time
                break

            logging.debug('Request: text "%s", region "%s"', text, region)

            json_reqid, json_docs, xml_reqid, xml_docs = 'None', [], 'None', []
            iter_json_url = cgi.UrlCgiCustomizer(common_json_url.base_url, common_json_url.params)
            iter_json_url.add_text(text).add_region(region)
            iter_xml_url = cgi.UrlCgiCustomizer(common_xml_url.base_url, common_xml_url.params)
            iter_xml_url.add_text(text).add_region(region)
            try:
                json_reqid, json_docs = self._get_json_response(
                    iter_json_url,
                    query_data,
                    reqid_key=txs_const.JSON_REQID_KEY,
                )
                if json_docs is None:
                    # allow some unanswers rate
                    fail_count += 1
                    continue

                xml_reqid, xml_docs, _ = self._get_xml_response(iter_xml_url)
                if xml_docs is None:
                    # allow some unanswers rate
                    fail_count += 1
                    continue

            except Exception as e:
                eh.log_exception("Something went wrong, using default values...", e)

            problem = 'xml unanswer' if (json_docs and not xml_docs) else None
            problem = txs_util.check_invalid_urls(xml_docs) if not problem else problem

            if problem:
                even = not even
                diff_entry = {
                    'text': text,
                    'region': region,
                    'json_reqid': json_reqid,
                    'json_docs': json_docs,
                    'xml_reqid': xml_reqid,
                    'xml_docs': xml_docs,
                    'even': 'even' if even else 'odd',
                    'problem': problem,
                }
                logging.debug('Problem detected: %s, diff entry\n%s', problem, diff_entry)
                diff.append(diff_entry)

        logging.debug('Summary diff: %s', diff)
        self.set_info("Empty docs problem count for '{}' search type: {}".format(search_type, fail_count))
        return diff, fail_count

    def _get_reqid(self, xml_response, xml_text):
        logging.info("xml_response: %s", xml_response)
        reqid_node = xml_response.find('./response/reqid')
        logging.info("xml_response: %s", reqid_node)
        if reqid_node is None:  # `if not` will not work, see the docs
            logging.error("ReqId not detected in response:\n%s\n--------------------------------", xml_text)
            return ''
        return reqid_node.text

    def _add_cgi(self):
        return "&" + self.Parameters.add_cgi

    def _add_xml_only_cgi(self):
        return "&" + self.Parameters.add_xml_only_cgi

    def _select_beta(self, beta_url, search_type, chosen_search_type, new_beta_url):
        """
        Beta alternator for verticals
        """
        if search_type == chosen_search_type and new_beta_url:
            logging.info("Switched to %s as target search type is %s", new_beta_url, chosen_search_type)
            beta_url = new_beta_url
        return beta_url

    def _get_queries(self):
        queries = []
        users_queries_resource_path = str(sdk2.ResourceData(self.Parameters.queries_plan).path)
        with codecs.open(users_queries_resource_path, 'r', 'utf-8') as f:
            for _ in range(self.Parameters.shoots_number):
                tmp = f.readline().split()
                text, region = ' '.join(tmp[:-1]), tmp[-1]
                queries.append((text, region))
        return queries

    def _set_error(self, error, exc=None, test_name=None):
        aux_error = ''
        if exc:
            eh.log_exception(error, exc)
            aux_error = ', additional error info: ' + str(exc)

        self.Context.tests_failed = True
        self.Context.save()
        self.set_info(
            '<b color="red">{test_name}{error}</b>{aux_error}'.format(
                error=error,
                test_name='[{}] '.format(test_name) if test_name else '',
                aux_error=aux_error,
            ),
            do_escape=False,
        )
        release_num = self.Parameters.release_number
        component_name = self.Parameters.component_name
        if release_num and component_name:
            st = st_helper.STHelper(sdk2.Vault.data(rm_const.COMMON_TOKEN_OWNER, rm_const.COMMON_TOKEN_NAME))
            c_info = rmc.COMPONENTS[component_name]()
            st.write_grouped_comment(
                rm_const.TicketGroups.XMLTest, "", "**!!ERROR!!** {}".format(error), release_num, c_info
            )

    def _fill_report(self, report):
        logging.debug('Data for HTML report: %s', report)
        out_diff_path = self.Parameters.xml_search_report_resource.path
        if report:
            self._fill_html_report(report, out_diff_path)
            eh.check_failed('\n' + '\n'.join(report.keys()))
        else:
            self._fill_html_report({}, out_diff_path)

    def _fill_html_report(self, diff, report_path):
        txs_util.write_html_file(diff, report_path)
        self.set_info(
            utils2.resource_redirect_link(self.Parameters.xml_search_report_resource.id, txs_const.OUTPUT_NAME),
            do_escape=False,
        )

    def _get_rm_test_results(self):

        if self.is_binary_run:
            logging.warning('Test results CANNOT be established: the task is not run in a binary task mode')
            return

        from release_machine.common_proto import test_results_pb2 as rm_test_results

        logging.info('Going to populate generate TestResult object')
        test_results = rm_test_results.TestResult(
            status=(
                rm_test_results.TestResult.TestStatus.OK if not self.Context.tests_failed
                else rm_test_results.TestResult.TestStatus.WARN
            ),
            report_link=self.Parameters.xml_search_report_resource.url,
        )
        logging.debug("The following data dumped to context:\n%s\n--------------------------", test_results)
        return test_results

    def _get_rm_proto_event_specific_data(self, rm_proto_events, event_time_utc_iso, status=None):
        return {
            'acceptance_test_data': rm_proto_events.AcceptanceTestData(
                acceptance_type=rm_proto_events.AcceptanceTestData.AcceptanceType.XML,
                job_name=self.Context.job_name,
                revision=six.text_type(self.Context.svn_revision),
                scope_number=six.text_type(self.Parameters.release_number),
                test_result=self._get_rm_test_results(),
            ),
        }
