import itertools
import json
import os.path

import jsonschema
import pytest

from taxi_tests.utils import yaml_util

from . import templates

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schemas/yamlcase.yaml')


class YamlFile(pytest.File):
    _yamlcase_validator = None

    # pytest internally use this property
    @property
    def obj(self):
        return None

    def collect(self):
        doc = yaml_util.load_file(self.fspath)
        self.schema_validate(doc)
        for testcase in doc.get('tests', []):
            yield YamlFunction(
                fspath=self.fspath,
                parent=self,
                testcase=testcase,
                root_doc=doc,
            )

    def schema_validate(self, doc):
        validator = self._get_schema_validator()
        validator.validate(doc)

    @classmethod
    def _get_schema_validator(cls):
        if not cls._yamlcase_validator:
            schema = yaml_util.load_file(SCHEMA_PATH)
            cls._yamlcase_validator = jsonschema.Draft4Validator(schema)
        return cls._yamlcase_validator


class YamlFunction(pytest.Function):
    def __init__(self, *, fspath, parent, testcase, root_doc):
        super().__init__(
            name=testcase['name'],
            parent=parent,
            callobj=create_testcase(testcase, root_doc=root_doc),
        )
        self.fspath = fspath
        self.testcase_doc = testcase
        self.root_doc = root_doc

    @property
    def mockserver_mocks(self):
        return itertools.chain(
            self.root_doc.get('mockserver', []),
            self.testcase_doc.get('mockserver', []),
        )

    @property
    def testpoint_handlers(self):
        return itertools.chain(
            self.root_doc.get('testpoint', []),
            self.testcase_doc.get('testpoint', []),
        )

    def reportinfo(self):
        return self.fspath, 1, f'{self.fspath}::{self.name}'


def pytest_collect_file(parent, path):
    if path.ext == '.yaml' and path.basename.startswith('test'):
        return YamlFile(path, parent)
    return None


def create_testcase(doc, root_doc):
    service_name = root_doc['service']

    fixtures = [service_name, 'yamlcase_init']
    fixtures.extend(root_doc.get('fixtures', []))
    fixtures.extend(doc.get('fixtures', []))

    pytest_marks = doc.get('marks', []) + root_doc.get('marks', [])

    test_request = doc.get('request', {})
    test_response = doc.get('response', {})

    @pytest.mark.usefixtures(*fixtures)
    async def testcase(
            request, yamlcase_load_body, yamlcase_assertion_runner, **kwargs,
    ):
        if 'body' in test_request:
            request_json = yamlcase_load_body(test_request['body'])
        else:
            request_json = None

        service = request.getfixturevalue(service_name)
        response = await service.request(
            test_request.get('method', 'POST'),
            test_request.get('path', '/'),
            headers=test_request.get('headers'),
            json=request_json,
        )
        assert response.status_code == test_response.get('status', 200)

        if 'body' in test_response:
            response_json = yamlcase_load_body(test_response['body'])
            assert response.json() == response_json

        _assert_headers(response.headers, test_response.get('headers', {}))

        if 'assertions' in doc:
            yamlcase_assertion_runner(doc['assertions'])

    testcase.__name__ = doc['name']
    testcase = _apply_marks(testcase, pytest_marks)
    return testcase


@pytest.fixture
def yamlcase_assertion_runner(mockserver, testpoint):
    def runner(assertions):
        for assertion in assertions:
            if assertion['type'] == 'mockserver-called':
                assert 'url' in assertion
                handler = mockserver.get_callqueue_for(assertion['url'])
                if 'times' in assertion:
                    assert handler.times_called == assertion['times']
                else:
                    assert handler.times_called > 0
            elif assertion['type'] == 'testpoint-called':
                assert 'name' in assertion
                handler = testpoint[assertion['name']]
                testpoint_calls = []
                tested = False
                while handler.has_calls:
                    testpoint_calls.append(handler.next_call()['data'])
                if 'calls' in assertion:
                    assert isinstance(assertion['calls'], list)
                    assert testpoint_calls == assertion['calls']
                    tested = True
                if 'times' in assertion:
                    assert len(testpoint_calls) == assertion['times']
                    tested = True
                if not tested:
                    assert testpoint_calls
            else:
                raise RuntimeError(
                    f'Unknown assertion type {assertion["type"]}',
                )

    return runner


@pytest.fixture
def yamlcase_context(request):
    params = {}
    for doc in (request.node.root_doc, request.node.testcase_doc):
        if 'params' in doc:
            params.update(doc['params'])
    return templates.StackedContext(params)


@pytest.fixture
def yamlcase_load_body(yamlcase_context):
    def load_body(obj):
        # json strings are obsolete will be removed soon
        if isinstance(obj, str):
            return json.loads(obj)
        return templates.render(obj, yamlcase_context)

    return load_body


@pytest.fixture
def yamlcase_init(
        mockserver, testpoint, request, yamlcase_load_body, yamlcase_context,
):
    for mock in request.node.mockserver_mocks:
        _create_mockserver_handler(
            mock, mockserver, yamlcase_load_body, yamlcase_context,
        )
    for handler in request.node.testpoint_handlers:
        _create_testpoint_handler(testpoint, handler, yamlcase_load_body)


def _create_mockserver_handler(
        mock, mockserver, yamlcase_load_body, yamlcase_context,
):
    @mockserver.handler(mock['url'])
    def handler(request):
        with yamlcase_context.context({'request': request}):
            mock_request = mock.get('request', {})
            if 'method' in mock_request:
                assert request.method == mock_request['method']
            if 'headers' in mock_request:
                _assert_headers(request.headers, mock_request['headers'])
            if 'body' in mock_request:
                expected_body = yamlcase_load_body(mock_request['body'])
                assert request.json == expected_body
            response = mock.get('response', {})
            return mockserver.make_response(
                status=response.get('status', 200),
                json=yamlcase_load_body(response['body']),
                headers=response.get('headers'),
            )

    return handler


def _create_testpoint_handler(testpoint, handler, yamlcase_load_body):
    @testpoint(handler['name'])
    def testpoint_handler(data):
        if 'data' in handler:
            expected = yamlcase_load_body(handler['data'])
            assert data == expected

    return testpoint_handler


def _apply_marks(func, marks):
    for mark in marks:
        markobj = getattr(pytest.mark, mark['name'])
        func = markobj(*mark.get('args', ()), **mark.get('kwargs', {}))(func)
    return func


def _assert_headers(headers, expected_headers):
    for key, value in expected_headers.items():
        assert key in headers
        assert headers[key] == value
