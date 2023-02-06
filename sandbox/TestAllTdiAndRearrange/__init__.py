# -*- coding: utf-8 -*-

import collections
import datetime
import dateutil
import dateutil.tz as tz
import json
import logging
import re
import time

import sandbox.projects.release_machine.core.task_env as task_env
import sandbox.common.types.task as ctt
from sandbox.common import rest

import sandbox.projects.release_machine.input_params as rm_params
from sandbox.projects import GetRandomRequests as RandReq
from sandbox.projects import resource_types
from sandbox.projects.common import apihelpers
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import ra2
from sandbox.projects.common import string
from sandbox.projects.common import utils
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.release_machine import yappy as yappy_helper
from sandbox.projects.release_machine.helpers import events_helper
from sandbox.projects.release_machine.helpers.startrek_helper import STHelper
from sandbox.projects.common.search import bugbanner
from sandbox.projects.release_machine.components import all as rmc
from sandbox.projects.common.betas.beta_api import BetaApi
import sandbox.projects.release_machine.rm_notify as rm_notify
from sandbox.projects.release_machine.tasks import GetReportSimultaneousResponses as grsr
from sandbox.projects.release_machine.tasks.ScrapeRequests2 import parameters as sr_params

from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.task import SandboxTask

_DEFAULT_CGI = (
    "&json_dump=searchdata"
    "&json_dump=search_props"
    "&json_dump=reqparam"
    "&waitall=da"
    "&nocache=da"
    "&no-tests=1"
    "&json_dump=rdat.cgi.hostname"
    "&json_dump=unanswer_data"
    "&timeout=9999999"
)

_FAST_JSON_DUMP_CGI = (
    "&json_dump=search_props.UPPER"
    "&json_dump=search_props.WEB"
    "&json_dump=searchdata.docs"
    "&json_dump=searchdata.docs_right"
    "&json_dump=search.context.global.rearr.0"
    "&nocache=da"
    "&no-tests=1"
    "&rearr=scheme_Local/ApplyBlender/DumpFactorsAsText=1"
)

_PROPS_ONLY_JSON_DUMP_CGI = (
    "&json_dump=search_props.UPPER"
    "&json_dump=search_props.WEB"
    "&nocache=da"
    "&no-tests=1"
    "&rearr=scheme_Local/ApplyBlender/DumpFactorsAsText=1"
)

_PROPS_QUICK_CGI = (
    "&json_dump=search_props.UPPER"
    "&json_dump=searchdata.docs"
    "&json_dump=search.context.clients.WEB.rearr.0"
    "&nocache=da"
    "&no-tests=1"
)


class RegionKeys(object):
    RU = "RU"
    KZ = "KZ"
    UA = "UA"
    BY = "BY"
    TR = "TR"


_REGIONS_DATA = {
    RegionKeys.RU: {"domain": "ru", "geo_id": 225},
    RegionKeys.KZ: {"domain": "kz", "geo_id": 159},
    RegionKeys.UA: {"domain": "ua", "geo_id": 187},
    RegionKeys.BY: {"domain": "by", "geo_id": 149},
    RegionKeys.TR: {"domain": "com.tr", "geo_id": 983},
}

_COLLECTIONS = [
    "search",
    "touchsearch",
    "padsearch",
]

BLENDER_RA_GROUPS = [
    "blender-facts",
    "blender-static_stream",
    "blender-stream",
]

BLENDER_RA2_GROUPS = [
    "ra2-{blender_test}-{collection}".format(
        blender_test=blender_test,
        collection=collection,
    ) for blender_test in BLENDER_RA_GROUPS for collection in _COLLECTIONS
]


_WEB_PROFILE = "weak_consistency__web__desktop__hamster__tier0"
_WEB_TOUCH_PROFILE = "weak_consistency__web__touch__hamster__tier0"

BLENDER_RESOURCES_CREATED = "blender_resources_created"
BLENDER_RESOURCES_FETCHED = "blender_resources_fetched"
GOT_RA2_COMMON_RES = "got_ra2_common_resources"
RA2_BUILD_PARSER = "ra2_build_parser"
BROKEN_TASKS_KEY = "broken_tasks_already_notified"

# RMDEV-3126
ALL_REGIONS = list(_REGIONS_DATA.keys())
BLENDER_REGIONS = [
    RegionKeys.RU,
    RegionKeys.KZ,
    RegionKeys.BY,
    RegionKeys.TR,
]
IMAGES_REGIONS = [
    RegionKeys.RU,
    RegionKeys.KZ,
    RegionKeys.BY,
    RegionKeys.TR,
]
VIDEO_REGIONS = [
    RegionKeys.RU,
    RegionKeys.TR,
]

REARR_BLENDER_PARAMS = {
    "blender": {
        "notify_if_failed": "dima-zakharov",
        "collections": {
            "search": BLENDER_REGIONS,
            "touchsearch": ["RU"],
            "padsearch": ["RU"],
        },
        "tests_groups": [  # деление на tests_groups, потому что у тестов могут быть разные группы регионов
            {
                "test_params": {
                    "predefined": ["static_stream"],
                    "random": ["stream"],
                },
                "regs": BLENDER_REGIONS,
            },
            {
                "test_params": {"predefined": ["facts"]},
                "regs": ["RU"],
            },
        ],
    },
}
REARR_OTHER_PARAMS = {
    "personalization": {
        "regs": ALL_REGIONS,
        "ctx": {
            "notify_if_failed": "sankear",
            "config_attr": "personalization_priemka_rearrange_config",
            "use_personal_uids": 1
        }
    },
}
REARR_NEW_PARAMS = {
    "rearrange": {
        "regs": BLENDER_REGIONS,
        "ctx": {}
    },
    "rearrange_filter": {
        "regs": [RegionKeys.RU, RegionKeys.TR],
        "ctx": {
            "search_prop_filter": "'UPPER.ApplyBlender.IntentWeight/FRESH' > 0.01"
        }
    },
}
MEDIA_REARR_NEW_PARAMS = {
    "images": {
        "regs": IMAGES_REGIONS,
        "ctx": {
            "success_only": "IMAGESQUICKP,IMAGESP",
            "unanswered_sources": "WEB:max_delta=0.02,VIDEOP:max_delta=0.01,IMAGESP:max_delta=0.01"
        },
        "collection": "search",
        "add_cgi": (
            "&rearr=scheme_Local/ApplyImagesBlender/DumpFactors=1"
            "&json_dump=search_props.IMAGESP"
        )
    },
    "video": {
        "regs": VIDEO_REGIONS,
        "ctx": {
            "success_only": "VIDEOQUICKP,VIDEOP",
            "unanswered_sources": "WEB:max_delta=0.02,VIDEOP:max_delta=0.01,IMAGESP:max_delta=0.01"
        },
        "collection": "search",
        "add_cgi": "&rearr=scheme_Local/ApplyVideoBlender/DumpFactors=1"
    },
    "videoserp": {
        "regs": VIDEO_REGIONS,
        "ctx": {
            "success_only": "VIDEOQUICK,VIDEO,ENTITYSEARCH,VIDEO_REQUEST_EXTENSIONS",
            "unanswered_sources": ""
        },
        "collection": "video",
        "add_cgi": (
            "&rearr=scheme_Local/ApplyVideoBlender/DumpFactors=1"
            "&json_dump=searchdata.clips"
        )
    },
}
_MAX_EXEC_CHILDREN = 30  # enough for SoY
_UNKNOWN = "Unknown"
_FAIL = "Fail"
_OK = "Ok"
TASK_LINK_REGEXP = re.compile("task_link\\(([^,]*),([^,]*),\\)")

CONFIG_DIRECTORY = "/sandbox/projects/release_machine/tasks/RearrangeAcceptance2/config/"


def _make_url(url, name, is_wiki_format):
    template = '(({url}/{name} {name}))' if is_wiki_format else '<a href="{url}/{name}" target="_blank">{name}</a>'
    return template.format(url=url, name=name)


def _service_url(name, is_wiki_format):
    return _make_url('https://abc.yandex-team.ru/services', name, is_wiki_format)


def _person_url(name, is_wiki_format):
    return _make_url('https://staff.yandex-team.ru', name, is_wiki_format)


class LaunchNewRAForBlenderDesktop(sp.SandboxBoolParameter):
    name = "launch_new_RA_for_blender_on_desktop"
    description = "Launch RA2 tests for blender on desktop"
    default_value = True
    collection = "search"


