import pytest
import hamcrest
import metrika.pylib.s3 as mts3
import yatest.common.network as ycn
import library.python.testing.pyremock.lib.pyremock as ltplp


@pytest.fixture()
def port():
    with ycn.PortManager() as pm:
        p = pm.get_port(80)
        yield p


@pytest.fixture()
def mock(port):
    with ltplp.mocked_http_server(port) as m:
        mts3.DEFAULT_S3_URL = 'http://localhost:%d' % port
        yield m


@pytest.fixture()
def s3_client(mock):
    request = ltplp.MatchRequest(path=hamcrest.is_("/"), method=hamcrest.is_(ltplp.HttpMethod.GET))
    response = ltplp.MockResponse(
        status=200,
        body="<?xml version='1.0' encoding='UTF-8'?>\n<ListAllMyBucketsResult "
             "xmlns=\"http://s3.amazonaws.com/doc/2006-03-01/\"><Buckets><Bucket>"
             "<Name>test-bucket</Name><CreationDate>2018-10-08T18:13:57.000Z"
             "</CreationDate></Bucket></Buckets></ListAllMyBucketsResult>",
        headers={
            'content-length': '249',
            'x-amz-request-id': 'a6268171ae411f0f',
            'date': 'Mon, 08 Oct 2018 23:17:50 GMT',
            'access-control-allow-origin': '*',
            'content-type': 'application/xml; charset=UTF-8',
        },
    )
    mock.expect(request, response)

    with mts3.S3Manager('qwe', 'asd') as s3:
        yield s3
