import csv
import io
import typing
import xml.dom.minidom as minidom

import pytest


def _format_xml(xml: typing.Union[bytes, str]) -> str:
    if isinstance(xml, bytes):
        rdom = minidom.parse(io.BytesIO(xml))
    else:
        rdom = minidom.parse(io.StringIO(xml))
    txt = rdom.toprettyxml()
    result = '\n'.join(
        x
        for x in txt.replace('\t', '\n').replace('\r', '\n').split('\n')
        if x.strip()
    )

    # A hack, the fix won't be backported to Python 3.7
    # https://bugs.python.org/issue36407
    result = result.replace('>\n<![CDATA', '><![CDATA').replace(
        ']]>\n<', ']]><',
    )
    return result


@pytest.fixture(name='mds_s3_storage', autouse=False)
def _mds_s3_storage():
    storage = {}

    class FakeMdsClient:
        def put_object(self, key, body):
            storage[key] = body

    client = FakeMdsClient()

    return client


@pytest.fixture(name='mds_s3', autouse=True)
def _mds_s3(mockserver, mds_s3_storage):
    class Context:
        def __init__(self):
            self.facebook = None
            self.direct = None
            self.google = None

        def set_data(self, facebook=None, direct=None, google=None):
            if facebook:
                self.facebook = facebook
            if direct:
                self.direct = direct
            if google:
                self.google = google

    context = Context()

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_all(request):
        if request.method == 'PUT':
            if request.path.startswith('/mds-s3/grocery_feeds_fb'):
                assert request.headers['Content-Type'] == 'text/xml'
                assert _format_xml(request.get_data()) == _format_xml(
                    context.facebook['mobile'],
                )
            elif request.path.startswith('/mds-s3/grocery_feeds_direct'):
                assert request.headers['Content-Type'] == 'text/xml'
                assert _format_xml(request.get_data()) == _format_xml(
                    context.direct['mobile'],
                )
            elif request.path.startswith('/mds-s3/grocery_feeds_google'):
                assert request.headers['Content-Type'] == 'text/csv'
                expected_csv = csv.reader(
                    io.StringIO(context.google['mobile']), delimiter=',',
                )
                requested_csv = csv.reader(
                    io.StringIO(request.get_data().decode()), delimiter=',',
                )
                for expected_row, requested_row in zip(
                        expected_csv, requested_csv,
                ):
                    assert requested_row == expected_row
            elif request.path.startswith('/mds-s3/web/grocery_feeds_direct'):
                assert request.headers['Content-Type'] == 'text/xml'
                assert _format_xml(request.get_data()) == _format_xml(
                    context.direct['web'],
                )
            elif request.path.startswith('/mds-s3/web/grocery_feeds_google'):
                assert request.headers['Content-Type'] == 'text/csv'
                expected_csv = csv.reader(
                    io.StringIO(context.google['web']), delimiter=',',
                )
                requested_csv = csv.reader(
                    io.StringIO(request.get_data().decode()), delimiter=',',
                )
                for expected_row, requested_row in zip(
                        expected_csv, requested_csv,
                ):
                    assert requested_row == expected_row
            elif request.path.startswith(
                '/mds-s3/lavket_ios/grocery_feeds_direct',
            ):
                assert request.headers['Content-Type'] == 'text/xml'
                assert _format_xml(request.get_data()) == _format_xml(
                    context.direct['lavket_ios'],
                )
            elif request.path.startswith(
                '/mds-s3/lavket_android/grocery_feeds_direct',
            ):
                assert request.headers['Content-Type'] == 'text/xml'
                assert _format_xml(request.get_data()) == _format_xml(
                    context.direct['lavket_android'],
                )
            else:
                assert False

            mds_s3_storage.put_object(request.path, request.get_data())
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Not found or invalid method', 404)

    return context