class LaunchNewRAForBlenderTouch(sp.SandboxBoolParameter):
    name = "launch_new_RA_for_blender_on_touch"
    description = "Launch RA2 tests for blender on touch"
    default_value = False
    collection = "touchsearch"


class LaunchNewRAForBlenderPad(sp.SandboxBoolParameter):
    name = "launch_new_RA_for_blender_on_pad"
    description = "Launch RA2 tests for blender on pad"
    default_value = False
    collection = "padsearch"


NEW_RA_BLENDER_TESTS_PLATFORM_PARAMETERS = (
    LaunchNewRAForBlenderDesktop,
    LaunchNewRAForBlenderTouch,
    LaunchNewRAForBlenderPad,
)


class LaunchNewRAForBlender(sp.SandboxBoolParameter):
    name = "launch_new_RA_for_blender_and_video"
    description = "Launch RA2 BLENDER tests"
    default_value = False
    sub_fields = {
        "true": [
            TestPlatformParameter.name for TestPlatformParameter in NEW_RA_BLENDER_TESTS_PLATFORM_PARAMETERS
        ]
    }


class LaunchImg(sp.SandboxBoolParameter):
    name = "launch_images_RA"
    description = "Launch images tests (RA2)"


class LaunchVideo(sp.SandboxBoolParameter):
    name = "launch_video_RA"
    description = "Launch video tests (RA2)"


class LaunchVideoserp(sp.SandboxBoolParameter):
    name = "launch_videoserp_RA"
    description = "Launch videoserp tests (RA2)"


class LaunchPersonalizationRA2(sp.SandboxBoolParameter):
    name = "launch_personalization_RA2"
    description = "Launch personalization RA2 tests"
    default_value = False


class LaunchQuickRA2(sp.SandboxBoolParameter):
    name = "launch_quick_RA2"
    description = "Launch QUICK RA2 tests"
    default_value = False


class LaunchNewRA(sp.SandboxBoolParameter):
    name = "launch_new_RA"
    description = "Launch RA2 tests"


class FailIfBetasChanged(sp.SandboxBoolParameter):
    name = "fail_if_betas_changed"
    description = "Fail task if betas changed"
    default_value = False


class GetRandomReqsOnce(sp.SandboxBoolParameter):
    name = "get_random_reqs_once"
    description = "Get random requests once (speeds up priemka)"
    default_value = True


class SeekTwoContextsFeaturesDiffBinary(sp.SandboxBoolParameter):
    name = "seek_two_contexts_features_diff_binary"
    description = "Seek for two_contexts_features_diff binary on sandbox before building it"
    default_value = False


class SeekQueries(sp.SandboxBoolParameter):
    name = "seek_queries"
    description = "Seek for random queries on sandbox before collecting them"
    default_value = False


class RunCount(sp.SandboxIntegerParameter):
    name = "run_count"
    description = "Number of runs for each test"
    default_value = 3


class SummonLogins(sp.SandboxStringParameter):
    name = "summon_logins"
    description = "Comma-separated list of logins to summon on test results"
    default_value = ""


class IgnorePassed(sp.SandboxBoolParameter):
    name = "ignore_passed"
    description = "Don't run tests that passed in previous run"
    default_value = False


class AddCgi(sp.SandboxStringParameter):
    name = "add_cgi"
    description = "Add CGI parameters (e.g. '&test-id=62534')"
    default_value = ""


class CommonAddCgi(sp.SandboxStringParameter):
    name = "common_add_cgi"
    description = "Add CGI parameters to both betas (e.g. '&test-id=62534')"
    default_value = ""


class DebugMode(sp.SandboxBoolParameter):
    name = "debug_mode"
    description = "Run task with debug features enabled"
    default_value = False


