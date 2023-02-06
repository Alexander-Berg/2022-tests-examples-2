import logging
import os

from collections import defaultdict

from sandbox.common.fs import get_unique_file_name
from sandbox.projects.common.yabs.server import requestlog
from sandbox.projects.common.yabs.server.util.libs.request_parser import HTTPRequest


logger = logging.getLogger(__name__)


def split_request_log(request_log_path, split_by_handlers):
    request_count = 0
    splitted_request_log_path = get_unique_file_name(os.path.dirname(request_log_path), 'splitted_request_log')
    with open(request_log_path) as req_log, open(splitted_request_log_path, 'wb') as splitted_request_log_file:
        for request, hdr_tail in requestlog.iterate(req_log):
            if HTTPRequest(request).handler in split_by_handlers:
                requestlog.write(splitted_request_log_file, request, hdr_tail)
                request_count += 1

    return splitted_request_log_path, request_count


def do_sort_request_log(request_log_path):
    handlers = set()
    requests_by_key = defaultdict(list)
    with open(request_log_path) as req_log:
        for request, hdr_tail in requestlog.iterate(req_log):
            parsed_request = HTTPRequest(request)
            if parsed_request.handler == 'ping':
                continue
            handlers.add(parsed_request.handler)
            request_key = (parsed_request.headers.get('x-yabs-request-id'), parsed_request.handler)
            requests_by_key[request_key].append((request, hdr_tail))

    sorted_request_log_path = request_log_path + '.sorted'
    sorted_keys = sorted(requests_by_key.keys())
    with open(sorted_request_log_path, 'wb') as sorted_request_log_file:
        for key in sorted_keys:
            for request, hdr_tail in requests_by_key[key]:
                requestlog.write(sorted_request_log_file, request, hdr_tail)

    return sorted_request_log_path, handlers


def check_meta_access_log(meta_module):
    meta_module.get_server_backend_object().check_access_log(
        ext_sharded={},
        quantiles={90, 99},
        error_rate_thr=0.01,
        request_error_rate_thr=0.2,
        ext_error_rate_thr=0.03,  # FIXME: increase timeouts in test configs
        ignore_handlers={
            'status', 'resource', 'ping', 'media',
            'count',
            'unknown',  # TODO What are they doing here?
            'metadsp',  # TODO 20% 4xx errors ??
            'setud',    # TODO Also lost of 4xx
            'vmap',     # TODO All 4xx
            'solomon_stats_spack',  # TODO temporary ignore new location BSSERVER-12291
            'solomon_stats',  # TODO temporary ignore new location BSSERVER-12291
        },
        ignore_ext={
            'awaps',
            'adv_machine', 'bsbts_all', 'bigb_balancer', 'bigb_rf_balancer', 'bigb_user_storage', 'market', 'count', 'saas_location',
            'rtcrypta', 'rtmr', 'new_saas_location', 'rtb_proxy', 'pnocsy', 'rtb_cache',
            'rtb_cache_get', 'rtb_cache_post',
            'pcode_renderer',
            'stat_dict',
            'market_recommend', 'market_report', 'news_recommend',
            'uaas', 'daemon_tvm_client',
            'mtsdsp', 'upravel', 'adlook', 'vinia', 'adriver', 'targetix', 'unity', 'beeline', 'tinkoff', 'criteo', 'rutarget', 'sociomantic',
            'yacofast_ssp', 'cookie_match', 'laas',
            'bigb_balancer_50',  # TODO igorock@: remove after BSSERVER-14443
            'linear_models_service',
            'linear_models_service_wide',
            'an_to_yabs_redirect_bad',  # @astkachev remove ignorance of this ext call after BSSERVER-16473
            'adv_machine_knn',  # remove after BSSERVER-16586
            'adv_machine_cat_engine',  # remove after BSSERVER-16586
            'adv_machine_offer_online_quorums',  # remove after BSSERVER-16586
            'yabs_banner_models_gpu',  # remove after BSSERVER-17951
            'goalnet',  # remove after SHMDUTY-159
            'yamarket',  # DSP-117
            'pnocsy350',  # SHMDUTY-291
            'pnocsy500',  # SHMDUTY-291
            'offer_match',  # SHMDUTY-327
            'word_net_service',  # SHMDUTY-392
            'panther',  # BSSERVER-22489
        },
        ext_service_thresholds={
            'rank_cache_get': 1,  # SHMDUTY-127
            'yabs_hit_models_gpu': 1,  # SHMDUTY-127
            'yabs_hit_models_heavy': 1,  # SHMDUTY-287
            'yabs_hit_models_heavy_nanny': 1,  # SHMDUTY-287
            'yabs_hit_models_light_nanny': 1,  # SHMDUTY-287
            'rsya_hit_models_light_01': 1,  # SHMDUTY-287
            'rsya_hit_models_heavy_01': 1,  # SHMDUTY-287
            'pnocsy_2': 1,  # SHMDUTY-258
            'pnocsy350': 1,  # SHMDUTY-291
            'pnocsy500': 1,  # SHMDUTY-291
        },
    )


def check_cachedaemon_access_log(cachedaemon):
    cachedaemon.check_access_log(
        broken_threshold=0.04,
        broken_thresholds={
            'awaps': 1.,
            'new_saas_location': 0.1,
            'news_recommend': 1,
            'pnocsy': 0.9,
            'rtb_proxy': 0.9,
            'pcode_renderer': 1,
            'rtb_cache': 1,
            'rtb_cache_get': 1,
            'rtb_cache_post': 1,
            'cookie_match': 1,
            'rtmr': 1,  # TODO maybe stricter
            'bigb_balancer': 0.5,
            'yacofast': 0.5,
            'yacofast_lite': 0.25,
            'yacoland': 0.2,
            'bscount': 1,
            'laas': 1,  # TODO vstromov@ to fix
            'rtcrypta': 1,  # TODO r4start@ to fix
            'bigb_rf_balancer': 1,  # SHMDUTY-72 SUPBS-16489
            'linear_models_service': 1,
            'linear_models_service_wide': 1,
            'yabs_hit_models': 1,
            'search_recommend': 1,  # TODO remove after SHMDUTY-53
            'yabs_page_models': 1,  # TODO remove after SHMDUTY-53
            'adv_machine_knn': 0.99,  # remove after BSSERVER-16586
            'adv_machine_cat_engine': 0.99,  # remove after BSSERVER-16586
            'adv_machine_offer_online_quorums': 0.99,  # remove after BSSERVER-16586
            'yabs_banner_models_gpu': 1,  # remove after BSSERVER-17951
            'yabs_hit_models_gpu': 1,  # SHMDUTY-127
            'rank_cache_get': 1,  # SHMDUTY-127
            'yamarket': 1,  # DSP-117
            'goalnet': 1,  # remove after SHMDUTY-159
            'yabs_hit_models_heavy': 1,  # SHMDUTY-287
            'yabs_hit_models_heavy_nanny': 1,  # SHMDUTY-287
            'yabs_hit_models_light_nanny': 1,  # SHMDUTY-287
            'rsya_hit_models_light_01': 1,  # SHMDUTY-287
            'rsya_hit_models_heavy_01': 1,  # SHMDUTY-287
            'pnocsy_2': 1,  # SHMDUTY-258
            'pnocsy350': 1,  # SHMDUTY-291
            'pnocsy500': 1,  # SHMDUTY-291
            'playlist_service': 1,  # SHMDUTY-320, remove after VH-13128
            'offer_match': 1,  # SHMDUTY-327
            'word_net_service': 1,  # SHMDUTY-392
            'panther': 1,  # BSSERVER-22489
        }
    )
