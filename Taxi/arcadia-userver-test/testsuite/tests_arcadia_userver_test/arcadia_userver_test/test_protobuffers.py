# pylint: disable=import-error
from google.protobuf import duration_pb2
from google.protobuf import json_format
import sample_pb2
from userver_sample.autogen import testing_request_pb2
from userver_sample.autogen import testing_response_pb2
from yabs.proto import user_profile_pb2


def test_local_schemas():
    sample = sample_pb2.TestModel()
    assert isinstance(sample.duration, duration_pb2.Duration)


async def test_flatbuffer_handler(taxi_arcadia_userver_test, mockserver):
    pb_request = testing_request_pb2.TestRequest()
    pb_request.first = 40
    pb_request.second = 2

    @mockserver.json_handler('/bigb/bigb')
    def bigb(request):
        assert request.args['client'] == 'test'
        assert request.args['format'] == 'protobuf'
        assert request.args['puid'] == '40'

        msg = user_profile_pb2.Profile()
        json_format.ParseDict({'items': [{'keyword_id': 1}]}, msg)
        return mockserver.make_response(
            msg.SerializeToString(deterministic=True),
        )

    response = await taxi_arcadia_userver_test.post(
        '/serialize/protobuf/echo',
        data=pb_request.SerializeToString(),
        headers={'content-type': 'application/x-protobuf'},
    )
    assert response.status_code == 200, response.content

    pb_response = testing_response_pb2.TestResponse()
    pb_response.ParseFromString(response.content)

    assert bigb.times_called == 1
    assert pb_response.sum == 3
