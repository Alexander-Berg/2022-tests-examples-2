import logging

from google.protobuf import json_format
import grpc
# pylint: disable=import-error
from jaeger.proto import collector_pb2 as collector_proto
from jaeger.proto import collector_pb2_grpc as collector_grpc
import pytest

GRPC_HOST = 'localhost:14251'

logger = logging.getLogger(__name__)


def bytes_to_int(raw_bytes):
    return int.from_bytes(raw_bytes, byteorder='big', signed=False)


def each_tag_has_hostname(request_dict):
    has_hostname = True
    for span in request_dict['spans']:
        span_has_hostname = False
        if 'tags' not in span['process']:
            return False
        for tag in span['process']['tags']:
            if tag['key'] == 'hostname':
                span_has_hostname = True
        has_hostname = has_hostname and span_has_hostname
    return has_hostname


def remove_hostname(request_dict):
    for span in request_dict['spans']:
        if 'tags' not in span['process']:
            return
        new_tags = []
        for tag in span['process']['tags']:
            if tag['key'] != 'hostname':
                new_tags.append(tag)
        span['process']['tags'] = new_tags


def remove_process_tags_if_empty(request_dict):
    for span in request_dict['spans']:
        if 'tags' in span['process']:
            if not span['process']['tags']:
                del span['process']['tags']


class JaegerCollectorMock(collector_grpc.CollectorServiceServicer):
    def __init__(self) -> None:
        super().__init__()
        self._grpc_server = None
        self._request_bench = None
        self._succeed = False
        self._ready = False

    def set_request_bench(self, batch):
        logger.info('JaegerCollectorMock: set received batch')
        self._request_bench = batch

    def is_succeed(self):
        res = self._succeed
        self._ready = False
        self._succeed = False
        return res

    def is_ready(self):
        return self._ready

    # pylint: disable=invalid-name
    async def PostSpans(self, request, context: grpc.aio.ServicerContext):
        logger.info('JaegerCollectorMock: accepting PostSpans')

        request_proto = collector_proto.PostSpansRequestOriginal()
        request_proto.ParseFromString(request.SerializeToString())
        request_dict = json_format.MessageToDict(request_proto.batch)

        for i, span in enumerate(request_dict['spans']):
            request_span = request_proto.batch.spans[i]
            span['spanId'] = bytes_to_int(request_span.span_id)
            span['traceId'] = bytes_to_int(request_span.trace_id)

            if 'references' in span:
                for j, reference in enumerate(span['references']):
                    request_ref = request_span.references[j]
                    reference['spanId'] = bytes_to_int(request_ref.span_id)
                    reference['traceId'] = bytes_to_int(request_ref.trace_id)

        has_hostname = each_tag_has_hostname(request_dict)

        # remove spans[tags[key==hostname]]
        remove_hostname(request_dict)
        remove_process_tags_if_empty(request_dict)

        self._succeed = has_hostname and bool(
            request_dict == self._request_bench,
        )
        self._ready = True

        return collector_proto.PostSpansResponse()

    async def stop(self) -> None:
        if self._grpc_server:
            await self._grpc_server.stop(grace=None)
            self._grpc_server = None

    async def restart(self) -> None:
        await self.stop()

        self._grpc_server = grpc.aio.server()
        assert self._grpc_server

        collector_grpc.add_CollectorServiceServicer_to_server(
            self, self._grpc_server,
        )
        self._grpc_server.add_insecure_port('localhost:14250')

        await self._grpc_server.start()


@pytest.fixture(name='jaeger_collector_mock')
async def _jaeger_collector_mock():
    mock = JaegerCollectorMock()
    await mock.restart()
    logger.info('JaegerCollectorMock server started')
    try:
        yield mock
    finally:
        await mock.stop()
        logger.info('JaegerCollectorMock server stopped')
