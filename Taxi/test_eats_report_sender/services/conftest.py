import pytest


from eats_report_sender.generated.service.swagger.models import (
    api as api_module,
)


@pytest.fixture
def report_object(load_json):
    return api_module.Report.deserialize(load_json('report_object.json'))
