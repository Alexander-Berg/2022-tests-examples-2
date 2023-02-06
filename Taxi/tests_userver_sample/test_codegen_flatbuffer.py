# pylint: disable=import-error
import flatbuffers
from userver_sample.autogen.fbs import TestPostErrorResponse as fb_resp400
from userver_sample.autogen.fbs import TestPostRequest as fb_req
from userver_sample.autogen.fbs import TestPostResponse as fb_resp200


def construct_fbs_post_request(data: str, is_error: bool = False) -> bytearray:
    builder = flatbuffers.Builder(initialSize=1024)
    input_string = builder.CreateString(data)
    fb_req.TestPostRequestStart(builder)
    fb_req.TestPostRequestAddReturnError(builder, is_error)
    fb_req.TestPostRequestAddArg1(builder, 100)
    fb_req.TestPostRequestAddArg2(builder, 10)
    fb_req.TestPostRequestAddData(builder, input_string)
    request = fb_req.TestPostRequestEnd(builder)
    builder.Finish(request)
    return builder.Output()


async def test_autogen_flatbuf_200(taxi_userver_sample):
    very_long_string = b'VERY_VERY_VERY_VERY_LONG_TEST_INPUT_2'
    data = construct_fbs_post_request(very_long_string)

    response = await taxi_userver_sample.post(
        'autogen/flatbuf/test',
        data=data,
        headers={
            'header-number': '1.0',
            'Content-Type': 'application/flatbuffer',
        },
        params={'query-enum': 'two'},
    )

    assert response.status_code == 200
    assert response.headers['header-number'] == '1.0'
    assert response.headers['query-enum'] == 'two'

    parsed_response = fb_resp200.TestPostResponse.GetRootAsTestPostResponse(
        bytearray(response.content), 0,
    )
    assert parsed_response.Sum() == 110
    assert parsed_response.Echo() == very_long_string


async def test_autogen_flatbuf_400(taxi_userver_sample):
    data = construct_fbs_post_request('TEST_INPUT_1', is_error=True)

    response = await taxi_userver_sample.post(
        'autogen/flatbuf/test',
        data=data,
        headers={
            'header-number': '42',
            'Content-Type': 'application/flatbuffer',
        },
        params={'query-enum': 'two'},
    )

    assert response.status_code == 400
    parsed = fb_resp400.TestPostErrorResponse.GetRootAsTestPostErrorResponse(
        bytearray(response.content), 0,
    )
    assert parsed.Code() == b'CODE'
    assert parsed.Message() == b'MESSAGE'
