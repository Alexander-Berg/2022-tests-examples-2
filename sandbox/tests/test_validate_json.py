import pytest

from conftest import valid_json, invalid_json, real_response, splitter
from sandbox import common
from sandbox.projects.yabs.qa.tasks.YabsServerValidateResponses.utils.validate_json import validate_json


class TestValidateJson(object):
    @pytest.mark.skipif(
        common.system.inside_the_binary(),
        reason="Unmet dependency (no `jsbeautifier` Python package in Arcadia)"
    )
    @pytest.mark.parametrize(
        'valid_json', [valid_json]
    )
    def test_valid_json_without_splitter(self, valid_json):
        assert len(validate_json(valid_json)) == 0

    @pytest.mark.skipif(
        common.system.inside_the_binary(),
        reason="Unmet dependency (no `jsbeautifier` Python package in Arcadia)"
    )
    @pytest.mark.parametrize(
        'invalid_json', [invalid_json]
    )
    def test_invalid_json_without_splitter(self, invalid_json):
        errors = validate_json(invalid_json)
        assert len(errors) == 1

        error = errors[0][0]
        assert error.position.line == 3
        assert error.position.column == 0
        assert error.message == 'Strict JSON does not allow a final comma in an object (dictionary) literal'

    @pytest.mark.xfail(reason="Fails miserably (investigation required)")
    @pytest.mark.parametrize(
        'valid_json', [
            splitter.join([valid_json, valid_json]),
        ]
    )
    def test_valid_json_with_splitter(self, valid_json):
        assert len(validate_json(valid_json, splitter)) == 0

    @pytest.mark.xfail(reason="Fails miserably (investigation required)")
    @pytest.mark.parametrize(
        'invalid_json', [
            splitter.join([valid_json, invalid_json]),
        ]
    )
    def test_invalid_json_with_splitter(self, invalid_json):
        errors = validate_json(invalid_json, splitter)
        assert len(errors) == 1

        error = errors[0][0]
        assert error.position.line == 7
        assert error.position.column == 0
        assert error.message == 'Strict JSON does not allow a final comma in an object (dictionary) literal'

    @pytest.mark.xfail(reason="Fails miserably (investigation required)")
    def test_real_valid_json_with_splitter(self):
        errors = validate_json(real_response, splitter)
        assert not len(errors)
