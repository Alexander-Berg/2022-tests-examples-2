from swagger_spec_validator.util import get_validator

from sandbox.web import api


def test_spec_is_valid():
    spec_json = api.v1.Api.dict
    validator = get_validator(spec_json)
    validator.validate_spec(spec_json)
