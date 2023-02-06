import json
import pytest

from taxi.external import driver_tags_service
from taxi.external import tvm
from taxi.conf import settings
from taxi.core import async
from taxi.core import arequests

TEST_TVM_TICKET = 'test_ticket'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{
        'dst': settings.DRIVER_TAGS_TVM_SERVICE_NAME,
        'src': settings.IMPORT_TVM_SERVICE_NAME
    }]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_tvm_sign(patch):
    @patch('taxi.external.tvm.get_ticket')
    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == settings.IMPORT_TVM_SERVICE_NAME
        assert dst_service_name == settings.DRIVER_TAGS_TVM_SERVICE_NAME
        yield async.return_value(TEST_TVM_TICKET)

    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        headers = kwargs.get('headers')
        assert headers == {tvm.TVM_TICKET_HEADER: TEST_TVM_TICKET}
        body = {'tags': []}
        response = arequests.Response(
            content=json.dumps(body), status_code=200
        )
        async.return_value(response)

    yield driver_tags_service.drivers_tags_by_profile_match(
        'dbid', 'uuid', settings.IMPORT_TVM_SERVICE_NAME
    )


@pytest.mark.config(TVM_ENABLED=False,
                    DRIVER_TAGS_CLIENT_QOS={
                        '__default__': {
                            'attempts': 1,
                            'timeout-ms': 200
                        }
                    })
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize(
    'dbid, uuid, expected, error', [
        ('bad_dbid', 'bad_uuid', [], None),
        ('correct_dbid', 'correct_uuid', ['correct_tag'], None),
        ('correct_dbid', 'correct_uuid', None, arequests.RequestError),
    ]
)
@pytest.inline_callbacks
def test_match_profile_request(patch, dbid, uuid, expected, error):
    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, params=None, **kwargs):
        if error is not None:
            raise error('msg')

        body = {'tags': []}
        if dbid == 'correct_dbid' and uuid == 'correct_uuid':
            body['tags'].append('correct_tag')

        response = arequests.Response(
            content=json.dumps(body), status_code=200
        )
        async.return_value(response)

    try:
        status = yield driver_tags_service.drivers_tags_by_profile_match(
            dbid, uuid, 'test_tvm_service_name'
        )
    except Exception:
        assert False, 'Exceptions should be caught'
    assert status == expected
    assert len(request.calls) == 1
