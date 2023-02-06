import copy

from sandbox.projects.common.constants import constants as common_const
import sandbox.projects.release_machine.components.job_graph.stages.job_graph_element as jg_element
import sandbox.projects.release_machine.components.job_graph.utils as jg_utils
import sandbox.projects.release_machine.components.job_graph.job_data as jg_job_data
import sandbox.projects.release_machine.components.job_graph.job_triggers as jg_job_triggers
import sandbox.projects.release_machine.components.job_graph.job_arrows as jg_arrows
import sandbox.projects.release_machine.core.const as rm_const


class JobGraphElementActionRunAcceptance(jg_element.JobGraphElement):
    def __init__(self, job_params=None, job_arrows=(), parents=()):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.ACTION_RUN_ACCEPTANCE,  # FIX
                "task_name": "CHECK_TASKS_CORRECTNESS",
                "ctx": {
                    "autotesting_ok": True,
                }
            },
        )
        super(JobGraphElementActionRunAcceptance, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )
        self.job_arrows += (
            jg_arrows.ParamsData("tasks_to_check", jg_utils.get_tasks_to_check),
        )
        for parent_params in parents:
            self.job_arrows += (jg_arrows.JobTrigger(**parent_params), )


class JobGraphElementActionRunAcceptanceBranched(JobGraphElementActionRunAcceptance):
    def __init__(self, job_params=None, job_arrows=(), parents=(), frequency=(jg_utils.TestFrequency.LAZY, None)):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.ACTION_RUN_ACCEPTANCE_BRANCHED,
                "should_add_to_db": jg_utils.should_add_to_db_branch,
                "cancel_fallbehind_runs_on_fix": False,
                "frequency": frequency,
            },
        )
        super(JobGraphElementActionRunAcceptanceBranched, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
            parents=parents,
        )
        self.job_arrows += (
            jg_arrows.ParamsData("release_num", jg_utils.get_major_release_number),
        )


class JobGraphElementActionRunAcceptanceTagged(JobGraphElementActionRunAcceptance):
    def __init__(self, job_params=None, job_arrows=(), parents=(), frequency=(jg_utils.TestFrequency.LAZY, None)):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "should_add_to_db": jg_utils.should_add_to_db_trunk,
                "frequency": frequency,
            },
        )
        super(JobGraphElementActionRunAcceptanceTagged, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
            parents=parents,
        )


class JobGraphElementActionRunAcceptanceBranchedScheduled(JobGraphElementActionRunAcceptanceBranched):
    def __init__(self, job_params=None, job_arrows=(), parents=(), frequency=(jg_utils.TestFrequency.LAZY, None)):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "frequency": frequency,
                "job_name_parameter": "SCHEDULED",
            },
        )
        super(JobGraphElementActionRunAcceptanceBranchedScheduled, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
            parents=parents,
        )


class JobGraphElementActionRunAcceptanceBranchedByMarker(JobGraphElementActionRunAcceptanceBranched):
    def __init__(
        self, job_params=None, job_arrows=(), parents=(), frequency=(jg_utils.TestFrequency.CHECK_EACH_COMMIT, None)
    ):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "filter_branches": True,
                "simple_filter": jg_utils.SimpleFilterRegex(commit_message_regex=r'\[ *rm *: *beta *\]'),
                "frequency": frequency,
                "job_name_parameter": "BY_MARKER",
            },
        )
        super(JobGraphElementActionRunAcceptanceBranchedByMarker, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
            parents=parents,
        )


class JobGraphElementTestCommon(jg_element.JobGraphElement):
    def __init__(self, task_name, job_params=None, job_arrows=(), ctx=None, out=None, platform="any"):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.TEST,
                "task_name": task_name,
                "ctx": ctx,
                "out": out,
                "apiargs": {"requirements": {"platform": platform}},
            },
        )
        super(JobGraphElementTestCommon, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )


