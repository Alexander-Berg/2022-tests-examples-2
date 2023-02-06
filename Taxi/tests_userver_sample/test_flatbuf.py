# pylint: disable=import-error
import flatbuffers
from samples.handlers.fbs import TestRequest
from samples.handlers.fbs import TestResponse


async def test_sum(taxi_userver_sample):
    builder = flatbuffers.Builder(0)
    TestRequest.TestRequestStart(builder)
    TestRequest.TestRequestAddArg1(builder, 100)
    TestRequest.TestRequestAddArg2(builder, 25)
    input_fbb = TestRequest.TestRequestEnd(builder)
    builder.Finish(input_fbb)

    response = await taxi_userver_sample.get('sum', data=builder.Output())
    assert response.status_code == 200
    result_fbb = TestResponse.TestResponse.GetRootAsTestResponse(
        response.content, 0,
    )
    assert result_fbb.Sum() == 125


async def test_wrong_arg(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        'sum', data='\x1f\x08\x00\x00\x00\x00\x00\x03',
    )
    assert response.status_code == 400
