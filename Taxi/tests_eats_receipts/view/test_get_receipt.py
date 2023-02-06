import pytest


DOCUMENT_ID = '0'
INVALID_DOCUMENT_ID = '9'
DOCUMENT_ID_FIELD_NAME = 'document_id'
INVALID_DOCUMENT_ID_FIELD_NAME = 'dcmnt_id'

ORIGINATOR = 'originator'

INCOMPLETE_ROW_DOCUMENT_ID = '1'


@pytest.mark.parametrize(
    'document_id_field_name, document_id, status_code',
    (
        pytest.param(DOCUMENT_ID_FIELD_NAME, DOCUMENT_ID, 200, id='ok'),
        pytest.param(
            DOCUMENT_ID_FIELD_NAME,
            INVALID_DOCUMENT_ID,
            404,
            id='invalid order id',
        ),
        pytest.param(
            INVALID_DOCUMENT_ID_FIELD_NAME,
            DOCUMENT_ID,
            400,
            id='invalid request',
        ),
    ),
)
async def test_get_valid_receipt(
        taxi_eats_receipts,
        pgsql,
        document_id_field_name,
        document_id,
        status_code,
):

    response = await taxi_eats_receipts.post(
        '/api/v1/receipt/',
        json={document_id_field_name: document_id, 'originator': ORIGINATOR},
    )
    if status_code == 200:
        assert (
            response.json()['ofd_info']['ofd_receipt_url']
            == 'https://ofd.yandex.ru/vaucher/ffffff/11111/22222'
        )

    assert response.status_code == status_code
