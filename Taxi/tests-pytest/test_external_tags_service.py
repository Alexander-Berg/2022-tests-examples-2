import json
import pytest
import requests

from taxi.external import tags_service
from taxi.external import tvm
from taxi.conf import settings
from taxi.core import async
from taxi.core import arequests

TEST_TVM_TICKET = 'test_ticket'
ENTITY_TYPES = [good_type.value for good_type in list(tags_service.EntityType)]


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{
        'dst': settings.TAGS_TVM_SERVICE_NAME,
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
        assert dst_service_name == settings.TAGS_TVM_SERVICE_NAME
        yield async.return_value(TEST_TVM_TICKET)

    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        headers = kwargs.get('headers')
        assert headers == {tvm.TVM_TICKET_HEADER: TEST_TVM_TICKET}
        response = arequests.Response(status_code=200)
        async.return_value(response)

    yield tags_service.upload_request(
        {}, 'pr_id', settings.IMPORT_TVM_SERVICE_NAME,
        tags_service.EntityType.DRIVER_LICENSE
    )


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize(
    'data, entity_type, error, expected', [
        ({}, tags_service.EntityType.CAR_NUMBER.value, None, True),
        ({}, tags_service.EntityType.CAR_NUMBER, None, True),
        ({}, tags_service.EntityType.CAR_NUMBER, arequests.RequestError, False),
        ({}, tags_service.EntityType.CAR_NUMBER, arequests.HTTPError, False),
        ({}, tags_service.EntityType.CAR_NUMBER, requests.RequestException,
         False),
        ({}, tags_service.EntityType.CAR_NUMBER, requests.HTTPError, False),
    ]
)
@pytest.inline_callbacks
def test_upload_request(patch, data, entity_type, error, expected):
    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        if error is None:
            response = arequests.Response(status_code=200)
            async.return_value(response)
        else:
            raise error('msg')

    try:
        status = yield tags_service.upload_request(
            data,
            'test_provider',
            'test_tvm_service_name',
            entity_type,
            merge_policy=tags_service.MergePolicy.REPLACE
        )
        assert status == expected
    except Exception:
        assert False, 'All exceptions should be caught'
    assert len(request.calls) == 1


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize(
    'entities, error, expected', [
        ([], arequests.RequestError, None),
        ([], arequests.HTTPError, None),
        ([], requests.RequestException, None),
        ([], requests.HTTPError, None),
        ([], None, {}),
        (['nonexistent_entity'], None, {}),
        (['empty_number'], None, {
            'empty_number': []
        }),
        (['number1'], None, {
            'number1': ['tag1']
        }),
        (['number3', 'number1'], None, {
            'number1': ['tag1'],
            'number3': ['tag1', 'tag2', 'tag3']
        }),
    ]
)
@pytest.inline_callbacks
def test_bulk_match_request(patch, entities, error, expected):
    tags_by_entity = {
        'empty_number': [],
        'number1': ['tag1'],
        'number2': ['tag1', 'tag2'],
        'number3': ['tag1', 'tag2', 'tag3'],
    }

    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        if error is None:
            data = []
            for entity in entities:
                if entity in tags_by_entity:
                    data.append({'id': entity, 'tags': tags_by_entity[entity]})

            mock_response = arequests.Response(
                status_code=200, content=json.dumps({'entities': data})
            )
            async.return_value(mock_response)
        else:
            raise error('some_msg')

    try:
        response = yield tags_service.bulk_match_request(
            tags_service.EntityType.CAR_NUMBER, entities,
            'test_tvm_service_name'
        )
    except Exception:
        assert False, 'All exceptions should be caught'
    assert response == expected
    assert len(request.calls) == 1


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize(
    'entity_type, expected_result, error', [
        ('dbid_uuid', True, None),
        ('invalid_type', False, None),
        ('dbid_uuid', False, arequests.TimeoutError),
    ]
)
@pytest.inline_callbacks
def test_check_entity_type(patch, entity_type, expected_result, error):
    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, params=None, **kwargs):
        if error is not None:
            raise error('msg')
        body = {'entity_types': ENTITY_TYPES}
        response = arequests.Response(
            content=json.dumps(body), status_code=200
        )
        async.return_value(response)

    try:
        is_valid = yield tags_service.check_entity_type(
            entity_type, 'test_tvm_service_name'
        )
    except Exception:
        assert False, 'Exceptions should be caught'
    assert is_valid == expected_result
    assert len(request.calls) == 1
