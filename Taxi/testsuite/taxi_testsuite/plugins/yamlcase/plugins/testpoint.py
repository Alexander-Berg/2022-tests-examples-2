import pytest


@pytest.fixture
def yamlcase_create_testpoints(request, testpoint, yamlcase_load_body):
    def create_testpoint_handler(handler):
        @testpoint(handler['name'])
        def _testpoint_handler(data):
            if 'data' in handler:
                expected = yamlcase_load_body(
                    handler['data'], allow_matching=True,
                )
                assert data == expected
            if 'returns' in handler:
                return yamlcase_load_body(handler['returns'])
            return None

    for handler in request.node.testpoint_handlers:
        create_testpoint_handler(handler)


@pytest.fixture
def yamlcase_assertion_testpoint_called(testpoint):
    async def run_assertion(assertion):
        assert 'name' in assertion
        handler = testpoint[assertion['name']]
        testpoint_calls = []
        tested = False

        if 'wait_call' in assertion:
            assert isinstance(assertion['wait_call'], bool)
            if assertion['wait_call'] is True:
                call = await handler.wait_call()
                testpoint_calls.append(call['data'])

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

    return run_assertion
