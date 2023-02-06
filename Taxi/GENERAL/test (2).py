import logging

from aiohttp import web

from taxi import opentracing
from taxi.logs import auto_log_extra
from taxi.opentracing.ext import http_client

from taxi_tracing import settings

logger = logging.getLogger(__name__)


async def handler(request) -> web.Response:
    url = f'http://{settings.SELF_HOST}/ping'
    async with http_client.OpentracingClientSession() as session:
        async with session.get(url) as resp:
            logger.info('Everything is going OK', extra=request['log_extra'])
            _tracer = opentracing.global_tracer()
            _span = _tracer.start_span('test operation')

            with _tracer.scope_manager.activate(_span) as _scope:
                logger.info(
                    'I`m testing some interesting thing',
                    extra=auto_log_extra.to_log_extra(
                        span_id=_scope.span.context.span_id,
                        trace_id=_scope.span.context.trace_id,
                    ),
                )

            return web.json_response(await resp.json())


async def non_recursive_handler(request) -> web.Response:
    logger.info('Outer message')
    _tracer = opentracing.global_tracer()
    _span = _tracer.start_span('test-op')
    with _tracer.scope_manager.activate(_span):
        logger.info('Inner message')
        contexts = await request.app.db.taxi_tracing_contexts.find(
            {}, {'_id': 0, 'span_id': 1},
        ).to_list(None)

        more_contexts = []
        async for item in request.app.db.taxi_tracing_contexts.find(
                {}, {'_id': 0, 'span_id': 1},
        ):
            more_contexts.append(item)

        contexts_count = await request.app.db.taxi_tracing_contexts.count()
        contexts_find_count = (
            await request.app.db.taxi_tracing_contexts.find().count()
        )

    return web.json_response(
        {
            'contexts': contexts,
            'more_contexts': more_contexts,
            'contexts_count': contexts_count,
            'contexts_find_count': contexts_find_count,
        },
    )