class JobGraphElementTestBranchCommon(JobGraphElementTestCommon):
    def __init__(self, task_name, job_params=None, job_arrows=(), ctx=None, out=None, platform="any"):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "should_add_to_db": jg_utils.should_add_to_db_branch,
                "cancel_fallbehind_runs_on_fix": False,
            },
        )
        super(JobGraphElementTestBranchCommon, self).__init__(
            task_name=task_name,
            job_params=merged_job_params,
            job_arrows=job_arrows,
            ctx=ctx,
            out=out,
            platform=platform,
        )


class JobGraphElementTestTagCommon(JobGraphElementTestCommon):
    def __init__(self, task_name, job_params=None, job_arrows=(), ctx=None, out=None, platform="any"):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "should_add_to_db": jg_utils.should_add_to_db_trunk,
            },
        )
        super(JobGraphElementTestTagCommon, self).__init__(
            task_name=task_name,
            job_params=merged_job_params,
            job_arrows=job_arrows,
            ctx=ctx,
            out=out,
            platform=platform,
        )


JobGraphElementTestTrunkCommon = JobGraphElementTestTagCommon


class JobGraphElementYappyBetaGenerator(jg_element.JobGraphElement):
    def __init__(self, beta_conf_type, job_params=None, job_arrows=(), ctx=None):
        default_ctx = {
            "beta_conf_type": beta_conf_type,
        }
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.YAPPY_BETA,
                "job_name_parameter": beta_conf_type.upper(),
                "task_name": "GENERATE_YAPPY_BETA",
                "ctx": _merge_ctx(default_ctx, ctx),
                "restart_policy": rm_const.beta_creation_restart_policy,
            }
        )
        super(JobGraphElementYappyBetaGenerator, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )


class JobGraphElementYappyBetaGeneratorTagged(JobGraphElementYappyBetaGenerator):
    def __init__(self, beta_conf_type, job_params=None, job_arrows=(), ctx=None):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "should_add_to_db": jg_utils.should_add_to_db_trunk,
            }
        )
        super(JobGraphElementYappyBetaGeneratorTagged, self).__init__(
            beta_conf_type=beta_conf_type,
            job_params=merged_job_params,
            job_arrows=job_arrows,
            ctx=ctx,
        )


class JobGraphElementYappyBetaGeneratorBranched(JobGraphElementYappyBetaGenerator):
    def __init__(self, beta_conf_type, job_params=None, job_arrows=(), ctx=None):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "should_add_to_db": jg_utils.should_add_to_db_branch,
                "cancel_fallbehind_runs_on_fix": False,
            }
        )
        super(JobGraphElementYappyBetaGeneratorBranched, self).__init__(
            beta_conf_type=beta_conf_type,
            job_params=merged_job_params,
            job_arrows=job_arrows,
            ctx=ctx,
        )
        self.job_arrows += (
            jg_arrows.ParamsData("release_number", jg_utils.get_major_release_number),
        )


class JobGraphElementE2ETest(jg_element.JobGraphElement):
    def __init__(self, job_params=None, job_arrows=(), search_subtype="web", ctx=None, task_name=None):
        default_ctx = {
            "test_id": 1,
            "release_machine_mode": True,
            "allow_data_flags": False,
            "tests_block": None,
            "release": "latest",
            "project_git_base_ref": None,
            "tests_source": "nothing",
            "tests_hash": None,
            "tools": ["hermione-e2e"],
            "platforms": ["desktop", "touch-pad", "touch-phone"],
        }
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.TEST_E2E,
                "job_name_parameter": search_subtype,
                "task_name": task_name or "SANDBOX_CI_WEB4_EXPERIMENTS_RELEASE_RUNNER",
                "should_add_to_db": jg_utils.should_add_to_db_branch,
                "cancel_fallbehind_runs_on_fix": False,
                "ctx": _merge_ctx(default_ctx, ctx),
            }
        )
        super(JobGraphElementE2ETest, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )
        self.job_arrows += (
            jg_arrows.ParamsData("release_number", jg_utils.get_major_release_number),
        )


