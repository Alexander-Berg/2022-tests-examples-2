import itertools
import json
import pathlib

import jsonschema
import pytest

from testsuite.utils import yaml_util

from . import assertions
from . import templates

SCHEMA_PATH = pathlib.Path(__file__).parent.joinpath('schemas/yamlcase.yaml')

pytest_plugins = [
    'taxi_testsuite.plugins.yamlcase.plugins.mockserver',
    'taxi_testsuite.plugins.yamlcase.plugins.mongodb',
    'taxi_testsuite.plugins.yamlcase.plugins.testpoint',
]


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
        # TODO: split schema into pieces
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

    fixtures = [
        service_name,
        'yamlcase_create_testpoints',
        'yamlcase_create_mockserver',
    ]
    fixtures.extend(root_doc.get('fixtures', []))
    fixtures.extend(doc.get('fixtures', []))

    pytest_marks = doc.get('marks', []) + root_doc.get('marks', [])

    test_request = doc.get('request', {})
    test_response = doc.get('response', {})

    # TODO: create context once
    yamlcase_context = _create_template_context(root_doc, doc)

    @pytest.mark.usefixtures(*fixtures)
    async def testcase(request, yamlcase_load_body, **kwargs):
        if 'body' in test_request:
            request_json = yamlcase_load_body(test_request['body'])
        else:
            request_json = None

        service = request.getfixturevalue(service_name)
        response = await service.request(
            test_request.get('method', 'POST'),
            test_request.get('path', '/'),
            headers=test_request.get('headers', {}),
            params=test_request.get('query_params', {}),
            json=request_json,
        )
        assert response.status_code == test_response.get('status', 200)

        if 'body' in test_response:
            response_json = yamlcase_load_body(
                test_response['body'], allow_matching=True,
            )
            assert response.json() == response_json

        assertions.assert_headers(
            response.headers, test_response.get('headers', {}),
        )

        if 'assertions' in doc:
            await _run_assertions(doc['assertions'], request)

    testcase.__name__ = doc['name']
    testcase = _apply_marks(testcase, pytest_marks, yamlcase_context)
    return testcase


async def _run_assertions(assertions, request):
    for assertion in assertions:
        assertion_type = assertion['type']
        fixture_name = 'yamlcase_assertion_' + assertion_type.replace('-', '_')
        try:
            handler = request.getfixturevalue(fixture_name)
        except Exception as exc:
            raise RuntimeError(
                f'Assertion type {assertion_type!r} is not supported',
            ) from exc
        await handler(assertion)


@pytest.fixture
def yamlcase_context(request):
    params = {}
    for doc in (request.node.root_doc, request.node.testcase_doc):
        if 'params' in doc:
            params.update(doc['params'])
    return templates.StackedContext(params)


@pytest.fixture
def yamlcase_load_body(yamlcase_context):
    def load_body(obj, allow_matching=False):
        # json strings are obsolete will be removed soon
        if isinstance(obj, str):
            return json.loads(obj)
        return templates.render(
            obj, yamlcase_context, allow_matching=allow_matching,
        )

    return load_body


def _create_template_context(root_doc, testcase_doc):
    params = {}
    for doc in (root_doc, testcase_doc):
        if 'params' in doc:
            params.update(doc['params'])
    return templates.StackedContext(params)


def _apply_marks(func, marks, yamlcase_context: templates.StackedContext):
    for mark in marks:
        markobj = getattr(pytest.mark, mark['name'])
        args = templates.render(mark.get('args', ()), yamlcase_context)
        kwargs = templates.render(mark.get('kwargs', {}), yamlcase_context)
        func = markobj(*args, **kwargs)(func)
    return func
