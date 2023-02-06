# pylint: disable=import-error
# Tier 0 tests it implicitly anyway

from arcadia_test.fbs import Sample
from arcadia_test.fbs import Stuff
import flatbuffers
from geometry.fbs import Position
from userver_sample.autogen.fbs import TestPostRequest


def test_flatbuffer_complex_model():
    builder = flatbuffers.Builder(0)

    Stuff.StuffStart(builder)
    Stuff.StuffAddId(builder, 1)
    stuff = Stuff.StuffEnd(builder)

    Sample.SampleStart(builder)
    Sample.SampleAddStuff(builder, stuff)
    Sample.SampleAddPosition(
        builder, Position.CreatePosition(builder, 55751244, 37618423),
    )
    sample = Sample.SampleEnd(builder)
    builder.Finish(sample)
    assert len(builder.Output()) == 48


async def test_flatbuffer_handler(taxi_arcadia_userver_test):
    builder = flatbuffers.Builder(0)
    data = builder.CreateString(b'foobar')
    TestPostRequest.TestPostRequestStart(builder)
    TestPostRequest.TestPostRequestAddArg1(builder, 100)
    TestPostRequest.TestPostRequestAddArg2(builder, 25)
    TestPostRequest.TestPostRequestAddData(builder, data)
    request = TestPostRequest.TestPostRequestEnd(builder)
    builder.Finish(request)

    response = await taxi_arcadia_userver_test.post(
        '/serialize/flatbuf/echo',
        data=builder.Output(),
        headers={'content-type': 'application/flatbuffer'},
    )
    assert response.status_code == 200, response.content
    result_fbb = TestPostRequest.TestPostRequest.GetRootAsTestPostRequest(
        response.content, 0,
    )
    assert result_fbb.Data() == b'foobar'
