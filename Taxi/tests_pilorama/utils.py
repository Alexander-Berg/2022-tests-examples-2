# pylint: disable=import-error
from jaeger.proto import collector_pb2 as collector_proto
from jaeger.proto import collector_pb2_grpc as collector_grpc


async def send_batch(
        collector_stub: collector_grpc.CollectorServiceStub,
) -> collector_proto.PostSpansResponse:
    def make_request():
        request = collector_proto.PostSpansRequest()
        yield request

    return collector_stub.PostSpans(make_request())
