import pytest


@pytest.mark.parametrize(
    'content_type, expected_result',
    [
        ('mds-link', b'https://read.test/print-form'),
        ('binary', b'test string'),
    ],
)
async def test_get_contract_print_form(
        taxi_process_automation_salesforce_esb_web,
        mockserver,
        load,
        mock_balance,
        content_type,
        expected_result,
):
    method_response = {
        'Balance2.GetContractPrintForm': f'{content_type}_response.xml',
    }
    mock_balance(method_response)

    response = await taxi_process_automation_salesforce_esb_web.get(
        '/v1/billing/contract/print-form',
        params={
            'object_id': '123',
            'object_type': 'contract',
            'desired_content_type': content_type,
        },
    )

    assert response.status == 200
    content = await response.content.read()
    assert content == expected_result