class JobGraphElementTestXMLSearch(jg_element.JobGraphElement):
    def __init__(self, job_params=None, job_arrows=(), job_name_parameter="", ctx=None):
        default_ctx = {
            "diff_barrier": 0.05,  # 5 percent diff
            "shoots_number": 150,
        }
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.TEST_XML_SEARCH,
                "job_name_parameter": job_name_parameter,
                "should_add_to_db": jg_utils.should_add_to_db_branch,
                "cancel_fallbehind_runs_on_fix": False,
                "task_name": "TEST_XML_SEARCH_2",
                "ctx": _merge_ctx(default_ctx, ctx),
            }
        )
        super(JobGraphElementTestXMLSearch, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )
        self.job_arrows += (
            jg_arrows.ParamsData("release_number", jg_utils.get_major_release_number),
            jg_arrows.GlobalResourceData("queries_plan", "XML_SEARCH_USERS_QUERIES"),
        )


class JobGraphElementTestTdiAndRearr(jg_element.JobGraphElement):
    def __init__(self, job_params=None, job_arrows=()):
        default_ctx = {
            "launch_tdi": False,
            "launch_RA_for_blender_and_video": False,
            "launch_new_RA_for_blender_and_video": True,
            "launch_personalization_RA2": True,
            "launch_new_RA": True,
            "launch_images_RA": True,
            "launch_video_RA": True,
            "launch_videoserp_RA": True,
            "launch_new_RA_for_people": True,
            "launch_new_RA_for_people_wizard": True,
            "launch_new_RA_for_people_vertical": True,
            "seek_queries": True,
            "seek_two_contexts_features_diff_binary": True,
            "sample_beta": "hamster",
            "ignore_passed": True,
        }
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.TEST_ALL_RA2,
                "task_name": "TEST_ALL_TDI_AND_REARRANGE",
                "should_add_to_db": jg_utils.should_add_to_db_branch,
                "cancel_fallbehind_runs_on_fix": False,
                "ctx": default_ctx,
            }
        )
        super(JobGraphElementTestTdiAndRearr, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )
        if not job_arrows:
            self.job_arrows += (
                jg_job_triggers.JobTriggerGenerateBeta(
                    parent_job_data=[
                        jg_job_data.ParentDataCtx(
                            input_key="checked_beta",
                            output_key="beta_name",
                            transform=lambda x, params: "{}.hamster".format(x),
                        )
                    ],
                    job_name_parameter="WEB",
                ),
            )
        self.job_arrows += (
            jg_arrows.ParamsData("release_number", jg_utils.get_major_release_number),
        )


class JobGraphElementLaunchMetrics(jg_element.JobGraphElement):

    def _prepare_job_params(self, search_subtype, job_params, job_name_parameter, ctx):
        default_ctx = {
            "autoclicker_metric_name": "diff-2-serps-empty-or-failed-5",
            "autoclicker_retry_count": 4,
            "enable_autoclicker": True,
            "custom_template_name": "common.json",
            "metrics_mode_type": "release_machine",
            "search_subtype": search_subtype,
        }
        if search_subtype == "web":
            default_ctx.update({
                "launch_template_quota": "web-ranking-runtime",
                "run_findurl": True,
            })
        if search_subtype == "news":
            default_ctx.update({
                "scraper_over_yt_pool": "news",
                "autoclicker_metric_name": "empty-or-failed",
                "launch_template_quota": "news",
                "run_findurl": False,
            })
        elif search_subtype == "images":
            default_ctx.update({
                "launch_template_quota": "images-ranking",
            })
        elif search_subtype == "video":
            default_ctx.update({
                "launch_template_quota": "video-quality",
            })
        elif search_subtype == "music":
            default_ctx.update({
                "scraper_over_yt_pool": "production_music_search",
                "autoclicker_metric_name": "empty-or-failed",
                "launch_template_quota": "music-search",
                "run_findurl": False,
            })

        return jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.LAUNCH_METRICS,
                "job_name_parameter": job_name_parameter or search_subtype.upper(),
                "task_name": "LAUNCH_METRICS",
                "should_add_to_db": jg_utils.should_add_to_db_branch,
                "cancel_fallbehind_runs_on_fix": False,
                "frequency": (jg_utils.TestFrequency.LAZY, None),
                "ctx": _merge_ctx(default_ctx, ctx),
            },
        )

    def __init__(
        self,
        search_subtype="web",
        job_params=None,
        job_arrows=(),
        job_name_parameter="",
        ctx=None,
        release_number_default=True,
    ):

        merged_job_params = self._prepare_job_params(search_subtype, job_params, job_name_parameter, ctx)

        super(JobGraphElementLaunchMetrics, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )

        if release_number_default:
            self.job_arrows += (
                jg_arrows.ParamsData("release_number", jg_utils.get_major_release_number),
            )


