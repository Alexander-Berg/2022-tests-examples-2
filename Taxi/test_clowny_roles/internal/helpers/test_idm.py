import typing
from typing import List

from clowny_roles.internal.helpers import idm


def _assert(lhs: List[idm.OkResponseItem], rhs: List[idm.OkResponseItem]):
    def _convert(data: List[idm.OkResponseItem]):
        return [(resp.serialize(), item) for resp, item in data]

    assert _convert(lhs) == _convert(rhs)


class TestApi(idm.BatchApiBase):
    def _make_operation_item(
            self, operation_item: idm.BatchOperationItem,
    ) -> idm.BatchOperationsRequestItem:
        return operation_item.to_api()

    def _parse_operation_response(
            self, response: idm.BatchOperationResponseItem,
    ) -> idm.BatchOperationItem:
        return idm.BatchOperationItem(
            method=idm.OperationMethod.POST,
            body=typing.cast(dict, response.body),
            id=response.id,
            path=response.id,  # this will be parsed from id
        )

    def _check_is_400_error_id_ok(
            self, response: idm.BatchOperationResponseItem,
    ) -> bool:
        if response.id == '400-error-but-really-ok':
            return True
        return super()._check_is_400_error_id_ok(response)


async def test_empty_batch(mock_idm, web_context):
    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        return {'responses': [{**x, 'status_code': 0} for x in request.json]}

    api = TestApi(web_context)
    success, failed = await api.batch_operations([])
    assert success == failed == []
    assert _batch_handler.times_called == 0


async def test_one_good_batch(mock_idm, web_context):
    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        return {'responses': [{**x, 'status_code': 0} for x in request.json]}

    api = TestApi(web_context)
    success, failed = await api.batch_operations(
        [
            idm.BatchOperationItem(
                method=idm.OperationMethod.POST,
                path='/some/path',
                body={},
                id='some-good-id',
            ),
        ],
    )
    assert not failed
    _assert(
        success,
        [
            (
                idm.BatchOperationResponseItem(
                    id='some-good-id', status_code=0, headers=None, body={},
                ),
                idm.BatchOperationItem(
                    method=idm.OperationMethod.POST,
                    # because we have little hack for tests
                    path='some-good-id',
                    body={},
                    id='some-good-id',
                ),
            ),
        ],
    )
    assert _batch_handler.times_called == 1


async def test_retries(mockserver, mock_idm, web_context):
    called_once = False

    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        nonlocal called_once
        if not called_once:
            called_once = True
            return mockserver.make_response(
                status=500,
                json={
                    'responses': [
                        {
                            **x,
                            'status_code': 500,
                            'body': {'message': 'internal error'},
                        }
                        for x in request.json
                    ],
                },
            )
        return {'responses': [{**x, 'status_code': 0} for x in request.json]}

    api = TestApi(web_context)
    success, failed = await api.batch_operations(
        [
            idm.BatchOperationItem(
                method=idm.OperationMethod.POST,
                path='/some/path',
                body={},
                id='some-good-id',
            ),
        ],
    )
    assert not failed
    _assert(
        success,
        [
            (
                idm.BatchOperationResponseItem(
                    id='some-good-id',
                    status_code=0,
                    headers=None,
                    body={'message': 'internal error'},
                ),
                idm.BatchOperationItem(
                    method=idm.OperationMethod.POST,
                    # because we have little hack for tests
                    path='some-good-id',
                    # because we have simple parser - just as-is converter
                    body={'message': 'internal error'},
                    id='some-good-id',
                ),
            ),
        ],
    )
    assert _batch_handler.times_called == 2


async def test_non_retryable_errors(mockserver, mock_idm, web_context):
    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        if len(request.json) == 2:
            request_to_500 = [
                x for x in request.json if x['id'] == 'some-good-id'
            ][0]
            request_to_400 = [
                x for x in request.json if x['id'] == 'some-bad-id'
            ][0]

            return mockserver.make_response(
                status=400,
                json={
                    'responses': [
                        {
                            **request_to_500,
                            'status_code': 500,
                            'body': {'message': 'internal error'},
                        },
                        {
                            **request_to_400,
                            'status_code': 400,
                            'body': {'message': 'some very bad'},
                        },
                    ],
                },
            )
        return {'responses': [{**x, 'status_code': 0} for x in request.json]}

    api = TestApi(web_context)
    success, failed = await api.batch_operations(
        [
            idm.BatchOperationItem(
                method=idm.OperationMethod.POST,
                path='some-good-id',
                body={},
                id='some-good-id',
            ),
            idm.BatchOperationItem(
                method=idm.OperationMethod.POST,
                path='/some/path',
                body={},
                id='some-bad-id',
            ),
        ],
    )

    assert failed == [
        idm.BatchOperationItem(
            method=idm.OperationMethod.POST,
            path='some-bad-id',
            body={'message': 'some very bad'},
            id='some-bad-id',
        ),
    ]
    _assert(
        success,
        [
            (
                idm.BatchOperationResponseItem(
                    id='some-good-id',
                    status_code=0,
                    headers=None,
                    body={'message': 'internal error'},
                ),
                idm.BatchOperationItem(
                    method=idm.OperationMethod.POST,
                    path='some-good-id',
                    body={'message': 'internal error'},
                    id='some-good-id',
                ),
            ),
        ],
    )
    assert _batch_handler.times_called == 2


async def test_ok_400_error(mockserver, mock_idm, web_context):
    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        return mockserver.make_response(
            status=400,
            json={
                'responses': [{**x, 'status_code': 400} for x in request.json],
            },
        )

    api = TestApi(web_context)
    success, failed = await api.batch_operations(
        [
            idm.BatchOperationItem(
                method=idm.OperationMethod.POST,
                path='/some/path',
                body={},
                id='400-error-but-really-ok',
            ),
        ],
    )
    assert not failed
    _assert(
        success,
        [
            (
                idm.BatchOperationResponseItem(
                    id='400-error-but-really-ok',
                    status_code=400,
                    headers=None,
                    body={},
                ),
                idm.BatchOperationItem(
                    method=idm.OperationMethod.POST,
                    # because we have little hack for tests
                    path='400-error-but-really-ok',
                    body={},
                    id='400-error-but-really-ok',
                ),
            ),
        ],
    )
    assert _batch_handler.times_called == 1
