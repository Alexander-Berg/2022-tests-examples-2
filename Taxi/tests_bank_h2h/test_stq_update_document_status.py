import json

import pytest

from tests_bank_h2h import common


def default_stq_kwargs(
        sender=common.SENDER, sender_reference=common.DOCUMENT_ID,
):
    return {'sender': sender, 'sender_reference': sender_reference}


@pytest.mark.now(common.MOCK_NOW)
async def test_stq_ok(pgsql, stq_runner, bank_core_tps):
    sender = common.SENDER
    document_id = common.DOCUMENT_ID
    common.insert_document(
        pgsql, status_info=json.dumps(common.get_status_info()),
    )
    await stq_runner.bank_h2h_update_document_status_from_bank_core.call(
        task_id='update_document_status_from_bank_core_'
        f'{sender}_{document_id}',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=False,
    )
    document_pg = common.select_document(pgsql, sender, document_id)
    assert document_pg.status_info == {
        'instruction_statuses': [
            {
                'instruction_id': '1',
                'original_money': {'amount': '1234.56', 'currency': 'RUB'},
                'taken_money': {'amount': '1234.56', 'currency': 'RUB'},
                'status': common.STATUS_FINISHED,
                'status_history': [
                    {
                        'date': common.MOCK_DATE_NOW,
                        'new_status': common.STATUS_ACCEPTED,
                    },
                    {
                        'date': common.MOCK_DATE_NOW,
                        'new_status': common.STATUS_FINISHED,
                        'old_status': common.STATUS_ACCEPTED,
                        'taken_money': {
                            'amount': '1234.56',
                            'currency': 'RUB',
                        },
                    },
                ],
            },
            {
                'instruction_id': '2',
                'original_money': {'amount': '234.56', 'currency': 'USD'},
                'status': common.STATUS_FAILED,
                'status_history': [
                    {
                        'date': common.MOCK_DATE_NOW,
                        'new_status': common.STATUS_ACCEPTED,
                    },
                    {
                        'date': common.MOCK_DATE_NOW,
                        'new_status': common.STATUS_FAILED,
                        'old_status': common.STATUS_ACCEPTED,
                    },
                ],
            },
        ],
    }

    assert bank_core_tps.document_status_get_handler.times_called == 1


@pytest.mark.now(common.MOCK_NOW)
async def test_stq_double_identical_update(pgsql, stq_runner, bank_core_tps):
    sender = common.SENDER
    document_id = common.DOCUMENT_ID
    common.insert_document(
        pgsql, status_info=json.dumps(common.get_status_info()),
    )
    await stq_runner.bank_h2h_update_document_status_from_bank_core.call(
        task_id='update_document_status_from_bank_core_'
        f'{sender}_{document_id}',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=False,
    )
    await stq_runner.bank_h2h_update_document_status_from_bank_core.call(
        task_id='update_document_status_from_bank_core_'
        f'{sender}_{document_id}',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=False,
    )
    document_pg = common.select_document(pgsql, sender, document_id)
    assert document_pg.status_info == {
        'instruction_statuses': [
            {
                'instruction_id': '1',
                'original_money': {'amount': '1234.56', 'currency': 'RUB'},
                'taken_money': {'amount': '1234.56', 'currency': 'RUB'},
                'status': common.STATUS_FINISHED,
                'status_history': [
                    {
                        'date': common.MOCK_DATE_NOW,
                        'new_status': common.STATUS_ACCEPTED,
                    },
                    {
                        'date': common.MOCK_DATE_NOW,
                        'new_status': common.STATUS_FINISHED,
                        'old_status': common.STATUS_ACCEPTED,
                        'taken_money': {
                            'amount': '1234.56',
                            'currency': 'RUB',
                        },
                    },
                ],
            },
            {
                'instruction_id': '2',
                'original_money': {'amount': '234.56', 'currency': 'USD'},
                'status': common.STATUS_FAILED,
                'status_history': [
                    {
                        'date': common.MOCK_DATE_NOW,
                        'new_status': common.STATUS_ACCEPTED,
                    },
                    {
                        'date': common.MOCK_DATE_NOW,
                        'new_status': common.STATUS_FAILED,
                        'old_status': common.STATUS_ACCEPTED,
                    },
                ],
            },
        ],
    }

    assert bank_core_tps.document_status_get_handler.times_called == 2


@pytest.mark.now(common.MOCK_NOW)
async def test_stq_not_found_document(stq_runner, bank_core_tps):
    sender = common.SENDER
    document_id = common.DOCUMENT_ID
    await stq_runner.bank_h2h_update_document_status_from_bank_core.call(
        task_id='update_document_status_from_bank_core_NONE',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=True,
    )

    assert bank_core_tps.document_status_get_handler.times_called == 1


@pytest.mark.now(common.MOCK_NOW)
async def test_stq_empty_instruction_list(mockserver, stq_runner):
    @mockserver.json_handler(
        '/bank-core-tps/v2/document/status/by-reference/get',
    )
    def _document_status_get(request):
        return {
            'sender': common.SENDER,
            'sender_reference': common.DOCUMENT_ID,
            'document_id': 'some_javist_id',
            'instructions': [],
        }

    sender = common.SENDER
    document_id = common.DOCUMENT_ID
    await stq_runner.bank_h2h_update_document_status_from_bank_core.call(
        task_id='update_document_status_from_bank_core_NONE',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=False,
    )

    assert _document_status_get.times_called == 1


@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.parametrize(
    'status_code, expected_times', [(400, 1), (500, 2), ('timeout', 2)],
)
async def test_stq_core_tps_error(
        mockserver, pgsql, stq_runner, status_code, expected_times,
):
    @mockserver.json_handler(
        '/bank-core-tps/v2/document/status/by-reference/get',
    )
    def _document_status_get(request):
        if status_code == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(status=status_code)

    sender = common.SENDER
    document_id = common.DOCUMENT_ID
    common.insert_document(
        pgsql, status_info=json.dumps(common.get_status_info()),
    )
    await stq_runner.bank_h2h_update_document_status_from_bank_core.call(
        task_id='update_document_status_from_bank_core_'
        f'{sender}_{document_id}',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=True,
    )

    assert _document_status_get.times_called == expected_times
