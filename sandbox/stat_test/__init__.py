"""
Utilites for yabs-stat performance test
"""
import abc
import logging
import os
import random
import re
import time
import itertools

from collections import namedtuple, defaultdict

from sandbox.common.errors import TaskFailure, TaskError

from sandbox.sandboxsdk import process

from sandbox.projects.common.yabs.server import requestlog
from sandbox.projects.common.yabs.server.util.libs.request_parser import HTTPRequest

from sandbox.projects.yabs.qa.sut.utils import ListContext
from sandbox.projects.yabs.qa.utils import general as general_qa_utils


class AbstractStatPerformanceTaskAdapter(object):
    """Should be subclassed by the task"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set_info(self, info):
        pass

    @abc.abstractmethod
    def get_d_planner(self):
        pass

    @abc.abstractmethod
    def get_d_executor(self, request_count=None):
        pass


LogGenSettings = namedtuple(
    'LogGenSettings',
    [
        'stat_shard',
        'stat_custom_env',
        'stat_store_access_log',

        'turl_custom_env',
        'turl_store_access_log',

        'meta_mode',
        'meta_custom_env',
        'meta_store_access_log',
        'meta_store_request_log',

        'freeze',
    ],
)


def make_request_log(
        task_adapter,
        d_plan_path,
        cached_stub,
        settings,
        yabs_server_factory,
        provide_bases,
):

    d_executor_path = task_adapter.get_d_executor().path

    null_stub = yabs_server_factory.create_null_stub({'caas', 'bigb_user_storage', 'yacofast_ssp'})

    stat = yabs_server_factory.create_stat(
        log_requests=True,
        shard=settings.stat_shard,
        custom_env=settings.stat_custom_env,
        store_access_log=settings.stat_store_access_log,
        backends=[null_stub],
    )

    meta = yabs_server_factory.create_meta(
        settings.meta_mode,
        backends=[cached_stub, null_stub, stat],
        custom_env=settings.meta_custom_env,
        store_access_log=settings.meta_store_access_log,
        store_request_log=settings.meta_store_request_log,
    )

    servers = [meta, stat]

    with ListContext(servers) as s:
        provide_bases(*s)

    # Start stat and meta once again.
    # Otherwise they complain about resets on dead keepalive connections.
    # FIXME Set longer keepalive timeouts in testing configs and start meta+stat only once.
    with null_stub, ListContext(servers) as s:
        # wait until bases on stat and meta are ready
        for server in s:
            server.wait_ping()

        if settings.freeze:
            _freeze(task_adapter.set_info, meta, d_plan_path, d_executor_path)
            raise RuntimeError("We should never get here, this is a bug")
        # We need quite exotic d-executor options here
        # FIXME??  refactor DolbilkaExecutor and use it here (?)

        # We should send each request once. No limits in d-executer parameters.
        cmdline = [
            d_executor_path,
            '--plan-file', d_plan_path,
            '--replace-port', str(meta.port),
            '--simultaneous', '16',
            '--mode', 'finger',
            '--keep-alive'
        ]
        meta.use_component(lambda: process.run_process(cmdline))  # We need meta.usage_impacts filled

    meta.check_access_log(
        ext_sharded={},
        quantiles={90, 99},
        error_rate_thr=0.01,
        request_error_rate_thr=0.06,
        ext_error_rate_thr=0.03,  # FIXME: increase timeouts in test configs
        ignore_handlers={
            'status', 'resource', 'ping', 'media',
            'count',
            'unknown',  # TODO What are they doing here?
            'metadsp',  # TODO 20% 4xx errors ??
            'setud',    # TODO Also lost of 4xx
            'vmap',     # TODO All 4xx
            'solomon_stats_spack',  # TODO temporary ignore new location BSSERVER-12291
        },
        ignore_ext={
            'bsbts_all', 'bigb_rf_balancer', 'bigb_user_storage', 'market', 'count', 'saas_location',
            'rtcrypta', 'rtmr', 'new_saas_location', 'pnocsy', 'rtb_cache', 'pcode_renderer',
            'stat_dict',
            'market_recommend', 'market_report', 'news_recommend',
            'uaas', 'daemon_tvm_client',
            'mtsdsp', 'upravel', 'adlook', 'vinia', 'adriver', 'targetix', 'unity', 'beeline', 'tinkoff', 'criteo', 'rutarget', 'sociomantic', 'yacofast_ssp', 'laas',
            'an_to_yabs_redirect_bad',  # @astkachev remove ignorance of this ext call after BSSERVER-16473
            'adv_machine_knn',  # remove after BSSERVER-16586
            'adv_machine_cat_engine',  # remove after BSSERVER-16586
            'adv_machine_offer_online_quorums',  # remove after BSSERVER-16586
            'yabs_banner_models_gpu',  # remove after BSSERVER-17951
            'panther',  # remove after BSSERVER-22489
        },
    )

    cached_stub.check_access_log(
        broken_threshold=0.04,
        broken_thresholds={
            'awaps': 0.1,
            'new_saas_location': 0.1,
            'pnocsy': 0.9,
            'rtb_cache': 1,
            'pcode_renderer': 1,
            'rtcrypta': 0.2,  # TODO maybe stricter
            'rtmr': 0.5,  # TODO maybe stricter
            'yacofast': 0.5,
            'yacofast_lite': 0.25,
            'yacoland': 0.2,
        }
    )

    return stat.get_phantom_log_path(stat.LOG_REQUEST), meta.usage_impacts


ShootSettings = namedtuple(
    'ShootSettings',
    [
        'request_regexp_str',
        'content_fraction',

        'shard',
        'custom_env',
        'store_access_log',

        'run_perf',
        'loop_count',
        'no_run_once',
        'freeze',
    ],
)


StatPerformanceResults = namedtuple('TestResults', ['stat_d_plan', 'results', 'perf_data_paths', 'stat_usage_impacts'])


def run(
    stat_request_log_path,
    task_adapter,
    settings,
    yabs_server_factory,
    provide_bases,
):
    stpd_path, request_count = _make_stpd(
        stat_request_log_path,
        settings.request_regexp_str,
        settings.content_fraction,
        task_adapter.set_info,
    )

    d_planner = task_adapter.get_d_planner()

    use_loop_count = settings.loop_count is not None and settings.loop_count > 0
    d_executor = task_adapter.get_d_executor(request_count * settings.loop_count if use_loop_count else None)

    null_stub = yabs_server_factory.create_null_stub({'caas', 'bigb_user_storage'})

    stat = yabs_server_factory.create_stat(
        shard=settings.shard,
        custom_env=settings.custom_env,
        store_access_log=settings.store_access_log,
        run_perf=settings.run_perf,
        backends=[null_stub],
    )

    stat_d_plan = d_planner.create_plan(
        stpd_path,
        loader_type='phantom',
        host='127.0.0.1',  # avoid subtle v4/v6 issues
        port=stat.port
    )

    with stat:
        provide_bases(stat)
        if settings.freeze:
            stat.wait_ping()
            _freeze(task_adapter.set_info, stat, stat_d_plan, d_executor.path)
            # we never get here
    deadline = time.time() + 7200  # FIXME check time per each session and fail early

    perf_data_paths = []

    def dolbilka_finish_callback(session):
        if settings.run_perf:
            if session != len(perf_data_paths):
                raise RuntimeError(
                    "Unexpected dolbilka session index {} (instead of {})".format(session, len(perf_data_paths))
                )
            perf_data_filename = 'perf.data.{}'.format(session)
            os.rename('perf.data', perf_data_filename)
            logging.info('perf.data moved to %s', perf_data_filename)
            perf_data_paths.append(perf_data_filename)

        if (session != d_executor.sessions + 1) and (time.time() > deadline):
            raise TaskFailure(
                "Total time limit for dolbilka sessions exceeded."
                "This is most likely caused by SEVERE degradation of yabs-server performance or/and start time."
            )

    with null_stub:
        # d_executor will call wait_ping in use_component
        results = d_executor.run_sessions(
            stat_d_plan,
            stat,
            callback=dolbilka_finish_callback,
            run_once=not settings.no_run_once,
            save_answers=False,
        )

    stat.check_access_log(
        ext_sharded={},
        quantiles={50, 90, 99},
        error_rate_thr=0.02,
        request_error_rate_thr=0.01,
        ext_error_rate_thr=2.0,  # suppress check
        ignore_handlers={'ping', 'pmatch', 'content', 'rank', 'count'},
        ignore_ext={'count'},
    )

    return StatPerformanceResults(
        stat_d_plan=stat_d_plan,
        results=results,
        perf_data_paths=perf_data_paths,
        stat_usage_impacts=stat.usage_impacts,
    )


PerfOut = namedtuple('PerfOut', ['path', 'descr'])


def process_perf_results(flamegraph_dir, stat_performance_results):
    shoot_results = stat_performance_results.results
    perf_data_paths = stat_performance_results.perf_data_paths

    if not shoot_results:
        logging.info("No shoot results, will not process perf data")
        return {}

    best_session_idx = max(xrange(len(shoot_results)), key=lambda i: shoot_results[i]['rps'])
    data_path = os.path.abspath(perf_data_paths[best_session_idx])

    perf_top_out = _perf('report', data_path)
    perf_script_out = _perf('script', data_path)

    stackcollapse_out = PerfOut(path='perf.script.collapsed', descr='yabs-server perf stack-collapse')
    _run_perf_pipeline_tool(
        ['perl', os.path.join(flamegraph_dir, 'stackcollapse-perf.pl'), perf_script_out.path],
        out_path=stackcollapse_out.path,
    )

    flamegraph_out = PerfOut(path='perf.svg', descr='yabs-server flamegraph')
    _run_perf_pipeline_tool(
        ['perl', os.path.join(flamegraph_dir, 'flamegraph.pl'), '--hash', stackcollapse_out.path],
        flamegraph_out.path,
    )

    return {
        'perf_top_txt_id': perf_top_out,
        'perf_script_txt_id': perf_script_out,
        'perf_script_collapsed_id': stackcollapse_out,
        'perf_svg_id': flamegraph_out,
    }


def _make_stpd(
        request_log_path,
        request_regexp_str,
        content_fraction,
        set_info,
        bad_rate_threshold=0.0022,
        client_error_threshold=0.002,
):
    request_regexp = re.compile(request_regexp_str)

    logging.info("Processing yabs-stat request log")
    stpd_path = request_log_path + '.stpd'

    total_good_size = 0

    unwritten_request_codes = dict()
    written_request_codes = dict()

    with open(request_log_path) as req_log, open(stpd_path, 'w') as stpd:
        for request, hdr_tail in requestlog.iterate(req_log):
            parsed_request = HTTPRequest(request)
            if parsed_request.handler == 'ping':
                continue
            if request_regexp.match(request) is None:
                continue
            if random.random() > content_fraction and parsed_request.handler in ('content', 'write_wide', 'get_data'):
                continue
            request_key = (parsed_request.headers.get('x-yabs-request-id'), parsed_request.handler)

            code = hdr_tail[2]
            if general_qa_utils.is_bad_http_code(code):
                if request_key not in written_request_codes:
                    unwritten_request_codes[request_key] = code
            else:
                if request_key in written_request_codes:
                    logging.warning("Skipping duplicate write of request with key %s", request_key)
                    continue
                requestlog.write_stpd(stpd, request, 0)
                written_request_codes[request_key] = code
                unwritten_request_codes.pop(request_key, None)

                total_good_size += len(request)

    requests_by_code = defaultdict(int)
    for code in itertools.chain(unwritten_request_codes.itervalues(), written_request_codes.itervalues()):
        requests_by_code[code] += 1

    set_info(
        "Request codes in yabs-stat log:\n" +
        '\n'.join('{}: {}'.format(code, requests_by_code[code]) for code in sorted(requests_by_code))
    )
    total_count = len(written_request_codes) + len(unwritten_request_codes)

    client_error_count = sum(count for code, count in requests_by_code.iteritems() if general_qa_utils.is_http_client_error(code))

    if client_error_count >= (client_error_threshold * total_count):
        raise TaskFailure(
            "Cannot shoot: too many 4xx codes in generated yabs-stat log ({} out of {})".format(
                client_error_count, total_count
            )
        )

    if len(unwritten_request_codes) >= (bad_rate_threshold * total_count):
        raise TaskError(
            "Cannot shoot: too many bad requests in generated yabs-stat log ({} out of {})".format(
                len(unwritten_request_codes), total_count
            )
        )
    set_info("Average request size for shooting yabs-stat: {} bytes".format(total_good_size / total_count))
    return stpd_path, len(written_request_codes)


def _freeze(set_info, service, d_plan_file, d_executor_path):
    msg = (
        "Task frozen for 10 hours.\n"
        "{sname} port: {port}\n"
        "Command line to start server: {cmdline}\n"
        "Dolbilka plan: {d_plan}\n"
        "Dolbilka executor: {d_executor}\n"
    ).format(
        sname=service.name,
        port=service.port,
        cmdline=service.get_manual_cmdline(),
        d_plan=d_plan_file,
        d_executor=d_executor_path
    )
    set_info(msg)
    time.sleep(60 * 60 * 10)
    raise TaskError("Task was required to freeze, not to shoot")


def _run_perf_pipeline_tool(cmdline, out_path):
    with open(out_path, 'w') as outfile:
        logging.info("Running %s", ' '.join(cmdline))
        process.run_process(
            cmdline,
            stdout=outfile,
            outputs_to_one_file=False,
            log_prefix='.'.join(os.path.basename(_) for _ in cmdline[:2])
        )


def _perf(cmd, data_path):
    out = PerfOut(path='perf.{}.txt'.format(cmd), descr='yabs-server perf {} output'.format(cmd))
    _run_perf_pipeline_tool(['perf', cmd, '-i', data_path], out.path)
    return out
