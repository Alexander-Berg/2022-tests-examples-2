import datetime as dt
import os
import typing as tp
from click.testing import CliRunner

import pytest

import logos.libs.conf as conf
import logos.libs.conf.enums.common as conf_enums
import logos.libs.config as config
import logos.libs.core as logos  # noqa
import logos.libs.reactor_runner.autorun as autorun
import logos.libs.reactor_runner.click_runner as click_runner
import logos.libs.reactor_runner.rdao as rdao
import logos.libs.reactor_runner.robj_builder as robj_builder
import logos.libs.reactor_runner.runner as reactor_runner
import logos.libs.reactor_runner.ut.lib.test_env as runner_test_env
import logos.logs as logs
import logos.projects.ads.graph as graph
import sandbox.projects.ads.infra.logos_preprod_runner.lib as preprod_runner

TEST_RELEASE_ID = "test-release"


class MockYTLogTypeFacade(autorun.AbstractYTLogTypeFacade):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        pass

    def link(
            self,        # type: autorun.AbstractYTLogTypeFacade
            table_from,  # type: logos.log_type.BaseTable
            table_to,    # type: logos.log_type.BaseTable
    ):  # type: (...) -> None
        pass

    def exists(
            self,      # type: autorun.AbstractYTLogTypeFacade
            log,       # type: tp.Type[logos.log_type.BaseLog]
            dt,        # type: dt.datetime
    ):  # type: (...) -> bool
        return True

    def get_all_tables(
        self,  # type: autorun.AbstractYTLogTypeFacade
        log    # type: tp.Type[logos.log_type.DatedLog]
    ):  # type: (...) -> tp.List[tp.Tuple[tp.Type[logos.log_type.DatedLog], tp.Optional[dt.datetime]]]
        return []

    def make_empty_log(
        self,      # type: autorun.AbstractYTLogTypeFacade
        log,       # type: tp.Type[logos.log_type.BaseLog]
        dt,        # type: dt.datetime
        schema=None,    # type: tp.Optional[tp.List[tp.Dict[str, str]]]
    ):
        pass


@pytest.fixture
def mock_yt_facade(monkeypatch):
    monkeypatch.setattr(autorun, "YTLogTypeFacade", MockYTLogTypeFacade)


@pytest.fixture
# @pytest.mark.usefixtures(runner_test_env.mock_reactor_client)
def runner():
    logos_conf = config.LogosConfig(
        graph_type=conf_enums.AqinfraGraphs.PREPROD,
        release_id=TEST_RELEASE_ID,
        tasks_conf=conf.load_tasks_configuration(
            graph.TASK_CONF, graph.PRODUCTION_TASKS),
        release_conf=graph.RELEASE_CONF,
    )
    obj_builder = robj_builder.ReactorObjectBuilder(
        runner_conf=logos_conf.release_conf,
        external_log_type_to_rpath=logs.EXTERNAL_LOGS_ARTIFACTS
    )
    reactor_dao = rdao.ReactorDAO(
        client=runner_test_env.mock_reactor_client,
        reactor_obj_builder=obj_builder
    )
    runner = reactor_runner.ReactorGraphRunner(reactor_dao=reactor_dao)
    return runner


def test_default_cli_works(runner, mock_yt_facade):
    args = preprod_runner.make_run_tasks_cli(
        None,
        dt.datetime(2021, 3, 2),
        TEST_RELEASE_ID,
        "schedule_file"
    )
    args.append("--dry-run")
    os.environ[click_runner.GraphEntryPoint.OAUTH_TOKEN] = "token"
    context = click_runner.Context(
        tasks_per_cluster=graph.PRODUCTION_TASKS,
        external_artifact_map=logs.EXTERNAL_LOGS_ARTIFACTS,
        tasks_conf=conf.load_tasks_configuration(graph.TASK_CONF, graph.PRODUCTION_TASKS),
        release_conf=graph.RELEASE_CONF,
        runner=runner,
    )
    CliRunner().invoke(click_runner.cli, args, obj=context, catch_exceptions=False)
