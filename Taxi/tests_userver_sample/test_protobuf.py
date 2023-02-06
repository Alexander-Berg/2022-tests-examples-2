# pylint: disable=import-error
from userver_sample.autogen import testing_request_pb2
from userver_sample.autogen import testing_response_pb2


async def test_protobuf(taxi_userver_sample):
    protobuf_request = testing_request_pb2.TestRequest()
    protobuf_request.first = 40
    protobuf_request.second = 2
    request_string = protobuf_request.SerializeToString()

    response = await taxi_userver_sample.post(
        'autogen/protobuf/test',
        headers={'Content-Type': 'application/protobuf'},
        data=request_string,
    )

    protobuf_response = testing_response_pb2.TestResponse()
    protobuf_response.ParseFromString(response.content)

    assert response.status_code == 200
    assert protobuf_response.sum == 42