@rm_notify.notify2()
class TestAllTdiAndRearrange(bugbanner.BugBannerTask):
    """
        **Release-machine**
        Таск для запуска всех RearrangeAcceptance тестов.
    """
    type = "TEST_ALL_TDI_AND_REARRANGE"
    environment = [task_env.TaskRequirements.startrek_client]
    client_tags = task_env.TaskTags.startrek_client
    execution_space = 1024  # 1 Gb
    input_parameters = (
        (
            rm_params.ComponentName,
            rm_params.ReleaseNum,
            rm_params.SampleBeta,
            rm_params.CheckedBeta,
            rm_params.CheckedBetaVideo,
            rm_params.CheckedBetaImages,
            LaunchNewRAForBlender,
        ) +
        NEW_RA_BLENDER_TESTS_PLATFORM_PARAMETERS +
        (
            LaunchImg,
            LaunchVideo,
            LaunchVideoserp,
            LaunchPersonalizationRA2,
            LaunchNewRA,
            LaunchQuickRA2,
            FailIfBetasChanged,
            GetRandomReqsOnce,
            SeekTwoContextsFeaturesDiffBinary,
            SeekQueries,
            RunCount,
            SummonLogins,
            IgnorePassed,
            AddCgi,
            CommonAddCgi,
        ) +
        (
            sr_params.ScraperOverYtPoolParameter,
        ) + (
            DebugMode,
        )
    )

    _GROUPS_ORDER = BLENDER_RA2_GROUPS + [
        "ra2 personalization",
        "personalization",
        "rearrange",
        "rearrange_filter",
        "images",
        "video",
        "videoserp",
    ]
    _TIMING_KEY = "children_execution_timing"

    _RESPONSIBLE = collections.defaultdict(lambda: {'persons': [], 'services': []})
    _RESPONSIBLE.update({
        'ra2-blender-facts-search': {
            'persons': ['antonio'],
            'services': ['facts', 'objectanswer'],
        },
        'ra2-blender-static_stream-search': {
            'persons': ['epar'],
            'services': ['blndr'],
        },
        'ra2-blender-stream-search': {
            'persons': ['epar'],
            'services': [],
        },
        'personalization': {
            'persons': [],
            'services': ['searchpers-web'],
        },
        'ra2 personalization': {
            'persons': [],
            'services': ['searchpers-web'],
        },
        'rearrange': {
            'persons': ['nkmakarov'],
            'services': ['verticalsonserp'],
        },
        'rearrange_filter': {
            'persons': ['nkmakarov'],
            'services': ['verticalsonserp'],
        },
        'images': {
            'persons': [],
            'services': ['images'],
        },
        'video': {
            'persons': ['shaveinikovds'],
            'services': [],
        },
        'videoserp': {
            'persons': ['shaveinikovds'],
            'services': [],
        },
    })

    @staticmethod
    def _get_responsible(is_wiki_format):
        res = []
        for g in TestAllTdiAndRearrange._GROUPS_ORDER:
            res.append(' '.join(
                [_person_url(p, is_wiki_format) for p in TestAllTdiAndRearrange._RESPONSIBLE[g]["persons"]] +
                [_service_url(s, is_wiki_format) for s in TestAllTdiAndRearrange._RESPONSIBLE[g]["services"]]
            ))
        return res

    @property
    def footer(self):
        if "launched_tasks" not in self.ctx:
            return
        run_count = utils.get_or_default(self.ctx, RunCount)
        launched_names = [sorted(n_run.keys()) for n_run in self.ctx["launched_tasks"]]
        client = rest.Client()
        children_info = client.task.read(
            parent=self.id,
            fields=(
                'status,'
                'description,'
                'context.html_report_resource_proxy_url'
            ),
            hidden=True,
            limit=len(self.list_subtasks()),
        ).get("items", [])
        children_info.sort(key=lambda info: info.get("description", ""))
        body = {
            "test_name": [],
            "result": [],
        }
        for n_run in xrange(run_count):
            body["run_" + str(n_run)] = []
        for launched_name in launched_names[0]:
            launch_report = None
            short_descr = self.shorten_name(launched_name)
            body["test_name"].append(short_descr)
            for n_run in xrange(run_count):
                i_x = [
                    child for child in children_info
                    if child["description"] == self._update_child_name(n_run, launched_name)
                ]
                body["run_" + str(n_run)].append(self._result_of_run(i_x))
                if i_x:
                    launch_report = i_x[0].get("context.html_report_resource_proxy_url")
            if launch_report:
                body["result"].append(
                    "\n".join(
                        '<a href="{url}/index.html">{domain}</a>'.format(
                            domain=key,
                            url=launch_report[key],
                        ) for key in launch_report
                    )
                )
            else:
                body['result'].append('No link')
        return [
            {
                "helperName": '',
                "content": {
                    "<h4>Test results</h4>": {
                        "header": [
                            {"key": "test_name", "title": "Test name"},
                        ] + [
                            {"key": "run_" + str(n_run), "title": "Run " + str(n_run)} for n_run in xrange(run_count)
                        ] + [
                            {"key": "result", "title": "Result"},
                        ],
                        "body": body
                    }
                }
            },
            {
                "helperName": '',
                "content": {"<h4>Final rearrange results</h4>": self._to_html(self.fill_final_rearr_results(False))}
            },
        ]

    def shorten_name(self, launched_name):
        return re.sub(r"run#[0-9]", "", launched_name, 1).replace(self.descr, "").strip(" ,")

    @staticmethod
    def _result_of_run(listed_name):
        return "{}, {}".format(
            lb.task_link(listed_name[0]["id"]),
            utils.colored_status(listed_name[0]["status"])
        ) if listed_name else "<b style='color:Cyan'>-</b>"

    def fill_final_rearr_results(self, is_wiki_format):
        rearr_results = {
            "header": [
                {"key": "test_group", "title": "Test Group"},
                {"key": "RU", "title": "RU"},
                {"key": "KZ", "title": "KZ"},
                {"key": "UA", "title": "UA"},
                {"key": "BY", "title": "BY"},
                {"key": "TR", "title": "TR"},
                {"key": "responsible", "title": "Responsinble"},
            ],
            "body": {
                "test_group": self._GROUPS_ORDER,
                "RU": [],
                "KZ": [],
                "UA": [],
                "BY": [],
                "TR": [],
                "responsible": [],
            }
        }
        for reg in _REGIONS_DATA.keys():
            rearr_results["body"][reg] = [self._get_result_for_group(g, reg) for g in self._GROUPS_ORDER]
        rearr_results["body"]["responsible"] = self._get_responsible(is_wiki_format)
        return rearr_results

    @staticmethod
    def _calc_answer_rate(found):
        # https://st.yandex-team.ru/SEARCH-2666#1478772311000
        # https://st.yandex-team.ru/SEARCH-2666#1479373560000
        is_enough = True
        if "request_count" in found[0].ctx and "total_request_count" in found[0].ctx:
            answer_rate = "({}/{})".format(
                found[0].ctx["request_count"],
                found[0].ctx["total_request_count"]
            )
            if found[0].ctx["total_request_count"]:
                is_enough = 1.0 * found[0].ctx["request_count"] / found[0].ctx["total_request_count"] > 0.7
        else:
            answer_rate = "No stats"
        return is_enough, answer_rate

    def _get_launched_tasks_for_group(self, group):
        for launches in reversed(self.ctx["launched_tasks"]):
            found = [
                channel.sandbox.get_task(t_id) for name, t_id in launches.iteritems()
                if name.startswith("{} for".format(group))
            ]

            if found:
                return found

        return []

    def _get_result_for_group(self, group, reg=None, format_link=True):

        default_return_value = "-" if format_link else ("-", "", "")

        found = self._get_launched_tasks_for_group(group)

        if not found:
            return default_return_value

        test_task = found[0]

        if "tests_final_statuses" not in test_task.ctx and not test_task.is_finished():
            return default_return_value

        is_enough, answer_rate = self._calc_answer_rate(found)
        state = _UNKNOWN

        if _REGIONS_DATA[reg]["domain"] in test_task.ctx.get("tests_final_statuses", {}):
            status = test_task.ctx["tests_final_statuses"][_REGIONS_DATA[reg]["domain"]]
            if status == "PASSED" and is_enough:
                state = _OK
            elif status == "FAILED":
                state = _FAIL

        if format_link:
            return "{} task_link({},{},)".format(state, lb.task_link(test_task.id, plain=True), answer_rate)
        else:
            return state, lb.task_link(test_task.id, plain=True), answer_rate

    def on_break(self):
        """
        Report about errors into ST ticket (SEARCH-2294)
        """
        bugbanner.BugBannerTask.on_break(self)
        try:
            token = self.get_vault_data(rm_const.COMMON_TOKEN_OWNER, rm_const.COMMON_TOKEN_NAME)
            c_info = rmc.COMPONENTS[self.ctx[rm_params.ComponentName.name]]()
            STHelper(token).comment_task_problem(self, self.ctx.get(rm_params.ReleaseNum.name), c_info)
        except ImportError:
            # Error report failure should not fail the whole job
            # https://st.yandex-team.ru/RMINCIDENTS-42#1484567762000
            pass

        self._post_rm_proto_event()

    def on_success(self):
        self._post_rm_proto_event('SUCCESS')

    def on_failure(self):
        self._post_rm_proto_event('FAILURE')

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        if rm_params.ComponentName.name in self.ctx and self.ctx[rm_params.ComponentName.name]:
            c_info = rmc.get_component(self.ctx[rm_params.ComponentName.name])
            sem_name = "{}/{}".format(self.type, c_info.name)
            self.semaphores(ctt.Semaphores(
                acquires=[
                    ctt.Semaphores.Acquire(name=sem_name, capacity=c_info.max_running_task_capacity)
                ]
            ))

    def get_summonees(self):
        return [login.strip() for login in utils.get_or_default(self.ctx, SummonLogins).split(',') if login.strip()]

    def on_execute(self):
        self.add_bugbanner(bugbanner.Banners.NoapacheUpper)
        self.fill_context()

        st_helper = STHelper(self.get_vault_data(rm_const.COMMON_TOKEN_OWNER, rm_const.COMMON_TOKEN_NAME))
        c_info = rmc.COMPONENTS[self.ctx[rm_params.ComponentName.name]]()
        beta_api = BetaApi.fromurl()
        run_count = utils.get_or_default(self.ctx, RunCount)

        self._notify_on_broken_subtasks(st_helper, c_info)

        if "launched_tasks" not in self.ctx:
            self._save_beta_info(beta_api)
            self._launch_random_requests_getter()

            priemka_ticket = st_helper.find_ticket_by_release_number(self.ctx.get(rm_params.ReleaseNum.name), c_info)
            if priemka_ticket:
                self.ctx["st_priemka_ticket"] = priemka_ticket.key
            self.ctx["launched_tasks"] = [{} for _ in xrange(run_count + 1)]  # need one more empty element
            self.ctx[self._TIMING_KEY] = [time.time()] + [None for _ in xrange(run_count)]

        prev_finished = True

        for n_run in xrange(run_count):
            cur_launched, cur_finished = self.launch_children(n_run, st_helper, c_info, beta_api)
            if prev_finished and cur_finished and self.ctx[self._TIMING_KEY][n_run + 1] is None:
                logging.info("Nothing left to launch for %s run, go to the next iteration", n_run)
                # SEARCH-2094
                # set timing for every task launching row
                self.ctx[self._TIMING_KEY][n_run + 1] = time.time()
            prev_finished = prev_finished and cur_finished
            if not cur_launched:
                break

        if not prev_finished:
            self._post_rm_proto_event()
            self.wait_tasks(
                utils.get_working_subtasks(),
                statuses=tuple(ctt.Status.Group.FINISH) + tuple(ctt.Status.Group.BREAK),
                wait_all=False,
            )

        results = self._to_wiki_format(self.fill_final_rearr_results(True))
        self._check_beta_info(beta_api)
        self._show_launch_timings()
        logging.debug("Send results to priemka noapache %s:\n%s", self.ctx.get(rm_params.ReleaseNum.name), results)
        summonees = self.get_summonees()
        st_helper.comment(
            self.ctx.get(rm_params.ReleaseNum.name),
            "{}\n\n{}".format(lb.task_wiki_link(self.id, "Task"), results),
            c_info,
            summonees,
        )
        utils.check_subtasks_fails(
            stop_on_broken_children=True,
            custom_subtasks=self._get_last_launched_row(),
        )

    def _launch_random_requests_getter(self):
        if not utils.get_or_default(self.ctx, GetRandomReqsOnce):
            return
        if self.ctx.get(GOT_RA2_COMMON_RES):
            logging.info("Random requests already exist")
            return

        # Batched mode won't work with older version
        # So if you need old yweb/freshness version, use resource_id=1879228666
        binary_task_description = "Periodically build search/ra2/two_contexts_features_diff"
        binary_sources_path = "search/ra2/two_contexts_features_diff"

        if self.ctx.get(SeekTwoContextsFeaturesDiffBinary.name):
            found_tasks = channel.sandbox.list_tasks(
                task_type="BUILD_ARCADIA_BINARY",
                status="FINISHED",
                completed_only=True,
                descr_mask=binary_task_description,
            )
            found_tasks = sorted(found_tasks, key=lambda x: int(x.id), reverse=True)
            for t in found_tasks:
                if t.ctx.get('out_resource_id'):
                    res = channel.sandbox.get_resource(t.ctx['out_resource_id'])
                    if res and res.is_ready():
                        logging.info(
                            "Found " + str(t.id) + " task which built two_contexts_features_diff. Reusing its result."
                        )
                        self.ctx[RA2_BUILD_PARSER] = t.id
                        break

        ra2_tasks = [t for t in self.get_tasks_to_launch(0) if t["task_type"] == "REARRANGE_ACCEPTANCE_2"]
        if ra2_tasks and not self.ctx.get(RA2_BUILD_PARSER):
            logging.info("Launch arcadia binary builder for two_contexts_features_diff")
            self.ctx[RA2_BUILD_PARSER] = self.create_subtask(
                task_type="BUILD_ARCADIA_BINARY",
                arch="linux",
                execution_space=20000,  # 20G
                description="Build two_contexts_features_diff for {} task #{}".format(self.type, self.id),
                input_parameters={
                    "notify_if_finished": "",
                    "build_path": binary_sources_path,
                    "binaries": binary_sources_path + "/two_contexts_features_diff",
                },
            ).id

        if [t for t in ra2_tasks if not t["input_parameters"].get("req_resource_id")]:
            if self.ctx.get(SeekQueries.name):
                need_to_build = False
                for reg_info in _REGIONS_DATA.itervalues():
                    dom = reg_info["domain"].split(".")[-1]
                    req_attr = "random_requests=1500,geo_id={}".format(reg_info["geo_id"])
                    reqs_resource = apihelpers.get_last_resource_with_attrs(
                        resource_types.USERS_QUERIES,
                        attrs=string.parse_attrs(req_attr),
                        all_attrs=True,
                    )
                    if reqs_resource:
                        logging.info("Found %s task which collected random queries for %s", reqs_resource.task_id, dom)
                        self.ctx["random_reqs_{}_task_id".format(dom)] = reqs_resource.task_id
                    if not self.ctx.get("random_reqs_{}_task_id".format(dom)):
                        need_to_build = True

                    # SEARCH-6820 TODO: Make queries caching more flexible
                    # filter_prop_search caching
                    req_attr = "random_requests=1501,geo_id={}".format(reg_info["geo_id"])
                    reqs_resource = apihelpers.get_last_resource_with_attrs(
                        resource_types.USERS_QUERIES,
                        attrs=string.parse_attrs(req_attr),
                        all_attrs=True,
                    )
                    if reqs_resource:
                        logging.info(
                            "Found %s task which collected random queries for %s with filter_prop_search",
                            reqs_resource.task_id, dom,
                        )
                        self.ctx["random_reqs_{}_task_id_filter".format(dom)] = reqs_resource.task_id
                    if not self.ctx.get("random_reqs_{}_task_id_filter".format(dom)):
                        need_to_build = True
            else:
                need_to_build = True
            if need_to_build:
                logging.info("Launch arcadia binary builder for get_random_queries")
                random_queries_binary_builder_task_id = self.create_subtask(
                    task_type="BUILD_ARCADIA_BINARY",
                    arch="linux",
                    execution_space=20000,  # 20G
                    description="Build get_random_queries binary for {} task #{}".format(self.type, self.id),
                    input_parameters={
                        "notify_if_finished": "",
                        "build_path": "yweb/freshness/get_random_queries",
                        "binaries": "yweb/freshness/get_random_queries/get_random_queries",
                    },
                ).id
                logging.info("Launch common random requests getters")
                for reg_info in _REGIONS_DATA.itervalues():
                    ctx_key = "random_reqs_{}_task_id".format(reg_info["domain"].split(".")[-1])
                    if not self.ctx.get(ctx_key):
                        self.ctx[ctx_key] = self.create_subtask(
                            task_type="GET_RANDOM_REQUESTS",
                            execution_space=10000,  # 10G
                            description="Requests for '{}'".format(reg_info["domain"]),
                            input_parameters={
                                "notify_if_finished": "",
                                "kill_timeout": 5 * 60 * 60,  # 5 hours
                                RandReq.NumOfRequestParameter.name: 1500,
                                RandReq.RegionalParameter.name: reg_info["geo_id"],
                                RandReq.ServicesParameter.name: "web",
                                RandReq.RandomQueriesBinary.name: random_queries_binary_builder_task_id,
                            },
                        ).id

                    # SEARCH-6820 TODO: Make queries caching more flexible
                    # filter_prop_search caching
                    ctx_key = "random_reqs_{}_task_id_filter".format(reg_info["domain"].split(".")[-1])
                    if not self.ctx.get(ctx_key):
                        self.ctx[ctx_key] = self.create_subtask(
                            task_type="GET_RANDOM_REQUESTS",
                            execution_space=10000,  # 10G
                            description="Requests for '{}' with filter_prop_search".format(reg_info["domain"]),
                            input_parameters={
                                "notify_if_finished": "",
                                "kill_timeout": 5 * 60 * 60,  # 5 hours
                                RandReq.NumOfRequestParameter.name: 1501,
                                RandReq.RegionalParameter.name: reg_info["geo_id"],
                                RandReq.ServicesParameter.name: "web",
                                RandReq.RandomQueriesBinary.name: random_queries_binary_builder_task_id,
                                RandReq.SearchPropFilterParameter.name: "'UPPER.ApplyBlender.IntentWeight/FRESH' > 0.01"
                            },
                        ).id
        if ra2_tasks:
            self.ctx[GOT_RA2_COMMON_RES] = True

    def _show_launch_timings(self):
        run_count = utils.get_or_default(self.ctx, RunCount)
        for n_run in reversed(xrange(run_count)):
            delta = self.ctx[self._TIMING_KEY][n_run + 1] - self.ctx[self._TIMING_KEY][n_run]
            self.set_info("Time spent for {} run: {}".format(n_run, datetime.timedelta(seconds=delta)))

    def _get_last_launched_row(self):
        run_count = utils.get_or_default(self.ctx, RunCount)
        for i in xrange(1, run_count + 1):
            last_launched_row = self.ctx["launched_tasks"][run_count - i].values()
            if last_launched_row:
                return last_launched_row

    def _save_beta_info(self, api):
        for beta_class in [rm_params.CheckedBeta, rm_params.SampleBeta]:
            beta_name = self._get_beta_name(utils.get_or_default(self.ctx, beta_class))
            try:
                beta_before = api.get_beta_info(beta_name)
                beta_key = "{}_info_before".format(beta_class.name)
                logging.debug("%s before launch:\n%s", beta_class.name, beta_before)
                self.ctx[beta_key] = beta_key
            except Exception:
                logging.info("Can't save '%s infos: %s", beta_class.name, eh.shifted_traceback())

    def _check_beta_info(self, api):
        for beta_class in [rm_params.CheckedBeta, rm_params.SampleBeta]:
            if "{}_info_before".format(beta_class.name) not in self.ctx:
                logging.info("Can't compare %s infos: nothing to compare!", beta_class.name)
                return
            beta_name = self._get_beta_name(utils.get_or_default(self.ctx, beta_class))
            try:
                beta_after = api.get_beta_info(beta_name)
                beta_before = self.ctx.get("{}_info_before".format(beta_class.name))
                beta_info_diff = yappy_helper.cmp_beta_infos(
                    beta_before["configuration"]["sourceConfigs"],
                    beta_after["configuration"]["sourceConfigs"]
                )
                if beta_info_diff:
                    self.set_info("Config for beta '{}' was changed during the execution! Check diff in {}".format(
                        beta_class.name, beta_info_diff
                    ))
                    self.ctx["{}_diff_res_id".format(beta_class.name)] = beta_info_diff
                    if self.ctx.get(FailIfBetasChanged.name, False):
                        eh.fail("Betas shouldn't change during testing")
            except Exception:
                logging.info("Can't compare '%s' infos: %s", beta_class.name, eh.shifted_traceback())

    def _validate_beta(self, st_helper, c_info, api):
        """SEARCH-2424"""
        for beta_class in [rm_params.CheckedBeta, rm_params.SampleBeta]:
            beta_name = utils.get_or_default(self.ctx, beta_class)
            if beta_name.endswith(".hamster") or beta_name.endswith(".hamster.yandex"):  # only for sdms betas
                beta_name = beta_name[:-8] if beta_name.endswith(".hamster") else beta_name[:-15]
                yappy_consistency = False
                try:
                    yappy_consistency = api.is_beta_consistent(beta_name)
                except Exception:
                    pass
                if yappy_consistency:
                    return
                is_consistent, message = yappy_helper.wait_consistency(self, api, beta_name)
                if not is_consistent and not yappy_consistency:
                    summonees = self.get_summonees()
                    st_helper.comment(self.ctx.get(rm_params.ReleaseNum.name), message, c_info, summonees)
                    eh.fail(message)
            else:
                logging.info("Beta '%s' is not from sdms! Unable to validate", beta_name)

    def launch_children(self, n_run, st_helper, c_info, beta_api):
        """
            Запускаем дочерние задачи таким образом, чтобы
            в каждый момент времени было в работе не более _MAX_EXEC_CHILDREN штук.
            :return: Кортеж из двух булевых значений: первое - больше нет задач для запуска в этой волне;
                второе - все задачи волны завершены.
        """
        launched = self.ctx["launched_tasks"][n_run]
        all_tasks = self.get_tasks_to_launch(n_run)
        left_to_launch = [t for t in all_tasks if t["description"] not in launched]

        if left_to_launch:
            self._validate_beta(st_helper, c_info, beta_api)

        while left_to_launch and utils.amount_of_working_subtasks() < _MAX_EXEC_CHILDREN:
            logging.info("%s left to launch for n_run = %s", len(left_to_launch), n_run)
            task = left_to_launch.pop(0)
            task["input_parameters"][
                ra2.ReleaseMachineLaunchVerboseNameParameter.name
            ] = self.shorten_name(task["description"])
            launched_id = self.create_subtask(**task).id
            launched[task["description"]] = launched_id
        if left_to_launch:
            return False, False
        else:
            for t in [t for t in all_tasks if t["description"] in launched]:
                t_id = launched[t["description"]]
                t_status = channel.sandbox.get_task(t_id).new_status
                if t_status not in ctt.Status.Group.BREAK and t_status not in ctt.Status.Group.FINISH:
                    return True, False
        return True, True

    def _notify_on_broken_subtasks(self, st_helper, c_info):
        """SEARCH-2498"""
        already_notified = self.ctx.get(BROKEN_TASKS_KEY, [])
        broken_subtasks_to_notify = [
            t for t in self.list_subtasks(load=True)
            if t.status in ctt.Status.Group.BREAK and t.id not in already_notified
        ]
        if broken_subtasks_to_notify:
            summonees = self.get_summonees()
            st_helper.comment(
                self.ctx.get(rm_params.ReleaseNum.name),
                "There are some broken subtasks:\n" + "\n".join([
                    "{} {}: {}".format(t.descr, lb.task_wiki_link(t.id), t.status) for t in broken_subtasks_to_notify
                ]),
                c_info,
                summonees,
            )
            self.ctx.setdefault(BROKEN_TASKS_KEY, []).extend([t.id for t in broken_subtasks_to_notify])

    def get_tasks_to_launch(self, n_run):
        """
            :param n_run: number of restarts
            :return: list of tasks (as input to create_subtask) to launch on n_run
        """
        all_possible = (
            self._get_blender_tests_for_batched_mode(n_run) +
            self._get_img_and_video_tests_for_batched_mode(n_run) +
            self._get_personalization_ra2_tests_for_batched_mode(n_run) +
            self._get_new_rearr_tests_for_batched_mode(n_run) +
            self._get_quick_tests(n_run)
        )
        if n_run == 0:
            to_restart = all_possible
        else:

            to_restart = []

            run_before_and_failed = [
                (descr, t_id)
                for descr, t_id in self.ctx["launched_tasks"][n_run - 1].iteritems()
                if (
                    channel.sandbox.get_task(t_id).new_status in ctt.Status.Group.BREAK or
                    channel.sandbox.get_task(t_id).new_status == ctt.Status.FAILURE
                )
            ]

            for t_descr, t_id in run_before_and_failed:

                new_descr = self._update_child_name(n_run, t_descr)

                for task in all_possible:

                    if new_descr != task["description"]:
                        continue

                    logging.info("Restart: %s", new_descr)

                    if utils.get_or_default(self.ctx, IgnorePassed):
                        task["input_parameters"][IgnorePassed.name] = True
                        task["input_parameters"]["previous_task_id"] = t_id

                    to_restart.append(task)

        return to_restart

    @staticmethod
    def _update_child_name(n_run, old_name):
        return re.sub(r"run#[0-9]", "run#{}".format(n_run), old_name, 1)

    def _append_cgi_impl(self, cgi_params, cgi_field):
        add_cgi = utils.get_or_default(self.ctx, cgi_field) or ""
        cgi_params = cgi_params or ""

        # SEARCH-6304
        if "test-id=" in add_cgi:
            cgi_params = cgi_params.replace("no-tests=1", "")

        if not (cgi_params or add_cgi):
            return ""

        return cgi_params + "&" + add_cgi

    def _append_cgi(self, cgi_params):
        return self._append_cgi_impl(cgi_params, AddCgi)

    def _append_common_cgi(self, cgi_params):
        return self._append_cgi_impl(cgi_params, CommonAddCgi)

    def _get_new_rearr_tests_for_batched_mode(self, n_run=0):
        tests = []
        if utils.get_or_default(self.ctx, LaunchNewRA):
            for prefix, info in REARR_NEW_PARAMS.iteritems():
                regs = info["regs"]
                domains = [_REGIONS_DATA[reg]["domain"] for reg in regs]
                if "search_prop_filter" in info["ctx"]:
                    filter = True
                else:
                    filter = False
                in_ctx = self._common_ra2_input_for_batched_mode("search", domains, filter)
                cgi_params = _FAST_JSON_DUMP_CGI + (
                    "&waitall=da"
                    "&timeout=2000000"
                )
                in_ctx.update({
                    "use_config_from_arcadia": True,
                    "arcadia_config_path": CONFIG_DIRECTORY + "RA_config",
                    "threads_count": 20,
                    "unanswered_diff_threshold": 0.001,
                    "unanswered_sources": "WEB:max_delta=0.02,VIDEOP:max_delta=0.01,IMAGESP:max_delta=0.01",
                    "success_only": "QUICK,NEWSP_REALTIME_MIDDLE",
                    "unanswered_tries_count": 5,
                    "use_unanswered": True,
                    "try_till_full_success": False,
                    "beta_dump_all_json_1": False,
                    "beta_dump_all_json_2": False,
                    "beta_cgi_params_1": self._append_common_cgi(self._append_cgi(cgi_params)),
                    "beta_cgi_params_2": self._append_common_cgi(cgi_params),
                    "processed_reqs_percent_threshold": 0.7,
                })
                in_ctx.update(info["ctx"])
                test_creation_info = {
                    "task_type": "REARRANGE_ACCEPTANCE_2",
                    "execution_space": 40 * 1024,  # 40G
                    "input_parameters": in_ctx,
                    "description": "{} for {}, run#{}, {}".format(prefix, regs, n_run, self.descr.encode("utf-8"))
                }
                tests.append(test_creation_info)
                logging.info("CREATE NEW RA TEST:\n%s", json.dumps(test_creation_info, indent=2))
        return tests

    def _get_blender_rearrange_2_tests(self, n_run=0):
        tests = []
        collections_to_test = [
            TestPlatformParameter.collection for TestPlatformParameter in NEW_RA_BLENDER_TESTS_PLATFORM_PARAMETERS
            if self.ctx.get(TestPlatformParameter.name)
        ]
        run_count = utils.get_or_default(self.ctx, RunCount)
        for prefix, info in REARR_BLENDER_PARAMS.iteritems():
            for test_group in info["tests_groups"]:
                for queries_source, test_params in test_group["test_params"].iteritems():
                    for reg in test_group["regs"]:
                        for coll, regions_for_coll in info["collections"].iteritems():
                            if coll in collections_to_test and reg in regions_for_coll:
                                for test_param in test_params:
                                    is_facts = 'facts' in test_param
                                    in_ctx = self._common_ra2_input(coll, _REGIONS_DATA[reg]["domain"])
                                    config_attr = "{}_priemka-{}-config-release".format(prefix, test_param)
                                    add_cgi = (_PROPS_ONLY_JSON_DUMP_CGI if is_facts else _FAST_JSON_DUMP_CGI) + (
                                        "&waitall=da"
                                        "&timeout=2000000"
                                    )
                                    in_ctx.update({
                                        "threads_count": 20,
                                        "tries_count": 5,
                                        "notify_if_failed": info["notify_if_failed"] if n_run >= run_count - 1 else "",
                                        "beta_dump_all_json_1": False,
                                        "beta_dump_all_json_2": False,
                                        "beta_cgi_params_1": self._append_common_cgi(self._append_cgi(add_cgi)),
                                        "beta_cgi_params_2": self._append_common_cgi(add_cgi),
                                        "use_unanswered": True,
                                        "unanswered_tries_count": 1,
                                        "try_till_full_success": False,
                                        "unanswered_diff_threshold": 0.3,
                                        "unanswered_sources": (
                                            "IMAGESP:max_unanswer=0.1,"
                                            "VIDEOP:max_unanswer=0.3,"
                                            "ENTITYSEARCH:max_unanswer=0.1,"
                                            "SUGGESTFACTS2:max_unanswer=0.1"
                                        ),
                                        "processed_reqs_percent_threshold": 0.7,
                                        "use_config_from_arcadia": True,
                                        "arcadia_config_path": CONFIG_DIRECTORY + "RA_config_{}".format(config_attr),
                                    })
                                    req_attr = ''
                                    if queries_source == "predefined":
                                        req_attr = "{}_priemka-{}-queries-release=1,locale={reg}".format(
                                            prefix, test_param, reg=reg.lower()
                                        )
                                    elif queries_source == "random":
                                        req_attr = "random_requests=3000,geo_id={}".format(_REGIONS_DATA[reg]["geo_id"])
                                    else:
                                        eh.check_failed("Unknown queries source: {}".format(queries_source))
                                    reqs_resource = apihelpers.get_last_resource_with_attrs(
                                        resource_types.USERS_QUERIES,
                                        attrs=string.parse_attrs(req_attr),
                                        all_attrs=True,
                                    )
                                    if reqs_resource:
                                        in_ctx["req_resource_id"] = reqs_resource.id
                                    in_ctx["random_requests"] = 1500
                                    tests.append({
                                        "task_type": 'REARRANGE_ACCEPTANCE_2',
                                        "execution_space": 40 * 1024,  # 40G
                                        "input_parameters": in_ctx,
                                        "description": "ra2-{}-{}-{} for {}, run#{}, {}".format(
                                            prefix, test_param, coll, reg, n_run, self.descr.encode("utf-8")
                                        )
                                    })
        return tests

    def _get_img_and_video_tests_for_batched_mode(self, n_run=0):
        tests = []
        for prefix, info in MEDIA_REARR_NEW_PARAMS.iteritems():
            if not self.ctx.get("launch_{}_RA".format(prefix)):
                continue
            regs = info["regs"]
            domains = [_REGIONS_DATA[reg]["domain"] for reg in regs]
            in_ctx = self._common_ra2_input_for_batched_mode(info["collection"], domains, filter=True)
            # filter=True because we use search_prop_filter in parameters
            add_cgi = (
                _FAST_JSON_DUMP_CGI if prefix != "videoserp" else _PROPS_ONLY_JSON_DUMP_CGI
            ) + info["add_cgi"] + (
                "&json_dump=reqparam.reqid"
                "&waitall=da"
                "&timeout=4999999"
            )
            in_ctx.update({
                "use_config_from_arcadia": True,
                "arcadia_config_path": CONFIG_DIRECTORY + "RA_config_{}".format(
                    "blender_priemka-{}-config-release".format(prefix)
                ),
                "threads_count": 10,
                "unanswered_diff_threshold": 0.001,
                "unanswered_tries_count": 5,
                "use_unanswered": True,
                "try_till_full_success": False,
                "beta_dump_all_json_1": False,
                "beta_dump_all_json_2": False,
                "beta_cgi_params_1": self._append_common_cgi(self._append_cgi(add_cgi)),
                "beta_cgi_params_2": self._append_common_cgi(add_cgi),
                "search_prop_filter": "'UPPER.ApplyBlender.IntentWeight/FRESH' > 0.01",
                "processed_reqs_percent_threshold": 0.7,
            })
            in_ctx.update(info["ctx"])
            test_creation_info = {
                "task_type": "REARRANGE_ACCEPTANCE_2",
                "execution_space": 40 * 1024,  # 40G
                "input_parameters": in_ctx,
                "description": "{} for {}, run#{}, {}".format(prefix, regs, n_run, self.descr.encode("utf-8"))
            }
            tests.append(test_creation_info)
            logging.info("CREATE %s RA2 TEST:\n%s", prefix, json.dumps(test_creation_info, indent=2))
        return tests

    def _common_ra2_input(self, coll, domain, filter=False):
        random_reqs_task_key = "random_reqs_{}_task_id".format(domain.split(".")[-1]) + ("_filter" if filter else "")
        if random_reqs_task_key in self.ctx:
            req_res_id = channel.sandbox.get_task(self.ctx[random_reqs_task_key]).ctx.get('random_queries_resource_id')
        else:
            req_res_id = None
        if RA2_BUILD_PARSER in self.ctx:
            two_ctx_features_diff = channel.sandbox.get_task(self.ctx[RA2_BUILD_PARSER]).ctx.get('out_resource_id')
        else:
            two_ctx_features_diff = None
        checked_beta = utils.get_or_default(self.ctx, rm_params.CheckedBeta)
        if coll == "video" and utils.get_or_default(self.ctx, rm_params.CheckedBetaVideo):
            checked_beta = utils.get_or_default(self.ctx, rm_params.CheckedBetaVideo)
        if coll == "images" and utils.get_or_default(self.ctx, rm_params.CheckedBetaImages):
            checked_beta = utils.get_or_default(self.ctx, rm_params.CheckedBetaImages)
        return {
            "notify_if_finished": "",  # не спамить, когда завершилось корректно
            "beta_host_1": self._get_beta_host(utils.get_or_default(self.ctx, rm_params.SampleBeta), domain),
            "beta_host_2": self._get_beta_host(checked_beta, domain),
            "beta_collection_1": coll,
            "beta_collection_2": coll,
            "random_requests": 1500,
            "threads_count": 32,
            "time_to_kill": 10,
            "parser_binary_resource_id": two_ctx_features_diff,
            "req_resource_id": req_res_id,
            grsr.ScraperProfileName.name: (
                {
                    "search": _WEB_PROFILE,
                    "touchsearch": _WEB_TOUCH_PROFILE,
                    "padsearch": _WEB_TOUCH_PROFILE,
                    "images": "weak_consistency__image__desktop__hamster",
                    "video": "weak_consistency__video__desktop__hamster",
                    "people": _WEB_PROFILE,
                    "touchpeople": _WEB_PROFILE,
                }[coll]
            ),
            sr_params.ScraperOverYtPoolParameter.name: (
                utils.get_or_default(self.ctx, sr_params.ScraperOverYtPoolParameter)
            ),
            ra2.ReleaseMachineModeParameter.name: bool(self.ctx[rm_params.ComponentName.name]),
            ra2.ReleaseMachineComponentNameParameter.name: self.ctx[rm_params.ComponentName.name],
            ra2.ReleaseMachineScopeNumberParameter.name: self.ctx.get(rm_params.ReleaseNum.name),
            ra2.ReleaseMachineRevisionParameter.name: self.ctx.get(rm_const.REVISION_CTX_KEY, ""),
            "send_notification_to_startrek": False,
        }

    def _common_ra2_input_for_batched_mode(self, coll, domains, filter=False):
        random_reqs_task_key_for_domain = {
            dom: "random_reqs_{}_task_id".format(dom.split(".")[-1]) + ("_filter" if filter else "") for dom in domains
        }
        req_res_id_for_domain = {
            dom: (
                channel.sandbox.get_task(self.ctx[key]).ctx.get('random_queries_resource_id')
                if key in self.ctx
                else None
            )
            for dom, key in random_reqs_task_key_for_domain.iteritems()
        }
        if RA2_BUILD_PARSER in self.ctx:
            two_ctx_features_diff = channel.sandbox.get_task(self.ctx[RA2_BUILD_PARSER]).ctx.get('out_resource_id')
        else:
            two_ctx_features_diff = None
        checked_beta = utils.get_or_default(self.ctx, rm_params.CheckedBeta)
        if coll == "video" and utils.get_or_default(self.ctx, rm_params.CheckedBetaVideo):
            checked_beta = utils.get_or_default(self.ctx, rm_params.CheckedBetaVideo)
        if coll == "images" and utils.get_or_default(self.ctx, rm_params.CheckedBetaImages):
            checked_beta = utils.get_or_default(self.ctx, rm_params.CheckedBetaImages)
        return {
            "notify_if_finished": "",  # не спамить, когда завершилось корректно
            "beta_host_1": self._get_beta_host("hamster", "ru"),
            "beta_host_2": self._get_beta_host("hamster", "ru"),
            "beta_collection_1": coll,
            "beta_collection_2": coll,
            "random_requests": 1500,
            "threads_count": 32,
            "time_to_kill": 10,
            "parser_binary_resource_id": two_ctx_features_diff,
            sr_params.ScraperOverYtPoolParameter.name: (
                utils.get_or_default(self.ctx, sr_params.ScraperOverYtPoolParameter)
            ),
            ra2.ReleaseMachineModeParameter.name: bool(self.ctx[rm_params.ComponentName.name]),
            ra2.ReleaseMachineComponentNameParameter.name: self.ctx[rm_params.ComponentName.name],
            ra2.ReleaseMachineScopeNumberParameter.name: self.ctx.get(rm_params.ReleaseNum.name),
            ra2.ReleaseMachineRevisionParameter.name: self.ctx.get(rm_const.REVISION_CTX_KEY, ""),
            "send_notification_to_startrek": False,
            "first_betas_dict": {
                dom: self._get_beta_host(utils.get_or_default(self.ctx, rm_params.SampleBeta), dom)
                for dom in domains
            },
            "second_betas_dict": {
                dom: self._get_beta_host(checked_beta, dom)
                for dom in domains
            },
            "queries_dict": {
                dom: str(res_id)
                for dom, res_id in req_res_id_for_domain.iteritems()
            },
            "req_resource_id": req_res_id_for_domain.values()[0],
        }

    def _get_blender_tests_for_batched_mode(self, n_run=0):
        tests = []
        collections_to_test = [
            TestPlatformParameter.collection for TestPlatformParameter in NEW_RA_BLENDER_TESTS_PLATFORM_PARAMETERS
            if self.ctx.get(TestPlatformParameter.name)
        ]
        run_count = utils.get_or_default(self.ctx, RunCount)
        for prefix, info in REARR_BLENDER_PARAMS.iteritems():
            for test_group in info["tests_groups"]:
                for queries_source, test_params in test_group["test_params"].iteritems():
                    for coll, regions_for_coll in info["collections"].iteritems():
                        regs = [reg for reg in test_group["regs"] if reg in regions_for_coll]
                        if coll in collections_to_test:
                            for test_param in test_params:
                                is_facts = 'facts' in test_param
                                in_ctx = self._common_ra2_input_for_batched_mode(
                                    coll,
                                    [_REGIONS_DATA[reg]["domain"] for reg in regs]
                                )
                                config_attr = "{}_priemka-{}-config-release".format(prefix, test_param)
                                add_cgi = (_PROPS_ONLY_JSON_DUMP_CGI if is_facts else _FAST_JSON_DUMP_CGI) + (
                                    "&waitall=da"
                                    "&timeout=2000000"
                                )
                                in_ctx.update({
                                    "threads_count": 20,
                                    "tries_count": 5,
                                    "notify_if_failed": info["notify_if_failed"] if n_run >= run_count - 1 else "",
                                    "beta_dump_all_json_1": False,
                                    "beta_dump_all_json_2": False,
                                    "beta_cgi_params_1": self._append_common_cgi(self._append_cgi(add_cgi)),
                                    "beta_cgi_params_2": self._append_common_cgi(add_cgi),
                                    "use_unanswered": True,
                                    "unanswered_tries_count": 1,
                                    "try_till_full_success": False,
                                    "unanswered_diff_threshold": 0.3,
                                    "unanswered_sources": (
                                        "IMAGESP:max_unanswer=0.1,"
                                        "VIDEOP:max_unanswer=0.3,"
                                        "ENTITYSEARCH:max_unanswer=0.1,"
                                        "SUGGESTFACTS2:max_unanswer=0.1"
                                    ),
                                    "processed_reqs_percent_threshold": 0.7,
                                    "use_config_from_arcadia": True,
                                    "arcadia_config_path": CONFIG_DIRECTORY + "RA_config_{}".format(config_attr),
                                })
                                for reg in regs:
                                    req_attr = ''
                                    if queries_source == "predefined":
                                        req_attr = "{}_priemka-{}-queries-release=1,locale={reg}".format(
                                            prefix, test_param, reg=reg.lower()
                                        )
                                    elif queries_source == "random":
                                        req_attr = "random_requests=3000,geo_id={}".format(_REGIONS_DATA[reg]["geo_id"])
                                    else:
                                        eh.check_failed("Unknown queries source: {}".format(queries_source))
                                    reqs_resource = apihelpers.get_last_resource_with_attrs(
                                        resource_types.USERS_QUERIES,
                                        attrs=string.parse_attrs(req_attr),
                                        all_attrs=True,
                                    )
                                    if reqs_resource:
                                        in_ctx["queries_dict"][_REGIONS_DATA[reg]["domain"]] = reqs_resource.id
                                        in_ctx["req_resource_id"] = reqs_resource.id
                                in_ctx["random_requests"] = 1500
                                tests.append({
                                    "task_type": 'REARRANGE_ACCEPTANCE_2',
                                    "execution_space": 40 * 1024,  # 40G
                                    "input_parameters": in_ctx,
                                    "description": "ra2-{}-{}-{} for {}, run#{}, {}".format(
                                        prefix, test_param, coll, str(regs), n_run, self.descr.encode("utf-8")
                                    )
                                })
        return tests

    def _get_personalization_ra2_tests_for_batched_mode(self, n_run=0):
        tests = []

        if not utils.get_or_default(self.ctx, LaunchPersonalizationRA2):
            return tests

        if not utils.get_or_default(self.ctx, DebugMode):
            self.set_info(
                "RA2 personalization tests are temporary turned off since they appear to be heavily unstable (UPS-71). "
                "For now they are only available in debug mode"
            )
            return tests

        run_count = utils.get_or_default(self.ctx, RunCount)
        for prefix, info in REARR_OTHER_PARAMS.iteritems():
            regs = info["regs"]
            domains = [_REGIONS_DATA[reg]["domain"] for reg in regs]
            in_ctx = self._common_ra2_input_for_batched_mode("search", domains)
            config_attr = info["ctx"]["config_attr"]
            add_cgi = _FAST_JSON_DUMP_CGI
            in_ctx.update({
                "threads_count": 20,
                "tries_count": 3,
                "notify_if_failed": info["ctx"]["notify_if_failed"] if n_run >= run_count - 1 else "",
                "beta_dump_all_json_1": False,
                "beta_dump_all_json_2": False,
                "beta_cgi_params_1": self._append_common_cgi(self._append_cgi(add_cgi)),
                "beta_cgi_params_2": self._append_common_cgi(add_cgi),
                "use_unanswered": True,
                "unanswered_tries_count": 3,
                "try_till_full_success": False,
                "unanswered_diff_threshold": 0.01,
                "unanswered_sources": (
                    "RTMR:max_unanswer=0.1,"
                    "SAAS_PERS:max_unanswer=0.1,"
                    "QUICK:max_unanswer=0.2"
                ),
                "processed_reqs_percent_threshold": 0.7,
                "use_config_from_arcadia": True,
                "arcadia_config_path": CONFIG_DIRECTORY + "RA_config_{}".format(config_attr),
                ra2.UsePersonalUidsParameter.name: True,
            })
            in_ctx["queries_dict"] = dict()
            for reg in regs:
                req_attr = "random_requests=3000,geo_id={}".format(_REGIONS_DATA[reg]["geo_id"])
                reqs_resource = apihelpers.get_last_resource_with_attrs(
                    resource_types.USERS_QUERIES,
                    attrs=string.parse_attrs(req_attr),
                    all_attrs=True,
                )
                if reqs_resource:
                    in_ctx["req_resource_id"] = reqs_resource.id
                    in_ctx["queries_dict"][_REGIONS_DATA[reg]["domain"]] = str(reqs_resource.id)
            in_ctx["random_requests"] = 3000
            tests.append({
                "task_type": 'REARRANGE_ACCEPTANCE_2',
                "execution_space": 40 * 1024,  # 40G
                "input_parameters": in_ctx,
                "description": "ra2 personalization for {}, run#{}, {}".format(
                    regs, n_run, self.descr.encode("utf-8")
                ),
            })
        return tests

    def _get_quick_tests(self, n_run=0):

        if not utils.get_or_default(self.ctx, LaunchQuickRA2):
            return []

        tests = []

        regs = ['RU']
        domains = [_REGIONS_DATA[reg]["domain"] for reg in regs]
        in_ctx = self._common_ra2_input_for_batched_mode("search", domains)
        add_cgi = _PROPS_QUICK_CGI
        in_ctx.update({
            "threads_count": 20,
            "tries_count": 3,
            "notify_if_failed": "",
            "beta_dump_all_json_1": False,
            "beta_dump_all_json_2": False,
            "beta_cgi_params_1": self._append_cgi(add_cgi),
            "beta_cgi_params_2": add_cgi,
            "use_unanswered": True,
            "unanswered_tries_count": 5,
            "try_till_full_success": False,
            "unanswered_diff_threshold": 0.001,
            "unanswered_sources": (
                "WEB:max_delta=0.02,"
                "VIDEOP:max_delta=0.01,"
                "IMAGESP:max_delta=0.01"
            ),
            "processed_reqs_percent_threshold": 0,
            "use_config_from_arcadia": False,
        })
        in_ctx["queries_dict"] = dict()
        for reg in regs:
            req_attr = "random_requests=3000,geo_id={}".format(_REGIONS_DATA[reg]["geo_id"])
            reqs_resource = apihelpers.get_last_resource_with_attrs(
                resource_types.USERS_QUERIES,
                attrs=string.parse_attrs(req_attr),
                all_attrs=True,
            )
            if reqs_resource:
                in_ctx["req_resource_id"] = reqs_resource.id
                in_ctx["queries_dict"][_REGIONS_DATA[reg]["domain"]] = str(reqs_resource.id)
        in_ctx["random_requests"] = 3000
        tests.append({
            "task_type": 'REARRANGE_ACCEPTANCE_2',
            "execution_space": 40 * 1024,  # 40G
            "input_parameters": in_ctx,
            "description": "ra2 quick for {}, run#{}, {}".format(
                regs, n_run, self.descr.encode("utf-8")
            ),
        })
        return tests

    def _common_rearr_input(self, domain):
        return {
            "notify_if_finished": "",  # не спамить, когда завершилось корректно
            "prod_host": self._get_beta_host(utils.get_or_default(self.ctx, rm_params.SampleBeta), domain),
            "beta_host": self._get_beta_host(utils.get_or_default(self.ctx, rm_params.CheckedBeta), domain),
            "prod_cgi_params": _DEFAULT_CGI,
            "beta_cgi_params": _DEFAULT_CGI,
            "use_random_requests": 0,
            "use_personal_uids": 0,
            "st_priemka_ticket": self.ctx.get("st_priemka_ticket"),
        }

    def fill_context(self):
        svn_info = rm_const.GSID_SVN_RE.search(self.ctx.get('__GSID', ''))
        self.ctx[rm_const.REVISION_CTX_KEY] = svn_info.group("svn_revision") if svn_info else ""

    @staticmethod
    def _to_wiki_format(info):
        if isinstance(info, basestring):
            return info

        body = info["body"]
        heads = [i["key"] for i in info.get("header", [])] or body.keys()
        lines = [" | ".join(["**{}**".format(head) for head in heads])]
        min_depth = min(len(body[h]) for h in heads)
        for i in range(min_depth):
            lines.append(" | ".join([body[h][i] for h in heads]))
        table = "\n".join(["|| {} ||".format(line) for line in lines])
        full_table = "#|\n{}\n|#".format(table).replace(
            _FAIL, "**!!(red){}!!**".format(_FAIL)
        ).replace(
            _UNKNOWN, "**!!(blue){}!!**".format(_UNKNOWN)
        )
        return TASK_LINK_REGEXP.sub('((\\1 ""\\2""))', full_table)

    @staticmethod
    def _highlight(text):
        return (
            TASK_LINK_REGEXP.sub(
                '<a href="\\1">\\2</a>',
                (
                    text
                    .replace(_FAIL, '<b style=\"color:red\">{}</b>'.format(_FAIL))
                    .replace(_OK, '<b style=\"color:green\">{}</b>'.format(_OK))
                )
            )
        )

    def _to_html(self, info):
        if isinstance(info, basestring):
            return self._highlight(info)

        body = info["body"]
        for reg in body:
            hl_items = [self._highlight(item) for item in body[reg]]
            info["body"][reg] = hl_items
        return info

    def _create_rm_proto_event_json(self, status=None):

        style_class_map = {
            _OK: "table-cell-success",
            _FAIL: "table-cell-fail",
        }

        status = status or self.status
        # This is to make sure the crawler event won't come over this one
        # ToDo(ilyaturuntaev): think of a way to do it better
        updated_at = (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).replace(tzinfo=tz.tzutc()).isoformat()
        header_cells = [{"content": "Test Group", "link": "", "styleClass": ""}]
        report_table_rows = []

        region_list = _REGIONS_DATA.keys()

        for region in region_list:
            header_cells.append({
                "content": region.upper(),
                "link": "",
                "styleClass": "",
            })
        header_cells.append({
            "content": "Responsible",
            "link": "",
            "styleClass": "",
        })

        status_map = {
            'FAILURE': 'CRIT',
            'SUCCESS': 'OK',
        }

        for test_group_name in self._GROUPS_ORDER:

            cells = [{"content": test_group_name, "link": "", "styleClass": ""}]

            for region in region_list:
                test_status, link, answer_rate = self._get_result_for_group(test_group_name, region, format_link=False)
                cells.append({
                    "content": "{status} {rate}".format(status=test_status, rate=answer_rate),
                    "link": link,
                    "styleClass": style_class_map.get(test_status, ""),
                })

            cells.append({
                "content": " ".join(
                    [_person_url(p, False) for p in TestAllTdiAndRearrange._RESPONSIBLE[test_group_name]["persons"]] +
                    [_service_url(s, False) for s in TestAllTdiAndRearrange._RESPONSIBLE[test_group_name]["services"]]
                ),
                "link": "",
                "styleClass": "",
            })

            report_table_rows.append({
                "cells": cells
            })

        return [
            {

                "generalData": {
                    "componentName": self.ctx[rm_params.ComponentName.name],
                    "hash": unicode(hash((self.id, status, updated_at))),
                    "referrer": "sandbox_task:{}".format(self.id),
                },
                "taskData": {
                    "taskId": "{}".format(self.id),
                    "status": status,
                    "createdAt": datetime.datetime.utcfromtimestamp(
                        self.timestamp,
                    ).replace(tzinfo=dateutil.tz.tzutc()).isoformat(),
                    "updatedAt": updated_at,
                },
                "acceptanceTestData": {
                    "testResult": {
                        "status": status_map.get(status, 'ONGOING'),
                        "reportTable": {
                            "header": {
                                "cells": header_cells,
                            },
                            "rows": report_table_rows,
                        },
                        "taskLink": lb.task_link(self.id, plain=True),
                        "reportLink": "",
                        "reportMessage": "",
                    },
                    "acceptanceType": "RA2",
                    "scopeNumber": "{}".format(self.ctx.get(rm_params.ReleaseNum.name)),
                    "revision": rm_const.GSID_SVN_RE.search(self.ctx.get('__GSID', '')).group('svn_revision'),
                    "jobName": rm_const.GSID_TE_RE.search(self.ctx.get('__GSID', '')).group('job_name'),
                },
                "customNotifications": [],
            }
        ]

    def _post_rm_proto_event(self, status=None):
        logging.debug("Going to build and post RM proto event (as json)")
        try:
            event_data = self._create_rm_proto_event_json(status=status)
            events_helper.post_proto_events(event_data, already_a_json=True)
        except Exception as e:
            eh.log_exception("Unable to build and send RM proto event", e)

    def _get_beta_host(self, beta_name, domain):
        return (
            "{}.{}".format(beta_name, domain) if beta_name.endswith(".yandex")
            else "{}.yandex.{}".format(beta_name, domain)
        )

    def _get_beta_name(self, beta_name):
        return beta_name.replace(".hamster", "").replace(".yandex", "")


__Task__ = TestAllTdiAndRearrange
