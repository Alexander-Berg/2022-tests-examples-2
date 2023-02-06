import pytest

from test_transactions import helpers


@pytest.mark.parametrize('data_path', ['not_found.json', 'success.json'])
async def test_resume(patch, load_py_json, web_app_client, db, stq, data_path):
    test_case = load_py_json(data_path)
    restore = helpers.patch_safe_restore_invoice(
        patch, None, [test_case['request']['invoice_id']],
    )
    response = await web_app_client.post(
        '/v2/invoice/resume_processing', json=test_case['request'],
    )
    assert response.status == test_case['expected_status']
    content = await response.json()
    assert content == test_case['expected_content']
    actual_order = await _fetch_flat_order(db, test_case)
    assert actual_order == test_case['expected_order']
    assert stq.transactions_events.times_called == (
        test_case['expected_process_events_times_called']
    )
    assert len(restore.calls) == 1


async def _fetch_flat_order(db, resume_test_case):
    order = await db.orders.find_one(
        {'_id': resume_test_case['request']['invoice_id']},
        {'invoice_request': True},
    )
    if order is None:
        return {}
    return {
        'is_processing_halted': (
            order['invoice_request'].get('is_processing_halted', False)
        ),
    }