class JobGraphElementTrunkWaiter(jg_element.JobGraphElement):
    def __init__(self, job_params=None, job_arrows=()):
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.WAIT_TRUNK,
                "task_name": "WAIT_TRUNK_DB",
                "should_add_to_db": jg_utils.should_add_to_db_branch,
                "cancel_fallbehind_runs_on_fix": False,
                "frequency": (jg_utils.TestFrequency.LAZY, None),
            },
        )
        super(JobGraphElementTrunkWaiter, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )
        self.job_arrows += (
            jg_arrows.ParamsData("release_number", jg_utils.get_major_release_number),
        )


def _merge_ctx(default_ctx, ctx):
    full_ctx = copy.deepcopy(default_ctx)
    if ctx:
        full_ctx.update(ctx)
    return full_ctx


class JobGraphElementBaseMetaTest(jg_element.JobGraphElement):
    def __init__(self, task_name, job_params, job_arrows, ctx, out=None, platform="any"):
        default_ctx = {
            common_const.USE_AAPI_FUSE: True,
            common_const.CHECK_RETURN_CODE: True,  # Report about any infrastructure error directly.
            common_const.FAILED_TESTS_CAUSE_ERROR: False,  # Report about failed tests indirectly via results.json.
            common_const.BUILD_SYSTEM_KEY: common_const.SEMI_DISTBUILD_BUILD_SYSTEM,
            "junit_report": True,
            "test": True,
        }

        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.META_TEST,
                "task_name": task_name,
                "test_type": jg_utils.TestType.META_TEST,
                "should_add_to_db": self.should_add_to_db,
                "ctx": _merge_ctx(default_ctx, ctx),
                "out": out,
                "apiargs": {"requirements": {"platform": platform}},
                "metatest_binary_search": True,
            },
        )

        super(JobGraphElementBaseMetaTest, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )

    @property
    def should_add_to_db(self):
        return jg_utils.should_add_to_db_trunk


class JobGraphElementMetaTestBranched(JobGraphElementBaseMetaTest):
    @property
    def should_add_to_db(self):
        return jg_utils.should_add_to_db_branch

    def __init__(
        self,
        task_name="KOSHER_YA_MAKE",
        job_params=None,
        job_arrows=(),
        ctx=None,
        out=None,
        platform="linux",
    ):
        super(JobGraphElementMetaTestBranched, self).__init__(task_name, job_params, job_arrows, ctx, out, platform)

        self.job_arrows += (
            jg_job_triggers.JobTriggerNewTag(
                parent_job_data=(
                    jg_job_data.ParentDataOutput(
                        input_key=common_const.ARCADIA_URL_KEY,
                        output_key=common_const.ARCADIA_URL_KEY,
                    ),
                ),
            ),
        )


class JobGraphElementMetaTestTrunk(JobGraphElementBaseMetaTest):
    def __init__(
        self,
        task_name="KOSHER_YA_MAKE",
        job_params=None,
        job_arrows=(),
        ctx=None,
        out=None,
        platform="linux",
    ):
        super(JobGraphElementMetaTestTrunk, self).__init__(task_name, job_params, job_arrows, ctx, out, platform)

        self.job_arrows += (
            jg_arrows.ParamsData(
                input_key=common_const.ARCADIA_URL_KEY,
                transform=lambda x, rm_config: "{svn_ssh_url}/arcadia@{revision}".format(
                    svn_ssh_url=x.svn_ssh_url,
                    revision=x.revision,
                ),
            ),
        )


