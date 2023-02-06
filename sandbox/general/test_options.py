import json
import os

import yatest.common as yac

from sandbox.projects.devtools.YaMakeYmakeCacheHeater.autocheck_params import DEFAULT_INPUT_PARTITION_PARAMS, DEFAULT_ENV_AUTOCHECK_YA_2_PARAMS
from sandbox.projects.devtools.YaMakeYmakeCacheHeater.autocheck_params import DEFAULT_PARTITION_ARGUMENTS
from sandbox.projects.autocheck.AutocheckBuildParent2.subtask import KVStore
from sandbox.projects.autocheck.AutocheckBuildParent2.partition_options import PartitionOptions
from sandbox.projects.autocheck.lib.builders.ymake import YaBuilder
import sandbox.projects.autocheck.lib.builders.ymake


def get_params(config, index, count):
    params = KVStore(**DEFAULT_INPUT_PARTITION_PARAMS)
    params.projects_partitions_count = count
    params.projects_partition_index = index
    params.autocheck_config_path = config
    return params


def test_autocheck_options():
    return_val = {}

    for config, count in DEFAULT_PARTITION_ARGUMENTS:
        key = '{config}-{count}'.format(config=config, count=count)
        return_val[key] = []

        for index in range(count):
            params = get_params(config, index, count)

            options = PartitionOptions(params, is_comparing_repo=False)
            options.load_config(yac.source_path())

            return_val[key].append(options.as_dict())

    return json.dumps(return_val, sort_keys=True, indent=2)


def test_builder_args(monkeypatch):
    result = []

    def run_process(*args, **kwargs):
        params = {'args': args, 'kwargs': kwargs}
        return json.dumps(params)

    for config, count in DEFAULT_PARTITION_ARGUMENTS:
        for index in range(count):
            logs_resource_path = yac.test_output_path()
            test_output_dir = yac.test_output_path()
            error_file = yac.test_output_path()
            # use_custom_context = (build_mode == BuildMode.ONLY_BUILD) and options.use_custom_context
            log_prefix = 'log'

            with monkeypatch.context() as m:
                m.setattr(sandbox.projects.autocheck.lib.builders.ymake, 'run_process', run_process)
                m.setattr(os, 'environ', DEFAULT_ENV_AUTOCHECK_YA_2_PARAMS)

                params = get_params(config, index, count)

                options = PartitionOptions(params, is_comparing_repo=False)
                options.load_config(yac.source_path())

                builder = YaBuilder(yac.source_path(), build_root=yac.test_output_path('build_root'), output_dir=yac.test_output_path(), ya_binary=yac.source_path("ya"))

                options.make_context_on_distbuild = False  # options.make_context_on_distbuild and build_mode not in [BuildMode.ONLY_BUILD, BuildMode.ONLY_META_GRAPH]

                ya_options = options.make_ya_options(
                    builder.ya_cmd,
                    builder.source_root,
                    builder.build_root,
                    logs_resource_path,
                    test_output_dir,
                    build_threads=0,  # '0' if build_mode in [BuildMode.ONLY_GRAPH, BuildMode.ONLY_META_GRAPH] else None,
                    build_threads_for_distbuild=0,
                    coordinators_filter=options.coordinators_filter,  # options.get_coordinators_filter(build_mode in [BuildMode.ONLY_GRAPH, BuildMode.ONLY_META_GRAPH], self.Context),
                    custom_context=None,  # build_state.context_path if use_custom_context else None,
                    distbs_pool=options.distbs_pool,
                    error_file=error_file,
                    patch_spec=options.arcadia_patch,
                    revision=0,  # revision,
                    streaming_url=None,  # None if build_mode in [BuildMode.ONLY_GRAPH, BuildMode.ONLY_META_GRAPH] else build_state.report_server_url,
                    svn_url=options.checkout_arcadia_from_url,  # svn_url,
                    task_id="task_id",  # self.id,
                )

                proc = builder.build(
                    ya_options,
                    wait_process=True,  # (build_mode != BuildMode.ONLY_GRAPH) or not build_state.async_build_graph,
                    log_prefix=log_prefix,
                    strace=False,  # str(self.path(build_prefix + 'strace.log')) if options.use_strace else False,
                )

                result.append(json.loads(proc.replace(yac.test_output_path(), "<TEST_OUT>").replace(yac.source_path(), "<SOURCE_ROOT>")))

    return json.dumps(result, sort_keys=True, indent=2)
