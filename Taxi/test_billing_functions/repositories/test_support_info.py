import pytest

from billing.docs import service
from billing_models.generated import models as generated_models
from billing_models.generated.models import support_info

from billing_functions.repositories import support_info as support_info_repo

_MOCK_NOW = '2021-01-01T00:00:00.000000+00:00'


@pytest.mark.parametrize(
    'method, test_data_json',
    (
        #
        ('save_for_commission', 'commission/test_data.json'),
        (
            'save_for_commission',
            'commission/test_data_with_config_disabled.json',
        ),
        (
            'save_for_commission',
            'commission/test_data_with_migration_mode.json',
        ),
        #
        ('save_for_driver_mode', 'driver_mode/test_data.json'),
        (
            'save_for_driver_mode',
            'driver_mode/test_data_with_config_disabled.json',
        ),
        (
            'save_for_driver_mode',
            'driver_mode/test_data_with_migration_mode.json',
        ),
        #
        ('save_for_order_subvention', 'order_subvention/test_data.json'),
    ),
)
@pytest.mark.json_obj_hook(
    #
    SupportInfoData=support_info.CommissionSupportInfoData,
    SupportInfoSearchParams=support_info.CommissionSupportInfoSearchParams,
    SupportInfoAgreement=support_info.CommissionSupportInfoAgreement,
    SupportInfoAgreementData=support_info.CommissionSupportInfoAgreementData,
    #
    DriverModeData=support_info.DriverModeSupportInfoData,
    DriverModeDataDriverMode=support_info.DriverModeSupportInfoDataDriverMode,
    #
    OrderSubventionData=support_info.OrderSubventionSupportInfoData,
    OrderSubventionDataPayout=(
        support_info.OrderSubventionSupportInfoDataPayout
    ),
    # common
    SupportInfoVar=support_info.Var,
    SupportInfoVarOperation=support_info.VarOperation,
    Money=generated_models.Money,
    Doc=service.Doc,
)
@pytest.mark.now(_MOCK_NOW)
async def test_save_for_commission(
        method,
        test_data_json,
        load_py_json,
        stq3_context,
        do_mock_billing_docs,
        monkeypatch,
):
    test_data = load_py_json(test_data_json)
    expected_data = test_data['expected']
    docs = do_mock_billing_docs()

    for key, value in test_data['config_variables'].items():
        monkeypatch.setattr(stq3_context.config, key, value)

    support_info_repo_instance = support_info_repo.DocsAsRepository(
        stq3_context.docs, stq3_context.config,
    )

    func = getattr(support_info_repo_instance, method)
    actual = await func(**test_data['query'])

    assert actual == expected_data['doc_id']
    assert docs.created_docs == expected_data['docs']