class JobGraphElementTrunkMetaTestCodeInBranch(JobGraphElementBaseMetaTest):
    @property
    def should_add_to_db(self):
        return jg_utils.should_add_to_db_branch

    def __init__(
        self,
        task_name="KOSHER_YA_MAKE",
        job_params=None,
        job_arrows=(),
        ctx=None,
        out=None,
        platform="linux",
    ):
        default_ctx = {
            # don't use SEMI_DISTBUILD_BUILD_SYSTEM because we make more 1500 requests to hamster
            common_const.BUILD_SYSTEM_KEY: common_const.YMAKE_BUILD_SYSTEM,
        }
        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "ctx": _merge_ctx(default_ctx, ctx),
            }
        )
        super(JobGraphElementTrunkMetaTestCodeInBranch, self).__init__(
            task_name=task_name,
            job_params=merged_job_params,
            job_arrows=job_arrows,
            ctx=ctx,
            out=out,
            platform=platform
        )


def search_integration_env(x, tld, soy_type="scraper"):
    return (
        "BETA_HOST={beta_url}.{tld} "
        "{soy_mode} {soy_map_op_type} {oauth_token}"
    ).format(
        beta_url=x,
        tld=tld,
        soy_mode="SOY_MODE=1",
        soy_map_op_type="SOY_MAP_OP_TYPE={}".format(soy_type),
        oauth_token="OAUTH_TOKEN='$(vault:value:SEARCH-RELEASERS:common_release_token)'"
    )


def search_integration_env_tld(x, params):
    return search_integration_env(x, 'ru')


def search_integration_env_tld_soy_http(x, params):
    return search_integration_env(x, 'ru', 'http')


def search_integration_env_ab(testid, params):
    return " ".join([
        search_integration_env("hamster", "yandex.ru"),
        "EXP_CONFS=testing",
        "TEST_ID={}".format(testid)
    ])


class JobGraphElementSearchIntegrationBase(JobGraphElementBaseMetaTest):
    def __init__(
        self,
        task_name="KOSHER_YA_MAKE",
        job_name_parameter="SEARCH_INTEGRATION",
        job_params=None,
        job_arrows=(),
        ctx=None,
        frequency=(jg_utils.TestFrequency.LAZY, None),
    ):
        default_ctx = {
            "targets": "search/integration_tests",
            "test": True,
            "disable_test_timeout": True,
            # don't use SEMI_DISTBUILD_BUILD_SYSTEM because we make more 1500 requests to hamster
            common_const.BUILD_SYSTEM_KEY: common_const.YMAKE_BUILD_SYSTEM,
            "binary_executor_release_type": "stable",
        }

        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "should_add_to_db": self.should_add_to_db,
                "frequency": frequency,
                "job_name_parameter": job_name_parameter,
            },
        )

        super(JobGraphElementSearchIntegrationBase, self).__init__(
            task_name=task_name,
            job_params=merged_job_params,
            job_arrows=job_arrows,
            ctx=_merge_ctx(default_ctx, ctx),
        )

    @property
    def should_add_to_db(self):
        return jg_utils.should_add_to_db_trunk


class JobGraphElementSearchIntegrationTestidTest(JobGraphElementSearchIntegrationBase):
    def __init__(
        self,
        task_name="KOSHER_YA_MAKE",
        job_name_parameter="SEARCH_INTEGRATION",
        job_params=None,
        job_arrows=(),
        ctx=None,
        frequency=(jg_utils.TestFrequency.CHECK_EACH_COMMIT, None),
    ):
        super(JobGraphElementSearchIntegrationTestidTest, self).__init__(
            task_name=task_name,
            job_name_parameter=job_name_parameter,
            job_params=job_params,
            job_arrows=job_arrows,
            ctx=ctx,
            frequency=frequency,
        )

        self.job_arrows += (
            jg_job_triggers.JobTriggerBuild(
                parent_job_data=(
                    jg_job_data.ParentDataOutput(
                        "env_vars",
                        "testid",
                        transform=search_integration_env_ab,
                    ),
                ),
            ),
        )

    @property
    def should_add_to_db(self):
        return jg_utils.should_add_to_db_trunk


