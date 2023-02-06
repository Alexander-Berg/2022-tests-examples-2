import pytest

from eats_report_sender.generated.service.swagger.models import (
    api as api_module,
)


CERTAIN_TEMPLATE_CONFIG_NAME = (
    'EATS_REPORT_SENDER_PARTNER_EMAIL_SETTINGS_MACHINE_NAME_CERTAIN'
)


@pytest.fixture
def report_with_certain_template(load_json):
    return api_module.Report.deserialize(
        load_json('report_data.json')['report_with_certain_template'],
    )


@pytest.fixture
def report_with_default_template(load_json):
    return api_module.Report.deserialize(
        load_json('report_data.json')['report_with_default_template'],
    )


# @pytest.fixture(autouse=True)
# def update_stq3_context(stq3_context, load_json):
#     setattr(
#         stq3_context.config,
#         CERTAIN_TEMPLATE_CONFIG_NAME,
#         load_json('config.json')[CERTAIN_TEMPLATE_CONFIG_NAME],
#     )
