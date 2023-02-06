from typing import Set

from taxi_dashboards import generator
from taxi_dashboards.layout_handlers.userver import userver_common


def _do_assert(names: Set[str], generic_names: Set[str]) -> None:
    assert names.issubset(generic_names), 'Missing in generic: "{}"'.format(
        list(names - generic_names),
    )


def test_userver_common() -> None:
    names = {
        'caches',
        'caches_documents_count',
        'lru_caches_hit_ratio',
        'lru_caches_documents_count',
        'mongo',
        'httpclient',
        'httpclient_destinations',
        'redis_client',
        'redis_subscribe_client',
        'task_processors',
        'logbroker_producer',
        'tvm2',
        'yt_replica_reader',
        'pilorama',
    }

    generic_names = {nm for nm, _ in userver_common.get_handlers()}
    _do_assert(names, generic_names)


def test_generator() -> None:
    names = {
        'userver_caches',
        'userver_caches_documents_count',
        'userver_task_processors',
        'userver_tvm2',
        'userver_logbroker_producer',
        'userver_lru_caches_documents_count',
        'userver_lru_caches_hit_ratio',
        'userver_httpclient',
        'userver_httpclient_destinations',
        'userver_mongo',
        'userver_pilorama',
        'userver_redis_client',
        'userver_yt_replica_reader',
    }
    extra_names = {'userver_tvm2_service_tickets'}

    generic_names = set(generator.HANDLERS.keys())

    _do_assert({'userver_common'}, generic_names)
    _do_assert(names, generic_names)
    _do_assert(extra_names, generic_names)
