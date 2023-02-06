from unittest import mock

import pytest

from document_templator import request_executer
from document_templator.generated.api import web_context
from document_templator.generated.service.swagger.models import api
from document_templator.models import request as request_model


@pytest.mark.parametrize(
    'first_param, second_param, expected_results',
    (
        (
            api.DynamicDocumentRequestParameter(
                id='1' * 24,
                name='test',
                body={
                    'body': {'body': {}},
                    'body2': [{}, {'body': [23], 123: 1.23}],
                },
                query={'query1': 'test query1', 'query2': 'test query2'},
                substitutions={'first': 'test_first'},
            ),
            api.DynamicDocumentRequestParameter(
                id='2' * 24,
                name='test',
                body={
                    'body': {'body': {}},
                    'body2': [{}, {'body': [23], 123: 1.23}],
                },
                query={'query1': 'test query1', 'query2': 'test query2'},
                substitutions={'second': 'test_second'},
            ),
            ['first', 'first', 'second', 'second'],
        ),
        (
            api.DynamicDocumentRequestParameter(
                id='1' * 24,
                name='test',
                body={
                    'body': {'body': {}},
                    'body2': [{}, {'body': [23], 123: 1.23}],
                },
                query={'query1': 'test query1', 'query2': 'test query2'},
                substitutions={'first': 'test_first'},
            ),
            # changed_body
            api.DynamicDocumentRequestParameter(
                id='2' * 24,
                name='test',
                body={
                    'changed_body': {'body': {}},
                    'body2': [{}, {'body': [23], 123: 1.23}],
                },
                query={'query1': 'test query1', 'query2': 'test query2'},
                substitutions={'second': 'test_second'},
            ),
            ['first', 'first', 'second', 'third'],
        ),
        (
            # changed_substitutions
            api.DynamicDocumentRequestParameter(
                id='1' * 24,
                name='test',
                body={
                    'body': {'body': {}},
                    'body2': [{}, {'body': [23], 123: 1.23}],
                },
                query={'query1': 'test query1', 'query2': 'test query2'},
                substitutions={'first': 'changed_substitutions'},
            ),
            api.DynamicDocumentRequestParameter(
                id='2' * 24,
                name='test',
                body={
                    'body': {'body': {}},
                    'body2': [{}, {'body': [23], 123: 1.23}],
                },
                query={'query1': 'test query1', 'query2': 'test query2'},
                substitutions={'second': 'test_second'},
            ),
            ['first', 'second', 'third', 'third'],
        ),
        (
            # changed_query
            api.DynamicDocumentRequestParameter(
                id='1' * 24,
                name='test',
                body={
                    'body': {'body': {}},
                    'body2': [{}, {'body': [23], 123: 1.23}],
                },
                query={'query1': 'changed_query', 'query2': 'test query2'},
                substitutions={'first': 'test_first'},
            ),
            api.DynamicDocumentRequestParameter(
                id='2' * 24,
                name='test',
                body={
                    'body': {'body': {}},
                    'body2': [{}, {'body': [23], 123: 1.23}],
                },
                query={'query1': 'changed_query', 'query2': 'test query2'},
                substitutions={'second': 'test_second'},
            ),
            ['first', 'second', 'third', 'fourth'],
        ),
    ),
)
async def test_cache_execute_request(
        first_param, second_param, expected_results,
):
    async def _execute_request(value):
        return value

    request_executer_ = request_executer.RequestExecuter(
        context=web_context.Context(),
    )
    execute_request_coros = (
        _execute_request(item)
        for item in ['first', 'second', 'third', 'fourth']
    )
    _execute_request_mock = mock.patch.object(
        request_executer_,
        '_execute_request',
        side_effect=execute_request_coros,
    )

    request1 = request_model.Request(
        request_model.Endpoint('test', '/first/{first}', 'POST', 100, 3),
        name='test',
        description='test',
        body_schema={},
        response_schema={},
        query={'query1', 'query2'},
        id_='1' * 24,
    )
    request2 = request_model.Request(
        request_model.Endpoint('test', '/second/{second}', 'POST', 100, 3),
        name='test',
        description='test',
        body_schema={},
        response_schema={},
        query=set(),
        id_='2' * 24,
    )
    request_param1 = api.DynamicDocumentRequestParameter(
        id='1' * 24,
        name='test',
        body={'body': {'body': {}}, 'body2': [{}, {'body': [23], 123: 1.23}]},
        query={'query1': 'test query1', 'query2': 'test query2'},
        substitutions={'first': 'test_first'},
    )
    request_param2 = api.DynamicDocumentRequestParameter(
        id='2' * 24,
        name='test',
        body={'body': {'body': {}}, 'body2': [{}, {'body': [23], 123: 1.23}]},
        query={'query1': 'test query1', 'query2': 'test query2'},
        substitutions={'second': 'test_second'},
    )
    results = []
    with _execute_request_mock:
        results.append(
            await request_executer_.execute_request(request1, request_param1),
        )
        results.append(
            await request_executer_.execute_request(request1, first_param),
        )
        results.append(
            await request_executer_.execute_request(request2, request_param2),
        )
        results.append(
            await request_executer_.execute_request(request2, second_param),
        )

    assert results == expected_results