class JobGraphElementSearchIntegrationBetaUrlTest(JobGraphElementSearchIntegrationBase):
    def __init__(
        self,
        task_name="KOSHER_YA_MAKE",
        job_name_parameter="SEARCH_INTEGRATION_TEST",
        job_name_parameter_beta="beta",
        job_params=None,
        job_arrows=(),
        ctx=None,
        frequency=(jg_utils.TestFrequency.LAZY, None),
    ):
        super(JobGraphElementSearchIntegrationBetaUrlTest, self).__init__(
            task_name=task_name,
            job_name_parameter=job_name_parameter,
            job_params=job_params,
            job_arrows=job_arrows,
            ctx=ctx,
            frequency=frequency,
        )

        self.job_arrows += (
            jg_job_triggers.JobTriggerGenerateBeta(
                job_name_parameter=job_name_parameter_beta,
                parent_job_data=(
                    jg_job_data.ParentDataOutput(
                        input_key="env_vars",
                        output_key="new_beta_url",
                        transform=search_integration_env_tld,
                    )
                )
            ),
        )

    @property
    def should_add_to_db(self):
        return jg_utils.should_add_to_db_branch


class JobGraphElementRunIceFlameBase(jg_element.JobGraphElement):

    def __init__(self, config_file="", job_params=None, job_arrows=(), ctx=None):

        default_ctx = {
            "iceflame_config_source": "file" if config_file else "input_json",
            "iceflame_config_file": config_file,
            "release_machine_mode": True,
            "iceflame_command_run_options_json": {
                "remote_collector_options": {
                    "analyze_inplace": True,
                    "build_flamegraph": True,
                },
            },
        }

        merged_job_params = jg_utils.merge_job_params(
            job_params,
            {
                "job_type": rm_const.JobTypes.ICEFLAME,
                "task_name": "RUN_ICE_FLAME",
                "ctx": _merge_ctx(default_ctx, ctx),
            },
        )

        super(JobGraphElementRunIceFlameBase, self).__init__(
            job_params=merged_job_params,
            job_arrows=job_arrows,
        )


class JobGraphElementRunIceFlame(JobGraphElementRunIceFlameBase):

    RELEASE_MACHINE_DEFAULT_YAV_SECRET = "sec-01ejz9hcr8tq4mmwga719ecgt0"
    SECRET_DEFAULT_SSH_KEY_NAME = "ssh_key"
    SECRET_DEFAULT_SANDBOX_TOKEN_NAME = "common_release_token"
    SECRET_DEFAULT_NANNY_TOKEN_NAME = "common_release_token"

    def __init__(
        self,
        config_file="",
        job_params=None,
        job_arrows=(),
        ctx=None,
    ):

        default_ctx = {
            "ssh_login": "robot-srch-releaser",
            "ssh_key_secret": "{}#{}".format(
                self.RELEASE_MACHINE_DEFAULT_YAV_SECRET,
                self.SECRET_DEFAULT_SSH_KEY_NAME,
            ),
            "sandbox_token_secret": "{}#{}".format(
                self.RELEASE_MACHINE_DEFAULT_YAV_SECRET,
                self.SECRET_DEFAULT_SANDBOX_TOKEN_NAME,
            ),
            "nanny_token_secret": "{}#{}".format(
                self.RELEASE_MACHINE_DEFAULT_YAV_SECRET,
                self.SECRET_DEFAULT_NANNY_TOKEN_NAME,
            ),
        }

        super(JobGraphElementRunIceFlame, self).__init__(
            config_file=config_file,
            job_params=job_params,
            job_arrows=job_arrows,
            ctx=_merge_ctx(default_ctx, ctx),
        )
