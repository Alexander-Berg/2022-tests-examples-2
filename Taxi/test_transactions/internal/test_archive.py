import datetime as dt

import bson
import pytest

from transactions.internal import archive


_ENABLE_ARCHIVE_FOR_EDA = pytest.mark.config(
    TRANSACTIONS_ARCHIVE_ENABLED={'eda': 1, '__default__': 0},
)


@_ENABLE_ARCHIVE_FOR_EDA
@pytest.mark.nofilldb()
@pytest.mark.now('2022-05-04T00:00:00+03:00')
async def test_fetch_invoice(patch, eda_web_context):
    invoice_id = 'some_invoice_id'
    execute = _patch_ydb_execute(patch, invoice_id)

    invoice = await archive.fetch_invoice(invoice_id, eda_web_context)

    assert invoice == {
        '_id': invoice_id,
        'updated': dt.datetime.utcnow(),
        'invoice_request': {},
    }
    assert len(execute.calls) == 1


@_ENABLE_ARCHIVE_FOR_EDA
@pytest.mark.nofilldb()
@pytest.mark.now('2022-05-04T00:00:00+03:00')
async def test_fetch_invoice_not_found(patch, eda_web_context):
    invoice_id = 'some_invoice_id'
    execute = _patch_ydb_execute(patch, invoice_id, response=[])

    with pytest.raises(archive.NotFoundError):
        await archive.fetch_invoice(invoice_id, eda_web_context)

    assert len(execute.calls) == 1


@_ENABLE_ARCHIVE_FOR_EDA
@pytest.mark.now('2022-05-04T00:00:00+03:00')
async def test_restore_invoice(patch, eda_web_context):
    invoice_id = 'some_invoice_id'
    execute = _patch_ydb_execute(patch, invoice_id)

    doc_before = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_before is None
    invoice = await archive.restore_invoice(invoice_id, eda_web_context)

    assert invoice['_id'] == invoice_id
    assert invoice['invoice_request'] == {}
    assert invoice['updated'] != dt.datetime.utcnow()

    assert len(execute.calls) == 1
    doc_after = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_after == invoice


@_ENABLE_ARCHIVE_FOR_EDA
@pytest.mark.now('2022-05-04T00:00:00+03:00')
async def test_restore_invoice_not_found(patch, eda_web_context):
    invoice_id = 'some_invoice_id'
    execute = _patch_ydb_execute(patch, invoice_id, response=[])

    doc_before = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_before is None
    with pytest.raises(archive.NotFoundError):
        await archive.restore_invoice(invoice_id, eda_web_context)

    assert len(execute.calls) == 1
    doc_after = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_after is None


@_ENABLE_ARCHIVE_FOR_EDA
@pytest.mark.now('2022-05-04T00:00:00+03:00')
async def test_safe_restore_invoice_not_found(patch, eda_web_context):
    invoice_id = 'some_invoice_id'
    execute = _patch_ydb_execute(patch, invoice_id, response=[])

    doc_before = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_before is None
    invoice = await archive.safe_restore_invoice(invoice_id, eda_web_context)
    assert invoice is None

    assert len(execute.calls) == 1
    doc_after = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_after is None


@pytest.mark.now('2022-05-04T00:00:00+03:00')
async def test_safe_restore_invoice_disabled_config(patch, eda_web_context):
    invoice_id = 'some_invoice_id'
    execute = _patch_ydb_execute(patch, invoice_id, response=[])

    doc_before = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_before is None
    invoice = await archive.safe_restore_invoice(invoice_id, eda_web_context)
    assert invoice is None

    assert not execute.calls
    doc_after = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_after is None


@_ENABLE_ARCHIVE_FOR_EDA
@pytest.mark.now('2022-05-04T00:00:00+03:00')
@pytest.mark.filldb(eda_invoices='for_test_restore_existing_invoice')
async def test_restore_existing_invoice(patch, eda_web_context):
    invoice_id = 'some_invoice_id'
    execute = _patch_ydb_execute(patch, invoice_id)

    doc_before = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    invoice = await archive.restore_invoice(invoice_id, eda_web_context)

    assert invoice == doc_before

    assert len(execute.calls) == 1
    doc_after = await eda_web_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    assert doc_before == doc_after


def _patch_ydb_execute(patch, invoice_id, response=None):
    @patch(
        'transactions.generated.service.ydb_client.plugin.'
        'YdbClient.execute',
    )
    async def execute(query, params, operation):
        assert params == {
            '$scope': 'eda',
            '$id_hash': '08f15b68288db085b573ca2a07a1d03f',
            '$id': invoice_id,
        }
        assert operation == 'invoices:select_by_id'
        if response is None:
            doc = {
                '_id': invoice_id,
                'updated': dt.datetime.utcnow(),
                'invoice_request': {},
            }
            local_response = [{'doc': bson.BSON.encode(doc)}]
        else:
            local_response = response
        return local_response

    return execute


@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            True,
            marks=_ENABLE_ARCHIVE_FOR_EDA,
            id='it should return True when config is enabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                TRANSACTIONS_ARCHIVE_ENABLED={'eda': 0, '__default__': 0},
            ),
            id='it should return False when config is disabled',
        ),
        pytest.param(False, id='it should return False by default'),
    ],
)
def test_is_enabled(eda_web_context, expected):
    assert archive.is_enabled(eda_web_context) is expected
